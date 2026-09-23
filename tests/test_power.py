import numpy as np

from selfref.analysis.variance import bootstrap_r2, metadata_r2, metadata_verdict
from selfref.sim.a import AParams, simulate
from selfref.sim.power import outcome_probabilities
from selfref.stats.bootstrap import percentile_interval


def _run_a(params):
    def run(seed):
        rng = np.random.default_rng(seed)
        df, P, Cf, _ = simulate(params, rng)
        res = metadata_r2(df, P, Cf, rng)
        reps = bootstrap_r2(res, 300, rng)
        return metadata_verdict(res["r2"], percentile_interval(reps, 0.95), percentile_interval(reps, 0.90), 0.02)

    return run


def test_outcome_probabilities_smoke():
    null = outcome_probabilities(_run_a(AParams()), range(20))
    eff = outcome_probabilities(_run_a(AParams(meta_amp=0.3)), range(20))
    assert null["n"] == 20 and abs(sum(v for k, v in null.items() if k not in ("n", "any_support")) - 1) < 1e-9
    assert null["any_support"] <= 0.1
    assert eff["any_support"] >= 0.9
