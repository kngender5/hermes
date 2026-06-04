# Inline FFC Keyboard Matrix Interceptor

Pattern for building an inline adapter that sits between a laptop's keyboard
FFC cable and the motherboard. Captures keypresses, sends to WiFi, types out
responses — all transparently.

## Architecture

```
Tastatur FFC → J1 (ZIF 30-pin) → 74HC4066 analog switches → J2 (solder pads) → hovedkort
                                                    ↕
                                            ESP32-S3 (inline)
```

## Key Components

- **J1**: Hirose FH34SRJ-30S-0.5SH (30-pin ZIF, 0.5mm, side-entry)
- **J2**: Solder pads (0.5mm pitch) → FFC cable to motherboard
- **Analog switches**: 4x 74HC4066 (quad bilateral) for rows + columns
- **Switch control**: Single GPIO (SW_CTL) to all 4066s via 74HC125 buffer
- **Column drivers**: 2N7000 N-MOSFET per column for typeout generation
- **Power**: 3.3V from FFC (motherboard supply), 150mA polyfuse

## Critical Rules

1. **FFC pinout is UNIQUE per laptop model.** Never assume. Calibrate with
   scan_debug firmware that prints GPIO state per keypress.
2. **74HC4066 truth table is inverted from intuition:**
   - SW_CTL = HIGH → switches CLOSED (passthrough active)
   - SW_CTL = LOW → switches OPEN (ESP32 takes over)
3. **Break-before-make timing**: Set SW_CTL LOW → wait 10µs → ESP32 drives lines
4. **ULP co-processor for wake-on-key**: ESP32-S3 ULP monitors columns at ~150µA,
   wakes main CPU via RTC interrupt on keypress
5. **Deep sleep as default**: 99.9% of time in <1mA deep sleep. Active only
   during record/send/typeout bursts.
6. **Column driver for typeout**: ESP32 can't just "set a column low" — needs
   MOSFET to pull column low while row is active. Pull-up holds column high
   when MOSFET is off.

## Bill of Materials (key parts only)

| Ref | Component | Package | Qty |
|-----|-----------|---------|-----|
| U1 | ESP32-S3-WROOM-1-N16R8 | Module | 1 |
| J1 | FH34SRJ-30S-0.5SH | ZIF | 1 |
| IC1-IC4 | 74HC4066 | TSSOP-14 | 4 |
| IC5 | 74HC125 | TSSOP-14 | 1 |
| Q1-Q20 | 2N7000 | SOT-23 | 20 |
| D1-D20 | PESD3V3Y1BCSX | SOD-523 | 20 |
| R1-R20 | 10kΩ pull-ups | 0402 | 20 |

## Source

Project: ~/projects/teleprompt/
Created: 2026-05-26
