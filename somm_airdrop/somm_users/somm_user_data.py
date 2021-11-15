#!/usr/bin/env python
import os
import pandas as pd
from typing import Dict, List

class SOMMAppQueries:

    file_paths: List[str]
    dir_path: str

    def __init__(self):
        dir_path = os.path.join("query_results")
        csv_file_names: List[str] = os.listdir(dir_path)
        self.file_paths: List[str] = [
            os.path.join(dir_path, fname) for fname in csv_file_names]
        self.dir_path = dir_path
    
    def load_csv(self, dataset:str) -> pd.DataFrame:
        if dataset not in ['v2_mints_burns', 'v2_user_addresses',
                           'v3_mints_burns', 'v3_user_addresses']:
            raise ValueError()
        file_path = [fp for fp in self.file_paths if dataset in fp].pop()
        return pd.read_csv(file_path, index_col=0)

somm = SOMMAppQueries()
 
def v2_mints_burns() -> pd.DataFrame:
    return somm.load_csv(dataset="v2_mints_burns")

def v3_mints_burns() -> pd.DataFrame:
    return somm.load_csv(dataset="v3_mints_burns")

def v2_user_addresses() -> List[str]:
    return somm.load_csv(dataset="v2_user_addresses").values[:, 0].tolist()

def v3_user_addresses() -> List[str]:
    return somm.load_csv(dataset="v3_user_addresses").values[:, 0].tolist()
