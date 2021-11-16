"""TODO module docs for somm_airdrop.etherscan"""
from somm_airdrop.etherscan import etherscan_connector
from somm_airdrop.etherscan import token_info_connector 

EtherscanConnector = etherscan_connector.EtherscanConnector 
TokenInfoConnector = token_info_connector.TokenInfoConnector
# TokenInfoConnector.__doc__ = 
"""TODO doc"""

__all__ = ['EtherscanConnector', 'TokenInfoConnector']
