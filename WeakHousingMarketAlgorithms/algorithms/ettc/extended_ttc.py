from typing import List, Set 
from ...utils import MarketPreferences, IndifferenceClass, Allocation, HousingMarket
from ...verbose_prints import * 


class ETTC_HousingMarket(HousingMarket):
    # Housing markets initialised with Market preferences structure
    def __init__(self, market_preferences: MarketPreferences) -> None:
        super().__init__(market_preferences)

    # Performs partitioning as per Xiong 2021
    def __partition(self, remaining_agents: Set[int]) -> None:
        
        # each index will be the rank of agents. 
        # So i = 0 are unsatisfied agents, i=1 are satisfied agents who have a preference in i = 0 houses aka objects_in_S_subsets[i]
        self.S_subsets = []
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
        
        if self.verbose:
            verbose_print_subsets(self.S_star, self.S_subsets)

    # this method performs the bulk of the allocation, forming the graph and allocating and exchanging objects 
    def execute(self, verbose: bool = False) -> Allocation:
        self.verbose = verbose
        iteration = 1
        remaining_agents = set([i for i in range(self.num_agents)])
        
        while remaining_agents:
            if self.verbose:
                print(f'Iteration: {iteration}\nRemaining Agents: {remaining_agents}')
                print()
            # Here we create the S partitions, S[0] are unsatisfied and S[-1] is S*
            # This resets the subsets every iteration
            self.__partition(remaining_agents)
  
            # These are the terminal sinks I believe
            if self.S_star:
                if self.verbose:
                    verbose_print_removing_terminal(remaining_agents, 
                                                    self.S_star,
                                                    self.object_by_agent_index)
                
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
                if self.verbose:
                    print('_______S_star is empty_______')
                    print()
                    print('    Creating disjoint cycles and exchanging objects:')
                    
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
                            out_edges_agent_to_object[unsatisfied_agent] = self.__priority_object_from_top_prefs(preferred_objects)
                            break
                
                # for each satisfied agent i.e. in subsets[1:], point to the highest priority in objects owned by agents in k-1
                for k in range(1,len(self.objects_in_S_subsets)):
                    for agent in self.S_subsets[k]:
                        preferred_objects = self._top_available(agent).intersection(self.objects_in_S_subsets[k-1])
                        
                        # assigning highest priority object to the out edge of the agent
                        out_edges_agent_to_object[agent] = self.__priority_object_from_top_prefs(preferred_objects)


                if self.verbose:   
                    verbose_print_out_edges(out_edges_agent_to_object, self.agent_by_object_index)
                    
                # This finds cycles and modifies self.objects_by_agent and agent_by_object to reflect exchanged (but not yet allocated) objects
                self.__identify_cycles_exchange_objects(out_edges_agent_to_object)
            
            iteration+=1

        if self.verbose:
            verbose_print_final_allocation(self.allocation)

        return self.allocation
                
    def __identify_cycles_exchange_objects(self, graph_agentIdx_to_object:List[int]) -> None:

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
                        
                        if self.verbose:
                            cycle_path = current_path[start_cycle_index:][:]
                            cycle_path.append(next_agent)
                            verbose_print_cycle(cycle_path, 
                                                self.object_by_agent_index,
                                                self.agent_by_object_index)
                            
                        
                        
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
            
        if self.verbose:
            verbose_print_exchanged_objects(self.object_by_agent_index)

    # method helps to break ties using global priority order
    def __priority_object_from_top_prefs(self, preferred_objects: set[int]) -> int:
        # this ensures we select highest priority by getting highest priority agent holding a preferred object
        
        priority_owner_of_preferred_objects = min({self.agent_by_object_index[i] for i in preferred_objects})

        # then finding the highest priority agent's object
        priority_preferred_object = self.object_by_agent_index[priority_owner_of_preferred_objects]

        return priority_preferred_object
