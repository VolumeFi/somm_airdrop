# VolumeFi/somm_airdrop <!-- omit in toc -->


![Python 3.8+] [![License: MIT]](https://github.com/VolumeFi/somm_airdrop/blob/main/LICENSE)

[Python 3.8+]: https://img.shields.io/badge/python-3.8+-blue.svg
[License: MIT]: https://img.shields.io/badge/License-MIT-yellow.svg 


This repository contains code to generate the Sommelier token distribution for the airdrop proposed in the [Sips-002 community proposal](https://community.sommelier.finance/t/sips-002-a-proposal-for-a-sommelier-token-airdrop-of-somm-to-select-liquidity-providers/272). The Sips-002 proposal implementation is described in [another community update](https://community.sommelier.finance/t/implementation-and-analysis-of-the-sommelier-sips-002-proposal/402).


---

# Token Distribution

##### Total distribution: 14,600,000

| Group |  Reward totals |
| :---: |  :---:   |
| Osmosis | 3.4M |
| Sommelier App | 5.2M | 
| Uniswap v3 | 6M |

| Group |  Reward splits |
| :---: |  :---:   |
| Osmosis | 23.3 % |
| Sommelier App |35.6 % |
| Uniswap v3 | 41.1 % |

To reproduce the these token allocations, see:

- [tokenDistributionReport.ipynb][tokenDistribution notebook link]: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)][tokenDistribution Colab link] 

- [airdrop.ipynb][airdrop notebook link]: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)][airdrop Colab link]

[tokenDistribution notebook link]: https://github.com/VolumeFi/somm_airdrop/blob/main/tokenDistributionReport.ipynb 

[tokenDistribution Colab link]: https://colab.research.google.com/github/VolumeFi/somm_airdrop/blob/main/tokenDistributionReport.ipynb

[airdrop notebook link]: https://github.com/VolumeFi/somm_airdrop/blob/main/airdrop.ipynb

[airdrop Colab link]: https://colab.research.google.com/github/VolumeFi/somm_airdrop/blob/main/airdrop.ipynb

---

# Corresponding Governance Proposal 

Implementation And Analysis Of The Sommelier SIPS-002 Proposal: https://volume.finance/blog/Implementation-and-Analysis-of-the-Sommelier-SIPS-002-Proposal


# Reproducing the retroactive queries from Google BigQuery

Data for this token distribution is extracted from Google BigQuery's [bigquery-public-data.crypto_ethereum](https://console.cloud.google.com/bigquery?p=bigquery-public-data&d=crypto_ethereum&page=dataset) table.

In order to run our retroactive queries to get Uniswap v2 and v3 mints and burns ([found here]()), you'll need to start the ["Run All Queries (V2, V3, SOMM)" workflow](https://github.com/VolumeFi/somm_airdrop/actions/workflows/all-queries.yaml) from the actions tab:
1. Create a Google Cloud project [here](https://cloud.google.com/) 
1. Find your Project ID in the Google Cloud console [here](https://console.cloud.google.com/). See [Locating the Project ID (article)](https://support.google.com/googleapi/answer/7014113?hl=en) if you're having trouble.
1. Fork this repository.
1. Add the folowing secrets under Settings > Secrets containing 
    - `GCP_PROJECT_ID`: Your project ID from the GCP dashboard.
    - `GCP_SA_KEY`: The base64 encoded JSON key of a service account
1. Go to the actions tab of your fork and run the workflow (roughly ~10 minutes to complete)

