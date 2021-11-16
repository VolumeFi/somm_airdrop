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
    
    def get_token_info(self, 
                       token_ids: Union[str, List[str]], 
                       save: bool = False) -> TokenInfoMap:
        """[summary]

        Args:
            token_ids (Union[str, List[str]]): A token address or list of token
                addresses.
            save (bool): Saves the queried token info to json. 
                Defaults to False.

        Raises:
            ValueError: If 'token_ids' is not a string or list.

        Returns:
            token_info_maps (TokenInfoMap): Dict[TokenID, TokenInfo]
        """
        if not isinstance(token_ids, (str, list)):
            raise ValueError()
        if isinstance(token_ids, str):
            token_ids = [token_ids]


        token_info_maps: TokenInfoMap = {}
        for query_count, token_id in enumerate(token_ids):

            query = self._token_info_query_url(token_id=token_id)
            response: List[Dict[str, str]] = self._execute_query(query=query)
            if isinstance(response, str):
                raise Exception(response)

            token_info_map: TokenInfoMap = {token_id: response.pop()}
            token_info_maps.update(token_info_map)
            # if query_count % 2 == 1:   
            #     time.sleep(secs=1) 
            if save:
                self.save_token_info_json(token_info_maps=token_info_maps)
        return token_info_maps
    
    def save_token_info_json(self, 
                             token_info_map: TokenInfoMap):
        """[summary] TODO docs

        Args:
            token_info_map (TokenInfoMap): [description]
        """
        save_path = os.path.join("data", "token_info.json")
        new_token_info_maps = token_info_map

        if not os.path.exists(save_path):
            token_info_json: TokenInfoMap = new_token_info_maps
        else:
            with open(file=save_path, mode='r') as f:
                current_token_info_maps: TokenInfoMap = json.load(f)
                if current_token_info_maps is None:
                    current_token_info_maps = {}
            current_token_info_maps.update(new_token_info_maps)
            token_info_json: TokenInfoMap = current_token_info_maps
            
        with open(save_path, "w") as f:
            json.dump(token_info_json, f, indent=3)