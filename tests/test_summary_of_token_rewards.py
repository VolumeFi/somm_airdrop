#!/usr/bin/env python

import pytest
import os
from somm_airdrop import utils
import summary_of_token_rewards as sotr
from typing import Dict

Wallet = str
TokenRewards = sotr.TokenRewards

class TestTokenRewards:

    @pytest.fixture
    def token_rewards(self) -> sotr.TokenRewards:
        return sotr.TokenRewards()

    def test_load_paths_somm(self, token_rewards: TokenRewards):
        for airdrop_group, path in token_rewards.reward_paths_map_usomm.items():
            assert os.path.exists(os.path.join(token_rewards.dir, path))

    def test_load_paths_usomm(self, token_rewards: TokenRewards):
        for airdrop_group, path in token_rewards.reward_paths_map_somm.items():
            assert os.path.exists(os.path.join(token_rewards.dir, path))

    def test_reward_totals(self):
        ...

    def test_total_distribution(self, token_rewards: TokenRewards):
        somm_total: float = token_rewards.total_distribution
        usomm_total: int = utils.somm2usomm(token_rewards.total_distribution)

        correct_total = 14.6 * 1e6
        assert round(somm_total) == correct_total
        assert round(usomm_total / 1e6) == correct_total

    def test_reward_pcts(self, token_rewards: TokenRewards):
        reward_pcts: Dict[sotr.AirdropGroup, float] = token_rewards.reward_pcts
        assert sum(reward_pcts.values()) == 1.0 # pcts sum to 1
        assert reward_pcts['uniswap_v3'] > reward_pcts['somm_app']
        assert reward_pcts['somm_app'] > reward_pcts['osmosis']

    def test_usomm_rewards(self, token_rewards: TokenRewards):
        usomm_rewards: Dict[
            sotr.AirdropGroup, Dict[Wallet, int]]  = token_rewards.usomm_rewards
        group_totals: Dict[sotr.AirdropGroup, int] = {}

        total_usomm_rewards: int = 0
        for airdrop_group in usomm_rewards:
            group_total: int = sum(usomm_rewards[airdrop_group].values())
            group_totals[airdrop_group] = group_total
            total_usomm_rewards += group_total
        
        assert round(total_usomm_rewards / 1e6) == 14.6 * 1e6
        
