# SCL → LAD/FBD Konverteringsteknikk

## Når brukes dette

Når du har SCL-kode (Structured Control Language — Siemens tekstbasert Pascal-lignende språk) som må konverteres til LAD (Ladder) eller FBD (Function Block Diagram) for å oppfylle oppgavekrav (f.eks. AUT23: "Språk: FBD og LAD (KUN disse to)").

SCL-filene kan beholdes som referanse/dokumentasjon i en `scl/`-mappe, men den faktiske TIA Portal-implementasjonen må bygges i LAD/FBD.

## Format for visuell tekstbeskrivelse

Lag en `.txt`-fil for hver SCL-fil med følgende format:

```
================================================================================
[NAVN] — [Funksjonsbeskrivelse]
================================================================================
Prosjekt:  Varemottak og Lager — AUT23
Språk:     LAD / FBD (bygges i TIA Portal)
Versjon:   3.0 — Konvertert fra SCL
Dato:      2026-05-31

For hvert nettverk:
NETTVERK [N]: [Tittel]
Funksjon: [Hva nettverket gjør]

I TIA Portal (LAD):
+---[ ]----+---[ ]----+---( )---+
| Signal1  | Signal2  | Utgang   |
+----------+----------+----------+

I TIA Portal (FBD):
+--------+    +--------+
|  AND   |    |  MOVE  |
| IN1: A |    | EN: 1  |
| IN2: B |    | IN: 99 |
| Q:-----|--->| OUT: X |
+--------+    +--------+

Bygg-instruksjer: [Stegvis forklaring]
```

## LAD-notasjon

| Symbol | Betydelse |
|--------|-----------|
| `+---[ ]----+` | NO-kontakt (Normally Open) |
| `+---[/]----+` | NC-kontakt (Normally Closed) |
| `+---( )----+` | Coil/utgang |
| `+---( S )---+` | SET-coil |
| `+---( R )---+` | RESET-coil |
| `+---[= ]----+` | Sammenligning likhet |
| `+---[>=]----+` | Sammenligning større eller lik |

## FBD-notasjon

| Symbol | Betydelse |
|--------|-----------|
| `+--[ AND ]--+` | AND-blokk |
| `+--[ OR ]---+` | OR-blokk |
| `+--[ NOT ]--+` | NOT-blokk |
| `+--[ MOVE ]-+` | MOVE-blokk |
| `+--[ CMP ==]+` | Sammenligning likhet |
| `+--[ TON ]--+` | On-Delay timer |
| `+--[ ADD ]--+` | Addisjon |
| `+--[ SUB ]--+` | Subtraksjon |
| `+--[ MUL ]--+` | Multiplikasjon |
| `+--[ DIV ]--+` | Divisjon |

## Vanlige SCL → LAD/FBD mønstre

### IF/THEN → LAD
IF A AND B THEN C := TRUE; END_IF;
→ LAD: +---[A]----+---[B]----+---(C)---+

### IF/THEN/ELSE → LAD
IF A THEN B := TRUE; ELSE B := FALSE; END_IF;
→ LAD: +---[A]----+---(B)---+

### CASE → LAD (sekvensielle nettverk)
IF SeqStep = 0 THEN CALL FC_Step0; END_IF;
IF SeqStep = 1 THEN CALL FC_Step1; END_IF;
→ LAD: Serie med [==] sammenligninger, hver med sin CALL.

### TON-timer → FBD
TON_1(IN:=A, PT:=T#100ms);
→ FBD: TON-blokk med IN=A, PT=T#100ms, Q til påfølgende logikk.

### SR-vippe → LAD
IF A AND B THEN SR:=TRUE; END_IF;
IF C OR D THEN SR:=FALSE; END_IF;
→ LAD: SET: +---[A]----+---[B]----+---( S )---+ (SR)
     RESET: +---[C]----+---[/]----+---( R )---+ (SR)

### Aritmetikk → FBD
Result := (A - B) * 100 / (C - B);
→ FBD: SUB(A,B) → MUL(100) → SUB(C,B) → DIV → Result

## Delegering til subagenter

Ved konvertering av mange filer (>10), deleger til parallelle subagenter:
- Maks 3 subagenter om gangen (config-begrensning)
- Gi hver subagent 3-9 filer
- Inkluder eksplisitt format-mal i instruksjonen
- Spesifiser filnavn for hvert resultat
- Subagenter timeouter ofte ved >8 filer — hold deg til 4-6 per subagent

## Eksempel

Se ~/projects/study-workbench/prosjektoppgave/program/plc/ladder-FB/ for komplett eksempel med 30 konverterte filer (OB1, OB100, FB1-3, FC1-5+Step0-11+Alarm, DB1-4+10-12).
