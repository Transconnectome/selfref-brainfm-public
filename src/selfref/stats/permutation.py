"""Freedman–Lane permutation for the added value of a predictor block.

Reduced model: y ~ Z. Full model: y ~ Z + X. Under H0, the residuals of the reduced
model are exchangeable within each block (e.g. within subject). Each permutation builds
y* = Z-fit + permuted residuals and recomputes the statistic on y* (Freedman & Lane 1983;
Winkler et al. 2014).
"""
from __future__ import annotations

from typing import Callable

import numpy as np


def permute_within_blocks(blocks: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Index array that permutes positions only within each block label."""
    blocks = np.asarray(blocks)
    idx = np.arange(blocks.size)
    out = idx.copy()
    for b in np.unique(blocks):
        pos = idx[blocks == b]
        out[pos] = rng.permutation(pos)
    return out


def freedman_lane(
    y: np.ndarray,
    Z: np.ndarray,
    statistic: Callable[[np.ndarray], float],
    blocks: np.ndarray,
    n_perm: int,
    rng: np.random.Generator | None = None,
) -> tuple[float, np.ndarray, float]:
    """Return (observed statistic, null replicates, one-sided p for 'larger is more extreme').

    `statistic(y)` must compute the full-vs-reduced comparison for outcome `y` with the
    predictors held fixed. `Z` should include an intercept column if one is wanted.
    """
    rng = np.random.default_rng() if rng is None else rng
    y = np.asarray(y, dtype=np.float64)
    Z = np.asarray(Z, dtype=np.float64)
    beta, *_ = np.linalg.lstsq(Z, y, rcond=None)
    fitted = Z @ beta
    resid = y - fitted
    observed = statistic(y)
    null = np.empty(n_perm, dtype=np.float64)
    for i in range(n_perm):
        null[i] = statistic(fitted + resid[permute_within_blocks(blocks, rng)])
    p = (1 + np.sum(null >= observed)) / (1 + n_perm)
    return float(observed), null, float(p)
