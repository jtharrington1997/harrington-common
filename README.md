# Harrington Common

Shared UI, theme, and admin-support package for the Harrington app ecosystem.

Harrington Common provides the shared design language and reusable interface primitives used across Joey Harrington's Streamlit applications. It exists to keep branding, layout, and common admin-facing behaviors consistent across repos.

## Purpose

This package centralizes:

- shared Americana theme styling
- reusable layout helpers
- panel and card wrappers
- common UI utilities
- shared admin-support functionality
- cross-app consistency for the Harrington ecosystem

## Apps using this package

- `pax-americana`
- `rickman-sequence-demo`
- `automation-station`
- `harrington-lmi`

## Theme system

The shared visual language uses the Americana palette and typography standard used across the ecosystem.

Representative design elements include:

- navy primary styling
- red accent styling
- gold highlight color
- cream/parchment surfaces
- Playfair Display headings
- Source Sans 3 body text

## Installation

This project uses `uv`.

### Install dependencies

```bash
uv sync
```

### Use as a sibling editable dependency

```toml
[tool.uv.sources]
harrington-common = { path = "../harrington-common", editable = true }
```

## Usage example

```python
from harrington_common.theme import apply_theme, aw_panel, render_header

apply_theme()
render_header()

with aw_panel():
    ...
```

## Development notes

- Keep app-specific business logic out of this package
- Prefer stable shared helpers over duplicated repo-local copies
- Commit `uv.lock` for reproducible installs across machines

## Related repos

- `pax-americana`
- `rickman-sequence-demo`
- `automation-station`
- `harrington-lmi`
