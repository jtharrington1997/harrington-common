"""
Shared dark theme CSS and Streamlit config for all Harrington apps.
Usage:
    from harrington_common.theme import apply_theme
    apply_theme()
"""

import streamlit as st

# Standard color palette
COLORS = {
    "bg_primary": "#0D1117",
    "bg_secondary": "#161B22",
    "bg_tertiary": "#21262D",
    "border": "#30363D",
    "text_primary": "#E6EDF3",
    "text_secondary": "#C9D1D9",
    "text_muted": "#8B949E",
    "accent_red": "#E63946",
    "accent_green": "#3FB950",
    "accent_blue": "#388BFD",
    "accent_yellow": "#D29922",
}

# Standard ports per app
PORTS = {
    "pax-americana": 8501,
    "rickman-sequence-demo": 8502,
    "harrington-automation-station": 8503,
    "harrington-lmi": 8504,
}

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }
    code, .stCode { font-family: 'JetBrains Mono', monospace; }

    .hero-banner {
        background: linear-gradient(135deg, #0D1117 0%, #161B22 50%, #1a0a0a 100%);
        border: 1px solid #30363D;
        border-left: 4px solid #E63946;
        border-radius: 8px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
    }
    .hero-banner h1 {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: #E6EDF3;
        margin: 0 0 0.3rem 0;
    }
    .hero-banner .subtitle {
        color: #8B949E;
        font-size: 0.95rem;
        margin: 0;
    }
    .hero-banner .accent { color: #E63946; font-weight: 600; }

    .hw-card, .info-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
    }

    .metric-box {
        background: #0D1117;
        border: 1px solid #30363D;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
    }
    .metric-box .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: #E63946;
    }
    .metric-box .metric-label {
        color: #8B949E;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .status-ok { color: #3FB950; font-weight: 600; }
    .status-warn { color: #D29922; font-weight: 600; }
    .status-err { color: #E63946; font-weight: 600; }
    .status-off { color: #6E7681; font-weight: 600; }

    section[data-testid="stSidebar"] {
        background: #0D1117;
        border-right: 1px solid #30363D;
    }
</style>
"""


def apply_theme():
    """Inject the shared CSS into the current Streamlit page."""
    st.markdown(CSS, unsafe_allow_html=True)


def hero_banner(title, subtitle, accent_color="#E63946"):
    """Render a standard hero banner."""
    st.markdown(f"""
    <div class="hero-banner" style="border-left-color: {accent_color};">
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def metric_card(value, label, col=None):
    """Render a styled metric card. Pass a streamlit column or uses current context."""
    html = f"""
    <div class="metric-box">
        <div class="metric-val">{value}</div>
        <div class="metric-label">{label}</div>
    </div>"""
    if col:
        col.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def status_badge(text, status="off"):
    """Return HTML for a status badge. status: ok, warn, err, off."""
    return f'<span class="status-{status}">{text}</span>'
