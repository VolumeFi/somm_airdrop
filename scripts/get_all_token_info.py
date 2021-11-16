import __init__
import os
import json

from somm_airdrop import etherscan
from somm_airdrop.somm_users import somm_user_data

import pandas as pd
from somm_airdrop.etherscan.token_info_connector import TokenInfoMap
from typing import List, Set

def _get_v2_somm_app_token_ids() -> Set[str]:
    """
    Returns:
        (Set[str]): Token IDs for all token pairs that Sommelier app users 
            provided liquidity for on Uniswap v2.
    """
    mints_burns_df: pd.DataFrame = pd.concat(
        objs=[somm_user_data.v2_mints(), somm_user_data.v2_burns()])
    unique_token_0 = set(mints_burns_df.token0.unique())
    unique_token_1 = set(mints_burns_df.token1.unique())
    token_ids: Set[str] = unique_token_0.union(unique_token_1)
    return token_ids

def _get_v3_somm_app_token_ids() -> Set[str]:
    """
    Returns:
        (Set[str]): Token IDs for all token pairs that Sommelier app users 
            provided liquidity for on Uniswap v3.
    """
    mints_burns_df: pd.DataFrame = pd.concat(
        objs=[somm_user_data.v3_mints(), somm_user_data.v3_burns()])
    unique_token_0 = set(mints_burns_df.token0.unique())
    unique_token_1 = set(mints_burns_df.token1.unique())
    token_ids: Set[str] = unique_token_0.union(unique_token_1)
    return token_ids

def get_all_somm_app_token_ids() -> List[str]:
    v2_token_ids: Set[str] = _get_v2_somm_app_token_ids() 
    v3_token_ids: Set[str] = _get_v3_somm_app_token_ids()
    all_token_ids: List[str] = sorted(list(v2_token_ids.union(v3_token_ids)))
    return all_token_ids

if __name__ == "__main__":
    token_ids: List[str] = get_all_somm_app_token_ids()
    tic = etherscan.TokenInfoConnector()
    print("Now querying token info.")
    token_info_map: TokenInfoMap = tic.get_token_info(
        token_ids=token_ids, save=True, verbose=True)
    print("Token info saved.")
    


