import os
import math
import collections
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Dict, List, Mapping, Sequence, Union
import json
import time
from utils import plot_utils
from pathlib import Path

# In terms of SOMM
LIQ_DURATION_REWARD = 2000000 
PARTICIPATION_REWARD = 3200000

# Transform to uSOMM
LIQ_DURATION_REWARD = 2000000 * 1e6
PARTICIPATION_REWARD = 3200000 * 1e6



PairID = str
Wallet = str


def token_to_usd(token_id: str,
                 token_amt: float,
                 ) -> float:
    """Args:
        token_id (str): Contract address for the token.
        token_amt (float): Amount of the token.

    Returns:
        (float): Value of 'token_amt' at the USD price of the token."""

    token_info_path: str = os.path.join("../data", "token_info.json")
    with open(token_info_path, mode="r") as f:
        token_info_maps: Dict[str, dict] = json.load(f)
    token_price_usd: float = float(token_info_maps[token_id]["tokenPriceUSD"])
    divisor = int(token_info_maps[token_id]['divisor'])
    decimal_adj = math.pow(10, -divisor)
    return token_price_usd * token_amt * decimal_adj


def get_position_amount_usd(
        token0: str, token1: str, amount0: int, amount1: int):
    """[summary]

    Args:
        token0 (str): Contract address for token 0.
        token1 (str): Contract address for token 1.
        amount0 (int): Amount of token 0 in the liquidity position.
        amount1 (int): Amount of token 1 in the liquidity position.

    Returns:
        (float): Value of the liquidity position in USD.
    """

    return token_to_usd(token_id=token0, token_amt=amount0)
    + token_to_usd(token_id=token1, token_amt=amount1)

    return math.isqrt(amount0 * amount1)


def get_somm_v3_scores():
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
        "../data/somm_v3_mints.csv").sort_values(
            'block_timestamp', ignore_index=True)
    somm_v3_burns: pd.DataFrame = pd.read_csv(
        "../data/somm_v3_burns.csv").sort_values(
            'block_timestamp', ignore_index=True)
    v3_burns: pd.DataFrame = pd.read_csv(
        "../data/uniswap_v3_burns.csv").sort_values(
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
            token0=mint["token0"], token1=mint["token1"], amount0=int(mint["amount0"]), amount1=int(mint["amount1"]))

        # TODO: replace mint["liquidity"] with position value
        position = {
            "start": mint['block_timestamp'],
            "end": end_time,
            "amount": position_value
        }

        if mint['from_address'] in somm_v3_user_positions:
            somm_v3_user_positions[mint['from_address']].append(position)
        else:
            somm_v3_user_positions[mint['from_address']] = [position]

    # Assign score to each position and sum across positions
    v3_user_scores = {}
    for wallet_address, user_positions in tqdm(somm_v3_user_positions.items()):
        user_score = 0
        for position in user_positions:
            position_score = math.sqrt(int(
                position['amount'])) * int((position['end'] - position['start']).total_seconds())
            user_score += position_score

        v3_user_scores[wallet_address] = user_score

    return v3_user_scores


