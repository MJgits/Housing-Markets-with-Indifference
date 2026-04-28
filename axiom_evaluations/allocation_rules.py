from typing import Callable

if __package__ in (None, ""):
    from _path_setup import ensure_project_root_on_path

    ensure_project_root_on_path()

from WeakHousingMarketAlgorithms import Allocation, ETTC_HousingMarket, MarketPreferences, PlaxtonAlgo1
from axiom_evaluations.preference_enumerator import deep_copy_profile


AllocationRule = Callable[[MarketPreferences], Allocation]


def run_extended_ttc(profile: MarketPreferences) -> Allocation:
    """
    Run extended TTC on a fresh copy of the preference profile.
    """
    market = ETTC_HousingMarket(market_preferences=deep_copy_profile(profile))
    return market.execute(verbose=False)


def run_plaxton_algo_1(profile: MarketPreferences) -> Allocation:
    """
    Run Plaxton algorithm 1 on a fresh copy of the preference profile.
    """
    market = PlaxtonAlgo1(market_preferences=deep_copy_profile(profile))
    return market.execute(verbose=False)
