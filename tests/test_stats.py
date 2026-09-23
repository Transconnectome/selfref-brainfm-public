import numpy as np
import pytest

from selfref.stats.bootstrap import cluster_bootstrap, percentile_interval
from selfref.stats.equivalence import Interval, Verdict, classify_benchmark, classify_effect
from selfref.stats.icc import icc_2_1
from selfref.stats.permutation import freedman_lane, permute_within_blocks

S = 0.2


@pytest.mark.parametrize(
    "est, ci95, ci90, expected",
    [
        (0.35, (0.25, 0.45), (0.27, 0.43), Verdict.SUPPORT_STRONG),
        (0.25, (0.05, 0.45), (0.08, 0.42), Verdict.SUPPORT_WEAK),
        (0.02, (-0.12, 0.16), (-0.10, 0.14), Verdict.REJECT),
        (0.10, (-0.05, 0.25), (-0.02, 0.22), Verdict.UNDETERMINED),
        # CI excludes 0 but the point estimate is below SESOI: neither support nor reject.
        (0.15, (0.05, 0.25), (0.07, 0.23), Verdict.UNDETERMINED),
        # Excludes 0 and sits inside the band: a small, real, but unimportant effect.
        (0.05, (0.01, 0.09), (0.02, 0.08), Verdict.REJECT),
    ],
)
def test_classify_effect(est, ci95, ci90, expected):
    assert classify_effect(est, Interval(*ci95), Interval(*ci90), S) is expected


def test_classify_effect_negative_direction_mirrors():
    v = classify_effect(-0.35, Interval(-0.45, -0.25), Interval(-0.43, -0.27), S, direction="negative")
    assert v is Verdict.SUPPORT_STRONG


def test_classify_benchmark():
    assert classify_benchmark(Interval(0.45, 0.8), 0.4) is Verdict.SUPPORT
    assert classify_benchmark(Interval(0.1, 0.35), 0.4) is Verdict.REJECT
    assert classify_benchmark(Interval(0.3, 0.6), 0.4) is Verdict.UNDETERMINED


def test_interval_rejects_reversed_bounds():
    with pytest.raises(ValueError):
        Interval(1.0, 0.0)


def test_icc_perfect_and_zero():
    trait = np.arange(10.0)
    assert icc_2_1(np.column_stack([trait, trait])) == pytest.approx(1.0)
    rng = np.random.default_rng(0)
    x = rng.standard_normal((4000, 2))
    assert abs(icc_2_1(x)) < 0.05


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_icc_recovers_planted_value(seed):
    rng = np.random.default_rng(seed)
    n, true_icc = 3000, 0.6
    trait = rng.standard_normal(n) * np.sqrt(true_icc)
    x = trait[:, None] + rng.standard_normal((n, 2)) * np.sqrt(1 - true_icc)
    assert icc_2_1(x) == pytest.approx(true_icc, abs=0.04)


def test_cluster_bootstrap_interval_covers_mean():
    rng = np.random.default_rng(3)
    vals = rng.normal(1.0, 1.0, size=200)
    reps = cluster_bootstrap(lambda idx: vals[idx].mean(), vals, n_boot=1000, rng=rng)
    ci = percentile_interval(reps, 0.95)
    assert ci.lo < 1.0 < ci.hi


def test_permute_within_blocks_keeps_blocks():
    rng = np.random.default_rng(4)
    blocks = np.repeat([0, 1, 2], 5)
    perm = permute_within_blocks(blocks, rng)
    assert (blocks[perm] == blocks).all()
    assert sorted(perm) == list(range(15))


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_freedman_lane_null_and_effect(seed):
    rng = np.random.default_rng(seed)
    n = 300
    blocks = np.repeat(np.arange(10), 30)
    z = rng.standard_normal(n)
    x = 0.5 * z + rng.standard_normal(n)  # predictor correlated with the nuisance
    Z = np.column_stack([np.ones(n), z])
    X = np.column_stack([Z, x])

    def gain(y):
        r_red = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
        r_full = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
        return (r_red @ r_red - r_full @ r_full) / (y - y.mean()) @ (y - y.mean())

    y_null = z + rng.standard_normal(n)
    _, _, p_null = freedman_lane(y_null, Z, gain, blocks, 199, rng)
    y_eff = z + 0.4 * x + rng.standard_normal(n)
    _, _, p_eff = freedman_lane(y_eff, Z, gain, blocks, 199, rng)
    assert p_eff < 0.01
    assert p_null > 0.01
