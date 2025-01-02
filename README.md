
# Bitcoin Network Tools

A Python wrapper for https://bitnodes.io/api/. 

This library provides tools for analyzing and monitoring Bitcoin network nodes. It supports both authenticated and unauthenticated requests, allowing flexibility based on your usage needs.

# Features

- Easy-to-use Python wrapper for the Bitnodes API
- Analyze and monitor Bitcoin network nodes with minimal setup
- Support for authenticated requests using an API key
- Includes node status, latency, leaderboard, and propagation statistics


# Installation 

```
pip install bitcoin-network-tools
```

# Usage    

## Initialization

If BITNODES_PUBLIC_KEY and BITNODES_PRIVATE_KEY are set as environment variables, they will be used for authenticated 
requests by default. 

Keys can also be configured via the constructor:
```
from bitcoin_network_tools.bitnodes_api import BitnodesAPI
bn = BitnodesAPI()
bn = BitnodesAPI(public_api_key="your_public_key", private_key_path="path_to_private_key")
```

The public and private keys can be set with 

```
In [3]: bn.set_public_api_key("examplekey")
Out[3]: True

In [4]: bn.set_private_key_path("private_key.txt") 
Out[4]: True
```

The private key is never stored. 

API keys are available at https://bitnodes.io/api/. 
Snapshot data is retained on Bitnodes servers for up to 60 days.

## Example Requests
### Fetch Snapshots

```
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

```
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

## License 

Apache v2.0
