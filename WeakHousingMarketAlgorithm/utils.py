from typing import Dict, List, Set

'''
In a weak preference market, agents can be indifferent between object.
A set of objects that an agent is indifferent over is called an indifference class.

Each agent has a strict ordering of indifference classes that I represent as an ordered array defined as PrefAgent.

Finally, all preferences in the market can then be represented as an array of agent preferences that I define as MarketPreferences
'''
type IndifferenceClass = Set[int]
type PrefAgent = List[IndifferenceClass]
type MarketPreferences = List[PrefAgent]

# An allocation is a dictionary of agent Ids to object Ids (both represented as ints)
type Allocation = Dict[int, int]


class HousingMarket():
    # Housing markets initialised with a number of agents, and a Market preferences structure
    def __init__(self, market_preferences: MarketPreferences) -> None:
        self.num_agents = len(market_preferences)
        self.market_preferences = market_preferences

        self._validate_market_preferences()

        # initialise a set of agents and object Ids such that agent i owns object i.
        self.object_by_agent_index: List[int] = [i for i in range(self.num_agents)]
        self.agent_by_object_index: List[int] = [i for i in range(self.num_agents)]

        # Initially, all objects should be available for the purpose of selecting top available
        self.available_objects: List[bool] = [True for _ in range(self.num_agents)]

        # this is the allocation that gets returned back from execute()
        self.allocation: Allocation = dict()

    def _validate_market_preferences(self) -> None:
        expected_objects = set(range(self.num_agents))

        for agent, pref in enumerate(self.market_preferences):
            seen_objects: Set[int] = set()

            for indiff_class in pref:
                for obj in indiff_class:
                    if obj in seen_objects:
                        raise ValueError(
                            f"Invalid preferences for agent {agent}: object {obj} appears more than once."
                        )
                    seen_objects.add(obj)

            if seen_objects != expected_objects:
                missing = sorted(expected_objects - seen_objects)
                extra = sorted(seen_objects - expected_objects)
                raise ValueError(
                    "Invalid preferences for agent "
                    f"{agent}: must list each object exactly once. "
                    f"Missing={missing}, Extra={extra}."
                )
