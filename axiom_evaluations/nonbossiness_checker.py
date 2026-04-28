import csv
from pathlib import Path
from typing import Dict, List

if __package__ in (None, ""):
    from _path_setup import ensure_project_root_on_path

    ensure_project_root_on_path()

from WeakHousingMarketAlgorithms import Allocation
from axiom_evaluations.allocation_rules import AllocationRule, run_extended_ttc, run_plaxton_algo_1
from axiom_evaluations.preference_enumerator import (
    canonical_pref,
    deep_copy_profile,
    preference_profiles_as_sets,
    weak_orders_as_sets,
)


def is_fully_indifferent_pref(pref: List[set], n_agents: int) -> bool:
    """
    Return True iff pref ranks every object in one indifference class.
    """
    return canonical_pref(pref) == (tuple(range(n_agents)),)


def other_agents_changed(
    truthful_alloc: Dict[int, int],
    misreport_alloc: Dict[int, int],
    manipulator: int,
) -> List[int]:
    """
    Return the list of agents j != manipulator whose assigned house changed.
    """
    changed = []
    all_agents = set(truthful_alloc.keys()) | set(misreport_alloc.keys())
    for j in sorted(all_agents):
        if j == manipulator:
            continue
        if truthful_alloc.get(j) != misreport_alloc.get(j):
            changed.append(j)
    return changed


def format_pref(pref: List[set]) -> str:
    """
    Convert one weak preference order into a compact readable string.
    Example: [{0,1}, {2}] -> "{0,1} > {2}"
    """
    return " > ".join("{" + ",".join(str(item) for item in sorted(block)) + "}" for block in pref)


def format_profile(profile: List[List[set]]) -> str:
    """
    Convert a full profile into a readable string grouped by agent.
    """
    return " | ".join(f"A{i}: {format_pref(pref)}" for i, pref in enumerate(profile))


def format_allocation(allocation: Dict[int, int]) -> str:
    """
    Convert an allocation dictionary into a stable readable string.
    """
    return ", ".join(f"A{i}->{allocation[i]}" for i in sorted(allocation))


def export_violations_to_csv(
    violations: List[dict],
    output_path: Path,
    n_agents: int,
) -> None:
    """
    Export violations to CSV with both machine-friendly and readable columns.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "violation_id",
        "n_agents",
        "manipulator",
        "changed_other_agents",
        "manipulator_assignment",
        "truthful_manipulator_pref",
        "misreport_manipulator_pref",
        "truthful_profile",
        "misreport_profile",
        "truthful_allocation",
        "misreport_allocation",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for violation_id, violation in enumerate(violations, start=1):
            manipulator = violation["manipulator"]
            writer.writerow(
                {
                    "violation_id": violation_id,
                    "n_agents": n_agents,
                    "manipulator": manipulator,
                    "changed_other_agents": ",".join(
                        str(agent) for agent in violation["changed_other_agents"]
                    ),
                    "manipulator_assignment": violation["truthful_allocation"][manipulator],
                    "truthful_manipulator_pref": format_pref(
                        violation["truthful_profile"][manipulator]
                    ),
                    "misreport_manipulator_pref": format_pref(
                        violation["misreport_profile"][manipulator]
                    ),
                    "truthful_profile": format_profile(violation["truthful_profile"]),
                    "misreport_profile": format_profile(violation["misreport_profile"]),
                    "truthful_allocation": format_allocation(violation["truthful_allocation"]),
                    "misreport_allocation": format_allocation(violation["misreport_allocation"]),
                }
            )

def find_nonbossiness_violations(
    n_agents: int,
    stop_at_first: bool = True,
    allocation_rule: AllocationRule = run_extended_ttc,
) -> List[dict]:
    """
    Exhaustively checks non-bossiness definition across all enumerated profiles.

    Non-bossiness here means:
      no agent can misreport, keep the same assigned object,
      and change some other agent's assignment.

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
            true_pref_key = canonical_pref(truthful_profile[i])

            for misreport in all_ranks:
                if canonical_pref(misreport) == true_pref_key:
                    continue

                deviated_profile = deep_copy_profile(truthful_profile)
                deviated_profile[i] = [set(block) for block in misreport]

                misreport_alloc = allocation_rule(deviated_profile)
                checked_deviations += 1

                if truthful_alloc[i] != misreport_alloc[i]:
                    continue

                changed_agents = other_agents_changed(truthful_alloc, misreport_alloc, i)
                if not changed_agents:
                    continue

                violations.append(
                    {
                        "manipulator": i,
                        "truthful_profile": deep_copy_profile(truthful_profile),
                        "misreport_profile": deep_copy_profile(deviated_profile),
                        "truthful_allocation": dict(truthful_alloc),
                        "misreport_allocation": dict(misreport_alloc),
                        "changed_other_agents": changed_agents,
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


def is_nonbossy_exhaustive(
    n_agents: int,
    allocation_rule: AllocationRule = run_extended_ttc,
) -> bool:
    """
    Returns True iff no violation is found over all enumerated weak-preference profiles.
    """
    return (
        len(
            find_nonbossiness_violations(
                n_agents=n_agents,
                stop_at_first=True,
                allocation_rule=allocation_rule,
            )
        )
        == 0
    )


if __name__ == "__main__":
    n_agents = 3

    violations = find_nonbossiness_violations(
        n_agents=n_agents,
        stop_at_first=False,
        allocation_rule=run_extended_ttc,
    )

    if not violations:
        print(f"No non-bossiness violations found for n_agents={n_agents}.")
    else:
        output_path = Path(__file__).with_name(
            f"nonbossiness_violations_n{n_agents}.csv"
        )
        export_violations_to_csv(violations, output_path=output_path, n_agents=n_agents)

        print(f"Total non-bossiness violations: {len(violations)}")
        print(f"CSV export written to: {output_path}")
        print()

        v = violations[0]
        print("Found a non-bossiness violation:")
        print("Manipulator:", v["manipulator"])
        print("Truthful profile:", v["truthful_profile"])
        print("Misreport profile:", v["misreport_profile"])
        print("Truthful allocation:", v["truthful_allocation"])
        print("Misreport allocation:", v["misreport_allocation"])
        print("Other agents changed:", v["changed_other_agents"])
