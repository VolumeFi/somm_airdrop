BEGIN

CREATE TEMP FUNCTION
    PARSE_V3_CREATE_LOG(data STRING, topics ARRAY<STRING>)
    RETURNS STRUCT<`token0` STRING, `token1` STRING, `pool` STRING>
    LANGUAGE js AS """
    const parsedEvent = {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "type": "address", "name": "token0"},
            {"indexed": true, "type": "address", "name": "token1"},
            {"indexed": false, "type": "uint256", "name": ""},
            {"indexed": false, "type": "address", "name": "pool"},
                   ],
        "name": "PoolCreated",
        "type": "event"
    }
    return abi.decodeEvent(parsedEvent, data, topics, false);
"""
    OPTIONS
  ( library="https://storage.googleapis.com/ethlab-183014.appspot.com/ethjs-abi.js" );

CREATE TABLE uniswap_v3_pools
AS
(
    SELECT
        PARSE_V3_CREATE_LOG(logs.data, logs.topics).token0 AS token0,
        PARSE_V3_CREATE_LOG(logs.data, logs.topics).token1 AS token1,
        PARSE_V3_CREATE_LOG(logs.data, logs.topics).pool AS pool
    -- Below address is the Uniswap v3 factory address. These cna be found on 
    -- https://etherscan.io/address/0x1f98431c8ad98523631ae4a59f267346ea31f984
    FROM `bigquery-public-data.crypto_ethereum.logs` AS logs
    WHERE address = '0x1f98431c8ad98523631ae4a59f267346ea31f984'
    -- Pool creation topic: can be found at Uniswap V3 factory / events
    AND topics[SAFE_OFFSET(0)] = '0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118'
);

-- END;
