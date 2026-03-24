"""Harrington Compute — cross-platform acceleration layer.

Provides a unified interface for numerical computation that
automatically selects the best available backend:

    Priority: CuPy (CUDA GPU) → Numba JIT (CPU) → NumPy (fallback)

Every hot-loop utility in this module works identically on:
    - iOS / mobile (NumPy only, no JIT)
    - macOS (Numba CPU or NumPy fallback)
    - Windows (Numba CPU, optional CUDA)
    - Linux desktop (Numba + optional CUDA)
    - HPC / supercomputer (Numba + CUDA + MPI-ready)

Design principles:
    1. No engine ever *requires* CUDA or Numba — pure NumPy always works
    2. JIT decorators are applied at import time based on availability
    3. GPU arrays stay on-device; transfers happen only at boundaries
    4. Parallel sweeps use concurrent.futures (portable) or joblib

No Streamlit imports.
"""
from __future__ import annotations

import os
import math
import logging
import warnings
import functools
from enum import Enum
from typing import Any, Callable, TypeVar
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import numpy as np

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


# ══════════════════════════════════════════════════════════════════
#  Backend detection
# ══════════════════════════════════════════════════════════════════

class Backend(Enum):
    NUMPY = "numpy"
    NUMBA = "numba"
    CUPY = "cupy"


def _detect_numba() -> bool:
    """Check if Numba is importable and functional."""
    if os.environ.get("HARRINGTON_NO_JIT", "").lower() in ("1", "true", "yes"):
        return False
    try:
        import numba  # noqa: F401
        return True
    except ImportError:
        return False


def _detect_cupy() -> bool:
    """Check if CuPy is importable and a CUDA GPU is available."""
    if os.environ.get("HARRINGTON_NO_CUDA", "").lower() in ("1", "true", "yes"):
        return False
    try:
        import cupy as cp
        cp.cuda.runtime.getDeviceCount()  # raises if no GPU
        return True
    except Exception:
        return False


HAS_NUMBA: bool = _detect_numba()
HAS_CUPY: bool = _detect_cupy()

# Module-level prange for use inside @jit(parallel=True) functions.
# Numba requires numba.prange as a first-class object in the function body;
# a Python wrapper won't work because Numba compiles the function at JIT time.
if HAS_NUMBA:
    import numba as _nb
    _prange = _nb.prange
else:
    _prange = range  # type: ignore[assignment]


def active_backend() -> Backend:
    """Return the highest-priority available backend."""
    if HAS_CUPY:
        return Backend.CUPY
    if HAS_NUMBA:
        return Backend.NUMBA
    return Backend.NUMPY


def backend_info() -> dict[str, Any]:
    """Return a dict describing the active compute environment."""
    info: dict[str, Any] = {
        "backend": active_backend().value,
        "has_numba": HAS_NUMBA,
        "has_cupy": HAS_CUPY,
        "numpy_version": np.__version__,
    }
    if HAS_NUMBA:
        import numba
        info["numba_version"] = numba.__version__
        info["numba_num_threads"] = numba.config.NUMBA_NUM_THREADS
    if HAS_CUPY:
        import cupy as cp
        info["cupy_version"] = cp.__version__
        dev = cp.cuda.Device()
        info["gpu_name"] = dev.attributes.get("DeviceName", "unknown")  # type: ignore[attr-defined]
        info["gpu_memory_mb"] = dev.mem_info[1] / (1024 * 1024)
    return info


# ══════════════════════════════════════════════════════════════════
#  JIT decorator — portable @jit that degrades gracefully
# ══════════════════════════════════════════════════════════════════

def jit(
    func: F | None = None,
    *,
    nopython: bool = True,
    parallel: bool = False,
    fastmath: bool = True,
    cache: bool = True,
    nogil: bool = True,
) -> F | Callable[[F], F]:
    """Numba @njit when available, identity decorator otherwise.

    Usage::

        @jit
        def my_kernel(x, y):
            ...

        @jit(parallel=True, fastmath=True)
        def my_parallel_kernel(x, y):
            ...
    """
    def decorator(fn: F) -> F:
        if HAS_NUMBA:
            import numba as nb
            return nb.njit(  # type: ignore[return-value]
                fn,
                parallel=parallel,
                fastmath=fastmath,
                cache=cache,
                nogil=nogil,
            )
        return fn  # type: ignore[return-value]

    if func is not None:
        return decorator(func)
    return decorator  # type: ignore[return-value]


