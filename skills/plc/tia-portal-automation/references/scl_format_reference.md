# SCL Import Format Reference

## UDT Definition Pattern
```scl
TYPE "UDT_Alarm"
TITLE = 'Alarm-status'
VERSION : 0.1
   STRUCT
      Safety_OK : Bool := 1;
      AlarmActive : Bool;
   END_STRUCT;
END_TYPE
```

## Global DB with UDT Reference
```scl
DATA_BLOCK "DB2_Alarmregister"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
   VAR
      Alarm : "UDT_Alarm";
   END_VAR;
BEGIN
   Alarm.Safety_OK := 1;
END_DATA_BLOCK
```

## User Constants DB
```scl
DATA_BLOCK "DB_UserConstants"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
   VAR CONSTANT
      STEP_INIT : Int := 0;
      STEP_ALARM : Int := 99;
   END_VAR;
END_DATA_BLOCK
```

## IO Tags XML Format
```xml
<?xml version="1.0" encoding="utf-8"?>
<Tags>
  <Tag Name="START_KNAPP" DataType="Bool" LogicalAddress="%I0.0" Comment="Start-knapp"/>
  <Tag Name="LYSGITTER_HOYDE" DataType="Int" LogicalAddress="%IW64" Comment="Lysgitter hoyde"/>
</Tags>
```

## HMI Tags Excel Format
| Name | Path | Data Type | Logical Address | Comment | Hmi Visible | Hmi Accessible | Hmi Writeable | Typeobject ID | Version ID |

Sheets: IO_Innganger, IO_Utganger, HMI_Tags, Alle_Tags, DB_Structures

## Import Order
1. UDTs.scl → PLC data types
2. DBs.scl → Program blocks
3. DB_UserConstants.scl → Program blocks
4. IO_Tags.xml → PLC tags
5. HMI_Tags.xml → HMI tags
6. FC/FB/OB *.scl → Program blocks