class TokenScoresSOMMV2:
    """
    1) Get unique pools + tokenIds
    2) Construct positions (while converting tokens to USD)
    3) Assign a score for each position and sum across positions
    4) Compute fraction of reward for each user
    5) Impose whale capp
    6) Redistribute to all users
    7) Distribute participation rewards to all users
    """
    unique_pairs: pd.DataFrame

    # v2 unique pools + tokenIds
    def __init__(self):
        self._load_data()
        self._scores = None

    @property
    def scores(self):
        if self._scores is not None:
            return self._scores

        self._get_unique_pairs()
        self._filter_burns_for_relevant_pairs()
        self._convert_amounts_columns()
        wallet_to_positions = self.get_wallet_to_positions_mapping()
        self._scores = self.get_scores(wallet_to_positions)
        return self._scores

    def _load_data(self, data_dir: str = "data") -> None:

        somm_v2_mints: pd.DataFrame = pd.read_csv(
            "../data/somm_v2_mints.csv").sort_values(
                'block_timestamp', ignore_index=True)
        somm_v2_burns: pd.DataFrame = pd.read_csv(
            "../data/somm_v2_burns.csv").sort_values(
                'block_timestamp', ignore_index=True)
        v2_burns: pd.DataFrame = pd.read_csv(
            "../data/uniswap_v2_burns.csv").sort_values(
                'block_timestamp', ignore_index=True)

        somm_v2_mints.loc[:, "block_timestamp"] = pd.to_datetime(
            somm_v2_mints.loc[:, "block_timestamp"], infer_datetime_format=True)
        somm_v2_burns.loc[:, "block_timestamp"] = pd.to_datetime(
            somm_v2_burns.loc[:, "block_timestamp"], infer_datetime_format=True)
        self.somm_v2_mints = somm_v2_mints
        self.somm_v2_burns = somm_v2_burns
        self.v2_burns = v2_burns

    def _get_unique_pairs(self) -> pd.DataFrame:
        unique_pairs = self.somm_v2_mints[[
            "token0", "token1", "pair"]].drop_duplicates()
        self.unique_pairs = unique_pairs
        # return unique_pairs

    def _filter_burns_for_relevant_pairs(self):
        self.v2_burns = self.v2_burns[self.v2_burns["pair"].isin(
            self.unique_pairs["pair"])].reset_index(drop=True)
        self.v2_burns.loc[:, "block_timestamp"] = pd.to_datetime(
            self.v2_burns.loc[:, "block_timestamp"], infer_datetime_format=True)

    def _convert_amounts_columns(self):
        self.somm_v2_mints.amount0 = self.somm_v2_mints.amount0.apply(
            lambda x: int(x))
        self.somm_v2_mints.amount1 = self.somm_v2_mints.amount1.apply(
            lambda x: int(x))
        self.somm_v2_mints["liquidity"] = (
            self.somm_v2_mints.amount0 * self.somm_v2_mints.amount1).apply(lambda x: math.isqrt(x))

        self.somm_v2_burns.amount0 = self.somm_v2_burns.amount0.apply(
            lambda x: int(x))
        self.somm_v2_burns.amount1 = self.somm_v2_burns.amount1.apply(
            lambda x: int(x))
        self.somm_v2_burns["liquidity"] = (
            self.somm_v2_burns.amount0 * self.somm_v2_burns.amount1).apply(lambda x: math.isqrt(x))

        self.v2_burns.amount0 = self.v2_burns.amount0.apply(lambda x: int(x))
        self.v2_burns.amount1 = self.v2_burns.amount1.apply(lambda x: int(x))
        self.v2_burns["liquidity"] = (
            self.v2_burns.amount0 * self.v2_burns.amount1).apply(lambda x: math.isqrt(x))

    def _create_amount_column(self, mints_burns, pair_info):

        mints_burns["amount"] = mints_burns.amount0.apply(lambda token_amt: token_to_usd(
            token_id=pair_info.token0, token_amt=token_amt)) + mints_burns.amount1.apply(lambda token_amt: token_to_usd(token_id=pair_info.token1, token_amt=token_amt))

        return mints_burns

    def _get_pair_v2_user_positions(self, pair_info) -> Dict[Wallet, List]:
        pair_v2_user_positions: Dict[Wallet, List] = {}

        somm_pair_mints = self.somm_v2_mints[
            self.somm_v2_mints["pair"] == pair_info["pair"]].copy()
        somm_pair_burns = self.somm_v2_burns[
            self.somm_v2_burns["pair"] == pair_info["pair"]].copy()
        v2_pair_burns = self.v2_burns[
            self.v2_burns["pair"] == pair_info["pair"]].copy()

        # Get unique users for given pool
        somm_pair_users: Sequence[Wallet] = somm_pair_mints["from_address"].drop_duplicates(
        )

        # Construct positions for each user (for each pair)
        for wallet_address in somm_pair_users:
            pair_v2_user_positions[wallet_address] = []
            somm_pair_user_mints = somm_pair_mints[somm_pair_mints["from_address"] == wallet_address].copy(
            )
            somm_pair_user_burns = somm_pair_burns[somm_pair_burns["from_address"] == wallet_address].copy(
            )
            v2_pair_user_burns = v2_pair_burns[v2_pair_burns["from_address"]
                                               == wallet_address].copy()

            # Multiply burn liquidity by -1
            somm_pair_user_burns.loc[:, "liquidity"] = somm_pair_user_burns["liquidity"].apply(
                lambda x: -x)
            v2_pair_user_burns.loc[:, "liquidity"] = v2_pair_user_burns["liquidity"].apply(
                lambda x: -x)

            # Stack relevant mints & burns
            user_pair_mints_burns = pd.concat(
                (somm_pair_user_mints, somm_pair_user_burns, v2_pair_user_burns))
            user_pair_mints_burns = user_pair_mints_burns.sort_values(
                'block_timestamp', ignore_index=True
            ).drop_duplicates().reset_index(drop=True)

            # Recall that for V2 burns don't have to directly match mints
            #   Each mint/burn will mark the end/beginning of a new "position"
            for idx, mint_burn in user_pair_mints_burns.iterrows():

                if len(pair_v2_user_positions[wallet_address]) == 0 or pair_v2_user_positions[wallet_address][-1]["end"] is not None:
                    # First position must start with a mint
                    if mint_burn["liquidity"] <= 0:
                        continue

                    # Calculate amount in USD
                    amount = get_position_amount_usd(
                        token0=pair_info.token0, token1=pair_info.token1, amount0=mint_burn.amount0, amount1=mint_burn.amount1)

                    new_position = {
                        "start": mint_burn["block_timestamp"],
                        "end": None,
                        "amount": amount
                    }
                    pair_v2_user_positions[wallet_address].append(new_position)

                else:
                    prev_position = pair_v2_user_positions[wallet_address][-1]
                    # Check if last position needs to be filled in and close it
                    if prev_position["end"] is None:
                        prev_position["end"] = mint_burn["block_timestamp"]

                    # Calculate amount in USD
                    amount = get_position_amount_usd(
                        token0=pair_info.token0, token1=pair_info.token1, amount0=mint_burn.amount0, amount1=mint_burn.amount1)

                    # If burn, make amount negative
                    if mint_burn["liquidity"] < 0:
                        amount *= -1

                    # If there's >0 liquidity left, treat it as a new position
                    if (prev_position["amount"] + amount) > 0:
                        new_position = {
                            "start": mint_burn['block_timestamp'],
                            "end": None,
                            "amount": prev_position["amount"] + amount
                        }
                        pair_v2_user_positions[wallet_address].append(
                            new_position)

            if pair_v2_user_positions[wallet_address][-1]["end"] is None:
                pair_v2_user_positions[wallet_address][-1]["end"] = pd.Timestamp(
                    "2021-10-31", tz="UTC")

        return pair_v2_user_positions

    def get_wallet_to_positions_mapping(self) -> Dict[Wallet, List]:

        wallet_to_positions: Dict[Wallet, List] = {}
        # Get positions on a pair-by-pair basis
        for pair_idx, pair_info in tqdm(self.unique_pairs.iterrows(), 
                                        total=len(self.unique_pairs)):
            pair_v2_user_positions: Dict[Wallet, List] = self._get_pair_v2_user_positions(
                pair_info)
            # Positions are already in USD, so we can aggregate them
            for address, positions in pair_v2_user_positions.items():
                if address in wallet_to_positions:
                    wallet_to_positions[address] += positions
                else:
                    wallet_to_positions[address] = positions

        return wallet_to_positions

    def get_scores(self, wallet_to_positions):
        # Assign score to each position and sum across positions
        wallet_scores: Dict[Wallet, float] = {}
        for wallet_address, wallet_positions in tqdm(wallet_to_positions.items(), leave=False):
            score = 0
            for position in wallet_positions:
                position_score = math.sqrt(
                    position['amount']) * int((position['end'] - position['start']
                    ).total_seconds())
                score += position_score

            wallet_scores[wallet_address] = score

        return wallet_scores


