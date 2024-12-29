import requests
import dns.resolver
import hashlib
import hmac
import time
import urllib.request
import urllib.error
import os
import json


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
        if public_api_key is None or no_private_key_found:
            print("Warning: Bitnodes API is being used in unauthenticated mode.")

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

    def _set_private_key_path(self, path_to_private_key: str) -> bool:
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
                return f.read()
        except Exception as e:
            raise RuntimeError(f"An error occurred while reading the private key: {e}")

    def _generate_auth_headers(self, uri: str) -> dict:
        """
        Generate the authentication headers using the public key and a 
        dynamically fetched private key.

        Parameters:
            uri (str): The full API endpoint URI.

        Returns:
            dict: The response from the API as a dictionary.
        """
        # Generate nonce (UNIX time in microseconds)
        nonce = str(int(time.time() * 1_000_000))
        message = f"{self.get_public_api_key()}:{nonce}:{uri}".encode()
        sig = hmac.new(
            self._get_private_key().encode(), message, hashlib.sha256
        ).hexdigest()
        return {
            "pubkey": self.get_public_api_key(),
            "nonce": nonce,
            "sig": f"HMAC_SHA256:{sig}",
        }


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
        if optional_params:
            og_url_str += "?"
            for key, value in optional_params.items():
                if value is not None:
                    og_url_str += f"{key}={value}&"
            if og_url_str[-1] == "&":
                og_url_str = og_url_str[:-1]
        return og_url_str

    def get_snapshots(self, page: int = None, limit: int = None):
        """
        List all snapshots that are available on the server from the latest to
        oldest snapshot. Snapshots are currently kept on the server for up to 60 days.

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

        """
        self._validate_pagination(page, limit)
        url = f"{self.__base_url}snapshots/"
        optional_params = {"page": page, "limit": limit}
        url = self._add_optional_params(url, optional_params)
        response = requests.get(url)
        return response.json()

    def get_nodes_list(self, timestamp: str = "latest", field: str = None) -> dict:
        """
        Retrieve the list of nodes from a snapshot.

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
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_address_list(
        self, page: int = None, limit: int = None, q: list[str] = None
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
        q : list
            Search addresses.

        Returns
        -------
        dict
            A dictionary containing the following keys: count, next, previous, results.
            Results is a list of dictionaries of the form
            [{
            "address": "2a01:e34:ec76:c9d0:2520:5f4d:852d:3aa2",
            "port": 8333
            },...
        """
        self._validate_pagination(page, limit)
        if q is not None:
            if not isinstance(q, list) or not all(isinstance(i, str) for i in q):
                raise ValueError("q must be a list of strings.")
            q = ",".join(q)
        url = f"{self.__base_url}addreses/"
        optional_params = {"page": page, "limit": limit, "q": q}
        url = self._add_optional_params(url, optional_params)
        response = requests.get(url)
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
        """
        self._validate_address_port(address, port)
        url = f"{self.__base_url}nodes/{address}-{port}/"
        response = requests.get(url)
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
            Each list
        """
        self._validate_address_port(address, port)
        url = f"{self.__base_url}nodes/{address}-{port}/latency/"
        response = requests.get(url)
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
        """
        self._validate_pagination(page, limit)
        url = f"{self.__base_url}leaderboard/"
        optional_params = {"page": page, "limit": limit}
        url = self._add_optional_params(url, optional_params)
        response = requests.get(url)
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
        """
        self._validate_address_port(address, port)
        url = f"{self.__base_url}nodes/leaderboard/{address}-{port}/"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_data_propagation_list(self, page: int = None, limit: int = None) -> dict:
        """
        List up to 100,000 recent inventory hashes (latest to oldest) with propagation stats
        available through data propagation endpoint. Bitnodes samples at most only
        1000 transaction invs per block.

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
        """
        self._validate_pagination(page, limit)
        url = f"{self.__base_url}data-propagation/"
        optional_params = {"page": page, "limit": limit}
        url = self._add_optional_params(url, optional_params)
        response = requests.get(url)
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
        """
        if not inv_hash:
            raise ValueError("Inventory hash must be a non-empty string.")
        url = f"{self.__base_url}inv/{inv_hash}/"
        response = requests.get(url)
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
        """
        if record.lower() not in ["a", "aaaa", "txt"]:
            raise ValueError("Record must be one of 'a', 'aaaa', 'txt'.")
        domain = f"{prefix}.seed.bitnodes.io" if prefix else "seed.bitnodes.io"
        resolver = dns.resolver.Resolver()
        try:
            if record.lower() == "txt":
                if not isinstance(resolver_timeout, int) or resolver_timeout < 1:
                    raise ValueError("Resolver timeout must be at least 1 second.")
                if not isinstance(resolver_lifetime, int) or resolver_lifetime < 1:
                    raise ValueError("Resolver lifetime must be at least 1 second.")
                resolver.timeout = resolver_timeout
                resolver.lifetime = resolver_lifetime

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


if __name__ == "__main__":
    b = BitnodesAPI()
    breakpoint()
