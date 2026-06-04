---
name: tia-portal-automation
description: TIA Portal SCL import/export automation — generate .scl files for UDTs, DBs, FCs, FBs, OB, User Constants, and IO-tags that can be imported into TIA Portal v19+. Use when the user asks to create, restructure, or automate TIA Portal project setup. Covers SCL file format, UDT design, User Constants, HMI-tag Excel import, and block interface definitions.
triggers:
  - "TIA Portal"
  - "SCL import"
  - "UDT"
  - "User Constants"
  - "PLC block import"
  - "TIA automation"
  - "generate SCL"
  - "import blocks"
  - "DB structure"
  - "HMI tags"
---

# TIA Portal SCL Import Automation

## Purpose
Generate .scl and .xml files for importing UDTs, DBs, FCs, FBs, OBs, User Constants, IO-tags, and HMI-tags into Siemens TIA Portal v19+.

## Key Rules

### Import Order (CRITICAL)
ALWAYS import in this order — UDTs first, then DBs, then blocks:
1. `UDTs.scl` → PLC data types → Import
2. `DBs.scl` → Program blocks → Import
3. `DB_UserConstants.scl` → Program blocks → Import
4. `IO_Tags.xml` → PLC tags → Import
5. `HMI_Tags.xml` → HMI tags → Import
6. `FC*.scl`, `FB*.scl`, `OB*.scl` → Program blocks → Import

### SCL File Format
TIA Portal expects this exact structure:

```scl
TYPE "UDT_Name"
TITLE = 'Display Name'
VERSION : 0.1
   STRUCT
      FieldName : DataType := DefaultValue;  // Comment
   END_STRUCT;
END_TYPE
```

For DBs:
```scl
DATA_BLOCK "DB_Name"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
   VAR
      FieldName : DataType := DefaultValue;
      UDT_Field : "UDT_Name";  // UDT reference
   END_VAR;
BEGIN
   // Start values
END_DATA_BLOCK
```

For FCs:
```scl
FUNCTION "FC_Name" : Void
TITLE = 'Display Name'
VERSION : 0.1
   VAR_INPUT
      ParamName : DataType;
   END_VAR
   VAR_OUTPUT
      ParamName : DataType;
   END_VAR
   VAR_TEMP
      TempVar : DataType;
   END_VAR
BEGIN
END_FUNCTION
```

For FBs:
```scl
FUNCTION_BLOCK "FB_Name"
TITLE = 'Display Name'
VERSION : 0.1
   VAR_INPUT
      ParamName : DataType;
   END_VAR
   VAR_OUTPUT
      ParamName : DataType;
   END_VAR
   VAR
      StaticVar : "UDT_Name";  // Static (retained) data
   END_VAR
BEGIN
END_FUNCTION_BLOCK
```

For OBs:
```scl
ORGANIZATION_BLOCK "OB_Name"
TITLE = 'Display Name'
VERSION : 0.1
   VAR_TEMP
      TempVar : DataType;
   END_VAR
BEGIN
END_ORGANIZATION_BLOCK
```

### User Constants
User Constants are defined as a special DB with `VAR CONSTANT`:
```scl
DATA_BLOCK "DB_UserConstants"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
   VAR CONSTANT
      CONST_NAME : Int := 42;
   END_VAR;
END_DATA_BLOCK
```

### UDT Design Best Practices
- Nest UDTs in DBs: `Alarm : "UDT_Alarm"` instead of flat STRUCT
- Group related fields: Status, Sensor, Diag, Config, etc.
- Use meaningful default values
- Add comments to every field
- Name convention: `UDT_<Function>` (e.g., `UDT_Alarm`, `UDT_Motor_Inst`)

### IO Tags XML Format
```xml
<?xml version="1.0" encoding="utf-8"?>
<Tags>
  <Tag Name="TAG_NAME" DataType="Bool" LogicalAddress="%I0.0" Comment="Description"/>
</Tags>
```

### HMI Tags XML Format
```xml
<?xml version="1.0" encoding="utf-8"?>
<HmiTags>
  <HmiTag Name="HMI_Tag" DataType="Int" Source="DB3.Field" Comment="Description"/>
</HmiTags>
```

