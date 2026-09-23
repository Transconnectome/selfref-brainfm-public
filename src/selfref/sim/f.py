"""Synthetic network time series for task F (autoregression vs stimulus prediction).

Structure from stage 0 (V3): cross-session repeats exist for inscapes/rest/checker in
17 subjects; movies repeat only within a session (22 subjects). Both designs are the
same generator with a different n_sub; the pair structure is a caller choice (PI decision
in PLAN §4.1). TR 2.1 s. No variance parameter comes from real data (PLAN §12.1).

Subject i, session r, network parcels p = 1..P:
    z_p(t) = phi_ir * z_p(t-1) + c_ir * z_{p-1}(t-1) + innovation      (intrinsic, VAR(1) ring)
    x_p(t) = stim_amp * (u * hrf)_p(t) + intr_amp * z_p(t) / sd + noise
phi_ir = phi_mean + phi_trait_sd * trait_i + phi_state_sd * state_ir   (spectral trait)
c_ir   = c_mean   + c_trait_sd   * trait2_i + c_state_sd * state2_ir   (lagged cross-parcel coupling)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import gaussian_filter1d

from selfref.analysis.hrf import convolve, hrf_kernel


@dataclass
class FParams:
    n_sub: int = 17
    n_ses: int = 2
    n_tr: int = 288
    n_parcel: int = 8
    tr: float = 2.1
    stim_amp: float = 0.7
    intr_amp: float = 1.0
    noise_amp: float = 0.5
    phi_mean: float = 0.5
    phi_trait_sd: float = 0.0
    phi_state_sd: float = 0.1
    c_mean: float = 0.0
    c_trait_sd: float = 0.0
    c_state_sd: float = 0.05
    burn_in: int = 50


def _var_ring(phi, c, T, P, rng, burn):
    z = np.zeros((T + burn, P))
    e = rng.standard_normal((T + burn, P))
    for t in range(1, T + burn):
        z[t] = phi * z[t - 1] + c * np.roll(z[t - 1], 1) + e[t]
    return z[burn:]


def simulate(p: FParams, rng: np.random.Generator) -> np.ndarray:
    """Return x with shape subjects x sessions x TRs x parcels."""
    n, S, T, P = p.n_sub, p.n_ses, p.n_tr, p.n_parcel
    u = gaussian_filter1d(rng.standard_normal((T, P)), 2.0, axis=0)
    drive = convolve(u / u.std(0), hrf_kernel(p.tr))
    drive /= drive.std(0)
    trait_phi = rng.standard_normal(n)
    trait_c = rng.standard_normal(n)
    x = np.empty((n, S, T, P))
    for i in range(n):
        for r in range(S):
            phi = np.clip(p.phi_mean + p.phi_trait_sd * trait_phi[i] + p.phi_state_sd * rng.standard_normal(), -0.3, 0.9)
            c = p.c_mean + p.c_trait_sd * trait_c[i] + p.c_state_sd * rng.standard_normal()
            # keep the VAR stable: spectral radius of phi*I + c*shift is |phi| + |c|
            c = float(np.clip(c, -(0.95 - abs(phi)), 0.95 - abs(phi)))
            z = _var_ring(phi, c, T, P, rng, p.burn_in)
            x[i, r] = p.stim_amp * drive + p.intr_amp * z / z.std(0) + p.noise_amp * rng.standard_normal((T, P))
    return x
