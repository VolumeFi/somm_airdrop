#!/usr/bin/env python
#%%
"""
All v2 liquidity provider data was queried using Google BigQuery's public 
ethereum dataset on 2021-11-08.


"""

import os
import pandas as pd
from typing import Optional

DIR_PATH: str = os.path.join("somm_airdrop", "uni_v2_positions", "data")

# TODO Format the UNI v2 data into the swaps and LP actions paradigm.
class RevenueV2Factory:
    """Liquidity provider revenue table
    
    Attributes:
        table (pd.DataFrame)
    """

    def __init__(self):
        self._table: Optional[pd.DataFrame] = None
    
    @property
    def table(self) -> pd.DataFrame:
        if self._table is None:
            self._table = self._load_table()
        return self._table

    def _load_table(self) -> pd.DataFrame:
        lp_revenue_paths = [
            os.path.join(DIR_PATH, fp) 
            for fp in os.listdir(DIR_PATH) if "lp-revenue" in fp]
        assert len(lp_revenue_paths) == 1
        file_path = lp_revenue_paths.pop()
        return pd.read_csv(file_path)
        

class ActionsPart1V2Factory:
    """LP actions (adding and removing liquidity) part 1 table"""
    ...
    def __init__(self):
        self._table: Optional[pd.DataFrame] = None
    
    @property
    def table(self) -> pd.DataFrame:
        if self._table is None:
            self._table = self._load_table()
        return self._table

    def _load_table(self) -> pd.DataFrame:
        lp_revenue_paths = [
            os.path.join(DIR_PATH, fp) 
            for fp in os.listdir(DIR_PATH) if "part_1" in fp]
        assert len(lp_revenue_paths) == 1
        file_path = lp_revenue_paths.pop()
        return pd.read_csv(file_path)

class ActionsPart2V2Factory:
    """LP actions (adding and removing liquidity) part 2 table"""
    ...
    def __init__(self):
        self._table: Optional[pd.DataFrame] = None
    
    @property
    def table(self) -> pd.DataFrame:
        if self._table is None:
            self._table = self._load_table()
        return self._table

    def _load_table(self) -> pd.DataFrame:
        lp_revenue_paths = [
            os.path.join(DIR_PATH, fp) 
            for fp in os.listdir(DIR_PATH) if "part_2" in fp]
        assert len(lp_revenue_paths) == 1
        file_path = lp_revenue_paths.pop()
        return pd.read_csv(file_path)

# TODO Find the number of unique v2 users.
