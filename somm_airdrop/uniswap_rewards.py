import pandas as pd
from tqdm import tqdm
import numpy as np
import v3_pool_info
import math
import json
from matplotlib import pyplot as plt
from pathlib import Path
from utils import plot_utils

if __name__ == "__main__":
    v3_mints: pd.DataFrame = pd.read_csv(
        "../data/uniswap_v3_mints.csv",
    ).sort_values('block_timestamp', ignore_index=True)
    v3_burns: pd.DataFrame = pd.read_csv(
        "../data/uniswap_v3_burns.csv",
    ).sort_values('block_timestamp', ignore_index=True)

    # Convert block_timestamp to datetime
    v3_mints.loc[:, "block_timestamp"] = pd.to_datetime(
        v3_mints.loc[:, "block_timestamp"], infer_datetime_format=True)
    v3_burns.loc[:, "block_timestamp"] = pd.to_datetime(
        v3_burns.loc[:, "block_timestamp"], infer_datetime_format=True)

    # Remove mints/burns after Oct 31
    v3_mints = v3_mints[v3_mints["block_timestamp"]
                        < pd.Timestamp("2021-10-31", tz="UTC")]
    v3_burns = v3_burns[v3_burns["block_timestamp"]
                        < pd.Timestamp("2021-10-31", tz="UTC")]

    wallet_rewards = {}

    for pool_idx, pool in tqdm(enumerate(v3_pool_info.AIRDROP_POOLS), total=len(v3_pool_info.AIRDROP_POOLS)):

        pool_mints = v3_mints[v3_mints['pool'] == pool].copy()
        pool_burns = v3_burns[v3_burns['pool'] == pool].copy()

        used_pool_burns = []
        pool_v3_user_positions = {}

        # Construct positions for each use  r
        for idx, mint in tqdm(pool_mints.iterrows(), total=pool_mints.shape[0], leave=False):
            # Ignore mints before the cutoff date

            relevant_burns = pool_burns[
                (pool_burns['liquidity'] == mint['liquidity']) &
                (pool_burns["from_address"] == mint["from_address"]) &
                (pool_burns["pool"] == mint["pool"]) &
                (~pool_burns.index.isin(used_pool_burns)) &
                (pool_burns['block_timestamp'] > mint['block_timestamp'])
            ]

            end_time = pd.Timestamp("2021-10-31", tz="UTC")
            if len(relevant_burns) > 0:
                used_pool_burns.append(relevant_burns.index[0])
                burn = relevant_burns.iloc[0]
                end_time = burn['block_timestamp']

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
            if user_address in wallet_rewards:
                wallet_rewards[user_address] += user_pool_token_reward
            else:
                wallet_rewards[user_address] = user_pool_token_reward


    plot_utils.plot_reward_distribution(wallet_rewards, save_path=Path(
        "../plots/uniswap_v3_pool_rewards_no_cap.png").resolve())


    # Impose whale cap
    total_redistribution_amount = 0
    for user_address, user_reward in wallet_rewards.items():
        if user_reward > 50000:
            total_redistribution_amount += user_reward - 50000
            wallet_rewards[user_address] = 50000

    # Redistribute somm from whale cap uniformly
    participation_reward = total_redistribution_amount/len(wallet_rewards)
    for user_address, user_reward in wallet_rewards.items():
        wallet_rewards[user_address] += participation_reward

    json_save_path = Path(
        '../token_rewards/uniswap_v3_pool_rewards.json').resolve()
    json_save_path.parent.mkdir(exist_ok=True, parents=True)

    with open(json_save_path, 'w') as fp:
        json.dump(wallet_rewards, fp)

    plot_utils.plot_reward_distribution(wallet_rewards, save_path=Path(
        "../plots/uniswap_v3_pool_rewards.png").resolve(), title="Uniswap V3 Pools SOMM Rewards")
