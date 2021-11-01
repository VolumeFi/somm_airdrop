BEGIN

CREATE TEMP FUNCTION
    PARSE_V3_CREATE_LOG(data STRING, topics ARRAY<STRING>)
    RETURNS STRUCT<`token` STRING, `exchange` STRING>
    LANGUAGE js AS """
    const parsedEvent = {
        "name": "NewExchange",
        "inputs": [{"type": "address", "name": "token", "indexed": true}, {"type": "address", "name": "exchange", "indexed": true}],
        "anonymous": false,
        "type": "event"
    }
    return abi.decodeEvent(parsedEvent, data, topics, false);
"""
    OPTIONS
  ( library="https://storage.googleapis.com/ethlab-183014.appspot.com/ethjs-abi.js" );


CREATE TABLE uniswap_v3_pairs
AS
(
    SELECT
        PARSE_V3_CREATE_LOG(logs.data, logs.topics).token as token,
        PARSE_V3_CREATE_LOG(logs.data, logs.topics).exchange as pair
    FROM `bigquery-public-data.crypto_ethereum.logs` AS logs
    -- Below address is the Uniswap v3 factory address. These cna be found on 
    -- https://etherscan.io/address/0x1f98431c8ad98523631ae4a59f267346ea31f984
    WHERE address = '0x1f98431c8ad98523631ae4a59f267346ea31f984'
    AND topics[SAFE_OFFSET(0)] = '0x9d42cb017eb05bd8944ab536a8b35bc68085931dd5f4356489801453923953f9'
);

-- END;