def vectorize(signatures=None, *, target: str = "parallel_or_cpu"):
    """Numba @vectorize when available, np.vectorize fallback.

    target: 'parallel_or_cpu' → numba parallel if available, else cpu
             'cuda' → cupy kernel (requires HAS_CUPY)
    """
    def decorator(fn: F) -> F:
        if HAS_NUMBA:
            import numba as nb
            nb_target = "parallel" if target == "parallel_or_cpu" else "cpu"
            if signatures:
                return nb.vectorize(signatures, target=nb_target, cache=True)(fn)  # type: ignore
            # Without explicit signatures, use @njit + manual broadcast
            return nb.vectorize(target=nb_target, cache=True)(fn)  # type: ignore
        return np.vectorize(fn)  # type: ignore[return-value]
    return decorator


def prange(n: int):
    """Numba prange when available, plain range otherwise."""
    if HAS_NUMBA:
        import numba as nb
        return nb.prange(n)
    return range(n)


# ══════════════════════════════════════════════════════════════════
#  Array backend — xp module (CuPy or NumPy)
# ══════════════════════════════════════════════════════════════════

def get_array_module():
    """Return the active array module (cupy or numpy)."""
    if HAS_CUPY:
        import cupy as cp
        return cp
    return np


def to_device(arr: np.ndarray):
    """Move a NumPy array to GPU if CuPy is available."""
    if HAS_CUPY:
        import cupy as cp
        return cp.asarray(arr)
    return arr


def to_host(arr) -> np.ndarray:
    """Ensure array is on CPU as NumPy."""
    if HAS_CUPY:
        import cupy as cp
        if isinstance(arr, cp.ndarray):
            return cp.asnumpy(arr)
    return np.asarray(arr)


# ══════════════════════════════════════════════════════════════════
#  Parallel sweep utilities
# ══════════════════════════════════════════════════════════════════

def parallel_map(
    fn: Callable,
    items: list,
    *,
    max_workers: int | None = None,
    use_processes: bool = True,
    backend: str = "auto",
) -> list:
    """Map fn over items in parallel.

    backend:
        'auto'     — ProcessPoolExecutor (best for CPU-bound)
        'threads'  — ThreadPoolExecutor (best for I/O-bound)
        'joblib'   — joblib.Parallel if installed
        'serial'   — no parallelism (debugging / iOS)

    Falls back gracefully: joblib → processes → threads → serial.
    """
    if len(items) == 0:
        return []
    if len(items) == 1 or backend == "serial":
        return [fn(item) for item in items]

    # Detect iOS / restricted environments
    if os.environ.get("HARRINGTON_SERIAL", "").lower() in ("1", "true"):
        return [fn(item) for item in items]

    if backend == "joblib" or backend == "auto":
        try:
            from joblib import Parallel, delayed
            n_jobs = max_workers or -1
            return Parallel(n_jobs=n_jobs, prefer="processes")(
                delayed(fn)(item) for item in items
            )
        except ImportError:
            if backend == "joblib":
                warnings.warn("joblib not installed, falling back to ProcessPoolExecutor")

    try:
        Executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        with Executor(max_workers=max_workers) as pool:
            return list(pool.map(fn, items))
    except (OSError, RuntimeError):
        # Fallback for platforms that don't support multiprocessing (iOS, WASM)
        logger.info("Multiprocessing unavailable, running serially")
        return [fn(item) for item in items]


def parameter_sweep(
    fn: Callable,
    param_grid: dict[str, list],
    *,
    max_workers: int | None = None,
    backend: str = "auto",
) -> list[dict]:
    """Run fn over a parameter grid in parallel.

    fn should accept **kwargs matching param_grid keys
    and return a dict of results.

    Returns list of dicts: [{**params, **results}, ...].
    """
    import itertools

    keys = list(param_grid.keys())
    combos = list(itertools.product(*param_grid.values()))

    def _run(combo):
        params = dict(zip(keys, combo))
        result = fn(**params)
        return {**params, **(result if isinstance(result, dict) else {"result": result})}

    return parallel_map(_run, combos, max_workers=max_workers, backend=backend)


