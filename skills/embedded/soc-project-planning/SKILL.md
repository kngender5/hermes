---
name: soc-project-planning
description: "End-to-end SoC project planning and documentation for System-on-Chip projects (Raspberry Pi, BeagleBone, NVIDIA Jetson, NXP i.MX, Allwinner, Rockchip). Covers hardware planning (pinout, peripheral assignment, power sequencing, thermal design), SoC-specific firmware (device tree, kernel modules, bootloaders), carrier board design, and writing the functional description document. Use for SBCs, embedded Linux, edge AI, industrial gateways, and similar SoC-based projects."
version: 0.1.0
category: embedded
triggers:
  - starting a new SoC/embedded Linux project (RPi, Jetson, BeagleBone, i.MX)
  - need to produce a complete SoC project plan (pinout, peripherals, power sequencing, thermal, device tree)
  - need to write a functional description (funksjonsbeskrivelse) for an SoC-based system
  - need to generate project documentation from source files (schematic, carrier board, device tree, bootloader)
  - starting a new SoC carrier board or SBC-based project
  - designing a custom carrier board / baseboard for a SoM (System-on-Module)
  - planning power sequencing, thermal management, or high-speed PCB for SoC
  - need to write a device tree overlay or configure a bootloader for SoC
---

# SoC Project Planning — System-on-Chip / Embedded Linux

This skill covers the **full lifecycle** of SoC project documentation and planning
for System-on-Chip projects (Raspberry Pi, NVIDIA Jetson, BeagleBone, NXP i.MX,
Allwinner, Rockchip, and similar):

1. **Hardware Planning** — Pin mapping, peripheral assignment, power sequencing,
   thermal design, carrier board design.
2. **Firmware/Software Architecture** — Bootloader, kernel, device tree,
   userspace application design.
3. **Functional Description** — Produce a structured, point-by-point functional
   description document from project source files.

Typical projects: edge AI inference, industrial gateways, custom SBCs,
embedded Linux controllers, carrier board design for SoMs.

---

## PHASE 0: Document-First Setup (BEFORE Coding)

*ALWAYS start with documentation before writing any software or drawing any
schematic. A new person must be able to take over the project without asking
the author anything.*

### 0A: Create README.md — The Entry Point

Every project MUST have a `README.md` as the very first file. Include:

1. **What is this project?** — One paragraph explaining what the system does
2. **How to read this documentation** — Numbered reading order
3. **File structure** — Tree diagram
4. **Technical choices** — SoC model, OS, toolchain, boot method
5. **Reading list** — Table mapping "I need to know X" → "Read file Y"
6. **Bill of Materials (BOM)** — Key components with part numbers

### 0B: Create Complete Document Set

| # | Document | File | Purpose |
|---|----------|------|---------|
| 1 | README.md | `README.md` | Entry point |
| 2 | Funksjonsbeskrivelse | `funksjonsbeskrivelse.md` | How the system works |
| 3 | Pin-kart / Pinout | `pinout.md` | All GPIO, high-speed, power pins |
| 4 | Spenningssekvens / Power Sequencing | `power_sequencing.md` | Rail order, timing, regulators |
| 5 | Termisk-design | `thermal_design.md` | Cooling, thermal pads, airflow |
| 6 | Fastvare/Software-arkitektur | `firmware_arkitektur.md` | Boot, kernel, DT, userspace |
| 7 | Enhets-tre / Device Tree | `device_tree.md` | DT overlays, pinmux, drivers |
| 8 | Kommunikasjon | `kommunikasjon.md` | Protocol specs |
| 9 | Skjematikk-plan | `skjematikk_plan.md` | Schematic structure |
| 10 | PCB-plan | `pcb_plan.md` | Layer stackup, high-speed rules |
| 11 | Testplan | `testplan.md` | Tests |
| 12 | Bruksanvisning | `bruksanvisning.md` | Operator manual |
| 13 | Bygg og flash | `bygg_og_flash.md` | How to build, flash, debug |

### 0C: Language Standard

- **ALL documentation MUST be in Norwegian (bokmål)**
- Consistent Norwegian technical terminology
- See `mcu-project-planning` Phase 0C for the Norwegian text quality gate

---

## PHASE 1: Hardware Planning

### 1. Understand the Specification

- Read the project description **in its entirety**
- Extract key functions: I/O requirements, compute needs, connectivity,
  power constraints, environmental conditions, safety requirements

### 2. Select the SoC

