"""Shared Americana theme for all Harrington Streamlit apps.

Usage:
    from harrington_common.theme import apply_theme, render_header, aw_panel

    st.set_page_config(page_title="My App", layout="wide")
    apply_theme()
    render_header("App Title", "Subtitle line")

    with aw_panel():
        st.subheader("Section")
        ...
"""
from __future__ import annotations

import base64
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import streamlit as st


# ── Brand tokens ─────────────────────────────────────────────────────────────

BRAND = {
    "app_title": "Harrington",
    "primary": "#1a3a5c",
    "primary_hover": "#244d78",
    "accent": "#8b2332",
    "gold": "#b8860b",
    "cream": "#faf8f5",
    "parchment": "#f0ece6",
    "font_heading": "Playfair Display",
    "font_body": "Source Sans 3",
}

# Standard ports per app
PORTS = {
    "harrington-pax-americana": 8501,
    "harrington-wealth-management": 8502,
    "harrington-automation-station": 8503,
    "harrington-labs": 8505,
    "harrington-health": 8506,
}


# ── Dark-mode palette ────────────────────────────────────────────────────────
# Streamlit exposes its theme via `st.get_option("theme.base")` and via the
# custom component message channel.  However, the most reliable detection is
# the CSS `prefers-color-scheme` media query combined with checking the
# Streamlit config `theme.base`.

BRAND_DARK = {
    "bg": "#0e1117",
    "surface": "#1a1d24",
    "panel_bg": "rgba(30,33,40,0.75)",
    "ink": "#e6e8ec",
    "muted": "#9ca3af",
    "border": "rgba(255,255,255,0.10)",
    "border_accent": "rgba(139,35,50,0.25)",
    "shadow": "0 1px 3px rgba(0,0,0,0.3)",
    "heading": "#c5d0e6",
    "primary_text": "#7eaed4",
    "code_bg": "#1a1d24",
    "parchment": "#161920",
}


