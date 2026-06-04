# LQR Tuning Results — Unicycle Juggler (2025-05-25)

## Best Configuration Found

```
Q = diag([9750, 300, 2, 15])
R = [2.4]
K = [95.52, 20.22, 0.91, 3.61]
```

## Performance (with juggling + push disturbance)

| Metric | Original (R=0.1) | Optimized (R=2.4) | Change |
|--------|------------------|-------------------|--------|
| rms tilt | 0.42° | 0.42° | Same |
| max tilt | 15.3° | 11.4° | -26% |
| rms torque | 4.73 Nm | 0.25 Nm | -95% |
| max torque | 16.19 Nm | 15.00 Nm | Within limit |
| saturation | 1.4% | 1.9% | Acceptable |

## Tuning Method

- **908 configurations** evaluated (coarse 192 + fine 900)
- Euler integration for speed (~75 eval/s)
- Score = 0.35·rms_tilt + 0.15·max_tilt/5 + 0.2·rms_torque/3 + 0.3·sat_pct
- Final validation with RK45 nonlinear integration

## Key Insight

Increasing R (torque penalty) from 0.1 to 2.4 dramatically reduced torque usage
with minimal tilt impact. The "textbook" low-R LQR is unnecessarily aggressive
for systems with periodic disturbances (juggling arm). Higher R = smoother control.

## Physical Parameters

    M_body = 8.0 kg
    M_wheel = 2.0 kg
    l_cg = 0.25 m
    r_wheel = 0.203 m (16" tire)
    I_body = 0.5 kg·m²
    I_wheel = 0.04 kg·m²
    tau_max = 15.0 Nm
    juggle_freq = 1.5 Hz
    juggle_tau_amp = 1.5 Nm

## Controllability

    A eigenvalues: [0, 0, +5.54, -5.57]
    Unstable pole: +5.54 rad/s
    Controllability rank: 4/4 (fully controllable)
