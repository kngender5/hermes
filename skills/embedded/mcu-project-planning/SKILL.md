---
name: mcu-project-planning
description: "End-to-end MCU project planning and documentation for embedded microcontroller projects (ESP32, STM32, Arduino, RP2040). Covers hardware planning (pin mapping, peripheral assignment, power budget), firmware architecture (state machines, ISR design, RTOS tasks), communication protocols, PCB/schematic planning, and writing the functional description document from project source files. Use for robotics, sensor nodes, motor control, IoT, and similar embedded projects."
version: 0.3.0
category: embedded
triggers:
  - starting a new MCU/embedded project (ESP32, STM32, Arduino, RP2040)
  - need to produce a complete MCU project plan (pinout, peripherals, firmware arch, comms, power)
  - need to write a functional description (funksjonsbeskrivelse) for an embedded/MCU system
  - need to generate project documentation from source files (schematic, pin map, firmware arch, protocol spec, test plan)
  - starting a new embedded project that needs handover-ready documentation
  - need to produce documentation a new person can take over without prior knowledge
  - planning PCB layout, BOM, or power budget for an MCU project
  - designing firmware architecture (bare-metal, RTOS, or hybrid)
---

# MCU Project Planning — Embedded Microcontroller Systems

This skill covers the **full lifecycle** of MCU project documentation and planning for embedded microcontroller projects (ESP32, STM32, Arduino, RP2040, and similar):

1. **Hardware Planning** — Pin mapping, peripheral assignment, power budget, PCB/schematic design.
2. **Firmware Architecture** — State machines, ISR design, RTOS tasks, communication protocols.
3. **Functional Description** — Produce a structured, point-by-point functional description document from project source files.

Typical projects: robotics control, sensor nodes, motor drivers, IoT gateways, CNC controllers, custom PCBs.

---

## PHASE 0: Document-First Setup (BEFORE Coding)

*ALWAYS start with documentation before writing any firmware or drawing any schematic. A new person must be able to take over the project without asking the author anything.*

### 0A: Create README.md — The Entry Point

Every project MUST have a `README.md` as the very first file. It is the entry point for anyone new to the project. Include:

1. **What is this project?** — One paragraph explaining what the system does, in plain language
2. **How to read this documentation** — Numbered reading order for new persons (README first, then funksjonsbeskrivelse, then pinout, then firmware arch...)
3. **File structure** — Tree diagram of the project folder
4. **Technical choices** — MCU model, clock speed, programming language/framework, communication protocols, toolchains
5. **Reading list for new persons** — Table mapping "I need to know X" → "Read file Y"
6. **Bill of Materials (BOM)** — Key components with part numbers and suppliers
7. **Contact info** — Who to ask about what

**CRITICAL:** Write the README as if the reader has NEVER seen this project and has NO access to you. Every document must be self-contained.

### 0B: Create Complete Document Set

Before writing any firmware or designing any PCB, produce these documents in order:

| # | Document | File | Purpose |
|---|----------|------|---------|
| 1 | README.md | `README.md` | Entry point — project overview |
| 2 | Funksjonsbeskrivelse | `funksjonsbeskrivelse.md` | How the system works |
| 3 | Pin-kart / Pinout | `pinout.md` | All GPIO assignments, peripheral mapping |
| 4 | Kraftforsyning / Power Budget | `power_budget.md` | Voltage rails, current draw, regulator selection |
| 5 | Firmware-arkitektur | `firmware_arkitektur.md` | State machine, ISRs, RTOS tasks, modules |
| 6 | Kommunikasjonsprotokoll | `kommunikasjon.md` | UART/SPI/I2C/CAN/USB/WiFi/BLE spec |
| 7 | Skjematikk-plan | `skjematikk_plan.md` | Schematic structure, key circuits |
| 8 | PCB-plan | `pcb_plan.md` | Layer stackup, layout constraints, DRC rules |
| 9 | Testplan | `testplan.md` | Unit tests, integration tests, hardware tests |
| 10 | Bruksanvisning | `bruksanvisning.md` | Operator manual / user guide |
| 11 | Bygg og flash | `bygg_og_flash.md` | How to build, flash, and debug |

