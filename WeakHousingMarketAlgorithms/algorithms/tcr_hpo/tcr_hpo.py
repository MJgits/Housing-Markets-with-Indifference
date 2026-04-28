from typing import List, Set 
from ...utils import MarketPreferences, Allocation, HousingMarket
from ...verbose_prints import format_terminal_sinks


class TCR_HPO(HousingMarket):
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

            # S* is equivalent to the terminal sink agents 
            # i.e. agents who cannot reach unsatisfied agents through a path composed of top preferences
            self._partition(remaining_agents)
            
            # ensuring that we keep checking the graph for terminal sinks
            while True:
                terminal_sink_agents = self.S_star
                if terminal_sink_agents:
                    self._log(format_terminal_sinks(terminal_sink_agents))
                    
                    # need to allocate the agents and remove them from the remaining sets
                    # need to remove terminal agents from the market
                    for agent in terminal_sink_agents:

                        # allocate object to agent
                        object_to_allocate = self.object_by_agent_index[agent]
                        self.allocation[agent] = object_to_allocate


                        # remove availability
                        self.available_objects[object_to_allocate] = False

                    # update remaining agents by removing terminal final allocated ones
                    remaining_agents = remaining_agents.difference(terminal_sink_agents)

                    self._partition(remaining_agents)
                
                
                else:
                    break

            # apply HPO rule
            graph_agent_idx_to_object = self.HPO_rule(remaining_agents)
            self._identify_cycles_exchange_objects(graph_agent_idx_to_object)

        return self.allocation



            
    
    def HPO_rule(self, remaining_agents: Set[int]) -> List[int]:

        # each index i is an agent and out_edges[i] is the object that agent i points to.
        # Initialise out edges as -1 such that removed agents arent part of the graph
        out_edges_agent_to_object = [-1] * self.num_agents
        
        # initially label all unsatisfied agents
        labelled_agents = self.S_subsets[0]
        objects_of_labelled_agents = set()


        # for each unsatisfied agent, point to the agent with highest priority object
        for agent_id in labelled_agents:
            
            preferred_object = min(self._top_available(agent_id))
            
            out_edges_agent_to_object[agent_id] = preferred_object

            # we need this set to determine adjacency of remaining agents
            objects_of_labelled_agents.add(self.object_by_agent_index[agent_id])
        
        
        # determine adjacent agents
        # need to do this in max priority order
        unlabelled_agents = remaining_agents.difference(labelled_agents)
        adjacent_to_labelled = {agent for agent in unlabelled_agents if self._top_available(agent)
                                .intersection(objects_of_labelled_agents)}


        # need to repeatedly take the highest priority agent in AL, make them point, then label, then add new adjacencies
        while adjacent_to_labelled:
            unlabelled_agents = remaining_agents.difference(labelled_agents)
            objects_in_al = {self.object_by_agent_index[agent] for agent in adjacent_to_labelled}
            
            # need to make agent point to their HPA in L
            highest_priority_agent = self.agent_by_object_index[min(objects_in_al)]

            # this is now the object in L that the agent in AL points to
            top_pref_hpo_of_hpa_in_L = min(self._top_available(highest_priority_agent)
                                           .intersection(objects_of_labelled_agents))
            
            # drawing the edge from agent in AL to object in L
            out_edges_agent_to_object[highest_priority_agent] = top_pref_hpo_of_hpa_in_L

            # put new agents in AL
            unlabelled_not_adjacent = unlabelled_agents.difference(adjacent_to_labelled)
            for agent in unlabelled_not_adjacent:
                if self.object_by_agent_index[highest_priority_agent] in self._top_available(agent):
                    adjacent_to_labelled.add(agent)


            # label the agent that was picked out and remove them from AL
            labelled_agents.add(highest_priority_agent)
            objects_of_labelled_agents.add(self.object_by_agent_index[highest_priority_agent])
            adjacent_to_labelled.remove(highest_priority_agent)


        return out_edges_agent_to_object


                    
            

        
    


        

        
