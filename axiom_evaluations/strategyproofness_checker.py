from typing import Dict, List

if __package__ in (None, ""):
    from _path_setup import ensure_project_root_on_path

    ensure_project_root_on_path()

from WeakHousingMarketAlgorithms import PrefAgent
from axiom_evaluations.allocation_rules import AllocationRule, run_extended_ttc, run_plaxton_algo_1
from axiom_evaluations.preference_enumerator import (
    canonical_pref,
    deep_copy_profile,
    preference_profiles_as_sets,
    weak_orders_as_sets,
)


def preference_rank(pref: PrefAgent, obj: int) -> int:
    """
    Return the rank of obj in pref. Lower rank is better.
    """
    for rank, indifference_class in enumerate(pref):
        if obj in indifference_class:
            return rank

    raise ValueError(f"Object {obj} is not listed in preference {pref}.")


def strictly_prefers(pref: PrefAgent, better_obj: int, worse_obj: int) -> bool:
    """
    Return True iff better_obj is strictly preferred to worse_obj under pref.
    """
    return preference_rank(pref, better_obj) < preference_rank(pref, worse_obj)


def find_strategyproofness_violations(
    n_agents: int,
    stop_at_first: bool = True,
    allocation_rule: AllocationRule = run_plaxton_algo_1,
) -> List[dict]:
    """
    Exhaustively checks strategy-proofness across all enumerated profiles.

    Strategy-proofness here means:
      no agent can misreport and receive an object that it strictly prefers,
      according to its truthful preference, to its truthful assignment.

    Returns a list of violations. If stop_at_first=True, returns a list of length 0 or 1.
    """
    items = list(range(n_agents))
    all_ranks = weak_orders_as_sets(items)
    all_profiles = preference_profiles_as_sets(items, n_agents=n_agents)

    violations: List[dict] = []

    checked_profiles = 0
    checked_deviations = 0

    for truthful_profile in all_profiles:
        checked_profiles += 1
        truthful_alloc = allocation_rule(truthful_profile)

        for i in range(n_agents):
            truthful_pref = truthful_profile[i]
            true_pref_key = canonical_pref(truthful_pref)
            truthful_object = truthful_alloc[i]

            for misreport in all_ranks:
                if canonical_pref(misreport) == true_pref_key:
                    continue

                deviated_profile = deep_copy_profile(truthful_profile)
                deviated_profile[i] = [set(block) for block in misreport]

                misreport_alloc = allocation_rule(deviated_profile)
                checked_deviations += 1

                misreport_object = misreport_alloc[i]
                if not strictly_prefers(truthful_pref, misreport_object, truthful_object):
                    continue

                violations.append(
                    {
                        "manipulator": i,
                        "truthful_profile": deep_copy_profile(truthful_profile),
                        "misreport_profile": deep_copy_profile(deviated_profile),
                        "truthful_allocation": dict(truthful_alloc),
                        "misreport_allocation": dict(misreport_alloc),
                        "truthful_object": truthful_object,
                        "misreport_object": misreport_object,
                    }
                )

                if stop_at_first:
                    print(
                        f"Checked {checked_profiles} profiles and "
                        f"{checked_deviations} deviations."
                    )
                    return violations

    print(f"Checked {checked_profiles} profiles and {checked_deviations} deviations.")
    if checked_deviations:
        print(f"Violation proportion (over deviations): {len(violations) / checked_deviations:.6f}")

    return violations


def is_strategyproof_exhaustive(
    n_agents: int,
    allocation_rule: AllocationRule = run_extended_ttc,
) -> bool:
    """
    Returns True iff no violation is found over all enumerated weak-preference profiles.
    """
    return (
        len(
            find_strategyproofness_violations(
                n_agents=n_agents,
                stop_at_first=True,
                allocation_rule=allocation_rule,
            )
        )
        == 0
    )


if __name__ == "__main__":
    n_agents = 3

    violations = find_strategyproofness_violations(n_agents=n_agents, stop_at_first=False, allocation_rule= run_plaxton_algo_1)

    if not violations:
        print(f"No strategy-proofness violations found for n_agents={n_agents}.")
    else:
        v = violations[0]
        print("Found a strategy-proofness violation:")
        print("Manipulator:", v["manipulator"])
        print("Truthful profile:", v["truthful_profile"])
        print("Misreport profile:", v["misreport_profile"])
        print("Truthful allocation:", v["truthful_allocation"])
        print("Misreport allocation:", v["misreport_allocation"])
        print("Truthful object:", v["truthful_object"])
        print("Misreport object:", v["misreport_object"])
