---
name: gcode-3d-printing
description: Write, customize, and debug G-code for 3D printers. Covers Marlin, Klipper, RepRap firmware. Includes movement, temperature, bed leveling, tool changes, custom macros, calibration scripts, and advanced techniques for multi-material printing.
---

# G-Code 3D Printing — Custom Scripts & Advanced Programming

Complete reference for writing custom G-code scripts for FDM/FFF 3D printers (Marlin, Klipper, RepRap, Prusa).

## Firmware Coverage

| Firmware | Coverage | Notes |
|----------|----------|-------|
| Marlin 2.x | ✅ Full | Most common (Ender, Prusa, Voron, custom) |
| Klipper | ✅ Full | Moonraker API, macros, kinematics |
| RepRap | ✅ Full | Open-source baseline |
| Prusa ( Buddy) | ✅ Full | Prusa-specific extensions |
| Marlin 1.x (legacy) | ⚠️ Partial | Older Creality, Anet |

**Forklaring:** G-koder (G0, G1, G28...) er standardisert av NIST RS274/NGC. M-koder (M104, M106...) er firmware-spesifikke.

## Core Movement Commands

### G0 — Rapid Move (Non-Extruding)
```gcode
G0 X100 Y100 Z5 F3000    ; Move to X100 Y100 Z5 at 50mm/s
G0 X50 F6000             ; Move only X-axis at 100mm/s
```

### G1 — Linear Move (Extruding)
```gcode
G1 X100 Y100 Z0.2 E5.0 F1500  ; Move while extruding 5mm filament at 25mm/s
G1 E-2 F300                   ; Retract 2mm at 5mm/s
G1 E2 F300                    ; Prime/de-retract 2mm
```

### G28 — Home All Axes
```gcode
G28          ; Home all axes (XYZ)
G28 X        ; Home only X
G28 X Y Z    ; Home specific axes in order
```

### G29 — Auto Bed Level (Probe Mesh)
```gcode
G29          ; Run bed leveling probe and generate mesh
G29 A       ; Activate bed leveling (Marlin)
G29 L0      ; Load mesh from slot 0
G29 P1      ; Probe 3x3 grid
G29 P3      ; Probe with interpolation
G29 S0      ; Save to EEPROM slot 0
G29 F 50    ; Set probe front offset
```

## Temperature Commands

### Hotend
```gcode
M104 S200        ; Set hotend to 200°C (non-blocking)
M104 S200 T0     ; Set extruder 0 to 200°C
M109 S200        ; Set hotend to 200°C and WAIT (blocking)
M109 S200 T1     ; Set extruder 1 to 200°C and WAIT
M105             ; Report all temperatures
M303 E0 S200 C8  ; PID tune hotend 0 at 200°C, 8 cycles
M303 E-1 S80 C8  ; PID tune bed at 80°C
```

### Heated Bed
```gcode
M140 S60         ; Set bed to 60°C (non-blocking)
M190 S60         ; Set bed to 60°C and WAIT
M141 S40         ; Set chamber to 40°C (if equipped)
```

### Fans
```gcode
M106 S255        ; Part cooling fan at 100%
M106 S128        ; Part cooling fan at 50%
M106 P0 S255     ; Fan 0 at 100%
M106 P1 S128     ; Fan 1 at 50% (if 2 fans)
M107             ; Turn off part cooling fan
```

## Extruder Control

### Modes
```gcode
M82              ; Absolute extrusion mode
M83              ; Relative extrusion mode (E resets per move)
G92 E0           ; Reset extruder position to 0
```

### Retraction
```gcode
; Standard retraction (Marlin)
G1 E-1.5 F1800   ; Retract 1.5mm at 30mm/s
G1 E1.5 F1800    ; De-retract

; Firmware retraction (Marlin)
M207 S1.5 F1800  ; Set retraction: 1.5mm at 30mm/s
M208 S0 F1800    ; Set deretraction: 0mm
M209 S1          ; Enable firmware retraction
M209 S0          ; Disable firmware retraction
```

### Pressure Advance (Klipper)
```gcode
SET_PRESSURE_ADVANCE EXTRUDER=extruder ADVANCE=0.05
SET_PRESSURE_ADVANCE EXTRUDER=extruder ADVANCE=0.05 SMOOTH_TIME=0.04
```

### Linear Advance (Marlin)
```gcode
M900 K0.22       ; Set Linear Advance K-factor to 0.22
M900 K0          ; Disable Linear Advance
```

## Bed Leveling (Advanced)

### Manual Mesh Bed Leveling (Marlin)
```gcode
G28              ; Home first
G29 P1           ; Probe 3x3 grid
G29 P3           ; Interpolate
G29 S0           ; Save mesh
M500             ; Save all settings to EEPROM
; At start of print:
M420 S1           ; Enable bed leveling before G28
; OR load mesh:
M420 S1 Z2        ; Load mesh with 2mm fade height
```

