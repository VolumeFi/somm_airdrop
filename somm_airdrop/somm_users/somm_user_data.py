#!/usr/bin/env python
import os
import pandas as pd
from typing import Dict, List

class SOMMAppQueries:

    file_paths: List[str]
    dir_path: str

    def __init__(self, dir_path: str = "data"):
        csv_file_names: List[str] = os.listdir(dir_path)
        self.file_paths: List[str] = [
            os.path.join(dir_path, fname) for fname in csv_file_names]
        self.dir_path = dir_path
    
    def load_csv(self, dataset: str) -> pd.DataFrame:
        if dataset not in ['somm_v2_burns', 'somm_v2_mints',
                           ]:
            raise ValueError()
        file_path = [fp for fp in self.file_paths if dataset in fp].pop()
        return pd.read_csv(file_path, index_col=0)

 
def v2_mints() -> pd.DataFrame:
    somm = SOMMAppQueries(dir_path="data")
    return somm.load_csv(dataset="somm_v2_mints")

def v2_burns() -> pd.DataFrame:
    somm = SOMMAppQueries(dir_path="data")
    return somm.load_csv(dataset="somm_v2_burns")


# User addresses now contained in mints_burns table.

def v3_mints_burns() -> pd.DataFrame:
    ... # TODO 
    # somm = SOMMAppQueries(dir_path="data")
    # return somm.load_csv(dataset="v3_mints_burns")