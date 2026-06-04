# Ground Truth Extract JSON Schema

## Per-File Extract Format

Each source file produces one JSON file in `workspace_groundtruth/extracts/`:

```json
{
  "source_file": "2025 EKOM - Del 1.pdf",
  "source_type": "pdf",
  "extracted_at": "2026-05-25T12:00:00",
  "topics": [
    {
      "title": "Fiberoptisk budsjett",
      "level": 1,
      "subtopics": [
        {"title": "Singlemode vs multimode", "level": 2},
        {"title": "GPON arkitektur", "level": 2}
      ]
    }
  ],
  "formulas": [
    {
      "name": "Fiberbudsjett",
      "latex": "P_{rx} = P_{tx} - L_{tot}",
      "variables": ["P_tx", "P_rx", "L_tot"],
      "source_page": 12
    }
  ],
  "tables": [
    {
      "title": "Splitterdempning",
      "headers": ["Forhold", "Tap (dB)"],
      "rows": [["1:2", "3.0"], ["1:4", "6.0"]],
      "source_page": 15
    }
  ],
  "definitions": [
    {
      "term": "dempning",
      "definition": "Reduksjon av signalstyrke over en transmisjonslinje",
      "english": "attenuation",
      "source_page": 3
    }
  ],
  "standards_referenced": ["NEK 701", "ITU-T G.984", "G.652.D"],
  "numerical_values": [
    {"parameter": "SM 1310nm demping", "value": 0.35, "unit": "dB/km", "page": 8},
    {"parameter": "GPON B+ TX min", "value": 1.5, "unit": "dBm", "page": 22}
  ],
  "exam_tips": [
    "Alltid inkluder systemmargin i fiberbudsjett",
    "Husk at 1550nm har lavere demping enn 1310nm"
  ],
  "verification_status": {
    "P_tx_range": "VERIFIED_SOURCE",
    "splitter_loss": "VERIFIED_SOURCE",
    "custom_claim": "PROVISIONAL"
  }
}
```

## Inventory JSON Format

`workspace_groundtruth/inventory.json`:

```json
{
  "last_scan": "2026-05-25T12:00:00",
  "files": [
    {
      "path": "curriculum/AUT23_-_Ekom/fagstoff_files/2025 EKOM - Del 1.pdf",
      "type": "pdf",
      "size_bytes": 123456,
      "status": "extracted",
      "extract_file": "extracts/ekom_del1.json",
      "last_processed": "2026-05-25T12:00:00"
    },
    {
      "path": "curriculum/AUT23_-_Ekom/panopto_recordings/WEB_12_februar_2026.srt",
      "type": "srt",
      "size_bytes": 45678,
      "status": "extracted",
      "extract_file": "extracts/web_12_feb.json",
      "last_processed": "2026-05-25T12:00:00"
    }
  ],
  "statistics": {
    "total_files": 20,
    "unprocessed": 3,
    "extracted": 15,
    "verified": 12,
    "consolidated": 10
  }
}
```

## Status Values

| Status | Meaning |
|--------|---------|
| `unprocessed` | Discovered but not yet read |
| `in-progress` | Currently being extracted |
| `extracted` | Knowledge extracted to JSON |
| `verified` | Claims verified against sources |
| `consolidated` | Merged into unified notes |
| `gap` | Identified as missing from notes |