### Block Interface (FC/FB) Conventions
- FCs: VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT, VAR_TEMP
- FBs: Same + VAR (static/retained data)
- Always include: TITLE, VERSION (0.1), AUTHOR, FAMILY, NAME, COMMENT
- TON timers go in VAR_TEMP for FCs, VAR for FBs

## Common Pitfalls
1. **Wrong import order**: UDTs MUST be imported before DBs that reference them
2. **SCL syntax errors**: Missing semicolons, wrong quotes, incorrect TYPE/DATA_BLOCK syntax
3. **UDT naming**: Must match exactly between definition and DB reference
4. **Retain setting**: Use `{ S7_Optimized_Access := 'FALSE' }` for non-optimized DBs
5. **Sub-agent timeouts**: Large file generation tasks may timeout sub-agents — generate directly

## Output File Structure
```
io/
├── UDTs.scl              ← User Defined Types
├── DBs.scl               ← Datablokker (UDT-basert)
├── UserConstants.scl     ← Konstanter
├── IO_Tags.xml           ← PLC IO-tags
├── HMI_Tags.xml          ← HMI-tags
├── Tags_Import.xlsx      ← Full tagliste (Excel)
└── tia_xml/              ← Block XML import files (TIA Portal SimaticML)
    ├── FC1_SeqManager.xml    ← FC: Sekvenssteg-velger
    ├── FC3_Skalering.xml     ← FC: 4-20mA til prosent
    ├── FC4_HMI_Kobling.xml   ← FC: PLS→HMI dataoverføring
    ├── FC5_CSV_Logg.xml      ← FC: CSV-logging
    ├── FC6_Tom_Etasje.xml    ← FC: Tømme-funksjon
    ├── FC7_Etasjelogikk.xml  ← FC: Pall-posisjon
    ├── FC_Step0_Init.xml     ← FC: Initialisering
    ├── FC_Step1-11.xml       ← FC: Sekvenssteg 1-11
    ├── FC_AlarmStep.xml      ← FC: Alarm og reset
    ├── FB1_MotorStyring.xml  ← FB: Motorstyring
    ├── FB2_HeisKontroll.xml  ← FB: Heiskontroll
    ├── FB3_Sikkerhet.xml     ← FB: Sikkerhetskrets
    ├── OB1_Main.xml          ← OB: Hovedprogram
    ├── OB100_Startup.xml     ← OB: Oppstart
    └── IMPORT_GUIDE.md       ← Import instruksjoner
```

## TIA Portal SimaticML XML Format (Block Import)

### Critical Distinction: SCL vs XML Import
- **SCL files (.scl)** → Import UDTs, DBs, User Constants (data structures only)
- **XML files (.xml)** → Import program blocks (FC/FB/OB) with interface definitions
- These are TWO DIFFERENT import mechanisms in TIA Portal

### XML Block Import Format