| Criterion | Questions |
|-----------|-----------|
| **Compute** | CPU arch? Cores? Clock? NPU/GPU needed? |
| **Memory** | RAM size? Type (LPDDR4/5)? eMMC support? |
| **Storage** | SD card? eMMC? NVMe? SPI NOR? |
| **GPIO** | Total available? Pinmux flexibility? |
| **High-speed** | PCIe lanes? USB 3.0? Ethernet? MIPI? |
| **Connectivity** | WiFi? BT? Cellular? |
| **Power** | Core voltage? IO voltage? Total TDP? |
| **Packaging** | Solder-down? SoM module? LGA? BGA? |
| **Ecosystem** | Mainline kernel? Vendor BSP? Yocto? Buildroot? |
| **Cost** | Unit cost? Availability? Longevity? |

**Common SoC families:**

| Family | Typical Use | Ecosystem |
|--------|-------------|-----------|
| BCM2711/2712 (RPi) | General purpose, education | Raspbian, mainline LTS |
| NVIDIA Jetson Orin | Edge AI, inference | JetPack, L4T, Ubuntu |
| NXP i.MX 8/9 | Industrial, automotive | Yocto, mainline |
| Rockchip RK3588 | Media, edge computing | Mainline, vendor SDK |
| Allwinner H6/H618 | Low-cost Linux | Mainline, Armbean |
| TI AM62/AM64 | Industrial, PRU-ICSS | TI Processor SDK |
| STM32MP1 | MCU+MPU hybrid | STM32CubeMP1, mainline |

### 3. Pin Mapping (Pinout Plan)

SoC pin mapping is significantly more complex than MCU pin mapping due to
pinmux (multiple alternate functions per pin).

**Pin mapping table format:**

| Pin | Default Func | Alt Func 1 | Alt Func 2 | Selected | Peripheral | Notes |
|-----|-------------|------------|------------|----------|------------|-------|
| A12 | GPIO1_A0 | I2C3_SDA | UART2_TX | I2C3_SDA | I2C (sensors) | Pull-up needed |
| B13 | GPIO1_A1 | I2C3_CLK | UART2_RX | I2C3_CLK | I2C (sensors) | Pull-up needed |
| C14 | GPIO1_B0 | SPI1_MOSI | PWM0 | SPI1_MOSI | SPI (display) | High speed |
| D15 | GPIO1_B1 | SPI1_MISO | — | SPI1_MISO | SPI (display) | |

**Pinmux rules:**
- **CONFLICT CHECK — no two peripherals can share the same physical pin.** Use the SoC's pinmux tool (e.g., TI PinMux Tool, NXP Pins Tool, RPi `pinctrl`) to verify.
- **Power groups:** Some pins are in different voltage domains (1.8V vs 3.3V). Document which pins belong to which rail.
- **Boot pins:** Some pins are sampled at reset to determine boot source. Document and do not use for general I/O.
- **DDR pins:** Memory interface pins are dedicated — completely unavailable for general I/O.

### 4. Power Sequencing

SoCs require specific power-up sequences. Getting this wrong = no boot.

| Step | Rail | Voltage | Tolerance | Max Ramp | SoC Pin Group |
|------|------|---------|-----------|----------|---------------|
| 1 | VDD_1V8_CORE | 1.8V | ±5% | 10 ms | Core logic |
| 2 | VDD_3V3_IO | 3.3V | ±5% | 10 ms | IO banks |
| 3 | VDD_1V1_DDR | 1.1V | ±3% | 5 ms | DDR PHY |
| 4 | VDD_1V0_NPU | 1.0V | ±3% | 5 ms | NPU |

**Critical:** Check the SoC datasheet for REQUIREMENTS on relative
timing between rails. Some SoCs require VDD_CORE before VDD_IO,
others require simultaneous ramp. Violation = damage.

**Power supply design:**
- Use PMIC (Power Management IC) designed for your SoC when available
- If discrete: use dedicated regulators with proper sequencing
- Add bulk caps per rail: 100 µF + 10 µF + 100 nF per rail
- Add inrush current limiting (soft-start) to avoid droop

### 5. Thermal Design

| SoC TDP | Cooling Solution | Notes |
|---------|-----------------|-------|
| <2W | Passive (copper pour + thermal pad) | RPi Zero, small SoMs |
| 2-5W | Heatsink + thermal pad | RPi 4, small SBCs |
| 5-15W | Active (fan) + heatsink | Jetson Orin Nano, RK3588 |
| 15-30W | Active (blower) + copper heatsink | Jetson Orin NX |
| >30W | Custom cooling, thermal simulation | Jetson AGX, high-end |

**Thermal pad placement:** Direct contact between SoC die and heatsink.
Use thermal pad material (Fujipoly, T-Global) with appropriate W/mK rating.
Gap pad for uneven surfaces, graphite sheet for even contact.

### 6. Schematic Plan

