---
name: plc-project-planning
description: "End-to-end PLC project planning and documentation for Siemens TIA Portal (LAD/FBD). Covers program planning (I/O list, variable/DB design, sequence control, safety circuit, HMI development plan, data logging) AND writing the functional description document from project source files. Use for warehouse/pallet handling and similar automation projects."
version: 0.4.0
category: plc
triggers:
  - starting a new PLC programming project in TIA Portal
  - need to produce a complete PLC program plan (I/O, DB, sequence, safety, HMI, logging)
  - need to write a functional description (funksjonsbeskrivelse) for a PLC control system
  - need to generate project documentation from source files (I/O list, PLC setup, sequences, safety, HMI plan, FAT plan, user manual)
  - starting a new PLC project that needs handover-ready documentation
  - need to produce documentation a new person can take over without prior knowledge
---

# PLC Project Planning — Siemens TIA Portal (LAD/FBD)

This skill covers the **full lifecycle** of PLC project documentation and planning for Siemens TIA Portal v19+ automation projects:

1. **Program Planning** — Design the complete PLC program: hardware config, variables/DBs, state machine, safety, HMI, logging.
2. **Functional Description** — Produce a structured, point-by-point functional description document from project source files.

Typical projects: warehouse/pallet handling, conveyor systems, automated storage.

---

## PHASE 0: Document-First Setup (BEFORE Coding)

*ALWAYS start with documentation before writing any code. A new person must be able to take over the project without asking the author anything.*

### 0A: Create README.md — The Entry Point

Every project MUST have a `README.md` as the very first file. It is the entry point for anyone new to the project. Include:

1. **What is this project?** — One paragraph explaining what the system does, in plain language
2. **How to read this documentation** — Numbered reading order for new persons (README first, then funksjonsbeskrivelse, then io_liste, then program blocks...)
3. **File structure** — Tree diagram of the project folder
4. **Technical choices** — PLC model, programming language, HMI platform, communication protocol, software versions
5. **Reading list for new persons** — Table mapping "I need to know X" → "Read file Y"
6. **Contact info** — Who to ask about what

**CRITICAL:** Write the README as if the reader has NEVER seen this project and has NO access to you. Every document must be self-contained.

### 0B: Create Complete Document Set

Before writing any PLC code, produce these documents in order:

| # | Document | File | Purpose |
|---|----------|------|---------|
| 1 | README.md | `README.md` | Entry point — project overview |
| 2 | Funksjonsbeskrivelse | `funksjonsbeskrivelse.md` | How the system works |
| 3 | I/O-liste | `io_liste.md` | All signals, addresses, locations |
| 4 | Programstruktur | `programstruktur.md` | OB/FC/FB/DB connections |
| 5 | Programsekvenser | `programsekvenser.md` | State machine step-by-step |
| 6 | Sikkerhetskrets | `sikkerhetskrets.md` | Safety system documentation |
| 7 | HMI-plan | `hmi_plan.md` | Operator screens and tags |
| 8 | Datalogg | `datalogg.md` | CSV logging format |
| 9 | FAT-testplan | `fat_testplan.md` | Acceptance test |
| 10 | Bruksanvisning | `bruksanvisning.md` | Operator manual |
| 11 | TIA Portal-oppsett | `oppsett_tia_portal.md` | How to create the TIA project |

### 0C: Language Standard

- **ALL documentation, comments, reports, manuals, and HMI text MUST be in Norwegian (bokmål)**
- This is both a course requirement and a legal requirement for HMI systems in Norway
- Use consistent Norwegian technical terminology:
  - "nødstopp" (never "nødstans" or "nødstoppbryter")
  - "funksjonsbeskrivelse", "bruksanvisning", "sekvensstyring", "tilstandsmaskin"
  - "transportør", "heis", "emitter", "lysgitter", "dørsensor", "pall"

---

## PHASE 0E: Pre-Submission Checklist

*Before submitting the project, verify ALL of these items:*

- [ ] **NO .scl files exist anywhere in the project** — delete them all
- [ ] All program blocks are in LAD/FBD format (`.txt` build guides or TIA Portal blocks)
- [ ] Dørsikkerhet is SELECTIVE (not global) — check FB3 has separate door stop outputs
- [ ] Tømme-funksjon per etasje is implemented (FC_Tøm_Etasje or equivalent)
- [ ] Floor shift logic is documented (even if just counting, not position tracking)
- [ ] IO_LISTE.xlsx and TAGLISTE.xlsx are generated and up to date
- [ ] All documentation files are version 2.0+ with correct dates
- [ ] README.md file structure matches actual project structure (no stale SCL references)
- [ ] Norwegian characters (Ø/Æ/Å) are correct in ALL files — run sed check
- [ ] Subagent-generated files have been audited for naming errors
- [ ] FAT testplan includes door selective stop test case
- [ ] HMI plan includes tømme-knapper and door alarm descriptions

## PHASE 1: Program Planning

*Use this phase when starting a new PLC project or when you need to produce a detailed plan before implementation.*

### 1. Understand the Specification

- Read the project description (PDF, text, or images) **in its entirety** before making any assumptions.
- Extract key functions: sensor/actuator list, sequence of operations, safety requirements (emergency stop, area sensors, alarm, reset), HMI screens, data to log.
- If the source is a scanned PDF, apply OCR (e.g., `tesseract` with language `nor+eng`) to obtain editable text.