Each block is a separate XML file. The format follows Siemens SimaticML schema:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V19"/>
  <SW.Blocks.FC ID="50">
    <AttributeList>
      <AutoNumber>false</AutoNumber>
      <HeaderFamily>FamilyName</HeaderFamily>
      <Interface>
        <Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
          <Section Name="Input">
            <Member Name="ParamName" Datatype="Bool">
              <Comment>
                <MultiLanguageText Lang="nb-NO">Kommentar</MultiLanguageText>
              </Comment>
            </Member>
          </Section>
          <Section Name="Output"/>
          <Section Name="InOut"/>
          <Section Name="Temp"/>
          <Section Name="Constant"/>
          <Section Name="Return">
            <Member Name="Ret_Val" Datatype="Void"/>
          </Section>
        </Sections>
      </Interface>
      <MemoryLayout>Optimized</MemoryLayout>
      <Name>BlockName</Name>
      <Namespace/>
      <Number>50</Number>
      <ProgrammingLanguage>FBD</ProgrammingLanguage>
      <SetENOAutomatically>false</SetENOAutomatically>
    </AttributeList>
    <ObjectList>
      <MultilingualText ID="501" CompositionName="Comment">
        <ObjectList>
          <MultilingualTextItem ID="502" CompositionName="Items">
            <AttributeList>
              <Culture>nb-NO</Culture>
              <Text>Block comment</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
      <SW.Blocks.CompileUnit ID="503" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource/>
          <ProgrammingLanguage>FBD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <!-- Empty comment and title for CompileUnit -->
        </ObjectList>
      </SW.Blocks.CompileUnit>
      <MultilingualText ID="508" CompositionName="Title">
        <!-- Title text -->
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.FC>
</Document>
```

### Block Type XML Elements
| Block Type | XML Element |
|---|---|
| FC | `<SW.Blocks.FC ID="num">` |
| FB | `<SW.Blocks.FB ID="num">` |
| OB | `<SW.Blocks.OB ID="num">` |

### Key XML Attributes
- `HeaderFamily`: Family number or string
- `Number`: Block number (must be unique)
- `ProgrammingLanguage`: Always "FBD" for our projects
- `MemoryLayout`: "Optimized" 
- `AutoNumber`: "false"
- `SetENOAutomatically`: "false"

### Block Numbers (WAREMOTTAK_LAGER)
| Block | Number |
|---|---|
| FC1_SeqManager | 50 |
| FC3_Skalering | 52 |
| FC4_HMI_Kobling | 53 |
| FC5_CSV_Logg | 54 |
| FC6_Tom_Etasje | 55 |
| FC7_Etasjelogikk | 56 |
| FC_Step0_Init | 60 |
| FC_Step1-11 | 61-71 |
| FC_AlarmStep | 250 |
| FB1_MotorStyring | 100 |
| FB2_HeisKontroll | 101 |
| FB3_Sikkerhet | 102 |
| OB1_Main | 200 |
| OB100_Startup | 201 |

## Excel Tag List Generation

For generating formatted IO_LISTE.xlsx and TAGLISTE.xlsx files with openpyxl, see:
`references/excel_generation.md`

Quick reference:
- IO_LISTE.xlsx: 2 sheets (IO_Innganger, IO_Utganger) — Adresse, Navn, Datatype, Kommentar
- TAGLISTE.xlsx: 4 sheets (Fysiske_IO, Reserverte_IO, HMI_Tags, DB_Elementer)
- HMI_Tags use UDT paths: DB3.Kommando.X, DB3.Status.X, DB2.Alarm.X
- DB_Elementer includes FB instance DBs (DB10/11/12) with UDT types
- Reserved IO rows use gray fill; alternating rows use light blue fill
- Title row includes version and date: "— AUT23 (v4.0 YYYY-MM-DD)"

## TIA Portal SimaticML XML Format for Block Import (CRITICAL)

### The XML File MUST Start Like This — No Exceptions

```
<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V19"/>
  <SW.Blocks.FC ID="50">
