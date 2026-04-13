#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0"]
# ///
"""Monte Carlo + analytical validation of the dependency cooldown cost model.

Backs the claims in the blog post
`content/dependency-cooldown-considered-harmful.md`.

Model
-----
Each year, a dep tree sees:
  - lambda_cve CVE disclosures (rate, /year). Each costs vuln_days_per_cve
    days of exposure, where:
        no cooldown:  vuln_days_per_cve = audit_latency_days
        cooldown C:   vuln_days_per_cve = max(C, audit_latency_days)
  - r_attack malicious releases (rate, /year) in packages you would
    plausibly adopt. For each, detection delay D is drawn from a
    3-component exponential mixture (typosquats, account comp, long-dwell).
    Your natural adoption delay N_0 ~ Uniform(0, natural_adopt_max).
    With cooldown C: effective adoption N = max(C, N_0).
    You are compromised iff N < D.

Annual expected cost per policy:
    cost = lambda_cve * vuln_days_per_cve * I_cve
         + r_attack  * P(compromise)     * I_attack

Break-even ratio I_attack / I_cve is solved from equating the two policies.

Run with:
    uv run scripts/simulate_dependency_cooldown.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import numpy as np
from numpy.typing import NDArray

SEED: Final[int] = 42

# --- Defaults matching the blog post --------------------------------------

LAMBDA_CVE: Final[float] = 25.0          # CVEs/year in your dep tree
R_ATTACK: Final[float] = 0.1             # malicious releases/year you could adopt
COOLDOWN_DAYS: Final[float] = 8.0
AUDIT_LATENCY_DAYS: Final[float] = 1.0   # no-cooldown case: daily audit
NATURAL_ADOPT_MAX: Final[float] = 7.0    # N_0 ~ U(0, 7) weekly upgrade cadence

# Detection-delay mixture: (weight, mean_days) for exponential components
MixtureComponent = tuple[float, float]
DETECTION_MIXTURE: Final[tuple[MixtureComponent, ...]] = (
    (0.50, 0.5),    # typosquats: hours
    (0.30, 3.0),    # compromised maintainer account: a few days
    (0.20, 60.0),   # long-dwell (xz, SolarWinds family)
)
assert math.isclose(sum(w for w, _ in DETECTION_MIXTURE), 1.0, abs_tol=1e-9), (
    "DETECTION_MIXTURE weights must sum to 1"
)

_MIXTURE_WEIGHTS: Final[NDArray[np.float64]] = np.array(
    [w for w, _ in DETECTION_MIXTURE], dtype=np.float64
)
_MIXTURE_MEANS: Final[NDArray[np.float64]] = np.array(
    [m for _, m in DETECTION_MIXTURE], dtype=np.float64
)

N_ATTACK_SAMPLES: Final[int] = 2_000_000
MC_ANALYTIC_TOLERANCE: Final[float] = 0.002

SWEEP_COOLDOWNS: Final[tuple[float, ...]] = (0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 8.0, 14.0, 30.0, 60.0, 90.0)
SHAPE_COOLDOWNS: Final[tuple[float, ...]] = (0.0, 1.0, 2.0, 5.0, 7.0, 14.0, 30.0)
REPORT_RATIOS: Final[tuple[float, ...]] = (1e2, 1e3, 1e4, 1e5, 1e6)


@dataclass(frozen=True)
class PolicyResult:
    cooldown_days: float
    vuln_days_per_year: float       # contribution from CVE exposure
    p_compromise: float             # per malicious release
    compromises_per_year: float     # = R_ATTACK * p_compromise


# --- Policy builders -------------------------------------------------------

def _policy(cooldown_days: float, p_compromise: float) -> PolicyResult:
    vuln_days_per_cve = max(cooldown_days, AUDIT_LATENCY_DAYS)
    return PolicyResult(
        cooldown_days=cooldown_days,
        vuln_days_per_year=LAMBDA_CVE * vuln_days_per_cve,
        p_compromise=p_compromise,
        compromises_per_year=R_ATTACK * p_compromise,
    )


# --- Vectorized sampling --------------------------------------------------

def sample_detection_delays(n: int, rng: np.random.Generator) -> NDArray[np.float64]:
    """Draw n samples from the exponential mixture (weights x means)."""
    component = rng.choice(len(_MIXTURE_MEANS), size=n, p=_MIXTURE_WEIGHTS)
    return rng.exponential(scale=_MIXTURE_MEANS[component])


def sample_natural_adoption(n: int, rng: np.random.Generator) -> NDArray[np.float64]:
    return rng.uniform(0.0, NATURAL_ADOPT_MAX, size=n)


# --- Analytical closed forms ----------------------------------------------

def _survival_at(t: float) -> float:
    """S(t) = Pr(D > t) for the detection-delay mixture."""
    return float(np.dot(_MIXTURE_WEIGHTS, np.exp(-t / _MIXTURE_MEANS)))


def analytical_p_compromise(cooldown: float) -> float:
    """P(max(C, N_0) < D) in closed form.

    Split the N_0 integral at C:
        P = (1/T) [C * S(C) + integral_{C}^{T} S(n) dn]
    with S(t) = Pr(D > t) = sum_k w_k exp(-t/mean_k).

    For C >= T the flat region covers [0, T] so P = S(C).
    """
    t = NATURAL_ADOPT_MAX
    if cooldown >= t:
        return _survival_at(cooldown)

    flat = cooldown * _survival_at(cooldown)
    # integral_{C}^{T} w_k * exp(-n/mean_k) dn = w_k * mean_k * (exp(-C/mean_k) - exp(-T/mean_k))
    tail = float(np.dot(
        _MIXTURE_WEIGHTS * _MIXTURE_MEANS,
        np.exp(-cooldown / _MIXTURE_MEANS) - np.exp(-t / _MIXTURE_MEANS),
    ))
    return (flat + tail) / t


def analytical_policy(cooldown_days: float) -> PolicyResult:
    return _policy(cooldown_days, analytical_p_compromise(cooldown_days))


# --- Monte Carlo -----------------------------------------------------------

def monte_carlo_policy(
    cooldown_days: float,
    rng: np.random.Generator,
    n_samples: int = N_ATTACK_SAMPLES,
) -> PolicyResult:
    d_mal = sample_detection_delays(n_samples, rng)
    n0 = sample_natural_adoption(n_samples, rng)
    n = np.maximum(cooldown_days, n0)
    p_compromise = float(np.mean(n < d_mal))
    return _policy(cooldown_days, p_compromise)


def run_paired_monte_carlo() -> tuple[PolicyResult, PolicyResult]:
    """Run both policies with common random numbers (seed reset per run)."""
    no_cooldown = monte_carlo_policy(0.0, np.random.default_rng(SEED))
    cooldown = monte_carlo_policy(COOLDOWN_DAYS, np.random.default_rng(SEED))
    return no_cooldown, cooldown


# --- Cost functions --------------------------------------------------------

def total_cost(result: PolicyResult, i_attack_over_i_cve: float) -> float:
    return result.vuln_days_per_year + result.compromises_per_year * i_attack_over_i_cve


def break_even_ratio(
    cooldown: PolicyResult, no_cooldown: PolicyResult
) -> float:
    """Return I_attack/I_cve at which the two policies tie.

    (vuln_days_co - vuln_days_nc) * I_cve = (compromises_nc - compromises_co) * I_attack
    """
    extra_vuln_days = cooldown.vuln_days_per_year - no_cooldown.vuln_days_per_year
    prevented = no_cooldown.compromises_per_year - cooldown.compromises_per_year
    if prevented <= 0:
        return math.inf
    return extra_vuln_days / prevented


def optimal_cooldown(
    policies: list[PolicyResult], i_attack_over_i_cve: float
) -> PolicyResult:
    return min(policies, key=lambda r: total_cost(r, i_attack_over_i_cve))


# --- Self-check ------------------------------------------------------------

def assert_mc_matches_analytical(
    mc: PolicyResult, analytical: float, label: str
) -> None:
    diff = abs(mc.p_compromise - analytical)
    if diff > MC_ANALYTIC_TOLERANCE:
        raise AssertionError(
            f"{label}: Monte Carlo {mc.p_compromise:.4f} vs analytical "
            f"{analytical:.4f} differ by {diff:.4f} "
            f"(tolerance {MC_ANALYTIC_TOLERANCE})"
        )


# --- Report sections -------------------------------------------------------

def _print_header(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def _fmt_policy(r: PolicyResult) -> str:
    return (
        f"vuln-days/yr={r.vuln_days_per_year:6.1f}  "
        f"P(compromise)={r.p_compromise:.4f}  "
        f"compromises/yr={r.compromises_per_year:.5f}"
    )


def print_config() -> None:
    print("=" * 72)
    print("Dependency Cooldown Cost Model - Simulation and Analytical Check")
    print("=" * 72)
    print(f"lambda_cve            = {LAMBDA_CVE} CVEs/year")
    print(f"r_attack              = {R_ATTACK} malicious releases/year")
    print(f"cooldown              = {COOLDOWN_DAYS} days")
    print(f"audit_latency         = {AUDIT_LATENCY_DAYS} days")
    print(f"natural_adopt_max     = {NATURAL_ADOPT_MAX} days (uniform)")
    print(f"detection_mixture     = {DETECTION_MIXTURE}")
    print(f"monte_carlo_samples   = {N_ATTACK_SAMPLES:,}")


def print_analytical(p_nc: float, p_co: float) -> None:
    _print_header("Analytical P(compromise per attack)")
    print(f"  no cooldown:            {p_nc:.4f}")
    print(f"  cooldown C={COOLDOWN_DAYS:.0f}:           {p_co:.4f}")
    print(f"  delta prevented:        {p_nc - p_co:+.4f}")


def print_monte_carlo(no_cooldown: PolicyResult, cooldown: PolicyResult) -> None:
    _print_header("Monte Carlo")
    print(f"  no cooldown:   {_fmt_policy(no_cooldown)}")
    print(f"  cooldown={COOLDOWN_DAYS}: {_fmt_policy(cooldown)}")


def print_mc_vs_analytical(
    no_cooldown: PolicyResult,
    cooldown: PolicyResult,
    p_nc: float,
    p_co: float,
) -> None:
    _print_header(f"Analytical vs Monte Carlo (tolerance {MC_ANALYTIC_TOLERANCE})")
    print(f"  P_nc: analytical={p_nc:.4f}  MC={no_cooldown.p_compromise:.4f}  "
          f"diff={no_cooldown.p_compromise - p_nc:+.4f}  [ok]")
    print(f"  P_co: analytical={p_co:.4f}  MC={cooldown.p_compromise:.4f}  "
          f"diff={cooldown.p_compromise - p_co:+.4f}  [ok]")


def print_cost_differential(
    cooldown: PolicyResult, no_cooldown: PolicyResult
) -> None:
    _print_header("Cost differential")
    extra_vd = cooldown.vuln_days_per_year - no_cooldown.vuln_days_per_year
    prevented = no_cooldown.compromises_per_year - cooldown.compromises_per_year
    years_between_prevented = 1.0 / max(prevented, 1e-12)
    print(f"  guaranteed extra CVE exposure: {extra_vd:7.1f} vuln-days/year")
    print(f"  attacks prevented by cooldown: {prevented:.5f}/year")
    print(f"    = 1 compromise prevented every ~{years_between_prevented:,.0f} years")


def print_break_even(cooldown: PolicyResult, no_cooldown: PolicyResult) -> None:
    _print_header("Break-even I_attack / I_cve")
    print(f"  {break_even_ratio(cooldown, no_cooldown):,.0f}")
    print("  (a single compromise must be at least this many vuln-days of CVE")
    print("   exposure to make an 8-day cooldown pay off for the default params)")


def print_shape_table(baseline: PolicyResult) -> None:
    """Side-by-side CVE cost and attack prevention for common cooldown windows.

    This is the table reproduced in the blog post's section 4.
    """
    _print_header("Shape of the tradeoff - common cooldown windows vs C=0 baseline")
    print(f"  {'C':>4} "
          f"{'vuln-days/yr':>13} "
          f"{'P(compr)':>10} "
          f"{'prevented/yr':>14} "
          f"{'1 per N yrs':>14} "
          f"{'break-even':>12}")
    for c in SHAPE_COOLDOWNS:
        policy = analytical_policy(c)
        prevented = baseline.compromises_per_year - policy.compromises_per_year
        years_between = 1.0 / prevented if prevented > 1e-12 else math.inf
        be = break_even_ratio(policy, baseline) if c > 0 else math.nan
        print(
            f"  {c:>4.0f} "
            f"{policy.vuln_days_per_year:>13.1f} "
            f"{policy.p_compromise:>10.4f} "
            f"{prevented:>14.5f} "
            f"{years_between:>14,.0f} "
            f"{be:>12,.0f}"
        )


def print_sweep_table(policies: list[PolicyResult]) -> None:
    _print_header("Cooldown sweep (analytical) - cost at several risk ratios")
    print(f"  {'C':>4} "
          f"{'vuln-days/yr':>13} "
          f"{'P(compr)':>10} "
          f"{'cost@1e3':>12} "
          f"{'cost@1e4':>12} "
          f"{'cost@1e5':>12}")
    for p in policies:
        print(
            f"  {p.cooldown_days:>4.0f} "
            f"{p.vuln_days_per_year:>13.1f} "
            f"{p.p_compromise:>10.4f} "
            f"{total_cost(p, 1e3):>12.2f} "
            f"{total_cost(p, 1e4):>12.2f} "
            f"{total_cost(p, 1e5):>12.2f}"
        )


def print_sweep_optima(policies: list[PolicyResult]) -> None:
    """For each risk ratio, pick the cooldown C that minimizes total cost.

    Total cost = CVE-exposure cost + expected attack cost, in vuln-day units
    (so a risk ratio of 10,000 means one compromise == 10k vuln-days of
    CVE exposure). Optimal C is the argmin over the sweep grid above.
    """
    _print_header("Optimal cooldown per risk ratio (argmin of the sweep above)")
    print("  Reads: 'if you value one compromise at N vuln-days of CVE exposure,")
    print("   the cost-minimizing cooldown window is C days'.")
    print()
    print(f"  {'I_attack/I_cve':>16}   {'optimal C':>10}   {'total cost':>14}")
    for ratio in REPORT_RATIOS:
        best = optimal_cooldown(policies, ratio)
        print(
            f"  {ratio:>16,.0f}   {best.cooldown_days:>8.0f}d   "
            f"{total_cost(best, ratio):>14.2f}"
        )


def print_verdict(no_cooldown: PolicyResult, cooldown: PolicyResult) -> None:
    _print_header("Verdict")
    ratio = 1e4
    zero_cost = total_cost(no_cooldown, ratio)
    eight_cost = total_cost(cooldown, ratio)
    print(f"  At I_attack/I_cve = {ratio:,.0f} (one compromise == 10k vuln-days):")
    print(f"    no cooldown total cost = {zero_cost:.2f}")
    print(f"    cooldown=8  total cost = {eight_cost:.2f}")
    winner = "no cooldown dominates" if eight_cost > zero_cost else "cooldown wins"
    print(f"  -> {winner} at this realistic risk ratio")


# --- Entry point -----------------------------------------------------------

def main() -> None:
    print_config()

    p_nc = analytical_p_compromise(0.0)
    p_co = analytical_p_compromise(COOLDOWN_DAYS)
    print_analytical(p_nc, p_co)

    no_cooldown, cooldown = run_paired_monte_carlo()
    print_monte_carlo(no_cooldown, cooldown)

    assert_mc_matches_analytical(no_cooldown, p_nc, "no-cooldown")
    assert_mc_matches_analytical(cooldown, p_co, f"cooldown={COOLDOWN_DAYS}")
    print_mc_vs_analytical(no_cooldown, cooldown, p_nc, p_co)

    print_cost_differential(cooldown, no_cooldown)
    print_break_even(cooldown, no_cooldown)
    print_shape_table(analytical_policy(0.0))

    sweep = [analytical_policy(c) for c in SWEEP_COOLDOWNS]
    print_sweep_table(sweep)
    print_sweep_optima(sweep)

    print_verdict(no_cooldown, cooldown)


if __name__ == "__main__":
    main()
