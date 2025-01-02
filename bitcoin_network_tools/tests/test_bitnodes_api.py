import pytest
from bitcoin_network_tools.bitnodes_api import BitnodesAPI
from urllib.parse import unquote
import tempfile
import os

ENV_API_KEY = (
    "BITNODES_PUBLIC_KEY" in os.environ and "BITNODES_PRIVATE_KEY" in os.environ
)


class TestBitnodesAPI:

    @pytest.fixture
    def bitnodesapi(self) -> BitnodesAPI:
        return BitnodesAPI()

    @pytest.fixture
    def inv_hash(self) -> str:
        return "51b4cc62ca39f7f7d567b8288a5d73aa29e4e059282077b4fe06eb16db882f37"

    @pytest.fixture
    def working_address_and_port(self, bitnodesapi: BitnodesAPI) -> tuple:
        nodes_list = bitnodesapi.get_leaderboard()

        working_address_port = nodes_list["results"][0]["node"]
        # find an address that does not contain brackets, such as 
        # [2001:1bc0:c1::2000]:8333'
        for i in range(1, len(nodes_list["results"])):
            if "[" not in nodes_list["results"][i]["node"]:
                working_address_port = nodes_list["results"][i]["node"]
                break
        return tuple(working_address_port.split(":"))

    @pytest.mark.skipif(ENV_API_KEY, reason="API keys in env: no warning.")
    def test_constructor_warns_unauthenticated(self):
        with pytest.warns(
            UserWarning,
            match="Warning: Bitnodes API is being used in unauthenticated mode.",
        ):
            BitnodesAPI()

    def test_set_public_key(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(
            ValueError, match="Public API key must be a non-empty string."
        ):
            bitnodesapi.set_public_api_key(-9999)

        assert bitnodesapi.set_public_api_key("true because string")

    def test_get_public_key(self, monkeypatch: pytest.MonkeyPatch):

        monkeypatch.delenv("BITNODES_PUBLIC_KEY", raising=False)
        bn = BitnodesAPI(public_api_key="test_public_key")
        assert bn.get_public_api_key() == "test_public_key"

    def test_set_private_key_path(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(
            FileNotFoundError, match="The private key file does not exist."
        ) as e:
            bitnodesapi.set_private_key_path("non_existent_file")

        with tempfile.TemporaryFile() as f:
            f.write(b"mock_private_key")
            f.flush()
            assert bitnodesapi.set_private_key_path(f.name)

    def test_get_private_key(self, bitnodesapi: BitnodesAPI, monkeypatch: pytest.MonkeyPatch):

        monkeypatch.delenv("BITNODES_PRIVATE_KEY", raising=False)

        with pytest.raises(RuntimeError):
            bitnodesapi._get_private_key()

        with tempfile.NamedTemporaryFile() as f:
            f.write(b"mock_private_key")
            f.flush()
            bitnodesapi.set_private_key_path(f.name)
            assert bitnodesapi._get_private_key() == "mock_private_key"

    def test_validate_pagination(self):
        with pytest.raises(ValueError, match="Page must be an integer."):
            BitnodesAPI._validate_pagination(page="test")
        with pytest.raises(
            ValueError, match="Limit must be an integer between 1 and 100."
        ):
            BitnodesAPI._validate_pagination(limit=101)

    def test_validate_address_port(self):
        with pytest.raises(ValueError, match="Address must be a non-empty string."):
            BitnodesAPI._validate_address_port(address=None, port=8333)

        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535."
        ):
            BitnodesAPI._validate_address_port(address="-99", port=0)

        with pytest.raises(
            ValueError,
            match="Port must be an integer or a string that can be converted to an integer.",
        ):
            BitnodesAPI._validate_address_port(
                address="test_string", port="test_string"
            )

    def test_add_optional_params(self, bitnodesapi: BitnodesAPI):
        """Test with optional parameters containing None values."""

        # URL for get_address_list
        url = "https://bitnodes.io/api/v1/addresses/"
        params = {
            "page": 2,
            "limit": 100,
            "q": ".onion",
        }
        observed = bitnodesapi._add_optional_params(url, params)
        expected = (
            "https://bitnodes.io/api/v1/addresses/"
            "?page=2&limit=100&"
            "q=.onion"
        )
        assert unquote(observed) == expected

        # URL for get_nodes_list
        url = "https://bitnodes.io/api/v1/snapshots/latest/"
        params = {"field": "coordinates"}
        observed = bitnodesapi._add_optional_params(url, params)
        expected = "https://bitnodes.io/api/v1/snapshots/latest/?field=coordinates"
        assert unquote(observed) == expected

        # test for get nodes list
        url = "https://bitnodes.io/api/v1/nodes/leaderboard/"
        params = {"page": None, "limit": None}
        observed = bitnodesapi._add_optional_params(url, params)
        expected = "https://bitnodes.io/api/v1/nodes/leaderboard/"
        assert unquote(observed) == expected

    def test_get_snapshots(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(ValueError, match="Page must be an integer."):
            bitnodesapi.get_snapshots(page="")
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

        observed_coordinates = bitnodesapi.get_nodes_list(field="coordinates")
        assert isinstance(observed_coordinates, dict)
        assert "timestamp" in observed_coordinates.keys()
        assert "total_nodes" in observed_coordinates.keys()
        assert "latest_height" in observed_coordinates.keys()
        assert "coordinates" in observed_coordinates.keys()

        observed_useragents = bitnodesapi.get_nodes_list(field="user_agents")
        assert isinstance(observed_useragents, dict)
        assert "timestamp" in observed_useragents.keys()
        assert "total_nodes" in observed_useragents.keys()
        assert "latest_height" in observed_useragents.keys()
        assert "user_agents" in observed_useragents.keys()

        observed_no_field = bitnodesapi.get_nodes_list()
        assert isinstance(observed_no_field, dict)
        assert "timestamp" in observed_no_field.keys()
        assert "total_nodes" in observed_no_field.keys()
        assert "latest_height" in observed_no_field.keys()
        assert "nodes" in observed_no_field.keys()

    def test_get_address_list(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(ValueError, match="Page must be an integer."):
            bitnodesapi.get_address_list(page="")
        with pytest.raises(
            ValueError, match="Limit must be an integer between 1 and 100."
        ):
            bitnodesapi.get_address_list(limit=0)
        with pytest.raises(ValueError, match="q must be a string representing a single search term."):
            bitnodesapi.get_address_list(q=[22, 80,])

        observed = bitnodesapi.get_address_list(q=".onion")
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
            bitnodesapi.get_node_status(address="127", port=0)
        
        working_address, working_port = working_address_and_port
        observed = bitnodesapi.get_node_status(working_address, working_port)
        assert isinstance(observed, dict)
        assert "address" in observed.keys()
        assert "status" in observed.keys()
        assert "data" in observed.keys()
        assert "mbps" in observed.keys()

    def test_get_node_latency(
        self, bitnodesapi: BitnodesAPI, working_address_and_port: tuple
    ):
        with pytest.raises(ValueError, match="Address must be a non-empty string."):
            bitnodesapi.get_node_latency(address=None)
        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535."
        ):
            bitnodesapi.get_node_latency(address="127.0.0.1", port=0)
        working_address, working_port = working_address_and_port
        observed = bitnodesapi.get_node_latency(working_address, working_port)
        assert isinstance(observed, dict)
        assert "daily_latency" in observed.keys()
        assert "weekly_latency" in observed.keys()
        assert "monthly_latency" in observed.keys()

    def test_get_leaderboard(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(ValueError, match="Page must be an integer."):
            bitnodesapi.get_leaderboard(page="txt")
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
            bitnodesapi.get_data_propagation_list(page="txt")
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
        assert "inv_hash" in observed["results"][0].keys()

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
        with pytest.raises(
            ValueError, match="Resolver timeout must be at least 1 second."
        ):
            bitnodesapi.get_dns_seeder("a", resolver_timeout=0)
        with pytest.raises(
            ValueError, match="Resolver lifetime must be at least 1 second."
        ):
            bitnodesapi.get_dns_seeder("a", resolver_lifetime=0)
        observed = bitnodesapi.get_dns_seeder("a")
        assert isinstance(observed, list)
        assert len(observed) > 0
