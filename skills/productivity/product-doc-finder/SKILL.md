---
name: product-doc-finder
description: Search and collect datasheets, user manuals, technical documentation, guides, operator handbooks, and specifications for any product. Aggregates from ManualsLib, manufacturer sites, GitHub, datasheet archives, and technical databases.
---

# Product Doc Finder — Manuals, Datasheets, Technical Documentation

Search, find, and aggregate product documentation from multiple sources.

## Document Types

| Type | Description | Typical Sources |
|------|-------------|-----------------|
| **Datasheet** | Electrical/mechanical specs, pinouts, characteristics | Manufacturer, Datasheet archives |
| **User Manual** | Operation instructions, safety, setup | ManualsLib, manufacturer support |
| **Technical Reference** | Protocol, API, command reference | GitHub, manufacturer docs |
| **Operator Handbook** | Day-to-day operation, procedures | ManualsLib, industry databases |
| **Service Manual** | Repair, maintenance, troubleshooting | ManualsLib, eBay (rare) |
| **Installation Guide** | Physical mounting, wiring, commissioning | Manufacturer |
| **Programming Guide** | Configuration, scripting, customization | GitHub, manufacturer |
| **Safety Data Sheet (SDS/MSDS)** | Chemical safety, handling, disposal | Manufacturer, regulatory |
| **CAD/Mechanical Drawing** | Dimensions, STEP files, 2D drawings | Manufacturer, GrabCAD |
| **Firmware/Software** | Binaries, source code, update tools | GitHub, manufacturer |

## Search Strategy

### Step 1: Identify Product
```
User provides: product name, model number, manufacturer
Normalize: strip whitespace, standardize model format
```

### Step 2: Search Multiple Sources (in parallel)

