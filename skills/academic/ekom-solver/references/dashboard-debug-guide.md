# Dashboard Debug Guide — ekom-dashboard.html

## Tab Switching Failure (FIXED 2026-05-26)

**Symptom:** Clicking tabs (Referanse, Formler, Kalkulatorer) makes all content disappear.
Nothing shows after tab switch.

**Root Cause:** ID mismatch between `data-tab` attributes and tab-content `id` attributes.
- Tab buttons: `data-tab="ref-splitter"` 
- Tab content divs: `id="ref-splitter"` (missing `tab-` prefix)
- JS handler (line 295): `document.getElementById('tab-'+targetId)` → finds nothing
- Result: all tab-content gets `classList.remove('active')`, nothing gets `classList.add('active')`

**Fix Pattern:**
```
# Calc tabs (special handler via switchCalcTab):
  data-tab="fiber"  →  id="calc-fiber"

# All other tabs (generic handler):
  data-tab="ref-splitter"  →  id="tab-ref-splitter"
  data-tab="f-form"       →  id="tab-f-form"
```

**Also update JS data initialization:**
```javascript
// refData keys must be prefixed with 'tab-' when looking up elements:
Object.entries(refData).forEach(([id,h])=>{
  const e=document.getElementById('tab-'+id);  // NOT getElementById(id)
  if(e) e.innerHTML=h
});
```

**Rule:** When adding new tabs to `ekom-dashboard.html`:
1. Calc tabs: `id="calc-{data-tab}"` + HTML via `document.getElementById('calc-{id}').innerHTML`
2. Other tabs: `id="tab-{data-tab}"` + data init via `getElementById('tab-'+key)`