# ══════════════════════════════════════════════════════════════════
#  Common numerical kernels (JIT-accelerated)
# ══════════════════════════════════════════════════════════════════

@jit
def _trapz_kernel(y, dx):
    """Trapezoidal integration — JIT-accelerated."""
    n = len(y)
    s = 0.0
    for i in range(1, n):
        s += 0.5 * (y[i - 1] + y[i]) * dx
    return s


@jit(parallel=True)
def _beer_lambert_step(irradiance, alpha_cm, beta_cm_per_w, dz_cm, n_points):
    """Vectorized Beer-Lambert propagation step with NLA."""
    out = np.empty(n_points)
    for i in _prange(n_points):
        I = irradiance[i]
        if alpha_cm > 0.0:
            lin_factor = math.exp(-alpha_cm * dz_cm)
            l_eff_cm = (1.0 - lin_factor) / alpha_cm
        else:
            lin_factor = 1.0
            l_eff_cm = dz_cm
        if beta_cm_per_w > 0.0 and I > 0.0:
            out[i] = I * lin_factor / (1.0 + beta_cm_per_w * I * l_eff_cm)
        else:
            out[i] = I * lin_factor
    return out


@jit
def _gaussian_w_z(w0, z_r, z_from_focus, n_medium):
    """Beam radius at z positions — JIT-accelerated."""
    n = len(z_from_focus)
    w = np.empty(n)
    z_r_eff = z_r * n_medium
    for i in range(n):
        w[i] = w0 * math.sqrt(1.0 + (z_from_focus[i] / z_r_eff) ** 2)
    return w


@jit
def _euler_two_temp(
    n_steps, dt_s, s_peak, t_center_s, pulse_sigma_s,
    G, Cl, ce_coeff, t_ambient_k
):
    """Two-temperature model Euler integration — JIT-accelerated."""
    te = np.full(n_steps, t_ambient_k)
    tl = np.full(n_steps, t_ambient_k)
    for i in range(1, n_steps):
        t_s = (i - 1) * dt_s
        s_t = s_peak * math.exp(-((t_s - t_center_s) ** 2) / (2.0 * pulse_sigma_s ** 2))
        ce = max(ce_coeff * te[i - 1], 1.0)
        dte = (s_t - G * (te[i - 1] - tl[i - 1])) / ce * dt_s
        dtl = G * (te[i - 1] - tl[i - 1]) / Cl * dt_s if Cl > 0.0 else 0.0
        te[i] = max(te[i - 1] + dte, t_ambient_k)
        tl[i] = max(tl[i - 1] + dtl, t_ambient_k)
    return te, tl


@jit
def _thermal_accumulation(
    n_pulses_max, delta_t_single, l_heat, l_between, t_ambient_k
):
    """Multi-pulse thermal accumulation — JIT-accelerated."""
    t_accum = np.zeros(n_pulses_max)
    for i in range(n_pulses_max):
        contributions = 0.0
        for j in range(i + 1):
            n_elapsed = i - j
            if n_elapsed == 0:
                contributions += delta_t_single
            else:
                denom = math.sqrt(l_heat ** 2 + n_elapsed * l_between ** 2)
                if denom > 0.0:
                    contributions += delta_t_single * l_heat / denom
        t_accum[i] = t_ambient_k + contributions
    return t_accum