**CRITICAL PITFALL — "Kontinuasjon" does NOT mean "same project":**
- In Norwegian course contexts, "Prosjektoppgave — Kontinuasjon" is often a **completely new project** that builds on the *competence* from previous work, not a continuation of the same system.
- **ALWAYS read the full assignment spec** before assuming any overlap with previous projects.
- Example: AUT23 2025 Prosjektoppgave was a package sorting system with robots. AUT23 2026 Kontinuasjon is a warehouse with a lift and 3 floors — **totally different systems** with no I/O or code reuse.
- **NEVER** copy I/O lists, DB structures, or sequence steps from a previous project into a new one without verifying each item against the new spec.
- If the assignment references previous work (e.g., "bruk TIA-prosjektet fra AK4"), identify exactly which components are reusable vs. which must be redesigned.

### 2. Create the TIA Portal Project

- **Project Name**: Choose a descriptive name (e.g., `Varemottak_Lager_AUT23`).
- **PLC Model**: Select the appropriate S7-1500 (or other) model available in your lab.
- **Programming Language**: Set to LAD and/or FBD (only these are allowed per spec).
- **Tip**: Use a consistent naming convention for blocks (FC/FB, DB, UDT).

**CRITICAL PITFALL — SCL is NOT allowed for AUT23 Prosjektoppgave/Kontineulasjon:**
- The AUT23 course spec (kontinuasjon_key_facts) explicitly states: "Språk: FBD og LAD (**KUN disse to**)"
- SCL (Structured Control Language) is a **text-based Pascal-like language** — NOT the same as LAD (ladder) or FBD (function block diagram)
- SCL files CAN exist as reference/scratch in a `scl/` subfolder, but the **actual TIA Portal project MUST use FBD and/or LAD** for all submission blocks
- Do NOT submit a project with .scl files as the primary code — it will be rejected or graded as non-compliant
- TIA Portal CAN import SCL, but auto-conversion to FBD/LAD is imperfect — manual rewrite is usually needed
- If you have extensive SCL code from previous work, use it as **reference documentation** for the logic, then re-implement in FBD/LAD inside TIA Portal

### 3. Hardware Configuration (HW Config)

- Add modules matching the I/O list:
  - Digital inputs for start/stop, emergency stop, reset, emitter sensor, size detection, door/area sensors, level sensors, pallet detection at lift in/out, removal sensors.
  - Digital outputs for transport belts, lift up/down, alarm lamp, run lamp, tower lights (green/yellow/red per section), and any spare.
- **ALWAYS reserve I/O addresses for future expansion:** Reserve ~10-20% extra addresses beyond what the current spec requires. Group reservations by type (DI/DO/AI/AQ), prefix with `RESV_`, document plausible future uses, mark status "RESERVERT". This prevents complete I/O redesign when new sensors/actuators are added.
- Addressing: Use the byte.bit format (e.g., `%I0.0`, `%Q0.0`) and note that addresses can be adjusted later.
- Configure PROFINET interface for HMI (WinCC Flexible Runtime) connection.

### 4. Define Variables and Data Blocks (DB)

Create the following DBs (numbers are suggestions; adjust as needed):

| DB | Purpose | Variables (Name, Type, Description) |
|----|---------|--------------------------------------|
| DB1 | **Counter Register** | `TotalEsker` (INT) – total pallets received<br>`Esker_Liten` (INT) – pallets small size<br>`Esker_Medium` (INT) – pallets medium size<br>`Esker_Stor` (INT) – pallets large size |
| DB2 | **Alarm Register** | `Safety_OK` (BOOL) – 1 when no E-stop or door sensor active<br>`Alarm_Nødstopp` (BOOL) – emergency stop triggered<br>`Alarm_Dør1-3` (BOOL) – door open alarms<br>`Alarm_HeisTimeout` (BOOL) – lift timeout<br>`Alarm_StorrelseFeil` (BOOL) – size detection error<br>`Alarm_EmitterTimeout` (BOOL) – emitter timeout<br>`Alarm_FullEtasje[3]` (BOOL) – floor full<br>`Alarm_Count` (INT) – number of active alarms |
| DB3 | **HMI & Control Variables** | `Cmd_Start/Stop/Reset` (BOOL) – HMI commands<br>`Cmd_Emitter_OnOff` (BOOL) – emitter control<br>`Cmd_TømEtasje[3]` (BOOL) – manual empty per floor<br>`SeqStep` (INT) – current sequence step (0-11, 99 for alarm)<br>`TargetLevel` (INT) – destination floor (1=bottom,2=middle,3=top)<br>`PallCount_Etasje[3]` (INT) – pallet count per floor<br>`HeisNåværendeNivå` (INT) – current lift level<br>`CycleDone` (BOOL) – one-scan pulse after full cycle<br>`AnleggStatus` (INT) – 0=Off,1=Drift,2=Standby,3=Alarm |
| DB4 | **Configuration** | `Max_Pall_Etasje[3]` (INT) — max pallets per floor<br>`Heis_Hastighet_Normal` (INT) — normal speed %<br>`Heis_Hastiguet_Kritisk` (INT) — critical speed %<br>`Timeout_Heis_Sek` (INT) — lift timeout<br>`Timeout_Emitter_Sek` (INT) — emitter timeout<br>`Deketek_Tid_MS` (INT) — debounce time |

