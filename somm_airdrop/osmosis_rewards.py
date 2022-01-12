#!/usr/bin/env python3
"""A module for parsing Osmosis data from a snapshot and computing the token 
distribution to each wallet in the Osmosis portion of the SOMM airdrop.
Ref: https://sommelier.finance/

Examples:
  >>> osr = OsmosisSnapshotRewards()
  >>> osr.compute_redistribution_amounts()
"""
import json
from pathlib import Path
from utils import plot_utils

from typing import Any, Dict, List, TypedDict

REWARD_PER_POOL = 200000

Wallet = str

class Account(TypedDict):
    """An Osmosis account.

    Keys: ValueTypes
        address: str 
        balance: List[dict]
        amount: str
    """
    address: str
    balance: List[dict]
    amount: str

PoolName = str
PoolAddress = str
PoolShareMap = Dict[PoolName, float] 

class OsmosisData(TypedDict):
    """A snapshot JSON for the Osmosis pools in SIPS-002.  

    Keys: ValueTypes
        num_accounts: int 
        pool_token_counter: Dict[PoolName, dict]
        accounts: Dict[Wallet, Account]
    """
    num_accounts: int 
    pool_token_counter: Dict[PoolName, dict]
    accounts: Dict[Wallet, Account]

class OsmosisSnapshotRewards:
    """
    
    Attributes:
        pool_to_liquidity_map: Dict[PoolName, int]: Maps a pool to the number of 
            tokens in the pool.
        wallet_to_account (Dict[Wallet, Account]): Maps an Osmosis wallet 
            address to its corresponding account. 
        wallet_to_pool_share_map (Dict[str, PoolShareMap])
        wallet_reward_map (Dict[Wallet, float])
    """

    def __init__(self):
        self.osmosis_data: OsmosisData = self.load_snapshot_data()
        self.wallet_to_account: Dict[Wallet, Account] = (
            self.osmosis_data["accounts"])
        self.pool_to_liquidity_map: Dict[PoolName, int] = (
            self.get_pool_to_liquidity_map(
                wallet_to_account=self.wallet_to_account))
        """For some reason, the pool liquidity values from 'pool_token_counter' 
        don't match the sums of the corresponding quantities from each wallet.
        """
        # self.pool_to_liquidity_map: Dict[PoolName, Any] = (
        #     self.osmosis_data["pool_token_counter"])
        self.wallet_to_pool_share_map: Dict[str, PoolShareMap] = (
            self.map_wallets_to_pool_share_maps())
        self.wallet_reward_map: Dict[Wallet, float] = (
            self.compute_wallet_reward_map())

    def load_snapshot_data(self) -> OsmosisData:
        data_path = Path("../data/osmosis_snapshot.json").resolve()
        with open(data_path, "r") as f:
            osmosis_data: OsmosisData = json.load(f)
        return osmosis_data
    
    def get_pool_to_liquidity_map(self, 
                               wallet_to_account: Dict[Wallet, Account]
                               ) -> Dict[PoolName, int]:
        pool_to_liquidity_map = {}
        for wallet_address, account in wallet_to_account.items():
            for pool_dict in account["balance"]:
                pool_name = pool_dict["denom"]
                
                if pool_name in pool_to_liquidity_map:
                    pool_to_liquidity_map[pool_name]['pool_total'] += int(
                        pool_dict["amount"])
                    pool_to_liquidity_map[pool_name]['coin_total'] += int(
                        pool_dict["amount"])
                else:
                    pool_to_liquidity_map[pool_name] = {}
                    pool_to_liquidity_map[pool_name]['pool_total'] = int(
                        pool_dict["amount"])
                    pool_to_liquidity_map[pool_name]['coin_total'] = int(
                        pool_dict["amount"])
        return pool_to_liquidity_map
    
    @property
    def num_pools(self) -> int:
        pool_totals = [int(v['pool_total']) 
                       for v in self.pool_to_liquidity_map.values()]
        num_pools: int = len(pool_totals)
        return num_pools
    
    def map_wallets_to_pool_share_maps(self) -> Dict[Wallet, PoolShareMap]:
        # Maps wallet address to a dictionary of pool shares
        wallet_to_pool_share_map: Dict[Wallet, PoolShareMap] = {}

        # Compute pool shares for each wallet
        wallet_row: Account
        for wallet_address, wallet_row in self.wallet_to_account.items():
            wallet_to_pool_share_map[wallet_address] = {}

            for pool_amount in wallet_row['balance']:
                wallet_tokens_in_pool: int = int(pool_amount['amount'])
                total_tokens_in_pool: int = int(self.pool_to_liquidity_map[
                    pool_amount['denom']]['pool_total'])
                pool_share: float = (
                    wallet_tokens_in_pool / total_tokens_in_pool)
                wallet_to_pool_share_map[wallet_address][
                    pool_amount['denom']] = pool_share
        return wallet_to_pool_share_map
    
    def compute_wallet_reward_map(self) -> Dict[Wallet, float]:
        wallet_reward_map: Dict[Wallet, float] = {}
        wallet_address: str
        pool_shares: Dict[PoolName, float]
        for wallet_address, pool_shares in self.wallet_to_pool_share_map.items():
            wallet_reward_map[wallet_address] = 0
            for pool_name, wallet_pool_share in pool_shares.items():
                wallet_reward_map[wallet_address] += (
                    wallet_pool_share * REWARD_PER_POOL)
        return wallet_reward_map

    def compute_redistribution_amounts(self):

        # Impose whale cap
        total_redistribution_amount = 0
        for wallet_address, wallet_reward in self.wallet_reward_map.items():
            if wallet_reward > 50000:
                total_redistribution_amount += wallet_reward - 50000
                self.wallet_reward_map[wallet_address] = 50000
        
        num_wallets: int = len(self.wallet_reward_map)
        redistribution_amount = total_redistribution_amount / num_wallets
        for wallet_address in self.wallet_reward_map:
            self.wallet_reward_map[wallet_address] += redistribution_amount

        json_save_path = Path(
            '../token_rewards/osmosis_pool_rewards.json').resolve()
        json_save_path.parent.mkdir(exist_ok=True, parents=True)

        with open(json_save_path, 'w') as fp:
            json.dump(self.wallet_reward_map, fp)

        plot_utils.plot_reward_distribution(
            wallet_to_reward=self.wallet_reward_map, 
            save_path=Path("../plots/osmosis_pool_rewards.png").resolve(), 
            title="Osmosis LP SOMM Rewards")


if __name__ == "__main__":

    osr = OsmosisSnapshotRewards()
    osr.compute_redistribution_amounts()
