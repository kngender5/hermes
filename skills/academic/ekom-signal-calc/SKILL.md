---
name: ekom-signal-calc
description: Kabel-TV (HFC) og signalberegninger for EKOM-fag. Beregner signalnivå ved uttak, kabeltap (LF/HF), splitter-/avgrenertap, og sjekker mot min/max-krav. Brukes for caser med kabel-TV-distribusjon i boligbloker. Integreres med ekom-solver for underliggende beregninger.
category: academic
triggers:
  - kabel-tv
  - kabel tv
  - hfc
  - signalnivå
  - signalberegning
  - kabeltap
  - avgrener
  - splitter tap
  - headend
  - koaksialkabel
  - rg6
  - rg11
  - signal level
  - dBuV
  - dBµV
  - kabel-tv case
---

# Kabel-TV Signalberegning

Beregner signalnivå i kabel-TV (HFC-nett). Bruker solver for underliggende
beregninger — estimer aldri.

## Når denne skillen brukes

- Case med kabel-TV-distribusjon i boligblokk
- Beregning av signalnivå ved uttak
- Splitter/avgrener-kjeder med kabeltap
- LF (47-83 MHz) og HF (470-862 MHz) beregninger
- Sjekk mot min/max signalnivå

## Kabel-TV-signalformel

```
P_ut = P_he - L_kabel - L_split - L_tap - L_connector

Hvor:
  P_he       = Headend-utgangsnivå (typisk 90-110 dBµV)
  L_kabel    = Kabeltap = (dB/100m × lengde_i_m) / 100
  L_split    = Splitter-gjennomgangstap
  L_tap      = Avgrenertap (branch tap)
  L_connector = Kontakttap (typisk 1 dB totalt ved uttak)
```

## Standard kabeltap (SJEKK MOT CASE — bruker dette som default)

### RG6 (typisk for grenledning til uttak)
| Frekvens | dB/100m |
|----------|---------|
| 83 MHz (LF) | 6.4 |
| 865 MHz (HF) | 20.0 |

### RG11 (typisk for hoved/fordelingskabel)
| Frekvens | dB/100m |
|----------|---------|
| 83 MHz (LF) | 3.87 |
| 865 MHz (HF) | 13.0 |

### Koaksialkabel generelt (fallback)
| Frekvens | dB/100m |
|----------|---------|
| 50 MHz | 5.0 |
| 100 MHz | 7.0 |
| 450 MHz | 14.0 |
| 860 MHz | 20.0 |

**⚠️ VIGTIGT:** Case skal alltid spesifisere kabeltype og demping. Bruk case-verdier først.

## Splitter og avgrenere — tap-verdier

### Kabel-TV-splitter (gjennomgang / tap)
| Komponent | Gjennomgang | Avgrener |
|-----------|-------------|----------|
| 2-veis | 3.5 dB | 3.5 dB |
| 4-veis | 7.0 dB | 3.5 dB |
| 8-veis | 11.0 dB | 3.5 dB |

### Avgrenere / Tap
| Avgrener | Gjennomgang | Avgrener |
|----------|-------------|----------|
| 8 dB | 3.0 dB | 8 dB |
| 12 dB | 1.5 dB | 12 dB |
| 16 dB | 1.0 dB | 16 dB |
| 20 dB | 0.8 dB | 20 dB |
| 24 dB | 0.6 dB | 24 dB |

**Ved trinnvis beregning (typisk eksamensoppgave):**
```
Trinn 1: Headend → kabel → splitter → kabel → avgrener → ... → Uttak
Trinn 2: KUMULER AV TAP — ikke konverter til mW
Trinn 3: P_ut = P_he - SUM(alle tap)
```

## Min/max signalnivå ved uttak

| Parameter | Min | Max | Enhet |
|-----------|-----|-----|-------|
| Digitalt TV-signal (DVB-C) | 47 | 80 | dBµV |
| Analogt TV-signal | 57 | 77 | dBµV |
| DOCSIS (data) | 50 | 80 | dBµV |
| SNR (signalt-til-støy) | 28 | - | dB |
| BER (bit-feilrate) | - | 10⁻¹¹ | - |

**Ved utenfor skallet:** Enten forsterk (amplifier) eller endre kabeldimensjon.

## Arbeidsflyt for kabel-TV-case

```
1. LES caset — finn headend-nivå, antall etasjer, kabeltyper, splitter- og avgrener-typer
2. LAG prinsippskisse (tekstbasert):
   Headend (XX dBµV) → [kabel RG11, XXm, LF: X dB / HF: X dB] → Splitter 4-vei (X dB) → ... → Uttak
3. BEREGN kabeltap for LF og HF separat:
   L_kabel_LF = (dB/100m_LF × lengde_m) / 100
   L_kabel_HF = (dB/100m_HF × lengde_m) / 100
4. SUMMER alle tap (gjennomgang + avgrenere + konnektorer)
5. BEREGN signal ved uttak:
   P_ut_LF = P_he - L_tot_LF
   P_ut_HF = P_he - L_tot_HF
6. SJEKK mot min/max-verdier
7. KONKLUDER: Innenfor/utenfor? Hva må justeres?
```

## Eksempelberegning

```
Headend: 100 dBµV
Kabel RG11, 200m til 4-veis splitter: LF: 3.87×200/100 = 7.74 dB, HF: 13.0×200/100 = 26.0 dB
Splitter 4-vei (gjennomgang): 7.0 dB
Kabel RG6, 50m til uttak: LF: 6.4×50/100 = 3.2 dB, HF: 20.0×50/100 = 10.0 dB
Uttak (kontakt): 1.0 dB

LF tap totalt: 7.74 + 7.0 + 3.2 + 1.0 = 18.94 dB
HF tap totalt: 26.0 + 7.0 + 10.0 + 1.0 = 44.0 dB

P_ut_LF = 100 - 18.94 = 81.06 dBµV  → OVER MAX (80 dBµV) → Må dempes!
P_ut_HF = 100 - 44.0 = 56.0 dBµV   → Innenfor (47-80 dBµV) → OK

Justering: Sett inn 4 dB demper ved uttak → LF = 77.06, HF = 52.0
⚠️ Etter justering SJEKK IGJEN.
```

## Kald solver for kabel-TV

```bash
# Direkte signalberegning
cd ~/projects/study-workbench/workspace_calculations
python3 ekom_solver.py -k '{"P_he":100,"L_kabel":18.9,"L_split_kt":7.0,"L_tap":0}' -t P_ut
```

Eller bruk `full_analysis` for å se hva som kan regnes ut fra kjente variabler.

## Common Pitfalls

1. **LF og HF beregnes SEPARAT** — forskjellig kabeltap per frekvens
2. **Splitter-gjennomgang ≠ splitter-avgrener** — les oppgaven nøyaktig
3. **dBµV er logaritmisk** — du kan IKKE konvertere til lineær og summere
4. **Kontakttap ved uttak** — ofte glemt, typisk 0.5-1 dB
5. **Etter justering SJEKK IGJEN** — en demper endrer både LF og HF
