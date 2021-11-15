#%%
import somm_airdrop
from somm_airdrop.uni_v2_positions import data_transforms
from somm_airdrop.somm_users import somm_user_data
import pandas as pd
from typing import List


#%% Actions table exploration

def actions_table_exploration():
    actions = data_transforms.ActionsPart1V2Factory().table
    v2_users: List[str] = somm_user_data.v2_user_addresses()
    for user in v2_users:

        breakpoint()

    print('yas')

#%%  Price data 
import secret
import messari
from messari import timeseries
messari.MESSARI_API_KEY = secret.MY_API_KEY

def prices_test_query():
    assets = ['btc', 'eth']
    metric = "price"
    start = "2020-06-01"
    end = "2020-07-01"
    prices_df = timeseries.get_metric_timeseries(
        asset_slugs=assets, asset_metric=metric, start=start, end=end)
    breakpoint()
    
# prices_test_query() # It works. Now, we just need parameters.


