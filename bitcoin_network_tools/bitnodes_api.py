import requests
import socket


# include a stack of latest call of each method?
class BitnodesAPI:
    """
    Implementation of the Bitnodes API https://bitnodes.io/api/
    """

    def __init__(self):
        self.__base_url = "https://bitnodes.io/api/v1/"

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

    def get_snapshots(
        self, page: int = None, limit: int = None
    ):
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
        url = f"{self.__base_url}snapshots/"
        optional_params = {"page": page, "limit": limit}
        url = self._add_optional_params(url, optional_params)
        response = requests.get(url)
        return response.json()

    def get_nodes_list(
        self, timestamp: str = "latest", field: str = None
    ) -> dict:
        """
        Retrieve the list of nodes from a snapshot.

        Parameters
        ----------
        timestamp : str
            The timestamp of the snapshot to retrieve. The default is "latest".
        field : str
            Specify field=coordinates to get the list of unique latitude and longitude
            pairs or field=user_agents to get the list of unique user agents instead of
            the full information listed below.

        Returns
        -------
        dict
            A dictionary of the form
            timestamp: int (the timestamp of the snapshot)
            total_nodes: int (the total number of nodes as of the snapshot)
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
        # create assertion for timestamp
        if field.lower() not in ["coordinates", "user_agents", None]:
            raise ValueError("Field must be either 'coordinates' or 'user_agents'.")
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

    def get_addresses(self, page: int = None, limit: int = None, q: list = None):
        """

        Parameters
        ----------
        page : int
            The page number to retrieve. If None, default of current page (1) will be used.
        limit : int
            The number of addresses to retrieve. If None, default of 10 will be used. Max 100.
        q : list
            Search addresses.
        """
        if page is not None and not isinstance(page, int):
            raise ValueError("Page must be an integer.")
        if limit is not None and not (1 <= limit <= 100):
            raise ValueError("Limit must be an integer between 1 and 100.")
        if q is not None:
            # check if q is iterable
            # also, may need to join q into a string
            pass
        url = f"{self.__base_url}addreses/"
        optional_params = {"page": page, "limit": limit, "q": q}
        url = self._add_optional_params(url, optional_params)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    # should probably make 8333 the default port
    def get_node_status(self, address: str, port: int):
        """
        Get status for an activated node. New node must be activated separately, i.e.
        from https://bitnodes.io/nodes/<ADDRESS>-<PORT>/, before it can be accessed from
        this endpoint.

        Parameters
        ----------
        address : str
            The IP address of the node.
        port : int
            The port of the node.

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
        if not isinstance(address, str) or not address:
            raise ValueError("Address must be a non-empty string.")
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("Port must be an integer between 1 and 65535.")
        url = f"{self.__base_url}nodes/{address}-{port}/"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_node_latency(self, address: str, port: int):
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
            The port of the node.

        Returns
        -------
        dict
            A dictionary containing the latency data for the node:
                daily: list of {timestamp: int, latency: int}
                weekly: list of {timestamp: int, latency: int}
                monthly: list of {timestamp: int, latency: int}
            Each list
        """
        if not isinstance(address, str) or not address:
            raise ValueError("Address must be a non-empty string.")
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("Port must be an integer between 1 and 65535.")
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
        if page is not None and not isinstance(page, int):
            raise ValueError("Page must be an integer.")
        if limit is not None and not (1 <= limit <= 100):
            raise ValueError("Limit must be an integer between 1 and 100.")
        url = f"{self.__base_url}leaderboard/"
        optional_params = {"page": page, "limit": limit}
        url = self._add_optional_params(url, optional_params)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_node_ranking(self, address: str, port: int) -> dict:
        """
        Get ranking and associated Peer Index (PIX) data for an activated node. New node must be
        activated separately, i.e. from https://bitnodes.io/nodes/<ADDRESS>-<PORT>/, before it
        can be accessed from this endpoint.

        Parameters
        ----------
        address : str
            The IP address of the node.
        port : int
            The port of the node.

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
        if not isinstance(address, str) or not address:
            raise ValueError("Address must be a non-empty string.")
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("Port must be an integer between 1 and 65535.")
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
        if page is not None and not isinstance(page, int):
            raise ValueError("Page must be an integer.")
        if limit is not None and not (1 <= limit <= 100):
            raise ValueError("Limit must be an integer between 1 and 100.")
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

    def get_dns_seeder(self, record: str = "AAAA", prefix: str = None) -> dict:
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

        Returns
        -------
        list
        A list of tuples, where each tuple represents a socket address for a resolved node.
        Each tuple contains:
            - Address Family: Indicates IPv4 (AF_INET) or IPv6 (AF_INET6).
            - Socket Type: The type of socket (e.g., SOCK_STREAM for TCP, SOCK_DGRAM for UDP).
            - Protocol: The protocol used (e.g., 6 for TCP, 17 for UDP).
            - Canonical Name: Typically an empty string, unless a canonical name is resolved.
            - Socket Address: A tuple containing:
                - The IP address (IPv4 or IPv6).
                - Additional fields (e.g., port, flow info, scope ID) depending on the address family.

        Examples
        --------
        """
        if record.lower() not in ["a", "aaaa", "txt"]:
            raise ValueError("Record must be one of 'a', 'aaaa', 'txt'.")
        domain = f"{prefix}.seed.bitnodes.io" if prefix else "seed.bitnodes.io"
        if record.lower() == "aaaa":
            domain_records = socket.getaddrinfo(domain, None, socket.AF_INET6)
        elif record.lower() == "a":
            domain_records = socket.getaddrinfo(domain, None, socket.AF_INET)
        # revisit tor domains. ipv4 won't work for tor
        else:
            domain_records = socket.getaddrinfo(domain, None, socket.AF_INET)
        return domain_records


if __name__ == "__main__":
    b = BitnodesAPI()
    print(
        b.get_data_propogation(
            "51b4cc62ca39f7f7d567b8288a5d73aa29e4e059282077b4fe06eb16db882f37"
        )
    )