### 0C: Language Standard

- **ALL documentation, comments, reports, manuals, and UI text MUST be in Norwegian (bokmål)**
- This is both a course requirement and professional practice for Norwegian engineering projects
- Use consistent Norwegian technical terminology:
  - "nødstopp" (never "nødstans" or "nødstoppbryter")
  - "funksjonsbeskrivelse", "bruksanvisning", "tilstandsmaskin", "avbrudd" (ISR)
  - "krystallfrekvens", "spenningsregulator", "kondensator", "motstand"
  - "protokoll", "databuss", "seriell kommunikasjon", "pinne"
  - "typeut", "opptak", "gjennomkobling", "mellomkort"

**NORWEGIAN TEXT QUALITY GATE — before delivering any document:**
- Scan every Norwegian word for non-Latin characters (Chinese/Japanese glyphs slip into
  Norwegian text from model context — e.g. "laptopen" must never contain CJK chars)
- Check for common Norwegian typos: itet/opptak/tasttur/typeut/med mellomrom
  (Norwegian words are NOT English words with swapped letters)
- If any document contains non-Norwegian characters in Norwegian sections,
  rewrite that section entirely — do not try to patch individual characters
- Read through every .md aloud (mentally) to catch words that "look right" but
  are wrong language or wrong spelling

---

## PHASE 1: Hardware Planning

*Use this phase when starting a new MCU project or when you need to produce a detailed hardware plan before PCB design.*

### 1. Understand the Specification

- Read the project description (PDF, text, or images) **in its entirety** before making any assumptions.
- Extract key functions: sensor/actuator list, communication requirements, power constraints, environmental conditions, safety requirements.
- If the source is a scanned PDF, apply OCR (e.g., `tesseract` with language `nor+eng`) to obtain editable text.

**CRITICAL PITFALL — "Kontinuasjon" does NOT mean "same project":**
- In Norwegian course contexts, "Prosjektoppgave — Kontinuasjon" is often a **completely new project** that builds on the *competence* from previous work, not a continuation of the same system.
- **ALWAYS read the full assignment spec** before assuming any overlap with previous projects.
- **NEVER** copy pin mappings, peripheral assignments, or firmware structures from a previous project into a new one without verifying each item against the new spec.

### 2. Select the MCU

Choose the MCU based on these criteria (document the rationale for each):

| Criterion | Questions to Answer |
|-----------|-------------------|
| **Processing power** | Required clock speed? DSP instructions needed? FPU? |
| **Memory** | Flash size for firmware? RAM for runtime data? External memory needed? |
| **GPIO count** | Total pins needed (including reserved)? |
| **Peripherals** | UART/SPI/I2C/CAN/USB/ADC/DAC/PWM — how many of each? |
| **Power** | Operating voltage? Sleep current? Active current? |
| **Connectivity** | WiFi? BLE? Ethernet? LoRa? |
| **Package** | TQFP/QFN/BGA — hand-solderable? |
| **Ecosystem** | Arduino? ESP-IDF? STM32HAL? Zephyr? PlatformIO? |
| **Cost** | Unit cost at volume? Availability? |
| **Temperature** | Operating range (industrial -40..85°C or commercial 0..70°C)? |

**Common MCU families and typical use cases:**

| Family | Typical Use | Ecosystem |
|--------|-------------|-----------|
| ESP32-S3 | IoT, WiFi/BLE, audio, display | ESP-IDF, Arduino, MicroPython |
| STM32F4 | Motor control, DSP, industrial | STM32CubeIDE, HAL, Zephyr |
| STM32H7 | High-performance, GUI, Ethernet | STM32CubeIDE, TouchGFX |
| RP2040 | General purpose, PIO, low cost | C/C++ SDK, Arduino, MicroPython |
| ATmega328P | Simple control, legacy | Arduino |
| nRF52840 | BLE, Thread, Zigbee | Zephyr, nRF Connect SDK |

### 3. Pin Mapping (Pinout Plan)

Create a complete pin mapping table. This is the single most important hardware document.

**Pin mapping table format:**

