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




CREATE TEMP FUNCTION
    PARSE_TRANSFER(data STRING, topics ARRAY<STRING>)
    RETURNS STRUCT<`src` STRING, `dst` STRING>
    LANGUAGE js AS """

    var parsedEvent = {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "internalType": "address", "name": "src", "type": "address"}, 
            {"indexed": true, "internalType": "address", "name": "dst", "type": "address"}, 
            {"indexed": false, "internalType": "uint256", "name": "wad", "type": "uint256"}
        ],
        "name": "Transfer", "type": "event"
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
     ,PARSE_TRANSFER(transfer_logs.data, transfer_logs.topics).src as pool
     ,transactions.from_address
FROM `bigquery-public-data.crypto_ethereum.logs` AS logs
    --  Filter for only `DecreaseLiquidity` events
    JOIN `bigquery-public-data.crypto_ethereum.logs` AS transfer_logs ON transfer_logs.transaction_hash = logs.transaction_hash
    JOIN `bigquery-public-data.crypto_ethereum.transactions` AS transactions ON transactions.hash = logs.transaction_hash
    WHERE logs.topics[SAFE_OFFSET(0)] = '0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4'
    AND transfer_logs.topics[SAFE_OFFSET(0)] = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
    AND transfer_logs.topics[SAFE_OFFSET(2)] = '0x000000000000000000000000c36442b4a4522e871399cd717abdd847ab11fe88'
);

-- TODO: Look at "Transfer" event to get Pool address

-- END;