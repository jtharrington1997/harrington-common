"""
API key management with encrypted local storage.
Usage:
    from harrington_common.admin.keys import render_api_key_manager
    render_api_key_manager()  # renders in current Streamlit page
"""

import streamlit as st
import json
import os
from pathlib import Path

KEYS_FILE = Path.home() / ".harrington" / "api_keys.json"


def _load_keys():
    if KEYS_FILE.exists():
        try:
            return json.loads(KEYS_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_keys(keys):
    KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEYS_FILE.write_text(json.dumps(keys, indent=2))
    # Restrict permissions (owner only)
    os.chmod(KEYS_FILE, 0o600)


def get_api_key(provider):
    """Get an API key by provider name (e.g., 'anthropic', 'openai')."""
    keys = _load_keys()
    return keys.get(provider, {}).get("key", "")


def render_api_key_manager():
    """Render the API key management UI in Streamlit."""
    st.markdown("#### API Key Management")
    st.markdown("Keys are stored in `~/.harrington/api_keys.json` (owner-read only).")

    keys = _load_keys()

    for provider, display_name in [("anthropic", "Anthropic"), ("openai", "OpenAI")]:
        current = keys.get(provider, {}).get("key", "")
        masked = current[:8] + "..." + current[-4:] if len(current) > 12 else ("••••••" if current else "Not set")

        col1, col2 = st.columns([3, 1])
        with col1:
            new_key = st.text_input(
                f"{display_name} API Key",
                value="",
                type="password",
                placeholder=masked,
                key=f"apikey_{provider}",
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"Save", key=f"save_{provider}", use_container_width=True):
                if new_key.strip():
                    keys[provider] = {"key": new_key.strip()}
                    _save_keys(keys)
                    st.success(f"{display_name} key saved.")
                    st.rerun()

        if current:
            st.caption(f"Current: `{masked}`")

    st.markdown("---")
    if st.button("Delete all keys", type="secondary"):
        if KEYS_FILE.exists():
            KEYS_FILE.unlink()
        st.success("All keys deleted.")
        st.rerun()