| Pin | Function | Direction | Peripheral | Notes |
|-----|----------|-----------|------------|-------|
| GPIO0 | UART0_TX | Output | UART0 (debug) | 115200 baud, boot pin — avoid loading |
| GPIO1 | UART0_RX | Input | UART0 (debug) | Pull-up required |
| GPIO2 | SPI_MOSI | Output | SPI0 (display) | 20 MHz max |
| GPIO3 | SPI_MISO | Input | SPI0 (display) | |
| GPIO4 | SPI_SCK | Output | SPI0 (display) | |
| GPIO5 | SPI_CS | Output | SPI0 (display) | Active low |
| GPIO6 | I2C_SDA | Bidir | I2C0 (sensors) | 4.7kΩ pull-up to 3.3V |
| GPIO7 | I2C_SCL | Output | I2C0 (sensors) | 4.7kΩ pull-up to 3.3V |
| GPIO8 | PWM_MOTOR | Output | LEDC CH0 | 25 kHz, 10-bit |
| GPIO9 | ENCODER_A | Input | PCNT | Pull-up, debounce |
| GPIO10 | ENCODER_B | Input | PCNT | Pull-up, debounce |
| GPIO11 | ADC_BATTERY | Input | ADC1 CH0 | Voltage divider 100k/100k |
| GPIO12 | STATUS_LED | Output | GPIO | Active low, 3.3V |
| GPIO13 | EMERG_STOP | Input | GPIO (interrupt) | NC contact, pull-up, 0ms response |
| GPIO14 | RESERVED | — | — | RESERVERT — future expansion |
| GPIO15 | RESERVED | — | — | RESERVERT — future expansion |

**Pin mapping rules:**
- **ALWAYS reserve 10-20% of GPIO pins for future expansion.** Mark as `RESERVERT` with plausible future use.
- **Boot/strap pins** (e.g., ESP32 GPIO0, GPIO2, GPIO12, GPIO15) — document their boot behavior and avoid loading them.
- **ADC pins** — note input impedance, voltage range, and required voltage dividers.
- **I2C pins** — always specify pull-up resistor values and voltage rail.
- **High-speed signals** (SPI >10 MHz, USB) — note impedance control and length matching requirements.
- **Interrupt-capable pins** — mark which pins support external interrupts (not all do on every MCU).

### 3B: Direct Matrix Scanning (FFC / ZIF Connector)

When the MCU reads a keyboard matrix directly via GPIO (not via USB),
use this pattern instead of/per alongside pin mapping from 3A:

- Most laptop keyboards are row/column matrices (typically 8×16 or 8×20)
- Rasters: Row pins as **output** (drive one low at a time)
- Columns: Column pins as **input with internal pull-up** (read all per scan)
- Scan rate: 1 kHz (1 ms per full matrix scan — far faster than human input)
- Debounce: 3 consecutive matching scans before registering (3 ms)
- FFC ZIF connector: 0.5mm pitch, 30-pin typical; each row + column = 1 pin
- TVS diodes on every FFC line at board entry (PESD5V0U4BC or similar)

**CRITICAL:** FFC pin-to-matrix mapping is **unique per laptop model**. NEVER assume
a pinout. The correct procedure is:
1. Flash a debug firmware that prints [ROW:COL] for every detected press
2. Press every key on the target keyboard and record the mapping
3. Build the keymap table from the captured data
4. The keymap converts [ROW][COL] → HID usage ID (USB keycode)

### 3C: USB Dual-Role (Passthrough Projects)

Projects that sit inline between a keyboard and PC need USB OTG
(device for PC, understanding of or direct scanning of key matrix):

- ESP32-S3 has native USB OTG — ideal for inline USB HID projects
- TinyUSB stack supports both device mode (to PC) and understanding of key input
- USB Device descriptor MUST declare only the HID Keyboard device (no MSC, no RNDIS)
- Passthrough latency target: <3 ms from physical keypress to USB report
- For inline USB physically: pass keyboard's USB signals through to MCU, MCU
  re-emits as its own HID report. Or use a USB switch IC (FSUSB30)

### 4. Power Budget

Calculate the complete power budget:

