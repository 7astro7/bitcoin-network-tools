import pytest
from bitcoin_network_tools.bitnodes_api import BitnodesAPI


class TestBitnodesAPI:

    @pytest.fixture
    def bitnodesapi(self) -> BitnodesAPI:
        return BitnodesAPI()

    @pytest.fixture
    def inv_hash(self) -> str:
        return "51b4cc62ca39f7f7d567b8288a5d73aa29e4e059282077b4fe06eb16db882f37"

    @pytest.fixture
    def working_address_and_port(self, bitnodesapi: BitnodesAPI) -> tuple:
        address_list = bitnodesapi.get_address_list()
        working_address = address_list["results"][0]["address"]
        working_port = address_list["results"][0]["port"]
        return working_address, working_port

    def test_validate_pagination(self, bitnodesapi: BitnodesAPI):
        pass 

    def test_validate_address_port(self, bitnodesapi: BitnodesAPI):
        pass

    def test_add_optional_params(self, bitnodesapi: BitnodesAPI):
        """Test with optional parameters containing None values."""
        url = "https://bitnodes.io/api/v1/snapshots/"
        params = {"page": 2, "limit": 100}
        result = bitnodesapi._add_optional_params(url, params)
        assert result == "https://bitnodes.io/api/v1/snapshots/?page=2&limit=100"
        # add tests for all other methods perhaps

    def test_get_snapshots(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(ValueError, match="Page must be an integer."):
            bitnodesapi.get_snapshots(page=None)
        with pytest.raises(
            ValueError, match="Limit must be an integer between 1 and 100."
        ):
            bitnodesapi.get_snapshots(limit=0)
        observed = bitnodesapi.get_snapshots(page=1, limit=10)
        assert isinstance(observed, dict)
        assert "count" in observed.keys()
        assert "next" in observed.keys()
        assert "previous" in observed.keys()
        assert "results" in observed.keys()

    def test_get_nodes_list(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(
            ValueError, match="Field must be either 'coordinates' or 'user_agents'."
        ):
            bitnodesapi.get_nodes_list(field="test")
        with pytest.raises(
            ValueError,
            match="Timestamp must be a string representation of integer or 'latest'.",
        ):
            bitnodesapi.get_nodes_list(timestamp="test")
        observed = bitnodesapi.get_nodes_list(field="coordinates")
        assert isinstance(observed, dict)
        assert "timestamp" in observed.keys()
        assert "total_nodes" in observed.keys()
        assert "latest_height" in observed.keys()
        assert "nodes" in observed.keys()

    def test_get_address_list(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(ValueError, match="Page must be an integer."):
            bitnodesapi.get_address_list(page=None)
        with pytest.raises(
            ValueError, match="Limit must be an integer between 1 and 100."
        ):
            bitnodesapi.get_address_list(limit=0)
        with pytest.raises(ValueError, match="q must be a list of strings."):
            bitnodesapi.get_address_list(
                q=[
                    22,
                    80,
                ]
            )
        observed = bitnodesapi.get_address_list(
            q=[
                "2a01:e34:ec76:c9d0:2520:5f4d:852d:3aa2",
                "2601:602:8d00:7070:1868:945c:98e6:d35",
            ]
        )
        assert isinstance(observed, dict)
        assert "count" in observed.keys()
        assert "next" in observed.keys()
        assert "previous" in observed.keys()
        assert "results" in observed.keys()

    def test_get_node_status(
        self, bitnodesapi: BitnodesAPI, working_address_and_port: tuple
    ):
        with pytest.raises(ValueError, match="Address must be a non-empty string."):
            bitnodesapi.get_node_status(address=None)
        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535."
        ):
            bitnodesapi.get_node_status(address=None)
        with pytest.raises(ValueError, match="Invalid URL."):
            bitnodesapi.get_node_status(port=0)
        working_address, working_port = working_address_and_port
        observed = bitnodesapi.get_node_status(working_address, working_port)
        assert isinstance(observed, dict)
        assert "address" in observed.keys()
        assert "status" in observed.keys()
        assert "port" in observed.keys()
        assert "mbps" in observed.keys()

    def test_get_node_latency(
        self, bitnodesapi: BitnodesAPI, working_address_and_port: tuple
    ):
        with pytest.raises(ValueError, match="Address must be a non-empty string."):
            bitnodesapi.get_node_latency(address=None)
        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535."
        ):
            bitnodesapi.get_node_latency(port=0)
        working_address, working_port = working_address_and_port
        observed = bitnodesapi.get_node_latency(working_address, working_port)
        assert isinstance(observed, dict)
        assert "daily_latency" in observed.keys()
        assert "weekly_latency" in observed.keys()
        assert "monthly_latency" in observed.keys()

    def test_get_leaderboard(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(ValueError, match="Page must be an integer."):
            bitnodesapi.get_leaderboard(page=None)
        with pytest.raises(
            ValueError, match="Limit must be an integer between 1 and 100."
        ):
            bitnodesapi.get_leaderboard(limit=0)
        observed = bitnodesapi.get_leaderboard(page=1, limit=10)
        assert isinstance(observed, dict)
        assert "count" in observed.keys()
        assert "next" in observed.keys()
        assert "previous" in observed.keys()
        assert "results" in observed.keys()

    def test_get_node_ranking(
        self, bitnodesapi: BitnodesAPI, working_address_and_port: tuple
    ):
        with pytest.raises(ValueError, match="Address must be a non-empty string."):
            bitnodesapi.get_node_ranking(address=None)
        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535."
        ):
            bitnodesapi.get_node_ranking(address="128.65.194.136", port=0)
        working_address, working_port = working_address_and_port
        observed = bitnodesapi.get_node_ranking(working_address, working_port)
        assert isinstance(observed, dict)
        assert "node" in observed.keys()
        assert "peer_index" in observed.keys()
        assert "rank" in observed.keys()

    def test_get_data_propagation_list(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(ValueError, match="Page must be an integer."):
            bitnodesapi.get_data_propagation_list(page=None)
        with pytest.raises(
            ValueError, match="Limit must be an integer between 1 and 100."
        ):
            bitnodesapi.get_data_propagation_list(limit=0)
        observed = bitnodesapi.get_data_propagation_list(page=1, limit=10)
        assert isinstance(observed, dict)
        assert "count" in observed.keys()
        assert "next" in observed.keys()
        assert "previous" in observed.keys()
        assert "results" in observed.keys()

    def test_get_data_propagation(self, bitnodesapi: BitnodesAPI, inv_hash: str):
        with pytest.raises(
            ValueError, match="Inventory hash must be a non-empty string."
        ):
            bitnodesapi.get_data_propagation(inv_hash=None)

        observed = bitnodesapi.get_data_propagation(inv_hash)
        assert isinstance(observed, dict)
        assert "inv_hash" in observed.keys()
        assert "stats" in observed.keys()

    def test_get_dns_seeder(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(
            ValueError, match="Record must be one of 'a', 'aaaa', 'txt'."
        ):
            bitnodesapi.get_dns_seeder("test")
        with pytest.raises(ValueError, match="Resolver timeout must be at least 1 second."):
            bitnodesapi.get_dns_seeder("a", timeout=0)
        with pytest.raises(ValueError, match="Resolver lifetime must be at least 1 second."):
            bitnodesapi.get_dns_seeder("a", lifetime=0)
        observed = bitnodesapi.get_dns_seeder("a")
        assert isinstance(observed, list)
        assert len(observed) > 0
