from typing import List, Set 
from ...utils import MarketPreferences, Allocation, HousingMarket
from ...verbose_prints import (
    format_cycle,
    format_exchanged_objects,
    format_final_allocation,
    format_out_edges,
    format_removing_terminal,
    format_subsets,
)


class ETTC_HousingMarket(HousingMarket):
    # Housing markets initialised with Market preferences structure
    def __init__(self, market_preferences: MarketPreferences) -> None:
        super().__init__(market_preferences)
        





    # this method performs the bulk of the allocation, forming the graph and allocating and exchanging objects 
    def execute(self, verbose: bool = False) -> Allocation:
        self.verbose = verbose
        iteration = 1
        remaining_agents = set([i for i in range(self.num_agents)])
        
        while remaining_agents:
            self._log(f'Iteration: {iteration}\nRemaining Agents: {remaining_agents}\n')
            # Here we create the S partitions, S[0] are unsatisfied and S[-1] is S*
            # This resets the subsets every iteration
            self._partition(remaining_agents)
  
            # These are the terminal sinks I believe
            if self.S_star:
                self._log(
                    format_removing_terminal(
                        remaining_agents,
                        self.S_star,
                        self.object_by_agent_index,
                    )
                )
                
                # need to remove terminal agents from the market
                for agent in self.S_star:

                    # allocate object to agent
                    object_to_allocate = self.object_by_agent_index[agent]
                    self.allocation[agent] = object_to_allocate
                    # remove availability
                    self.available_objects[object_to_allocate] = False

                # update remaining agents by removing terminal final allocated ones
                remaining_agents = remaining_agents.difference(self.S_star)


            # Need to construct graph according to rule A
            else:
                self._log('_______S_star is empty_______\n')
                self._log('    Creating disjoint cycles and exchanging objects:')
                    
                # each index i is an agent and out_edges[i] is the object that agent i points to.
                # Initialise out edges as -1 such that removed agents arent part of the graph
                out_edges_agent_to_object = [-1]*self.num_agents
                
                # for each unsatisfied agent, point to the agent in the smallest possible k
                for unsatisfied_agent in self.S_subsets[0]:

                    # checking from lowest k subset to highest, including unsatisfied agents? TODO this technically still to be clarified by the authors
                    for subset_k_objects in self.objects_in_S_subsets:
                        
                        # checking if unsatisfied agent has any overlap with objects owned by agents in subset k
                        preferred_objects = self._top_available(unsatisfied_agent).intersection(subset_k_objects)

                        # assign out edge and break out of subset sk
                        if preferred_objects:

                            # assigning highest priority object to the out edge of the agent
                            out_edges_agent_to_object[unsatisfied_agent] = self._priority_object_from_top_prefs(preferred_objects)
                            break
                
                # for each satisfied agent i.e. in subsets[1:], point to the highest priority in objects owned by agents in k-1
                for k in range(1,len(self.objects_in_S_subsets)):
                    for agent in self.S_subsets[k]:
                        preferred_objects = self._top_available(agent).intersection(self.objects_in_S_subsets[k-1])
                        
                        # assigning highest priority object to the out edge of the agent
                        out_edges_agent_to_object[agent] = self._priority_object_from_top_prefs(preferred_objects)

                self._log(format_out_edges(out_edges_agent_to_object, self.agent_by_object_index))
                    
                # This finds cycles and modifies self.objects_by_agent and agent_by_object to reflect exchanged (but not yet allocated) objects
                self._identify_cycles_exchange_objects(out_edges_agent_to_object)
            
            iteration+=1

        self._log(format_final_allocation(self.allocation))

        return self.allocation
                
    def _identify_cycles_exchange_objects(self, graph_agentIdx_to_object:List[int]) -> None:

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

    # method helps to break ties using global priority order
    def _priority_object_from_top_prefs(self, preferred_objects: set[int]) -> int:
        # this ensures we select highest priority by getting highest priority agent holding a preferred object
        
        priority_owner_of_preferred_objects = min({self.agent_by_object_index[i] for i in preferred_objects})

        # then finding the highest priority agent's object
        priority_preferred_object = self.object_by_agent_index[priority_owner_of_preferred_objects]

        return priority_preferred_object
