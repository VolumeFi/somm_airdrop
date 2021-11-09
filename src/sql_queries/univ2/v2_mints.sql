BEGIN
-- Code for parsing Sync events from Uniswap v2

CREATE TEMP FUNCTION
    PARSE_MINT(data STRING, topics ARRAY<STRING>)
    RETURNS STRUCT<`amount0` STRING, `amount1` STRING, `sender` STRING>
    LANGUAGE js AS """
    var parsedEvent = {"anonymous": false, "inputs": [{"indexed": false, "internalType": "uint112", "name": "amount0", "type": "uint112"}, {"indexed": false, "internalType": "uint112", "name": "amount1", "type": "uint112"}], "name": "Mint", "type": "event"}
    return abi.decodeEvent(parsedEvent, data, topics, false);
"""
    OPTIONS
  ( library="https://storage.googleapis.com/ethlab-183014.appspot.com/ethjs-abi.js" );



CREATE TABLE uniswap_v2_mints AS (
SELECT
    logs.block_timestamp AS block_timestamp
     ,logs.block_number AS block_number
     ,logs.transaction_hash AS transaction_hash
     ,PARSE_MINT(logs.data, logs.topics).sender as sender_address
     ,PARSE_MINT(logs.data, logs.topics).amount0 AS amount0
     ,PARSE_MINT(logs.data, logs.topics).amount1 AS Amount1
     ,address as pair
FROM `bigquery-public-data.crypto_ethereum.logs` AS logs
         JOIN uniswap_v2_pairs AS pairs ON logs.address = pairs.pair
    --  Filter for only `Mint` events
    AND topics[SAFE_OFFSET(0)] = '0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f'
);

-- END;