| Component | Voltage | Active Current | Sleep Current | Duty Cycle | Avg Current |
|-----------|---------|----------------|---------------|------------|-------------|
| MCU (core) | 3.3V | 80 mA | 10 µA | 100% | 80 mA |
| MCU (WiFi TX) | 3.3V | +240 mA | — | 5% | +12 mA |
| Display | 3.3V | 45 mA | 1 mA | 80% | 36 mA |
| Sensors (total) | 3.3V | 15 mA | 0.5 mA | 100% | 15 mA |
| Motor driver | 5V | 500 mA | 10 mA | 20% | 100 mA |
| LEDs | 3.3V | 20 mA | 0 mA | 50% | 10 mA |
| **TOTAL** | | | | | **~253 mA** |

**Power supply design:**
- Select regulator (LDO vs DSW) based on efficiency requirements
- Calculate thermal dissipation: P = (V_in - V_out) × I_max
- Add bulk capacitance: 100 µF electrolytic + 100 nF ceramic per power rail
- Add decoupling: 100 nF ceramic per IC power pin, placed close to pin
- Document battery life if applicable: Capacity (mAh) / Avg Current (mA) = Hours

### 5. Schematic Plan

Organize the schematic into functional blocks:

```
┌─────────────────────────────────────────────────┐
│                  SCHEMATIC BLOCKS                │
├─────────────────────────────────────────────────┤
│  [Power Supply]                                  │
│   Input → Protection → Regulator → Rails        │
│   (5V/3.3V/1.8V)                                │
├─────────────────────────────────────────────────┤
│  [MCU Core]                                      │
│   MCU + Decoupling + Crystal + Boot Config      │
│   + Reset Circuit + SWD/JTAG Header             │
├─────────────────────────────────────────────────┤
│  [Communication]                                 │
│   UART (debug) + USB (CDC/DFU) + Wireless       │
├─────────────────────────────────────────────────┤
│  [Sensors]                                       │
│   I2C bus + SPI bus + ADC inputs + GPIO         │
├─────────────────────────────────────────────────┤
│  [Actuators]                                     │
│   Motor drivers + PWM outputs + Relays          │
├─────────────────────────────────────────────────┤
│  [User Interface]                                │
│   LEDs + Buttons + Display + Buzzer             │
├─────────────────────────────────────────────────┤
│  [Safety]                                        │
│   Emergency stop + Watchdog + Failsafe          │
└─────────────────────────────────────────────────┘
```

**Key schematic rules:**
- **Decoupling capacitors:** 100 nF ceramic on EVERY power pin, placed as close as possible
- **Bulk capacitors:** 10-100 µF per power rail near the regulator output
- **Crystal/oscillator:** Load capacitors per datasheet, short traces, ground plane underneath
- **Reset circuit:** 10 kΩ pull-up + 100 nF cap to ground + optional reset button
- **SWD/JTAG header:** Standard pinout, 10-pin or 20-pin, with GND reference
- **ESD protection:** TVS diodes on external connectors (USB, UART, etc.)
- **Reverse polarity protection:** Schottky diode or P-MOSFET on power input

---

## PHASE 2: Firmware Architecture

*Use this phase when designing the firmware structure for an MCU project.*

### 1. Choose Execution Model

| Model | When to Use | Pros | Cons |
|-------|-------------|------|------|
| **Super-loop (bare-metal)** | Simple systems, <5 tasks, no hard real-time | Simple, predictable, low overhead | No preemption, timing drifts |
| **RTOS (FreeRTOS/Zephyr)** | Multiple tasks, communication stacks, complex timing | Preemption, queues, semaphores | RAM overhead, complexity |
| **Hybrid** | RTOS for comms + ISR for time-critical | Best of both worlds | More complex to debug |
| **Async/Event-driven** | State-machine-heavy, low power | Efficient, responsive | Callback complexity |

**Decision criteria:**
- Need WiFi/BLE stack? → RTOS (required by most wireless SDKs)
- Hard real-time motor control (<10 µs jitter)? → Bare-metal or ISR-driven
- Multiple independent functions? → RTOS
- Battery powered with deep sleep? → Super-loop with sleep states

### 2. State Machine Design

Most embedded systems are state machines. Design the main state machine:

