
import requests

class Analyzer:

    """
    Implementation of the Bitnodes API https://bitnodes.io/api/
    """

    def __init__(self):
        self.__base_url = "https://bitnodes.io/api/v1/"

    def get_snapshots(self, page: int = None):
        url = self.__base_url + "snapshots/"
        response = requests.get(url)
        return response.json()
    
    def get_nodes(self, timestamp: str = "latest", as_dataframe: bool = False) -> dict:
        """
        Retrieve the list of nodes from a snapshot.

        Parameters
        ----------
        timestamp : str
            The timestamp of the snapshot to retrieve. The default is "latest".
        as_dataframe : bool
            If True, the function will return a pandas DataFrame. The default is False.

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
        url = f"{self.__base_url}snapshots/{timestamp}/"
        response = requests.get(url)
        nodes = response.json()
        # 
        breakpoint()
        if as_dataframe:
            pass 
        return nodes
    
    def get_addresses(self):
        pass 

    def get_node_status(self):
        pass 
    
    def get_node_latency(self, address: str, port: int):
        url = f"{self.__base_url}nodes/{address}-{port}/latency/"
        response = requests.get(url)
        return response.json()
    
    def getleaderboard(self):
        pass

    def get_node_ranking(self):
        pass

    def get_data_propogation_list(self):
        pass

    def get_data_propogation(self):
        pass

    def get_dns_seeder(self):
        pass

    
    


    


if __name__ == "__main__":
    analyzer = Analyzer()
    print(analyzer.get_nodes())