### Z-Offset Calibration
```gcode
M851 Z-1.85      ; Set Z-offset to -1.85mm
M500             ; Save to EEPROM
G28              ; Home (applies offset)
G1 Z0 F300       ; Move to Z0 (should be paper-width above bed)
```

### BLTouch / CR-Touch
```gcode
M280 P0 S10      ; Deploy BLTouch probe
M280 P0 S90      ; Stow BLTouch probe
M280 P0 S120     ; BLTouch self-test (push-pin 3x)
M280 P0 S160     ; BLTouch reset (clear error)
G28              ; Home
G29              ; Auto bed level with BLTouch
```

### UBL (Unified Bed Leveling) — Marlin
```gcode
G28              ; Home
G29 A            ; Activate UBL
G29 L0           ; Load mesh slot 0
G29 J            ; 3-point tilt adjust
G29 P1           ; Probe 3 corners
G29 P3           ; Fill remaining points
G29 S0           ; Save mesh
G29 T            ; Report topology
G26              ; Validate mesh (print test pattern)
```

## Multi-Extruder / Tool Change

### Tool Selection
```gcode
T0               ; Select tool/extruder 0
T1               ; Select tool/extruder 1
T2               ; Select tool/extruder 2
```

### Filament Change (M600)
```gcode
M600             ; Filament change (park, unload, beep for reload)
M600 X5 Y5       ; Filament change with custom park position
```

### Custom Tool Change G-code (Dual Extruder)
```gcode
; Begin toolchange from T0 to T1
G92 E0                          ; Reset extruder
M83                             ; Relative extrusion
G1 E-1.0 F1800                  ; Retract
G1 Z2.0 F300                    ; Lift Z
G1 X5 Y5 F3000                  ; Park position
M104 S0 T0                      ; Cool down old tool
M109 S220 T1                    ; Wait for new tool temp
G1 X{gcode_x} Y{gcode_y} F3000 ; Move to print position
G1 E1.0 F300                    ; Prime new filament
G92 E0                          ; Reset extruder
M82                             ; Absolute extrusion
```

### IDEX / Duplicate Mode
```gcode
M605 S0          ; Full control mode (independent)
M605 S1          ; Duplicate mode (mirror)
M605 S2          ; Mirror mode
```

## Pause & Resume

### Pause Print
```gcode
M0               ; Unconditional stop (Resume on LCD)
M1               ; Same as M0
M25              ; Pause SD print
M226             ; Wait for user input (if supported)
M601              ; Pause (Klipper conditional)
```

### Resume Print
```gcode
M24              ; Resume SD print
M108             ; Break waiting loop
M602              ; Resume (Klipper conditional)
```

### Conditional Pause Script
```gcode
; Pause at current position, retract, park, cool
G92 E0
G1 E-1.0 F1800
G91              ; Relative positioning
G1 Z10 F300      ; Lift Z 10mm
G90              ; Absolute positioning
G1 X10 Y10 F3000 ; Park at front-left
M104 S180        ; Reduce hotend to 180°C (prevent ooze)
M0               ; Wait for user
M104 S210        ; Reheat to printing temp
M109 S210        ; Wait for temp
G1 X{gcode_x} Y{gcode_y} F3000 ; Move back
G1 Z{gcode_z} F300             ; Restore Z
G1 E1.0 F300     ; Prime
G92 E0
```

## Fan Control

```gcode
M106 S255        ; Fan at 100%
M106 S128        ; Fan at 50%
M106 P0 S255     ; Fan 0 at 100%
M106 P1 S128     ; Fan 1 at 50%
M107 P0          ; Fan 0 off
M107             ; All fans off
```

## Speed & Acceleration Control

```gcode
M220 S100        ; Set speed factor override to 100%
M220 S50         ; 50% speed
M221 S95         ; Set flow rate override to 95%
M221 S105        ; 105% flow
M204 P500        ; Set printing acceleration to 500mm/s²
M204 T300        ; Set travel acceleration to 300mm/s²
M203 X5000 Y5000 ; Set max feedrate X/Y to 5000mm/min
M205 X8 Y8       ; Set jerk X/Y to 8mm/s
```

## Steps/mm Calibration

```gcode
M92 X80 Y80      ; Set XY steps/mm (default: 80 for most)
M92 Z400         ; Set Z steps/mm (default: 400 for M8 leadscrew)
M92 E93         ; Set E steps/mm (check your extruder)
M500             ; Save to EEPROM
```

## Custom Macros (Klipper)

Klipper bruker `cfg`-filer for macros. Her er Python-ekvivalenter:

