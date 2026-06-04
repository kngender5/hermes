---
name: ekom-lovverk
description: Forskrift/standard-mapping for grounded reasoning i EKOM-fag. Brukes i eksamenssvar for å referere korrekt til forskrifter, standarder og paragrafer. Dekker Ekomloven, Ekomforskriften, Elsikkerhetsforskriften, NEK 400, NEK 701/702, MICE-klassifisering, EMC-separasjon, brannkrav og dokumentasjon. Gir sensor-godvile ved korrekt lovverk-referanse.
category: academic
triggers:
  - lovverk
  - forskrift
  - standard
  - NEK
  - NEK 400
  - NEK 701
  - NEK 702
  - ekomlov
  - ekomforskrift
  - elsikkerhet
  - paragraf
  - §
  - MICE
  - EMC
  - segregasjon
  - brannkrav
  - dokumentasjon
  - hvilken forskrift
  - hvilken standard
  - begrunn med lov
  - begrunn med forskrift
  - begrunn med standard
  - lovverk referanse
  - føringsvei
  - bøyeradius
  - fyllingsgrad
  - separasjonsavstand
---

# EKOM Lovverk og Standarder — Grounded Reasoning

Brukes for å gi korrekte forskrift/standard-referanser i eksamenssvar.
Kalles av `ekom-exam-writer` og `ekom-solver` når case krever lovverk-mapping.

## Viktig: Lov vs Forskrift vs Standard

| Type | Eksempel | Bruk på eksamen |
|------|----------|-----------------|
| **Lov** | Ekkomloven | Overordnet rammeverk — refereres sjelden direkte |
| **Forskrift** | Ekomforskriften, Elsikkerhetsforskriften | **REFERERES SAMMEN MED STANDARDER** |
| **Standard** | NEK 400, NEK 701, NEK EN 50174 | Konkrete krav og verdier |

**→ Referer ALLTID til FORSKRIFTEN + STANDARDEN, ikke bare loven.**

## Komplett forskrift/standard-oversikt

### Ekomloven og tilhørende forskrifter

| Forskrift | Formål | Nøkkelparagrafer | Bruksområde |
|-----------|--------|------------------|-------------|
| **Ekomloven** | Hovedloven for elektronisk kommunikasjon | § 1-5 (definisjoner) | Overordnet — refereres sjelden |
| **Ekomforskriften** | Installasjon, drift, vedlikehold av ekom-nett | Kap. 10 (private nett) | Private installasjoner |
| **Elsikkerhetsforskriften** | Elsikkerhet i ekom-nett | § 1, § 4, § 6, § 9 | **OFTEST REFERERT** |
| **Autorisasjonsforskriften** | Krav til virksomheter | § 4, § 5, § 6, § 7 | Bedriftskrav |
| **Internkontrollforskriften** | Risikokartlegging | § 5 | HMS/dokumentasjon |

### Elsikkerhetsforskriften — viktige paragrafer

| Paragraf | Krav | Bruk |
|----------|------|------|
| **§ 1** | Formål: Hindre at spenninger/strømmer skader liv, helse, eiendom | Generell begrunnelse |
| **§ 4** | Sikkerhetskrav — oppfylt når relevante standarder i § 6 er fulgt | **Hovedparagraf for krav** |
| **§ 6** | Standarder: NEK 400, NEK-EN 50083-1, NEK-EN 50174-1/2 | **Standard-referanse** |
| **§ 9** | Dokumentasjon — oppbevares så lenge nettet er i drift | Dokumentasjonskrav |

**Eksempel-referanse:**
> "Ifølge Elsikkerhetsforskriften § 4 skal sikkerhetskrav være oppfylt når
> relevante standarder i § 6 er fulgt, herunder NEK 400 for elektriske
> installasjoner."

### NEK 700-serien (Strukturert kabling)

| Standard | Tittel | Bruksområde |
|----------|--------|-------------|
| **NEK 701** | Felles kablingssystemer (EN 50173) | Kablingsstruktur, klasser, lengder |
| **NEK 702** | Installasjon innendørs (EN 50174-1/2) | Installasjonskrav, føringsveier |
| **NEK 702 Del 3** | Installasjon utendørs (EN 50174-3) | Utendørs installasjon |
| **NEK 703** | Anlegg og infrastruktur i datasentre (EN 50600) | Datasentre |