- Add meaningful comments (in Norwegian) to each variable.
- Use UDTs where appropriate for structured data.
- Retain: DB1 (counters) and DB4 (config) should have Retain enabled.

### 5. Develop the Control Sequence (State Machine)

Implement the main sequence as a state machine using an integer variable (`SeqStep`) or a block-structure with jumps. Typical steps:

| SeqStep | Description | Key Actions | Exit Condition |
|---------|-------------|-------------|----------------|
| 0 | **Initialization** | Reset outputs, counters; move lift to home (floor 1) | No alarm AND Start button = 1 |
| 1 | **Wait for Infeed** | Activate emitter; wait for pallet sensor | Emitter sensor = 1 |
| 2 | **Detect Size** | Read size sensors; validate exactly 1 active; set TargetLevel | Exactly one size signal active |
| 3 | **Transport to Lift** | Start infeed belt + lift entry belt | Pallet at lift-in sensor |
| 4 | **Wait Lift-In** | Stop belts; debounce 100ms | Timer elapsed |
| 5 | **Lift Travel** | Determine direction; start lift; timeout 30s | Level sensor = target OR timeout → alarm |
| 6 | **Wait Position** | Stop lift; debounce 100ms | Timer elapsed |
| 7 | **Transport Out** | Start correct outbound belt per TargetLevel | Pallet exit sensor |
| 8 | **Wait Outfeed** | Debounce 100ms; increment pallet count | Timer elapsed |
| 9 | **Count** | Increment total + size counter; set CycleDone | Automatic |
| 10 | **Log** | After 1 scan, reset CycleDone | 1 scan |
| 11 | **Reset for Next Cycle** | Stop belts; return lift to home; check emitter status | Ready for next |
| 99 | **Emergency Stop / Alarm** | ALL outputs = 0; alarm lamp = 1; await E-stop release + reset | E-stop released AND reset pressed → go to step 0 |

**DEBOUNCING IS MANDATORY — ALL sensor signals used for decisions MUST be debounced with TON timers:**

| Signal Type | Debounce Time | Notes |
|-------------|--------------|-------|
| Emergency stop buttons | **0 ms** | IMMEDIATE — NEVER debounce safety! |
| Door sensors | 50 ms | Fast but filters contact bounce |
| Photocells (pallet detection) | 100 ms | Standard for conveyor belts |
| Level sensors (lift) | 100 ms | Stabilization after movement |
| Size sensors (light curtain) | 150 ms | Wait for stable measurement |
| Start/Stop buttons | 200 ms | Operator-activated — add buffer |

**SELF-HEALING — Design auto-recovery where safe:**
- Transient errors (pallet jam, sensor glitch): Wait configured time, re-check condition, auto-recover if cleared
- Critical errors (lift timeout, mechanical fault): **NO auto-recovery** — require operator reset
- Use TON timers for ALL wait periods — never use raw signal edges for transitions

- Implement each step as its own FC (or use FC1_SeqManager to select) using LAD/FBD.
- Use modular FBs (FB1 for motor control, FB2 for lift, FB3 for safety) to improve reusability.
- Add comments in Norwegian on every network or block.

### 6. Safety Circuit Logic

- Wire all emergency stop buttons and door/area sensors as normally-closed (NC) series to derive `Safety_OK`.
- Use `Safety_OK` to gate ALL motion-critical outputs. SINGLE POINT OF FAILURE: if Safety_OK = 0, nothing moves.
- Alarm handling:
  - Set individual alarm bits per safety source (for HMI detail)
  - Drive HMI alarm lamp and tower lights from aggregated alarm state
  - Reset ONLY when `Safety_OK = 1` AND reset button pressed (one-scan pulse)
  - Reset button is PHYSICAL — NOT from HMI
- Document fail-safe behavior: loss of power or broken wire → input = 0 → safe state

### 7. HMI Concept (WinCC Flexible Runtime)

- **Minimum 3 screens required by spec:**
  1. **Main Overview** — System layout, pallet counts per floor, controls
  2. **Alarm Screen** — Active alarms with Norwegian descriptions
  3. **Alarm Log** — Historical alarms with timestamps
- **Recommended 4th screen:** Settings (password-protected)
- **Tags**: Link HMI tags to PLC DB variables (DB3 for commands, DB1 for counters, DB2 for alarms)
- **Language**: ALL on-screen text in Norwegian
- **Update Rate**: 500 ms
- **Data Logging to CSV**:
  - Use VBScript triggered by `CycleDone` pulse
  - Format: `DD.MM.YYYY HH:MM:SS;Total;Liten;Medium;Stor`
  - Optional: new file per day (`EskerLogg_YYYYMMDD.csv`)

### 8. Complete File Structure

