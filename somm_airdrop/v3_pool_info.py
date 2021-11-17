"""
See SIPs-002 proposal: https://community.sommelier.finance/t/sips-002-a-proposal-for-a-sommelier-token-airdrop-of-somm-to-select-liquidity-providers/272
"""

from typing import Dict, List

AIRDROP_POOLS: List[str] = [
    '0x3019d4e366576a88d28b623afaf3ecb9ec9d9580',
    '0xc2e9f25be6257c210d7adf0d4cd6e3e881ba25f8',
    '0x60594a405d53811d3bc4766596efd80fd545a270',
    '0x97e7d56a0408570ba1a7852de36350f7713906ec',
    '0x7379e81228514a1d2a6cf7559203998e20598346',
    '0x8c54aa2a32a779e6f6fbea568ad85a19e0109c26',
    '0xc63b0708e2f7e69cb8a1df0e1389a98c35a76d52',
    # '0xc2a856c3aff2110c1171b8f942256d40e980c726',
    '0x3b685307c8611afb2a9e83ebc8743dc20480716e',
    '0xa6cc3c2531fdaa6ae1a3ca84c2855806728693e8',
    '0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801',
    '0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8',
    '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
    '0x7858e59e0c01ea06df3af3d20ac7b0003275d4bf',
    '0x4585fe77225b41b697c938b018e2ac67ac5a20c0',
    '0xcbcdf9626bc03e24f779434178a73a0b4bad62ed',
    '0x8f8ef111b67c04eb1641f5ff19ee54cda062f163',
    '0x99ac8ca7087fa4a2a1fb6357269965a2014abc35',
    '0x9db9e0e53058c89e5b94e29621a205198648425b',
    '0x4e68ccd3e89f51c3074ca5072bbac773960dfa36',
    '0x11b815efb8f581194ae79006d24e0d814b7697f6']

POOL_TO_ADDRESS: Dict[str, str] = {
    "AXS_WETH_0pt3": "0x3019d4e366576a88d28b623afaf3ecb9ec9d9580",
    "DAI_WETH_0pt3": "0xc2e9f25be6257c210d7adf0d4cd6e3e881ba25f8",
    "DAI_WETH_0pt05": "0x60594a405d53811d3bc4766596efd80fd545a270",
    "DAI_FRAX_0pt05": "0x97e7d56a0408570ba1a7852de36350f7713906ec",
    "WETH_sETH2_0pt3": "0x7379e81228514a1d2a6cf7559203998e20598346",
    "FEI_USDC_0pt05": "0x8c54aa2a32a779e6f6fbea568ad85a19e0109c26",
    "FRAX_USDC_0pt05": "0xc63b0708e2f7e69cb8a1df0e1389a98c35a76d52",
    # "FRAX_USDT_0pt05": "0xc2a856c3aff2110c1171b8f942256d40e980c726",
    "FTM_WETH_1pt": "0x3b685307c8611afb2a9e83ebc8743dc20480716e",
    "HEX_USDC_0pt3": "0x69d91b94f0aaf8e8a2586909fa77a5c2c89818d5", 
    "LINK_WETH_0pt3": "0xa6cc3c2531fdaa6ae1a3ca84c2855806728693e8",
    "UNI_WETH_0pt3": "0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801",
    "USDC_WETH_0pt3": "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8",
    "USDC_WETH_0pt05": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
    "USDC_USDT_0pt05": "0x7858e59e0c01ea06df3af3d20ac7b0003275d4bf",
    "WBTC_WETH_0pt05": "0x4585fe77225b41b697c938b018e2ac67ac5a20c0",
    "WBTC_WETH_0pt3": "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed",
    "WBTC_PAX_0pt3": "0x8f8ef111b67c04eb1641f5ff19ee54cda062f163",
    "WBTC_USDC_0pt3": "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35",
    "WBTC_USDT_0pt3": "0x9db9e0e53058c89e5b94e29621a205198648425b",
    "WETH_USDT_0pt3": "0x4e68ccd3e89f51c3074ca5072bbac773960dfa36",
    "WETH_USDT_0pt05": "0x11b815efb8f581194ae79006d24e0d814b7697f6"}
"""Map from human-readable pool name to pool address""" 

ADDRESS_TO_POOL: Dict[str, str] = {v: k for k, v in POOL_TO_ADDRESS.items()}
"""Map from pool address to human-readable pool name""" 


TOKEN_REWARD: int = 300000