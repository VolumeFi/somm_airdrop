import requests
from ratelimit import limits, sleep_and_retry
from tenacity import retry, wait_exponential, stop_after_attempt


class EtherscanApiConnector(object):
    etherscan_api = "https://api.etherscan.io/api?"

    # Needed to get the gas spent
    TRANSACTION_RECEIPT_URL = etherscan_api + \
        "module=proxy&action=eth_getTransactionReceipt&txhash={transaction_hash}&apikey={api_key}"

    EVENT_LOG_URL = etherscan_api + \
        "module=logs&action=getLogs&address={address}&topic0={topic0}&apikey={api_key}"

    TRANSACTION_LIST_URL = etherscan_api + \
        "module=account&action=txlist&address={address}&sort=asc&apikey={api_key}"
    
    CONTRACT_ABI_URL = etherscan_api + \
        "module=contract&action=getabi&address={address}&apikey={api_key}"
    
    BLOCK_NUMBER_BY_TIMESTAMP = etherscan_api + \
        "module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={api_key}"

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
    
    def get_normal_transactions(self, address: str):
        query = self.TRANSACTION_LIST_URL.format(address=address, api_key=self.API_KEY)
        return self._execute_query(query)

    
    def get_contract_abi(self, address: str):
        query = self.CONTRACT_ABI_URL.format(address=address, api_key=self.API_KEY)
        return self._execute_query(query)
    
    def get_block_number_before_timestamp(self, timestamp: int):
        query = self.BLOCK_NUMBER_BY_TIMESTAMP.format(timestamp=timestamp, api_key=self.API_KEY)
        return self._execute_query(query)

