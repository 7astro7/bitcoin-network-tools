
## Bitcoin Network Tools

A Python wrapper for https://bitnodes.io/api/. 
Credit to this library for making this possible https://github.com/ayeowch/bitnodes.git

Users can work with or without API keys, supporting both authenticated and unauthenticated requests.

###
A library for analyzing and monitoring Bitcoin network nodes

    Provide clear and concise instructions on how to install and use your library.
    Include examples and explanations of the different analysis functions.
    Explain the data requirements and limitations.


## Installation 

## Testing

## Usage    

### Mention API key considerations 
If used without an api key, requests are limited to 50 per 24 hours. API keys are available at 
https://bitnodes.io/api/

BITNODES_PUBLIC_KEY, BITNODES_PRIVATE_KEY

In [1]: from bitcoin_network_tools.bitnodes_api import BitnodesAPI

In [2]: bn = BitnodesAPI() 

## Contributing 

Contributions are welcome. Bug reports, feature requests, ideas for scope expansion, documentation, code contributions are appreciated. 

## License 

Apache v2.0
