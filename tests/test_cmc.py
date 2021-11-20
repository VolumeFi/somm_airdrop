#!/usr/bin/env python
# import __init__

import os
import json
import pytest
from somm_airdrop import cmc
from typing import Any, Dict, List, Union

# from somm_airdrop.cmc import CMCSpecificTypeHints

class TestCoinMarketCapAPI:

    @pytest.fixture
    def cmc_api(self) -> cmc.CoinMarketCapAPI:
        return cmc.CoinMarketCapAPI()

    def test_cmc_id_map(self, cmc_api: cmc.CoinMarketCapAPI):
        symbols: List[str] = ["BTC", "ETH"]
        cmc_id_maps: List[dict] = cmc_api.cmc_id_map(symbols=symbols)
        assert isinstance(cmc_id_maps, list)
        assert isinstance(cmc_id_maps[0], dict)
        assert all([k in cmc_id_maps[0].keys() for k in ['id', 'slug', 'name']])
        breakpoint()
    
    @pytest.fixture
    def cmc_id_maps(self) -> List[dict]:
        return [
            {'id': 1, 'name': 'Bitcoin', 'symbol': 'BTC', 'slug': 'bitcoin', 
                'rank': 1, 'is_active': 1, 
                'first_historical_data': '2013-04-28T18:47:21.000Z', 
                'last_historical_data': '2021-11-19T00:59:02.000Z', 
                'platform': None}, 
            {'id': 1027, 'name': 'Ethereum', 'symbol': 'ETH', 
                'slug': 'ethereum', 'rank': 2, 'is_active': 1, 
                'first_historical_data': '2015-08-07T14:49:30.000Z', 
                'last_historical_data': '2021-11-19T00:59:02.000Z', 
                'platform': None}] 
    
    def test_save_cmc_id_maps(self, 
                              cmc_api: cmc.CoinMarketCapAPI, 
                              cmc_id_maps: List[dict]):
        """Tests whether the CMC ID Map query saves correctly."""

        temp_filename: str = "temp.json"
        temp_save_path = os.path.join("data", temp_filename)

        assert not os.path.exists(temp_save_path)
        cmc_api._save_cmc_id_maps(cmc_id_maps=cmc_id_maps,
                                  filename=temp_filename)
        with open(temp_save_path, mode="r") as f:
            saved_cmc_id_maps: List[dict] = json.load(f)
        assert isinstance(saved_cmc_id_maps, list)
        assert len(saved_cmc_id_maps) == 2
        assert all([[k in dict_.keys() for k in ["id", "name", "symbol"]] 
                    for dict_ in saved_cmc_id_maps])

        os.remove(temp_save_path)
        assert not os.path.exists(temp_save_path)
