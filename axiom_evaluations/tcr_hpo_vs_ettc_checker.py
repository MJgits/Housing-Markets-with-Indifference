from typing import List

if __package__ in (None, ""):
    from _path_setup import ensure_project_root_on_path

    ensure_project_root_on_path()

from axiom_evaluations.allocation_rules import run_extended_ttc, run_tcr_hpo
from axiom_evaluations.preference_enumerator import preference_profiles_as_sets


def compare_tcr_hpo_and_ettc(n_agents: int) -> List[dict]:
    """
    Exhaustively compare TCR-HPO and ETTC on all weak-preference profiles.

    Returns a list of mismatches and runtime failures.
    """
    items = list(range(n_agents))
    all_profiles = preference_profiles_as_sets(items, n_agents=n_agents)

    discrepancies: List[dict] = []
    checked_profiles = 0

    for profile in all_profiles:
        checked_profiles += 1

        try:
            ettc_allocation = run_extended_ttc(profile)
        except Exception as exc:
            discrepancies.append(
                {
                    "profile_index": checked_profiles,
                    "profile": profile,
                    "status": "ettc_error",
                    "error": repr(exc),
                }
            )
            continue

        try:
            tcr_hpo_allocation = run_tcr_hpo(profile)
        except Exception as exc:
            discrepancies.append(
                {
                    "profile_index": checked_profiles,
                    "profile": profile,
                    "status": "tcr_hpo_error",
                    "ettc_allocation": ettc_allocation,
                    "error": repr(exc),
                }
            )
            continue

        if ettc_allocation != tcr_hpo_allocation:
            discrepancies.append(
                {
                    "profile_index": checked_profiles,
                    "profile": profile,
                    "status": "allocation_mismatch",
                    "ettc_allocation": ettc_allocation,
                    "tcr_hpo_allocation": tcr_hpo_allocation,
                }
            )

    print(f"Checked {checked_profiles} profiles.")
    print(f"Discrepancies found: {len(discrepancies)}")

    return discrepancies


if __name__ == "__main__":
    n_agents = 3
    discrepancies = compare_tcr_hpo_and_ettc(n_agents=n_agents)

    if not discrepancies:
        print(f"TCR-HPO and ETTC match on all profiles for n_agents={n_agents}.")
    else:
        first = discrepancies[0]
        print("First discrepancy:")
        print("Profile index:", first["profile_index"])
        print("Status:", first["status"])
        print("Profile:", first["profile"])
        if "ettc_allocation" in first:
            print("ETTC allocation:", first["ettc_allocation"])
        if "tcr_hpo_allocation" in first:
            print("TCR-HPO allocation:", first["tcr_hpo_allocation"])
        if "error" in first:
            print("Error:", first["error"])
