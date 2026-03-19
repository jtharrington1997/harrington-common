# Harrington Common

Shared theme, admin framework, and UI components for the Harrington app ecosystem.

## Apps Using This Package

| App | Domain | Port |
|-----|--------|------|
| pax-americana | Geopolitical predictions | 8501 |
| rickman-sequence-demo | Retirement planning | 8502 |
| automation-station | Lab automation | 8503 |
| harrington-lmi | Laser-material interaction | 8504 |

## Installation

All apps reference this as a local editable dependency via uv:

```toml
[tool.uv.sources]
harrington-common = { path = "../harrington-common", editable = true }
```

Then:
```bash
uv sync
```

## Usage

```python
from harrington_common.theme import apply_theme, render_header, aw_panel, esc
from harrington_common.theme import hero_banner, metric_card, status_badge
from harrington_common.admin.keys import load_api_keys

# In any Streamlit page:
st.set_page_config(page_title="My Page", layout="wide")
apply_theme()

with aw_panel():
    st.subheader("Section Title")
    st.write("Content here")
```

## Theme: Americana

The shared theme uses a cream/parchment palette with navy and red accents:

- **Primary (navy):** `#1a3a5c`
- **Accent (red):** `#8b2332`
- **Gold:** `#b8860b`
- **Background (cream):** `#faf8f5`
- **Parchment:** `#f0ece6`
- **Heading font:** Playfair Display
- **Body font:** Source Sans 3

## Components

- `apply_theme()` -- Inject Americana CSS
- `render_header(title, subtitle, logo_path)` -- Standard app header
- `aw_panel()` -- Context manager for styled card panels
- `hero_banner(title, subtitle, accent_word)` -- Hero section
- `metric_card(value, label, col)` -- Styled metric display
- `status_badge(text, status)` -- Colored status indicator
- `esc(text)` -- Escape Markdown/LaTeX special characters
