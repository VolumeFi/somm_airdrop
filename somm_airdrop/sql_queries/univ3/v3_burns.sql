BEGIN
-- Code for parsing Sync events from Uniswap v2

CREATE TEMP FUNCTION
    PARSE_BURN(data STRING, topics ARRAY<STRING>)
    RETURNS STRUCT<`amount0` STRING, `amount1` STRING, `liquidity` STRING>
    LANGUAGE js AS """

    var parsedEvent = {
        "anonymous": false,
        "inputs": [
            {"indexed": false, "internalType": "uint112", "name": "amount0", "type": "uint112"}, 
            {"indexed": false, "internalType": "uint112", "name": "amount1", "type": "uint112"}, 
            {"indexed": false, "internalType": "uint112", "name": "liquidity", "type": "uint112"}
        ],
        "name": "DecreaseLiquidity", "type": "event"
    }
    return abi.decodeEvent(parsedEvent, data, topics, false);

"""
    OPTIONS
  ( library="https://storage.googleapis.com/ethlab-183014.appspot.com/ethjs-abi.js" );


CREATE TABLE uniswap_v3_burns AS (
SELECT DISTINCT
    logs.block_timestamp AS block_timestamp
     ,logs.block_number AS block_number
     ,logs.transaction_hash AS transaction_hash
     ,PARSE_BURN(logs.data, logs.topics).amount0 AS amount0
     ,PARSE_BURN(logs.data, logs.topics).amount1 AS amount1
     ,PARSE_BURN(logs.data, logs.topics).liquidity AS liquidity
     ,pool_logs.address as pool
     ,transactions.from_address AS from_address
     ,pools.token0
     ,pools.token1
FROM `bigquery-public-data.crypto_ethereum.logs` AS logs
    --  Filter for only `DecreaseLiquidity` events
    JOIN `bigquery-public-data.crypto_ethereum.logs` AS pool_logs ON pool_logs.transaction_hash = logs.transaction_hash
    JOIN `bigquery-public-data.crypto_ethereum.transactions` AS transactions ON transactions.hash = logs.transaction_hash
    JOIN uniswap_v3_pools AS pools on pools.pool=pool_logs.address
    -- "0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4" is the DecreaseLiquidity topic
    WHERE logs.topics[SAFE_OFFSET(0)] = '0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4'
    -- "0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c" is the log that emits the pool address for burns
    AND pool_logs.topics[SAFE_OFFSET(0)] = '0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c'
);

-- END;