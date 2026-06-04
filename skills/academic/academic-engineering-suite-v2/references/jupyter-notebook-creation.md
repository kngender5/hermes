# Jupyter Notebook Creation for EKOM Exam Prep

## Pattern: Programmatic Notebook Generation

When creating Jupyter notebooks with many interactive widgets, build them programmatically via Python's `json` module rather than writing JSON directly. This avoids escaping nightmares with f-strings, triple quotes, and LaTeX in widget descriptions.

### Core Technique

```python
import json, textwrap

def make_cells():
    cells = []
    def md(s):
        return {"cell_type": "markdown", "metadata": {}, "source": textwrap.dedent(s).strip()}
    def code(s):
        return {"cell_type": "code", "metadata": {}, "source": textwrap.dedent(s).strip(),
                "execution_count": None, "outputs": []}
    # ... build cells list ...
    return cells

nb = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3.14.4"}},
    "cells": make_cells()
}
with open("output.ipynb", "w") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
```

### Key Pitfalls

1. **Never use triple-quoted strings inside execute_code for notebook generation** — the sandbox's Python parser chokes on nested quotes. Use `textwrap.dedent()` with regular strings instead.

2. **Widget descriptions with special characters** — keep descriptions simple, avoid nested quotes.

3. **Source field format** — Jupyter nbformat 4.5 expects `source` as a **string**, not a list.

4. **Validation** — always validate after writing with `json.load()` + `ast.parse()` for each code cell.

5. **Norwegian characters** (æ, ø, å) work fine with `ensure_ascii=False`.

### Widget Patterns That Work

- `@interact` decorator for simple sliders/dropdowns
- `interactive_output` for more complex layouts
- `Layout(width='450px')` for consistent widget sizing
- `style={'description_width': '150px'}` for aligned labels
- `Checkbox()` for boolean options
- `Text(value="1.5, 3.0")` for comma-separated numeric input

## Server Management

```bash
jupyter server list          # Show running servers
jupyter server stop 8888     # Stop server
jupyter server list 2>&1 | grep -oP 'token=[a-f0-9]+'  # Get token
```

Note: Jupyter assigns a new port if the requested one is in use. Always check `jupyter server list` for the actual URL and token.
