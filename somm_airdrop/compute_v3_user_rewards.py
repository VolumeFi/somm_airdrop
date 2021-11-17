import pandas as pd
from tqdm import tqdm
import numpy as np
import v3_pool_info
import math
import json
from plotting_utils import plot_v3_pool_rewards
from matplotlib import pyplot as plt


if __name__ == "__main__":
    v3_mints: pd.DataFrame = pd.read_csv(
        "../query_results/uniswap_v3_mints.csv",
    ).sort_values('block_timestamp', ignore_index=True)

    v3_burns: pd.DataFrame = pd.read_csv(
        "../query_results/uniswap_v3_burns.csv",
    ).sort_values('block_timestamp', ignore_index=True)

    user_token_rewards = {}

    for pool_idx, pool in tqdm(enumerate(v3_pool_info.AIRDROP_POOLS), total=len(v3_pool_info.AIRDROP_POOLS)):

        pool_mints = v3_mints[v3_mints['pool'] == pool].copy()
        pool_burns = v3_burns[v3_burns['pool'] == pool].copy()

        pool_mints.loc[:, "block_timestamp"] = pd.to_datetime(
            pool_mints.loc[:, "block_timestamp"])
        pool_burns.loc[:, "block_timestamp"] = pd.to_datetime(
            pool_burns.loc[:, "block_timestamp"])

        used_pool_burns = []
        pool_v3_user_positions = {}

        # Construct positions for each user
        # TODO: Use October 31, 2021 as end_time
        for idx, mint in tqdm(pool_mints.iterrows(), total=pool_mints.shape[0], leave=False):
            # Ignore mints before the cutoff date
            if mint["block_timestamp"] >= pd.Timestamp("2021-10-31", tz="UTC"):
                continue

            relevant_burns = pool_burns[
                (pool_burns['liquidity'] == mint['liquidity']) &
                (pool_burns["from_address"] == mint["from_address"]) &
                (pool_burns["pool"] == mint["pool"]) &
                (~pool_burns.index.isin(used_pool_burns)) &
                (pool_burns['block_timestamp'] > mint['block_timestamp'])
            ]

            end_time = None
            if len(relevant_burns) > 0:
                used_pool_burns.append(relevant_burns.index[0])
                burn = relevant_burns.iloc[0]
                end_time = burn['block_timestamp']

            if end_time is None or end_time > pd.Timestamp("2021-10-31", tz="UTC"):
                end_time = pd.Timestamp("2021-10-31", tz="UTC")

            position = {
                "start": mint['block_timestamp'],
                "end": end_time,
                "liquidity": mint['liquidity']
            }
            if mint['from_address'] in pool_v3_user_positions:
                pool_v3_user_positions[mint['from_address']].append(position)
            else:
                pool_v3_user_positions[mint['from_address']] = [position]

        # Assign score to each position and sum across positions
        pool_user_score = {}
        for user_address, user_positions in tqdm(pool_v3_user_positions.items(), leave=False):
            user_score = 0
            for position in user_positions:
                position_score = math.isqrt(int(
                    position['liquidity'])) * int((position['end'] - position['start']).total_seconds())
                user_score += position_score

            pool_user_score[user_address] = user_score

        total_pool_score = sum(pool_user_score.values())

        # Compute fraction of reward for each user
        for user_address, user_score in tqdm(pool_user_score.items(), leave=False):
            user_pool_token_reward = (
                user_score / total_pool_score) * v3_pool_info.TOKEN_REWARD
            if user_address in user_token_rewards:
                user_token_rewards[user_address] += user_pool_token_reward
            else:
                user_token_rewards[user_address] = user_pool_token_reward

    # Impose whale cap
    total_redistribution_amount = 0
    for user_address, user_reward in user_token_rewards.items():
        if user_reward > 50000:
            total_redistribution_amount += user_reward - 50000
            user_token_rewards[user_address] = 50000

    # Redistribute somm from whale cap uniformly
    participation_reward = total_redistribution_amount/len(user_token_rewards)
    for user_address, user_reward in user_token_rewards.items():
        user_token_rewards[user_address] += participation_reward

    with open('v3_pool_rewards.json', 'w') as fp:
        json.dump(user_token_rewards, fp)
