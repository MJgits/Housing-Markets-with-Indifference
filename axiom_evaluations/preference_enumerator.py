from itertools import product
from typing import Any, Iterable, List, Set, Tuple

if __package__ in (None, ""):
    from _path_setup import ensure_project_root_on_path

    ensure_project_root_on_path()

from WeakHousingMarketAlgorithms import MarketPreferences, PrefAgent


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
