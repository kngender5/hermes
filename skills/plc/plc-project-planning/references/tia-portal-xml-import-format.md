# TIA Portal XML Import Format — Block Interfaces

**Discovered:** 2026-06-01. This is the SimaticML XML format for importing FC/FB/OB block interfaces into TIA Portal v19.

## Key Facts

- This format imports **block interfaces only** (input/output/temp/constant sections) — NOT code
- Different from SCL import: SCL imports UDTs/DBs, XML imports block interfaces
- Two separate import mechanisms in TIA Portal v19

## XML Schema

```xml
<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V19"/>
  <SW.Blocks.FC ID="100" Name="FC_Step0_Init">
    <AttributeList>
      <Name>FC_Step0_Init</Name>
      <Number>100</Number>
      <HeaderFamily>FC</HeaderFamily>
      <ProgrammingLanguage>LAD</ProgrammingLanguage>
      <MemoryLayout>Optimized</MemoryLayout>
    </AttributeList>
    <Interface>
      <Sections>
        <Input><!-- input params --></Input>
        <Output><!-- output params --></Output>
        <InOut><!-- inout params --></InOut>
        <Temp><!-- local temp vars --></Temp>
        <Constant><!-- local constants --></Constant>
        <Return><!-- FC return value --></Return>
      </Sections>
    </Interface>
    <ObjectList>
      <MultilingualText ID="L01">
        <Comment>Norwegian comment here</Comment>
      </MultilingualText>
      <MultilingualText ID="L02">
        <Title>Block title in Norwegian</Title>
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.FC>
</Document>
```

## File Naming Convention

Reference files: `io/scl_blocks/` contains 24 XML files for all FC/FB/OB blocks.

## Combined Import File

`io/TIA_Import_All.xml` — Combined file containing:
1. UDT definitions (12 UDTs)
2. User Constants (STEP_0-11+99, TARGET_1-3, STATUS_0-3, ALARM_0-6)
3. DB definitions (structured via UDTs)
4. Block interfaces (FC/FB/OB — no code)

**User Constants defined:**
| Constant Group | Values |
|---|---|
| STEP_0 through STEP_11 | Sequence step numbers |
| STEP_99 | Alarm step |
| TARGET_1, TARGET_2, TARGET_3 | Floor targets (Stor, Medium, Liten) |
| STATUS_0 through STATUS_3 | Av, Drift, Standby, Alarm |
| ALARM_0 through ALARM_6 | None, Nødstopp, Dør, HeisTimeout, StørrelseFeil, EmitterTimeout, FullEtasje |

## UDT-Path DB References

When UDTs are used, ALL FC/FB references must use the UDT path format:
- `DB3.Status.SeqStep` (not `DB3.SeqStep`)
- `DB2.Alarm.Safety_OK` (not `DB2.Safety_OK`)
- `DB4.Konfig_Tid.Timeout_Heis` (not `DB4.Timeout_Heis`)
- `DB3.Kommando.Cmd_Start` (not `DB3.Cmd_Start`)

All ladder-FB files and XML import files must be updated consistently when DB structure changes.
