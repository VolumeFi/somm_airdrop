import logging

from pprint import pprint
from web3 import Web3
from decoding_utils import decode_log
import json
import pandas as pd
from tqdm import tqdm
from etherscan_connector import EtherscanApiConnector
import math
import datetime

api_rate_limit_message = "Max rate limit reached"

# Etherscan Logs:
# https://docs.etherscan.io/api-endpoints/logs

# ======================================================================================================================




SOMM_V2_CONTRACTS = [
    {
        "name": "Release1 Add",
        "address": "0xFd8A61F94604aeD5977B31930b48f1a94ff3a195",
        "abi": [{"name":"TestValue","inputs":[{"type":"uint256","name":"value","indexed":False},{"type":"string","name":"text","indexed":False}],"anonymous":False,"type":"event"},{"name":"TestAddress","inputs":[{"type":"address","name":"addr","indexed":False},{"type":"string","name":"text","indexed":False}],"anonymous":False,"type":"event"},{"name":"TestData","inputs":[{"type":"bytes32","name":"data","indexed":False},{"type":"string","name":"text","indexed":False}],"anonymous":False,"type":"event"},{"outputs":[],"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"name":"investTokenForEthPair","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"token"},{"type":"address","name":"pair"},{"type":"uint256","name":"amount"},{"type":"uint256","name":"minPoolTokens"}],"stateMutability":"payable","type":"function"},{"name":"investTokenForEthPair","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"token"},{"type":"address","name":"pair"},{"type":"uint256","name":"amount"},{"type":"uint256","name":"minPoolTokens"},{"type":"uint256","name":"deadline"}],"stateMutability":"payable","type":"function"},{"name":"pause","outputs":[],"inputs":[{"type":"bool","name":"_paused"}],"stateMutability":"nonpayable","type":"function","gas":36577},{"name":"newAdmin","outputs":[],"inputs":[{"type":"address","name":"_admin"}],"stateMutability":"nonpayable","type":"function","gas":36607},{"name":"newFeeAmount","outputs":[],"inputs":[{"type":"uint256","name":"_feeAmount"}],"stateMutability":"nonpayable","type":"function","gas":36537},{"name":"newFeeAddress","outputs":[],"inputs":[{"type":"address","name":"_feeAddress"}],"stateMutability":"nonpayable","type":"function","gas":36667},{"name":"seizeMany","outputs":[],"inputs":[{"type":"address[8]","name":"token"},{"type":"uint256[8]","name":"amount"},{"type":"address[8]","name":"to"}],"stateMutability":"nonpayable","type":"function","gas":282577},{"name":"seize","outputs":[],"inputs":[{"type":"address","name":"token"},{"type":"uint256","name":"amount"},{"type":"address","name":"to"}],"stateMutability":"nonpayable","type":"function","gas":36677},{"stateMutability":"payable","type":"fallback"},{"name":"paused","outputs":[{"type":"bool","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1571},{"name":"admin","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1601},{"name":"feeAmount","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1631},{"name":"feeAddress","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1661}],
        "topic0": "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f" # Mint
    },
    {
        "name": "Release1 Remove",
        "address": "0x418915329226AE7fCcB20A2354BbbF0F6c22Bd92",
        "abi": [{"outputs":[],"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"name":"divestEthPairToToken","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"pair"},{"type":"address","name":"token"},{"type":"uint256","name":"amount"}],"stateMutability":"payable","type":"function"},{"name":"divestEthPairToToken","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"pair"},{"type":"address","name":"token"},{"type":"uint256","name":"amount"},{"type":"uint256","name":"deadline"}],"stateMutability":"payable","type":"function"},{"name":"pause","outputs":[],"inputs":[{"type":"bool","name":"_paused"}],"stateMutability":"nonpayable","type":"function","gas":36397},{"name":"newAdmin","outputs":[],"inputs":[{"type":"address","name":"_admin"}],"stateMutability":"nonpayable","type":"function","gas":36427},{"name":"newFeeAmount","outputs":[],"inputs":[{"type":"uint256","name":"_feeAmount"}],"stateMutability":"nonpayable","type":"function","gas":36357},{"name":"newFeeAddress","outputs":[],"inputs":[{"type":"address","name":"_feeAddress"}],"stateMutability":"nonpayable","type":"function","gas":36487},{"stateMutability":"payable","type":"fallback"},{"name":"paused","outputs":[{"type":"bool","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1331},{"name":"admin","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1361},{"name":"feeAmount","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1391},{"name":"feeAddress","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1421}],
        "topic0": "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496" # Burn
    },
    {
        "name": "Release2 Add",
        "address": "0xA522AA47C40F2BAC847cbe4D37455c521E69DEa7",
        "abi": [{"name":"LPTokenMint","inputs":[{"type":"address","name":"msg_sender","indexed":False},{"type":"uint256","name":"liquidity","indexed":False}],"anonymous":False,"type":"event"},{"outputs":[],"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"name":"investTokenForUniPair","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"token"},{"type":"address","name":"pair"},{"type":"uint256","name":"amount"},{"type":"uint256","name":"minPoolTokens"}],"stateMutability":"payable","type":"function"},{"name":"investTokenForUniPair","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"token"},{"type":"address","name":"pair"},{"type":"uint256","name":"amount"},{"type":"uint256","name":"minPoolTokens"},{"type":"uint256","name":"deadline"}],"stateMutability":"payable","type":"function"},{"name":"addLiquidity","outputs":[{"type":"uint256","name":""},{"type":"uint256","name":""},{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"tokenA"},{"type":"address","name":"tokenB"},{"type":"uint256","name":"amountADesired"},{"type":"uint256","name":"amountBDesired"},{"type":"uint256","name":"amountAMin"},{"type":"uint256","name":"amountBMin"},{"type":"address","name":"to"}],"stateMutability":"nonpayable","type":"function"},{"name":"addLiquidity","outputs":[{"type":"uint256","name":""},{"type":"uint256","name":""},{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"tokenA"},{"type":"address","name":"tokenB"},{"type":"uint256","name":"amountADesired"},{"type":"uint256","name":"amountBDesired"},{"type":"uint256","name":"amountAMin"},{"type":"uint256","name":"amountBMin"},{"type":"address","name":"to"},{"type":"uint256","name":"deadline"}],"stateMutability":"nonpayable","type":"function"},{"name":"addLiquidityETH","outputs":[{"type":"uint256","name":""},{"type":"uint256","name":""},{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"token"},{"type":"uint256","name":"amountTokenDesired"},{"type":"uint256","name":"amountTokenMin"},{"type":"uint256","name":"amountETHMin"},{"type":"address","name":"to"}],"stateMutability":"payable","type":"function"},{"name":"addLiquidityETH","outputs":[{"type":"uint256","name":""},{"type":"uint256","name":""},{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"token"},{"type":"uint256","name":"amountTokenDesired"},{"type":"uint256","name":"amountTokenMin"},{"type":"uint256","name":"amountETHMin"},{"type":"address","name":"to"},{"type":"uint256","name":"deadline"}],"stateMutability":"payable","type":"function"},{"name":"pause","outputs":[],"inputs":[{"type":"bool","name":"_paused"}],"stateMutability":"nonpayable","type":"function","gas":36727},{"name":"newAdmin","outputs":[],"inputs":[{"type":"address","name":"_admin"}],"stateMutability":"nonpayable","type":"function","gas":36757},{"name":"newFeeAmount","outputs":[],"inputs":[{"type":"uint256","name":"_feeAmount"}],"stateMutability":"nonpayable","type":"function","gas":36687},{"name":"newFeeAddress","outputs":[],"inputs":[{"type":"address","name":"_feeAddress"}],"stateMutability":"nonpayable","type":"function","gas":36817},{"stateMutability":"payable","type":"fallback"},{"name":"paused","outputs":[{"type":"bool","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1661},{"name":"admin","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1691},{"name":"feeAmount","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1721},{"name":"feeAddress","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1751}],
        "topic0": "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f" # Mint
    },
    {
        "name": "Release2 Remove",
        "address": "0x430f33353490b256D2fD7bBD9DaDF3BB7f905E78",
        "abi": [{"stateMutability":"nonpayable","type":"constructor","inputs":[],"outputs":[]},{"stateMutability":"payable","type":"function","name":"divestUniPairToToken","inputs":[{"name":"pair","type":"address"},{"name":"token","type":"address"},{"name":"amount","type":"uint256"},{"name":"minTokenAmount","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"payable","type":"function","name":"divestUniPairToToken","inputs":[{"name":"pair","type":"address"},{"name":"token","type":"address"},{"name":"amount","type":"uint256"},{"name":"minTokenAmount","type":"uint256"},{"name":"deadline","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"removeLiquidity","inputs":[{"name":"tokenA","type":"address"},{"name":"tokenB","type":"address"},{"name":"liquidity","type":"uint256"},{"name":"amountAMin","type":"uint256"},{"name":"amountBMin","type":"uint256"},{"name":"to","type":"address"}],"outputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"removeLiquidity","inputs":[{"name":"tokenA","type":"address"},{"name":"tokenB","type":"address"},{"name":"liquidity","type":"uint256"},{"name":"amountAMin","type":"uint256"},{"name":"amountBMin","type":"uint256"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"outputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"removeLiquidityETH","inputs":[{"name":"token","type":"address"},{"name":"liquidity","type":"uint256"},{"name":"amountTokenMin","type":"uint256"},{"name":"amountETHMin","type":"uint256"},{"name":"to","type":"address"}],"outputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"removeLiquidityETH","inputs":[{"name":"token","type":"address"},{"name":"liquidity","type":"uint256"},{"name":"amountTokenMin","type":"uint256"},{"name":"amountETHMin","type":"uint256"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"outputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"pause","inputs":[{"name":"_paused","type":"bool"}],"outputs":[],"gas":36454},{"stateMutability":"nonpayable","type":"function","name":"newAdmin","inputs":[{"name":"_admin","type":"address"}],"outputs":[],"gas":36484},{"stateMutability":"nonpayable","type":"function","name":"newFeeAmount","inputs":[{"name":"_feeAmount","type":"uint256"}],"outputs":[],"gas":36414},{"stateMutability":"nonpayable","type":"function","name":"newFeeAddress","inputs":[{"name":"_feeAddress","type":"address"}],"outputs":[],"gas":36544},{"stateMutability":"payable","type":"fallback"},{"stateMutability":"view","type":"function","name":"paused","inputs":[],"outputs":[{"name":"","type":"bool"}],"gas":1388},{"stateMutability":"view","type":"function","name":"admin","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":1418},{"stateMutability":"view","type":"function","name":"feeAmount","inputs":[],"outputs":[{"name":"","type":"uint256"}],"gas":1448},{"stateMutability":"view","type":"function","name":"feeAddress","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":1478}],
        "topic0": "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496" # Burn
    }
]



if __name__ == "__main__":
    etherscan_conn = EtherscanApiConnector()

    mints_burns_dict = []

    # Get latest block number before October 31, 2021
    timestamp = int(datetime.datetime.strptime('10/31/2021', '%m/%d/%Y').strftime("%s"))
    maximum_block_number = int(etherscan_conn.get_block_number_before_timestamp(timestamp=timestamp))
    
    for somm_contract_dict in SOMM_V2_CONTRACTS:
        normal_txs = etherscan_conn.get_normal_transactions(somm_contract_dict["address"])
        for tx_dict in tqdm(normal_txs):
            tx_hash = tx_dict['hash']
            tx_receipt = etherscan_conn.get_tx_receipt(transaction_string=tx_hash)
            all_tx_logs = tx_receipt['logs']
            if len(all_tx_logs) > 0:
                # Select log with topic0
                for tx_log in all_tx_logs:
                    if tx_log["topics"][0] == somm_contract_dict['topic0']:
                        decoded_event = decode_log(data=tx_log['data'], topics=tx_log['topics'], abi=etherscan_conn.get_contract_abi(address=tx_log['address']))
                        decoded_event_dict = json.loads(decoded_event[1])
                        event_dict = {}
                        # event_dict keys: [pool, liquidity, somm_user_address]
                        event_dict['liquidity'] = int(math.sqrt(decoded_event_dict['amount0'] * decoded_event_dict['amount1']))

                        if decoded_event[0] == "Burn":
                            event_dict['liquidity'] *= -1

                        event_dict['somm_user_address'] = tx_receipt['from']
                        event_dict["pool"] = tx_log["address"]

                        # Only count transactions with block number < maximum block number
                        if int(tx_receipt['blockNumber'], 16) < maximum_block_number:
                            mints_burns_dict.append(event_dict)


    mints_burns_df = pd.DataFrame(mints_burns_dict)
    unique_somm_users = mints_burns_df['somm_user_address'].unique().tolist()
    mints_burns_df.to_csv("somm_v2_mints_burns.csv")
    pd.Series(mints_burns_df['somm_user_address'].unique()).to_csv("somm_v2_user_addresses.csv")

    breakpoint()