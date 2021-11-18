from typing import Any, Dict, List, Union
import requests
from requests import exceptions
import ratelimit
import time
import os
import json
import tenacity
import logging

from somm_airdrop import custom_secrets
# https://pro-api.coinmarketcap.com/v1/cryptocurrency/map

class CoinMarketCapConnector:
    """Python connector the Coin Market Cap API.

    Attributes:
        API_KEY (str)
    """

    endpoint_preamble = "" # TODO
    API_KEY: str = custom_secrets.COINMARKETCAP_API_KEY 

    # @ratelimit.limits(calls=2, period=1) 
    def run_query(self, 
                  endpoint: str, 
                  params: Dict[str, str]) -> Union[list, dict]:
        """Note, Etherscan restricts the token_info query to 2 calls per second.
        
        Args: 
            endpoint (str): URL/API endpoint to query with `Requests.request.get()`
            params (Dict[str, str]): TODO
        
        Returns: 
            (dict): Component of the Requests.Response object
        """
        headers = {
            'Accepts': 'application/json', 
            'X-CMC_PRO_API_KEY': self.API_KEY}
        session = requests.Session()
        session.headers.update(headers)
        try:
            response: requests.Response = session.get(
                endpoint, headers=headers, params=params)
            if response and response.ok:
                return response.json()['result']
            else:
                msg = (f"Failed request with status code {response.status_code}"
                       + f": {response.text}")
                logging.warning(msg)
                raise Exception(msg)
        except (exceptions.ConnectionError, 
                exceptions.Timeout, 
                exceptions.TooManyRedirects) as e:
            logging.exception("\n".join([
                f"ConnectionError: {e[0]}", f"Timeout: {e[1]}", 
                f"TooManyRedirects: {e[2]}"]))
            raise # Raise so retry can retry
        except Exception as e:
            logging.exception(f"Exception raised: {e}")
            raise # Raise so retry can retry
    
    def foo(self, ) -> str:

        ...

    # -----------------------------------------------   
    # TODO
    # -----------------------------------------------   

    def _currency_map_query_url(self, token_id: str) -> str:
        # TODO needs refactor.
        return "".join([
            self.endpoint_preamble, "module=token", "&action=tokeninfo",
            f"&contractaddress={token_id}", f"&apikey={self.API_KEY}"])

    def get_token_info(self, 
                       token_ids: Union[str, List[str]], 
                       save: bool = False, 
                       verbose: bool = False) -> TokenInfoMap:
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

        for _, token_id in enumerate(token_ids):
            # Make query.
            query = self._token_info_query_url(token_id=token_id)
            response: List[Dict[str, str]] = self.run_query(query=query)
            if isinstance(response, str):
                raise Exception(response)

            # Create token info map
            token_info_map: TokenInfoMap = {token_id: response[0]}
            token_info_maps.update(token_info_map)

            if _ % 2 == 1:
                time.sleep(0.99) # Wait 1 second after 2 queries.

            if save:
                self.save_token_info_json(token_info_map=token_info_maps)
            if verbose:
                print(f"Token info gathered for {response[0]['symbol']}.")

        return token_info_maps

class CoinMarketCapEndpoint: 
    """
    Args & Attributes: 
        category (str): CMC endpoint category.
        path (str): CMC endpoint path.
    
    Endpoint categories:
        cryptocurrency: Endpoints that return data around cryptocurrencies such 
            as ordered cryptocurrency lists or price and volume data.
        exchange: Endpoints that return data around cryptocurrency exchanges 
            such as ordered exchange lists and market pair data.
        global-metrics: Endpoints that return aggregate market data such as 
            global market cap and BTC dominance.
        tools: Utilities such as cryptocurrency and fiat price conversions.
        blockchain: Endpoints that return block explorer related data.
        fiat: Endpoints that return data around fiats currencies including 
            mapping to CMC IDs.
        partners: Endpoints for convenient access to 3rd party crypto data.
        key: API key administration endpoints to review and manage your usage.

    Endpoint paths:
        latest: Latest market data. Latest market ticker quotes and averages for 
            cryptocurrencies and exchanges.
        historical: Historical market data. Intervals of historic market data 
            like OHLCV data or data for use in charting libraries.
        info: Metadata. Cryptocurrency and exchange metadata like block explorer
            URLs and logos.
        map: ID maps. Utility endpoints to get a map of resources to 
            CoinMarketCap IDs.
    """

    endpoint_categories: List[str] = [
        "cryptocurrency", "exchange", "global-metrics", "tools", "blockchain", 
        "fiat", "partners", "key"]
    endpoint_paths: List[str] = ["latest", "historical", "info", "map"]

    def __init__(self, category: str, path: str):
        if category not in self.endpoint_categories:
            raise ValueError("") # TODO
        if path not in self.endpoint_paths:
            raise ValueError("") # TODO
        self.category = category
        self.path = path
    
    def get(self) -> str:
        ...
    
    
        