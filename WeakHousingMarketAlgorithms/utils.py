from typing import Dict, List, Set
from .verbose_prints import (format_subsets,
                             format_cycle, 
                             format_exchanged_objects)


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

        # this lets you access agents by indexing their held object
        self.agent_by_object_index: List[int] = [i for i in range(self.num_agents)]

        # Initially, all objects should be available for the purpose of selecting top available
        self.available_objects: List[bool] = [True for _ in range(self.num_agents)]

        # this is the allocation that gets returned back from execute()
        self.allocation: Allocation = dict()

        # toggles printing algorithm structure
        self.verbose = False
    
    #  this method takes an agent id and produces an indifference class. I.e. a set of available objects that are preferenced equally and greater than any other available objects
    def _top_available(self, agent: int) -> IndifferenceClass:

        top_objects: IndifferenceClass = set()
 
        for indiff_class in self.market_preferences[agent]:
            for obj in indiff_class:
                if self.available_objects[obj]:
                    top_objects.add(obj)

            # if we have at least one object returned after checking an entire indiff class, we should break
            if top_objects: 
                break    
        
        return top_objects


    
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
            


        # Performs partitioning as per Xiong 2021
    def _partition(self, remaining_agents: Set[int]) -> None:
        
        # each index will be the rank of agents. 
        # So i = 0 are unsatisfied agents, i=1 are satisfied agents who have a preference in i = 0 houses aka objects_in_S_subsets[i]
        self.S_subsets: List[Set[int]] = []
        self.objects_in_S_subsets = []
        
        # distinct subset of terminal agents
        self.S_star = set()
        
        # 'subset' and 'owned_objects' will get appended to S_subsets at the end of each subset iteration
        subset = set()
        owned_objects = set()
        
        # remaining gets used to further subset the satisfied agents
        remaining = set()
 
        # get satisfied agents
        for agent in remaining_agents:

            # satisfied if owned object is in the set of its top available items
            if self.object_by_agent_index[agent] in self._top_available(agent):
                remaining.add(agent)
            
            # unsatisfied otherwise
            else:
                subset.add(agent)
                # this constructs the set of items owned by the unsatisfied agents
                owned_objects.add(self.object_by_agent_index[agent])
        
        # here we add the first subset (unsatisfied agents) along with their owned objects
        self.S_subsets.append(subset)
        self.objects_in_S_subsets.append(owned_objects)


        # we start actually subsetting satisfied agents here starting with rank 1 agents and iterating until no agents remain
        rank = 1

        while remaining:

            # subset will get appended to S_subsets
            subset = set()
            
            # the objects owned by agents in subset_k will go in to owned_objects
            owned_objects = set()

            # we reset and repopulate remaining
            next_remaining = set()
            
            for agent in remaining:

                # we are checking if any of the agents top available objects exist in the previous ranks owned objects
                top_pref_in_prev_rank = self._top_available(agent).intersection(self.objects_in_S_subsets[rank-1])
                
                # add agent and object to subset and objects in subset
                if top_pref_in_prev_rank:
                    subset.add(agent)
                    owned_objects.add(self.object_by_agent_index[agent])
                
                # we repopulate remaining set to use in the next iteration
                else:
                    next_remaining.add(agent)

            # if there are no agents being placed in a new subset on a given iteration, remaining agents should be all put in the final subset S*
            if len(remaining) == len(next_remaining):
                self.S_star = remaining
                break
            
            # here we add to S_subsets and also the objects owned by Subset[rank]
            self.S_subsets.append(subset)
            self.objects_in_S_subsets.append(owned_objects)

            # Add one to rank so that we search the next rank of objects
            rank+=1

            # Reset the remaining agents with any that were not inserted into S
            remaining = next_remaining
        
        self._log(format_subsets(self.S_star, self.S_subsets))

    def _log(self, message: str = "") -> None:
        if self.verbose:
            print(message)



    def _identify_cycles_exchange_objects(self, graph_agentIdx_to_object: List[int]) -> None:

        # start with a used_in_cycle array thats true for any agent who has been taken out of the system 
        used_in_cycle = [graph_agentIdx_to_object[i] < 0 for i in range(self.num_agents)]

        
        for agentIdx in range(len(graph_agentIdx_to_object)):
            
            # check that they are not involved in another cycle? probably a useless check since disjoint?
            if not used_in_cycle[agentIdx]:
                
                # start search
                current_path = [agentIdx]
                visited = [False for _ in range(len(graph_agentIdx_to_object))]
                visited[agentIdx] = True
                
                # check for cycles
                while True:
                    
                    owner_of_out_edge = self.agent_by_object_index[graph_agentIdx_to_object[agentIdx]]
                    next_agent = owner_of_out_edge
                    
                    # if we encroach onto an already identified cycle via some path, we should break. No agent along this path should have it's items traded in this iteration
                    if used_in_cycle[next_agent]:
                        break

                    # do swap objects, do not allocate, also update used_in_cycle
                    if visited[next_agent]:
                        # identify cycle do stuff
                        
                        start_cycle_index = current_path.index(next_agent)
                        
                        cycle_path = current_path[start_cycle_index:][:]
                        cycle_path.append(next_agent)
                        self._log(
                            format_cycle(
                                cycle_path,
                                self.object_by_agent_index
                            )
                        )

                        
                        for agent in current_path[start_cycle_index:]:
                            # update self.object by agent
                            self.object_by_agent_index[agent] = graph_agentIdx_to_object[agent]
                            # update self.agent by object
                            self.agent_by_object_index[graph_agentIdx_to_object[agent]] = agent
                            # update used in cycle
                            used_in_cycle[agent] = True
                        break
                    
                    # continue traversing path 
                    else:
                        current_path.append(next_agent)
                        agentIdx = next_agent
                        visited[agentIdx] = True
            
        self._log(format_exchanged_objects(self.object_by_agent_index))
