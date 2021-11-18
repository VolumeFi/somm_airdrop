import pandas as pd
from tqdm import tqdm
import numpy as np
import math

LIQ_DURATION_REWARD = 2000000
PARTICIPATION_REWARD = 3200000


def get_position_amount_usd(token0: str, token1: str, amount0: int, amount1: int, mint_ts: pd.Timestamp):
    # return token_to_usd(token_id=token0, token_amount=amount0, ts=mint_ts)
    #        + token_to_usd(token_id=token1, token_amount=amount1, ts=mint_ts)
    return math.isqrt(amount0 * amount1)


def get_somm_v3_token_rewards():
    user_token_rewards = {}

    # DO THIS FOR BOTH V2 and V3
    # 1) Get unique pools + tokenIds
    # 2) Construct positions (while converting tokens to USD)
    # 3) Assign a score for each position and sum across positions
    # 4) Compute fraction of reward for each user
    # 5) Impose whale capp
    # 6) Redistribute to all users
    # 7) Distribute participation rewards to all users

    # v3 unique pools + tokenIds
    somm_v3_mints: pd.DataFrame = pd.read_csv(
        "../query_results/somm_v3_mints.csv").sort_values(
            'block_timestamp', ignore_index=True)
    somm_v3_burns: pd.DataFrame = pd.read_csv(
        "../query_results/somm_v3_burns.csv").sort_values(
            'block_timestamp', ignore_index=True)
    v3_burns: pd.DataFrame = pd.read_csv(
        "../query_results/uniswap_v3_burns.csv").sort_values(
            'block_timestamp', ignore_index=True)

    somm_v3_mints.loc[:, "block_timestamp"] = pd.to_datetime(
        somm_v3_mints.loc[:, "block_timestamp"])
    somm_v3_burns.loc[:, "block_timestamp"] = pd.to_datetime(
        somm_v3_burns.loc[:, "block_timestamp"])
    v3_burns.loc[:, "block_timestamp"] = pd.to_datetime(
        v3_burns.loc[:, "block_timestamp"], infer_datetime_format=True)

    used_somm_v3_burns = []
    used_v3_burns = []
    somm_v3_user_positions = {}

    # Construct positions for each user
    for idx, mint in tqdm(somm_v3_mints.iterrows(), total=somm_v3_mints.shape[0]):
        if mint["block_timestamp"] >= pd.Timestamp("2021-10-31", tz="UTC"):
            continue

        # First search for somm burns
        relevant_burns = somm_v3_burns[
            (somm_v3_burns['liquidity'] == mint['liquidity']) &
            (somm_v3_burns["from_address"] == mint["from_address"]) &
            (somm_v3_burns["pool"] == mint["pool"]) &
            (~somm_v3_burns.index.isin(used_somm_v3_burns)) &
            (somm_v3_burns['block_timestamp']
                > mint['block_timestamp'])
        ]

        # If there's a corresponding somm burn, add to used somm list
        if len(relevant_burns) > 0:
            used_somm_v3_burns.append(relevant_burns.index[0])

        # Try searching v3 burns
        else:
            relevant_burns = v3_burns[
                (v3_burns['liquidity'] == mint['liquidity']) &
                (v3_burns["from_address"] == mint["from_address"]) &
                (v3_burns["pool"] == mint["pool"]) &
                (~v3_burns.index.isin(used_v3_burns)) &
                (v3_burns['block_timestamp']
                    > mint['block_timestamp'])
            ]

            # If there's a corresponding v3 burn, add to used v3 list
            if len(relevant_burns) > 0:
                used_v3_burns.append(relevant_burns.index[0])

        end_time = pd.Timestamp("2021-10-31", tz="UTC")
        if len(relevant_burns) > 0:
            burn = relevant_burns.iloc[0]
            end_time = burn['block_timestamp']

        position_value = get_position_amount_usd(
            token0=mint["token0"], token1=mint["token1"], amount0=int(mint["amount0"]), amount1=int(mint["amount1"]), mint_ts=mint["block_timestamp"])

        # TODO: replace mint["liquidity"] with position value
        position = {
            "start": mint['block_timestamp'],
            "end": end_time,
            "amount": mint['liquidity']
        }

        if mint['from_address'] in somm_v3_user_positions:
            somm_v3_user_positions[mint['from_address']].append(position)
        else:
            somm_v3_user_positions[mint['from_address']] = [position]

    # Assign score to each position and sum across positions
    v3_user_scores = {}
    for user_address, user_positions in tqdm(somm_v3_user_positions.items()):
        user_score = 0
        for position in user_positions:
            position_score = math.isqrt(int(
                position['amount'])) * int((position['end'] - position['start']).total_seconds())
            user_score += position_score

        v3_user_scores[user_address] = user_score

    total_v3_score = sum(v3_user_scores.values())

    for user_address, user_score in tqdm(v3_user_scores.items(), leave=False):
        user_pool_token_reward = (
            user_score / total_v3_score) * LIQ_DURATION_REWARD
        if user_address in user_token_rewards:
            user_token_rewards[user_address] += user_pool_token_reward
        else:
            user_token_rewards[user_address] = user_pool_token_reward

    return user_token_rewards