```
┌─────────────────────────────────────────────────┐
│               SCHEMATIC BLOCKS                  │
├─────────────────────────────────────────────────┤
│  [PMIC / Power Sequencing]                       │
│   Input → PMIC → All rails with correct order   │
├─────────────────────────────────────────────────┤
│  [SoC Core]                                      │
│   SoC + bypass caps + crystal + boot config     │
├─────────────────────────────────────────────────┤
│  [DDR Memory]                                    │
│   LPDDR4/5 PoP or discrete + decoupling         │
├─────────────────────────────────────────────────┤
│  [Boot Storage]                                  │
│   eMMC / SD card / SPI NOR / NVMe               │
├─────────────────────────────────────────────────┤
│  [Connectivity]                                  │
│   Ethernet (RGMII/SGMII) + USB + WiFi/BT module │
├─────────────────────────────────────────────────┤
│  [User Interface]                                │
│   GPIO header + LEDs + buttons + display        │
├─────────────────────────────────────────────────┤
│  [Debug / Programming]                           │
│   UART debug + JTAG/SWD + USB recovery          │
└─────────────────────────────────────────────────┘
```

**Key schematic rules for SoC:**
- **Bypass capacitors: per the SoC datasheet EXACTLY.** SoCs typically need
  multiple values per rail (e.g., 100nF + 10µF + 47µF) at specific distances.
- **DDR traces: length-matched, impedance-controlled, solid reference plane.**
  Consult the SoC vendor's layout guide — this is not negotiable.
- **PCIe, USB 3.0, Ethernet PHY: differential pairs with controlled impedance.**
  90Ω differential for USB, 100Ω for PCIe/Ethernet.
- **Crystal/oscillator: load caps per datasheet, solid ground underneath,
  keep away from high-speed and switching power signals.**

---

## PHASE 2: Firmware/Software Architecture

### 1. Boot Flow

```
Power On
  → PMIC releases reset
  → SoC ROM code (first stage)
  → Bootloader (U-Boot / GRUB)
  → Linux Kernel
  → Init system (systemd / busybox init)
  → Userspace application
```

**Boot sources (common):**
| Priority | Source | Typical Use |
|----------|--------|-------------|
| 1 | SPI NOR Flash | Small, fast boot, OTA |
| 2 | eMMC | Primary boot on SBCs |
| 3 | SD Card | Development, recovery |
| 4 | USB (DFU) | Recovery, flashing |
| 5 | Network (TFTP) | Production flashing |

### 2. Device Tree

Device Tree (DT) is how Linux describes hardware to the kernel.
Every SoC project needs a Device Tree Source (.dts) file.

**Key DT sections:**
```dts
/dts-v1/;
/plugin/;

/ {
    compatible = "your-vendor,your-board";
    fragment@0 {
        target = <&i2c3>;
        __overlay__ {
            status = "okay";
            clock-frequency = <400000>;

            sensor@48 {
                compatible = "vendor,sensor-model";
                reg = <0x48>;
            };
        };
    };
};
```

**DT overlays** are used to enable/disable peripherals without recompiling
the base DT. Document which overlays are needed for the project.

### 3. Kernel Configuration

- Start with the vendor's defconfig: `make vendor_defconfig`
- Enable only the drivers you need (keeps boot fast and image small)
- Disable unused drivers (reduces attack surface for security-critical projects)
- Document all custom `CONFIG_` options and why they're needed

### 4. Userspace Architecture

| Component | Options | When to Use |
|-----------|---------|-------------|
| **OS** | Yocto, Buildroot, Debian, Alpine | Full control → Yocto/Buildroot |
| **Init** | systemd, busybox init, s6 | Full system → systemd |
| **IPC** | D-Bus, MQTT, gRPC, Unix sockets | Service → D-Bus, IoT → MQTT |
| **OTA** | SWUpdate, Mender, RAUC, Balena | Field updates needed |

### 5. Application Design

State machine models still apply for SoC applications, but now you have
a full OS with processes, threads, and IPC.

- **Single-process:** Simple, use threads + mutexes
- **Multi-process:** Better isolation, use D-Bus/Unix sockets for IPC
- **Containerized:** Use balenaEngine or Docker for app isolation

---

## PHASE 3: PCB Planning for SoC

### 1. Layer Stackup

SoC projects almost always need 4+ layers for DDR routing:

| Layers | SoC Complexity | Cost |
|--------|---------------|------|
| 2-layer | Simple SoCs, no external DDR | Lowest |
| 4-layer | SoC with external DDR, moderate | Medium |
| 6-layer | PCIe, USB 3.0, multiple DDR | Higher |
| 8+ layer | High-speed, dense BGA | Highest |

**Recommended 4-layer stackup:**
```
Layer 1 (Top):    Signal + components
Layer 2 (Inner):  Ground plane (unbroken under SoC and DDR)
Layer 3 (Inner):  Power plane (split if multiple rails)
Layer 4 (Bottom): Signal + components + DDR traces
```

