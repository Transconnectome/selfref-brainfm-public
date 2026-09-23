"""Recovery tests and negative controls for task D (PLAN §5 D, 3-seed rule)."""
import numpy as np
import pytest

from selfref.analysis.probe import bootstrap_delta, delta_r2, design
from selfref.sim.d import DParams, simulate
from selfref.stats.bootstrap import percentile_interval
from selfref.stats.equivalence import Verdict, classify_effect
from selfref.stats.permutation import freedman_lane

SESOI = 0.01  # proposed ΔR² in PLAN §5 D
SEEDS = [0, 1, 2]


def run_d(params: DParams, seed: int):
    rng = np.random.default_rng(seed)
    df, X = simulate(params, rng)
    d = design(df, X)
    res = delta_r2(d, rng)
    reps = bootstrap_delta(res, d["groups"], 1000, rng)
    v = classify_effect(res["delta"], percentile_interval(reps, 0.95), percentile_interval(reps, 0.90), SESOI)
    return res, v


def test_structure_matches_stage0():
    df, X = simulate(DParams(), np.random.default_rng(0))
    assert len(df) == 840
    assert df.groupby("subject")["session"].nunique().sum() == 47
    assert df.groupby(["subject", "session"])["run"].nunique().sum() == 140
    assert df["self"].between(1, 10).all()
    assert X.shape == (840, 186)


@pytest.mark.parametrize("seed", SEEDS)
def test_null_is_not_support(seed):
    _, v = run_d(DParams(), seed)
    assert not v.is_support


@pytest.mark.parametrize("seed", SEEDS)
def test_control_shared_time_on_task_drift(seed):
    """EEG and self both drift with time-on-task; the reduced model has the order covariates."""
    _, v = run_d(DParams(eeg_drift=0.1, self_drift=0.8), seed)
    assert not v.is_support


@pytest.mark.parametrize("seed", SEEDS)
def test_control_eeg_tracks_arousal_only(seed):
    """EEG carries arousal only; self correlates with arousal (0.5); arousal rating is in the reduced model."""
    _, v = run_d(DParams(eeg_arou=0.1, rho_self_arou=0.5), seed)
    assert not v.is_support


@pytest.mark.parametrize("seed", SEEDS)
def test_recovers_planted_self_signal(seed):
    res, v = run_d(DParams(eeg_self=0.05), seed)
    assert res["delta"] > 0.05
    assert v is Verdict.SUPPORT_STRONG


@pytest.mark.slow
def test_freedman_lane_separates_null_and_effect():
    def pvalue(params, seed):
        rng = np.random.default_rng(seed)
        df, X = simulate(params, rng)
        d = design(df, X)
        stat_rng = np.random.default_rng(seed + 100)
        stat = lambda y: delta_r2(d, stat_rng, y=y)["delta"]
        _, _, p = freedman_lane(d["y"], d["Z"], stat, d["groups"], n_perm=19, rng=rng)
        return p

    assert pvalue(DParams(eeg_self=0.05), 0) == pytest.approx(1 / 20)
    assert pvalue(DParams(), 0) > 0.05