| State | Description | Key Actions | Exit Condition |
|-------|-------------|-------------|----------------|
| INIT | Initialize peripherals, self-test | Init GPIO, UART, SPI, I2C, ADC; run POST | Self-test passed |
| IDLE | Waiting for command/event | Low power mode, poll buttons | Command received or sensor trigger |
| RUNNING | Main operation active | Execute control loop, read sensors, drive actuators | Stop command or error |
| ERROR | Fault detected | Safe state, log error, indicate fault | Reset command + fault cleared |
| SLEEP | Deep sleep / low power | Disable peripherals, enter sleep | Wake-up event (timer, GPIO) |
| BOOTLOADER | Firmware update mode | Receive new firmware via UART/USB/OTA | Update complete or timeout |

**State machine implementation patterns:**
- **Switch-case:** Simple, readable, good for <10 states
- **Function pointer table:** Scalable, good for >10 states
- **RTOS task per state:** When states run concurrently
- **Hierarchical state machine:** When states have sub-states

### 3. ISR (Interrupt Service Routine) Design

**ISR rules — follow these strictly:**

| Rule | Rationale |
|------|-----------|
| Keep ISRs SHORT (<10 µs execution) | Long ISRs block other interrupts |
| NO blocking calls in ISR | No `delay()`, `malloc()`, `printf()`, I2C/SPI blocking reads |
| NO floating point in ISR (unless FPU context saved) | Corrupts FPU state |
| Set flag / send to queue, defer processing | Main loop or RTOS task handles the work |
| Use volatile for shared variables | Compiler optimization can break shared access |
| Disable interrupts briefly for critical sections | Prevent race conditions on shared data |
| Document interrupt priority | Higher number = higher priority (check MCU-specific) |

**Common ISR patterns:**

```c
// Pattern 1: Flag + main loop processing
volatile bool sensor_ready = false;

void IRAM_ATTR sensor_isr(void* arg) {
    sensor_ready = true;  // Just set flag
}

void loop() {
    if (sensor_ready) {
        sensor_ready = false;
        process_sensor_data();  // Heavy processing here
    }
}

// Pattern 2: RTOS queue from ISR
void IRAM_ATTR encoder_isr(void* arg) {
    int32_t count = pcnt_get_count(PCNT_UNIT_0);
    xQueueSendFromISR(encoder_queue, &count, NULL);
}
```

### 4. Communication Protocol Design

Document each communication interface:

#### UART
| Parameter | Value | Notes |
|-----------|-------|-------|
| Baud rate | 115200 | Standard debug baud |
| Data bits | 8 | |
| Parity | None | |
| Stop bits | 1 | |
| Flow control | None (or RTS/CTS) | |
| Buffer size | 256 bytes RX, 256 bytes TX | |
| Protocol | COBS/SLIP framing or custom | |

#### SPI
| Parameter | Value | Notes |
|-----------|-------|-------|
| Mode | CPOL=0, CPHA=0 | Check slave device requirements |
| Clock speed | 10 MHz | Max per slave |
| Bit order | MSB first | |
| CS polarity | Active low | |
| DMA | Yes (if available) | Offload from CPU |

#### I2C
| Parameter | Value | Notes |
|-----------|-------|-------|
| Speed | 100 kHz (standard) or 400 kHz (fast) | |
| Pull-up resistors | 4.7 kΩ to 3.3V | Adjust for bus capacitance |
| Address | 0x48 (7-bit) | Per device |
| Bus capacitance | <400 pF | Max per spec |

#### CAN (if applicable)
| Parameter | Value | Notes |
|-----------|-------|-------|
| Bit rate | 250 kbit/s or 500 kbit/s | |
| Termination | 120 Ω at both ends | |
| Frame format | Standard (11-bit) or Extended (29-bit) | |
| Filter | Acceptance filter per node | |

### 5. RTOS Task Design (if using RTOS)

