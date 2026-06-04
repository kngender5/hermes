---
name: excel-generation
description: Generate Excel (.xlsx) spreadsheets from data — convert CSV/XML/JSON to formatted workbooks, side-by-side version comparisons, diff reports, and styled tables using openpyxl. Use when the user asks to create, convert, or generate Excel files from any data source, or when producing reports/dashboards as .xlsx.
triggers:
  - "excel"
  - "xlsx"
  - "spreadsheet"
  - "excel file"
  - "convert to excel"
  - "generate excel"
  - "excel report"
  - "excel ark"
  - "regneark"
metadata:
  version: "1.0"
  author: "OWL"
---

# Excel Generation

Generate formatted `.xlsx` workbooks from data sources (CSV, XML, JSON, Python structures) using `openpyxl`.

## Key Rules

1. **Write the Python script to a temp file, then execute it.** Never try to inline complex openpyxl code in `execute_code` — write to `~/.tmp/gen_xlsx.py`, then `python3 ~/.tmp/gen_xlsx.py`.
2. **Verify the output.** After saving, load the workbook back and print sheet names + dimensions to confirm.
3. **Clean up** temp scripts after successful generation (`rm ~/.tmp/gen_xlsx.py`).

## Workflow

### 1. Parse the source data

Identify file types:
- **CSV** — Use `csv.reader` with `delimiter=";"` for Norwegian files, `utf-8-sig` encoding
- **XML** — Use `xml.etree.ElementTree` with `.parse()` and `.iter()`; check both attributes (`tag.get()`) and child elements (`tag.find()`) since formats vary
- **JSON** — Use `json.load()`, handle both list-of-dicts and nested structures

### 2. Plan the workbook structure

- **Side-by-side comparisons**: V1 columns | narrow separator column | V2 columns. 2 header rows (title group + column headers).
- **Diff sheets**: 3 sections (deleted/added/changed) with color coding: red=`FCE4D6`, green=`E8F0D6`, yellow=`FFF2CC`
- **Single data source**: Group by logical category, alternate row colors per group, merge category headers vertically

### 3. Build with openpyxl

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Standard border
thin = Side(style="thin", color="AAAAAA")
BDR = Border(left=thin, right=thin, top=thin, bottom=thin)

# Header fills
BLUE_DARK  = PatternFill("solid", fgColor="1F4E79")  # title row
BLUE_MED   = PatternFill("solid", fgColor="2E75B6")  # column headers / section headers
ALT1       = PatternFill("solid", fgColor="EBF3FB")  # alternating row color
ALT2       = PatternFill("solid", fgColor="FFFFFF")  # alternating row color
GRAY_SEP   = PatternFill("solid", fgColor="CCCCCC")  # V1|V2 separator column

# Standard functions
def h1(ws, r, cols, txt, fill=BLUE_DARK):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=cols)
    c = ws.cell(r, 1, txt)
    c.font = Font(name="Calibri", bold=True, size=12 if fill==BLUE_DARK else 10, color="FFFFFF")
    c.fill = fill
    c.alignment = Alignment(horizontal="center", vertical="center")

def hdrs(ws, r, labels, fill=BLUE_MED):
    for i, lbl in enumerate(labels, 1):
        c = ws.cell(r, i, lbl)
        c.font = Font(name="Calibri", bold=True, size=9, color="FFFFFF")
        c.fill = fill
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BDR

def row_fill(ws, r, vals, fill, ncols):
    for i, v in enumerate(vals, 1):
        c = ws.cell(r, i, v)
        c.font = Font(name="Calibri", size=10)
        c.fill = fill
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = BDR
    for i in range(len(vals)+1, ncols+1):
        c = ws.cell(r, i, "")
        c.border = BDR
        c.fill = fill

def set_widths(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
```

### 4. Common patterns

**Side-by-side V1/V2 with separator:**
```
NCOLS = len(v1_headers) + 1 + len(v2_headers)
# Row layout: [V1 cols...] [sep] [V2 cols...]
# Separator cell: fill=GRAY_SEP, width=2-3
ws.freeze_panes = "A4"  # freeze below title+headers
```

**Merged group headers (vertically):**
```python
if n_rows_in_group > 1:
    ws.merge_cells(start_row=row, start_column=group_col, end_row=row+n-1, end_column=group_col)
c = ws.cell(row, group_col, label)
c.alignment = Alignment(vertical="center", horizontal="center")
```

**Landscape print setup:**
```python
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1
```

### 5. Pitfalls

- **Sheet titles**: Cannot contain `/`, `\`, `?`, `*`, `[`, `]`, `:`. Strip or replace (e.g., `"I/O-liste"` -> `"IO-liste"`).
- **File paths in WSL**: Use absolute paths. Windows files are under `/mnt/c/Users/<user>/`.
- **XML encoding**: Some TIA Portal exports use `utf-8-sig` (BOM). Open with `encoding="utf-8-sig"` if parsing fails, but ElementTree handles BOM automatically.
- **CSV with semicolons**: Norwegian locale CSVs use `;` not `,`. Specify `delimiter=";"` in `csv.reader`.
- **`write_file` creates copies**: If you write a `.py` file via `write_file` and then try to delete it in the same session, the system may have already backed it up. Use `rm -f` with the absolute path.
- **`execute_code` heredoc issue**: Complex Python with special chars can break heredocs. Always write the script to a file first and `python3` it separately.

### 6. Verification

After saving, always verify:
```python
wb2 = openpyxl.load_workbook(out_path)
for s in wb2.worksheets:
    print(f"{s.title}: {s.max_row} rows x {s.max_column} cols")
wb2.close()
```

## Support Files

- `scripts/csv_to_xlsx.py` — Convert any CSV to formatted xlsx with auto-detected delimiter
- `scripts/xml_to_xlsx.py` — Generic XML tag-to-rows converter
