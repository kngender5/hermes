---
name: embedded-robotics-control
description: End-to-end embedded robotics control system design — from dynamic simulation and controller synthesis through firmware implementation and PCB integration. Covers inverted pendulum systems, motor control, state estimation (complementary filter, EKF), LQR/PID control, sensor fusion (IMU + encoder), and telemetry. Use when designing self-balancing robots, wheeled robots, or any system requiring real-time embedded control loops on ESP32/STM32.
version: 0.1.0
triggers:
  - designing a self-balancing robot or inverted pendulum
  - need to simulate robot dynamics and design a controller (LQR, PID)
  - writing embedded firmware for motor control / balance / robotics
  - designing PCB for robotics (motor drive, IMU, encoder, CAN bus)
  - need telemetry system for real-time robot monitoring
  - working with ESP32 or STM32 for control applications
  - need state estimation (complementary filter, EKF) for IMU + encoder
---

# Embedded Robotics Control Systems

Full pipeline: **physics simulation → controller design → firmware → PCB → telemetry**.

Typical projects: self-balancing robots, wheeled mobile robots, inverted pendulum systems, gimbal stabilization.

---

## Phase 1: Dynamic Simulation

*Always simulate before building hardware. Validate controller gains in software first.*

### 1.1 Derive Equations of Motion

For an inverted pendulum on a wheel, use Lagrangian mechanics. State vector:
```
x = [θ, θ̇, φ, φ̇]
θ  = body tilt from vertical
φ  = wheel rotation angle
```

Linearize around θ ≈ 0 for LQR design. Get state-space form: `ẋ = Ax + Bu`

### 1.2 Simulate in Python

Use `scipy.integrate.solve_ivp` (RK45) for **final validation** of the nonlinear system. For **controller tuning** (evaluating hundreds of gain combinations), use **Euler integration** — it's ~30x fast enough and the results correlate well with RK45 for stable controllers:

```python
# Fast Euler step (for tuning loops)
def step_dynamics(x, u, dt):
    x_dot = dynamics(t, x, u)
    return x + np.array(x_dot) * dt

# Use solve_ivp only for final validation of the best controller
```

**NumPy array gotcha**: `K @ x` where K is (1,4) and x is (4,) returns shape (1,), not a scalar. Use `float((K @ x)[0])` or `(K @ x).item()` — `float(K @ x)` raises TypeError on newer NumPy.

**Key parameters to define:**
- Body mass, wheel mass, CG height, wheel radius
- Moments of inertia (body about CG, wheel about axle)
- Motor torque limit, friction coefficients
- Sensor noise std dev (IMU, encoder)

**Control loop in simulation:**
```python
# At each timestep (e.g., 200 Hz):
# 1. Read sensors (add noise if testing estimator)
# 2. State estimation (complementary filter or EKF)
# 3. Compute control: tau = -K @ x_est
# 4. Saturate: tau = clip(tau, -tau_max, tau_max)
# 5. Integrate dynamics one step
# 6. Check for fall condition (|theta| > threshold)
```

### 1.3 Controller Design & Tuning

**LQR** (preferred for multi-state systems):
```python
from scipy import linalg
Q = np.diag([q_angle, q_rate, q_wheel_pos, q_wheel_vel])
R = np.array([[r_control]])
P = linalg.solve_continuous_are(A, B, Q, R)
K = np.linalg.solve(R, B.T @ P)
```

**Tuning strategy — Coarse-to-fine grid search:**
1. **Coarse phase**: Sweep wide ranges (e.g., q_angle: 100–6000, R: 0.05–0.8) with ~200 configs
2. **Fine phase**: Narrow ranges around the best coarse result, ~900 configs
3. Use Euler integration for speed (~75 eval/s vs ~2.5 eval/s with solve_ivp)
4. Score = weighted sum: `0.35*rms_tilt + 0.15*max_tilt/5 + 0.2*rms_torque/3 + 0.3*sat_pct`
5. Re-validate the top 5 with full RK45 integration

Tuning heuristics for inverted pendulum:
- `q_angle` (θ penalty): 500–10000 (most important)
- `q_rate` (θ̇ penalty): 50–300
- `q_wheel_pos` (φ penalty): 1–20 (prevents wheel runaway)
- `q_wheel_vel` (φ̇ penalty): 5–20
- `r_control`: 0.05–2.4 (lower = more aggressive; higher = smoother, less torque)

**Key insight from tuning**: Increasing R (torque penalty) from 0.1 to 2.4 reduced RMS torque by 95% with minimal impact on tilt performance. The optimal controller is much less aggressive than the "textbook" low-R solution.

**Cascaded PID** (simpler alternative):
- Outer loop: angle PD → desired wheel velocity
- Inner loop: wheel velocity PI → motor torque

### 1.4 Validate

