# PCB Design Guide — Robotics Controller

## Power Architecture

```
LiPo (6S–8S, 18–33.6V)
  │
  ├─► High-side MOSFET switch (SI4436 or similar)
  │     │
  │     ├──► Motor driver (VESC/Odrive) — direct battery voltage
  │     │
  │     ├──► Buck converter: Batt → 5V / 3A
  │     │     IC: TPS54360, MP1584, or LM2596 (simple)
  │     │     Output: servos, sensors, CAN transceiver
  │     │
  │     └──► LDO: 5V → 3.3V / 1A
  │           IC: AMS1117-3.3 or TPS7A91 (low noise)
  │           Output: MCU, IMU, encoder, logic
  │
  └─► Battery voltage sense → ADC
        Divider for 6S (25.2V max → 3.3V ADC):
        68kΩ / 10kΩ → ratio 0.128 → 25.2V → 3.23V ✓
        
        Divider for 8S (33.6V max → 3.3V ADC):
        91kΩ / 10kΩ → ratio 0.099 → 33.6V → 3.33V ✓
```

## MCU Pin Assignment (ESP32-S3)

```
GPIO   Function              Notes
─────────────────────────────────────────────
1      SPI3_CLK (IMU)        Shared SPI bus
2      SPI3_MOSI (IMU)
3      SPI3_MISO (IMU)
4      SPI3_CS_IMU           Active low
5      SPI2_CLK (Encoder)    Separate bus for encoder
6      SPI2_MOSI (Encoder)
7      SPI2_MISO (Encoder)
8      SPI2_CS_Encoder
9      CAN_TX (TWAI)         To VESC/Odrive
10     CAN_RX (TWAI)
11     UART0_TX              Debug/telemetry
12     UART0_RX
13     I2C_SCL               ToF, OLED expansion
14     I2C_SDA
15     ADC1_CH0              Battery voltage
16     ADC1_CH1              Motor current sense
17     PWM_SERVO             Juggling/actuator arm
18     GPIO_ESTOP_IN         NC contact, pull-up
19     GPIO_STATUS_LED       Visual state indicator
20     GPIO_BUZZER           Piezo for audio feedback
21     GPIO_LEG_SERVO        Landing gear servo
35     GPIO_BTN_USER         Start/reset button
43-44  UART1 (alt)           WiFi telemetry
```

## Sensor Circuits

### IMU (ICM-42688-P)

```
ESP32 GPIO1  → SCLK
ESP32 GPIO2  → SDI (MOSI)
ESP32 GPIO3  → SDO (MISO)
ESP32 GPIO4  → CS
ESP32 GPIO45 → INT1 (data ready, optional)

VDD  → 3.3V with 100nF + 10µF decoupling
VDDIO → 3.3V with 100nF
GND  → solid ground plane

CRITICAL: Vibration isolation required.
Option A: PCB cutout with 4 narrow tabs
Option B: Separate daughter board on silicone pads
Option C: Soft mounting with foam tape
```

### Encoder (AS5047P)

```
ESP32 GPIO5  → CLK
ESP32 GPIO6  → MOSI
ESP32 GPIO7  → MISO
ESP32 GPIO8  → CS

VDD5V → 5V (100nF + 10µF)
VDD3V → 3.3V (from internal LDO or external)

Magnet: diametric ring magnet on motor shaft
Air gap: 1–2 mm
```

### CAN Transceiver (TJA1051T/3)

```
ESP32 GPIO9  → TX
ESP32 GPIO10 → RX

VCC → 5V
CANH → to VESC CAN bus
CANL → to VESC CAN bus
120Ω termination across CANH-CANL (only at bus ends)
```

### Current Sense (INA240A2)

```
Shunt resistor: 5mΩ, 1W (2512 package)
INA240A2 gain: 50 V/V

Voltage divider on output to scale for 3.3V ADC:
10kΩ / 10kΩ → halves the output

For 40A max: 0.005 × 40 × 50 = 10V → divider → 5V → still too high!
Use 10kΩ / 6.8kΩ → ratio 0.405 → 10V → 4.05V → still marginal
Better: use INA240A1 (gain 20 V/V) → 40A → 4V → divider → 1.6V ✓
Or: larger shunt (10mΩ) with lower gain
```

## PCB Layout — 4-Layer Stackup

```
L1 (top):    Signal + components
L2 (inner): Ground plane (SOLID, no splits)
L3 (inner): Power planes (5V, 3.3V pours)
L4 (bottom): Signal + ground fill
```

### Component Placement (80 × 60 mm board)

```
┌────────────────────────────────────────────┐
│  [USB-C]  [ESP32-S3]     [LEDs] [Btn]     │
│                                            │
│  [IMU]          [INA240]                   │
│  (isolated)     [Current Sense]            │
│                                            │
│  [AS5047P]      [TJA1051]                  │
│  (encoder)      [CAN transceiver]          │
│                                            │
│  [Buck 24→5V]   [LDO 5V→3.3V]             │
│  [Inductor]     [Caps]                     │
│                                            │
│  [XT60]  [Servo]  [CAN]  [E-Stop] [I2C]   │
│  [Power] [Conn]   [Conn]  [Conn]  [Conn]   │
└────────────────────────────────────────────┘
```

### Critical Layout Rules

1. **IMU isolation**: Cutout with 4 tabs (0.5 mm width each). No traces under IMU.
2. **Ground plane**: Unbroken on L2. All ground vias stitched.
3. **Decoupling**: 100nF within 2 mm of every VDD pin. 10µF bulk per IC.
4. **CAN differential pair**: 120Ω impedance, matched length, away from power.
5. **Motor power**: ≥2 mm traces or copper pours. Multiple vias for current sharing.
6. **Antenna keepout**: ESP32 module antenna zone — no copper on any layer underneath.

## Connector Pinout

| Ref | Connector | Pinout |
|-----|-----------|--------|
| J1 | XT60 | +Bat, GND |
| J2 | JST-GH 4-pin | CANH, CANL, 5V, GND |
| J3 | JST-SH 3-pin | Servo signal, 5V, GND |
| J4 | JST-SH 3-pin | Leg servo signal, 5V, GND |
| J5 | JST-SH 4-pin | SDA, SCL, 3.3V, GND |
| J6 | USB-C | Standard USB-C pinout |
| J7 | Screw terminal | E-stop NC contact |
| J8 | Pin header 1×4 | TX, RX, 3.3V, GND |

## BOM — Key Components

| Ref | Component | Package | Qty |
|-----|-----------|---------|-----|
| U1 | ESP32-S3-WROOM-1-N16R8 | Module | 1 |
| U2 | ICM-42688-P | LGA-14 | 1 |
| U3 | AS5047P | TSSOP-14 | 1 |
| U4 | TJA1051T/3 | SO-8 | 1 |
| U5 | INA240A2 | SO-8 | 1 |
| U6 | TPS54360 | SO-8 | 1 |
| U7 | AMS1117-3.3 | SOT-223 | 1 |
| L1 | 10–22µH inductor | SMD | 1 |
| D1 | SS34 Schottky | SMA | 2 |
| R_shunt | 5mΩ 1W | 2512 | 1 |
| C_dec | 100nF MLCC | 0402 | 20 |
| C_bulk | 10µF MLCC | 0805 | 10 |
| PCB | 4-layer, 80×60mm | JLCPCB | 5 |

Estimated PCB + components: ~650 NOK (~$60 USD) for 5 boards.
