#%%
import somm_airdrop
from somm_airdrop.uni_v2_positions import data_transforms
from somm_airdrop import somm_user_data
import pandas as pd
from typing import List

actions = data_transforms.ActionsPart1V2Factory().table
v2_users: List[str] = somm_user_data.v2_user_addresses()
for user in v2_users:

    breakpoint()

print('yas')