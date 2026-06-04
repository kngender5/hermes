# TIA Portal v19 Import Guide

Generert etter arbeid med Varemottak og Lager-prosjektet, 2026-05-27.

## PLC-variabler XML

Format: `io/plc_variabler_tia_tia.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<PlcTags>
  <PlcTag Name="START_KNAPP" DataType="Bool" Address="%I0.0" Comment="Start-knapp. NO." />
  <PlcTag Name="TotalPaller" DataType="Int" Address="" Comment="Total antall paller" />
  <!-- Array: -->
  <PlcTag Name="Pall_Etasje" DataType="Array[1..3] of Int" Address="" Comment="Palltelling per etasje" />
</PlcTags>
```

Attributter:
- `Name` — Variabelnavn (norske descriptive navn)
- `DataType` — `Bool`, `Int`, `DInt`, `Real`, `Array[1..3] of Int`
- `Address` — PLS-adresse med `%`-prefiks: `%I0.0`, `%Q0.0`, `%IW64`, `%QW80`. Tom for interne variabler.
- `Comment` — Norsk beskrivelse

Import i TIA Portal: PLC-variabel-tabell → Høyreklikk → Import → velg XML-fil.

Merk: Bruk UTF-8 med BOM og CRLF linjeslutt for best kompatibilitet.

## HMI-tags XML

Format: `io/hmi_tags.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<HmiTags>
  <HmiTag Name="HMI_TotalPaller" DataType="Int" Source="DB3.HMI_TotalPaller" Comment="Total paller" />
  <HmiTag Name="HMI_Cmd_Start" DataType="Bool" Source="DB3.Cmd_Start" Comment="Start-knapp" />
</HmiTags>
```

Attributter: `Name`, `DataType`, `Source` (PLS-variabelsti), `Comment`.

## Datablokker CSV

Format: `io/datablokker.csv` — semikolon-separert for norsk Excel.

```
DB1 — Telleregister (RETAIN)
Variabel;Datatype;Startverdi;Kommentar
TotalPaller;Int;0;Totalt antall håndterte paller
Pall_Liten;Int;0;Antall paller: liten størrelse
Pall_Etasje[1];Array[1..3] of Int;[3(0)];Palltelling per etasje
```

## Oppsummert antall variabler (Varemottak og Lager)

Fra eksempelprosjektet:
- 20 DI innganger
- 19 DO utganger (16 normale + 3 reserverte)
- 2 AI innganger
- 1 AQ utgang
- 12 reserverte DI adresser
- 7 reserverte DO adresser
- 20 interne variabler (DB3 HMI_Tags)
- Totalt: 81 variabler i XML-import
- 30 HMI-tags

## Filtyper per import

| Fil | Type | Import-target |
|-----|------|---------------|
| `plc_variabler_tia.xml` | XML | PLC → Variables table |
| `hmi_tags.xml` | XML | HMI → Tags |
| `datablokker.csv` | CSV | Manuelle DB-oppsett (eller Excel-import) |
