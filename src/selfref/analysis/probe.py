"""Task D: does pre-probe EEG add to the prediction of the self rating (PLAN §5 D)?

- Target: the self rating, centered within subject. Predictors are centered within subject too.
- Reduced model: probe order (position in run, session, time-on-task) + the other 12 items.
- Full model: reduced + EEG features.
- Both are ridge models under nested CV: outer leave-one-subject-out; inner 5-fold split by
  subject inside the training subjects picks the penalty. The statistic is ΔR² computed on
  all pooled held-out predictions.
- p-value: Freedman–Lane, permuting reduced-model residuals within subject and rerunning the
  whole nested CV each time. Probe-number exchange across runs is not implemented; whether to
  allow it is a PI decision (PLAN §4.1).
- CI (prereg choice for the PI): subject-cluster bootstrap of ΔR² over the pooled held-out
  predictions, with no refitting.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ALPHAS = np.logspace(-2, 4, 13)


def center_within(values: np.ndarray, groups: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    out = values.copy()
    for g in np.unique(groups):
        m = groups == g
        out[m] = values[m] - values[m].mean(axis=0)
    return out


def _ridge_path(X: np.ndarray, y: np.ndarray, alphas: np.ndarray) -> np.ndarray:
    """Coefficients for every alpha (features x alphas), no intercept (data are centered)."""
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    uy = U.T @ y
    d = s[:, None] / (s[:, None] ** 2 + alphas[None, :])
    return Vt.T @ (d * uy[:, None])


def _inner_alpha(X, y, groups, alphas, n_folds, rng):
    subs = rng.permutation(np.unique(groups))
    folds = np.array_split(subs, n_folds)
    sse = np.zeros(alphas.size)
    for f in folds:
        test = np.isin(groups, f)
        B = _ridge_path(X[~test], y[~test], alphas)
        sse += ((y[test, None] - X[test] @ B) ** 2).sum(0)
    return alphas[np.argmin(sse)]


def nested_cv_predictions(X, y, groups, rng, alphas=ALPHAS, n_inner=5) -> np.ndarray:
    pred = np.empty_like(y)
    for g in np.unique(groups):
        test = groups == g
        a = _inner_alpha(X[~test], y[~test], groups[~test], alphas, n_inner, rng)
        pred[test] = X[test] @ _ridge_path(X[~test], y[~test], np.array([a]))[:, 0]
    return pred


def r2(y: np.ndarray, pred: np.ndarray) -> float:
    return float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def design(df: pd.DataFrame, eeg: np.ndarray, target: str = "self") -> dict[str, np.ndarray]:
    groups = df["subject"].to_numpy()
    items = [c for c in df.columns if c not in ("subject", "session", "run", "position", "time_on_task", target)]
    order = pd.get_dummies(df["position"], prefix="pos", drop_first=True, dtype=float)
    Z = np.column_stack([order.to_numpy(), df[["session", "time_on_task"]].to_numpy(float), df[items].to_numpy(float)])
    Z = center_within(Z, groups)
    E = center_within(eeg, groups)
    E = E / np.maximum(E.std(axis=0), 1e-12)
    y = center_within(df[target].to_numpy(float), groups)
    return {"y": y, "Z": Z, "X": np.column_stack([Z, E]), "groups": groups}


def delta_r2(d: dict[str, np.ndarray], rng: np.random.Generator, y: np.ndarray | None = None) -> dict:
    y = d["y"] if y is None else y
    seed = int(rng.integers(2**31))
    # the same inner splits for both models
    p_red = nested_cv_predictions(d["Z"], y, d["groups"], np.random.default_rng(seed))
    p_full = nested_cv_predictions(d["X"], y, d["groups"], np.random.default_rng(seed))
    return {"delta": r2(y, p_full) - r2(y, p_red), "pred_red": p_red, "pred_full": p_full, "y": y}


def bootstrap_delta(res: dict, groups: np.ndarray, n_boot: int, rng: np.random.Generator) -> np.ndarray:
    subs = np.unique(groups)
    idx_by = {s: np.flatnonzero(groups == s) for s in subs}
    reps = np.empty(n_boot)
    for b in range(n_boot):
        idx = np.concatenate([idx_by[s] for s in rng.choice(subs, subs.size)])
        y = res["y"][idx]
        reps[b] = r2(y, res["pred_full"][idx]) - r2(y, res["pred_red"][idx])
    return reps
