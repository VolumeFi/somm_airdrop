BEGIN
-- Code for parsing Sync events from Uniswap v2

CREATE TEMP FUNCTION
    PARSE_BURN(data STRING, topics ARRAY<STRING>)
    RETURNS STRUCT<`amount0` STRING, `amount1` STRING, `token0` STRING, `token1` STRING, `liquidity` STRING>
    LANGUAGE js AS """
    var parsedEvent = {
        "anonymous": false, 
        "inputs": [
            {"indexed": true, "internalType": "uint256", "name": "tokenId", "type": "uint256"}, 
            {"indexed": true, "internalType": "address", "name": "token0", "type": "address"}, 
            {"indexed": true, "internalType": "address", "name": "token1", "type": "address"}, 
            {"indexed": false, "internalType": "uint256", "name": "liquidity", "type": "uint256"}, 
            {"indexed": false, "internalType": "uint256", "name": "amount0", "type": "uint256"}, 
            {"indexed": false, "internalType": "uint256", "name": "amount1", "type": "uint256"}, 
        ],
        "name": "RemovedLiquidity", "type": "event"}
    return abi.decodeEvent(parsedEvent, data, topics, false);
"""
    OPTIONS
  ( library="https://storage.googleapis.com/ethlab-183014.appspot.com/ethjs-abi.js" );



CREATE TABLE somm_v3_burns AS (
SELECT
    logs.block_timestamp AS block_timestamp
     ,logs.block_number AS block_number
     ,logs.transaction_hash AS transaction_hash
     ,PARSE_BURN(logs.data, logs.topics).amount0 AS amount0
     ,PARSE_BURN(logs.data, logs.topics).amount1 AS amount1
     ,PARSE_BURN(logs.data, logs.topics).liquidity AS liquidity
     ,mint_burn_logs.address AS pool
     ,transactions.from_address AS from_address
     ,PARSE_BURN(logs.data, logs.topics).token0 AS token0
     ,PARSE_BURN(logs.data, logs.topics).token1 AS token1
    
FROM `bigquery-public-data.crypto_ethereum.logs` AS logs
    JOIN `bigquery-public-data.crypto_ethereum.logs` AS mint_burn_logs ON mint_burn_logs.transaction_hash = logs.transaction_hash
    JOIN `bigquery-public-data.crypto_ethereum.transactions` AS transactions ON logs.transaction_hash=transactions.hash
    --  Filter for only `Burn` events
    -- "0x24345136764733eb66b7482a1178ace3dc025c4dd07e4abacdc7e1b445e70751" is the "RemovedLiquidity" topic
    WHERE logs.topics[SAFE_OFFSET(0)] = '0x24345136764733eb66b7482a1178ace3dc025c4dd07e4abacdc7e1b445e70751'
    -- "0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c" is a topic whose address is the pool
    AND mint_burn_logs.topics[SAFE_OFFSET(0)] = "0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c"
);

-- END;