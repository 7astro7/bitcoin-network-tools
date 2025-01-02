import requests
import dns.resolver
import hashlib
import hmac
import time
import os
from urllib.parse import urlencode
import warnings


# include a stack of latest call of each method?
class BitnodesAPI:
    """
    Implementation of the Bitnodes API https://bitnodes.io/api/
    """

    def __init__(self, public_api_key: str = None, private_key_path: str = None):
        """
        Construct Bitnodes API object. Private key can be used via setting
        environment variable BITNODES_PRIVATE_KEY or by calling set_private_key_path.
        In either case, the private key is only used ephemerally and never stored.
        BITNODES_PUBLIC_KEY environment variable will also be used by default.

        Parameters
        ----------
        public_api_key : str
            The public API key for the Bitnodes API. If public_api_key is None and
            BITNODES_PUBLIC_KEY is not set in the environment, the API will be used in
            unauthenticated mode. Set the public API key using the set_public_api_key method.
        path_to_private_key : str
            The path to the private key file for the Bitnodes API. If None, the API will be
            used in unauthenticated mode. Alternatively, the private key can be set using the
            set_private_key_path method.

        """
        self.__base_url = "https://bitnodes.io/api/v1/"
        if "BITNODES_PUBLIC_KEY" in os.environ:
            self.__public_api_key = os.environ["BITNODES_PUBLIC_KEY"]
        else:
            self.__public_api_key = public_api_key
        no_private_key_found = (
            private_key_path is None and "BITNODES_PRIVATE_KEY" not in os.environ
        )
        if self.__public_api_key is None or no_private_key_found:
            warnings.warn(
                "Warning: Bitnodes API is being used in unauthenticated mode.",
                UserWarning,
            )

    def set_public_api_key(self, public_api_key: str) -> bool:
        """
        Set the public API key for the Bitnodes API.

        Parameters
        ----------
        public_api_key : str
            The public API key for the Bitnodes API.

        Returns
        -------
        bool
            True if the public API key was set successfully.
        """
        if not public_api_key or not isinstance(public_api_key, str):
            raise ValueError("Public API key must be a non-empty string.")
        self.__public_api_key = public_api_key
        return True

    def get_public_api_key(self) -> str:
        """
        Get the public API key for the Bitnodes API.

        Returns
        -------
        str
            The public API key for the Bitnodes API.
        """
        return self.__public_api_key

    def set_private_key_path(self, path_to_private_key: str) -> bool:
        """
        Set the path to the private key for the Bitnodes API.

        Parameters
        ----------
        path_to_private_key : str
            The path to the private key file for the Bitnodes API.

        Returns
        -------
        bool
            True if the private key path was set successfully.
        """
        if not os.path.exists(path_to_private_key):
            raise FileNotFoundError("The private key file does not exist.")
        self.__private_key_path = path_to_private_key
        return True

    def _get_private_key(self) -> str:
        """
        Get the private key for the Bitnodes API.

        Returns
        -------
        str
            The private key for the Bitnodes API.
        """
        try:
            if "BITNODES_PRIVATE_KEY" in os.environ:
                return os.environ["BITNODES_PRIVATE_KEY"]
            with open(self.__private_key_path, "r") as f:
                return f.read().strip()
        except Exception as e:
            raise RuntimeError(f"An error occurred while reading the private key: {e}")

    @staticmethod
    def _validate_pagination(page: int = None, limit: int = None) -> None:
        """
        Validate pagination parameters.

        Parameters
        ----------
        page : int
            The page number to retrieve.
        limit : int
            The number of addresses to retrieve.
        """
        if page is not None and not isinstance(page, int):
            raise ValueError("Page must be an integer.")
        if limit is not None:
            if not isinstance(limit, int) or not (1 <= limit <= 100):
                raise ValueError("Limit must be an integer between 1 and 100.")

    @staticmethod
    def _validate_address_port(address: str, port: int) -> None:
        """
        Validate the address and port parameters.

        Parameters
        ----------
        address : str
            The IP address of the node.
        port : int
            The port of the node.
        """
        if not isinstance(address, str) or not address:
            raise ValueError("Address must be a non-empty string.")

        try:
            port = int(port)
        except (ValueError, TypeError):
            raise ValueError(
                "Port must be an integer or a string that can be converted to an integer."
            )
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("Port must be an integer between 1 and 65535.")

    def _add_optional_params(self, og_url_str: str, optional_params: dict) -> str:
        """
        Add optional parameters to the URL string.

        Parameters
        ----------
        og_url_str : str
            The original URL string.
        optional_params : dict
            A dictionary of optional parameters to add to the URL string.

        Returns
        -------
        str
            The URL string with the optional parameters added.
        """
        params = {k: v for k, v in optional_params.items() if v is not None}
        return f"{og_url_str}?{urlencode(params)}" if params else og_url_str

    def get_snapshots(self, page: int = None, limit: int = None) -> dict:
        """
        List all snapshots that are available on the server from the latest to
        oldest snapshot. Snapshots are currently kept on the server for up to 60 days.
        https://bitnodes.io/api/v1/snapshots/

        Parameters
        ----------
        page: int
            The page number to retrieve. If None, default of current page (1) will be used.
        limit: int
            The number of snapshots to retrieve. If None, default of 10 will be used. Max 100.

        Returns
        -------
        dict
            A dictionary containing the following keys: count, next, previous, results.
            Results is a list of dictionaries of the form
            {
            "url": "https://bitnodes.io/api/v1/snapshots/1656292357/",
            "timestamp": 1656292357,
            "total_nodes": 14980,
            "latest_height": 742491
            },...

        Examples
        --------
        In [3]: bn.get_snapshots(limit=5)

        Out[3]:
        {'count': 8614,
        'next': 'https://bitnodes.io/api/v1/snapshots/?limit=5&page=2',
        'previous': None,
        'results': [{'url': 'https://bitnodes.io/api/v1/snapshots/1735685327/',
        'timestamp': 1735685327,
        'total_nodes': 20773,
        'latest_height': 877253},
        {'url': 'https://bitnodes.io/api/v1/snapshots/1735684735/',
        'timestamp': 1735684735,
        'total_nodes': 20772,
        'latest_height': 877253},
        {'url': 'https://bitnodes.io/api/v1/snapshots/1735684143/',
        'timestamp': 1735684143,
        'total_nodes': 20464,
        'latest_height': 877252},
        {'url': 'https://bitnodes.io/api/v1/snapshots/1735683542/',
        'timestamp': 1735683542,
        'total_nodes': 20781,
        'latest_height': 877252},
        {'url': 'https://bitnodes.io/api/v1/snapshots/1735682930/',
        'timestamp': 1735682930,
        'total_nodes': 20214,
        'latest_height': 877249}]}
        """
        self._validate_pagination(page, limit)
        url = f"{self.__base_url}snapshots/"
        optional_params = {"page": page, "limit": limit}
        url = self._add_optional_params(url, optional_params)

        headers = None
        if self.__public_api_key:
            nonce = str(int(time.time() * 1_000_000))
            message = f"{self.get_public_api_key()}:{nonce}:{url}".encode()
            sig = hmac.new(
                self._get_private_key().encode(), message, hashlib.sha256
            ).hexdigest()
            headers = {
                "pubkey": self.get_public_api_key(),
                "nonce": nonce,
                "sig": f"HMAC-SHA256:{sig}",
            }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_nodes_list(self, timestamp: str = "latest", field: str = None) -> dict:
        """
        Retrieve the list of reachable nodes from a snapshot.

        Parameters
        ----------
        timestamp : str
            The timestamp of the snapshot to retrieve. The default is "latest".
        field : str
            Specify field=coordinates to get the list of unique latitude and longitude
            pairs or field=user_agents to get the list of unique user agents instead of
            the full information listed below. If None, the full information is returned.

        Returns
        -------
        dict
            A dictionary of the form
            timestamp: int (the timestamp of the snapshot)
            total_nodes: int (the total number of nodes as of the snapshot)
            latest_height: the block height of the most recent block in the blockchain
                at the time the snapshot was taken.
            If no field is specified, the dictionary will also contain the following key:
            nodes: list (a list of dictionaries, each containing information about a node):
                    Protocol version
                    User agent
                    Connected since
                    Services
                    Height
                    Hostname
                    City
                    Country code
                    Latitude
                    Longitude
                    Timezone
                    ASN
                    Organization name

        Examples
        --------
        In [6]: bn.get_nodes_list(timestamp="1735684735", field="user_agents")

        Out[6]:
        {'timestamp': 1735684735,
        'total_nodes': 20772,
        'latest_height': 877253,
        'user_agents': ['/Satoshi:27.1.0/',
        '/Satoshi:27.0.0/',
        '/Satoshi:28.0.0/',
        '/Satoshi:24.1.0/',
        '/Satoshi:26.0.0/',
        '/Satoshi:23.0.0/',
        '/Satoshi:27.0.0(RoninDojo 2.1.4)/',
        '/Satoshi:25.1.0/',
        ...
        '/Bitcoin ABC:0.15.1(EB8.0)/',
        '/Satoshi:28.0.0(barneyricket.com)/',
        '/Satoshi:27.0.0(Samourai Dojo 1.24.1)/',
        '/Satoshi:21.2.0/Knots:20210629/',
        '/Satoshi:25.1.0(@devinbileck)/']}
        """
        if field is not None:
            if field.lower() not in [
                "coordinates",
                "user_agents",
            ]:
                raise ValueError("Field must be either 'coordinates' or 'user_agents'.")
        if timestamp != "latest" and not timestamp.isdigit():
            raise ValueError(
                "Timestamp must be a string representation of integer or 'latest'."
            )
        url = f"{self.__base_url}snapshots/{timestamp}/"
        if timestamp != "latest" or field is not None:
            optimal_params = {}
            if timestamp != "latest":
                optimal_params["timestamp"] = timestamp
            if field is not None:
                optimal_params["field"] = field
            url = self._add_optional_params(url, optimal_params)

        headers = None
        if self.__public_api_key:
            nonce = str(int(time.time() * 1_000_000))
            message = f"{self.get_public_api_key()}:{nonce}:{url}".encode()
            sig = hmac.new(
                self._get_private_key().encode(), message, hashlib.sha256
            ).hexdigest()
            headers = {
                "pubkey": self.get_public_api_key(),
                "nonce": nonce,
                "sig": f"HMAC-SHA256:{sig}",
            }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_address_list(
        self, page: int = None, limit: int = None, q: str = None
    ) -> dict:
        """
        List all IPv4/IPv6/.onion addresses observed by the Bitnodes crawler in
        the Bitcoin peer-to-peer network.

        Parameters
        ----------
        page : int
            The page number to retrieve. If None, default of current page (1) will be used.
        limit : int
            The number of addresses to retrieve. If None, default of 10 will be used. Max 100.
        q : str
            A pattern used to filter addresses. Supports matching with regular expression syntax
            for beginning filtering.
            Examples:
            - `^fc`: Matches addresses starting with "fc".

        Returns
        -------
        dict
            A dictionary containing the following keys: count, next, previous, results.
            Results is a list of dictionaries of the form
            [{
            "address": "2a01:e34:ec76:c9d0:2520:5f4d:852d:3aa2",
            "port": 8333
            },...

        Examples
        --------
        In [13]: bn.get_address_list(q=".onion")

        Out[13]:
        {'count': 113000,
        'next': 'https://bitnodes.io/api/v1/addresses/?page=2&q=.onion',
        'previous': None,
        'results': [{'address': 'romjsh6fjm643qkjft52w4lfxacsltbcrav2hd5yt23vkhjl5o452mad.onion',
        'port': 8333},
        {'address': 'z7re2iwdl4w6i46aax53qesna7xug7aa6yg23ox6koyxsskxmf3io6ad.onion',
        'port': 8333},
        {'address': '5j7z5fovfahxe3gwqt2lthhyxvotcveopld375l2k4rvqccc36lexbad.onion',
        'port': 8333},
        {'address': 'ygw7oagmzz4bga6tc2w3q47zv7lnzmxe5yn7z4bjxnlrvyx4zg4he3ad.onion',
        'port': 8333},
        {'address': 'vjegtb7ve6dj26xqrbl6txfw6rlurcrit3a2encqkvptt6l47cehfpid.onion',
        'port': 8333},
        {'address': 'tewefnepsin4yniz2dcmxjeetvelr74bwveeixo7jglyngri7tr2v2qd.onion',
        'port': 8333},
        {'address': 'ouq3uttpj6pvqphvvh6yrbkv3xidph4na3tpsrgi4zx2kbon4na6orqd.onion',
        'port': 8333},
        {'address': 'rglv2r4zbk2dp3fvrjjagf4bbvqe2bmakozgb3vrwo4hs7h25g6ndqyd.onion',
        'port': 8333},
        {'address': '2d6b2zk7w3ifi76qxgolvuhxmzswlmttq6i5d7vg6x5zqdphkueva2id.onion',
        'port': 8333},
        {'address': '4tywk7f5foha6g6inkocmpymkrxzd73m2cprlytdxrbnh3dd4nz3j3ad.onion',
        'port': 8333}]}
        """
        self._validate_pagination(page, limit)
        if q is not None and not isinstance(q, str):
            raise ValueError("q must be a string representing a single search term.")
        url = f"{self.__base_url}addresses/"
        optional_params = {"page": page, "limit": limit, "q": q}
        url = self._add_optional_params(url, optional_params)

        headers = None
        if self.__public_api_key:
            nonce = str(int(time.time() * 1_000_000))
            message = f"{self.get_public_api_key()}:{nonce}:{url}".encode()
            sig = hmac.new(
                self._get_private_key().encode(), message, hashlib.sha256
            ).hexdigest()
            headers = {
                "pubkey": self.get_public_api_key(),
                "nonce": nonce,
                "sig": f"HMAC-SHA256:{sig}",
            }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_node_status(self, address: str, port: int = 8333):
        """
        Get status for an activated node. New node must be activated separately, i.e.
        from https://bitnodes.io/nodes/<ADDRESS>-<PORT>/, before it can be accessed from
        this endpoint.

        Parameters
        ----------
        address : str
            The IP address of the node.
        port : int, optional
            The port of the node. Default is 8333.

        Returns
        -------
        dict
            A dictionary containing the status of the node:
                status: str
                protocol_version: int
                user_agent: str
                services: str
                height: int
                hostname: str
                city: str
                country_code: str
                latitude: float
                longitude: float
                timezone: str
                asn: int
                organization: str
            Plus address and status.

        Examples
        --------
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

        """
        self._validate_address_port(address, port)
        url = f"{self.__base_url}nodes/{address}-{port}/"

        headers = None
        if self.__public_api_key:
            nonce = str(int(time.time() * 1_000_000))
            message = f"{self.get_public_api_key()}:{nonce}:{url}".encode()
            sig = hmac.new(
                self._get_private_key().encode(), message, hashlib.sha256
            ).hexdigest()
            headers = {
                "pubkey": self.get_public_api_key(),
                "nonce": nonce,
                "sig": f"HMAC-SHA256:{sig}",
            }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_node_latency(self, address: str, port: int = 8333):
        """
        Get daily, weekly and monthly latency data for an activated node. New node must be
        activated separately, i.e. from https://bitnodes.io/nodes/<ADDRESS>-<PORT>/, before
        it can be accessed from this endpoint.
        t - Timestamp of this data point.
        v - Average latency of this node in milliseconds;
        v = -1 (node is unreachable),
        v = 0 (node is reachable but no latency data is available).

        Parameters
        ----------
        address : str
            The IP address of the node.
        port : int
            The port of the node. Default is 8333.

        Returns
        -------
        dict
            A dictionary containing the latency data for the node:
                daily: list of {timestamp: int, latency: int}
                weekly: list of {timestamp: int, latency: int}
                monthly: list of {timestamp: int, latency: int}

        Examples
        --------
        In [5]: bn.get_node_latency(address="31.47.202.112", port=8333)

        Out[5]:
        {'daily_latency': [{'t': 1735602300, 'v': 23},
        {'t': 1735603200, 'v': 23},
        {'t': 1735604100, 'v': 23},
        {'t': 1735605000, 'v': 23},
        {'t': 1735687800, 'v': 23},
        ...
        {'t': 1735688700, 'v': 23}],
        'weekly_latency': [{'t': 1735081200, 'v': 23},
        {'t': 1735084800, 'v': 23},
        {'t': 1735088400, 'v': 23},
        {'t': 1735678800, 'v': 23},
        {'t': 1735682400, 'v': 23},
        ...
        {'t': 1735686000, 'v': 23}],
        'monthly_latency': [{'t': 1704067200, 'v': 24},
        {'t': 1704153600, 'v': 24},
        {'t': 1704240000, 'v': 23},
        {'t': 1735516800, 'v': 23},
        ...
        {'t': 1735603200, 'v': 23}]}
        """
        self._validate_address_port(address, port)
        url = f"{self.__base_url}nodes/{address}-{port}/latency/"

        headers = None
        if self.__public_api_key:
            nonce = str(int(time.time() * 1_000_000))
            message = f"{self.get_public_api_key()}:{nonce}:{url}".encode()
            sig = hmac.new(
                self._get_private_key().encode(), message, hashlib.sha256
            ).hexdigest()
            headers = {
                "pubkey": self.get_public_api_key(),
                "nonce": nonce,
                "sig": f"HMAC-SHA256:{sig}",
            }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_leaderboard(self, page: int = None, limit: int = None) -> dict:
        """
        List all activated nodes according to their Peer Index (PIX) in descending order.

        The Bitnodes Peer Index (PIX) is a numerical value that measures its desirability
        to the Bitcoin network. See https://bitnodes.io/nodes/leaderboard/#peer-index for
        more information.

        Parameters
        ----------
        page : int
            The page number to retrieve. If None, default of current page (1) will be used.
        limit : int
            The number of addresses to retrieve. If None, default of 10 will be used. Max 100.

        Returns
        -------
        dict
            A dictionary containing the leaderboard data with the following
            keys: count, next,  previous, results. Results is a list of dictionaries
            of the form
            "node": "37.191.249.99:8333",
            "vi": "1.0000",
            "si": "1.0000",
            "hi": "1.0000",
            "ai": "1.0000",
            "pi": "1.0000",
            "dli": "1.0000",
            "dui": "1.0000",
            "wli": "1.0000",
            "wui": "1.0000",
            "mli": "1.0000",
            "mui": "0.9856",
            "nsi": "0.9000",
            "ni": "0.0058",
            "bi": "1.0000",
            "peer_index": "9.2082",
            "rank": 1

        Examples
        --------
        In [4]: bn.get_leaderboard(limit=5)

        Out[4]:
        {'count': 13163,
        'next': 'https://bitnodes.io/api/v1/nodes/leaderboard/?limit=5&page=2',
        'previous': None,
        'results': [{'node': '[2001:1bc0:c1::2000]:8333',
        'vi': '1.0000',
        'si': '0.9907',
        'hi': '1.0000',
        'ai': '0.9357',
        'pi': '1.0000',
        'dli': '1.0000',
        'dui': '1.0000',
        'wli': '1.0000',
        'wui': '1.0000',
        'mli': '1.0000',
        'mui': '1.0000',
        'nsi': '0.9769',
        'ni': '0.9916',
        'bi': '1.0000',
        'peer_index': '9.9249',
        'rank': 1},
        {'node': '31.47.202.112:8333',
        'vi': '1.0000',
        'si': '0.9907',
        'hi': '1.0000',
        'ai': '0.9801',
        'pi': '1.0000',
        'dli': '1.0000',
        'dui': '1.0000',
        'wli': '1.0000',
        'wui': '1.0000',
        'mli': '1.0000',
        'mui': '1.0000',
        'nsi': '0.9503',
        'ni': '0.9324',
        'bi': '1.0000',
        'peer_index': '9.8954',
        'rank': 2},
        {'node': '198.154.93.110:8333',
        ...
        'rank': 5}]}
        """
        self._validate_pagination(page, limit)
        url = f"{self.__base_url}nodes/leaderboard/"
        optional_params = {"page": page, "limit": limit}
        url = self._add_optional_params(url, optional_params)

        headers = None
        if self.__public_api_key:
            nonce = str(int(time.time() * 1_000_000))
            message = f"{self.get_public_api_key()}:{nonce}:{url}".encode()
            sig = hmac.new(
                self._get_private_key().encode(), message, hashlib.sha256
            ).hexdigest()
            headers = {
                "pubkey": self.get_public_api_key(),
                "nonce": nonce,
                "sig": f"HMAC-SHA256:{sig}",
            }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_node_ranking(self, address: str, port: int = 8333) -> dict:
        """
        Get ranking and associated Peer Index (PIX) data for an activated node. New node must be
        activated separately, i.e. from https://bitnodes.io/nodes/<ADDRESS>-<PORT>/, before it
        can be accessed from this endpoint. See https://bitnodes.io/nodes/leaderboard/#peer-index
        for more information.

        Parameters
        ----------
        address : str
            The IP address of the node.
        port : int
            The port of the node. Default is 8333.

        Returns
        -------
        dict
            A dictionary of the form
            {
                "node": "128.65.194.136:8333",
                "vi": "1.0000",
                "si": "1.0000",
                "hi": "1.0000",
                "ai": "0.0000",
                "pi": "1.0000",
                "dli": "1.0000",
                "dui": "0.9588",
                "wli": "1.0000",
                "wui": "0.9645",
                "mli": "1.0000",
                "mui": "0.9873",
                "nsi": "0.5000",
                "ni": "0.0013",
                "bi": "0.0000",
                "peer_index": "7.4371",
                "rank": 3619
            }

        Examples
        --------
        In [6]: bn.get_node_ranking(address="31.47.202.112", port=8333)

        Out[6]:
        {'node': '31.47.202.112:8333',
        'vi': '1.0000',
        'si': '0.9907',
        'hi': '1.0000',
        'ai': '0.9801',
        'pi': '1.0000',
        'dli': '1.0000',
        'dui': '1.0000',
        'wli': '1.0000',
        'wui': '1.0000',
        'mli': '1.0000',
        'mui': '1.0000',
        'nsi': '0.9503',
        'ni': '0.9324',
        'bi': '1.0000',
        'peer_index': '9.8954',
        'rank': 2}
        """
        self._validate_address_port(address, port)
        url = f"{self.__base_url}nodes/leaderboard/{address}-{port}/"

        headers = None
        if self.__public_api_key:
            nonce = str(int(time.time() * 1_000_000))
            message = f"{self.get_public_api_key()}:{nonce}:{url}".encode()
            sig = hmac.new(
                self._get_private_key().encode(), message, hashlib.sha256
            ).hexdigest()
            headers = {
                "pubkey": self.get_public_api_key(),
                "nonce": nonce,
                "sig": f"HMAC-SHA256:{sig}",
            }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_data_propagation_list(self, page: int = None, limit: int = None) -> dict:
        """
        List up to 100,000 recent inventory hashes (latest to oldest) with propagation stats
        available through data propagation endpoint. Bitnodes samples at most only 1000
        transaction invs per block.

        Parameters
        ----------
        page : int
            The page number to retrieve. If None, default of current page (1) will be used.
        limit : int
            The number of addresses to retrieve. If None, default of 10 will be used. Max 100.

        Returns
        -------
        dict
            A dictionary containing the following keys:
            count, next, previous, results. Results is a list of dictionaries of the form
            [{
                "inv_hash": "51b4cc62ca39f7f7d567b8288a5d73aa29e4e059282077b4fe06eb16db882f37"
            },...]

        Examples
        --------
        In [4]: bn.get_data_propagation_list(limit=5)

        Out[4]:
        {'count': 100000,
        'next': 'https://bitnodes.io/api/v1/inv/?limit=5&page=2',
        'previous': None,
        'results': [{'inv_hash': 'bd45b4835c82d68fd4c793a2c11c481f22ebe2011838a5a5b1b2a192ca5be6a7'},
        {'inv_hash': '60dc421ea3961a3bd11398afcd18f5436d951904f2cd1a33c7f98e831d96dc1e'},
        {'inv_hash': 'c8f932d15398f1c49a51021d3deb7141d48919676d9db259998556a973c2d0f0'},
        {'inv_hash': '6fb3287162ce77e35c3ddf41adab646d62984e2ae29a3652c3045920812e50a3'},
        {'inv_hash': '4926e3520374d0e1c71df7998f3041811f1c063783befeb89f6bf560b8492205'}]}
        """
        self._validate_pagination(page, limit)
        url = f"{self.__base_url}inv/"
        optional_params = {"page": page, "limit": limit}
        url = self._add_optional_params(url, optional_params)

        headers = None
        if self.__public_api_key:
            nonce = str(int(time.time() * 1_000_000))
            message = f"{self.get_public_api_key()}:{nonce}:{url}".encode()
            sig = hmac.new(
                self._get_private_key().encode(), message, hashlib.sha256
            ).hexdigest()
            headers = {
                "pubkey": self.get_public_api_key(),
                "nonce": nonce,
                "sig": f"HMAC-SHA256:{sig}",
            }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_data_propagation(self, inv_hash: str) -> dict:
        """
        Get inv propagation stats in milliseconds for a block or transaction broadcasted over
        8 hours ago. Stats are calculated based on the inv arrival times (UNIX time in milliseconds)
        from the first 1000 nodes.

        Parameters
        ----------
        inv_hash : str
            The inventory hash of the block or transaction.

        Returns
        -------
        dict
            A dictionary containing inv_hash and stats.
            Values in stats represent the following information:

            head - Arrival times for the first 10 (or 1000 for newer inv) nodes in
                a list of ["<ADDRESS>:<PORT>", <TIMESTAMP>].
            min - Delta for earliest arrival time. Value can be 0 if the delta is
                less than 1 millisecond.
            max - Delta for latest arrival time.
            mean - Average of deltas.
            std - Standard deviation of deltas.
            50% - 50th percentile of deltas.
            90% - 90th percentile of deltas.

        Examples
        --------
        In [5]: bn.get_data_propagation(inv_hash="51b4cc62ca39f7f7d567b8288a5d73aa29e4e059282077b4fe06eb16db882f37")

        Out[5]:
        {'inv_hash': '51b4cc62ca39f7f7d567b8288a5d73aa29e4e059282077b4fe06eb16db882f37',
        'stats': {'mean': 8836,
        'std': 4040,
        'min': 145,
        '50%': 8149,
        '90%': 17970,
        'max': 20010,
        'head': [['217.20.131.64:8333', 1695996990986],
        ['94.177.8.76:8333', 1695996991131],
        ['167.71.51.223:8333', 1695996991202],
        ['81.183.51.15:8333', 1695996991223],
        ['35.195.234.115:8333', 1695996991227],
        ['57.128.96.115:8333', 1695996991239],
        ['5.199.168.101:39388', 1695996991259],
        ['46.4.41.117:8334', 1695996991260],
        ['54.146.65.218:8333', 1695996991285],
        ['217.183.93.159:8333', 1695996991291]]}}
        """
        if not inv_hash:
            raise ValueError("Inventory hash must be a non-empty string.")
        url = f"{self.__base_url}inv/{inv_hash}/"

        headers = None
        if self.__public_api_key:
            nonce = str(int(time.time() * 1_000_000))
            message = f"{self.get_public_api_key()}:{nonce}:{url}".encode()
            sig = hmac.new(
                self._get_private_key().encode(), message, hashlib.sha256
            ).hexdigest()
            headers = {
                "pubkey": self.get_public_api_key(),
                "nonce": nonce,
                "sig": f"HMAC-SHA256:{sig}",
            }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_dns_seeder(
        self,
        record: str = "AAAA",
        prefix: str = None,
        resolver_timeout: int = 10,
        resolver_lifetime: int = 10,
    ) -> list:
        """
        Get a list of reachable nodes to bootstrap your Bitcoin client
        connection to the Bitcoin network. The DNS records are generated using seeder.py at
        https://github.com/ayeowch/bitnodes/blob/master/seeder.py.

        Parameters
        ----------
        record : str, case-insensitive
            The DNS record to retrieve. Options are:
            - "a" (IPv4): Retrieves IPv4 addresses.
            - "aaaa" (IPv6): Retrieves IPv6 addresses.
            - "txt" (Onion): Retrieves .onion addresses for Tor.
        prefix : str, optional
            A prefix in the format x[hex], used to filter nodes based on specific services.
            The hex value corresponds to the service bits of the nodes you want to query.
            For example:
            - "x409" returns nodes with services set to 1033 (hex 1033 = 0x409).
            This includes:
            - NODE_NETWORK (1)
            - NODE_WITNESS (8)
            - NODE_NETWORK_LIMITED (1024).
            If not provided, all nodes are returned without filtering.
        resolver_timeout: int
            The maximum amount of time (in seconds) that a single DNS query will wait for a response.
            If the query exceeds this duration, it will time out and raise a `LifetimeTimeout` error.
            Default is 10 seconds.

        resolver_lifetime: int
            The total duration (in seconds) allowed for the DNS resolver to complete all retries
            and queries for the given domain. This includes multiple attempts if the resolver retries
            after a timeout or other transient errors. If the lifetime is exceeded, the query will fail
            with a `LifetimeTimeout` error.
            Default is 10 seconds.

        Returns
        -------
        list
            A list of resolved records. The content of the list depends on the `record` type:
            - For "a" (IPv4): A list of IPv4 addresses as strings.
            - For "aaaa" (IPv6): A list of IPv6 addresses as strings.
            - For "txt" (Onion): A list of `.onion` addresses as strings, extracted from the TXT records.
            Example outputs:
                - ["192.0.2.1", "198.51.100.2"] for "a".
                - ["2001:db8::1", "2001:db8::2"] for "aaaa".
                - ["abcd1234.onion", "efgh5678.onion"] for "txt".


        Examples
        --------
        In [4]: bn.get_dns_seeder(record="txt", prefix="x409")

        Out[4]:
        ['b6occtielfswjoizrl6bxki7ecpl4zijqegd5dzk5e66s5fduyhbrtyd.onion',
        'bznwam37uhpeuodct2ppxkoe4h6xs37vjb64cpb22aiafh75vabqujqd.onion',
        'dgc6bwlf4ynzcm7xpfpu4wiefvlc7676fk4jkio6jnuiawktyruhdbyd.onion',
        'eqpprgcdrjfea7lacdplgj6y5uon6psekszqla4byrtjhlhjcgfaibyd.onion',
        'eu4dj74s2yqakg7ggk4depqe6nmqj7sse6nvhoo4etf25mx35aifgryd.onion',
        ...
        '6hanskegwge7hvpqlf7itcwqgk6t3xinldyyhp2xvnfvg4gjwwtw3iqd.onion']

        """
        if record.lower() not in ["a", "aaaa", "txt"]:
            raise ValueError("Record must be one of 'a', 'aaaa', 'txt'.")
        domain = f"{prefix}.seed.bitnodes.io" if prefix else "seed.bitnodes.io"
        resolver = dns.resolver.Resolver()

        if not isinstance(resolver_timeout, int) or resolver_timeout < 1:
            raise ValueError("Resolver timeout must be at least 1 second.")
        if not isinstance(resolver_lifetime, int) or resolver_lifetime < 1:
            raise ValueError("Resolver lifetime must be at least 1 second.")
        resolver.timeout = resolver_timeout
        resolver.lifetime = resolver_lifetime

        try:
            if record.lower() == "txt":

                txt_records = resolver.resolve(domain, "TXT")
                onion_addresses = [
                    txt_string.decode()
                    for txt_record in txt_records
                    for txt_string in txt_record.strings
                    if ".onion" in txt_string.decode()
                ]
                return onion_addresses

            elif record.lower() == "a":
                a_records = resolver.resolve(domain, "A")
                return [str(a_record) for a_record in a_records]

            elif record.lower() == "aaaa":
                aaaa_records = resolver.resolve(domain, "AAAA")
                return [str(aaaa_record) for aaaa_record in aaaa_records]

        except dns.exception.DNSException as e:
            raise RuntimeError(f"An error occurred while querying DNS: {e}")
