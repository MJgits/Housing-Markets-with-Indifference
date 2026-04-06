from itertools import product
from typing import Any, Dict, Iterable, List, Set, Tuple, Optional
from copy import deepcopy

from WeakHousingMarketAlgorithm import MarketPreferences, PrefAgent, ETTC_HousingMarket
# Assume HousingMarket is available and has:
#   HousingMarket(preferences: MarketPreferences)
#   .execute_extended_ttc(verbose: bool = False) -> Dict[int, int]


def weak_orders_as_sets(items: List[int]) -> List[PrefAgent]:
    """
    Enumerate all weak orders over items.
    Each weak order is represented as an ordered list of sets.
    """
    items = list(items)
    out: List[PrefAgent] = []

    def backtrack(i: int, blocks: List[Set[Any]]) -> None:
        if i == len(items):
            out.append([set(b) for b in blocks])
            return

        x = items[i]

        # Put x into an existing indifference block
        for j in range(len(blocks)):
            blocks[j].add(x)
            backtrack(i + 1, blocks)
            blocks[j].remove(x)

        # Start a new block for x in any position
        for pos in range(len(blocks) + 1):
            blocks.insert(pos, {x})
            backtrack(i + 1, blocks)
            blocks.pop(pos)

    backtrack(0, [])
    return out


def preference_profiles_as_sets(items: List[Any], n_agents: int) -> Iterable[MarketPreferences]:
    """
    Generate all preference profiles for n_agents,
    where each agent's preference is a weak order over items.
    """
    all_ranks = weak_orders_as_sets(items)
    for combo in product(all_ranks, repeat=n_agents):
        yield [[set(s) for s in rank] for rank in combo]


def canonical_pref(pref: PrefAgent) -> Tuple[Tuple[int, ...], ...]:
    """
    Hashable canonical representation of one weak order.
    Example: [{1,2}, {0}] -> ((1,2), (0,))
    """
    return tuple(tuple(sorted(block)) for block in pref)


def canonical_profile(profile: MarketPreferences) -> Tuple[Tuple[Tuple[int, ...], ...], ...]:
    """
    Hashable canonical representation of a whole profile.
    """
    return tuple(canonical_pref(agent_pref) for agent_pref in profile)


def deep_copy_profile(profile: MarketPreferences) -> MarketPreferences:
    return [[set(block) for block in agent_pref] for agent_pref in profile]


def allocation_equal(a1: Dict[int, int], a2: Dict[int, int]) -> bool:
    return dict(a1) == dict(a2)


def other_agents_changed(
    truthful_alloc: Dict[int, int],
    misreport_alloc: Dict[int, int],
    manipulator: int
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


def run_extended_ttc(num_agents,profile: MarketPreferences) -> Dict[int, int]:
    """
    Small wrapper so the checker is easy to adapt if your constructor differs.
    """
    market = ETTC_HousingMarket(market_preferences = deep_copy_profile(profile))
    return market.execute(verbose=False)


def find_nonbossiness_violations(
    n_agents: int,
    stop_at_first: bool = True,
) -> List[dict]:
    """
    Exhaustively checks your non-bossiness definition across all enumerated profiles.

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
        truthful_alloc = run_extended_ttc(n_agents, truthful_profile)

        for i in range(n_agents):
            true_pref_key = canonical_pref(truthful_profile[i])

            for misreport in all_ranks:
                if canonical_pref(misreport) == true_pref_key:
                    continue

                deviated_profile = deep_copy_profile(truthful_profile)
                deviated_profile[i] = [set(block) for block in misreport]

                misreport_alloc = run_extended_ttc(n_agents, deviated_profile)
                checked_deviations += 1

                # Same object for manipulator?
                if truthful_alloc[i] != misreport_alloc[i]:
                    continue

                changed_agents = other_agents_changed(truthful_alloc, misreport_alloc, i)
                if not changed_agents:
                    continue

                violations.append({
                    "manipulator": i,
                    "truthful_profile": deep_copy_profile(truthful_profile),
                    "misreport_profile": deep_copy_profile(deviated_profile),
                    "truthful_allocation": dict(truthful_alloc),
                    "misreport_allocation": dict(misreport_alloc),
                    "changed_other_agents": changed_agents,
                })

                if stop_at_first:
                    print(f"Checked {checked_profiles} profiles and {checked_deviations} deviations.")
                    return violations

    print(f"Checked {checked_profiles} profiles and {checked_deviations} deviations.")
    return violations


def is_nonbossy_exhaustive(n_agents: int) -> bool:
    """
    Returns True iff no violation is found over all enumerated weak-preference profiles.
    """
    return len(find_nonbossiness_violations(n_agents=n_agents, stop_at_first=True)) == 0


if __name__ == "__main__":
    n_agents = 3

    violations = find_nonbossiness_violations(n_agents=n_agents, stop_at_first=False)

    if not violations:
        print(f"No non-bossiness violations found for n_agents={n_agents}.")
    else:
        v = violations[0]
        print("Found a non-bossiness violation:")
        print("Manipulator:", v["manipulator"])
        print("Truthful profile:", v["truthful_profile"])
        print("Misreport profile:", v["misreport_profile"])
        print("Truthful allocation:", v["truthful_allocation"])
        print("Misreport allocation:", v["misreport_allocation"])
        print("Other agents changed:", v["changed_other_agents"])