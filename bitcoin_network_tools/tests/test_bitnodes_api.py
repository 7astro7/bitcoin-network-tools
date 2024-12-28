import pytest
from bitcoin_network_tools.bitnodes_api import BitnodesAPI


class TestBitnodesAPI:

    @pytest.fixture
    def bitnodesapi(self) -> BitnodesAPI:
        return BitnodesAPI()

    @pytest.fixture
    def inv_hash(self) -> str:
        return "51b4cc62ca39f7f7d567b8288a5d73aa29e4e059282077b4fe06eb16db882f37"

    def test_add_optional_params(self, bitnodesapi: BitnodesAPI):
        """Test with optional parameters containing None values."""
        url = "https://bitnodes.io/api/v1/snapshots/"
        params = {"page": 2, "limit": 100}
        result = bitnodesapi._add_optional_params(url, params)
        assert result == "https://bitnodes.io/api/v1/snapshots/?page=2&limit=100"
        # add tests for all other methods perhaps

    def test_get_snapshots(self, bitnodesapi: BitnodesAPI):
        pass 

    def test_get_nodes_list(self, bitnodesapi: BitnodesAPI):
        pass 

    def test_get_addresses(self, bitnodesapi: BitnodesAPI):
        pass 

    def test_get_node_status(self, bitnodesapi: BitnodesAPI):
        pass 

    def test_get_node_latency(self, bitnodesapi: BitnodesAPI):
        pass 

    def test_get_leaderboard(self, bitnodesapi: BitnodesAPI):
        pass 

    def test_get_node_ranking(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(ValueError, match="Address must be a non-empty string."):
            bitnodesapi.get_node_ranking(address=None)
        with pytest.raises(
            ValueError, match="Port must be an integer between 1 and 65535."
        ):
            bitnodesapi.get_node_ranking(address="128.65.194.136", port=0)
        observed = bitnodesapi.get_node_ranking("128.65.194.136", 8333)
        assert isinstance(observed, dict)
        assert "node" in observed.keys()
        assert "peer_index" in observed.keys()
        assert "rank" in observed.keys()

    def test_get_data_propagation_list(self, bitnodesapi: BitnodesAPI):
        with pytest.raises(ValueError, match="Page must be an integer."):
            bitnodesapi.get_data_propagation_list(page=None)
        with pytest.raises(ValueError, match="Limit must be an integer between 1 and 100."):
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
        observed = bitnodesapi.get_dns_seeder("a")
        assert isinstance(observed, list)
        assert len(observed) > 0
