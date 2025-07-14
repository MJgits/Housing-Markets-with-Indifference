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
type Allocation = Dict[int,int]
