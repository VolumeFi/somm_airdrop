BEGIN

CREATE TEMPORARY TABLE all_pairs AS (
  SELECT pair
  FROM uniswap_v3_pairs
--   UNION ALL
);
-- returns all UNI v3 contracts
CREATE TABLE uniswap_contracts AS (
  SELECT pair as contract
  FROM all_pairs
  UNION
  DISTINCT
  SELECT '0x1f98431c8ad98523631ae4a59f267346ea31f984' as contract -- UNI v3 Factory
);