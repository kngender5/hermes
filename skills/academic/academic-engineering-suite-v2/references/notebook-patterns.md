# Jupyter Notebook Creation and Repair Patterns (2026-05-25)

## Cell Corruption Detection and Fix

### Symptom
Cells have hundreds/thousands of lines, each containing a single character.
This happens when content is written character-by-character instead of line-by-line.

### Detection Script
```python
import json

def check_nb_cells(path):
    with open(path) as f:
        nb = json.load(f)
    issues = []
    for i, cell in enumerate(nb['cells']):
        src = cell.get('source', [])
        if len(src) > 100 and all(len(l.strip()) <= 1 for l in src if l.strip()):
            issues.append((i, len(src), cell['cell_type']))
    return issues

# Usage
corrupted = check_nb_cells('notebook.ipynb')
for cell_idx, n_lines, ctype in corrupted:
    print(f"Cell {cell_idx} ({ctype}): {n_lines} garbled lines")
```

### Fix Pattern
Rewrite corrupted cells with proper line strings:
```python
# GOOD — each element is a complete line
cell['source'] = [
    "# Title\n",
    "\n",
    "Description text here.\n",
]

# BAD — each character becomes a separate element
cell['source'] = ['#', ' ', 'T', 'i', 't', 'l', 'e', '\n', ...]
```

### Prevention
When building notebooks programmatically:
- Always construct `source` as a list of complete line strings
- Each line should end with `\n`
- Use `json.dump(nb, f, indent=1)` — never manually serialize cell content
- After writing, run the detection script to verify

## Notebook Structure for EKOM Exam Notes

The EKOM notebook (`EKOM_Eksamensnotater_v2.ipynb`) follows this pattern:
- Cell 0: Markdown title + metadata
- Cell 1: Markdown section header
- Cell 2: Code setup (imports)
- Then alternating: markdown section header → code widget → markdown → code...
- `@interact` decorators for ipywidgets interactive calculators
- `FloatSlider`, `IntSlider`, `Dropdown` for parameter input
- Each interactive cell is self-contained (imports at top of notebook)

## ipywidgets Pattern for Calculators

```python
from ipywidgets import interact, FloatSlider, IntSlider, Dropdown, Layout

s = {'description_width': '200px'}
LW = Layout(width='500px')

@interact(
    param1=FloatSlider(min=0, max=100, value=50, step=1, description="Param 1", style=s, layout=LW),
    param2=Dropdown(options=['A', 'B'], value='A', description="Param 2"),
)
def my_calculator(param1, param2):
    result = param1 * 2  # your formula
    print(f"Result: {result}")
```
