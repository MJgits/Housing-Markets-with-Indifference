from typing import List, Set 
from ...utils import MarketPreferences, IndifferenceClass, Allocation, HousingMarket



class TCR_WithPriority(HousingMarket):
    # TODO initialise subclass properly
    def __init__(self, market_preferences: MarketPreferences) -> None:
        super().__init__(market_preferences)

    # a common priority ordering is applied over objects. For this implementation, min object index value is the highest priority
    
    # execution logic
    def execute(self, verbose: bool = False) -> Allocation:
        self.verbose = verbose
        iteration = 1
        remaining_agents = set([i for i in range(self.num_agents)])
        
        while remaining_agents:
            if self.verbose:
                print(f'Iteration: {iteration}\nRemaining Agents: {remaining_agents}')
                print()

        
