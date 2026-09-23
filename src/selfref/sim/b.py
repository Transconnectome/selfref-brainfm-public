"""Synthetic NATVIEW-like movie runs for task B.

Structure (not values) comes from stage 0 (V3): 22 subjects, two runs of the same movie
within one session, TR 2.1 s, ~288 TRs per run, 100 parcels. Every variance parameter is
free; none is fitted to real data (PLAN §12.1).

Components of subject i's BOLD in run r, parcel p:
    stimulus  gain_i * (u * hrf(lag_i + lag_ip))            shared drive u, same in both runs
    moment    moment_amp * gain_i * (v_i * hrf(lag_i+lag_ip)) subject-specific but time-locked:
                                                            identical in both runs (the planted effect)
    static    spontaneous activity mixed by a subject-specific parcel loading (static FC
              fingerprint); a new realisation in every run
    noise     white, new in every run

A checker block run per subject is generated with the same subject HRF, so lag/gain can
be estimated the way the real analysis must do it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import gaussian_filter1d

from selfref.analysis.hrf import convolve, hrf_kernel


@dataclass
class BParams:
    n_sub: int = 22
    n_tr: int = 288
    n_parcel: int = 100
    tr: float = 2.1
    drive_smooth_tr: float = 2.0
    stim_amp: float = 1.0
    moment_amp: float = 0.0
    static_amp: float = 0.5
    static_rank: int = 5
    noise_amp: float = 1.0
    lag_sd_s: float = 1.0
    gain_sd: float = 0.3
    lag_parcel_sd_s: float = 0.0  # subject x parcel HRF deviation not visible in checker
    checker_n_tr: int = 98
    checker_block_s: float = 21.0  # real block timing is unknown (V3: no func events)
    checker_parcels: int = 10
    checker_noise_amp: float = 0.5
    extra: dict = field(default_factory=dict)


@dataclass
class BData:
    run1: np.ndarray  # subjects x TRs x parcels
    run2: np.ndarray
    checker: np.ndarray  # subjects x checker TRs x checker_parcels
    checker_design: np.ndarray
    true_lag: np.ndarray
    true_gain: np.ndarray


def _smooth_noise(rng, shape, sigma):
    x = gaussian_filter1d(rng.standard_normal(shape), sigma, axis=0)
    return x / x.std(axis=0, keepdims=True)


def _hrf_apply(signal, tr, lag_sub, lag_parcel, gain):
    if np.allclose(lag_parcel, 0):
        return gain * convolve(signal, hrf_kernel(tr, lag_sub))
    out = np.empty_like(signal)
    for p in range(signal.shape[1]):
        out[:, p] = gain * convolve(signal[:, p], hrf_kernel(tr, lag_sub + lag_parcel[p]))
    return out


def simulate(p: BParams, rng: np.random.Generator) -> BData:
    n, T, P = p.n_sub, p.n_tr, p.n_parcel
    lag = rng.normal(0.0, p.lag_sd_s, n)
    gain = np.exp(rng.normal(0.0, p.gain_sd, n))
    lag_parcel = rng.normal(0.0, p.lag_parcel_sd_s, (n, P)) if p.lag_parcel_sd_s > 0 else np.zeros((n, P))
    u = _smooth_noise(rng, (T, P), p.drive_smooth_tr)
    runs = np.empty((2, n, T, P))
    for i in range(n):
        locked = p.stim_amp * u
        if p.moment_amp > 0:
            locked = locked + p.moment_amp * _smooth_noise(rng, (T, P), p.drive_smooth_tr)
        bold_locked = _hrf_apply(locked, p.tr, lag[i], lag_parcel[i], gain[i])
        loading = rng.standard_normal((p.static_rank, P))
        for r in range(2):
            spont = gaussian_filter1d(rng.standard_normal((T, p.static_rank)), p.drive_smooth_tr, axis=0) @ loading
            spont = spont / spont.std()
            runs[r, i] = bold_locked + p.static_amp * spont + p.noise_amp * rng.standard_normal((T, P))

    n_block = max(1, int(round(p.checker_block_s / p.tr)))
    design = ((np.arange(p.checker_n_tr) // n_block) % 2 == 1).astype(float)
    checker = np.empty((n, p.checker_n_tr, p.checker_parcels))
    for i in range(n):
        resp = gain[i] * convolve(design, hrf_kernel(p.tr, lag[i]))
        checker[i] = resp[:, None] + p.checker_noise_amp * rng.standard_normal((p.checker_n_tr, p.checker_parcels))
    return BData(runs[0], runs[1], checker, design, lag, gain)
