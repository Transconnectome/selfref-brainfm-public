"""Recovery tests and negative controls for task F (PLAN §5 F, 3-seed rule).

Estimator bias is checked at large N (150-400) so sampling noise does not hide it. The
planned-N behaviour (17 cross-session, 22 within-session) is a power question for the
week-1 prereg; see docs/stage0/S0_findings.md.
CI choice (prereg item): subject-cluster bootstrap of the residual ICC(2,1).
"""
import numpy as np
import pytest

from selfref.analysis.autoregression import f_indices, residualize
from selfref.sim.f import FParams, simulate
from selfref.stats.bootstrap import cluster_bootstrap, percentile_interval
from selfref.stats.equivalence import classify_benchmark
from selfref.stats.icc import icc_2_1

SEEDS = [0, 1, 2]
BENCHMARK = 0.4  # proposed ICC in PLAN §5 F


def run_f(params: FParams, seed: int):
    rng = np.random.default_rng(seed)
    x = simulate(params, rng)
    o = f_indices(x, params.tr)
    res = residualize(o["D"], [o["slope"], o["lowfreq"], o["isc"], o["sd"]])
    return o, res, rng


@pytest.mark.parametrize("seed", SEEDS)
def test_null_residual_icc_near_zero(seed):
    # N=150 gave -0.15..0.20 across seeds (sampling SE of ICC is ~0.1 there); 400 isolates bias
    _, res, _ = run_f(FParams(n_sub=400), seed)
    assert abs(icc_2_1(res)) < 0.1


@pytest.mark.parametrize("seed", SEEDS)
def test_control_spectral_only_trait_is_removed(seed):
    o, res, _ = run_f(FParams(n_sub=150, phi_trait_sd=0.15), seed)
    assert icc_2_1(o["D"]) > 0.2  # the raw index is trait-like ...
    assert icc_2_1(res) < 0.15  # ... only because of the spectrum


@pytest.mark.parametrize("seed", SEEDS)
def test_control_spectral_only_trait_not_support_at_planned_n(seed):
    """Weak check: at N=17 nothing reaches support (see findings); the large-N control discriminates."""
    _, res, rng = run_f(FParams(n_sub=17, phi_trait_sd=0.15), seed)
    reps = cluster_bootstrap(lambda idx: icc_2_1(res[idx]), res, 1000, rng)
    assert not classify_benchmark(percentile_interval(reps, 0.95), BENCHMARK).is_support


@pytest.mark.parametrize("seed", SEEDS)
def test_recovers_planted_coupling_trait(seed):
    _, res, _ = run_f(FParams(n_sub=150, c_trait_sd=0.3, phi_mean=0.3), seed)
    assert icc_2_1(res) > 0.2
