
from ..ettc.extended_ttc import ETTC_HousingMarket
from ...utils import MarketPreferences, Allocation
from math

class ETTC_RandomPriority(ETTC_HousingMarket):
    
    def __init__(self, market_preferences: MarketPreferences) -> None:
        super().__init__(market_preferences)  # run parent setup


    # ETTC only differs from plaxton through the priority ordering
    def _priority_object_from_top_prefs(self, preferred_objects: set[int]) -> int:
        
        return min(preferred_objects)