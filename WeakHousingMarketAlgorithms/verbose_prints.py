from typing import List, Set
from .utils import Allocation


def format_subsets(S_star, S_subsets) -> str:
    return "\n".join([
        '_______Partitioning_______',
        '    Agents partitioned into:',
        f'    Unsatisfied agents: {S_subsets[0]}',
        f'    Satisfied agents in S_1 to S_t: {S_subsets[1:]}',
        f'    Satisfied agents in S*: {S_star}',
        '__________________________',
        '',
    ])


def format_removing_terminal(remaining_agents: Set,
                             S_star: Set,
                             objects_by_agent: list) -> str:
    lines = ['_______Removal of terminal agents_______']

    agents_in_remaining_agents = ','.join([str(agent) for agent in remaining_agents])
    lines.append(f'    Remaining agent(s) before removal: {agents_in_remaining_agents}')

    agents_in_S_star_str = ','.join([str(agent) for agent in S_star])
    lines.append(f'    S* contains agent(s): {agents_in_S_star_str}')
    for agent in S_star:
        lines.append(f'      - Allocating object {objects_by_agent[agent]} to agent {agent}')

    lines.extend([
        '________________________________________',
        '',
    ])
    return "\n".join(lines)


def format_out_edges(out_edges: List,
                     agent_by_object_idx: List) -> str:
    lines = ['    Graph constructed by Rule A:']
    for agent in range(len(out_edges)):
        object_pointed_to = out_edges[agent]
        if object_pointed_to > -1:
            lines.append(
                f'    Agent {agent}  ==prefers==>  Object {object_pointed_to}  ==owned_by==>  Agent {agent_by_object_idx[object_pointed_to]}'
            )
    lines.append('')
    return "\n".join(lines)


def format_cycle(cycle_agents: List,
                 objects_by_agent_idx: List,
                 agent_by_object_id: List) -> str:
    parts = [f'Agent {cycle_agents[0]}']
    for agent in cycle_agents[1:]:
        parts.append(f'==> Object {objects_by_agent_idx[agent]} ==> Agent {agent}')

    return "\n".join([
        '    Cycle detected:',
        f"    {''.join(parts)}...",
    ])


def format_exchanged_objects(object_by_agent_id: List) -> str:
    lines = []
    for agent in range(len(object_by_agent_id)):
        lines.append(f'    Agent {agent} now holds Object {object_by_agent_id[agent]}.')
    lines.extend([
        '_____________________________',
        '',
    ])
    return "\n".join(lines)


def format_final_allocation(allocation: Allocation) -> str:
    lines = [
        '_______Final Allocation_______',
        '______________________________',
    ]

    for agent in allocation:
        lines.append(f'    Agent {agent} is allocated Object {allocation[agent]}')

    lines.extend([
        '______________________________',
        '______________________________',
    ])
    return "\n".join(lines)


if __name__ == '__main__':
    print(format_removing_terminal({1, 2, 3}, {1, 2}, [9, 8, 7, 5, 4]))
    print(format_subsets({1, 2}, [{9, 8}, {7, 5, 4}]))
