"""HRF model, subject-level lag/gain estimation from a block task, and HRF surrogate data (PLAN §5 B).

The HRF is the SPM-style double gamma, shifted by a subject lag (seconds) and scaled by
a subject gain. Subject lag/gain are estimated from the block task (NATVIEW `checker`)
by grid search over lags, using the mean of a set of responsive parcels.

Known limitation (PLAN §5 B.4): lag/gain estimated from visual parcels are applied to
every parcel, so region-specific HRF differences are not removed.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import gamma


def double_gamma(t: np.ndarray, peak: float = 6.0, undershoot: float = 16.0, ratio: float = 1 / 6) -> np.ndarray:
    t = np.asarray(t, dtype=np.float64)
    h = gamma.pdf(t, peak) - ratio * gamma.pdf(t, undershoot)
    h[t < 0] = 0.0
    return h


def hrf_kernel(tr: float, lag: float = 0.0, length_s: float = 32.0) -> np.ndarray:
    """HRF sampled at TR, shifted later by `lag` seconds, unit-sum normalized."""
    t = np.arange(0.0, length_s, tr)
    h = double_gamma(t - lag)
    return h / h.sum()


def convolve(u: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Causal convolution along axis 0, truncated to the input length."""
    u = np.asarray(u, dtype=np.float64)
    n = u.shape[0]
    flat = u.reshape(n, -1)
    out = np.stack([np.convolve(flat[:, j], kernel)[:n] for j in range(flat.shape[1])], axis=1)
    return out.reshape(u.shape)


def convolution_matrix(kernel: np.ndarray, n: int) -> np.ndarray:
    H = np.zeros((n, n))
    for k, v in enumerate(kernel[:n]):
        H += v * np.eye(n, k=-k)
    return H


def deconvolve(y: np.ndarray, kernel: np.ndarray, ridge: float = 1e-2) -> np.ndarray:
    """Ridge deconvolution along axis 0: argmin ||y - H u||^2 + ridge * ||u||^2."""
    y = np.asarray(y, dtype=np.float64)
    n = y.shape[0]
    H = convolution_matrix(kernel, n)
    A = H.T @ H + ridge * np.trace(H.T @ H) / n * np.eye(n)
    return np.linalg.solve(A, H.T @ y.reshape(n, -1)).reshape(y.shape)


def estimate_lag_gain(
    response: np.ndarray,
    design: np.ndarray,
    tr: float,
    lags: np.ndarray | None = None,
) -> tuple[float, float]:
    """Fit response (TRs,) ~ a + gain * (design * hrf(lag)); return the best (lag, gain)."""
    lags = np.arange(-3.0, 3.01, 0.1) if lags is None else lags
    y = np.asarray(response, dtype=np.float64)
    best = (0.0, 0.0, -np.inf)
    for lag in lags:
        x = convolve(design, hrf_kernel(tr, lag))
        X = np.column_stack([np.ones_like(x), x])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ beta
        score = -(r @ r)
        if score > best[2]:
            best = (float(lag), float(beta[1]), score)
    return best[0], best[1]


def hrf_surrogate(
    runs: np.ndarray,
    lags: np.ndarray,
    gains: np.ndarray,
    tr: float,
    rng: np.random.Generator,
    ridge: float = 1e-2,
) -> np.ndarray:
    """HRF surrogate for one run of every subject.

    `runs` is subjects x TRs x parcels. The group-mean signal is deconvolved with the
    group HRF (mean lag) to get a drive estimate; each subject's surrogate is that drive
    convolved with the subject's own HRF lag, scaled per parcel by least squares on the
    subject's own run, plus Gaussian noise whose per-parcel variance matches the residual.

    Deviation from PLAN §5 B.2 (prereg item): because of the per-parcel amplitude fit,
    `gains` has no effect; amplitude comes from the movie data, only the lag from checker.
    """
    runs = np.asarray(runs, dtype=np.float64)
    group = runs.mean(axis=0)
    drive = deconvolve(group - group.mean(axis=0), hrf_kernel(tr, float(np.mean(lags))), ridge)
    drive /= max(float(np.mean(gains)), 1e-12)
    out = np.empty_like(runs)
    for i in range(runs.shape[0]):
        locked = gains[i] * convolve(drive, hrf_kernel(tr, lags[i]))
        centered = runs[i] - runs[i].mean(axis=0)
        # scale the locked part to the subject's data by per-parcel least squares
        scale = (locked * centered).sum(0) / np.maximum((locked * locked).sum(0), 1e-12)
        fit = locked * scale
        noise_sd = (centered - fit).std(axis=0)
        out[i] = fit + rng.standard_normal(fit.shape) * noise_sd
    return out
