# -*- coding: utf-8 -*-

import os
import json
from typing import Dict, List
from pprint import pprint
import collections


TokenRewardSummary = collections.namedtuple(
    "TokenRewardSummary", 
    field_names=["total_num_tokens", "reward_totals", "reward_pcts"])

AirdropGroup = str # Osmosis, SOMM app, or UNI v3
Wallet = str

class TokenRewards:

    reward_paths_map_usomm: Dict[str, str] = {
        'osmosis': 'osmosis_pool_rewards_usomm.json',
        'somm_app': 'somm_app_rewards_usomm.json',
        'uniswap_v3': 'uniswap_v3_pool_rewards_usomm.json'}

    reward_paths_map_somm: Dict[str, str] = {
        'osmosis': os.path.join(
            'old_rewards_in_units_somm', 'osmosis_pool_rewards.json'),
        'somm_app': os.path.join(
            'old_rewards_in_units_somm', 'somm_app_rewards.json'),
        'uniswap_v3': os.path.join(
            'old_rewards_in_units_somm', 'uniswap_v3_pool_rewards.json'),
        }

    def __init__(self) -> None:
        self.dir = os.path.join("token_rewards")
        self.reward_paths = os.listdir(self.dir)
        self.usomm_totals: Dict[AirdropGroup, int] = {}
        self.reward_totals: Dict[str, float] = self.compute_reward_totals()
        self.total_distribution: float = self._total_distribution()
        self.reward_pcts: Dict[AirdropGroup, float] = self._reward_pcts()
        self.usomm_rewards: Dict[
            AirdropGroup, Dict[Wallet, int]] = self.compute_usomm_rewards()

    def compute_reward_totals(self) -> Dict[str, float]:
        reward_totals: Dict[str, float]= {}
        for airdrop_group in self.reward_paths_map_somm:
            path = os.path.join(
                self.dir, self.reward_paths_map_somm[airdrop_group])

            with open(path, "r") as f:
                data = json.load(f)
                reward_totals[airdrop_group] = sum(data.values())
        return reward_totals
    
    
    def _total_distribution(self) -> float:
        """The total number of SOMM tokens going out in the airdrop."""
        return sum(self.reward_totals.values())

    def _reward_pcts(self) -> Dict[AirdropGroup, float]:
        return {
            k: (v / self.total_distribution) 
            for k, v in self.reward_totals.items()}

    def summary(self, print_it: bool) -> TokenRewardSummary: 

        if print_it:
            num_somm: int = self.total_distribution
            print(f"\nReward totals (SOMM): num_tokens = {num_somm}")
            pprint(self.reward_totals)
            print("\nReward percentages:")
            pprint(self.reward_pcts)

        return TokenRewardSummary(
            total_num_tokens=self.total_distribution, 
            reward_totals=self.reward_totals, 
            reward_pcts=self.reward_pcts)

    def compute_usomm_rewards(self) -> Dict[AirdropGroup, Dict[Wallet, int]]:
        groupwise_usomm_wallet_reward_maps: Dict[AirdropGroup, Dict[Wallet, int]] = {}
        for airdrop_group in self.reward_paths_map_usomm:
            read_path = os.path.join(
                self.dir, 
                self.reward_paths_map_somm[airdrop_group])

            with open(read_path, "r") as f:
                wallet_reward_map = json.load(f)
            usomm_wallet_reward_map = {
                k:int(v * 1e6) for k, v in wallet_reward_map.items()}

            self.usomm_totals[airdrop_group] = sum(
                usomm_wallet_reward_map.values())
            groupwise_usomm_wallet_reward_maps[airdrop_group] = (
                usomm_wallet_reward_map)

        return groupwise_usomm_wallet_reward_maps

    def save_usomm_rewards(self, overwrite: bool = False) -> None:

        for airdrop_group in self.reward_paths_map_usomm:
            usomm_wallet_reward_map: Dict[Wallet, int] = (
                self.usomm_rewards[airdrop_group])

            write_path = os.path.join(
                self.dir, 
                self.reward_paths_map_usomm[airdrop_group])

            if overwrite:
                with open(write_path, 'w+') as f:
                    json.dump(usomm_wallet_reward_map, f)
            else:
                if not os.path.exists(write_path):
                    with open(write_path, 'w+') as f:
                        json.dump(usomm_wallet_reward_map, f)

if __name__ == "__main__":
    token_rewards = TokenRewards()
    token_rewards.summary(print_it=True)
    token_rewards.save_usomm_rewards(overwrite=True)
    num_tokens: int = sum(token_rewards.usomm_totals.values())
    print(f"\nuSOMM totals: num_tokens = {num_tokens}")
    pprint(token_rewards.usomm_totals)