def _is_dark_mode() -> bool:
    """Detect whether Streamlit is running in dark mode.

    Checks `theme.base` in the Streamlit config.  Falls back to False
    (light mode) if the option isn't set.
    """
    try:
        base = st.get_option("theme.base")
        if base == "dark":
            return True
    except Exception:
        pass
    # Also check the background color — if it's very dark, assume dark mode
    try:
        bg = st.get_option("theme.backgroundColor")
        if bg and bg.startswith("#"):
            r = int(bg[1:3], 16)
            g = int(bg[3:5], 16)
            b = int(bg[5:7], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminance < 0.4
    except Exception:
        pass
    return False


def is_dark_mode() -> bool:
    """Public API to check if dark mode is active."""
    return _is_dark_mode()


# ── CSS ──────────────────────────────────────────────────────────────────────

_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@300;400;500;600&display=swap');
:root {{
  --aw-heading: "{fh}", "Georgia", serif;
  --aw-body: "{fb}", "Helvetica Neue", sans-serif;
  --aw-navy: {primary};
  --aw-navy-hover: {hover};
  --aw-red: {accent};
  --aw-gold: {gold};
  --aw-cream: {cream};
  --aw-parchment: {parchment};
  --aw-ink: #1a1a2e;
  --aw-muted: #5c5c6e;
  --aw-panel-bg: rgba(255,255,255,0.65);
  --aw-border: rgba(26,58,92,0.12);
  --aw-border-accent: rgba(139,35,50,0.15);
  --aw-shadow: 0 1px 3px rgba(26,26,46,0.06);
}}

html, body, .stApp {{
  font-family: var(--aw-body) !important;
  color: var(--aw-ink) !important;
}}

.stApp {{
  background: var(--aw-cream) !important;
  background-image:
    radial-gradient(ellipse at 20%% 0%%, rgba(26,58,92,0.03) 0%%, transparent 50%%),
    radial-gradient(ellipse at 80%% 100%%, rgba(139,35,50,0.02) 0%%, transparent 50%%) !important;
}}

.stMarkdown, .stText, label, p, li {{
  color: var(--aw-ink) !important;
  font-family: var(--aw-body) !important;
  line-height: 1.65;
}}

.stCaption, small {{
  color: var(--aw-muted) !important;
  font-weight: 300;
}}

h1 {{
  font-family: var(--aw-heading) !important;
  font-weight: 700 !important;
  color: var(--aw-navy) !important;
  letter-spacing: -0.03em;
  font-size: 2.2rem !important;
  border-bottom: 2px solid var(--aw-red);
  padding-bottom: 8px;
}}

h2 {{
  font-family: var(--aw-heading) !important;
  font-weight: 600 !important;
  color: var(--aw-navy) !important;
  letter-spacing: -0.02em;
}}

h3 {{
  font-family: var(--aw-heading) !important;
  font-weight: 600 !important;
  color: var(--aw-ink) !important;
}}

h4,h5,h6 {{
  font-family: var(--aw-body) !important;
  font-weight: 600 !important;
  color: var(--aw-ink) !important;
}}

.block-container {{
  padding-top: 1.2rem;
  padding-bottom: 2rem;
  max-width: 1200px;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
  background: var(--aw-parchment) !important;
  border-right: 2px solid var(--aw-border);
}}
section[data-testid="stSidebar"] .stMarkdown p {{
  color: var(--aw-ink) !important;
}}

/* Panels */
div[data-testid="stVerticalBlock"]:has(.aw-panel-marker) {{
  background: var(--aw-panel-bg);
  border: 1px solid var(--aw-border);
  border-radius: 12px;
  padding: 20px 24px;
  margin: 8px 0 16px 0;
  box-shadow: var(--aw-shadow);
  backdrop-filter: blur(8px);
}}
.aw-panel-marker {{ height:0; margin:0; padding:0; }}

/* Metrics */
div[data-testid="stMetric"] {{
  border-radius: 10px;
  border: 1px solid var(--aw-border);
  background: rgba(255,255,255,0.5);
  padding: 14px 18px;
  box-shadow: var(--aw-shadow);
}}
div[data-testid="stMetric"] label {{
  font-family: var(--aw-body) !important;
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.7rem !important;
  letter-spacing: 0.08em;
  color: var(--aw-muted) !important;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
  font-family: var(--aw-heading) !important;
  font-weight: 700;
  color: var(--aw-navy) !important;
}}

/* Buttons */
button[kind="primary"], .stFormSubmitButton button {{
  background-color: var(--aw-navy) !important;
  border: 0 !important;
  border-radius: 8px !important;
  font-family: var(--aw-body) !important;
  font-weight: 600 !important;
  letter-spacing: 0.03em;
  color: #faf8f5 !important;
  transition: background-color 0.2s ease;
}}
button[kind="primary"]:hover, .stFormSubmitButton button:hover {{
  background-color: var(--aw-navy-hover) !important;
  color: #ffffff !important;
}}
button[kind="primary"] p, button[kind="primary"] span,
.stFormSubmitButton button p, .stFormSubmitButton button span {{
  color: #faf8f5 !important;
}}
button[kind="primary"] *, .stFormSubmitButton button * {{
  color: #faf8f5 !important;
}}

/* Secondary buttons */
button[kind="secondary"] {{
  color: var(--aw-navy) !important;
  border-color: var(--aw-navy) !important;
  border-radius: 8px !important;
  font-family: var(--aw-body) !important;
}}
button[kind="secondary"]:hover {{
  background-color: var(--aw-navy) !important;
  color: #faf8f5 !important;
}}
button[kind="secondary"]:hover p, button[kind="secondary"]:hover span {{
  color: #faf8f5 !important;
}}

/* Links */
a {{ color: var(--aw-navy) !important; text-decoration: none; }}
a:hover {{ color: var(--aw-red) !important; }}

/* Expanders */
div[data-testid="stExpander"] {{
  border: 1px solid var(--aw-border) !important;
  border-radius: 10px !important;
  margin-bottom: 8px;
  background: rgba(255,255,255,0.4);
}}
div[data-testid="stExpander"] summary {{
  font-family: var(--aw-body) !important;
  font-weight: 500;
}}

/* Text inputs */
input[type="text"], textarea {{
  border: 1px solid var(--aw-border) !important;
  border-radius: 8px !important;
  background: rgba(255,255,255,0.6) !important;
}}
input[type="text"]:focus, textarea:focus {{
  border-color: var(--aw-navy) !important;
  box-shadow: 0 0 0 1px var(--aw-navy) !important;
}}

/* Selectbox */
div[data-testid="stSelectbox"] > div {{
  border-radius: 8px !important;
}}

/* Tabs */
button[data-baseweb="tab"] {{
  font-family: var(--aw-body) !important;
  font-weight: 500;
  color: var(--aw-muted) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
  color: var(--aw-navy) !important;
}}

/* Dataframes / tables */
div[data-testid="stDataFrame"] {{
  border: 1px solid var(--aw-border);
  border-radius: 8px;
}}

/* Top accent line */
.stApp > header {{
  background: linear-gradient(90deg, var(--aw-navy) 0%%, var(--aw-navy) 33%%, var(--aw-cream) 33%%, var(--aw-cream) 67%%, var(--aw-red) 67%%, var(--aw-red) 100%%) !important;
  height: 4px !important;
}}

/* Code blocks — keep monospace readable */
code, .stCode {{
  font-family: "JetBrains Mono", "Source Code Pro", monospace;
  background: var(--aw-parchment);
  border: 1px solid var(--aw-border);
  border-radius: 4px;
}}

/* Hero banner component */
.hw-hero {{
  background: linear-gradient(135deg, var(--aw-cream) 0%%, #fff 50%%, var(--aw-parchment) 100%%);
  border: 1px solid var(--aw-border);
  border-left: 4px solid var(--aw-red);
  border-radius: 12px;
  padding: 2rem 2.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--aw-shadow);
}}
.hw-hero h1 {{
  font-family: var(--aw-heading) !important;
  font-size: 2rem !important;
  font-weight: 700;
  color: var(--aw-navy) !important;
  margin: 0 0 0.3rem 0;
  border-bottom: none;
  padding-bottom: 0;
}}
.hw-hero .subtitle {{
  color: var(--aw-muted);
  font-family: var(--aw-body);
  font-size: 0.95rem;
  margin: 0;
}}
.hw-hero .accent {{ color: var(--aw-red); font-weight: 600; }}

/* Metric card component */
.hw-metric {{
  background: rgba(255,255,255,0.5);
  border: 1px solid var(--aw-border);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
  box-shadow: var(--aw-shadow);
}}
.hw-metric .metric-val {{
  font-family: var(--aw-heading);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--aw-navy);
}}
.hw-metric .metric-label {{
  color: var(--aw-muted);
  font-family: var(--aw-body);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}}

