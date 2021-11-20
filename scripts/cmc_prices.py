""""""
import __init__
import os
import json
import requests
import somm_airdrop
from somm_airdrop.somm_users import somm_user_data
from somm_airdrop import cmc
import pandas as pd

from typing import Dict, List, Tuple, Union


def save_all_cmc_id_maps():
    token_info_path = os.path.join("data", "token_info.json")
    with open(token_info_path, mode="r") as f:
        token_info_json: Dict[str, dict] = json.load(f)
    token_id_to_symbol: Dict[str, str] = {
        k: d["symbol"] for k, d in token_info_json.items()}
    symbols: List[str] = [v for v in token_id_to_symbol.values()]
    symbols[symbols.index('⚗️')] = "MIST"
    cmc_api = cmc.CoinMarketCapAPI()
    # cmc_api.cmc_id_map(symbols=symbols, save=True)
    cmc_api.cmc_id_map(symbols="all", save=True)

def get_start_and_end_dates_for_ohlcv() -> Tuple[str, str]:
    v2_mints, v2_burns = somm_user_data.v2_mints(), somm_user_data.v2_burns()
    v3_mints, v3_burns = somm_user_data.v3_mints(), somm_user_data.v3_burns()
    earliest_ts: str = pd.Series(
        [df.index.min() for df in [v2_mints, v2_burns, v3_mints, v3_burns]]).min()
    latest_ts: str = pd.Series(
        [df.index.min() for df in [v2_mints, v2_burns, v3_mints, v3_burns]]).max()
    
    return earliest_ts, latest_ts

def _get_cmc_id_from_token_id(token_ids: Union[str, List[str]]):
    cmc_id_path = os.path.join("data", "cmc_id_maps.json")
    with open(cmc_id_path, mode="r") as f:
        cmc_id_maps: List[dict] = json.load(f)
    
    if isinstance(token_ids, str):
        token_ids = [token_ids]
    
    cmc_ids: List[int] = []
    for token_id in token_ids:
        cmc_id: int = None
        for map_ in cmc_id_maps:
            if map_["platform"] is not None:
                if map_["platform"]["token_address"] == token_id:
                    cmc_id = map_["id"] 
                    break
        if cmc_id is None:
            # breakpoint()
            ...
        cmc_ids.append(cmc_id)
        
    breakpoint()
    return cmc_ids

def ohlcv_query_between_dates():
    token_info_path = os.path.join("data", "token_info.json")
    with open(token_info_path, mode="r") as f:
        token_info_json: Dict[str, dict] = json.load(f)
    token_ids: List[str] = [k for k in token_info_json.keys()]

    cmc_ids = _get_cmc_id_from_token_id(token_ids=token_ids)

    return cmc_ids


def get_all_ohlcv_data():
    ...


if __name__ == "__main__":
    # save_all_cmc_id_maps()
    # start_ts, end_ts = get_start_and_end_dates_for_ohlcv()
    foo = ohlcv_query_between_dates()
    ...