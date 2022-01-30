import json
import numpy as np
from matplotlib import pyplot as plt
from typing import Dict, List, Mapping, Union
from pathlib import Path


def somm2usomm(amt_somm: float) -> int:
    return int(amt_somm * 1e6)

def usomm2somm(amt_usomm: int) -> int:
    return amt_usomm / 1e6

def plot_reward_distribution(wallet_to_reward: Dict[str, Union[float, int]], save_path: Path = None, dpi=300, title=None):
    save_path.parent.mkdir(exist_ok=True, parents=True)
    plt.figure(figsize=(16, 10))
    plt.hist(wallet_to_reward.values(), bins=100)
    plt.locator_params(axis='x', nbins=20)
    plt.yscale('log')
    plt.xlabel("SOMM reward")
    plt.ylabel("Number of users")
    if title is not None:
        plt.title(title)
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=dpi)
    else:
        plt.show()
