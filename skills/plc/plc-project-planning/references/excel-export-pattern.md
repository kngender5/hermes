# Excel Export Pattern for PLC Project Data

## When to Use

When the user asks to convert PLC project data (IO lists, tag lists, DB structures) to Excel format. This is a recurring request — always produce `.xlsx` alongside `.txt` files.

## Pattern

Use `openpyxl` with this structure:

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# Styles
hdr_font = Font(bold=True, color="FFFFFF", size=11)
hdr_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
alt_fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
resv_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
retain_ja = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
retain_nei = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
thin = Side(style="thin", color="BFBFBF")
bdr = Border(left=thin, right=thin, top=thin, bottom=thin)
```

## Recommended Sheets

### PLC Projects: TAGLISTE.xlsx
1. **Fysiske_IO** — DI, DO, AI, AO with tag-ID (DI_01, DO_01, etc.)
2. **Reserverte_IO** — Reserved DI/DO with plausible future use
3. **HMI_Tags** — All WinCC tags with DB source paths
4. **DB_Elementer** — All DB variables: name, type, start value, retain status
   - Retain=JA → green fill, Retain=NEI → yellow fill

### IO_LISTE.xlsx
1. **IO_Innganger** — DI + AI + Reserved DI
2. **IO_Utganger** — DO + AO + Reserved DO + Analog AO

## Color Coding
- Header row: dark blue (#1F4E79) with white text
- Alternating rows: light blue (#D6E4F0)
- Reserved IO: gray (#F2F2F2)
- Retain=JA: green (#E2EFDA) with dark green text (#375623)
- Retain=NEI: yellow (#FFF2CC) with dark yellow text (#7F6000)
- Section dividers: dark gray (#595959) with white text

## Column Widths (typical)
- Tag-ID: 9, Address: 12, Datatype: 10, Navn/Source: 28, Kommentar: 45-55
- DB name: 28, Element name: 30, Startverdi: 12, Retain: 8

## Freeze Panes
Always freeze row 3 (first data row after header):
```python
ws.freeze_panes = ws.cell(row=3, column=1)
```

## Output Location
Save to: `prosjektoppgave/io/FILNAVN.xlsx`
