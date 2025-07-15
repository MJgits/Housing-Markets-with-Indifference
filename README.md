## Usage
Use the following commands to set up the repo:
```bash
git clone https://github.com/MJgits/Housing-Markets-with-Indifference.git
  
cd Housing-Markets-with-Indifference
  
pip install -e .
```
Run the main file to execute the algorithm with some examples. Preferences have to be complete and inputted as per the examples.

## Description
This algorithm facilitates exchange of indivisible items among agents where each agent is endowed with one object and expresses weak preferences across all objects. Agents and objects should be inputted as integer values. E.g. for a three agent market, agents are represented by 0,1,2 with endowments 0,1,2. Weak preferences allow agents to be indifferent between subsets of objects in the market. E.g. If Agent 0 prefers either of object 0 or object 1 to object 2, we represent Agent 0's preferences = [{1,2},{0}].

A housing market is initialised with all preferences represented as a list of agent preferences, each composed by a list of sets of objects. Extending the above example:

your_market_preferences = [
[{1,2},{0}],
[{2},{1},{0}],
[{1},{0,2}],
]

your_market = HousingMarket(n_agents = 3, market_preferences = your_market_preferences)

Users can observe the algorithm as its executing with an optional verbose setting:
your_market = HousingMarket(n_agents = 3, market_preferences = your_market_preferences, verbose = True)

Finally the extended TTC algorithm is executed upon running the execute method:
your_market.execute_extended_ttc() which returns an Allocation:Dict[agent (int), object (int)] representing the final allocation of each agent.

## Acknowledgements
This implementation is based on work by Xinsheng Xiong, Xianjia Wang & Kun He in 'A new allocation rule for the housing market problem with ties' found at: https://doi.org/10.1007/s10878-021-00727-z.