| Task | Priority | Stack Size | Period | Description |
|------|----------|------------|--------|-------------|
| Control loop | High (24) | 4096 | 10 ms | PID motor control |
| Sensor read | Medium (20) | 2048 | 50 ms | Read all sensors |
| Communication | Medium (18) | 8192 | Event | Handle UART/USB/WiFi |
| Display | Low (10) | 4096 | 100 ms | Update display |
| Logging | Low (8) | 2048 | 1000 ms | Write to SD card |
| Idle | Lowest (0) | 1024 | — | Feed watchdog, enter sleep |

**RTOS rules:**
- **Stack sizing:** Start with generous stack, use stack watermarking to optimize
- **Priority inversion:** Use mutex with priority inheritance
- **Queue sizing:** Size for worst-case burst + 20% margin
- **Watchdog:** Feed watchdog in idle task; if a task hangs, system resets
- **Memory:** Prefer static allocation; avoid heap fragmentation

### 6. Timing Analysis

| Function | Execution Time | Period | CPU Load |
|----------|---------------|--------|----------|
| Control loop ISR | 50 µs | 10 ms | 0.5% |
| Sensor read | 2 ms | 50 ms | 4% |
| Communication | 5 ms | Event | ~2% |
| Display update | 8 ms | 100 ms | 8% |
| Logging | 3 ms | 1000 ms | 0.3% |
| **TOTAL** | | | **~15%** |

Keep total CPU load below 70% to leave headroom for bursts and future features.

---

## PHASE 3: PCB Planning

*Use this phase when designing the printed circuit board.*

### 1. Layer Stackup

| Layers | Use Case | Cost |
|--------|----------|------|
| 2-layer | Simple designs, low speed | Lowest |
| 4-layer | Mixed signal, moderate speed | Medium |
| 6+ layer | High-speed, RF, dense designs | High |

**Recommended 4-layer stackup:**
```
Layer 1 (Top):    Signal + components
Layer 2 (Inner):  Ground plane (unbroken)
Layer 3 (Inner):  Power plane (split if multiple rails)
Layer 4 (Bottom): Signal + components
```

### 2. Layout Rules

| Rule | Rationale |
|------|-----------|
| Place decoupling caps within 2 mm of power pins | Minimize inductance |
| Keep crystal traces short (<15 mm) and symmetric | Stable oscillation |
| Route high-speed signals on top layer with ground reference | Controlled impedance |
| Keep analog and digital grounds separate, join at one point | Prevent noise coupling |
| Place connectors on board edge, oriented consistently | Ease of assembly |
| Add test points on critical signals | Debugging and production test |
| Include mounting holes (M3) | Mechanical mounting |
| Add silkscreen labels for all connectors and test points | Assembly and debug |
| Keep 0.5 mm clearance for 3.3V, 2 mm for 24V+ | Safety clearance |
| Use 0.25 mm trace width for signals, 0.5 mm+ for power | Current capacity |

### 3. DRC (Design Rule Check) Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Min trace width | 0.2 mm (8 mil) | Manufacturer dependent |
| Min clearance | 0.2 mm (8 mil) | Manufacturer dependent |
| Min via size | 0.3 mm drill, 0.6 mm pad | |
| Min annular ring | 0.15 mm | |
| Copper pour clearance | 0.3 mm | From traces to pour |

---

## PHASE 4: Writing the Functional Description

*Use this phase when you have project source files and need to produce a complete, point-by-point functional description (funksjonsbeskrivelse) for an MCU-based embedded system.*

### Prerequisites

- Access to source files (schematic, pinout, firmware source, test results)
- Optional: oscilloscope measurements, power consumption data, protocol captures

### Procedure

#### Step 1: Collect and Read Source Files
Read each file sequentially to build a system overview. Note:
- Pin assignments and peripheral mappings
- Power budget and regulator selection
- Firmware architecture (state machine, ISRs, RTOS tasks)
- Communication protocols and timing
- PCB layout decisions and constraints
- Test results and measured values

#### Step 2: Determine Document Structure
A typical functional description contains:
1. Innledning og formål
2. Systemoversikt (block diagram, overall function)
3. Maskinvare (MCU selection, pin mapping, power supply, schematic)
4. Fastvare/Firmware (architecture, state machine, ISRs, RTOS, protocols)
5. PCB-design (layer stackup, layout rules, DRC)
6. Sikkerhet (emergency stop, watchdog, failsafe)
7. Testing (test plan, measured results, validation)
8. Bruksanvisning (operation, maintenance, troubleshooting)
9. Konklusjon