- Check controllability: `rank([B, AB, A²B, A³B])` must equal state count
- Verify unstable poles exist (system should be open-loop unstable)
- Test with initial tilt of 5–10°
- Test with impulse disturbance (simulates a push)
- Test with periodic disturbance (simulates juggling arm, etc.)
- Confirm torque does not saturate excessively (<5% of samples)

### 1.5 Export Gains for Firmware

```python
import json
config = {
    "lqr_gain": K.tolist(),
    "params": {relevant physical params},
    "A_matrix": A.tolist(),
    "B_matrix": B.tolist(),
}
with open("controller_config.json", "w") as f:
    json.dump(config, f, indent=2)
```

---

## Phase 2.5: Mechanical CAD

*Generate parametric mechanical designs from Python for OpenSCAD preview or Fusion 360 export.*

### OpenSCAD Generation from Python

Pre-compute all numeric values in Python, then build the OpenSCAD string via list append. **Do NOT use f-strings with OpenSCAD code** — OpenSCAD variables like `{plate_t}` conflict with Python f-string syntax:

```python
# WRONG — f-string tries to evaluate {plate_t} as Python
scad = f"cube([{plate_t}, {motor_dia}, 10]);"  # NameError!

# RIGHT — pre-compute, then use f-string only for the numeric value
pt = d['mount_plate_thickness']  # pre-compute
lines.append(f"plate_t = {pt};")  # safe: just a number
lines.append("cube([plate_t, motor_dia, 10]);")  # OpenSCAD variable in plain string

# ALTERNATIVE — build with list append, no f-strings in OpenSCAD code blocks
lines = []
a = lines.append
a(f"wheel_dia = {wd};")       # numeric value via f-string
a("cylinder(d=wheel_dia, h=10);")  # OpenSCAD code as plain string
return "\n".join(lines)
```

