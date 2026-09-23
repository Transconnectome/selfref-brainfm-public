"""Recovery tests and negative controls for task A, metadata path (PLAN §5 A, 3-seed rule)."""
import numpy as np
import pytest

from selfref.analysis.variance import bootstrap_r2, metadata_r2, metadata_verdict
from selfref.sim.a import AParams, simulate
from selfref.stats.bootstrap import percentile_interval
from selfref.stats.equivalence import Interval, Verdict

SESOI = 0.02  # proposed cross-validated R² in PLAN §5 A
SEEDS = [0, 1, 2]


def run_a(params: AParams, seed: int):
    rng = np.random.default_rng(seed)
    df, P, Cf, truth = simulate(params, rng)
    res = metadata_r2(df, P, Cf, rng)
    reps = bootstrap_r2(res, 1000, rng)
    v = metadata_verdict(res["r2"], percentile_interval(reps, 0.95), percentile_interval(reps, 0.90), SESOI)
    return res, v, truth, df


def test_missingness_matches_stage0():
    _, _, _, df = run_a(AParams(), 0)
    assert 0.48 < 1 - len(df) / (116 * 49) < 0.55  # V2: 51.7% of relevance ratings are n/a


def test_metadata_path_never_rejects():
    assert metadata_verdict(0.0, Interval(-0.01, 0.01), Interval(-0.005, 0.005), SESOI) is Verdict.UNDETERMINED


@pytest.mark.parametrize("seed", SEEDS)
def test_null_is_not_support(seed):
    _, v, _, _ = run_a(AParams(), seed)
    assert v is Verdict.UNDETERMINED


@pytest.mark.parametrize("seed", SEEDS)
def test_control_interaction_invisible_to_metadata(seed):
    res, v, _, _ = run_a(AParams(free_amp=0.7), seed)
    assert abs(res["r2"]) < 0.01
    assert not v.is_support


@pytest.mark.parametrize("seed", SEEDS)
def test_recovers_planted_metadata_interaction(seed):
    res, v, _, _ = run_a(AParams(meta_amp=0.3), seed)
    assert res["r2"] > SESOI
    assert v is Verdict.SUPPORT_STRONG


@pytest.mark.parametrize("seed", SEEDS)
def test_position_is_absorbed_into_clip_effect(seed):
    """Same order for everyone: the estimated clip effect is clip + position drift, not clip alone."""
    res, _, truth, _ = run_a(AParams(drift=0.8), seed)
    b = res["clip_effect"]
    with_drift = np.corrcoef(b, truth["clip"] + truth["drift_by_clip"])[0, 1]
    clip_only = np.corrcoef(b, truth["clip"])[0, 1]
    assert with_drift > 0.95
    assert clip_only < with_drift - 0.1
