# PC Build Configuration — Reference

## Typical Build: Music / Office / Browsing

For use cases like music recording (DAW), office work, and browsing — a dedicated GPU is NOT needed. Intel Arc integrated graphics in Core Ultra 7 265 is sufficient.

### Core Components (Custom Build) — Komplett.no Prices 2026-06-03

| Component | Product | Price (NOK) | Status |
|-----------|---------|-------------|--------|
| **CPU** | Intel Core Ultra 7 265 (non-K) | 4.373,- | Check stock |
| **CPU alt** | Intel Core Ultra 7 265K | 4.990,- | Higher TDP, needs better cooler |
| **Motherboard** | ASUS Prime Z890-P WIFI7 (ATX, DDR5, WiFi7, **USB4**) | 2.389,- | ✅ 33stk på lager |
| **RAM** | Corsair Vengeance RGB DDR5 6000MHz 32GB (2x16GB) | 4.990,- | ✅ På lager |
| **RAM alt** | Corsair Vengeance RGB DDR5 6400MHz 32GB CL32 | ~5.200,- | ✅ Worth the premium for music production |
| **SSD** | Kingston KC3000 2TB NVMe (7000/7000 MB/s) | 3.219,- | ✅ 50+ stk |
| **PSU** | Corsair RM750e 750W ATX 3.1 Gold | 1.274,- | ✅ 50+ stk |
| **AIO Cooler** | Phanteks Glacier One 360M25 | 1.169,- | ✅ 50+ stk |
| **Case** | Cooler Master MasterBox CM695 (5.25" bay) | Ikke på Komplett | Brukt ~500-1.000 på FINN.no |
| **Optical** | LG / Pioneer slim Blu-ray (9.5mm SATA) | Ikke på Komplett | Ekstern USB ~600 |
| **Total (uten case+optisk)** | | **~17.414,-** | |

**CPU note**: User confirmed Core Ultra 7 265 (non-K), NOT 265K. Non-K has lower TDP (65W vs 125W), runs cooler, perfectly sufficient for music/office/browsing. Price difference ~600 NOK.

**Motherboard note**: ASUS Prime Z890-P WIFI7 confirmed to have USB4 on rear I/O. Double-check before ordering — ASUS product page lists "USB4 40Gbps" specifically.

**Case note**: FINN.no blocks bot scraping entirely. User must search manually for cases with 5.25" bay. Alternative: ekstern USB Blu-ray (~500-800 NOK) which avoids the case requirement.

### Alternative: Lenovo ThinkCentre M70t Gen 6 (Pre-built)

Pre-built alternative covering many requirements. User specifically requested evaluation of this model.

| Spec | Value |
|------|-------|
| CPU | Core Ultra 7 265 (non-K, close to 265K performance) |
| RAM | Up to 128GB DDR5, 4 UDIMM slots |
| Storage | 4 drives (NVMe + SATA) |
| Optical | DVD-ROM/DVD-RW (slim SATA) — included |
| USB | USB 3.2 Gen2, USB-C |
| WiFi | WiFi 6E, BT 5.3 |
| GPU | Intel Arc integrated (sufficient for office/music/browsing) |
| Form factor | Tower |
| Price (Lenovo.no) | ~12,000-15,000 NOK base config |

**Trade-off**: Pre-built is cheaper and includes Windows license + optical drive. Less customizable. Uses B860 chipset — confirm 265K compatibility before buying (may need BIOS update).

**Verdict**: For music recording + office + browsing, the M70t Gen 6 with Core Ultra 7 265 + 32GB RAM upgrade is ~15,000-17,000 NOK all-in. Custom build with same specs is ~19,500+ NOK without optical drive. Pre-built wins on price + includes optical.

## DDR5 Price Crisis (2025-2026)

DDR5 prices increased ~4x since September 2025 due to AI/memory demand:
- 32GB DDR5-6000 kit: Was ~1000 NOK → Now ~4.990 NOK
- 16GB DDR5 kit: Was ~500 NOK → Now ~2.500 NOK

**Options**: Wait for price drop, buy used, or start with 16GB and upgrade later.

## Audio Recording Add-on

For music production, add a USB audio interface:
- **Focusrite Scarlett 2i2** (~1.500 NOK) — 2-in/2-out, ASIO, low latency
- **Audient iD14** (~2.500 NOK) — Better preamps, ADAT expansion
- **Behringer UMC202HD** (~800 NOK) — Budget option, decent quality

## GPU Selection Guide

| Use Case | GPU | Notes |
|----------|-----|-------|
| Office/browsing/music | Integrated (Intel Arc / AMD Radeon) | Sufficient. Saves 3.000-6.000 NOK |
| 1080p gaming | RTX 4060 / RX 7600 | Budget-friendly |
| 1440p gaming | RTX 4070 Super / RX 7800 XT | Sweet spot |
| 4K gaming | RTX 4080 Super / RX 7900 XTX | High-end |
| AI/ML (CUDA) | RTX 4070 Ti+ | NVIDIA only for CUDA |
| AI/ML (inference) | RTX 4060 Ti 16GB | VRAM matters more than speed |

## Compatibility Checklist

- [ ] CPU socket matches motherboard (LGA 1700, LGA 1851, AM5, etc.)
- [ ] RAM type matches board (DDR4 vs DDR5 — NOT interchangeable)
- [ ] PSU wattage headroom: CPU TDP + GPU TDP + 100W margin
- [ ] Case supports cooler height / radiator size
- [ ] Case supports GPU length (important for 3+ fan GPUs)
- [ ] M.2 slots available for NVMe SSDs
