BEGIN
-- Code for parsing Sync events from Uniswap v2

CREATE TEMP FUNCTION
    PARSE_BURN(data STRING, topics ARRAY<STRING>)
    RETURNS STRUCT<`amount0` STRING, `amount1` STRING>
    LANGUAGE js AS """
    var parsedEvent = {
        "anonymous": false, 
        "inputs": [
            {"indexed": false, "internalType": "uint256", "name": "amount0", "type": "uint256"}, 
            {"indexed": false, "internalType": "uint256", "name": "amount1", "type": "uint256"}, 
        ],
        "name": "Burn", "type": "event"}
    return abi.decodeEvent(parsedEvent, data, topics, false);
"""
    OPTIONS
  ( library="https://storage.googleapis.com/ethlab-183014.appspot.com/ethjs-abi.js" );



CREATE TABLE somm_v2_burns AS (
SELECT
    logs.block_timestamp AS block_timestamp
    ,logs.block_number AS block_number
    ,logs.transaction_hash AS transaction_hash
    ,PARSE_BURN(logs.data, logs.topics).amount0 AS amount0
    ,PARSE_BURN(logs.data, logs.topics).amount1 AS amount1
    ,logs.address as pair
    ,transactions.from_address AS from_address
    ,pairs.token0
    ,pairs.token1
    --  ,address as pair
FROM `bigquery-public-data.crypto_ethereum.logs` AS logs
    JOIN `bigquery-public-data.crypto_ethereum.transactions` AS transactions ON logs.transaction_hash=transactions.hash
    JOIN uniswap_v2_pairs AS pairs on logs.address=pairs.pair
    WHERE 
        (transactions.to_address="0x418915329226ae7fccb20a2354bbbf0f6c22bd92"
        OR transactions.to_address="0x430f33353490b256d2fd7bbd9dadf3bb7f905e78"
        )
    AND logs.topics[SAFE_OFFSET(0)] = '0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496'
);


-- END;