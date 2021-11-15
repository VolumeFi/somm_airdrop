# Categories of users
---
1. SOMM pairings V2
2. SOMM pairings V3
3. Uniswap V3 LPs
4. Osmosis LPs  

# 1. SOMM Pairings
---
## Address Participation
* Each user that participated in SOMM (with V2 or V3) will receive tokens. The reward is $\dfrac{3,200,000 \text{ SOMM}}{\text{Number of users}}$ for each user.

## Liquidity Amount and Duration
Each user is additionally rewarded based on the amount of liquidity they've provided using SOMM pairings, and for how long they've provided it. The total reward in this category is $2,000,000 \text{ SOMM}$.
<br/><br/>
We will use the value function $ V = D \sqrt{L}$ where $V$ is the value of a position, $L$ is the liquidity amount for that position, and $D$ is the duration of that position. This rewards duration more than amount so that mercenaries don't reap all the rewards.

<br><br/>
### V3 SOMM Liquidity Details
For each user, we calculate $V_p$ for each position they entered using the SOMM app and sum over the positions. The reward for a given user $i$ on V3 is $$ R_{i, V3} = \dfrac{\sum_{p_i} V_{p_i}}{\sum_{\text{j}} \sum_{p_j} V_{p_j} }$$ where $j$ iterates through ALL SOMM V3 users. Note that we also have to aggregate across pools.
* In English: to get the reward for a given user we sum the value of all their positions (across all pools), and divide by the total value for all SOMM users.
<br><br/>
#### Some details on computation:
1. Computing duration
    * Each SOMM V3 user has entered a position (Mint) on some pool using the SOMM app. 
    * In most cases, they burn their position directly on Uniswap V3 (not on the SOMM app)
    * To compute duration of position, we need to draw correspondence between the Uniswap V3 Burns and SOMM V3 Mints.
2. Computing amount
    * There's one **problem** with the method described previously: we are ignoring differences in liquidity amounts for each pool. 
    * What we actually want liquidity to mean is "amount of USD entered into position." In reality, liquidity is dependent on things like ERC20 token decimal values.
    * Basically the question is: how do we compare liquidity amounts across pools? Possible solutions:
        * Ignore this. Just treat liquidity the same across pools. 
        * Before computing liquidity, convert the raw amounts to USD using the current price for each coin.
        * Convert to USD using the price *at the time of the Mint*


### V2 SOMM Liquidity Details
We do something similar for V2. In V2 there are no "positions", just active liquidity. In this case, a user's active liquidity on a pool is given as (step) function of time, $f(t)$. We look at each constant segment (periods with no Mints/Burns) of $f(t)$ and assign it a value in the same way as $V_p$.

#### Some details on computation
* In V2 a (Uniswap V2) Burn doesn't necessarily correspond to a (SOMM) Mint
* We can make a conservative estimate by looking at all Uniswap V2 Burns a user makes on a given pool and subtracting that liquidity from the liquidity added on the SOMM app. 
* We still have the problem of comparing liquidity across pools, though.

### Aggregating V2 and V3
Once we have assigned values to each user (the sum of values for each of their positions) on V2 and V3, we can simply sum the V2 and V3 values. 

The final token reward (for the amount/duration reward category) to user $i$ is given by: 
    $$ R_i = \dfrac{R_{i, V2} + R_{i, V3}}{\sum_j (R_{j, V2} + R_{j, V3})} $$

where $j$ indexes all SOMM users.

