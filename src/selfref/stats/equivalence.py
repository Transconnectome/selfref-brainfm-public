"""Outcome categories from PLAN §6.

Rule 2 (tasks that claim an effect exists: A, B, D, E):
    support_strong  95% CI lower bound >= SESOI
    support_weak    95% CI excludes 0 and point >= SESOI, but lower bound < SESOI
    reject          TOST at alpha = .05 per side, i.e. the 90% CI lies inside (-SESOI, SESOI)
    undetermined    none of the above

Rule 3 (tasks that claim a benchmark value: C preservation, F reliability):
    support         95% CI lower bound >= benchmark
    reject          95% CI upper bound < benchmark
    undetermined    otherwise

The direction argument handles one-sided hypotheses stated as "effect < 0":
the estimate and CIs are mirrored so the same rules apply.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    SUPPORT_STRONG = "support_strong"
    SUPPORT_WEAK = "support_weak"
    SUPPORT = "support"
    REJECT = "reject"
    UNDETERMINED = "undetermined"

    @property
    def is_support(self) -> bool:
        return self in (Verdict.SUPPORT_STRONG, Verdict.SUPPORT_WEAK, Verdict.SUPPORT)


@dataclass(frozen=True)
class Interval:
    lo: float
    hi: float

    def __post_init__(self) -> None:
        if not self.lo <= self.hi:
            raise ValueError(f"interval lower bound {self.lo} exceeds upper bound {self.hi}")


def _mirror(x: float, ci: Interval, direction: str) -> tuple[float, Interval]:
    if direction == "positive":
        return x, ci
    if direction == "negative":
        return -x, Interval(-ci.hi, -ci.lo)
    raise ValueError("direction must be 'positive' or 'negative'")


def classify_effect(
    estimate: float,
    ci95: Interval,
    ci90: Interval,
    sesoi: float,
    direction: str = "positive",
) -> Verdict:
    """Rule 2 of PLAN §6. `sesoi` is a positive magnitude."""
    if sesoi <= 0:
        raise ValueError("sesoi must be positive")
    est, c95 = _mirror(estimate, ci95, direction)
    _, c90 = _mirror(estimate, ci90, direction)
    if c95.lo >= sesoi:
        return Verdict.SUPPORT_STRONG
    if c95.lo > 0 and est >= sesoi:
        return Verdict.SUPPORT_WEAK
    # TOST: both one-sided tests at .05 <=> 90% CI strictly inside the equivalence band.
    if c90.lo > -sesoi and c90.hi < sesoi:
        return Verdict.REJECT
    return Verdict.UNDETERMINED


def classify_benchmark(ci95: Interval, benchmark: float) -> Verdict:
    """Rule 3 of PLAN §6."""
    if ci95.lo >= benchmark:
        return Verdict.SUPPORT
    if ci95.hi < benchmark:
        return Verdict.REJECT
    return Verdict.UNDETERMINED