@jit
def _nonlinear_propagation(
    n_z, dz_cm, alpha_linear_cm, mpa_coeff, photon_order,
    n2_cm2_w, irradiance_0, pulse_width_s, photon_j
):
    """Depth-resolved nonlinear propagation — JIT-accelerated."""
    irr = np.zeros(n_z)
    dn = np.zeros(n_z)
    carriers = np.zeros(n_z)
    irr[0] = irradiance_0

    for i in range(1, n_z):
        I = irr[i - 1]
        dI_linear = -alpha_linear_cm * I * dz_cm
        dI_mpa = 0.0
        if photon_order > 1 and mpa_coeff > 0.0:
            dI_mpa = -mpa_coeff * I ** photon_order * dz_cm
        irr[i] = max(I + dI_linear + dI_mpa, 0.0)
        dn[i] = n2_cm2_w * irr[i]
        if photon_order > 0 and photon_j > 0.0:
            abs_rate = abs(dI_mpa) * 1e4
            carriers[i] = carriers[i - 1] + abs_rate * pulse_width_s / (
                photon_order * photon_j
            ) * (dz_cm / 100.0)
    return irr, dn, carriers


@jit
def _material_propagation_loop(
    n_points, z_mat_m, area_cm2, peak_power_w_init, pulse_energy_j_init,
    alpha_cm, beta_cm_per_w
):
    """Core material propagation loop — JIT-accelerated."""
    irradiance_z = np.zeros(n_points)
    fluence_z = np.zeros(n_points)
    power_track = peak_power_w_init
    energy_track = pulse_energy_j_init

    for i in range(n_points):
        area_i = area_cm2[i]
        if area_i <= 0.0:
            continue

        irradiance_z[i] = power_track / area_i if power_track > 0.0 else 0.0
        fluence_z[i] = energy_track / area_i if energy_track > 0.0 else 0.0

        if i == n_points - 1:
            break

        dz_cm = (z_mat_m[i + 1] - z_mat_m[i]) * 100.0
        i_peak = irradiance_z[i]

        if alpha_cm > 0.0:
            lin_factor = math.exp(-alpha_cm * dz_cm)
            l_eff_cm = (1.0 - lin_factor) / alpha_cm
        else:
            lin_factor = 1.0
            l_eff_cm = dz_cm

        if beta_cm_per_w > 0.0 and i_peak > 0.0:
            i_out = i_peak * lin_factor / (1.0 + beta_cm_per_w * i_peak * l_eff_cm)
        else:
            i_out = i_peak * lin_factor

        step_factor = i_out / i_peak if i_peak > 0.0 else 1.0
        power_track *= step_factor
        energy_track *= step_factor

    return irradiance_z, fluence_z, power_track, energy_track


@jit(parallel=True)
def _transfer_matrix_stack(wavelengths_m, n_layers, d_layers_m, theta_rad, polarization_s):
    """Transfer matrix method for multilayer coatings — JIT-accelerated.

    Computes reflectance for each wavelength across a layer stack.
    polarization_s: 1.0 for s-pol, 0.0 for p-pol.
    """
    n_wl = len(wavelengths_m)
    reflectance = np.empty(n_wl)
    n_ly = len(n_layers)

    for w in _prange(n_wl):
        lam = wavelengths_m[w]
        # Initialize transfer matrix as identity
        M00_r, M00_i = 1.0, 0.0
        M01_r, M01_i = 0.0, 0.0
        M10_r, M10_i = 0.0, 0.0
        M11_r, M11_i = 1.0, 0.0

        for j in range(n_ly):
            n_j = n_layers[j]
            cos_t = math.sqrt(max(1.0 - (math.sin(theta_rad) / n_j) ** 2, 0.0))
            if polarization_s > 0.5:
                eta = n_j * cos_t
            else:
                eta = n_j / cos_t

            delta = 2.0 * math.pi * n_j * d_layers_m[j] * cos_t / lam
            cd = math.cos(delta)
            sd = math.sin(delta)

            # Layer matrix: [[cos(d), i*sin(d)/eta], [i*eta*sin(d), cos(d)]]
            L00_r, L00_i = cd, 0.0
            L01_r, L01_i = 0.0, sd / eta
            L10_r, L10_i = 0.0, eta * sd
            L11_r, L11_i = cd, 0.0

            # Matrix multiply M = M @ L (complex)
            a_r = M00_r * L00_r - M00_i * L00_i + M01_r * L10_r - M01_i * L10_i
            a_i = M00_r * L00_i + M00_i * L00_r + M01_r * L10_i + M01_i * L10_r
            b_r = M00_r * L01_r - M00_i * L01_i + M01_r * L11_r - M01_i * L11_i
            b_i = M00_r * L01_i + M00_i * L01_r + M01_r * L11_i + M01_i * L11_r
            c_r = M10_r * L00_r - M10_i * L00_i + M11_r * L10_r - M11_i * L10_i
            c_i = M10_r * L00_i + M10_i * L00_r + M11_r * L10_i + M11_i * L10_r
            d_r = M10_r * L01_r - M10_i * L01_i + M11_r * L11_r - M11_i * L11_i
            d_i = M10_r * L01_i + M10_i * L01_r + M11_r * L11_i + M11_i * L11_r

            M00_r, M00_i = a_r, a_i
            M01_r, M01_i = b_r, b_i
            M10_r, M10_i = c_r, c_i
            M11_r, M11_i = d_r, d_i

        # Fresnel reflection coefficient r = (M00 - M11) / (M00 + M11)
        # (simplified for real substrate = 1.0)
        num_r = M00_r + M01_r - M10_r - M11_r
        num_i = M00_i + M01_i - M10_i - M11_i
        den_r = M00_r + M01_r + M10_r + M11_r
        den_i = M00_i + M01_i + M10_i + M11_i

        den_sq = den_r * den_r + den_i * den_i
        if den_sq > 0.0:
            r_r = (num_r * den_r + num_i * den_i) / den_sq
            r_i = (num_i * den_r - num_r * den_i) / den_sq
            reflectance[w] = r_r * r_r + r_i * r_i
        else:
            reflectance[w] = 0.0

    return reflectance


