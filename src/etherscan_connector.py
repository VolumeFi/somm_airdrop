import logging
import logging

import requests
from ratelimit import limits, sleep_and_retry
from tenacity import retry, wait_exponential, stop_after_attempt
from token_bucket.limiter import Limiter
from token_bucket.storage import MemoryStorage

from pprint import pprint
from web3 import Web3
from decoding_utils import decode_log
import json
import pandas as pd
from tqdm import tqdm

api_rate_limit_message = "Max rate limit reached"

# Etherscan Logs:
# https://docs.etherscan.io/api-endpoints/logs

# ======================================================================================================================


class EtherscanApiConnector(object):
    etherscan_api = "https://api.etherscan.io/api?"

    # Needed to get the gas spent
    TRANSACTION_RECEIPT_URL = etherscan_api + \
        "module=proxy&action=eth_getTransactionReceipt&txhash={transaction_hash}&apikey={api_key}"

    EVENT_LOG_URL = etherscan_api + \
        "module=logs&action=getLogs&address={address}&topic0={topic0}&apikey={api_key}"

    API_KEY = "FCD48UAF7G87XBTK3G934Q42MCV8PE3TVM"

    # ------------------------------------------------------------------------------------------------------------------
    @retry(stop=stop_after_attempt(20), wait=wait_exponential(min=0.1, max=5, multiplier=2))
    @sleep_and_retry
    @limits(calls=30, period=1)  # 60-seconds
    def _execute_query(self, query):
        """
        Func is wrapped with some ultimate limiters to ensure this method is never callled too much.  However, the
        batch-call function should also limit itself, since it is likely to have a higher-level awareness (at least
        passed in by the caller) as to how the rate itself should be spread across different token-pairs
        :param str query: URL/API endpoint to query with Requests.request.get()
        :return: dict component of the Requests.Response object
        :rtype dict
        """
        # ToDo: Parse response to see if the rate-limit has been hit
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.get(query, headers=headers)
            if response and response.ok:
                return response.json()['result']
            else:
                msg = f"Failed request with status code {response.status_code}:  {response.text}"
                logging.warning(msg)
                raise Exception(msg)

        except Exception:
            logging.exception(f"Problem in query: {query}")
            # Raise so retry can retry
            raise

    # ------------------------------------------------------------------------------------------------------------------

    def get_tx_receipt(self, transaction_string: str):
        query = self.TRANSACTION_RECEIPT_URL.format(
            transaction_hash=transaction_string, api_key=self.API_KEY)
        tx_receipt = self._execute_query(query)
        return tx_receipt

    def get_event_log(self, address: str, topic0: str):
        query = self.EVENT_LOG_URL.format(
            address=address, topic0=topic0, api_key=self.API_KEY)
        return self._execute_query(query)


