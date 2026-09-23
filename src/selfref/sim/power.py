"""Outcome probabilities for the prereg (PLAN §6 rule 4).

`run(seed) -> Verdict` wraps one simulate-estimate-classify cycle of a task. The runner
tallies verdicts over replicate seeds, e.g. P(support | effect = SESOI) and
P(reject | effect = 0). Setting generator parameters so that the true effect equals the
SESOI is task-specific and is done in the week-1 prereg, not here.
"""
from __future__ import annotations

from collections import Counter
from typing import Callable, Iterable

from selfref.stats.equivalence import Verdict


def outcome_probabilities(run: Callable[[int], Verdict], seeds: Iterable[int]) -> dict[str, float]:
    counts = Counter(run(s) for s in seeds)
    n = sum(counts.values())
    probs = {v.value: counts.get(v, 0) / n for v in Verdict}
    probs["any_support"] = sum(c for v, c in counts.items() if v.is_support) / n
    probs["n"] = n
    return probs