def get_somm_v2_token_rewards():
    user_token_rewards = {}

    # 1) Get unique pools + tokenIds
    # 2) Construct positions (while converting tokens to USD)
    # 3) Assign a score for each position and sum across positions
    # 4) Compute fraction of reward for each user
    # 5) Impose whale capp
    # 6) Redistribute to all users
    # 7) Distribute participation rewards to all users

    # v2 unique pools + tokenIds
    somm_v2_mints: pd.DataFrame = pd.read_csv(
        "../query_results/somm_v2_mints.csv").sort_values(
            'block_timestamp', ignore_index=True)
    somm_v2_burns: pd.DataFrame = pd.read_csv(
        "../query_results/somm_v2_burns.csv").sort_values(
            'block_timestamp', ignore_index=True)
    v2_burns: pd.DataFrame = pd.read_csv(
        "../query_results/uniswap_v2_burns.csv").sort_values(
            'block_timestamp', ignore_index=True)

    somm_v2_mints.loc[:, "block_timestamp"] = pd.to_datetime(
        somm_v2_mints.loc[:, "block_timestamp"], infer_datetime_format=True)
    somm_v2_burns.loc[:, "block_timestamp"] = pd.to_datetime(
        somm_v2_burns.loc[:, "block_timestamp"], infer_datetime_format=True)

    # Get unique pairs:
    unique_pairs = somm_v2_mints[[
        "token0", "token1", "pair"]].drop_duplicates()

    # Only keep burns that are for the relevant pairs
    v2_burns = v2_burns[v2_burns["pair"].isin(
        unique_pairs["pair"])].reset_index(drop=True)
    v2_burns.loc[:, "block_timestamp"] = pd.to_datetime(
        v2_burns.loc[:, "block_timestamp"], infer_datetime_format=True)

    # Convert amount0/1 to type int and create liquidity column
    somm_v2_mints.amount0 = somm_v2_mints.amount0.apply(lambda x: int(x))
    somm_v2_mints.amount1 = somm_v2_mints.amount1.apply(lambda x: int(x))
    somm_v2_mints["liquidity"] = (
        somm_v2_mints.amount0 * somm_v2_mints.amount1).apply(lambda x: math.isqrt(x))

    somm_v2_burns.amount0 = somm_v2_burns.amount0.apply(lambda x: int(x))
    somm_v2_burns.amount1 = somm_v2_burns.amount1.apply(lambda x: int(x))
    somm_v2_burns["liquidity"] = (
        somm_v2_burns.amount0 * somm_v2_burns.amount1).apply(lambda x: math.isqrt(x))

    v2_burns.amount0 = v2_burns.amount0.apply(lambda x: int(x))
    v2_burns.amount1 = v2_burns.amount1.apply(lambda x: int(x))
    v2_burns["liquidity"] = (
        v2_burns.amount0 * v2_burns.amount1).apply(lambda x: math.isqrt(x))

    # Get positions on a pair-by-pair basis
    for pair_idx, pair_info in unique_pairs.iterrows():
        pair_v2_user_positions = {}

        somm_pair_mints = somm_v2_mints[somm_v2_mints["pair"]
                                        == pair_info["pair"]].copy()
        somm_pair_burns = somm_v2_burns[somm_v2_burns["pair"]
                                        == pair_info["pair"]].copy()
        v2_pair_burns = v2_burns[v2_burns["pair"] == pair_info["pair"]].copy()

        # Get unique users for given pool
        somm_pair_users = somm_pair_mints["from_address"].drop_duplicates()
        # Construct positions for each user (for each pair)
        for user_address in somm_pair_users:
            pair_v2_user_positions[user_address] = []
            somm_pair_user_mints = somm_pair_mints[somm_pair_mints["from_address"] == user_address].copy(
            )
            somm_pair_user_burns = somm_pair_burns[somm_pair_burns["from_address"] == user_address].copy(
            )
            v2_pair_user_burns = v2_pair_burns[v2_pair_burns["from_address"]
                                               == user_address].copy()

            # TODO: At this stage we can convert token amounts to USD
            # Multiply burn liquidity by -1
            somm_pair_user_burns.loc[:, "liquidity"] = somm_pair_user_burns["liquidity"].apply(
                lambda x: -x)
            v2_pair_user_burns.loc[:, "liquidity"] = v2_pair_user_burns["liquidity"].apply(
                lambda x: -x)

            # Stack relevant mints & burns
            user_pair_mints_burns = pd.concat((somm_pair_user_mints, somm_pair_user_burns, v2_pair_user_burns)).sort_values(
                'block_timestamp', ignore_index=True).drop_duplicates().reset_index(drop=True)

            # Recall that for V2 burns don't have to directly match mints
            #   Each mint/burn will mark the end/beginning of a new "position"
            for idx, mint_burn in user_pair_mints_burns.iterrows():

                if len(pair_v2_user_positions[user_address]) == 0 or pair_v2_user_positions[user_address][-1]["end"] is not None:
                    # First position must start with a mint
                    if mint_burn["liquidity"] <= 0:
                        continue

                    new_position = {
                        "start": mint_burn["block_timestamp"],
                        "end": None,
                        "amount": mint_burn["liquidity"]
                    }
                    pair_v2_user_positions[user_address].append(new_position)

                else:
                    prev_position = pair_v2_user_positions[user_address][-1]
                    # Check if last position needs to be filled in and close it
                    if prev_position["end"] is None:
                        prev_position["end"] = mint_burn["block_timestamp"]

                    # If there's >0 liquidity left, treat it as a new position
                    if (prev_position["amount"] + mint_burn["liquidity"]) > 0:
                        new_position = {
                            "start": mint_burn['block_timestamp'],
                            "end": None,
                            "amount": prev_position["amount"] + mint_burn["liquidity"]
                        }
                        pair_v2_user_positions[user_address].append(
                            new_position)

            if pair_v2_user_positions[user_address][-1]["end"] is None:
                pair_v2_user_positions[user_address][-1]["end"] = pd.Timestamp(
                    "2021-10-31", tz="UTC")


if __name__ == "__main__":

    # v3_user_token_rewards = get_somm_v3_token_rewards()
    v2_user_token_rewards = get_somm_v2_token_rewards()

    """
    # Impose whale cap
    total_redistribution_amount = 0
    for user_address, user_reward in user_token_rewards.items():
        if user_reward > 50000:
            total_redistribution_amount += user_reward - 50000
            user_token_rewards[user_address] = 50000

    # Redistribute somm from whale cap uniformly
    redistribution_amount = total_redistribution_amount/len(user_token_rewards)
    for user_address, user_reward in user_token_rewards.items():
        user_token_rewards[user_address] += redistribution_amount
        use
    """

    breakpoint()
