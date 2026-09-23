"""Synthetic Kucyi-like experience-sampling probes with pre-probe EEG features (task D).

Structure from stage 0 (V1): 24 subjects, 47 sessions (one subject has a single
session), 140 ExperienceSampling runs (one session has 2 runs), 6 probes per run,
13 items including `self` and `arou`, integer scale 1-10. Probe times differ between
runs, so only the probe's position (1-6) is shared. No variance parameter is taken
from real data (PLAN §12.1).

Latent state per probe: arousal a, self s (corr(a, s) = rho_self_arou), and a shared
factor g for the other 11 items. EEG features (n_feat, e.g. 31 channels x bands) are
    subject offset + eeg_arou * a * L_a + eeg_self * s * L_s + eeg_drift * tot * L_d + noise
and the self latent also drifts with time-on-task (tot: probe index within session).
Loadings are per feature, in units of the per-feature noise SD, so the decodable signal
grows with n_feat (about n_feat * loading^2 before regularisation).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

ITEMS = ["self", "arou"] + [f"item{k:02d}" for k in range(3, 14)]


@dataclass
class DParams:
    n_sub: int = 24
    single_session_subjects: int = 1
    two_run_sessions: int = 1
    runs_per_session: int = 3
    probes_per_run: int = 6
    n_feat: int = 186
    rho_self_arou: float = 0.0
    rho_items: float = 0.3
    eeg_self: float = 0.0
    eeg_arou: float = 0.0
    eeg_drift: float = 0.0
    self_drift: float = 0.0
    eeg_noise: float = 1.0
    discretize: bool = True


def _to_scale(z: np.ndarray) -> np.ndarray:
    return np.clip(np.round(5.5 + 1.5 * z), 1, 10)


def simulate(p: DParams, rng: np.random.Generator) -> tuple[pd.DataFrame, np.ndarray]:
    """Return (probe table, EEG feature matrix). One row per probe, in session order."""
    rows = []
    two_run_left = p.two_run_sessions
    for sub in range(p.n_sub):
        n_ses = 1 if sub < p.single_session_subjects else 2
        for ses in range(n_ses):
            n_run = p.runs_per_session
            if two_run_left > 0 and ses == n_ses - 1 and sub == p.n_sub - 1:
                n_run, two_run_left = n_run - 1, two_run_left - 1
            tot = 0
            for run in range(n_run):
                for pos in range(p.probes_per_run):
                    rows.append((sub, ses, run, pos, tot))
                    tot += 1
    df = pd.DataFrame(rows, columns=["subject", "session", "run", "position", "time_on_task"])
    n = len(df)

    a = rng.standard_normal(n)
    s = p.rho_self_arou * a + np.sqrt(1 - p.rho_self_arou**2) * rng.standard_normal(n)
    tot_z = (df["time_on_task"].to_numpy() - 8.5) / 5.2
    s = s + p.self_drift * tot_z
    g = rng.standard_normal(n)
    latent = {"self": s, "arou": a}
    for it in ITEMS[2:]:
        latent[it] = np.sqrt(p.rho_items) * g + np.sqrt(1 - p.rho_items) * rng.standard_normal(n)
    for it in ITEMS:
        df[it] = _to_scale(latent[it]) if p.discretize else latent[it]

    # eeg_* are per-feature loadings in units of the per-feature noise SD
    L = rng.standard_normal((3, p.n_feat))
    offsets = rng.standard_normal((p.n_sub, p.n_feat))
    X = (
        offsets[df["subject"].to_numpy()]
        + p.eeg_arou * a[:, None] * L[0]
        + p.eeg_self * s[:, None] * L[1]
        + p.eeg_drift * tot_z[:, None] * L[2]
        + p.eeg_noise * rng.standard_normal((n, p.n_feat))
    )
    return df, X