### NEK 701 — Kablingklasser

| Klasse | Frekvens | Anvendelse |
|--------|----------|------------|
| A | 100 kHz | Telefon |
| B | 1 MHz | ISDN |
| C | 16 MHz | 10/100 Mbps |
| D | 100 MHz | Gigabit Ethernet |
| E | 250 MHz | 2.5 Gbps |
| EA | 500 MHz | 5 Gbps |
| F | 600 MHz | 10 Gbps |
| FA | 1000 MHz | 10 Gbps+ |

### NEK 701 — Komponentkrav

| Kanal-klasse | Minimum kabel-kategori |
|--------------|----------------------|
| C (Cat 3) | Kategori 3 |
| D (Cat 5e) | Kategori 5e |
| E (Cat 6) | Kategori 6 |
| EA (Cat 6A) | Kategori 6A eller 8.1 |
| F (Cat 7) | Kategori 7 |
| FA (Cat 7A) | Kategori 7A eller 8.2 |

**⚠️ Viktig:** Kanalytelse begrenses av komponenten med LAVEST ytelse.

### NEK 701 — Kabellengder

| Type | Maks |
|------|------|
| Permanent link | 90 m |
| Kanal (total) | 100 m |
| OF til EF | 2000 m |
| FB-TO (arbeidssnor) | 20 m |
| Horisontalkabel (med CP) | min 15 m |

### NEK 701 — Fjernmating-kategorier

| Kategori | Strøm (Ic-middel) | Krav |
|----------|-------------------|------|
| RP1 | ≤ 212 mA | Dokumentasjon og administrativ kontroll |
| RP2 | 212 mA – 500 mA | Egne metoder for planlegging og installasjon |
| RP3 | ≤ 500 mA | Egne metoder + dokumentasjon og administrativ styring |

### NEK 701 — MICE-miljøklassifisering

| Dimensjon | Klasse 1 (lav) | Klasse 2 (middels) | Klasse 3 (høy) |
|-----------|----------------|--------------------|-----------------|
| M (Mekanisk) | Lav | Middels | Høy |
| I (Inntrengning) | Tett | Delvis tett | Åpen |
| C (Klimatisk) | Kontrollert | Delvis kontrollert | Ukontrollert |
| E (Elektromagnetisk) | Lav EMI | Middels EMI | Høy EMI |

Typisk: Kontor = M1I1C1E1, Lette industri = M2I2C2E2, Tyngre industri = M3I3C3E3

### NEK 702 — Føringsveier og installasjon

| Parameter | Krav | Kilde |
|-----------|------|-------|
| Fyllingsgrad | Maks 40 % | NEK 702 |
| Maks kabler per bunt | 24 stk | NEK 702 |
| Stablingshøyde (fast underlag) | Maks 150 mm | NEK 702 |
| Avstand mellom underlag | Maks 1500 mm | NEK 702 |
| Bøyeradius metallisk kabel | 8× ytterdiameter | NEK 702 |
| Bøyeradius fiber/koaks | 10× ytterdiameter | NEK 702 |
| Rør — maks bend mellom trekkepunkter | 2 stk à 90° (total 180°) | NEK 702 |
| Rørbend — min radius | 6× innvendig rørdiameter | NEK 702 |
| Rør i bolig — min diameter | 38 mm (Size 40) | NEK 702 |
| Avstand til varmerør | Min 0.1 m (med mindre isolasjon) | NEK 702 |
| Klaring over føring | 50 mm | NEK 702 |
| Kabelstige til vegg | 25 mm | NEK 702 |

### NEK 702 — EMC-separasjon

**Formel: A = S × P**

| IT-kabel klasse | S (meget god) | S (god) | S (mindre god) |
|-----------------|---------------|---------|-----------------|
| a (skjermet, god) | 10 mm | 30 mm | 300 mm |
| b (skjermet) | 10 mm | 30 mm | 150 mm |
| c (uskjermet) | 10 mm | 50 mm | 300 mm |
| d (uskjermet, dårlig) | 30 mm | 100 mm | 300 mm |

| Antall kretser | P (faktor) |
|----------------|------------|
| 1-3 | 0.2 |
| 4-6 | 0.4 |
| 7-20 | 0.6 |
| >20 | 0.8 |