### Typical Dimensions (self-balancing unicycle)
- Wheel: 406mm (16") pneumatic
- Frame: 25×25 T-slot AL 6060, 500mm tall
- Motor: Ø63mm BLDC, 80mm long
- Battery: 140×50×35mm 6S LiPo, mounted low for CG
- PCB: 80×60mm, M3 standoffs
- Juggling arm: 300mm × Ø16mm CF/AL tube
- Overall: ~293×150×703 mm (W×D×H), ~10-12 kg

### Manufacturing Outputs to Generate
1. **OpenSCAD file** (.scad) — 3D preview, render with `openscad`
2. **Dimensions JSON** — all critical measurements
3. **Cutting list** — extrusion lengths, plate sizes, hardware BOM
4. **Fusion 360 export script** — STEP/STL export via `adsk.fusion`

*Target: ESP32-S3 or STM32H7, PlatformIO + Arduino framework.*

### 2.1 Control Loop Architecture

```
Timer ISR (200–500 Hz):
  1. Read IMU (SPI burst, ~50 µs)
  2. Read encoder (SPI, ~20 µs)
  3. State estimation (complementary filter, ~10 µs)
  4. LQR computation (4 multiply-adds, ~5 µs)
  5. Send torque command to motor driver (CAN/UART, ~100 µs)
  6. Update juggling/actuator if active
  7. Send telemetry (if telemetry period elapsed)
```

Total: <250 µs per iteration at 200 Hz (50% CPU budget).

### 2.2 State Machine

```
BOOT → SELF_TEST → BALANCING → JUGGLING/ACTIVE
  ↓         ↓            ↓
  ↓    (sensor check)   FALL_DETECTED → (recovery) → BALANCING
  ↓                      ↓
  └──────── EMERGENCY_STOP (hardware E-stop, highest priority)
```

**Fall detection**: `|θ| > 30°` → disable motors, wait for manual recovery.

**Auto-start sequence**: After 3s of stable balance (`|θ| < 3°`), auto-enable secondary actuators (juggling arm, etc.).

### 2.3 Sensor Drivers

**IMU (ICM-42688-P)**:
- SPI, 1 kHz ODR minimum
- ±4g accel, ±1000°/s gyro
- Use FIFO burst read for atomic sampling
- Mount on vibration-isolated section of PCB (cutout with tabs, or silicone damper)

**Encoder (AS5047P)**:
- SPI, 14-bit resolution
- Diametric ring magnet on motor shaft, 1–2 mm air gap
- Read angle register (0x3FFF), check error bit

### 2.4 Motor Control

**VESC/Odrive via CAN**:
- Send torque or current commands via CAN 2.0B
- VESC CAN ID: 0x01, command SET_CURRENT (0x01)
- Current = torque / Kt (motor torque constant)
- Always implement hardware E-stop that cuts motor enable pin

### 2.5 Telemetry

**UDP broadcast** (50 Hz) to laptop for live monitoring:
```c
struct __attribute__((packed)) TelemetryPacket {
    uint32_t timestamp_ms;
    float theta_deg;
    float theta_dot_dps;
    float phi_rev;
    float phi_dot_rps;
    float motor_torque;
    float juggle_torque;
    float battery_voltage;
    uint8_t state;
    uint8_t flags;
};  // 34 bytes
```

Python receiver: `socket.SOCK_DGRAM`, `matplotlib.animation` for live plots.

---

## Phase 3: PCB Design

*4-layer board, KiCad, ~80×60 mm for a wheeled robot controller.*

### 3.1 Power Architecture

```
LiPo (6S–8S) → High-side MOSFET switch
  ├──► Motor driver (direct battery voltage)
  ├──► Buck: Batt → 5V (3A) for servos, sensors
  └──► LDO/Buck: 5V → 3.3V (1A) for MCU, logic
```

Battery voltage sensing: resistor divider to ADC. For 6S (25.2V max) → 3.3V ADC:
- 68kΩ / 10kΩ divider (ratio 0.128, 25.2V → 3.23V)

### 3.2 Critical Layout Rules

1. **IMU isolation**: PCB cutout with 4 tabs, or separate daughter board on silicone pads. Keep away from motor current traces.
2. **Ground plane**: Solid, unbroken on L2. Star ground at battery input.
3. **Decoupling**: 100nF on every VDD pin, within 2 mm. 10µF bulk per IC.
4. **CAN bus**: Differential pair, 120Ω termination (only at bus ends).
5. **Motor power**: ≥2 mm trace width for 20A, or copper pours with vias.
6. **Antenna keepout**: ESP32 module antenna zone per datasheet (typically 15×10 mm).

### 3.3 Connector Guide

| Function | Connector | Notes |
|----------|-----------|-------|
| Battery | XT60 | High current |
| CAN bus | JST-GH 4-pin | Standard VESC connector |
| Servo | JST-SH 3-pin | Signal + power |
| Debug | USB-C | Programming + UART |
| E-stop | Screw terminal | NC contact, hardware kill |
| Expansion | JST-SH 4-pin | I2C for ToF, OLED |

---

## Phase 4: Testing & Tuning

### 4.1 Simulation-First Workflow

1. Tune all gains in simulation
2. Export to firmware
3. Test on real hardware with **legs deployed** (safety)
4. Gradually reduce leg support as confidence grows
5. Log telemetry, compare against simulation

### 4.2 Real-World Tuning

- Start with **P only** (I=0, D=0), increase until oscillation
- Add **D** to dampen
- Add **I** last, only if steady-state error is unacceptable
- For LQR: increase Q diagonal entries for faster response, increase R for less aggressive control

### 4.3 Safety

- Hardware E-stop must cut motor power independently of software
- Deployable legs for startup/shutdown
- Fall detection with automatic motor disable
- Battery voltage monitoring with low-voltage cutoff
- Current limiting in motor driver

---

## Tips & Pitfalls

- **Use `python3` not `python`** on Ubuntu/WSL2 — `python` is not a symlink
- **`scipy.linalg.ctrb` was removed** in newer SciPy — build controllability matrix manually:
  ```python
  n = A.shape[0]
  C = B
  for k in range(1, n):
      C = np.hstack([C, np.linalg.matrix_power(A, k) @ B])
  rank = np.linalg.matrix_rank(C)
  ```
- **`K @ x` returns (1,) array, not scalar** when K is (1,4): use `(K @ x)[0]` not `float(K @ x)`. This breaks silently in tuning loops.
- **f-string vs OpenSCAD variable conflict**: OpenSCAD uses `{var}` syntax which clashes with Python f-strings. Pre-compute all values and use plain strings for OpenSCAD code blocks.
- **Euler vs RK45 for tuning**: Euler is ~30x faster and fine for comparing controllers. Always re-validate the final choice with RK45.
- **IMU vibration noise** is the #1 real-world issue. Mechanical isolation > software filtering.
- **Complementary filter** (α=0.98) is sufficient for most balance applications. EKF adds complexity with marginal benefit unless you need full orientation.
- **Motor torque saturation** causes integrator windup in PID. Always clamp and use anti-windup.
- **SPI clock speed**: ICM-42688-P supports 16 MHz, AS5047P supports 10 MHz. Use 8 MHz for reliability.
- **CAN bus termination**: Only place 120Ω resistors at the two physical ends of the bus, not at every node.
- **PlatformIO**: Use `monitor_filters = esp32_exception_decoder` in `platformio.ini` for readable crash dumps.

## References

- `references/simulation_template.py` — Full nonlinear simulation with LQR, complementary filter, animation, and parameter sweep
- `references/firmware_template.cpp` — ESP32-S3 firmware: LQR, state machine, sensor drivers, telemetry
- `references/pcb_design_guide.md` — PCB layout guide, power architecture, connector pinout, BOM
- `references/telemetry_receiver.py` — Python UDP receiver with live matplotlib plots
- `references/lqr_tuning_results.md` — Optimized LQR gains from 908-config grid search (unicycle juggler)
- `references/mechanical_design.md` — Frame dimensions, cutting list, hardware BOM, OpenSCAD generation pattern