```
prosjektoppgave/
├── README.md                          ← Entry point (READ FIRST)
├── funksjonsbeskrivelse.md           ← System description
├── io_liste.md                        ← I/O list with reserved addresses
├── programstruktur.md                 ← OB/FC/FB/DB overview
├── programsekvenser.md                ← Step-by-step state machine
├── sikkerhetskrets.md                 ← Safety system
├── hmi_plan.md                        ← Operator screens
├── datalogg.md                        ← CSV logging
├── fat_testplan.md                    ← Acceptance test
├── bruksanvisning.md                  ← Operator manual
├── oppsett_tia_portal.md              ← TIA Portal setup guide
│
├── program/
│   ├── plc/
│   │   ├── ob/    OB1, OB100
│   │   ├── fc/    FC1-FC5, FC_Step0-11, FC_AlarmStep
│   │   ├── fb/    FB1, FB2, FB3
│   │   └── db/    DB1-DB4, DB10-DB12
│   ├── hmi/       Screens, tags, VBScript
│   └── factory_io/  Digital twin
├── io/            I/O Excel list
├── sekvensdiagrammer/  Sequence diagrams
└── test/          FAT protocol
```

---

## PHASE 2: Writing the Functional Description

*Use this phase when you have project source files and need to produce a complete, point-by-point functional description (funksjonsbeskrivelse) for a PLC-based control system.*

### Prerequisites

- Access to source files (typically in `~/Output/Prosjektoppgave/` or similar):
  - I/O-liste, PLC-oppsett-plan, Program_sekvenser, Sikkerhetskrets-dokumentasjon
  - HMI-utviklingsplan, Konfigurasjonsoppsummering, FAT-testplan, Bruksanvisning
- Optional: block diagrams, P&ID, hardware specifications.

### Procedure

#### Step 1: Collect and Read Source Files
Read each file sequentially to build a system overview. Note:
- I/O addresses and descriptions (sensors, actuators)
- Data blocks (DB names, variables, data types, purpose)
- Sequence steps (state machine, actions per step, transition conditions)
- Safety circuit (E-stop, door/area sensors, reset logic, alarm handling)
- HMI structure (tag mapping, screens, alarm display, logging)
- Test requirements (FAT) and user procedures (operating manual)

#### Step 2: Determine Document Structure
A typical functional description contains:
1. Innledning og formål
2. Systemoversikt (overall function, block diagram description)
3. Maskinvare og I/O (detailed I/O list with reserved addresses, address allocation, signal types)
4. Programmstruktur (PLC platform, language, data blocks, sequence control)
5. Sikkerhetskrets (physical wiring, PLC logic, alarm handling)
6. HMI-kobling (communication, tag structure, screens, logging)
7. Testing og overlevering (FAT plan, operating manual, maintenance)
8. Konklusjon

#### Step 3: Write Section by Section
- Summarize relevant facts from source files for each section.
- Provide a brief justification for every technical choice (e.g., why a specific I/O address was chosen, why a specific data type was used, why a specific sequence logic was chosen).
- Keep text in Norwegian, technically precise, and avoid unnecessary flourish.
- Number sub-points for readability (e.g., 3.1 Datablokker, 3.2 Sekvensstyring).

#### Step 4: Format and Deliver
- Save as `.txt` or `.md` depending on requirements.
- Use headings (`#`, `##`, `###`) for clear hierarchy.
- Insert code examples or excerpts from source files where they clarify the description.
- Verify all important variables, I/O addresses, and sequence steps are mentioned at least once.

#### Step 5: Quality Check
- Verify every source file is represented.
- Verify every technical choice has an associated justification.
- Verify language is consistently Norwegian.
- Verify the document is readable by both technicians and decision-makers.
- Verify the document is comprehensible WITHOUT access to the original author.

### Extraction Guide by Source File

See `references/extract_info_from_sources.md` for a detailed breakdown of what to extract from each source file type.

### Example Document Structure

See `references/example_structure.md` for a structural template.

### Course Project Examples

See `references/course-projects-97TE01I.md` for complete I/O lists, DB designs, state machines, and HMI concepts from AUT23 course projects (97TE01I).

---

## Phase 0D: TIA Portal v19 Import Files (XML/CSV)

*Always generate machine-readable import files alongside documentation. This lets the next programmer import variables directly into TIA Portal instead of typing them manually.*

### PLC Variable XML Format (TIA Portal v19)

Use this exact format for `io/plc_variabler_tia.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<PlcTags>
  <PlcTag Name="START_KNAPP" DataType="Bool" Address="%I0.0" Comment="Start-knapp. NO." />
  <!-- ... more tags ... -->
</PlcTags>
```

Key attributes per tag:
- `Name` — Variable name (use Norwegian descriptive names)
- `DataType` — `Bool`, `Int`, `DInt`, `Real`, `Array[1..3] of Int`, etc.
- `Address` — PLS address with `%` prefix: `%I0.0`, `%Q0.0`, `%IW64`, `%QW80`, `%M0.0`
- `Comment` — Norwegian description of what the signal does

TIA Portal v19 import: PLC variables table → Right-click → Import → select `.xml` file.

### HMI Tag XML Format

Use for `io/hmi_tags.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HmiTags>
  <HmiTag Name="HMI_TotalPaller" DataType="Int" Source="DB1.TotalPaller" Comment="Total paller" />
</HmiTags>
```

Key attributes: `Name`, `DataType`, `Source` (PLC variable path), `Comment`.