```

**Rules:**
- `<?xml ...?>` MUST be on line 1, column 1 — NO BOM, NO whitespace, NO blank lines before it
- NO double `<?xml>` declarations (a common bug when combining ElementTree + minidom)
- NO self-closing `<Member>` tags with `<Comment>` sub-elements inside — Members are ALWAYS self-closing: `<Member Name="..." Datatype="..."/>`
- NO `<Return>` section — it does not exist in TIA Portal XML import format
- NO `<MemoryReserve>` in OB files
- NO `<HeaderFamily>` in FB or OB files (FC only)
- OB files MUST have `<SecondaryType>` — `ProgramCycle` for OB1, `Startup` for OB100
- Empty sections are self-closing: `<Section Name="Input"/>`, `<Section Name="Temp"/>`, `<Namespace/>`, `<NetworkSource/>`
- NO pretty-printing inside `<Interface>` — Sections should be on separate lines but Members should NOT have closing `</Member>` tags

### Correct FB Block Format (verified working)
```xml
<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V19"/>
  <SW.Blocks.FB ID="100">
    <AttributeList>
      <AutoNumber>false</AutoNumber>
      <Interface>
        <Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
          <Section Name="Input">
            <Member Name="Start" Datatype="Bool"/>
          </Section>
          <Section Name="Output">
            <Member Name="Kontaktor" Datatype="Bool"/>
          </Section>
          <Section Name="InOut"/>
          <Section Name="Static"/>
          <Section Name="Temp"/>
          <Section Name="Constant"/>
        </Sections>
      </Interface>
      <MemoryLayout>Optimized</MemoryLayout>
      <Name>FB1_MotorStyring</Name>
      <Namespace/>
      <Number>100</Number>
      <ProgrammingLanguage>FBD</ProgrammingLanguage>
      <SetENOAutomatically>false</SetENOAutomatically>
    </AttributeList>
    <ObjectList>
      <MultilingualText ID="1001" CompositionName="Comment">
        <ObjectList>
          <MultilingualTextItem ID="1002" CompositionName="Items">
            <AttributeList>
              <Culture>nb-NO</Culture>
              <Text>Comment text</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
      <SW.Blocks.CompileUnit ID="1003" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource/>
          <ProgrammingLanguage>FBD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="1004" CompositionName="Comment">
            <ObjectList>
              <MultilingualTextItem ID="1005" CompositionName="Items">
                <AttributeList>
                  <Culture>nb-NO</Culture>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
          <MultilingualText ID="1006" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="1007" CompositionName="Items">
                <AttributeList>
                  <Culture>nb-NO</Culture>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>
      <MultilingualText ID="1008" CompositionName="Title">
        <ObjectList>
          <MultilingualTextItem ID="1009" CompositionName="Items">
            <AttributeList>
              <Culture>nb-NO</Culture>
              <Text>Title text</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.FB>
</Document>
```

### Critical Differences by Block Type

| Element | FC | FB | OB |
|---|---|---|---|
| HeaderFamily | ✅ | ❌ | ❌ |
| Static section | ❌ | ✅ | ❌ |
| SecondaryType | ❌ | ❌ | ✅ |
| MemoryReserve | ❌ (not in example) | ✅ (100) | ❌ |
| Return section | ❌ | ❌ | ❌ |
| MemoryLayout | Optimized | Optimized | Optimized |

**IMPORTANT**: The skill's earlier XML examples showed MemoryReserve for FC — this was INCORRECT. Only FB has MemoryReserve. FC has NO MemoryReserve and NO Return section. The user's example files (FB1_MotorStyring.xml, Main.xml, Startup.xml) are the authoritative reference.

### Common XML Import Errors

| Error | Cause | Fix |
|---|---|---|
| "XML declaration must be first node" | BOM, blank lines, or double `<?xml>` | Write file with `open(path, "w", encoding="utf-8")`, prepend `<?xml...?>` manually, skip minidom output's own declaration |
| "Invalid child element" | `<Comment>` inside `<Member>` | Members are self-closing ONLY — no sub-elements |
| "Missing required element" | `<Return>` section present | Remove entire `<Return>` section — not used in import XML |
| "Invalid section name" | Wrong section for block type | FC: Input/Output/InOut/Temp/Constant. FB: +Static. OB: Input/Output/InOut/Temp only |
| Pretty-print breaks import | minidom adds whitespace/declaration | Generate XML manually as string, or strip minidom output |

### Generating XML Files Programmatically

When generating XML via Python ElementTree:
1. Build tree with `ET.Element()` / `ET.SubElement()`
2. Use `ET.tostring(root, encoding="unicode", xml_declaration=False)` — NO declaration
3. Strip any `<?xml...?>` from the string output
4. Prepend your own `<?xml version="1.0" encoding="utf-8"?>\n`
5. Write with `open(path, "w", encoding="utf-8")` — NO utf-8-sig (that adds BOM)
6. Do NOT use minidom pretty-print if it adds its own `<?xml>` declaration
7. Use `\r\n` (CRLF) line endings — TIA Portal expects Windows line endings

**File list:** `io/tia_xml/` contains 24 pre-generated XML files (19 FC + 3 FB + 2 OB) ready for import.

### Import Steps
1. Right-click "Program blocks" → "Import block"
2. Select XML file
3. Confirm import
4. Repeat for all files
5. Add program code manually in FBD/LAD
6. Compile
