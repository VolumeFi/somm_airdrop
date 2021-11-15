import pandas as pd
from tqdm import tqdm
import numpy as np


def get_somm_v3_positions():
    somm_v3_mints: pd.DataFrame = pd.read_csv(
        "../query_results/somm_v3_mints.csv").sort_values('block_timestamp', ignore_index=True)
    somm_v3_burns: pd.DataFrame = pd.read_csv(
        "../query_results/somm_v3_burns.csv").sort_values('block_timestamp', ignore_index=True)
    v3_burns: pd.DataFrame = pd.read_csv(
        "../query_results/uniswap_v3_burns.csv").sort_values('block_timestamp', ignore_index=True)

    used_somm_v3_burns = []
    used_v3_burns = []
    somm_v3_user_positions = {}

    # TODO: Ignore mints/burns after October 31, 2021
    for idx, mint in tqdm(somm_v3_mints.iterrows(), total=somm_v3_mints.shape[0]):
        # Search somm_v3_burns for burn that matches mint
        relevant_burns = somm_v3_burns[
            (somm_v3_burns['liquidity'] == mint['liquidity']) &
            (somm_v3_burns["from_address"] == mint["from_address"]) &
            (somm_v3_burns["pool"] == mint["pool"]) &
            (~somm_v3_burns.index.isin(used_somm_v3_burns)) &
            (somm_v3_burns['block_timestamp'] > mint['block_timestamp'])
        ]

        # If matching burn is in somm burns
        if len(relevant_burns) > 0:
            used_somm_v3_burns.append(relevant_burns.index[0])

        else:
            # Search the general v2 burns for a matching one
            relevant_burns = v3_burns[
                (v3_burns['liquidity'] == mint['liquidity']) &
                (v3_burns["from_address"] == mint["from_address"]) &
                (v3_burns["pool"] == mint["pool"]) &
                (~v3_burns.index.isin(used_v3_burns)) &
                (v3_burns['block_timestamp'] > mint['block_timestamp'])
            ]

            # If matching burn is in general v3 burns
            if len(relevant_burns) > 0:
                used_v3_burns.append(relevant_burns.index[0])

        end_time = None
        if len(relevant_burns) > 0:
            # If there are multiple, choose the earliest
            burn = relevant_burns.iloc[0]
            end_time = burn['block_timestamp']

        position = {
            "start": mint['block_timestamp'],
            "end": end_time,
            "liquidity": mint['liquidity']
        }
        if mint['from_address'] in somm_v3_user_positions:
            somm_v3_user_positions[mint['from_address']].append(position)
        else:
            somm_v3_user_positions[mint['from_address']] = [position]

    return somm_v3_user_positions


def get_somm_v2_position():
    somm_v2_mints: pd.DataFrame = pd.read_csv(
        "../query_results/somm_v2_mints.csv").sort_values('block_timestamp', ignore_index=True)
    somm_v2_burns: pd.DataFrame = pd.read_csv(
        "../query_results/somm_v2_burns.csv").sort_values('block_timestamp', ignore_index=True)
    v2_burns: pd.DataFrame = pd.read_csv(
        "../query_results/uniswap_v2_burns.csv").sort_values('block_timestamp', ignore_index=True)


if __name__ == "__main__":
    get_somm_v3_positions()
    # get_somm_v2_position()
