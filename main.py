
from WeakHousingMarketAlgorithm import (MarketPreferences,
                                        Allocation,# MarketPreferences is type definition to help with input structure
                                        HousingMarket) # HousingMarket handles the algorithm

# Helps with input structure
from WeakHousingMarketAlgorithm import MarketPreferences 



'''
Two example markets are presented below from Xiong 2021. This shows example usage.
'''


if __name__ == "__main__":

    xiong_preferences_fig2: MarketPreferences = [
                                [{0},           {1,2,3,4,5}],
                                [{0},{3,4},     {1,2,5}],
                                [{5},           {0,1,2,3,4}],
                                [{2,3,4,5},     {0,1}],
                                [{3,4},         {0,1,2,5}],
                                [{4},           {0,1,2,3,5}]]


    xiong_market_fig2 = HousingMarket(6, xiong_preferences_fig2)
    fig2_allocation: Allocation = xiong_market_fig2.execute_extended_ttc()
    print(f"fig 2 allocation return: {fig2_allocation}")
    


    xiong_preferences_table_2: MarketPreferences = [
        [{0},       {  1,2,3,4,5,6,7,8,9,10}],
        [{0},{1},   {    2,3,4,5,6,7,8,9,10}],
        [{5},       {0,1,2,3,4,  6,7,8,9,10}],
        [{2,3,4,5}, {0,1,        6,7,8,9,10}],
        [{3,4,6},   {0,1,2,    5,  7,8,9,10}],
        [{3,4},     {0,1,2,    5,6,7,8,9,10}],
        [{3},{6},   {0,1,2,  4,5,  7,8,9,10}],
        [{3,7,8},   {0,1,2,  4,5,6,    9,10}],
        [{2,8},     {0,1,  3,4,5,6,7,  9,10}],
        [{0,1,9},   {    2,3,4,5,6,7,8,  10}],
        [{4,8,10},  {0,1,2,3,  5,6,7,  9   }]]

    xiong_market_table_2 = HousingMarket(11, xiong_preferences_table_2, verbose=True)
    xiong_market_table_2.execute_extended_ttc()

    
