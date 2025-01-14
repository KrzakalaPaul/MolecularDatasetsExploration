import os 
import pickle
import lmdb
from functools import lru_cache
import torch

class LMDBDataset:
    def __init__(self, db_path, split="train"):
        self.db_path = os.path.join(db_path, split+".lmdb")
        assert os.path.isfile(self.db_path), "{} not found".format(self.db_path)
        env = self.connect_db(self.db_path)
        self.dataset_size = int(env.begin().get("size".encode("ascii")).decode("ascii")) 
        node_labels = eval(env.begin().get("node_labels".encode("ascii")))
        self.n_node_labels = len(node_labels)
        edge_labels = eval(env.begin().get("edge_labels".encode("ascii")))
        self.n_edge_labels = len(edge_labels)

    def connect_db(self, lmdb_path, save_to_self=False):
        env = lmdb.open(
            lmdb_path,
            subdir=False,
            readonly=True,
            lock=False,
            readahead=False,
            meminit=False,
            max_readers=256,
        )
        if not save_to_self:
            return env
        else:
            self.env = env

    def __len__(self):
        return self.dataset_size

    @lru_cache()
    def __getitem__(self, idx):
        if not hasattr(self, "env"):
            self.connect_db(self.db_path, save_to_self=True)
        datapoint_pickled = self.env.begin().get(f"{idx}".encode("ascii"))
        data = pickle.loads(datapoint_pickled)
        
        if isinstance(data, tuple):
            graph, target = data
        else:
            graph = data
            
        node_labels = graph["node_labels"]
        adjacency_matrix = graph["adjacency_matrix"]
        edges_labels = graph["edges_labels"]
        SP_matrix = graph["SP_matrix"]
        
        node_labels = torch.nn.functional.one_hot(torch.tensor(node_labels, dtype=torch.long), num_classes=self.n_node_labels)
        adjacency_matrix = torch.tensor(adjacency_matrix.todense())
        edges_labels = torch.nn.functional.one_hot(torch.tensor(edges_labels.todense(), dtype=torch.long), num_classes=self.n_edge_labels)
        SP_matrix = torch.tensor(SP_matrix)
    
        graph = {'node_labels': node_labels,
                 'adjacency_matrix': adjacency_matrix,
                 'edges_labels': edges_labels,
                 'SP_matrix': SP_matrix}
            
        return graph