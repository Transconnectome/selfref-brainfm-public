"""ICC(2,1): two-way random effects, absolute agreement, single measurement (Shrout & Fleiss 1979)."""
from __future__ import annotations

import numpy as np


def icc_2_1(x: np.ndarray) -> float:
    """`x` is subjects x sessions with no missing values."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 2:
        raise ValueError("x must be a 2-D array with >= 2 subjects and >= 2 sessions")
    if not np.isfinite(x).all():
        raise ValueError("x must not contain missing values")
    n, k = x.shape
    grand = x.mean()
    ss_rows = k * ((x.mean(axis=1) - grand) ** 2).sum()
    ss_cols = n * ((x.mean(axis=0) - grand) ** 2).sum()
    ss_err = ((x - grand) ** 2).sum() - ss_rows - ss_cols
    msr = ss_rows / (n - 1)
    msc = ss_cols / (k - 1)
    mse = ss_err / ((n - 1) * (k - 1))
    return float((msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n))