```python
import requests
from urllib.parse import quote_plus
import json

class ProductDocFinder:
    """Search and collect product documentation from multiple sources."""
    
    def __init__(self, product_name, model_number="", manufacturer=""):
        self.product_name = product_name
        self.model_number = model_number
        self.manufacturer = manufacturer
        self.query = f"{manufacturer} {product_name} {model_number}".strip()
        self.results = []
    
    def search_all(self):
        """Search all sources and aggregate results."""
        sources = [
            self.search_manualslib,
            self.search_github,
            self.search_manufacturer,
            self.search_datasheet_catalog,
            self.search_google_scholar,
        ]
        for source_fn in sources:
            try:
                docs = source_fn()
                self.results.extend(docs)
            except Exception as e:
                print(f"Source {source_fn.__name__} failed: {e}")
        return self.deduplicate()
    
    def _web_search(self, site, doc_type=""):
        """Search with site restriction."""
        query = f"site:{site} {self.query} {doc_type}"
        return query
    
    def search_manualslib(self):
        """Search ManualsLib.com — largest free manual archive (7M+ manuals)."""
        # URL format: https://www.manualslib.com/products/{Product-Name}.html
        # Or search: https://www.manualslib.com/search.html?text={query}
        name_slug = self.product_name.replace(" ", "-").lower()
        model_slug = self.model_number.replace(" ", "-").lower() if self.model_number else ""
        
        urls = [
            f"https://www.manualslib.com/products/{name_slug}.html",
            f"https://www.manualslib.com/products/{name_slug}-{model_slug}.html",
            f"https://www.manualslib.com/search.html?text={quote_plus(self.query)}",
        ]
        
        results = []
        for url in urls:
            results.append({
                "source": "ManualsLib",
                "url": url,
                "type": "manual",
                "priority": 1,
            })
        return results
    
    def search_github(self):
        """Search GitHub for documentation repos, source code, configs."""
        queries = [
            f"github.com/search?q={quote_plus(self.query + ' documentation')}",
            f"github.com/search?q={quote_plus(self.query + ' manual')}",
            f"github.com/search?q={quote_plus(self.query + ' datasheet')}",
        ]
        return [{"source": "GitHub", "url": q, "type": "technical"} for q in queries]
    
    def search_manufacturer(self):
        """Generate manufacturer support page URLs."""
        domains = {
            "siemens": "https://support.industry.siemens.com/cs/search?search={query}&type=Manual",
            "abb": "https://library.abb.com/r/searchengine/search?query={query}",
            "schneider": "https://www.se.com/ww/en/search/?q={query}",
            "omron": "https://www.omron.com/global/en/search/?q={query}",
            "festo": "https://www.festo.com/net/en-us_us/SupportPortal/default.aspx?q={query}",
            "phoenix": "https://www.phoenixcontact.com/en-pc/search?q={query}",
            "molex": "https://www.molex.com/molex/search/partSearch?query={query}",
            "texas_instruments": "https://www.ti.com/tool/{query}",
            "microchip": "https://www.microchip.com/en-us/search?search={query}",
            "st": "https://www.st.com/en/search.html#{query}",
            "nordic": "https://www.nordicsemi.com/Products/{query}",
            "espressif": "https://www.espressif.com/en/support/documents/technical-documents",
            "raspberry_pi": "https://www.raspberrypi.com/documentation/",
            "arduino": "https://docs.arduino.cc/",
            "hp": "https://support.hp.com/us-en/document/",
            "dell": "https://www.dell.com/support/home/en-us/product-support/",
            "lenovo": "https://pcsupport.lenovo.com/us/en/products/",
            "cisco": "https://www.cisco.com/c/en/us/support/",
            "juniper": "https://www.juniper.net/documentation/",
            "rockwell": "https://literature.rockwellautomation.com/",
            "bosch": "https://www.bosch-home.com/us/support/",
            "milwaukee": "https://www.milwaukeetool.com/support/",
            "snapmaker": "https://snapmaker.zendesk.com/hc/en-us",
            "prusa": "https://help.prusa3d.com/",
            "creality": "https://www.creality.com/pages/download",
            "bambulab": "https://bambulab.com/en/download",
        }
        
        results = []
        mfr_lower = self.manufacturer.lower().replace(" ", "_")
        if mfr_lower in domains:
            url = domains[mfr_lower].format(query=quote_plus(self.query))
            results.append({"source": f"Manufacturer ({self.manufacturer})", "url": url, "type": "all"})
        return results
    
    def search_datasheet_catalog(self):
        """Search datasheet aggregation sites."""
        sources = [
            f"https://www.alldatasheet.com/search.jsp?Searchword={quote_plus(self.query)}",
            f"https://www.datasheetarchive.com/?q={quote_plus(self.query)}",
            f"https://datasheetspdf.com/search.php?q={quote_plus(self.query)}",
            f"https://www.datasheetcatalog.com/datasheets/{quote_plus(self.query.replace(' ', '_'))}.html",
            f"https://www.icmaster.com/search/?q={quote_plus(self.query)}",
        ]
        return [{"source": "Datasheet Archive", "url": s, "type": "datasheet"} for s in sources]
    
    def search_google_scholar(self):
        """Search for academic/technical papers about the product."""
        return [{
            "source": "Google Scholar",
            "url": f"https://scholar.google.com/scholar?q={quote_plus(self.query + ' technical')}",
            "type": "academic",
        }]
    
    def deduplicate(self):
        """Remove duplicate URLs."""
        seen = set()
        unique = []
        for r in self.results:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique.append(r)
        return unique
```

## Source Reference

### Manual & Documentation Archives
| Source | URL | Coverage |
|--------|-----|----------|
| **ManualsLib** | manualslib.com | 7M+ manuals, all categories |
| **Manuals+** | manualsplus.com | Electronics, appliances |
| **Scribd** | scribd.com | Technical documents (subscription) |
| **Internet Archive** | archive.org | Historical manuals |
| **Google Books** | books.google.com | Technical books |

### Datasheet Archives
| Source | URL | Coverage |
|--------|-----|----------|
| **AllDataSheet** | alldatasheet.com | 300M+ components |
| **Datasheet Archive** | datasheetarchive.com | 15M+ PDFs |
| **DatasheetPDF** | datasheetspdf.com | Components |
| **Datasheet Catalog** | datasheetcatalog.com | Legacy + modern |
| **IC Master** | icmaster.com | Cross-reference |

### Manufacturer Support Portals
| Manufacturer | Support URL |
|-------------|-------------|
| Siemens | support.industry.siemens.com |
| ABB | library.abb.com |
| Schneider | se.com/en/search |
| Omron | omron.com/global/en/search |
| Rockwell | literature.rockwellautomation.com |
| Phoenix Contact | phoenixcontact.com/en-pc/search |
| Festo | festo.com/net/en-us_us/SupportPortal |
| Texas Instruments | ti.com/tool |
| Microchip | microchip.com/en-us/search |
| ST Micro | st.com/en/search |
| Nordic Semi | nordicsemi.com/Products |
| Espressif | espressif.com/en/support/documents |
| Raspberry Pi | raspberrypi.com/documentation |
| Arduino | docs.arduino.cc |
| Prusa | help.prusa3d.com |
| Creality | creality.com/pages/download |
| Bambu Lab | bambulab.com/en/download |
| Snapmaker | snapmaker.zendesk.com |
| HP | support.hp.com |
| Dell | dell.com/support |
| Lenovo | pcsupport.lenovo.com |
| Cisco | cisco.com/c/en/us/support |
| Juniper | juniper.net/documentation |

