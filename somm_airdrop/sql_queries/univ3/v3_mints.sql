BEGIN
-- Code for parsing Sync events from Uniswap v2

CREATE TEMP FUNCTION
    PARSE_MINT(data STRING, topics ARRAY<STRING>)
    RETURNS STRUCT<`amount0` STRING, `amount1` STRING, `liquidity` STRING>
    LANGUAGE js AS """

    var parsedEvent = {
        "anonymous": false,
        "inputs": [
            {"indexed": false, "internalType": "uint112", "name": "amount0", "type": "uint112"}, 
            {"indexed": false, "internalType": "uint112", "name": "amount1", "type": "uint112"}, 
            {"indexed": false, "internalType": "uint112", "name": "liquidity", "type": "uint112"}
        ],
        "name": "IncreaseLiquidity", "type": "event"
    }
    return abi.decodeEvent(parsedEvent, data, topics, false);

"""
    OPTIONS
  ( library="https://storage.googleapis.com/ethlab-183014.appspot.com/ethjs-abi.js" );




CREATE TABLE uniswap_v3_mints AS (
SELECT DISTINCT
    logs.block_timestamp AS block_timestamp
     ,logs.block_number AS block_number
     ,logs.transaction_hash AS transaction_hash
     ,PARSE_MINT(logs.data, logs.topics).amount0 AS amount0
     ,PARSE_MINT(logs.data, logs.topics).amount1 AS amount1
     ,PARSE_MINT(logs.data, logs.topics).liquidity AS liquidity
     ,pool_logs.address as pool
     ,pools.token0
     ,pools.token1
FROM `bigquery-public-data.crypto_ethereum.logs` AS logs
    --  Filter for only `DecreaseLiquidity` events
    JOIN `bigquery-public-data.crypto_ethereum.logs` AS pool_logs ON pool_logs.transaction_hash = logs.transaction_hash
    JOIN `bigquery-public-data.crypto_ethereum.transactions` AS transactions ON transactions.hash = logs.transaction_hash
    JOIN uniswap_v3_pools AS pools on pools.pool=pool_logs.address
    -- "0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f" is the IncreaseLiquidity topic
    WHERE logs.topics[SAFE_OFFSET(0)] = '0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f'
    -- "0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde" is the log that emits the pool address for mints
    AND pool_logs.topics[SAFE_OFFSET(0)] = '0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde'
);

-- TODO: Look at "Transfer" event to get Pool address

-- END;