### 2. High-Speed Layout Rules

| Signal Type | Requirement | Notes |
|-------------|-------------|-------|
| DDR3/4/5 | Length-matched ±5 mil, 40Ω single, 80Ω diff | Follow SoC vendor layout guide |
| PCIe Gen2/3 | 85Ω differential, <5" trace length | Length-matched ±5 mil |
| USB 3.0 | 90Ω differential | Length-matched ±5 mil |
| Ethernet PHY | 100Ω differential | Magnetics placement |
| RGMII | 50Ω single-ended | Length-matched ±200 mil |

### 3. SoC-Specific Layout Rules

- **BGA escape routing:** Fanout under BGA using via-in-pad or dog-bone vias.
  Typical BGA pitch: 0.8mm → 4 mil trace/clearance minimum.
- **Thermal pad:** Exposed pad under SoC → thermal vias (0.3mm drill) to
  ground plane → copper pour on bottom. No signal traces under thermal pad.
- **DDR impedance:** Calculate trace width/spacing for target impedance
  using your PCB stackup. Get this wrong = memory errors/decreased reliability.

---

## Complete File Structure

```
soc-project/
├── README.md
├── funksjonsbeskrivelse.md
├── pinout.md
├── power_sequencing.md
├── thermal_design.md
├── firmware_arkitektur.md
├── device_tree.md
├── kommunikasjon.md
├── skjematikk_plan.md
├── pcb_plan.md
├── testplan.md
├── bruksanvisning.md
├── bygg_og_flash.md
│
├── firmware/
│   ├── bootloader/          U-Boot patches, config
│   ├── kernel/              Kernel config fragments, patches
│   ├── device-tree/         .dts, .dtsi overlay files
│   ├── userspace/
│   │   ├── app/             Main application source
│   │   ├── systemd/         Service units
│   │   └── ota/             OTA update scripts
│   └── rootfs/              Yocto layer or Buildroot config
│
├── hardware/
│   ├── schematic/
│   │   └── soc-project.kicad_sch
│   ├── pcb/
│   │   └── soc-project.kicad_pcb
│   ├── datasheets/
│   └── bom/
│       └── bom.csv
│
└── test/
    ├── boot_test/           Boot timing, sequence verification
    ├── peripheral_test/     GPIO, I2C, SPI, UART loopback
    ├── thermal_test         Thermal imaging, stress test
    └── ota_test             Update verification, rollback test
```

---

## Tips & Pitfalls

### Hardware
- **Power sequencing is NOT optional:** SoCs will be damaged or fail to boot
  if rails come up in the wrong order. ALWAYS follow the datasheet sequence.
- **Bypass caps placement:** For SoCs, placement and values are critical.
  Follow the vendor schematic EXACTLY — guess = instability.
- **DDR layout is a hard requirement:** Signal integrity on DDR traces is
  non-negotiable. If you cannot meet impedance/length requirements, reduce
  DDR speed grade before changing the layout approach.
- **Thermal design affects reliability:** A SoC at 10°C above max junction
  temperature halves its expected lifetime. Always validate with thermal
  imaging under full load.
- **Boot strap pins:** Document the reset state of all boot configuration pins.
  A wrong pull-up/pull-down = SoC won't boot.

### Software
- **Device tree is the single source of truth:** The kernel uses DT to know
  what hardware exists. A wrong DT = driver never loads = mystery failures.
- **Don't use userspace for time-critical I/O:** GPIO bit-banging in Python
  has ms jitter. Use kernel driver or PRU (TI) / RISC-V coprocessor (ESP32)
  for μs-precise timing.
- **Yocto/Buildroot: use kas or repo tool** for reproducible builds. Never
  manually edit layers — version-control your manifest.
- **OTA must have A/B partitions:** A failed brick in the field is unrecoverable
  without physical access. Always implement rollback capability.

### Behavioral Pitfalls
- **"Kontinuasjon" ≠ "same project":** Read the full spec first.
- **Handover-ready documentation:** Same standard as MCU projects — Norwegian,
  self-contained, README-first.
- **See `mcu-project-planning` behavioral pitfalls** — same rules apply.

## References

- U-Boot Documentation: https://docs.u-boot.org/
- Linux Device Tree Documentation: https://devicetree-specification.readthedocs.io/
- Yocto Project: https://docs.yoctoproject.org/
- Buildroot: https://buildroot.org/downloads/manual/manual.html
- Raspberry Pi Docs: https://www.raspberrypi.com/documentation/computers/
- NVIDIA Jetson Docs: https://developer.nvidia.com/embedded/learn/jetson-embedded-systems
- NXP i.MX Docs: https://www.nxp.com/design/design-center/development-boards-and-designs:IMX-SBCS
