
# Bitcoin Network Tools

A Python wrapper for https://bitnodes.io/api/. 

This library provides tools for analyzing and monitoring Bitcoin network nodes. It supports both authenticated and unauthenticated requests, allowing flexibility based on your usage needs.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Initialization](#initialization)
  - [Example Requests](#example-requests)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)


# Features

- Easy-to-use Python wrapper for the Bitnodes API
- Analyze and monitor Bitcoin network nodes with minimal setup
- Support for authenticated requests using an API key
- Includes node status, latency, leaderboard, and propagation statistics


# Installation 

### Install from PyPI
```bash
pip install bitcoin-network-tools
```

### Install from Source

Clone the repository and install:
```bash
git clone https://github.com/your-repo/bitcoin-network-tools.git
cd bitcoin-network-tools
pip install .
```

## Usage

### Initialization

This library supports both authenticated and unauthenticated requests. To authenticate, set `BITNODES_PUBLIC_KEY` and `BITNODES_PRIVATE_KEY` as environment variables or pass them directly during initialization.

#### Example Initialization

```python
from bitcoin_network_tools.bitnodes_api import BitnodesAPI

# Unauthenticated
bn = BitnodesAPI()

# Authenticated
bn = BitnodesAPI(public_api_key="your_public_key", private_key_path="path_to_private_key")
```

Keys can also be configured after initialization:

```python
In [3]: bn.set_public_api_key("examplekey")
Out[3]: True

In [4]: bn.set_private_key_path("private_key.txt") 
Out[4]: True
```

Note: The private key is used ephemerally and **never** stored.

API keys are available at https://bitnodes.io/api/. 
Snapshot data is retained on Bitnodes servers for up to 60 days.

### API Key Considerations
- Without an API key: Limited to **50 requests per 24 hours**.
- With an API key: Up to **200,000 requests per 24 hours**.

## Example Requests
### Fetch Snapshots
Retrieves a list of snapshots from the server, showing details such as timestamp, total nodes, and block height.


```python
In [3]: bn.get_snapshots(limit=5)
Out[3]: 
{'count': 8612,
 'next': 'https://bitnodes.io/api/v1/snapshots/?limit=5&page=2',
 'previous': None,
 'results': [{'url': 'https://bitnodes.io/api/v1/snapshots/1735849765/',
   'timestamp': 1735849765,
   'total_nodes': 20833,
   'latest_height': 877541},
  {'url': 'https://bitnodes.io/api/v1/snapshots/1735849164/',
   'timestamp': 1735849164,
   'total_nodes': 20816,
   'latest_height': 877541},
  {'url': 'https://bitnodes.io/api/v1/snapshots/1735848574/',
   'timestamp': 1735848574,
   'total_nodes': 20265,
   'latest_height': 877541},
  {'url': 'https://bitnodes.io/api/v1/snapshots/1735847963/',
   'timestamp': 1735847963,
   'total_nodes': 20293,
   'latest_height': 877541},
  {'url': 'https://bitnodes.io/api/v1/snapshots/1735847372/',
   'timestamp': 1735847372,
   'total_nodes': 20298,
   'latest_height': 877538}]}
```

### Retrieve Node Status
Get the status of a specific node:

```python
In [4]: bn.get_node_status(address="31.47.202.112", port=8333)
Out[4]:
{'address': '31.47.202.112',
'status': 'UP',
'data': [70016,
'/Satoshi:27.1.0/',
1734410285,
3081,
877256,
'btc.dohmen.net',
'Gothenburg',
'SE',
57.7065,
11.967,
'Europe/Stockholm',
'AS34385',
'Tripnet AB'],
'mbps': '38.850493'}
```

# Testing

Tests can be run with BITNODES_PUBLIC_KEY and BITNODES_PRIVATE_KEY environment variables set and 

```
pytest
```

# Contributing 

Contributions are welcome! Here's how you can contribute:
1. Report bugs or request features by opening an issue.
2. Fork the repository and create a pull request for code contributions.
3. Expand the documentation or propose new analysis features.

# License 

Apache v2.0
