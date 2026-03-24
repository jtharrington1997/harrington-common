"""Harrington Common — shared theme, admin, compute, and components."""
from __future__ import annotations

__version__ = "0.3.1"

# Convenient re-exports
from .theme import (  # noqa: F401
    apply_theme,
    render_header,
    aw_panel,
    hero_banner,
    metric_card,
    status_badge,
    st_svg,
    esc,
    BRAND,
    PORTS,
)

# Compute layer (lazy — no heavy imports at module level)
from .compute import (  # noqa: F401
    Backend,
    active_backend,
    backend_info,
    jit,
    vectorize,
    prange,
    get_array_module,
    to_device,
    to_host,
    parallel_map,
    parameter_sweep,
    render_compute_info,
    HAS_NUMBA,
    HAS_CUPY,
)
