"""Cluster (subject) bootstrap percentile intervals."""
from __future__ import annotations

from typing import Callable, Sequence

import numpy as np

from selfref.stats.equivalence import Interval


def cluster_bootstrap(
    statistic: Callable[[np.ndarray], float],
    clusters: Sequence,
    n_boot: int = 2000,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Resample whole clusters with replacement.

    `statistic` receives an index array into `clusters` (with repeats) and returns a scalar.
    Returns the n_boot bootstrap replicates.
    """
    rng = np.random.default_rng() if rng is None else rng
    n = len(clusters)
    reps = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        reps[b] = statistic(rng.integers(0, n, size=n))
    return reps


def percentile_interval(reps: np.ndarray, level: float) -> Interval:
    reps = np.asarray(reps, dtype=np.float64)
    reps = reps[np.isfinite(reps)]
    if reps.size == 0:
        raise ValueError("no finite bootstrap replicates")
    a = (1 - level) / 2
    lo, hi = np.quantile(reps, [a, 1 - a])
    return Interval(float(lo), float(hi))