#### Step 3: Write Section by Section
- Summarize relevant facts from source files for each section.
- Provide a brief justification for every technical choice (e.g., why a specific MCU was chosen, why a specific pin was assigned, why a specific RTOS task priority was used).
- Keep text in Norwegian, technically precise, and avoid unnecessary flourish.
- Number sub-points for readability.

#### Step 4: Format and Deliver
- Save as `.md` for version control and readability.
- Use headings (`#`, `##`, `###`) for clear hierarchy.
- Include code snippets, pin tables, and timing diagrams where they clarify the description.
- Verify all important design decisions are mentioned at least once.

#### Step 5: Quality Check
- Verify every source file is represented.
- Verify every technical choice has an associated justification.
- Verify language is consistently Norwegian.
- Verify the document is readable by both firmware developers and hardware engineers.
- Verify the document is comprehensible WITHOUT access to the original author.

---

## PHASE 5: Build, Flash, and Debug

### Build System

| Tool | Use Case |
|------|----------|
| PlatformIO | Multi-platform, VS Code integration, library manager |
| ESP-IDF | ESP32 native development |
| STM32CubeIDE | STM32 with HAL, code generation |
| Arduino IDE | Quick prototyping, simple projects |
| CMake + GCC ARM | Custom builds, CI/CD |
| Zephyr RTOS build | Zephyr-based projects |

### Flashing Methods

| Method | Interface | Tools |
|--------|-----------|-------|
| SWD/JTAG | 2-wire debug | J-Link, ST-Link, OpenOCD |
| UART bootloader | Serial | esptool.py, stm32flash |
| USB DFU | USB | dfu-util |
| OTA (Over-The-Air) | WiFi/Ethernet | ESP OTA, custom bootloader |

### Debugging Techniques

| Technique | When to Use |
|-----------|-------------|
| Serial printf | Quick debug, state tracing |
| SWD debugger (GDB) | Breakpoints, memory inspection, step-through |
| Logic analyzer | Protocol debugging (SPI, I2C, UART) |
| Oscilloscope | Signal integrity, timing measurement |
| LED blink codes | Production debugging without tools |
| SWO/ITM trace | Real-time printf over SWD (no UART needed) |
| Core dump | Post-mortem crash analysis (ESP32) |

---

## Complete File Structure

```
mcu-project/
├── README.md                          ← Entry point (READ FIRST)
├── funksjonsbeskrivelse.md           ← System description
├── pinout.md                          ← GPIO assignments, peripheral mapping
├── power_budget.md                    ← Power analysis, regulator selection
├── firmware_arkitektur.md             ← State machine, ISRs, RTOS tasks
├── kommunikasjon.md                   ← Protocol specifications
├── skjematikk_plan.md                 ← Schematic structure
├── pcb_plan.md                        ← PCB layout rules, layer stackup
├── testplan.md                        ← Test procedures and results
├── bruksanvisning.md                  ← Operator manual
├── bygg_og_flash.md                   ← Build and flash instructions
│
├── firmware/
│   ├── src/
│   │   ├── main.c / main.cpp
│   │   ├── state_machine.c
│   │   ├── sensors.c
│   │   ├── actuators.c
│   │   ├── communication.c
│   │   └── safety.c
│   ├── include/
│   │   ├── config.h
│   │   ├── pin_definitions.h
│   │   └── protocol.h
│   ├── platformio.ini / CMakeLists.txt
│   └── sdkconfig / Kconfig
│
├── hardware/
│   ├── schematic/
│   │   ├── mcu-project.kicad_sch
│   │   └── mcu-project.kicad_pcb
│   ├── datasheets/
│   └── bom/
│       └── bom.csv
│
├── test/
│   ├── unit_tests/
│   ├── integration_tests/
│   └── hardware_tests/
│
└── docs/
    ├── images/
    └── references/
```

---

## Tips & Pitfalls

