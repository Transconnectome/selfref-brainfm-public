"""Recovery tests and negative controls for task B (PLAN §5 B, §10 gates, 3-seed rule).

CI choice (prereg item for the PI): subject-cluster bootstrap of mean e_i, where
e_i = d_i - d_i^HRF is the per-subject contribution to Δ̄_id - Δ̄_id^HRF.
"""
import numpy as np
import pytest

from selfref.analysis.identifiability import delta_id, hrf_controlled_delta, min_gap_trs
from selfref.sim.b import BParams, simulate
from selfref.stats.bootstrap import cluster_bootstrap, percentile_interval
from selfref.stats.equivalence import Verdict, classify_effect

SESOI = 0.02  # proposed value in PLAN §5 B; fixed in week-1 prereg
SEEDS = [0, 1, 2]


def run_b(params: BParams, seed: int):
    rng = np.random.default_rng(seed)
    data = simulate(params, rng)
    out = hrf_controlled_delta(data.run1, data.run2, data.checker, data.checker_design, params.tr, 20, 10, rng)
    e = out["e"]
    reps = cluster_bootstrap(lambda idx: e[idx].mean(), e, n_boot=2000, rng=rng)
    verdict = classify_effect(e.mean(), percentile_interval(reps, 0.95), percentile_interval(reps, 0.90), SESOI)
    return out, verdict, percentile_interval(reps, 0.95)


def test_min_gap_matches_plan():
    assert min_gap_trs(20, 2.1) == 28


def test_delta_id_is_zero_for_pure_noise():
    rng = np.random.default_rng(0)
    r1 = rng.standard_normal((22, 288, 30))
    r2 = rng.standard_normal((22, 288, 30))
    assert abs(delta_id(r1, r2, 20, 10, 28).mean()) < 0.003


@pytest.mark.parametrize("seed", SEEDS)
def test_negative_control_static_and_hrf_only(seed):
    """Static FC fingerprint + subject HRF lag/gain + window-varying drive, no moment effect."""
    out, verdict, ci = run_b(BParams(), seed)
    # The confound is real: raw Δ̄_id is positive without any moment-specific signal ...
    assert out["d"].mean() > 0.01
    # ... and the HRF-surrogate correction removes it.
    assert not verdict.is_support
    assert ci.lo < 0 < ci.hi


@pytest.mark.parametrize("seed", SEEDS)
def test_recovers_planted_moment_specificity(seed):
    out, verdict, ci = run_b(BParams(moment_amp=0.3), seed)
    assert ci.lo > 0
    assert out["e"].mean() >= SESOI
    assert verdict in (Verdict.SUPPORT_STRONG, Verdict.SUPPORT_WEAK)


@pytest.mark.parametrize("seed", SEEDS)
def test_checker_lag_estimates_are_close(seed):
    rng = np.random.default_rng(seed)
    p = BParams()
    data = simulate(p, rng)
    out = hrf_controlled_delta(data.run1, data.run2, data.checker, data.checker_design, p.tr, 20, 10, rng)
    assert np.abs(out["lag_hat"] - data.true_lag).mean() < 0.3
