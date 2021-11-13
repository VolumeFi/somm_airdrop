BEGIN
-- Code for parsing Sync events from Uniswap v2

CREATE TEMP FUNCTION
    PARSE_MINT(data STRING, topics ARRAY<STRING>)
    RETURNS STRUCT<`amount0` STRING, `amount1` STRING>
    LANGUAGE js AS """
    var parsedEvent = {
        "anonymous": false, 
        "inputs": [
            {"indexed": false, "internalType": "uint256", "name": "amount0", "type": "uint256"}, 
            {"indexed": false, "internalType": "uint256", "name": "amount1", "type": "uint256"}, 
        ],
        "name": "Mint", "type": "event"}
    return abi.decodeEvent(parsedEvent, data, topics, false);
"""
    OPTIONS
  ( library="https://storage.googleapis.com/ethlab-183014.appspot.com/ethjs-abi.js" );



CREATE TABLE somm_v2_mints AS (
SELECT
    logs.block_timestamp AS block_timestamp
    ,logs.block_number AS block_number
    ,logs.transaction_hash AS transaction_hash
    ,PARSE_MINT(logs.data, logs.topics).amount0 AS amount0
    ,PARSE_MINT(logs.data, logs.topics).amount1 AS amount1
    ,logs.address as pair
    ,transactions.from_address AS from_address
    ,pairs.token0
    ,pairs.token1
    --  ,address as pair
FROM `bigquery-public-data.crypto_ethereum.logs` AS logs
    JOIN `bigquery-public-data.crypto_ethereum.transactions` AS transactions ON logs.transaction_hash=transactions.hash
    JOIN uniswap_v2_pairs AS pairs on logs.address=pairs.pair
    WHERE 
        (transactions.to_address="0xfd8a61f94604aed5977b31930b48f1a94ff3a195"
        OR transactions.to_address="0xa522aa47c40f2bac847cbe4d37455c521e69dea7"
        )
    AND logs.topics[SAFE_OFFSET(0)] = '0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f'
);


-- END;