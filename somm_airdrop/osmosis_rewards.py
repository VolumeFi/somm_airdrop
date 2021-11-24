import pandas as pd
from tqdm import tqdm
import numpy as np
import math
import json
from pathlib import Path
from utils import plot_utils

REWARD_PER_POOL = 200000


if __name__ == "__main__":
    # Load osmosis data
    data_path = Path("../data/osmosis_snapshot.json").resolve()
    with open(data_path, "r") as f:
        osmosis_data: dict = json.load(f)

    total_liquidity_per_pool = osmosis_data["pool_token_counter"]
    liquidity_per_user = osmosis_data["accounts"]

    # Maps user address to pool to pool share
    user_shares_per_pool: dict[str, dict] = {}

    # Compute pool shares for each user
    for wallet_address, user_row in liquidity_per_user.items():
        user_shares_per_pool[wallet_address] = {}

        for pool_amount in user_row['balance']:
            user_share = int(pool_amount['amount']) / int(
                total_liquidity_per_pool[pool_amount['denom']]['pool_total'])
            user_shares_per_pool[wallet_address][pool_amount['denom']] = user_share

    # Compute user rewards
    wallet_rewards = {}
    for wallet_address, pool_shares in user_shares_per_pool.items():
        wallet_rewards[wallet_address] = 0
        for pool_name, user_pool_share in pool_shares.items():
            wallet_rewards[wallet_address] += (
                user_pool_share * REWARD_PER_POOL)

    # Impose whale cap
    total_redistribution_amount = 0
    for wallet_address, user_reward in wallet_rewards.items():
        if user_reward > 50000:
            total_redistribution_amount += user_reward - 50000
            wallet_rewards[wallet_address] = 50000
    
    redistribution_amount = total_redistribution_amount/len(wallet_rewards)
    for wallet_address, reward in wallet_rewards.items():
        wallet_rewards[wallet_address] += redistribution_amount

    json_save_path = Path(
        '../token_rewards/osmosis_pool_rewards.json').resolve()
    json_save_path.parent.mkdir(exist_ok=True, parents=True)

    with open(json_save_path, 'w') as fp:
        json.dump(wallet_rewards, fp)

    plot_utils.plot_reward_distribution(wallet_rewards, save_path=Path(
        "../plots/osmosis_pool_rewards.png").resolve(), title="Osmosis LP SOMM Rewards")