/* Status badges */
.status-ok {{ color: #2d6a4f; font-weight: 600; }}
.status-warn {{ color: var(--aw-gold); font-weight: 600; }}
.status-err {{ color: var(--aw-red); font-weight: 600; }}
.status-off {{ color: var(--aw-muted); font-weight: 600; }}

/* ─── Dark mode overrides ─────────────────────────────────────────────────── */
/* Applied when Streamlit is set to dark theme or system prefers dark */

.stApp[data-theme="dark"],
.stApp.dark-mode {{
  --aw-navy: #7eaed4;
  --aw-navy-hover: #9dc4e8;
  --aw-red: #d4626f;
  --aw-gold: #d4a843;
  --aw-cream: #0e1117;
  --aw-parchment: #161920;
  --aw-ink: #e6e8ec;
  --aw-muted: #9ca3af;
  --aw-panel-bg: rgba(30,33,40,0.75);
  --aw-border: rgba(255,255,255,0.10);
  --aw-border-accent: rgba(212,98,111,0.25);
  --aw-shadow: 0 1px 3px rgba(0,0,0,0.3);
}}

.stApp[data-theme="dark"] .stApp,
.stApp.dark-mode .stApp,
.stApp[data-theme="dark"],
.stApp.dark-mode {{
  background: #0e1117 !important;
  background-image:
    radial-gradient(ellipse at 20%% 0%%, rgba(126,174,212,0.04) 0%%, transparent 50%%),
    radial-gradient(ellipse at 80%% 100%%, rgba(212,98,111,0.03) 0%%, transparent 50%%) !important;
}}

.stApp[data-theme="dark"] section[data-testid="stSidebar"],
.stApp.dark-mode section[data-testid="stSidebar"] {{
  background: #161920 !important;
  border-right-color: rgba(255,255,255,0.08) !important;
}}

.stApp[data-theme="dark"] div[data-testid="stMetric"],
.stApp.dark-mode div[data-testid="stMetric"] {{
  background: rgba(30,33,40,0.6) !important;
  border-color: rgba(255,255,255,0.08) !important;
}}

.stApp[data-theme="dark"] div[data-testid="stMetric"] [data-testid="stMetricValue"],
.stApp.dark-mode div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
  color: #c5d0e6 !important;
}}

.stApp[data-theme="dark"] div[data-testid="stExpander"],
.stApp.dark-mode div[data-testid="stExpander"] {{
  background: rgba(30,33,40,0.4) !important;
  border-color: rgba(255,255,255,0.08) !important;
}}

.stApp[data-theme="dark"] input[type="text"],
.stApp[data-theme="dark"] textarea,
.stApp.dark-mode input[type="text"],
.stApp.dark-mode textarea {{
  background: rgba(30,33,40,0.6) !important;
  border-color: rgba(255,255,255,0.12) !important;
  color: #e6e8ec !important;
}}