### Klipper `printer.cfg` macroer:
```ini
[gcode_macro CHANGE_FILAMENT]
gcode:
    G92 E0
    G1 E-2 F1800
    G91
    G1 Z10 F300
    G90
    G1 X10 Y10 F3000
    M104 S180
    M0 Wait for filament change
    M109 S210
    G1 E2 F300
    G92 E0
    RESUME

[gcode_macro RESUME]
gcode:
    G1 E1 F300
    G1 X{printer.gcode_move.gcode_position.x} Y{printer.gcode_move.gcode_position.y} F3000
    G1 Z{printer.gcode_move.gcode_position.z} F300
    G92 E0

[gcode_macro BED_MESH_CALIBRATE_FAST]
gcode:
    G28
    BED_MESH_CALIBRATE PROFILE=default METHOD=automatic
    BED_MESH_PROFILE SAVE=default
    SAVE_CONFIG
```

## Custom Calibration Scripts

### Temperature Tower
```gcode
; Temperature tower script (run between layers)
; Layer 1-20: 220°C
M104 S220
G1 Z4.0 F300
; ... print layer ...

; Layer 21-40: 215°C
M104 S215
G1 Z8.0 F300
; ... print layer ...

; Layer 41-60: 210°C
M104 S210
; ... etc ...
```

### Retraction Calibration
```gcode
; Retraction test: vary retraction distance
; Start
G28
M109 S200
G28 Z
G92 E0

; Test 1: 0.5mm retraction
G1 E-0.5 F1800
G1 X50 Y50 F3000
G1 E0.5 F1800
G1 X100 Y50 E5 F1500

; Test 2: 1.0mm retraction
G1 E-1.0 F1800
G1 X50 Y60 F3000
G1 E1.0 F1800
G1 X100 Y60 E5 F1500

; Test 3: 1.5mm retraction
G1 E-1.5 F1800
G1 X50 Y70 F3000
G1 E1.5 F1800
G1 X100 Y70 E5 F1500

; Continue for 2.0, 2.5, 3.0mm...
```

### Flow Rate Calibration
```gcode
; Print single-wall cube, measure wall thickness
; Adjust flow:
M221 S90          ; 90% flow
; ... print ...
M221 S95          ; 95% flow
; ... print ...
M221 S100         ; 100% flow
; ... print ...
M221 S105         ; 105% flow
; ... print ...
```

### PID Tuning
```gcode
; Hotend PID tune
M303 E0 S200 C8  ; 8 cycles at 200°C
M500             ; Save results

; Bed PID tune
M303 E-1 S60 C8  ; 8 cycles at 60°C
M500
```

## Start/End G-code Templates

### Standard Start G-code (Marlin)
```gcode
; Start G-code
G28              ; Home all axes
G29              ; Auto bed level (or M420 S1 to load mesh)
M104 S{material_print_temperature_layer_0}  ; Start heating
M140 S{material_bed_temperature_layer_0}   ; Start heating bed
M109 S{material_print_temperature_layer_0}  ; Wait for hotend
M190 S{material_bed_temperature_layer_0}   ; Wait for bed
G92 E0           ; Reset extruder
G1 Z2.0 F300     ; Move Z up slightly
G1 X5 Y5 F3000   ; Move to prime position
G1 Z0.2 F300     ; Move to first layer height
G1 X100 Y5 E10 F1500  ; Prime line
G1 X100 Y5.4 F3000    ; Wipe
G92 E0           ; Reset extruder
```

### Standard End G-code
```gcode
; End G-code
G91              ; Relative positioning
G1 E-2 F1800     ; Retract
G1 Z5 F300       ; Raise Z
G90              ; Absolute positioning
G1 X10 Y200 F3000 ; Park at front
M104 S0          ; Turn off hotend
M140 S0          ; Turn off bed
M107             ; Turn off fan
M84              ; Disable steppers
```

### Advanced Start G-code (with mesh + purge)
```gcode
; Advanced Start G-code
G28              ; Home
M420 S1 Z2       ; Load mesh, 2mm fade
M104 S[first_layer_temperature]
M140 S[first_layer_bed_temperature]
M109 S[first_layer_temperature]
M190 S[first_layer_bed_temperature]
G28 Z            ; Re-home Z after mesh
G92 E0
G1 Z2.0 F300
G1 X5 Y20 F3000
G1 Z0.28 F300
G1 X60 Y20 E15 F1500   ; Prime line
G1 X60 Y20.4 F3000     ; Wipe
G92 E0
```

## Advanced Techniques

### Vase Mode (Spiralize)
```gcode
; Enable in slicer: Spiral Vase mode
; Or manually:
G92 E0
G1 Z0.2 F300
; Single continuous Z-rise per layer, no retractions
G1 X100 Y100 Z0.4 E5 F1500
G1 X100 Y100 Z0.6 E10 F1500
; ... continuous spiral ...
```

