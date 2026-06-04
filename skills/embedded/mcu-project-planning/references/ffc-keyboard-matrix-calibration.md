# FFC Keyboard Matrix Calibration Procedure

> How to map an unknown laptop keyboard FFC cable to MCU GPIO for direct matrix scanning.

## Background

Laptop keyboards use a row/column matrix printed on flexible PET film. The FFC
(Flat Flexible Cable) carries one line per row and one per column, plus ground
and sometimes VCC. The mapping from FFC pin to matrix row/column is unique per
laptop model and is NOT documented publicly.

## Equipment

- MCU board with FFC ZIF connector (see pinout.md for target board)
- Multimeter (continuity mode)
- Laptop keyboard FFC cable (disconnected from laptop)
- Debug firmware flashed to MCU (see below)

## Method 1: Continuity Test (No Firmware)

1. Identify keyboard matrix traces on the FFC cable:
   - Set multimeter to continuity/beep mode
   - Press and hold a key on the keyboard
   - Probe pairs of FFC pins until you find continuity
   - One pin is the row, one is the column for that key
   - Repeat for 5-10 keys to establish the row/column pattern

2. Map all rows and columns:
   - Each row pin will show continuity with multiple column pins (one per key in that row)
   - Each column pin will show continuity with multiple row pins
   - Group pins by their connectivity pattern

3. Document the mapping in pinout.md

## Method 2: Firmware Scan (Recommended)

Flash this debug firmware to the MCU:

```c
// matrix_debug.c — flash this first to identify FFC pin mapping
#include <stdio.h>
#include "driver/gpio.h"

// Configure ALL FFC pins as input with pull-up
void setup() {
    for (int i = 0; i < NUM_FFC_PINS; i++) {
        gpio_set_direction(ffc_pins[i], GPIO_MODE_INPUT);
        gpio_set_pull_mode(ffc_pins[i], GPIO_PULLUP_ONLY);
    }
    uart_init(115200);
}

void loop() {
    for (int pin = 0; pin < NUM_FFC_PINS; pin++) {
        if (gpio_get_level(ffc_pins[pin]) == 0) {
            printf("FFC_PIN_%d LOW\n", pin);
        }
    }
    delay(10);
}
```

Procedure:
1. Flash the debug firmware
2. Open serial monitor at 115200 baud
3. Press each key on the keyboard one at a time
4. Note which FFC pin(s) go LOW for each key
5. Build the row/column map from the pattern

## Method 3: Combined (Most Reliable)

1. Use Method 1 to identify ground pins (continuity to keyboard shield/metal)
2. Use Method 2 to identify active pins
3. Cross-reference to build complete mapping

## Common FFC Pin Counts

| Laptop Type    | FFC Pins | Matrix Size | Notes                    |
|----------------|----------|-------------|--------------------------|
| Standard 14"   | 26-30    | 8×16        | Most common              |
| Standard 15.6" | 30-34    | 8×18        | With numpad              |
| Gaming 16"     | 30-40    | 8×20        | Per-key RGB adds lines   |
| Ultra-thin     | 22-26    | 8×14        | Compact layout           |

## Safety Notes

- FFC cables are fragile — do not bend sharply
- ZIF connector: lift flap fully before inserting/removing
- ESD protection: ground yourself before handling FFC
- Do not power the keyboard from MCU VCC until you've confirmed the voltage
  requirement (some keyboards need 3.3V, some 5V, some 1.8V for logic)