# Uniswap V3 Liquidity Release1 Add
CONTRACT_ABI = [{"name": "AddedLiquidity", "inputs": [{"name": "tokenId", "type": "uint256", "indexed": True}, {"name": "token0", "type": "address", "indexed": True}, {"name": "token1", "type": "address", "indexed": True}, {"name": "liquidity", "type": "uint256", "indexed": False}, {"name": "amount0", "type": "uint256", "indexed": False}, {"name": "amount1", "type": "uint256", "indexed": False}], "anonymous": False, "type": "event"}, {"name": "NFLPModified", "inputs": [{"name": "oldTokenId", "type": "uint256", "indexed": True}, {"name": "newTokenId", "type": "uint256", "indexed": True}], "anonymous": False, "type": "event"}, {"name": "Paused", "inputs": [{"name": "paused", "type": "bool", "indexed": False}], "anonymous": False, "type": "event"}, {"stateMutability": "nonpayable", "type": "constructor", "inputs": [], "outputs":[]}, {"stateMutability": "payable", "type": "function", "name": "addLiquidityEthForUniV3", "inputs": [{"name": "_tokenId", "type": "uint256"}, {"name": "uniV3Params", "type": "tuple", "components": [{"name": "token0", "type": "address"}, {"name": "token1", "type": "address"}, {"name": "fee", "type": "uint256"}, {"name": "tickLower", "type": "int128"}, {"name": "tickUpper", "type": "int128"}, {"name": "amount0Desired", "type": "uint256"}, {"name": "amount1Desired", "type": "uint256"}, {"name": "amount0Min", "type": "uint256"}, {"name": "amount1Min", "type": "uint256"}, {"name": "recipient", "type": "address"}, {"name": "deadline", "type": "uint256"}]}], "outputs": [], "gas":963921}, {"stateMutability": "nonpayable", "type": "function", "name": "addLiquidityForUniV3", "inputs": [{"name": "_tokenId", "type": "uint256"}, {"name": "uniV3Params", "type": "tuple", "components": [{"name": "token0", "type": "address"}, {"name": "token1", "type": "address"}, {"name": "fee", "type": "uint256"}, {"name": "tickLower", "type": "int128"}, {"name": "tickUpper", "type": "int128"}, {"name": "amount0Desired", "type": "uint256"}, {"name": "amount1Desired", "type": "uint256"}, {
    "name": "amount0Min", "type": "uint256"}, {"name": "amount1Min", "type": "uint256"}, {"name": "recipient", "type": "address"}, {"name": "deadline", "type": "uint256"}]}], "outputs": [], "gas":867874}, {"stateMutability": "nonpayable", "type": "function", "name": "modifyPositionForUniV3NFLP", "inputs": [{"name": "_tokenId", "type": "uint256"}, {"name": "modifyParams", "type": "tuple", "components": [{"name": "fee", "type": "uint256"}, {"name": "tickLower", "type": "int128"}, {"name": "tickUpper", "type": "int128"}, {"name": "recipient", "type": "address"}, {"name": "deadline", "type": "uint256"}]}], "outputs": [], "gas":547339}, {"stateMutability": "nonpayable", "type": "function", "name": "pause", "inputs": [{"name": "_paused", "type": "bool"}], "outputs": [], "gas":39101}, {"stateMutability": "nonpayable", "type": "function", "name": "newAdmin", "inputs": [{"name": "_admin", "type": "address"}], "outputs": [], "gas":37784}, {"stateMutability": "nonpayable", "type": "function", "name": "newFeeAddress", "inputs": [{"name": "_feeAddress", "type": "address"}], "outputs": [], "gas":37814}, {"stateMutability": "nonpayable", "type": "function", "name": "batchWithdraw", "inputs": [{"name": "token", "type": "address[8]"}, {"name": "amount", "type": "uint256[8]"}, {"name": "to", "type": "address[8]"}], "outputs": [], "gas":352127}, {"stateMutability": "nonpayable", "type": "function", "name": "withdraw", "inputs": [{"name": "token", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "to", "type": "address"}], "outputs": [], "gas":96427}, {"stateMutability": "payable", "type": "fallback"}, {"stateMutability": "view", "type": "function", "name": "paused", "inputs": [], "outputs":[{"name": "", "type": "bool"}], "gas": 2718}, {"stateMutability": "view", "type": "function", "name": "admin", "inputs": [], "outputs":[{"name": "", "type": "address"}], "gas": 2748}, {"stateMutability": "view", "type": "function", "name": "feeAddress", "inputs": [], "outputs":[{"name": "", "type": "address"}], "gas": 2778}]
ADDRESS = "0x8039722EE74dE2e37fDc39783b0a574Ea492DBAc"

if __name__ == "__main__":
    etherscan_conn = EtherscanApiConnector()

    mints_burns_dict = []

    all_events = etherscan_conn.get_event_log(
        address=ADDRESS, topic0="0x8608f0d1a9f263ba6515609d93d7510949b8477690ce655f3b813420049d3d84")
    for event in tqdm(all_events):
        decoded_event = decode_log(
            event['data'], topics=event['topics'], abi=CONTRACT_ABI)

        event_dict = json.loads(decoded_event[1])

        if decoded_event[0] == "RemovedLiquidity":
            event_dict['liquidity'] *= -1

        event_tx_receipt = etherscan_conn.get_tx_receipt(
            transaction_string=event['transactionHash'])
        event_dict['somm_user_address'] = event_tx_receipt['from']
        mints_burns_dict.append(event_dict)

    mints_burns_df = pd.DataFrame(mints_burns_dict)
    unique_somm_users = mints_burns_df['somm_user_address'].unique().tolist()
