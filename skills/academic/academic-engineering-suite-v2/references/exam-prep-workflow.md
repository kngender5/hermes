# EXAM-PREP: Expanded Workflow (2026-05-25)

## Jupyter Notebook Creation for Interactive Exam Prep

When the user asks for interactive tools, calculators, or system design tools, create a Jupyter notebook with ipywidgets. This is preferred over static scripts for exam prep because students can experiment with parameters interactively.

### Workflow

1. **Plan sections** — identify all calculators, reference tables, and interactive tools needed
2. **Build programmatically** — use Python `json` module to generate the notebook (see `references/jupyter-notebook-creation.md`)
3. **Structure**: Setup cell → numbered sections with markdown headers → code cells with `@interact` widgets
4. **Validate** — `json.load()` + `ast.parse()` for each code cell
5. **Start server** — `jupyter notebook FILE.ipynb --no-browser --port=8888 &`
6. **Deliver** — provide URL + token

### Notebook Sections for EKOM (v2 reference)

The v2 notebook has 55 cells / 21 sections covering:
- Physical layer: frequency/wavelength, dB calculations, SNR/Shannon
- Fiber optics: budget calculator, splitter loss, PON capacity, OTDR simulator
- System types: GPON, XG-PON, WDM-PON, HFC, DOCSIS, PoE
- Design tools: end-to-end link designer, project planner (BOM/cost/Gantt)
- Reference: NEK standards, connector types, cable types, SFP matching
- Assessment: exam quiz, HMS checklist

### Key Design Principles

- **Every calculator gets a visualization** — bar charts for budgets, gauge plots for pass/fail, frequency spectrum plots
- **Reference tables are interactive** — use Dropdown selectors to show relevant info
- **Include worked examples** — show a complete calculation with realistic values
- **Norwegian language** — all labels, descriptions, and output in Norwegian
- **Metric units** — dB, dBm, km, MHz, GHz, Gbit/s, NOK

### Common Pitfalls

- Triple-quoted strings in `execute_code` → use `textwrap.dedent()` instead
- Widget descriptions with special characters → keep simple
- Large notebooks → split into focused sections, each with clear markdown headers
- Server port conflicts → check `jupyter server list` after starting
