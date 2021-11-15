#!/usr/bin/env python
# import __init__

import os
import pytest
from typing import List

class TestDataPaths:

    def test_data_dir_visibility(self):
        assert os.path.exists("data")

    @pytest.fixture
    def somm_app_data_paths(self) -> List[str]:
        return [os.path.join("data", fname) for fname in os.listdir("data")
                if "somm_" in fname]

    def test_somm_app_data(self, somm_app_data_paths):
        assert any(["somm_v2_mints" in path for path in somm_app_data_paths])
        assert any(["somm_v2_burns" in path for path in somm_app_data_paths])
        for data_path in somm_app_data_paths:
            assert os.path.exists(data_path), f"Missing path: {data_path}"