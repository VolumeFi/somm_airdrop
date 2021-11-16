from typing import Any, Dict, List, Union
import requests
import ratelimit
import time
import os
import json
import tenacity
import logging
from somm_airdrop.etherscan import etherscan_connector

TokenID = str
TokenInfo = Dict[str, str]
TokenInfoMap = Dict[TokenID, TokenInfo]

class TokenInfoConnector(etherscan_connector.EtherscanConnector):
    """An Etherscan API connector for gathering token info. 

    Attributes:
        API_KEY (str)
    """

    endpoint_preamble = "https://api.etherscan.io/api?"
    API_KEY: str

    def _token_info_query_url(self, token_id: str) -> str:
        return "".join([
            self.endpoint_preamble, "module=token", "&action=tokeninfo",
            f"&contractaddress={token_id}", f"&apikey={self.API_KEY}"])

    @ratelimit.limits(calls=2, period=1) 
    def _execute_query(self, query: str):
        """Note, Etherscan restricts the token_info query to 2 calls per second.
        
        Args: 
            query (str): URL/API endpoint to query with `Requests.request.get()`
        
        Returns: 
            (dict): Component of the Requests.Response object
        """
        return super()._execute_query(query=query)
    
    def get_token_info(self, token_ids: Union[str, List[str]]) -> Dict[str, Any]:
        if not isinstance(token_ids, (str, list)):
            raise ValueError()
        if isinstance(token_ids, str):
            token_ids = [token_ids]

        token_infos: list = []
        for query_count, token_id in enumerate(token_ids):
            query = self.token_info_query_url(token_id=token_id)
            token_infos.append(self._execute_query(query=query))
            if query_count % 2 == 1:   
            # Etherscan restricts this API to a rate of 2 calls per second.
                time.sleep(secs=1) 
        return {token_ids[i]: token_infos[i] for i, token in enumerate(token_ids)}
    