### CSV Alternative (Excel-friendly)

Also generate `.csv` files with semicolon separator (Norwegian Excel format):
- `io/plc_variabler.csv` — Header: `Navn;Datatype;Adresse;Kommentar`
- `io/hmi_tags.csv` — Header: `Navn;Datatype;Kilde (PLS);Kommentar`
- `io/datablokker.csv` — DB structure with variables, types, start values

### DB Variable CSV Format

For `io/datablokker.csv`, list each DB as a section:

```
DB1 — Telleregister (RETAIN)
Variabel;Datatype;Startverdi;Kommentar
TotalPaller;Int;0;Totalt antall paller
...
```

---

## Workflow: Capturing Knowledge from Lectures/Recordings

When processing lecture recordings, transcripts, or course material, if a specific workflow,
methodology, or structured procedure is described in detail (e.g., a TIA Portal setup
sequence, a HMI tag-mapping procedure, a PROFINET configuration workflow):

1. Extract the step-by-step procedure from the transcript/SRT
2. Verify against official documentation where possible
3. Create a new class-level skill via `skill_manage(action='create')`:
   - Name at the class level (e.g., `tia-portal-hmi-setup`, not `lecture-3-workflow`)
   - `references/` for session-specific details (quotes, timestamps, source attribution)
   - Pitfalls section for known gotchas
4. Update the extraction log with the skill creation reference

This ensures reusable knowledge from lectures is captured for future sessions, not lost
in temporary transcript extracts.

---

## PHASE 3: Simulation & Testing with S7-PLCSIM

*Use this phase after PLC code is compiled and ready for testing. Simulation catches logic errors before physical commissioning.*

### 3A — Quick Test with S7-PLCSIM V20 (No License Required)

PLCSIM V20 comes free with TIA Portal V19. Covers 80% of test needs.

**Setup:**
1. Open TIA project → Compile (no errors)
2. Online → Extended Download to Device
3. PG/PC Interface: `PLCSIM.TCPIP.1` → Start Search → Select simulated CPU
4. Load program → RUN mode

**SIM Tables (manual I/O test):**
- Create SIM table for inputs (sensors) and outputs (actuators)
- Toggle input bits to simulate sensor states
- Observe output responses in real-time
- Test each sequence step: e.g. toggle emitter sensor → verify belt starts → toggle lift sensor → verify lift moves

**Sequence Editor (automated test sequences):**
- Define timed sequences: Set input X at T=0ms, clear at T=2000ms
- Run unattended to verify multi-step sequences
- Useful for: full pallet cycle, alarm injection, reset behavior

**Virtual Time Scaling:**
- Default 1x = real-time
- 0.1x = 10x slower (good for observing fast timers)
- 2x+ = faster (good for long-duration tests like fill-all-floors)

**Essentials View:**
- Minimizes PLCSIM to just the instance list
- Pin it to keep visible while working in TIA

### 3B — Advanced Simulation with S7-PLCSIM Advanced V7.0 (Requires License)

Needed for: HMI simulation, multi-PLC, co-simulation, OPC UA/Modbus TCP testing.

**Key differences from PLCSIM V20:**
- Virtual PLC has its own IP stack (Softbus or real NIC)
- WinCC Unified HMI can connect over TCP/IP to simulated PLC
- Up to 16 parallel virtual instances
- Runtime API for C# co-simulation

**Co-Simulation Architecture:**
```
C# Application ←→ Runtime API (.NET DLL) ←→ PLCSIM Advanced Runtime Manager
     ↓                    ↓
  Simulated plant    Virtual PLC instance
  (sensors/motors)   (runs actual PLC code)
```
- Data sync on every PLC cycle (OnSyncPointReached event)
- C# reads PLC outputs → simulates plant response → writes PLC inputs
- Can inject errors (sensor failures, mechanical faults) for alarm testing

**Included Siemens Examples (from Siemens Industry Online Support Entry 109739660):**
- `109739660_PLCSIM_ADV_COSIM_APPL_V1_0.2.zip` — C# co-simulation project (Visual Studio 2022)
- `109739660_PLCSIM_ADV_Display_1.0.2.zip` — Display panel simulator (rarely needed)
- `109739660_PLCSIM_ADV_GettingStarted_v1.0.2.pdf` — Full walkthrough

### 3C — Recommended Test Sequence for Warehouse/Lager Projects

Test in this order (each step before proceeding):

| # | Test | Tool | What to Verify |
|---|------|------|----------------|
| 1 | I/O Check | PLCSIM V20 + SIM tables | Every input toggles, every output responds |
| 2 | Safety Circuit | PLCSIM V20 | E-stop → all motion stops; door open → alarm; reset → recovery |
| 3 | Single Cycle | PLCSIM V20 + sequence editor | One pallet: infeed → size detect → lift → outfeed → count |
| 4 | All Sizes | PLCSIM V20 | Small/medium/large routing to correct floor |
| 5 | Floor Full | PLCSIM V20 | Floor full alarm, no more pallets routed there |
| 6 | Lift Timeout | PLCSIM V20 | Timeout alarm triggers, requires manual reset |
| 7 | Continuous Run | PLCSIM V20 (time scale 2x+) | Multiple pallets, no missed counts, no deadlocks |
| 8 | HMI Integration | PLCSIM Advanced V7.0 | Screens update, commands work, alarms display |
| 9 | Error Injection | Co-simulation | Package drop, sensor fault → alarm → ack → resume |
| 10 | FAT Protocol | Physical or simulated | Full acceptance test per `fat_testplan.md` |

