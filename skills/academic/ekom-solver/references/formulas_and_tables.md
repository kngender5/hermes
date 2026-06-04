# Formelsamling og nøkkeltall — EKOM

**Pugg denne.** Alt her er ofte testet på eksamen.

---

## Desibel

```
dB  = 10 · log₁₀(P₁/P₂)       ← EFFEKT (10-logaritmen)
dB  = 20 · log₁₀(V₁/V₂)       ← SPENNING (20-logaritmen)
dBm = 10 · log₁₀(P/1 mW)       ← Absolutt effekt (ref: 1 mW)
```

| dB | Effekt | dBm | mW |
|----|--------|-----|-----|
| -30 | 0,001 µW | -30 | 0,001 µW |
| -10 | 0,1 mW | 0 | 1,0 mW |
| -3 | 0,5 mW | +3 | 2,0 mW |
| +3 | 2× | +10 | 10 mW |
| +10 | 10× | +20 | 100 mW |
| +20 | 100× | +30 | 1 W |

---

## Fiberdempning (G.652D / OS2)

| Bølgelengde | dB/km | Bruk |
|-------------|-------|------|
| 850 nm (MM) | 2,5 | Multimode |
| 1310 nm | 0,35 | SM, GPON opp |
| 1490 nm | 0,25 | GPON ned |
| 1550 nm | 0,22 | TV, CWDM, ZR |
| 1383 nm (OH) | ~33 | Vann-topp (unngå!) |

## Splitterdempning

| 1:2 | 1:4 | 1:8 | 1:16 | 1:32 | 1:64 | 1:128 |
|-----|-----|-----|------|------|------|-------|
| 3 dB | 6 dB | 9 dB | 12 dB | 15 dB | 18 dB | 21 dB |

+3 dB per dobling. Splittertap gjelder i BEGGE retninger.

## Fiberbudsjett-formler

```
L_tot   = L·α + N_k·L_k + N_s·L_s + L_split + M
P_rx    = P_tx − L_tot
LB      = P_tx − P_rx_min
margin  = LB − L_tot   (> 0 dB kreves, typisk ≥ 2 dB)
L_max   = (LB − fast_tap) / α
```

## GPON SFP-klasser

| Klasse | TX | RX sens | Budsjett |
|--------|-----|---------|----------|
| B+ | 1,5–5,0 dBm | −28 dBm | 29,5 dB |
| C+ | 3,0–7,0 dBm | −32 dBm | 35,0 dB |

## PoE-standarder

| Std | Navn | PSE max | PD max |
|-----|------|---------|--------|
| 802.3af | PoE | 15,4 W | 12,95 W |
| 802.3at | PoE+ | 30 W | 25,5 W |
| 802.3bt T3 | PoE++ | 60 W | 51 W |
| 802.3bt T4 | UPoE | 100 W | 71 W |

## Spenningsfall

```
1-fase: ΔU = 2·L·I·ρ/A         (ρ Cu = 0,0175 Ω·mm²/m)
3-fase: ΔU = √3·L·I·ρ/A
ΔU%    = ΔU / U_n · 100

Grense: ≤ 4 % (anbefalt), ≤ 5 % (motor)
```

## NEK-fremføring

- Maks fylling: **40 %**
- Maks kabler/bunt: **24**
- Bøyeradius metall: **8× diameter**
- Bøyeradius fiber: **10× diameter**

## SNR og kapasitet

```
SNR (dB) = P_signal − P_støy
SNR_lin = 10^(SNR_dB/10)
Shannon: C = B·log₂(1 + SNR_lin)   [bps]
DOCSIS:  C = B·log₂(M)·(1−oh)      [bps, M=QAM, oh=0.05-0.15]
```

## EMC-separasjon

```
N_tot = N_1f + N_3f·3
P     = 0,2              (N≤3)
P     = 0,4              (4≤N≤6)
P     = 0,2·N_tot/3      (N>6)
A     = S·P              [mm]
```

## Fjernmating (NEK)

| Kategori | Strømgrense | Krav |
|----------|-------------|------|
| RP1 | I_c ≤ 212 mA | Dokumentasjon |
| RP2 | 212 < I_c ≤ 500 mA | Egne metoder |
| RP3 | I_c ≤ 500 mA | Planlegging + dok. |

## Kabellengder strukturert kabling

| Element | Maks |
|---------|------|
| Permanent link | 90 m |
| Channel | 100 m |
| PoE | 100 m |

## Frekvens/bølgelengde

```
f = 1/T                    [Hz]
λ = c/f                    [m]    c = 3×10⁸ m/s
ω = 2π·f                   [rad/s]
```