if __name__ == "__main__":

    v3_wallet_scores: Dict[Wallet, float] = get_somm_v3_scores()
    v2_wallet_scores: Dict[Wallet, float] = TokenScoresSOMMV2().scores

    # Combine wallet score dicts
    somm_wallet_scores = collections.Counter(v3_wallet_scores)
    somm_wallet_scores.update(collections.Counter(v2_wallet_scores))
    somm_wallet_scores = dict(somm_wallet_scores)

    # Compute rewards from scores
    wallet_rewards: Dict[Wallet, float] = {}
    total_score = sum(list(somm_wallet_scores.values()))
    for wallet_address, score in somm_wallet_scores.items():
        wallet_rewards[wallet_address] = (
            score / total_score) * LIQ_DURATION_REWARD + (PARTICIPATION_REWARD / len(somm_wallet_scores))

    # Impose whale cap
    total_redistribution_amount = 0
    for wallet_address, reward in wallet_rewards.items():
        if reward > 50000:
            total_redistribution_amount += reward - 50000
            wallet_rewards[wallet_address] = 50000

    # Redistribute somm from whale cap uniformly
    redistribution_amount = total_redistribution_amount/len(wallet_rewards)
    for wallet_address, reward in wallet_rewards.items():
        wallet_rewards[wallet_address] += redistribution_amount

    # Chop off decimals because uSOMM is the smallest unit
    for wallet, reward in wallet_rewards.items():
        wallet_rewards[wallet] = round(reward)

    json_save_path = Path('../token_rewards/somm_app_rewards_usomm.json').resolve()
    json_save_path.parent.mkdir(exist_ok=True, parents=True)

    with open(json_save_path, 'w') as fp:
        json.dump(wallet_rewards, fp)

    plot_utils.plot_reward_distribution(wallet_rewards, save_path=Path(
        "../plots/somm_app_rewards.png").resolve(), title="Sommelier App Users SOMM Rewards")

    total_rewards: float = sum(wallet_rewards.values())
    print(f"Total airdrop rewards on : {total_rewards}")