### Multi-Material with Purge Tower
```gcode
; Tool change with purge
T1               ; Switch to tool 1
G92 E0
G1 E-1 F1800     ; Retract
G1 X{purge_x} Y{purge_y} F3000  ; Move to purge tower
G1 E2 F300       ; Purge
G1 X{print_x} Y{print_y} F3000 ; Move to print
G92 E0
```

### Ironing (Top Surface Smoothing)
```gcode
; Enable in slicer: Ironing
; Manual:
G1 Z{layer_height} F300
G1 X50 Y50 F9000  ; Slow move with no extrusion
G1 X100 Y50 F9000
; ... sweep top surface ...
```

### Fuzzy Skin
```gcode
; Enable in slicer: Fuzzy Skin
; Or use post-processing script to add random XY offsets
```

## Klipper-Specific Commands

```gcode
; Moonraker API (HTTP POST)
; http://printer_ip:7125/printer/gcode/script
; Body: {"script": "G28"}

; Klipper G-code
STEPPER_BUZZ STEPPER=extruder  ; Buzz stepper to test
QUERY_ENDSTOPS                 ; Report endstop status
QUERY_PROBE                    ; Report probe status
PROBE_CALIBRATE                ; Calibrate probe Z offset
Z_OFFSET_APPLY_PROBE           ; Apply probe offset
BED_MESH_CALIBRATE             ; Calibrate mesh
BED_MESH_OUTPUT                ; Print mesh data
BED_MESH_PROFILE SAVE=name     ; Save mesh profile
BED_MESH_PROFILE LOAD=name     ; Load mesh profile
BED_MESH_PROFILE REMOVE=name   ; Remove mesh profile
SAVE_CONFIG                    ; Save all to config
RESTART                        ; Restart firmware
FIRMWARE_RESTART               ; Full firmware restart
```

## Post-Processing Scripts (Python)

```python
# Example: Insert filament change at specific layer
import re

def insert_filament_change(gcode, layer_num, change_gcode="M600"):
    """Insert filament change at specified layer."""
    lines = gcode.split('\n')
    result = []
    current_layer = 0
    
    for line in lines:
        if line.startswith(';LAYER:'):
            current_layer = int(line.split(':')[1])
            if current_layer == layer_num:
                result.append(change_gcode)
                result.append(f"; Filament change at layer {layer_num}")
        result.append(line)
    
    return '\n'.join(result)

# Example: Adjust temperature per layer
def temperature_tower(gcode, base_temp, step=-5, layers_per_step=20):
    """Generate temperature tower G-code."""
    lines = gcode.split('\n')
    result = []
    current_layer = 0
    current_temp = base_temp
    
    for line in lines:
        if line.startswith(';LAYER:'):
            new_layer = int(line.split(':')[1])
            if new_layer // layers_per_step != current_layer // layers_per_step:
                current_temp = base_temp + (new_layer // layers_per_step) * step
                result.append(f"M104 S{current_temp} ; Layer {new_layer}")
            current_layer = new_layer
        result.append(line)
    
    return '\n'.join(result)
```

## Common Issues & Fixes

| Problem | G-code Fix |
|---------|-----------|
| Stringing | Increase retraction: `M207 S2.0 F2100` |
| Blobs at seams | Add `M205 J0.015` (jerk control) |
| First layer too close | `M851 Z-0.1` (increase offset) |
| Under-extrusion | `M92 E95` (calibrate E-steps) |
| Over-extrusion | `M221 S95` (reduce flow to 95%) |
| Layer shifting | `M204 P500 T500` (reduce acceleration) |
| Warping | `M140 S65` (increase bed temp), add brim |
| Z-wobble | Check Z-lead screw, add `M205 Z0.5` |
| Hotend ooze during pause | `M104 S180` (cooldown before pause) |
| Mesh not loading | `M420 S1` AFTER `G28` (G28 disables leveling) |

## G-code Validation

```python
def validate_gcode(gcode):
    """Basic G-code validation."""
    issues = []
    lines = gcode.split('\n')
    
    has_home = False
    has_temp = False
    has_mesh = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('G28'):
            has_home = True
        if line.startswith('M104') or line.startswith('M109'):
            has_temp = True
        if line.startswith('G29') or line.startswith('M420'):
            has_mesh = True
        
        # Check for common errors
        if line.startswith('G1') and 'F' not in line and 'E' in line:
            issues.append(f"Line {i+1}: Extrusion without feedrate")
        if line.startswith('M104') and 'S' not in line:
            issues.append(f"Line {i+1}: Temperature without value")
    
    if not has_home:
        issues.append("WARNING: No G28 (home) command found")
    if not has_temp:
        issues.append("WARNING: No temperature commands found")
    
    return issues
```
