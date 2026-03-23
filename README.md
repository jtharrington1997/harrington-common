# harrington-common

Shared UI theme, reporting infrastructure, and admin framework for the Harrington app ecosystem.

## What It Provides

**Americana Theme** — Consistent visual language across all apps: navy primary, red accent, gold highlights, cream/parchment surfaces, Playfair Display headings, Source Sans 3 body text. One `apply_theme()` call styles any Streamlit app.

**Layout Components** — `render_header()`, `aw_panel()` context manager, `hero_banner()`, `metric_card()`, `status_badge()`. All apps use these for consistent panel styling and navigation.

**Reporting Infrastructure** — `harrington_common.reporting` provides LaTeX document generation, gnuplot figure export, and PDF compilation. Every app can produce professional branded reports from the command line without touching Streamlit.

**Admin Support** — Shared admin panel, API key management, and access control helpers.

## Consuming Apps

| App | Port | Purpose |
|-----|------|---------|
| harrington-labs | 8505 | Photonics lab simulators + LMI platform |
| harrington-wealth-management | 8502 | Retirement simulation + budget tracking |
| harrington-health | 8506 | Health analysis and clinical reporting |
| harrington-pax-americana | 8501 | Geo-strategic intelligence platform |
| harrington-automation-station | 8503 | Lab automation and beam profiling |

## Reporting API

```python
from harrington_common.reporting import (
    build_report_pdf, ReportConfig, ReportSection, latex_table,
    write_gnuplot_bundle, GnuplotSpec, GnuplotSeries,
)

sections = [
    ReportSection(title="Results", content="Analysis complete.", tables=[
        latex_table(["Metric", "Value"], [["Power", "50 W"], ["Efficiency", "65%"]])
    ]),
]
build_report_pdf(sections, "output/report.pdf", ReportConfig(title="My Report"))
```

## Installation

```bash
# As workspace member (preferred)
uv sync

# As sibling editable dependency
pip install -e ../harrington-common
```

## TODO

- [ ] Add report templates per app (LMI simulation report, health lab report, budget summary)
- [ ] Move gnuplot color palette and figure sizing defaults into reporting config
- [ ] Add shared Streamlit components for file export (download buttons, format selection)
- [ ] Standardize admin panel across all apps (currently each app has slight variations)
- [ ] Add dark mode theme variant
