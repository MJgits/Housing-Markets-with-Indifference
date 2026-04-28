from WeakHousingMarketAlgorithms import (
    MarketPreferences,
    ETTC_HousingMarket,
    PlaxtonAlgo1
)


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
   
    xiong_market_fig2 = ETTC_HousingMarket(xiong_preferences_fig2)
    # fig2_allocation = xiong_market_fig2.execute_extended_ttc(verbose=True)
    # print(f"fig 2 allocation return: {fig2_allocation}")
    


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

    xiong_market_table_2 = ETTC_HousingMarket(xiong_preferences_table_2)
    # xiong_market_table_2.execute_extended_ttc(verbose=True)


    # Agent 5 loses its object and then receives it back. Allocation is unchanged even when we force agent 5 to only prefer object 5
    nb_test_preferences: MarketPreferences = [
        [{0,1},{2,3,4,5,6}],
        [{2},{6},{0,1,3,4,5}],
        [{2,3},{0,1,4,5,6}],
        [{2},{0,1,3,4,5,6}],
        [{0,4,5},{1,2,3,6}],
        [{5,6},{0,1,2,3,4}],
        [{4},{0,1,2,3,5,6}]
    ]

    nb_housing_market = ETTC_HousingMarket(nb_test_preferences)
    # nb_housing_market.execute_extended_ttc(verbose=True)

    # agent 5 only prefers its own object now but has no change in final allocation.
    nb_misreport_5: MarketPreferences = [
        [{0,1},{2,3,4,5,6}],
        [{2},{6},{0,1,3,4,5}],
        [{2,3},{0,1,4,5,6}],
        [{2},{0,1,3,4,5,6}],
        [{0,4,5},{1,2,3,6}],
        [{5},{0,1,2,3,4,6}],
        [{4},{0,1,2,3,5,6}]

    ]

    nb_5_misreport = ETTC_HousingMarket(nb_misreport_5)
    # nb_5_misreport.execute_extended_ttc(verbose=True)


    saban_sp_market: MarketPreferences = [
        [{2,4},{0,1,3}],
        [{0}, {3}, {1,2,4}],
        [{0},{1,2,3,4}],
        [{1,2},{0,3,4}],
        [{3},{0,1,2,4}]
    ]

    saban_agent_2_misreport: MarketPreferences = [
        [{2,4},{0,1,3}],
        [{3}, {0,1,2,4}],
        [{0},{1,2,3,4}],
        [{1,2},{0,3,4}],
        [{3},{0,1,2,4}]
    ]

    saban_market = ETTC_HousingMarket(saban_sp_market).execute(verbose=True)
    saban_misreport_market = ETTC_HousingMarket(saban_agent_2_misreport).execute(verbose= True) 


    truthful_preferences: MarketPreferences = [
        [{0,1,2}],
        [{0},{1,2}],
        [{0},{1},{2}]
    ]

    misreported_preferences: MarketPreferences = [
        [{2},{0,1}],
        [{0},{1,2}],
        [{0},{1},{2}]
    ]
    detected_bossiness_truthful_market = ETTC_HousingMarket(truthful_preferences).execute(verbose=True)
    print("============================================\n====================================")
    detected_bossiness_manipulated_market = ETTC_HousingMarket(misreported_preferences).execute(verbose=True)

    print("plaxton test\n\n\n\n\n\n")

    plaxton_test_on_saban = PlaxtonAlgo1(saban_sp_market).execute()
    plaxton_test_saban_misreport = PlaxtonAlgo1(saban_agent_2_misreport).execute()
    
    if plaxton_test_on_saban == plaxton_test_saban_misreport:
        print("saban strategy proof")



    print(plaxton_test_on_saban)
    print(plaxton_test_saban_misreport)