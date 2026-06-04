# EXAM-PREP: EKOM Exam Solving Patterns (2026-05-26)

## Source Material Patterns

When exam questions reference "Vedlegg 1" with attenuation tables:
- The Vedlegg is typically a table inside a DOCX file (not a separate PDF)
- Extract with: `python3 -c "from docx import Document; doc = Document('FILE.docx'); [print(' | '.join(c.text for c in r.cells)) for t in doc.tables for r in t.rows]"`
- Tables contain: component, calculation formula, LF attenuation, HF attenuation
- Sum all rows to get total attenuation, then subtract from input signal

## Fiber Budget Calculation Pattern

Standard form:
```
Tx (dBm) - [all losses] = Rx (dBm)
```

Always list every component:
1. Splitter loss (given in dB)
2. Fiber attenuation (dB/km x km)
3. Temperature addition (dB/km x km)
4. Splice loss (dB x count)
5. Connector loss (dB x count)
6. Adapter loss (dB x count)
7. System margin (given in dB)

For "dynamic range" questions: calculate Rx for BOTH shortest and longest distance, then subtract.

## Cable-TV Signal Level Pattern

```
Signal_out = Signal_in - Sum_of_all_losses
```

Where losses include:
- Cable attenuation: (dB/100m x length_in_m) / 100
- Splitter tap: dB x count
- Through-pass loss: dB x count  
- Branch/tap loss: dB x count
- Antenna outlet: dB x count

LF and HF are calculated SEPARATELY (different attenuation per frequency).

## Splitter Level Calculation Pattern

For signal level at each output of a splitter:
1. Convert Tx from dBm to mW: P_mW = 10^(dBm/10)
2. Divide by N (splitter ratio): P_per_output = P_mW / N
3. Convert back to dBm: P_dBm = 10 x log10(P_per_output)
4. Attenuation per output = Tx_dBm - P_dBm

## Seperation Distance Pattern

Formula: A = S x P
- S = separation factor (from table, depends on cable class and shielding)
- P = parallel length factor (depends on conduit material)
- Result in mm

## Key Reference Values (EKOM)

### Splitter Loss Table
| Ratio | Loss (dB) |
|-------|-----------|
| 1:2   | 3.0       |
| 1:4   | 6.0       |
| 1:8   | 9.0       |
| 1:16  | 12.0      |
| 1:32  | 15.0      |
| 1:64  | 18.0      |
| 1:128 | 21.0      |
| 1:256 | 24.0      |

### Coaxial Cable Attenuation (RG6)
| Frequency | dB/100m |
|-----------|---------|
| 83 MHz    | 6.4     |
| 865 MHz   | 20.0    |

### Coaxial Cable Attenuation (RG11)
| Frequency | dB/100m |
|-----------|---------|
| 83 MHz    | 3.87    |
| 865 MHz   | 13.0    |

### GPON SFP Classes
| Parameter | B+    | C+    |
|-----------|-------|-------|
| TX (min)  | 1.5   | 3.0   |
| TX (max)  | 5.0   | 7.0   |
| RX        | -28   | -32   |
| Budget    | 29.5  | 35.0  |

### PoE Standards
| Standard | Power/port | Current | Pairs |
|----------|------------|---------|-------|
| 802.3af  | 15.4 W     | 350 mA  | 2     |
| 802.3at  | 30 W       | 600 mA  | 2     |
| 802.3bt  | 60 W       | 910 mA  | 4     |

### Connector Reflectance
| Type  | Reflectance | Color |
|-------|-------------|-------|
| PC    | -40 to -50  | Blue  |
| UPC   | -50 to -55  | Blue  |
| APC   | -60 to -65  | Green |

### Fiber Attenuation by Wavelength
| Wavelength | dB/km (typical) |
|------------|-----------------|
| 850 nm     | 2.5             |
| 1310 nm    | 0.35            |
| 1550 nm    | 0.22            |

## Common Exam Mistakes to Avoid

1. Forgetting temperature addition in fiber calculations
2. Counting splices wrong (cable_length / cable_roll_length + 1)
3. Using wrong attenuation values for LF vs HF in cable-TV
4. Not converting dBm to mW when calculating splitter output levels
5. Forgetting system margin in fiber budget
6. Using 0.35 dB/km for 1550 nm (should be ~0.22)