### 3D — Known PLCSIM Issues & Workarounds

| Issue | Cause | Fix |
|-------|-------|-----|
| Download fails with NTP error | NTP time sync enabled in CPU config | Disable NTP in device configuration |
| Timeout on large arrays | HMI-visible arrays create thousands of tags | Reduce array size or split into smaller arrays |
| Instance not found | PLCSIM Advanced not running | Start PLCSIM Advanced or use PLCSIM V20 UI first |
| Softbus communication fails | Network mode mismatch | Set `ENetworkMode.Softbus` in API or select Softbus in UI |

---

## Phase 4: SCL → LAD/FBD Konverting

*Use this phase when you have SCL code that must be converted to LAD/FBD for TIA Portal submission.*

The AUT23 course spec explicitly states: "Språk: FBD og LAD (KUN disse to)". SCL files may exist as reference documentation, but the actual TIA Portal project MUST use FBD and/or LAD for all submission blocks.

### Procedure

1. Keep original SCL files in `scl/` folder as reference (DO NOT delete)
2. Create a parallel `ladder-FB/` folder with same ob/fb/fc/db structure
3. For each SCL file, create a `.txt` file with visual LAD/FBD text descriptions
4. Each text file contains:
   - Header (project, version, date)
   - For each network: title, function description, LAD/FBD visual notation, build instructions
5. Use the visual notation conventions documented in `references/scl-to-lad-fbd-conversion.md`
6. Delegate to subagents in batches of 4-6 files each (max 3 concurrent subagents)
7. DB files are NOT networks — create table-formatted structure listings with member names, types, start values
8. **ALWAYS verify subagent output for Norwegian character encoding** — see pitfall below

### IO Cross-Reference Verification (MANDATORY after conversion)

After generating ladder-FB files, ALWAYS cross-reference against the `io/` XML files:

1. Parse `io/plc_variabler_tia_v2.xml` → build lookup: `navn → (adresse, datatype, kommentar)`
2. Parse `io/hmi_tags_v2.xml` → build lookup: `hmi_tag → (source, datatype, kommentar)`
3. Scan ALL ladder-FB `.txt` files for:
   - `%I`, `%Q`, `%IW`, `%QW` address references — verify they match XML
   - `"NAVN"` quoted name references — verify they exist in XML or DB
4. Run a diff script to find:
   - **Used in ladder-FB but NOT in XML** → likely a naming error (e.g., `NIVAA` vs `NIVÅ`)
   - **In XML but NOT in ladder-FB** → IO point not yet implemented in program
5. Generate `io/IO_LISTE.txt` — complete IO list (navn + adresse + kommentar) grouped by type
6. Generate `io/TAGLISTE.txt` — full tag list with tag-ID prefixes (DI_01, DO_01, AI_01, etc.)

**CRITICAL — DO NOT modify ladder-FB source files during verification.** When the user asks to cross-reference and fix naming issues, the correct workflow is:
- Fix naming errors in ladder-FB files (these are generated reference docs, not source code)
- BUT do NOT restructure, reformat, or "improve" ladder-FB files beyond what was asked
- If the user says "just ensure names match" — ONLY fix names, don't touch structure or content
- Keep original SCL files in `scl/` completely untouched — they are the canonical source
- The ladder-FD files in `ladder-FB/` are build guides for TIA Portal, not the program itself

**Norwegian character check after subagent delegation:** ALWAYS scan subagent output for Ø/Æ/Å corruption. Subagents frequently produce `TRANSPORTOER` (should be `TRANSPORTØR`), `NIVAA` (should be `NIVÅ`), `SAEKERHET` (should be `SIKKERHET`). Use `sed -i 's/TRANSPORTOER/TRANSPORTØR/g; s/NIVAA/NIVÅ/g; s/OER/ØR/g; s/AA_/Å_/g' filename.txt` across ALL subagent-generated files before delivery.

### Generating IO_LISTE.txt and TAGLISTE.txt

## Tips & Pitfalls

- **Use IEC timers** (TON, TOF, TP) from the *Extended Instructions* library rather than legacy S5 timers.
- **Keep the sequence modular** — each major step as its own FC with clear inputs/outputs.
- **Do not wire emergency stop or door sensors in parallel** — series-NC wiring ensures fail-safe behavior.
- **Avoid using the same input for both safety and normal control** without proper gating; always gate motion outputs with `Safety_OK`.
- **When using OCR on scanned PDFs**, verify Norwegian characters (æ, ø, å) — use `nor` language pack for tesseract.
- **In sequence control**, ensure lift movement to home position is properly interlocked to prevent starting a new cycle while the lift is still moving.
- **Do not copy raw text from source files directly** — rephrase and add justification; raw copy makes the functional description less valuable.
- **Keep sections short and focused** — each section should not exceed 300-400 words except for appendices.
- **Use consistent Norwegian terminology** (always "nødstopp" not "nødstans" or "nødstoppbryter").
- **For HMI mockups**, add viewport meta tag for responsiveness, `role="alert"` on alarm banners, and explicit `type="button"` on buttons.

