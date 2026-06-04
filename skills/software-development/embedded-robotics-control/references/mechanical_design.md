# Mechanical Design Reference — Unicycle Juggler (2025-05-25)

## Overall Dimensions

    293 × 150 × 703 mm (W × D × H)
    Wheel: Ø406mm (16") pneumatic
    Est. mass: 10-12 kg (with battery)

## Frame

- Material: AL 6060 T-slot extrusion, 25×25 mm
- Vertical tubes: 500 mm long, qty 2
- Cross members: 200 mm long, qty 3
- Motor mount plate: 5mm AL, 83×73 mm
- Battery mount plate: 5mm AL, 160×70 mm

## Component Placement (relative to axle center)

| Component | X (lateral) | Y (fore-aft) | Z (height) |
|-----------|-------------|--------------|------------|
| Wheel center | 0 | 0 | 203 mm |
| Motor | +106 mm | +5 | +250 mm |
| Battery | -100 mm | -25 | +213 mm |
| PCB | +30 mm | -15 | +663 mm |
| Juggle arm servo | -223 mm | 0 | +733 mm |

## Juggling Arm

- Tube: Ø16mm CF or AL, 300mm long
- Servo: MG90S (20×20mm mount)
- Scoop: 60×30mm, 3D printed TPU or 3mm AL
- Oscillation: 1.5 Hz, ±0.5 Nm reaction torque

## Manufacturing Cutting List

| Item | Length | Qty | Material |
|------|--------|-----|----------|
| Vertical frame tube | 500 mm | 2 | T-slot 25×25 AL 6060 |
| Cross member | 200 mm | 3 | T-slot 25×25 AL 6060 |
| Motor mount plate | 83×73 mm | 1 | AL 5mm |
| Battery mount plate | 160×70 mm | 1 | AL 5mm |
| Arm tube | 300 mm | 1 | CF/AL tube Ø16 |

## Hardware BOM (frame only)

| Item | Qty | Note |
|------|-----|------|
| M5x16 button head socket | 16 | Frame joints |
| M5 T-nut for 25×25 T-slot | 20 | Frame assembly |
| M4x12 socket head | 8 | Motor mount |
| M3x10 standoff (F-F) | 4 | PCB mount |
| M3x8 socket head | 8 | PCB, battery plate |
| M5 nyloc nut | 16 | Frame joints |
| 6001-2RS bearing | 2 | Wheel axle |
| Circlip Ø12 | 2 | Axle retention |

## OpenSCAD Generation Pattern

When generating OpenSCAD from Python, pre-compute all values and use list append:

```python
# Pre-compute all numeric values
wd = d['wheel_diameter']
mx = ts/2 + md/2 + 5
axle_y = -(al/2 - ww/2)

# Build OpenSCAD via list append
lines = []
a = lines.append
a(f"wheel_dia = {wd};")        # numeric via f-string
a("cylinder(d=wheel_dia, h=10);")  # OpenSCAD code as plain string
a(f"translate([0, {axle_y}, 0])")  # pre-computed value

# NEVER do this — f-string conflicts with OpenSCAD {variables}:
# scad = f"cube([{plate_t}, {motor_dia}, 10]);"  # NameError!
```
