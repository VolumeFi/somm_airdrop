import os
from typing import List
import numpy as np
import pandas as pd

from somm_airdrop import somm_user_data

"""Notes / Objectives 
A user maps to an address

LPPosition 
- timestamp the position started 
- timestamp the position ended 
- the sender of the transaction (the user)
- liquidity amt provided
- duration of the position(s)
- pool, tokens, etc. 
- v2 or v3
"""


class BigQueryV2MintsBurnsTable(pd.DataFrame):
    """
    Columns: 
        block_timestamp, 
        transaction_hash 
        amt0:
        amt1:
        pair: Token pair address.
        sender_address: User that added liquidity to the pool.  
    """


class LPActionsTableV2(pd.DataFrame):
    """
    Usage example:
    >>> mints_burns_df = LPActionsTableV2()

    Index:
        block_timestamp 

    Columns:
        liq (int): Liquidity added to the pool. If negative, 'liq' reflects 
            the amount burned.
        pair (str): Token pair address
        sender_address (str): User that added liquidity to the pool.  
    """
    mints_table: BigQueryV2MintsBurnsTable # read from csv 
    burns_table: BigQueryV2MintsBurnsTable # read from csv

    def __new__(cls) -> 'LPActionsTableV2':
        """Returns the combined LP actions table."""

        cls.mints_table: BigQueryV2MintsBurnsTable # read from csv 
        cls.burns_table: BigQueryV2MintsBurnsTable # read from csv
        cls._append_liquidity_columns()
        cls._drop_amts_columns()
        mints_burns_table: BigQueryV2MintsBurnsTable = pd.concat(
            [cls.mints_table, cls.burns_table], ignore_index=True)
        mints_burns_table.set_index('block_timestamp', inplace=True)
        mints_burns_table.sort_index(axis=0, inplace=True)
        return mints_burns_table

    @staticmethod
    def _create_liquidity_column(table: BigQueryV2MintsBurnsTable, 
                                 tx_type: str) -> np.ndarray:
        if not tx_type in ['mint', 'burn']:
            raise ValueError()

        liq_col: np.ndarray = np.sqrt(table['amt0'] * table['amt1'])
        if tx_type == 'burn':
            liq_col = -liq_col
        return liq_col

    @classmethod    
    def _append_liquidity_columns(cls):
        cls.mints_table['liq'] = cls._create_liquidity_column(
            table=cls.mints_table, tx_type='mint')
        cls.burns_table['liq'] = cls._create_liquidity_column(
            table=cls.burns_table, tx_type='burn')
    
    @classmethod    
    def _drop_amts_columns(cls):
        cls.mints_table.drop(columns=['amt0', 'amt1'], inplace=True)
        cls.burns_table.drop(columns=['amt0', 'amt1'], inplace=True)
    
"""
Let's assume you have the mints and burns. How should you 

"""
df: LPActionsTableV2

def filter_v2_lp_actions_by_somm_users(df: LPActionsTableV2) -> pd.DataFrame:
    somm_users_v2: List[str] = somm_user_data.v2_user_addresses()
    somm_users_mask: List[bool] = [
        (user in somm_users_v2) for user in df['sender_addresses']]
    return df.loc[somm_users_mask]
    ...


# TODO Below 

class LPActionsTableV3:
    ...

def filter_v3_lp_actions_by_somm_users(df: LPActionsTableV3):
    somm_users_v3: List[str] = somm_user_data.v3_user_addresses()
    somm_users_mask: List[bool] = [
        (user in somm_users_v3) for user in df['sender_addresses']]
    return df.loc[somm_users_mask]