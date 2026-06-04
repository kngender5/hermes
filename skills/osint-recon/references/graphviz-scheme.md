# Graphviz DOT — OSINT Relationship Graphs

## Color Schema

Use this standardized color scheme for all OSINT relationship graphs:

```
digraph G {
    // Color scheme
    node [style="filled,rounded", fontname="Helvetica", fontsize=11];
    
    // Red — critical vulnerabilities / exposed data
    "leaked_email@example.com" [fillcolor="#ff6b6b", fontcolor="white", shape=box];
    "192.168.1.1" [fillcolor="#ff6b6b", fontcolor="white", shape=octagon];
    "/home/user/secret_key" [fillcolor="#ff6b6b", fontcolor="white", shape=note];
    
    // Yellow — provisional / unconfirmed profiles
    "@suspicious_handle" [fillcolor="#ffd93d", fontcolor="black", shape=ellipse];
    "possible_alias" [fillcolor="#ffd93d", fontcolor="black", shape=ellipse];
    
    // Green — confirmed / validated identifiers
    "@confirmed_handle" [fillcolor="#6bcb77", fontcolor="white", shape=ellipse];
    "John Doe" [fillcolor="#6bcb77", fontcolor="white", shape=box];
    "user@company.com" [fillcolor="#6bcb77", fontcolor="white", shape=box];
    
    // Blue — third-party / CDN / infrastructure
    "142.250.80.14" [fillcolor="#4d96ff", fontcolor="white", shape=octagon];
    "cloudflare.com" [fillcolor="#4d96ff", fontcolor="white", shape=hexagon];
    "+4712345678" [fillcolor="#4d96ff", fontcolor="white", shape=diamond];
    
    // Edges with source labels
    "@confirmed_handle" -> "user@company.com" [label="via holehe", fontsize=9];
    "user@company.com" -> "example.com" [label="MX record", fontsize=9, style=dashed];
    "@confirmed_handle" -> "+4712345678" [label="via ignorant", fontsize=9];
    "example.com" -> "142.250.80.14" [label="A record", fontsize=9];
    
    // Graph metadata
    labelloc="t";
    label="OSINT Dossier: [TARGET_NAME]\nGenerated: [DATE]";
    rankdir="LR";
    splines="ortho";
}
```

## Node Shapes

| Shape | Meaning |
|-------|---------|
| `ellipse` | Username / handle |
| `box` | Name, email, text identifier |
| `octagon` | IP address, server |
| `diamond` | Phone number |
| `hexagon` | Domain, CDN, infrastructure |
| `note` | System path, file, exposure |
| `folder` | Directory, database |
| `component` | Service, API endpoint |

## Edge Styles

| Style | Meaning |
|-------|---------|
| `solid` | Confirmed / validated link |
| `dashed` | Inferred / probable link |
| `dotted` | Historical / archived link |
| `bold` | Direct / primary connection |

## Export Commands

```bash
# Install graphviz if needed
sudo apt-get install -y graphviz

# PNG (for sharing)
dot -Tpng ./artifacts/TARGET.dot -o ./artifacts/TARGET.png

# SVG (for web / scaling)
dot -Tsvg ./artifacts/TARGET.dot -o ./artifacts/TARGET.svg

# PDF (for reports)
dot -Tpdf ./artifacts/TARGET.dot -o ./artifacts/TARGET.pdf

# DOT with embedded image (for tools that support it)
dot -Tsvg -o output.svg input.dot && inkscape output.svg --export-pdf=output.pdf
```

## Full Workflow

1. Collect all indicators from previous phases
2. Assign colors by confidence (red=critical, yellow=unconfirmed, green=confirmed, blue=infra)
3. Write DOT file to `./artifacts/TARGET.dot`
4. Render to PNG + SVG
5. Include both in final dossier report
