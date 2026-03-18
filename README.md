# Harrington Common

Shared theme, admin framework, and UI components for the Harrington app ecosystem.

## Apps Using This Package

| App | Domain | Port |
|-----|--------|------|
| pax-americana | Geopolitical predictions | 8501 |
| rickman-sequence-demo | Retirement planning | 8502 |
| harrington-automation-station | Lab equipment | 8503 |
| harrington-lmi | Laser-material interaction | 8504 |

## Installation

Add to any app's `pyproject.toml`:
```toml
dependencies = [
    "harrington-common @ git+https://github.com/jtharrington1997/harrington-common.git",
]
```

Then:
```bash
uv sync
```

## Usage
```python
from harrington_common.theme import apply_theme, hero_banner, metric_card
from harrington_common.admin.keys import render_api_key_manager, get_api_key

# Apply dark theme
apply_theme()

# Render hero banner
hero_banner("MY APP", "Subtitle here")

# Metric cards
metric_card("42.0", "w₀ (µm)")

# API key management (admin page)
render_api_key_manager()

# Use keys in code
key = get_api_key("anthropic")
```

## What's Included

- **Theme** — dark CSS, JetBrains Mono + Inter fonts, red accent palette, hero banners, metric cards, status badges
- **Admin** — API key manager (Anthropic/OpenAI) with encrypted local storage at `~/.harrington/api_keys.json`
- **Components** — reusable UI elements shared across all apps
