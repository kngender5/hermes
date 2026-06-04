# Course Projects — 97TE01I (AUT23)

> Concrete project templates from the course "Programmering og digitalisering i automatiserte systemer" at Fagskolen i Nord.

---

## 2026 — Prosjektoppgave Kontinuasjon: Varemottak og Lager med Heis

**Full assignment text:** `kontinuasjon_oppgave_full.txt`

### System
Warehouse receiving area with a lift that sorts pallets to 3 floors by size.

### Pallet routing
| Size | Destination |
|------|-------------|
| Small | Floor 3 (top) |
| Medium | Floor 2 (middle) |
| Large | Floor 1 (bottom) |

### Sequence states (SeqStep)
| Step | Name | Action | Transition |
|------|------|--------|------------|
| 0 | Initialization | Reset, lift to floor 1 | Safety OK + Start |
| 1 | Wait for pallet | Activate emitter | Pallet detected |
| 2 | Detect size | Read light curtain, set TargetLevel | Exactly 1 signal |
| 3 | Transport to lift | Start conveyor 1+2 | Pallet at lift-in |
| 4 | Stabilize | Stop belts, debounce 100ms | Timer |
| 5 | Lift travel | Run lift, timeout 30s | Level sensor |
| 6 | Stabilize | Stop lift, debounce 100ms | Timer |
| 7 | Transport out | Start floor conveyor | Pallet exit sensor |
| 8 | Stabilize | Debounce 100ms | Timer |
| 9 | Count | Increment counters, CycleDone | Auto |
| 10 | Log | Reset CycleDone | 1 scan |
| 11 | Ready next | Reset sequence | Auto → Step 1 |
| 99 | Alarm | ALL outputs = 0 | Reset → Step 0 |

### Key requirements
- Siemens TIA Portal v19+
- FBD and LAD ONLY (no other languages accepted)
- PC-based HMI (WinCC Flexible Runtime)
- ALL HMI text in Norwegian (legally required)
- CSV logging: date;time;total;small;medium;large
- FactoryIO digital twin (provided, must be completed)
- FAT documented with protocol
- Video (max 15 min): demo + safety handling + code walkthrough

### Programming rules from assignment
- All program code in TIA Portal v19+
- PC-based HMI
- All HMI text in Norwegian (lovpålagt)
- Only FBD and LAD accepted
- Follow course programming techniques (vanntett, TON, SR)
- All comments in Norwegian