.stApp[data-theme="dark"] code, .stApp[data-theme="dark"] .stCode,
.stApp.dark-mode code, .stApp.dark-mode .stCode {{
  background: #1a1d24 !important;
  border-color: rgba(255,255,255,0.08) !important;
  color: #e6e8ec !important;
}}

.stApp[data-theme="dark"] h1,
.stApp.dark-mode h1 {{
  color: #c5d0e6 !important;
  border-bottom-color: #d4626f !important;
}}

.stApp[data-theme="dark"] h2,
.stApp.dark-mode h2 {{
  color: #c5d0e6 !important;
}}

.stApp[data-theme="dark"] a,
.stApp.dark-mode a {{
  color: #7eaed4 !important;
}}
.stApp[data-theme="dark"] a:hover,
.stApp.dark-mode a:hover {{
  color: #d4626f !important;
}}

.stApp[data-theme="dark"] button[data-baseweb="tab"][aria-selected="true"],
.stApp.dark-mode button[data-baseweb="tab"][aria-selected="true"] {{
  color: #7eaed4 !important;
}}

.stApp[data-theme="dark"] .hw-hero,
.stApp.dark-mode .hw-hero {{
  background: linear-gradient(135deg, #0e1117 0%%, #161920 50%%, #1a1d24 100%%) !important;
  border-color: rgba(255,255,255,0.08) !important;
  border-left-color: #d4626f !important;
}}
.stApp[data-theme="dark"] .hw-hero h1,
.stApp.dark-mode .hw-hero h1 {{
  color: #c5d0e6 !important;
}}

.stApp[data-theme="dark"] .hw-metric,
.stApp.dark-mode .hw-metric {{
  background: rgba(30,33,40,0.6) !important;
  border-color: rgba(255,255,255,0.08) !important;
}}
.stApp[data-theme="dark"] .hw-metric .metric-val,
.stApp.dark-mode .hw-metric .metric-val {{
  color: #c5d0e6 !important;
}}

.stApp[data-theme="dark"] .status-ok,
.stApp.dark-mode .status-ok {{ color: #4ade80 !important; }}

/* Also handle the system preference for browsers */
@media (prefers-color-scheme: dark) {{
  :root {{
    --aw-navy: #7eaed4;
    --aw-red: #d4626f;
    --aw-gold: #d4a843;
    --aw-ink: #e6e8ec;
    --aw-muted: #9ca3af;
  }}
}}

</style>"""


# ── Theme application ────────────────────────────────────────────────────────


def apply_theme() -> None:
    """Inject the shared Americana CSS into the current Streamlit page.

    Detects dark mode and adds a `dark-mode` CSS class to the app root
    so the dark palette overrides activate automatically.
    """
    st.markdown(
        _CSS.format(
            fh=BRAND["font_heading"],
            fb=BRAND["font_body"],
            primary=BRAND["primary"],
            hover=BRAND["primary_hover"],
            accent=BRAND["accent"],
            gold=BRAND["gold"],
            cream=BRAND["cream"],
            parchment=BRAND["parchment"],
        ),
        unsafe_allow_html=True,
    )
    # Inject JS to add dark-mode class when Streamlit is in dark mode.
    # This bridges the gap between Streamlit's theme config and CSS selectors.
    st.markdown(
        """<script>
        (function() {
            const app = document.querySelector('.stApp');
            if (!app) return;
            const style = getComputedStyle(document.documentElement);
            const bg = style.getPropertyValue('--background-color') || '';
            // Detect dark theme by checking computed background luminance
            const body = getComputedStyle(document.body);
            const bodyBg = body.backgroundColor;
            if (bodyBg) {
                const m = bodyBg.match(/\\d+/g);
                if (m && m.length >= 3) {
                    const lum = (0.299*m[0] + 0.587*m[1] + 0.114*m[2]) / 255;
                    if (lum < 0.35) {
                        app.classList.add('dark-mode');
                        app.setAttribute('data-theme', 'dark');
                    }
                }
            }
        })();
        </script>""",
        unsafe_allow_html=True,
    )


# Alias for backward compatibility with pax-americana
apply_brand_css = apply_theme


# ── Plotly theme helper ──────────────────────────────────────────────────────


def plotly_layout(**overrides) -> dict:
    """Return a Plotly layout dict that adapts to light/dark mode.

    Usage:
        fig.update_layout(**plotly_layout(height=400, xaxis_title="Time"))

    In dark mode, uses plotly_dark template with dark backgrounds.
    In light mode, uses plotly_white with transparent backgrounds.
    """
    dark = _is_dark_mode()
    base = {
        "template": "plotly_dark" if dark else "plotly_white",
        "paper_bgcolor": "rgba(14,17,23,0.0)" if dark else "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(14,17,23,0.0)" if dark else "rgba(0,0,0,0)",
        "font": {
            "family": BRAND["font_body"],
            "color": "#e6e8ec" if dark else "#1a1a2e",
        },
        "colorway": (
            ["#7eaed4", "#d4626f", "#d4a843", "#4ade80", "#a78bfa", "#f472b6"]
            if dark else
            ["#1a3a5c", "#8b2332", "#b8860b", "#2d6a4f", "#6b21a8", "#be185d"]
        ),
    }
    base.update(overrides)
    return base


def plotly_line_color() -> str:
    """Return the primary line color for the current mode."""
    return "#7eaed4" if _is_dark_mode() else "#1a3a5c"


def plotly_accent_color() -> str:
    """Return the accent line color for the current mode."""
    return "#d4626f" if _is_dark_mode() else "#8b2332"


# ── Components ───────────────────────────────────────────────────────────────


def render_header(
    title: str = "Harrington",
    subtitle: str = "",
    logo_path: Optional[str] = None,
) -> None:
    """Render the standard app header with optional logo.

    Args:
        title: App title displayed in the header.
        subtitle: Caption line below the title.
        logo_path: Path to an SVG logo file. If None, renders title only.
    """
    apply_theme()

    if logo_path:
        col1, col2 = st.columns([1, 4], vertical_alignment="center")
        with col1:
            st_svg(logo_path, height_px=56)
        with col2:
            st.title(title)
            if subtitle:
                st.caption(subtitle)
    else:
        st.title(title)
        if subtitle:
            st.caption(subtitle)


def st_svg(path: str, height_px: int = 56) -> None:
    """Render an SVG file inline."""
    p = Path(path)
    if not p.exists():
        return
    svg_bytes = p.read_bytes()
    b64 = base64.b64encode(svg_bytes).decode("utf-8")
    html = (
        '<div style="display:flex; align-items:center; min-height:{h}px;">'
        '<img src="data:image/svg+xml;base64,{d}" '
        'style="height:{h}px; width:auto; max-width:100%; object-fit:contain; display:block;" />'
        '</div>'
    ).format(h=height_px, d=b64)
    st.markdown(html, unsafe_allow_html=True)


@contextmanager
def aw_panel():
    """Context manager that wraps content in a styled panel card."""
    panel_id = "aw-panel-" + uuid.uuid4().hex
    with st.container():
        st.markdown(
            '<div class="aw-panel-marker" data-aw-panel="' + panel_id + '"></div>',
            unsafe_allow_html=True,
        )
        yield


def hero_banner(
    title: str,
    subtitle: str = "",
    accent_word: Optional[str] = None,
) -> None:
    """Render a hero banner at the top of a page.

    Args:
        title: Main heading.
        subtitle: Subtitle text.
        accent_word: Optional word to highlight in the accent color.
    """
    title_html = title
    if accent_word and accent_word in title:
        title_html = title.replace(
            accent_word, '<span class="accent">' + accent_word + '</span>'
        )
    st.markdown(
        '<div class="hw-hero">'
        '<h1>' + title_html + '</h1>'
        + ('<p class="subtitle">' + subtitle + '</p>' if subtitle else '')
        + '</div>',
        unsafe_allow_html=True,
    )


def metric_card(value: str, label: str, col=None) -> None:
    """Render a styled metric card.

    Args:
        value: The metric value to display.
        label: Label below the value.
        col: Optional Streamlit column. If None, renders in current context.
    """
    html = (
        '<div class="hw-metric">'
        '<div class="metric-val">' + str(value) + '</div>'
        '<div class="metric-label">' + str(label) + '</div>'
        '</div>'
    )
    if col:
        col.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def status_badge(text: str, status: str = "off") -> str:
    """Return HTML for a status badge.

    Args:
        text: Badge text.
        status: One of 'ok', 'warn', 'err', 'off'.
    """
    return '<span class="status-' + status + '">' + text + '</span>'


# ── Text utilities ───────────────────────────────────────────────────────────

import re

_ESCAPE_RE = re.compile(r"([$*_`~\[\]<>\\])")


def esc(text: str) -> str:
    """Escape special Markdown/LaTeX characters for safe Streamlit rendering."""
    if not text:
        return text
    result = _ESCAPE_RE.sub(r"\\\1", text)
    result = re.sub(r"^(#{1,6})\s", r"\\\1 ", result, flags=re.MULTILINE)
    return result