@jit(parallel=True)
def _monte_carlo_retirement_paths(
    n_sims, n_years, returns_mean, returns_std,
    start_balance, annual_withdrawal, fee_rate, seed
):
    """Monte Carlo retirement simulation — JIT-accelerated.

    Returns (balances, ruin_flags) arrays.
    """
    balances = np.zeros((n_sims, n_years))
    ruin_year = np.full(n_sims, -1, dtype=np.int64)

    for sim in _prange(n_sims):
        # Simple LCG PRNG (numba-compatible, seeded per simulation)
        rng_state = np.uint64(seed + sim * 6364136223846793005)
        bal = start_balance
        ruined = False
        for yr in range(n_years):
            if ruined or bal <= 0.0:
                balances[sim, yr] = 0.0
                if not ruined:
                    ruin_year[sim] = yr
                    ruined = True
                continue

            # Box-Muller from LCG
            rng_state = rng_state * np.uint64(6364136223846793005) + np.uint64(1442695040888963407)
            u1 = (np.float64(rng_state) / np.float64(np.uint64(18446744073709551615))) * 0.99998 + 0.00001
            rng_state = rng_state * np.uint64(6364136223846793005) + np.uint64(1442695040888963407)
            u2 = (np.float64(rng_state) / np.float64(np.uint64(18446744073709551615))) * 0.99998 + 0.00001
            z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

            ret = returns_mean + returns_std * z
            bal = bal * (1.0 + ret - fee_rate) - annual_withdrawal
            if bal < 0.0:
                bal = 0.0
                ruin_year[sim] = yr
                ruined = True
            balances[sim, yr] = bal

    return balances, ruin_year


# ══════════════════════════════════════════════════════════════════
#  Streamlit admin widget for compute info
# ══════════════════════════════════════════════════════════════════

def render_compute_info():
    """Render compute backend info in a Streamlit expander."""
    try:
        import streamlit as st
    except ImportError:
        return

    info = backend_info()
    with st.expander("⚡ Compute Backend", expanded=False):
        backend = info["backend"]
        if backend == "cupy":
            st.success(f"🚀 GPU Accelerated — {info.get('gpu_name', 'CUDA')}")
            st.caption(f"CuPy {info.get('cupy_version', '?')} | "
                      f"VRAM: {info.get('gpu_memory_mb', 0):.0f} MB")
        elif backend == "numba":
            st.info(f"⚡ Numba JIT — {info.get('numba_num_threads', '?')} threads")
            st.caption(f"Numba {info.get('numba_version', '?')}")
        else:
            st.warning("🐢 NumPy only — install numba for 10-100× speedup")
        st.caption(f"NumPy {info['numpy_version']}")
