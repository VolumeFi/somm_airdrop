from typing import Any, Dict
import requests
import ratelimit
import tenacity
import logging

import somm_airdrop.custom_secrets

class EtherscanConnector:

    api_endpoint_preamble = "https://api.etherscan.io/api?"
    API_KEY = somm_airdrop.custom_secrets.ETHERSCAN_API_KEY

    # Needed to get the gas spent
    EVENT_LOG_URL = api_endpoint_preamble + \
        "module=logs&action=getLogs&address={address}&topic0={topic0}&apikey={api_key}"

    TRANSACTION_LIST_URL = api_endpoint_preamble + \
        "module=account&action=txlist&address={address}&sort=asc&apikey={api_key}"
    
    CONTRACT_ABI_URL = api_endpoint_preamble + \
        "module=contract&action=getabi&address={address}&apikey={api_key}"
    
    BLOCK_NUMBER_BY_TIMESTAMP = api_endpoint_preamble + \
        "module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={api_key}"


    def run_query(self, query, rate_limit: bool = False) -> requests.Response:
        """Func is wrapped with some ultimate limiters to ensure this method is 
        never callled too much.  However, the batch-call function should also 
        limit itself, since it is likely to have a higher-level awareness (at 
        least passed in by the caller) as to how the rate itself should be 
        spread across different token-pairs

        :param str query: URL/API endpoint to query with Requests.request.get()
        :return: dict component of the Requests.Response object
        :rtype dict
        """
        response: requests.Response
        if rate_limit:
            response = self._run_query_with_rate_limit(query=query)
        else:
            response = self._run_base_query(query=query)
        return response


    @tenacity.retry(stop=tenacity.stop_after_attempt(20), 
                    wait=tenacity.wait_exponential(min=0.1, max=5, multiplier=2))
    @ratelimit.sleep_and_retry
    @ratelimit.limits(calls=30, period=1)  # period (float) is in seconds.
    def _run_query_with_rate_limit(self, query: str) -> requests.Response:
        return self._run_base_query(query=query)

    def _run_base_query(self, query: str) -> requests.Response:
        # TODO: Parse response to see if the rate-limit has been hit
        headers = {'Content-Type': 'application/json'}
        try:
            response: requests.Response = requests.get(query, headers=headers)
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

    def get_tx_receipt(self, tx_hash: str) -> Dict[str, Any]:
        TRANSACTION_RECEIPT_URL = "".join([
            self.api_endpoint_preamble, "module=proxy", 
            "&action=eth_getTransactionReceipt", "&txhash={transaction_hash}", 
            "&apikey={api_key}"])

        query = TRANSACTION_RECEIPT_URL.format(
            transaction_hash=tx_hash, api_key=self.API_KEY)
        tx_receipt = self.run_query(query)
        return tx_receipt

    def get_event_log(self, address: str, topic0: str):
        query = self.EVENT_LOG_URL.format(
            address=address, topic0=topic0, api_key=self.API_KEY)
        return self.run_query(query)
    
    def get_normal_transactions(self, address: str):
        query = self.TRANSACTION_LIST_URL.format(address=address, api_key=self.API_KEY)
        return self.run_query(query)

    
    def get_contract_abi(self, address: str):
        query = self.CONTRACT_ABI_URL.format(address=address, api_key=self.API_KEY)
        return self.run_query(query)
    
    def get_block_number_before_timestamp(self, timestamp: int):
        query = self.BLOCK_NUMBER_BY_TIMESTAMP.format(timestamp=timestamp, api_key=self.API_KEY)
        return self.run_query(query)

