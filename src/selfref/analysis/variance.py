"""Task A (PLAN §5 A), metadata path.

1. Additive person + clip fit (alternating least squares on the observed cells). Without
   repeated presentations the person x clip interaction and rating noise cannot be
   separated, so their sum is reported descriptively only. Because every subject saw the
   clips in the same order, the clip effect also absorbs presentation position.
2. The residual r_ic is predicted from person-feature x clip-feature products by ridge,
   cross-validated by clip folds (generalisation to unseen clips).
3. Verdict asymmetry (PLAN §5 A): only support is possible; anything else is undetermined.
   CI (prereg choice for the PI): clip-cluster bootstrap of the pooled held-out R².
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from selfref.stats.equivalence import Interval, Verdict, classify_effect

ALPHAS = np.logspace(-2, 4, 13)


def additive_fit(df: pd.DataFrame, n_iter: int = 50) -> tuple[np.ndarray, np.ndarray, float, np.ndarray]:
    s = df["subject"].to_numpy()
    c = df["clip"].to_numpy()
    y = df["rating"].to_numpy(float)
    mu = y.mean()
    a = np.zeros(s.max() + 1)
    b = np.zeros(c.max() + 1)
    for _ in range(n_iter):
        a = np.bincount(s, y - mu - b[c], minlength=a.size) / np.maximum(np.bincount(s, minlength=a.size), 1)
        b = np.bincount(c, y - mu - a[s], minlength=b.size) / np.maximum(np.bincount(c, minlength=b.size), 1)
        b -= b.mean()
    resid = y - mu - a[s] - b[c]
    return a, b, mu, resid


def interaction_features(df, person_feat, clip_feat) -> np.ndarray:
    P = person_feat[df["subject"].to_numpy()]
    Cf = clip_feat[df["clip"].to_numpy()]
    X = (P[:, :, None] * Cf[:, None, :]).reshape(len(df), -1)
    return X - X.mean(0)


def _ridge_path(X, y, alphas):
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    d = s[:, None] / (s[:, None] ** 2 + alphas[None, :])
    return Vt.T @ (d * (U.T @ y)[:, None])


def clip_cv_predictions(X, r, clips, rng, n_folds=7, alphas=ALPHAS) -> np.ndarray:
    uniq = rng.permutation(np.unique(clips))
    folds = np.array_split(uniq, n_folds)
    pred = np.empty_like(r)
    for f in folds:
        te = np.isin(clips, f)
        tr_clips = np.unique(clips[~te])
        inner = np.array_split(rng.permutation(tr_clips), 5)
        sse = np.zeros(alphas.size)
        for g in inner:
            ite = np.isin(clips, g) & ~te
            itr = ~te & ~ite
            sse += ((r[ite, None] - X[ite] @ _ridge_path(X[itr], r[itr], alphas)) ** 2).sum(0)
        a = alphas[np.argmin(sse)]
        pred[te] = X[te] @ _ridge_path(X[~te], r[~te], np.array([a]))[:, 0]
    return pred


def metadata_r2(df, person_feat, clip_feat, rng) -> dict:
    _, b, _, resid = additive_fit(df)
    X = interaction_features(df, person_feat, clip_feat)
    clips = df["clip"].to_numpy()
    pred = clip_cv_predictions(X, resid, clips, rng)
    r2 = 1 - ((resid - pred) ** 2).sum() / (resid**2).sum()
    return {"r2": float(r2), "pred": pred, "resid": resid, "clips": clips, "clip_effect": b}


def bootstrap_r2(res: dict, n_boot: int, rng: np.random.Generator) -> np.ndarray:
    clips = res["clips"]
    uniq = np.unique(clips)
    idx_by = {c: np.flatnonzero(clips == c) for c in uniq}
    reps = np.empty(n_boot)
    for k in range(n_boot):
        idx = np.concatenate([idx_by[c] for c in rng.choice(uniq, uniq.size)])
        r, p = res["resid"][idx], res["pred"][idx]
        reps[k] = 1 - ((r - p) ** 2).sum() / ((r - r.mean()) ** 2).sum()
    return reps


def metadata_verdict(estimate: float, ci95: Interval, ci90: Interval, sesoi: float) -> Verdict:
    v = classify_effect(estimate, ci95, ci90, sesoi)
    return Verdict.UNDETERMINED if v is Verdict.REJECT else v
