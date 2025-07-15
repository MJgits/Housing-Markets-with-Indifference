from typing import List, Set
from .utils import Allocation

def verbose_print_subsets(S_star, S_subsets):
    print('_______Partitioning_______')
    print(f'    Agents partitioned into:')
    print(f'    Unsatisfied agents: {S_subsets[0]}')
    print(f'    Satisfied agents in S_1 to S_t: {S_subsets[1:]}')
    print(f'    Satisfied agents in S*: {S_star}')
    print('__________________________')
    print()



def verbose_print_removing_terminal(remaining_agents: Set, 
                                    S_star: Set,
                                    objects_by_agent: list):
    print('_______Removal of terminal agents_______')
    
    agents_in_remaining_agents = ','.join([str(agent) for agent in remaining_agents])
    print(f'    Remaining agent(s) before removal: {agents_in_remaining_agents}.')
    

    agents_in_S_star_str = ','.join([str(agent) for agent in S_star])
    print(f'    S* contains agent(s): {agents_in_S_star_str}.')
    for agent in S_star:

        print(f'      - Allocating object {objects_by_agent[agent]} to agent {agent}')
    print('________________________________________')
    print()    


def verbose_print_out_edges(out_edges: List, 
                            
                            agent_by_object_idx: List):
    print('    Graph constructed by Rule A:')
    for agent in range(len(out_edges)):
        object_pointed_to = out_edges[agent]
        if object_pointed_to > -1:
        
            print(f'    Agent {agent}  ==prefers==>  Object {object_pointed_to}  ==owned_by==>  Agent {agent_by_object_idx[object_pointed_to]}')
    print()


def verbose_print_cycle(cycle_agents: List,
                        objects_by_agent_idx: List,
                        agent_by_object_id: List):
    
    print('    Cycle detected:')
    print('    ', end = '')
    
    print(f'Agent {cycle_agents[0]}', end = '')

    for agent in cycle_agents[1:]:
        print(f'==> Object {objects_by_agent_idx[agent]} ==> Agent {agent}', end = '')
    print('...')



def verbose_print_exchanged_objects(object_by_agent_id: List):
    for agent in range(len(object_by_agent_id)):
        print(f'    Agent {agent} now holds Object {object_by_agent_id[agent]}.')
    print('_____________________________')
    print()
            
def verbose_print_final_allocation(allocation: Allocation):
    print('_______Final Allocation_______')
    print('______________________________')

    for agent in allocation:
        print(f'    Agent {agent} is allocated Object {allocation[agent]}')

    print('______________________________')
    print('______________________________')


if __name__ == '__main__':
    verbose_print_removing_terminal({1,2,3}, {1,2}, [9,8,7,5,4])
    verbose_print_subsets({1,2}, [{9,8},{7,5,4}])
