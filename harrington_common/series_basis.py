from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


BasisMethod = str


@dataclass(frozen=True)
class BasisConfig:
    method: BasisMethod = "latest"
    recent_n: int = 3
    ewma_span: int = 3


@dataclass(frozen=True)
class BasisSummary:
    method: BasisMethod
    label: str
    value: float | None
    latest: float | None
    count: int


def basis_label(config: BasisConfig) -> str:
    method = config.method.lower()
    if method == "latest":
        return "Latest result"
    if method == "recent_mean":
        return f"Mean of last {max(int(config.recent_n), 1)} results"
    if method == "ewma":
        return f"EWMA (span={max(int(config.ewma_span), 1)})"
    return method


def _coerce_values(values: Sequence[float | int]) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError("values must be one-dimensional")
    return arr[~np.isnan(arr)]


def resolve_basis_value(values: Sequence[float | int], config: BasisConfig | None = None) -> float | None:
    config = config or BasisConfig()
    arr = _coerce_values(values)
    if arr.size == 0:
        return None

    method = config.method.lower()

    if method == "latest":
        return float(arr[-1])

    if method == "recent_mean":
        n = max(int(config.recent_n), 1)
        return float(np.mean(arr[-n:]))

    if method == "ewma":
        span = max(int(config.ewma_span), 1)
        alpha = 2.0 / (span + 1.0)
        out = float(arr[0])
        for x in arr[1:]:
            out = alpha * float(x) + (1.0 - alpha) * out
        return float(out)

    raise ValueError(f"Unsupported basis method: {config.method}")


def summarize_basis(values: Sequence[float | int], config: BasisConfig | None = None) -> BasisSummary:
    config = config or BasisConfig()
    arr = _coerce_values(values)

    if arr.size == 0:
        return BasisSummary(
            method=config.method,
            label=basis_label(config),
            value=None,
            latest=None,
            count=0,
        )

    return BasisSummary(
        method=config.method,
        label=basis_label(config),
        value=resolve_basis_value(arr.tolist(), config=config),
        latest=float(arr[-1]),
        count=int(arr.size),
    )
