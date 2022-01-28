# -*- coding: utf-8 -*-

import os
import json
from typing import Dict, List
from pprint import pprint
import collections


TokenRewardSummary = collections.namedtuple(
    "TokenRewardSummary", 
    field_names=["total_num_tokens", "reward_totals", "reward_pcts"])

Group = str # Osmosis, SOMM app, or UNI v3
Wallet = str

class TokenRewards:

    reward_paths_map_usomm = {
        'osmosis': 'osmosis_pool_rewards_usomm.json',
        'somm_app': 'somm_app_rewards_usomm.json',
        'uniswap_v3': 'uniswap_v3_pool_rewards_usomm.json'}


    def __init__(self) -> None:
        self.token_rewards_dir = os.path.join("token_rewards")
        self.reward_paths = os.listdir(self.token_rewards_dir)
        self.reward_paths_map = self.get_reward_paths_map()
        self.usomm_totals: Dict[Group, int] = {}

    def get_reward_paths_map(self) -> Dict[str, str]:
        groups = ["osmosis", "somm_app", "uniswap_v3"]

        reward_paths_map = {
            'osmosis': 'osmosis_pool_rewards.json',
            'somm_app': 'somm_app_rewards.json',
            'uniswap_v3': 'uniswap_v3_pool_rewards.json'}
        return reward_paths_map

    def summary(self, print_it: bool) -> TokenRewardSummary: 

        reward_totals: Dict[str, float]= {}
        for distribution_group in self.reward_paths_map:
            path = os.path.join(
                self.token_rewards_dir, self.reward_paths_map[distribution_group])

            with open(path, "r") as f:
                data = json.load(f)
                reward_totals[distribution_group] = sum(data.values())
            

        total_distribution = sum(reward_totals.values())
        reward_pcts = {
            k: (v / total_distribution) for k, v in reward_totals.items()}

        if print_it:
            print(f"Total distribution\t{total_distribution}")
            print("\nReward totals (SOMM):")
            pprint(reward_totals)
            print("\nReward percentages:")
            pprint(reward_pcts)

        return TokenRewardSummary(
            total_num_tokens=total_distribution, 
            reward_totals=reward_totals, 
            reward_pcts=reward_pcts)

    def compute_usomm_rewards(self, save: bool = True) -> List[Dict[str, int]]:
        maps: List[Dict[str, int]] = [] 
        for distribution_group in self.reward_paths_map_usomm:
            read_path = os.path.join(
                self.token_rewards_dir, 
                self.reward_paths_map[distribution_group])

            with open(read_path, "r") as f:
                wallet_reward_map = json.load(f)
            usomm_wallet_reward_map = {
                k:int(v * 1e6) for k, v in wallet_reward_map.items()}
            write_path = os.path.join(
                self.token_rewards_dir, 
                self.reward_paths_map_usomm[distribution_group])

            self.usomm_totals[distribution_group]: int = sum(
                usomm_wallet_reward_map.values())
            maps.append(usomm_wallet_reward_map)
            if save and (not os.path.exists(write_path)):
                with open(write_path, 'w+') as f:
                    json.dump(usomm_wallet_reward_map, f)
        return maps

if __name__ == "__main__":
    token_rewards = TokenRewards()
    token_rewards.summary(print_it=True)
    token_rewards.compute_usomm_rewards(save=True)
    num_tokens: int = sum(token_rewards.usomm_totals.values())
    print(f"\nuSOMM totals: num_tokens = {num_tokens}")
    pprint(token_rewards.usomm_totals)