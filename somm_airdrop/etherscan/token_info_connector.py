from typing import Any, Dict, List, Union
import requests
import ratelimit
import time
import tenacity
import logging
import custom_secrets


class TokenInfoConnector:

    endpoint_preamble = "https://api.etherscan.io/api?"
    API_KEY = custom_secrets.ETHERSCAN_API_KEY

    def token_info_query_url(self, token_id: str) -> str:
        return "".join(self.endpoint_preamble, "?module=token", "&action=tokeninfo",
                       f"&contractaddress={token_id}",
                       f"&apikey=f{self.API_KEY}")

    @tenacity.retry(stop=tenacity.stop_after_attempt(20), 
                    wait=tenacity.wait_exponential(min=0.1, max=5, multiplier=2))
    @ratelimit.sleep_and_retry
    @ratelimit.limits(calls=30, period=1)  # 60-seconds
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
    