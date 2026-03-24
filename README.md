# harrington-common

Shared UI theme, cross-platform compute acceleration, reporting infrastructure, and admin framework for the Harrington app ecosystem.

## What It Provides

**Compute Acceleration** — `harrington_common.compute` provides automatic backend detection and JIT compilation across all platforms:

| Platform | Backend | Performance |
|----------|---------|-------------|
| iOS / WASM | NumPy | Baseline |
| macOS / Windows | Numba JIT (CPU) | 10–100× faster |
| Linux desktop | Numba JIT (12 threads) | 10–100× faster |
| Linux + NVIDIA GPU | CuPy (CUDA) + Numba | 100–1000× faster |
| HPC / supercomputer | CuPy + MPI-ready | Maximum |

Key APIs:
- `@jit` — Numba `@njit` when available, identity decorator on iOS/WASM
- `parallel_map()` / `parameter_sweep()` — joblib → ProcessPool → serial fallback
- `get_array_module()` / `to_device()` / `to_host()` — CuPy/NumPy array dispatch
- `render_compute_info()` — Streamlit widget for Admin pages

Pre-built JIT kernels: Gaussian beam propagation, Beer-Lambert absorption, material propagation, nonlinear optics, thermal accumulation, two-temperature Euler integration, transfer matrix coatings, Monte Carlo retirement simulations.

Environment variables: `HARRINGTON_NO_JIT=1` (force NumPy), `HARRINGTON_NO_CUDA=1` (disable GPU), `HARRINGTON_SERIAL=1` (no parallelism).

**Americana Theme** — Consistent visual language across all apps: navy primary, red accent, gold highlights, cream/parchment surfaces, Playfair Display headings, Source Sans 3 body text. One `apply_theme()` call styles any Streamlit app.

**Layout Components** — `render_header()`, `aw_panel()` context manager, `hero_banner()`, `metric_card()`, `status_badge()`.

**Reporting Infrastructure** — `harrington_common.reporting` provides LaTeX document generation, gnuplot figure export, and PDF compilation.

**Admin Support** — Shared admin panel with Compute tab, API key management, and access control helpers.

## Consuming Apps

| App | Port | Purpose |
|-----|------|---------|
| harrington-pax-americana | 8501 | Geo-stragic intelligence platform |
| harrington-wealth-management | 8502 | Retirement simulation + budget tracking |
| harrington-automation-station | 8503 | Lab automation and beam profiling |
| harrington-health | 8504 | Health analysis and clinical reporting |
| harrington-labs | 8505 | Photonics lab simulators + LMI platform |

## Installation

```bash
# Base install (all platforms)
uv sync

# With Numba JIT acceleration
pip install "harrington-common[hpc]"

# With CUDA GPU support
pip install "harrington-common[full]"
```

## Current IronMan Stack

- CuPy 14.0.1 (CUDA GPU, ~10 GB VRAM)
- Numba 0.64.0 (12 CPU threads)
- NumPy 2.4.3
