import pandas as pd
from tqdm import tqdm
import numpy as np
import math
import json

REWARD_PER_POOL = 200000


if __name__ == "__main__":
    # Load osmosis data
    with open("../data/osmosis_snapshot.json", "r") as f:
        osmosis_data: dict = json.load(f)

    total_liquidity_per_pool = osmosis_data["pool_token_counter"]
    liquidity_per_user = osmosis_data["accounts"]

    # Maps user address to pool to pool share
    user_shares_per_pool: dict[str, dict] = {}

    # Compute pool shares for each user
    for user_address, user_row in liquidity_per_user.items():
        user_shares_per_pool[user_address] = {}

        for pool_amount in user_row['balance']:
            user_share = int(pool_amount['amount']) / int(
                total_liquidity_per_pool[pool_amount['denom']]['pool_total'])
            user_shares_per_pool[user_address][pool_amount['denom']] = user_share


    # Compute user rewards
    user_token_rewards = {}
    for user_address, pool_shares in user_shares_per_pool.items():
        user_token_rewards[user_address] = 0
        for pool_name, user_pool_share in pool_shares.items():
            user_token_rewards[user_address] += (
                user_pool_share * REWARD_PER_POOL)

    # Impose whale cap
    total_redistribution_amount = 0
    for user_address, user_reward in user_token_rewards.items():
        if user_reward > 50000:
            total_redistribution_amount += user_reward - 50000
            user_token_rewards[user_address] = 50000

    with open('osmosis_pool_rewards.json', 'w') as f:
        json.dump(user_token_rewards, f)
