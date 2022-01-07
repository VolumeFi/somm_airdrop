# %%
import pandas as pd
from tqdm import tqdm
import numpy as np
import math
import json
from pathlib import Path
from utils import plot_utils

from typing import Any, Dict, List, TypedDict

REWARD_PER_POOL = 200000

Wallet = str

class Account(TypedDict):
    address: str
    balance: List[Dict]
    amount: str

PoolName = str
PoolAddress = str

class OsmosisData(TypedDict):
    num_accounts: int 
    pool_token_counter: Dict[PoolName, dict]
    accounts: Dict[Wallet, Account]

class OsmosisSnapshotRewards:

    def __init__(self):
        self.osmosis_data = self.load_snapshot_data()
        self.total_liquidity_per_pool: Dict[PoolName, Any] = (
            self.osmosis_data["pool_token_counter"])
        self.liquidity_per_user = self.osmosis_data["accounts"]
        self.user_shares_per_pool: Dict[str, Dict] = self.get_user_shares_per_pool()
        self.wallet_reward_map: Dict[Wallet, float] = self.compute_wallet_reward_map()

    def load_snapshot_data(self):
        data_path = Path("../data/osmosis_snapshot.json").resolve()
        with open(data_path, "r") as f:
            osmosis_data: OsmosisData = json.load(f)
        return osmosis_data
    
    def custom_pool_liquidity_map(self) -> Dict[PoolName, float]:
        ...
    
    @property
    def num_pools(self) -> int:
        pool_totals = [
            int(v['pool_total']) for v in self.total_liquidity_per_pool.values()]
        num_pools: int = len(pool_totals)
        return num_pools
    
    def get_user_shares_per_pool(self) -> Dict[str, Dict]:
        # Maps user address to pool to pool share
        user_shares_per_pool: Dict[str, Dict] = {}

        # Compute pool shares for each user
        for wallet_address, user_row in self.liquidity_per_user.items():
            user_shares_per_pool[wallet_address] = {}

            for pool_amount in user_row['balance']:
                user_share = int(pool_amount['amount']) / int(
                    self.total_liquidity_per_pool[pool_amount['denom']]['pool_total'])
                user_shares_per_pool[wallet_address][pool_amount['denom']] = user_share
        return user_shares_per_pool
    
    def compute_wallet_reward_map(self) -> Dict[Wallet, float]:
        wallet_reward_map: Dict[Wallet, float] = {}
        wallet_address: str
        pool_shares: Dict[PoolName, float]
        for wallet_address, pool_shares in self.user_shares_per_pool.items():
            wallet_reward_map[wallet_address] = 0
            for pool_name, user_pool_share in pool_shares.items():
                wallet_reward_map[wallet_address] += (
                    user_pool_share * REWARD_PER_POOL)
        return wallet_reward_map

    
    def compute_redistribution_amounts(self):

        breakpoint()

        # Impose whale cap
        total_redistribution_amount = 0
        for wallet_address, wallet_reward in self.wallet_reward_map.items():
            if wallet_reward > 50000:
                total_redistribution_amount += wallet_reward - 50000
                self.wallet_reward_map[wallet_address] = 50000
        
        redistribution_amount = total_redistribution_amount / len(self.wallet_reward_map)
        for wallet_address, reward in self.wallet_reward_map.items():
            self.wallet_reward_map[wallet_address] += redistribution_amount

        json_save_path = Path(
            '../token_rewards/osmosis_pool_rewards.json').resolve()
        json_save_path.parent.mkdir(exist_ok=True, parents=True)

        with open(json_save_path, 'w') as fp:
            json.dump(self.wallet_reward_map, fp)

        plot_utils.plot_reward_distribution(self.wallet_reward_map, save_path=Path(
            "../plots/osmosis_pool_rewards.png").resolve(), title="Osmosis LP SOMM Rewards")


if __name__ == "__main__":

    osr = OsmosisSnapshotRewards()
    osr.compute_redistribution_amounts()