### Behavioral Pitfalls

- **DO NOT modify ladder-FB files during IO verification.** When the user asks to cross-reference and document IO, the correct workflow is: (1) verify names match between ladder-FB and IO XML, (2) fix ONLY naming errors in ladder-FB (e.g., `NIVAA`→`NIVÅ`, `TRANSPORTOER`→`TRANSPORTØR`), (3) generate IO_LISTE.txt and TAGLISTE.txt as separate files, (4) do NOT restructure, reformat, or "improve" ladder-FB files beyond what was explicitly asked. The ladder-FB files are build guides, not source code — keep changes minimal and targeted.
- **Use the endringslogg workflow from `plc-change-log` skill:** Every PLC project MUST have an `endringslogg.md`. Read it at the start of each session. Update it at the end. Never start work without noting the taskID.
- **STAY ON TASK — verify before investing effort:** Before spending time on browser automation, SSO logins, or complex tool chains, always check if the material is already available locally. User downloads to Windows (`/mnt/c/Users/rkarl/Downloads/`) may already contain what you need. Search local filesystem first.
- **When user says "check progress" or "I've already done X":** STOP. Verify current state before continuing planned work. Do not re-do work that is already complete. Do not assume — list the actual files that exist.
- **Handover-ready documentation is a first-class requirement:** When user asks for documentation a new person can take over: (1) README as self-contained entry point, (2) every document describes system without assuming prior knowledge, (3) I/O lists are self-documenting with physical locations, (4) Norwegian language throughout, (5) document numbers (FB-001, IO-001, etc.) for traceability.
- **Debouncing is NOT optional:** All sensor signals used for program decisions MUST be debounced with TON timers. Raw signal edges cause phantom transitions. Emergency stops are the ONLY exception (0 ms).
- **Self-healing where safe, manual for critical:** Transient errors should auto-recover after wait time. Critical errors MUST require operator reset — never auto-recover from potentially dangerous conditions.
- **I/O reservation pattern:** Always reserve 10-20% extra I/O addresses. Prefix with `RESV_`, document plausible future uses, mark "RESERVERT". Group by type (DI/DO/AI/AQ).
- **"Kontinuasjon" ≠ "same project":** Always read the full spec. Norwegian course "Kontinuasjon" projects are often completely new systems that only share competence (not code or I/O) with previous work.
- **SCL ≠ LAD ≠ FBD — know your PLC languages:**
  - SCL = text-based, Pascal/Ada-like syntax (NOT allowed for AUT23 submission)
  - LAD = graphical ladder diagram (relay logic, coils/contacts)
  - FBD = graphical function block diagram (boxes, wires, signals)
  - STL = text-based assembler-like (low-level, rarely used)
  - When the spec says "FBD og LAD (KUN disse to)" — it means EXACTLY those two graphical languages
  - In conversation, user may say "SCL" when they mean the general PLC code — verify which spec they actually need before writing code
- **Norwegian character encoding (Ø/Æ/Å) in subagent output — ALWAYS verify:**
  - Subagents frequently corrupt Norwegian special characters:
    - `Ø` → `OE` or `O` (e.g., `TRANSPORTØR` → `TRANSPORTOER`, `NIVÅ` → `NIVAA`)
    - `Æ` → `AE` (e.g., `SAEKERHET` instead of `SIKKERHET`)
    - `Å` → `AA` (e.g., `STORRELSE` → Storrelse is OK, but `NIVÅ` → `NIVAA` is wrong)
  - **ALWAYS run a Norwegian character check** after subagent completion:
    - Search for `OER`, `AA_`, `OE_` patterns that should be `ØR`, `Å_`, `Æ_`
    - Common corrections: `TRANSPORTOER_*` → `TRANSPORTØR_*`, `HEIS_NIVAA_*` → `HEIS_NIVÅ_*`
    - Use `sed -i 's/TRANSPORTOER/TRANSPORTØR/g; s/NIVAA/NIVÅ/g' filename.txt`
  - TIA Portal tag names MUST use correct Norwegian characters — matching the XML import files exactly
  - When generating IO files or tag lists, copy Norwegian names from a known-good source (XML) rather than retyping
- **Excel export pattern**: When user asks for `.xlsx` exports of IO/tag/DB data, use `openpyxl` with color-coded sheets. See `references/excel-export-pattern.md` for formatting template, color codes, column widths, and freeze pane setup.
- **Generate import files, not just docs:** Always produce XML/CSV import files (plc_variabler_tia.xml, hmi_tags.xml, datablokker.csv) alongside documentation. The next programmer should import variables directly into TIA Portal rather than typing them manually. See Phase 0D.
- **ALWAYS generate `io/TIA_Import_All.xml`** — UDTs, DBs, User Constants, block interfaces (no code). See `references/tia-portal-xml-import-format.md` for the XML schema and naming conventions.
- **ALWAYS generate `io/Tags_Import.xlsx`** — UDT-based tag list for HMI import
- **ALWAYS define User Constants** — STEP_x, TARGET_x, STATUS_x, ALARM_xxx (no magic numbers)
- **ALWAYS use UDTs for DBs** — UDT_Alarm, UDT_Sikkerhet_Sensor, UDT_Motor_Inst, UDT_Heis_Inst, UDT_Etasje, UDT_HMI_Kommando, UDT_HMI_Status, UDT_Prosess_Alarm, UDT_Konfig_Tid, UDT_Konfig_Heis, UDT_Konfig_Analog

