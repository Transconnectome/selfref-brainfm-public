"""Task F index (PLAN §5 F).

For one subject-session with network time series x (TRs x parcels) and the mean of the
other subjects in the same session/stimulus o (TRs x parcels):
    R²_self   out-of-sample R² of ridge predicting x(t+h) from x(t-k+1..t)   (all parcels' past)
    R²_others out-of-sample R² of ridge predicting x(t+h) from o(t-k+1..t)
    D = R²_self - R²_others
Cross-validation is by contiguous time blocks inside the run (PLAN §12.2).

Spectral control: D is regressed on per subject-session descriptors (aperiodic slope,
low-frequency power ratio, ISC with the others' mean, signal SD as a tSNR stand-in); the
ICC(2,1) of the residual across sessions is the H4 statistic.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import welch

ALPHAS = np.logspace(-2, 3, 11)


def lagged(x: np.ndarray, k: int, h: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Predictors from lags 0..k-1 before t, target x(t+h). Returns (X, Y, t index)."""
    T = x.shape[0]
    t = np.arange(k - 1, T - h)
    X = np.concatenate([x[t - j] for j in range(k)], axis=1)
    return X, x[t + h], t


def block_cv_r2(X: np.ndarray, Y: np.ndarray, n_blocks: int = 5, alphas: np.ndarray = ALPHAS, gap: int = 5) -> float:
    """Pooled out-of-sample R² over contiguous blocks; alpha chosen by inner block CV."""
    n = X.shape[0]
    edges = np.linspace(0, n, n_blocks + 1).astype(int)
    pred = np.empty_like(Y)
    for b in range(n_blocks):
        test = np.zeros(n, bool)
        test[edges[b] : edges[b + 1]] = True
        guard = np.zeros(n, bool)
        guard[max(0, edges[b] - gap) : min(n, edges[b + 1] + gap)] = True
        train = ~guard
        Xtr, Ytr = X[train], Y[train]
        mx, my = Xtr.mean(0), Ytr.mean(0)
        a = _choose_alpha(Xtr - mx, Ytr - my, alphas)
        B = _ridge(Xtr - mx, Ytr - my, a)
        pred[test] = (X[test] - mx) @ B + my
    ss_res = ((Y - pred) ** 2).sum()
    ss_tot = ((Y - Y.mean(0)) ** 2).sum()
    return float(1 - ss_res / ss_tot)


def _ridge(X, Y, a):
    return np.linalg.solve(X.T @ X + a * np.eye(X.shape[1]), X.T @ Y)


def _choose_alpha(X, Y, alphas, n_folds=3):
    n = X.shape[0]
    edges = np.linspace(0, n, n_folds + 1).astype(int)
    sse = np.zeros(alphas.size)
    for f in range(n_folds):
        te = np.zeros(n, bool)
        te[edges[f] : edges[f + 1]] = True
        for ai, a in enumerate(alphas):
            B = _ridge(X[~te], Y[~te], a)
            sse[ai] += ((Y[te] - X[te] @ B) ** 2).sum()
    return alphas[np.argmin(sse)]


def spectral_descriptors(x: np.ndarray, tr: float) -> tuple[float, float]:
    """Aperiodic slope (log-log PSD fit) and low-frequency (<0.05 Hz) power ratio, parcel-averaged."""
    f, pxx = welch(x, fs=1 / tr, nperseg=min(64, x.shape[0]), axis=0)
    keep = f > 0
    lf, lp = np.log(f[keep]), np.log(pxx[keep].mean(axis=1))
    slope = np.polyfit(lf, lp, 1)[0]
    low = pxx[(f > 0) & (f < 0.05)].sum() / pxx[keep].sum()
    return float(slope), float(low)


def f_indices(x: np.ndarray, tr: float, k: int = 5, h: int = 3) -> dict[str, np.ndarray]:
    """x: subjects x sessions x TRs x parcels. Returns D, R² parts and covariates, each subjects x sessions."""
    n, S = x.shape[:2]
    out = {key: np.empty((n, S)) for key in ("D", "r2_self", "r2_others", "slope", "lowfreq", "isc", "sd")}
    for r in range(S):
        total = x[:, r].sum(0)
        for i in range(n):
            xi = x[i, r]
            oi = (total - xi) / (n - 1)
            Xs, Y, _ = lagged(xi, k, h)
            Xo, _, _ = lagged(oi, k, h)
            out["r2_self"][i, r] = block_cv_r2(Xs, Y)
            out["r2_others"][i, r] = block_cv_r2(Xo, Y)
            out["slope"][i, r], out["lowfreq"][i, r] = spectral_descriptors(xi, tr)
            out["isc"][i, r] = np.mean([np.corrcoef(xi[:, p], oi[:, p])[0, 1] for p in range(xi.shape[1])])
            out["sd"][i, r] = xi.std()
    out["D"] = out["r2_self"] - out["r2_others"]
    return out


def residualize(D: np.ndarray, covariates: list[np.ndarray]) -> np.ndarray:
    """Pooled OLS of D (subjects x sessions) on covariates of the same shape; returns residuals."""
    y = D.ravel()
    C = np.column_stack([np.ones_like(y)] + [c.ravel() for c in covariates])
    beta, *_ = np.linalg.lstsq(C, y, rcond=None)
    return (y - C @ beta).reshape(D.shape)
