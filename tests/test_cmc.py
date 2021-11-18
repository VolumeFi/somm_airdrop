#!/usr/bin/env python
# import __init__

import os
import json
import pytest
from somm_airdrop import cmc
from typing import Any, Dict, List, Union

# from somm_airdrop.cmc import CMCSpecificTypeHints

class TestCoinMarketCapConnector:

    @pytest.fixture
    def connector(self) -> cmc.CoinMarketCapConnector:
        return cmc.CoinMarketCapConnector()

    def test_skeleton(self, connector: cmc.CoinMarketCapConnector):
        ...
    