- **Convert data sources to Excel for human review:** When the user asks for `.xlsx` exports of project data (IO lists, datablokker, PLC/HMI variable lists), use the `excel-generation` skill. This produces formatted, color-coded workbooks with side-by-side V1/V2 comparison and diff sheets from CSV/XML sources.e documentation. The next programmer should import variables directly into TIA Portal rather than typing them manually. See Phase 0D.
- **Subagent file naming discipline:** When delegating program block creation to subagents, verify file names match the calling convention (e.g., SeqManager calls FC_Step5_HeisTilEtasje but subagent may create FC_Step4_HeisTilEtasje). Subagents use different numbering. ALWAYS audit and rename files after delegation.
- **Handover-ready standard — the "next person" test:** Every document must be written as if the reader has NEVER seen this project and has NO access to the author. Before finishing any session, ask: "Can a new person take over from this documentation alone, without asking me anything?" If not, add the missing context. This applies to: README.md (entry point with numbered reading order), all .scl files (Norwegian comments explaining WHY not just WHAT), endringslogg.md (current state and next steps), and io_liste.md (signal descriptions with physical location).

- **Dørsikkerhet er SELEKTIV, ikke global:** Dørsensorer stopper KUN transportører innenfor 2m rekkevidde. Nødstopp stopper HELE anlegget. Dette er en kritisk sikkerhets-endring — IKKE bland dem sammen i én Safety_OK-variabel. Ha separate utganger: `Safety_OK` (nødstopp) og `Dør_N_Stop` (per dør).
- **Tømme-funksjon er påkrevd:** "Hver etasje skal også ha en tømmefunksjon som kan aktiveres fra HMI." Dette er IKKE implementert. Legg til FC_Tøm_Etasje som kan kalles uavhengig av sekvenssteg.
- **SCL-filer skal SLETTES før innlevering:** Oppgaven tillater KUN FBD og LAD. SCL (Structured Control Language) er et tekstbasert språk (ligner Pascal) — IKKE det samme som LAD (ledningsdiagram) eller FBD (funksjonsblokkdiagram). Leverer du med .scl-filer, blir besvarelsen underkjent.
- **Subagent-batch-størrelse:** Maks 4-6 filer per subagent, maks 3 samtidige. Flere fører til timeout (observert ved 8+ filer per subagent).
- **IO-kryssreferanse er PÅKREVET etter konvertering:** Generer alltid IO_LISTE.txt og TAGLISTE.txt som separate referansfiler. Bruk XML-importfilene som kilde for norske tegn — kopier navn, ikke skriv dem på nytt.
- **User Constants are MANDATORY:** Always define named constants for ALL magic numbers — sequence steps (STEP_INIT=0, STEP_VENT_PALL=1, ..., STEP_ALARM=99), targets (TARGET_STOR=1, TARGET_MEDIUM=2, TARGET_LITEN=3), status codes (STATUS_AV=0, STATUS_DRIFT=1, STATUS_STANDBY=2, STATUS_ALARM=3), alarm codes (ALARM_NONE=0, ALARM_NØDSTOPP=1, etc.). Never use raw numbers in FC/FB logic.
- **UDT-based DB structure is MANDATORY:** Always use UDTs to structure data blocks. Never create flat DBs with individual variables. Each UDT represents one conceptual entity (Motor, Sensor, Etasje, Alarm, etc.). DB2 uses UDT_Alarm + UDT_Sikkerhet_Sensor + UDT_Sikkerhet_Diag + UDT_Prosess_Alarm. DB3 uses UDT_HMI_Kommando + UDT_HMI_Status.
- **DB reference format changes with UDTs:** When UDTs are used, all FC/FB references must use the UDT path format: `DB3.Status.SeqStep` (not `DB3.SeqStep`), `DB2.Alarm.Safety_OK` (not `DB2.Safety_OK`), `DB4.Konfig_Tid.Timeout_Heis` (not `DB4.Timeout_Heis`), `DB3.Kommando.Cmd_Start` (not `DB3.Cmd_Start`). All ladder-FB files and XML import files must be updated consistently.

## References

- **PLCSIM & Co-Simulation:** `references/plcsim-advanced-reference.md` — PLCSIM V20 vs Advanced V7.0, API functions, co-simulation architecture, test procedures, known issues
- **TIA Portal Import XML:** `references/tia-portal-import-xml-format.md` — Full XML schema for UDTs, DBs, User Constants, and block interface import
- Siemens TIA Portal Help: *Ladder Logic (LAD) – Basic Instructions*
- Siemens TIA Portal Help: *Function Block Diagram (FBD) – Extended Instructions*
- Siemens TIA Portal Help: *Using IEC Timers and Counders*
- Siemens TIA Portal Help: *Creating and Calling Function Blocks (FC/FB)*
- Siemens TIA Portal Help: *Managing Data Blocks (DB) for Global Variables*