### CAD & Mechanical
| Source | URL | Coverage |
|--------|-----|----------|
| **GrabCAD** | grabcad.com/library | 11M+ CAD models |
| **TraceParts** | traceparts.com | Manufacturer CAD |
| **3D ContentCentral** | 3dcontentcentral.com | Supplier models |
| **McMaster-Carr** | mcmaster.com | Standard parts + CAD |

### Safety & Regulatory
| Source | URL | Coverage |
|--------|-----|----------|
| **SDS Search** | sds.com/sds-search | Safety Data Sheets |
| **Chemwatch** | chemwatch.net | SDS database |
| **ECHA** | echa.europa.eu | EU chemical registry |
| **OSHA** | osha.gov/chemicaldata | US chemical safety |

## Search Workflow

### 1. Quick Search (Single Source)
```
User: "Snapmaker A350T manual"
→ Search ManualsLib: https://www.manualslib.com/products/Snapmaker-A350T.html
→ Search manufacturer: https://snapmaker.zendesk.com/hc/en-us
→ Return: PDF links, page links
```

### 2. Deep Search (All Sources)
```
User: "Siemens S7-1200 PLC technical documentation"
→ Search ManualsLib for user manual
→ Search Siemens support portal
→ Search GitHub for example code
→ Search datasheet archives for CPU specs
→ Search GrabCAD for CAD models
→ Aggregate all results with metadata
```

### 3. Component-Level Search
```
User: "ESP32-S3 datasheet"
→ Search manufacturer: espressif.com → ESP32-S3 Technical Reference Manual
→ Search AllDataSheet: alldatasheet.com → pinouts, electrical specs
→ Search GitHub: example code, Arduino libraries
→ Search GrabCAD: PCB footprint, 3D model
```

## Output Format

```json
{
  "product": "Snapmaker A350T",
  "manufacturer": "Snapmaker",
  "model": "A350T",
  "documents": [
    {
      "type": "User Manual",
      "title": "Snapmaker A350T User Manual v2.1",
      "source": "ManualsLib",
      "url": "https://www.manualslib.com/manual/1234567/Snapmaker-A350T.html",
      "format": "PDF",
      "language": "English",
      "pages": 85,
      "file_size": "4.2 MB"
    },
    {
      "type": "Technical Reference",
      "title": "A350T Technical Specifications",
      "source": "Snapmaker Support",
      "url": "https://snapmaker.zendesk.com/hc/en-us/articles/...",
      "format": "HTML",
      "language": "English"
    },
    {
      "type": "CAD Model",
      "title": "A350T 3D Model (STEP)",
      "source": "GrabCAD",
      "url": "https://grabcad.com/library/snapmaker-a350t-1",
      "format": "STEP/STL"
    }
  ]
}
```

## CLI Usage

```bash
# Quick search
python product_doc_finder.py "Snapmaker A350T" --type manual

# Deep search all sources
python product_doc_finder.py "Siemens S7-1200" --deep

# Component search
python product_doc_finder.py "ESP32-S3" --manufacturer "Espressif" --type datasheet

# Export results
python product_doc_finder.py "Prusa MK4" --output docs.json --format json
```

## Integration with Hermes

When user asks for product documentation:
1. Parse product name, model, manufacturer from query
2. Search top 3 sources in parallel (ManualsLib, manufacturer, GitHub)
3. Present results with direct links
4. Optionally download and extract key information
5. Save to local cache for future reference

## Common Patterns

| Query Pattern | Example |
|--------------|---------|
| `[product] manual` | "Ender 3 V3 manual" |
| `[product] datasheet` | "LM358 datasheet" |
| `[product] service manual` | "HP LaserJet Pro service manual" |
| `[product] programming guide` | "Siemens S7-1200 programming guide" |
| `[product] installation guide` | "Nest Thermostat installation guide" |
| `[product] CAD` | "NEMA 17 stepper motor CAD" |
| `[product] firmware` | "Bambu Lab X1C firmware" |
| `[product] SDK` | "DJI Tello SDK" |
| `[product] API reference` | "Home Assistant API reference" |
| `[product] pinout` | "Raspberry Pi 4 pinout" |