**Minste separasjon:**
- ≤ 1000V AC / 1500V DC: **0.05 m**
- \> 1000V AC / 1500V DC: **0.3 m**
- Kryssingsvinkel: **90°**

### NEK 702 — Brannkrav

| Sted | Krav |
|------|------|
| Rømningsvei | Minst Eca, Dca s2,d2,a2 |
| Brannskille | Minst Eca |
| Eksterne kabler inn | Termineres utenfor brannskille eller maks 2m eksponert |

### NEK 702 — Romstørrelse for telekommunikasjonsrom

| Termineringspunkter | Kun kabling | Med aktivt utstyr |
|---------------------|-------------|-------------------|
| ≤ 500 | 3.2m × 2.2m | 3.2m × 3.0m |
| Per 500 ekstra | +0.8m | +1.6m |

### NEK 400 — Elektriske installasjoner

| Parameter | Verdi | Merknad |
|-----------|-------|---------|
| Kursikring | 16 A | Standard |
| Kabel | 2.5 mm² Cu | Standard |
| Jordfeilbryter (RCBO) | 30 mA | Obligatorisk |
| Karakteristikk | C | For utstyr med høy startstrøm |
| Maks spenningsfall | 2-4 % | **ANBEFALING, ikke krav!** |
| Kobber ρ | 0.0175 Ω·mm²/m | Ved 20°C |
| Aluminium ρ | 0.028 Ω·mm²/m | Ved 20°C |

### NEK 400 — Overspenningsvern

| Type | Plassering |
|------|------------|
| Type 1 | Inntak |
| Type 2 | Hovedfordeler |
| Type 3 | Ved utstyr |

### NEK 400 — Dokumentasjon (obligatorisk)

- Samsvarserklæring
- Sluttkontroll (måltekniske resultater)
- Brukerveiledning (norsk)
- Kursfortegnelse
- FTV-dokumentasjon

## Lovverk-mapping for typiske eksamensoppgaver

### Fiber/FTTH-case
```
Beregningskrav → Ingen direkte lovverk, men:
- Sjekk mot NEK 701 (kablingsstruktur)
- Sjekk mot NEK 702 (installasjon, føringsveier)
- Dokumentasjon → Elsikkerhetsforskriften § 9
- Sikkerhet → Elsikkerhetsforskriften § 4 + § 6
```

### Kabel-TV-case
```
Signalnivå → NEK-EN 50083-1 (via Elsikkerhetsforskriften § 6)
Installasjon → NEK 702
Føringsveier → NEK 702
```

### Strukturert kabling-case
```
Kabellengder → NEK 701 (90m/100m)
Kablingklasser → NEK 701
Føringsveier → NEK 702
EMC-separasjon → NEK 702 (A = S × P)
Brannkrav → NEK 702
Fjernmating → NEK 701 (RP1/RP2/RP3)
```

### EMC-case
```
Separasjon → NEK 702 (A = S × P)
Kryssing → 90°
Høy spenning → 0.3m minimum
```

## Korrekt referansestil på eksamen

**Gjør dette:**
> "Ifølge Elsikkerhetsforskriften § 4 skal sikkerhetskrav være oppfylt når
> relevante standarder nevnt i § 6 er fulgt, herunder NEK 400 for elektriske
> installasjoner."

**Ikke dette:**
> "NEK sier at spenningsfall skal være under 4%"
> (Det er en ANBEFALING, ikke et krav!)

**Bonuspoeng-referanse:**
> "Dokumentasjon skal oppbevares så lenge installasjonen er i drift,
> jf. Elsikkerhetsforskriften § 9."

## Kunnskapsgraf-spørring

For detaljert informasjon om et spesifikt emne, spørr kunnskapsgrafen:

```bash
cd ~/projects/study-workbench
# Søk etter noder med spesifikke tags
grep -l "NEK 702" workspace_groundtruth/knowledge_graph/domain_nek_hms_reg.jsonl
# Vis en spesifikk node
python3 -c "
import json
for line in open('workspace_groundtruth/knowledge_graph/domain_nek_hms_reg.jsonl'):
    n = json.loads(line)
    if n.get('id') == 'nek702-separation-power-cables':
        print(json.dumps(n, indent=2, ensure_ascii=False))
"
```