### Hardware
- **Decoupling is NOT optional:** Every IC power pin needs a 100 nF ceramic capacitor, placed as close as possible. Missing decoupling causes mysterious crashes and noise.
- **Boot/strap pins:** Document and handle correctly. A wrong pull-up/pull-down can prevent the MCU from booting.
- **Crystal load capacitors:** Use the values from the MCU datasheet, not guesses. Wrong values cause frequency drift or no oscillation.
- **I2C pull-ups:** Too weak → slow rise time, communication errors. Too strong → excessive current, signal distortion. Calculate based on bus capacitance.
- **ESD protection:** Any connector exposed to the outside world needs TVS diodes. ESD kills MCUs silently.
- **Thermal management:** Check regulator power dissipation. A linear regulator dropping 12V to 3.3V at 500 mA dissipates 4.35W — it WILL need a heatsink.

### Firmware
- **Keep ISRs short:** The #1 cause of embedded bugs is doing too much in an ISR. Set a flag, return, process in main loop.
- **Volatile for shared variables:** Without `volatile`, the compiler optimizes away reads from variables changed in ISRs.
- **Stack overflow:** The #2 cause of embedded bugs. Use stack watermarking to measure actual usage.
- **Watchdog timer:** ALWAYS enable the watchdog. A hung firmware should reset, not stay hung.
- **Debounce mechanical inputs:** Buttons and switches bounce. Use a 10-50 ms debounce timer or software filter.
- **Avoid floating point on MCUs without FPU:** Software FP is 10-100x slower. Use fixed-point or integer math instead.
- **Check return values:** I2C, SPI, and UART operations can fail. Check return codes and handle errors.

### PCB
- **Ground plane integrity:** Never route a signal trace across a split in the ground plane. It creates an antenna.
- **Via stitching:** Connect ground planes on different layers with vias around the board perimeter and near high-speed signals.
- **Thermal relief:** Use thermal relief pads for through-hole components soldered to ground planes. Without them, soldering is extremely difficult.
- **Silkscreen:** Label everything. Future you will thank present you.
- **Test points:** Add test points for power rails, communication signals, and critical GPIOs. Essential for debugging and production test.

### Behavioral Pitfalls
- **STAY ON TASK — verify before investing effort:** Before spending time on complex tool chains, check if the material is already available locally.
- **When user says "check progress" or "I've already done X":** STOP. Verify current state before continuing planned work.
- **Handover-ready documentation is a first-class requirement:** README as self-contained entry point, every document describes system without assuming prior knowledge, Norwegian language throughout.
- **"Kontinuasjon" ≠ "same project":** Always read the full spec. Norwegian course "Kontinuasjon" projects are often completely new systems.
- **Subagent file naming discipline:** When delegating to subagents, verify file names match the calling convention. Subagents use different numbering.
- **Norwegian text quality — scan BEFORE delivering:** Character-by-character scan for CJK bleed-through (Chinese/Japanese glyphs), English words in Norwegian sections, and spelling errors ("sjuk" not "sjekk", "tuyk" not "type"). Run `file` to verify UTF-8. Fix entire sections, not individual characters. See 0C quality gate.
- **"Gjennomgå alle" means ALL files:** User means every single file, not a sample. Read each file top to bottom.
- **Keyboard matrix pinout is per-device:** Never assume. Always calibrate with scan_debug firmware first. See 3B.
- **"My own device, I trigger it" — add guards, don't refuse:** Legitimate personal-use projects need safety guards (explicit activation combo, visible LED, buzzer, no silent storage) — not flat refusal. Architecturally identical to malicious use, ethically different.

## References

- ESP-IDF Programming Guide: https://docs.espressif.com/projects/esp-idf/
- STM32 HAL/LL Documentation: https://www.st.com/en/development-tools/stm32cubemx.html
- RP2040 Datasheet: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
- FreeRTOS Documentation: https://www.freertos.org/Documentation/RTOS_book.html
- PlatformIO Documentation: https://docs.platformio.org/
- Kicad EDA: https://www.kicad.org/

### Support Files

- `references/inline-ffc-keyboard-design.md` — Inline FFC keyboard matrix interceptor pattern (analog switch passthrough, scan/typeout via GPIO, ULP wake-on-key, per-laptop calibration).
