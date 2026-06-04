# Excel Tag List Generation with openpyxl

## Pattern for Formatted Excel Files

Use this pattern when generating IO lists, tag lists, or DB element lists for PLC projects.

### Basic Setup

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Styles
hdr_font = Font(bold=True, color="FFFFFF", size=10)
hdr_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
alt_fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
resv_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
thin = Side(style="thin", color="CCCCCC")
bdr = Border(left=thin, right=thin, top=thin, bottom=thin)
center = Alignment(horizontal="center", vertical="center")

def setup_sheet(ws, title, cols, widths):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(cols))
    c = ws.cell(row=1, column=1, value=title)
    c.font = Font(bold=True, size=13, color="2F5496")
    c.alignment = Alignment(horizontal="center")
    for i, (col, w) in enumerate(zip(cols, widths), 1):
        c = ws.cell(row=2, column=i, value=col)
        c.font = hdr_font; c.fill = hdr_fill
        c.alignment = center; c.border = bdr
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=3, column=1)
    return 3

def add_row(ws, row, data, is_alt=False, is_resv=False):
    for ci, val in enumerate(data, 1):
        c = ws.cell(row=row, column=ci, value=val); c.border = bdr
        if is_resv: c.fill = resv_fill
        elif is_alt: c.fill = alt_fill
```

### Sheet Structure

IO_LISTE.xlsx sheets:
- IO_Innganger: Adresse, Navn, Datatype, Kommentar
- IO_Utganger: Adresse, Navn, Datatype, Kommentar

TAGLISTE.xlsx sheets:
- Fysiske_IO: Tag-ID, Adresse, Datatype, Navn, Kommentar
- Reserverte_IO: Tag-ID, Adresse, Datatype, Navn, Kommentar (gray fill)
- HMI_Tags: HMI_Tag, DB_Kilde, Datatype, Kommentar (UDT paths like DB3.Kommando.X)
- DB_Elementer: DB, Elementnavn, Datatype, Startverdi, Kommentar, Retain

### DB Naming Convention
- DB1_Telleregister (RETAIN), DB2_Alarmregister, DB3_HMI_Tags, DB4_Konfigurasjon (RETAIN)
- DB5_Etasje_Pos (RETAIN), DB10_FB1_Motor_Inst (RETAIN), DB11_FB2_Heis_Inst (RETAIN), DB12_FB3_Sikkerhet_Inst

### Title Format
Include version and date in merged title row: "— AUT23 (v4.0 YYYY-MM-DD)"
