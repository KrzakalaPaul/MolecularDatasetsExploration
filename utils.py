import numpy as np
from rdkit.Chem import MolFromSmiles
import os
from rdkit import RDLogger
import lmdb
from scipy.sparse import csgraph, csr_matrix
import os 
import lmdb
import pickle
from functools import lru_cache
from torch_geometric.data import Data
import torch.nn.functional as F
import torch

# -------------------------------- SMIES TO GRAPHS -------------------------------- #

def safe_index(lst, item):
    '''
    If item in list: return idx of item
    Elif "ukn" in list: return idx of "ukn"
    Else: return None
    '''
    if item in lst:
        return lst.index(item)
    elif "ukn" in lst:
        return lst.index("ukn")
    else:
        return None

def smiles2graph(smiles, max_size, valid_atomic_nums, valid_bond_types):
    RDLogger.DisableLog('rdApp.*')
    mol = MolFromSmiles(smiles)
    #logp = MolLogP(mol)
    if mol is None:
        return None
    node_labels = []
    for atom in mol.GetAtoms():
        label = safe_index(valid_atomic_nums, atom.GetAtomicNum())
        if label is None:
            return None
        node_labels.append(label)
    node_labels = np.array(node_labels, dtype=np.uint8)
    size = len(node_labels)
    
    if size > max_size:
        return None
    
    edges_i = []
    edges_j = []
    edge_labels = []

    for bond in mol.GetBonds():
        i = bond.GetBeginAtomIdx()
        j = bond.GetEndAtomIdx()
        bondtype = str(bond.GetBondType())
        
        edges_i.append(i)
        edges_j.append(j)
        edges_i.append(j)
        edges_j.append(i)

        label = safe_index(valid_bond_types, bondtype)+1 # 0 is reserved for "None"
        if label is None:
            return None
        edge_labels.append(label) 
        edge_labels.append(label) 

    adjacency_matrix = csr_matrix((np.ones(len(edges_i), dtype=np.uint8), (edges_i, edges_j)), shape=(size,size))
    edge_labels = csr_matrix((np.array(edge_labels, dtype=np.uint8), (edges_i, edges_j)), shape=(size,size))
    SP_matrix = csgraph.shortest_path(adjacency_matrix, directed=False, unweighted=True)
    if np.max(SP_matrix) == np.inf:
        return None
    SP_matrix = SP_matrix.astype(np.uint8)

    graph = {
        "node_labels": node_labels,
        "adjacency_matrix": adjacency_matrix,
        "edge_labels": edge_labels,
        "SP_matrix": SP_matrix
    }

    return graph

def smiles2geometricTensor(smiles, max_size, valid_atomic_nums, valid_bond_types):
    RDLogger.DisableLog('rdApp.*')
    mol = MolFromSmiles(smiles)
    if mol is None:
        return None

    node_labels = []
    for atom in mol.GetAtoms():
        label = safe_index(valid_atomic_nums, atom.GetAtomicNum())
        if label is None:
            return None
        node_labels.append(label)

    node_labels = torch.tensor(node_labels, dtype=torch.long)
    size = node_labels.size(0)
    if size > max_size:
        return None

    edges_i = []
    edges_j = []

    for bond in mol.GetBonds():
        i = bond.GetBeginAtomIdx()
        j = bond.GetEndAtomIdx()
        edges_i += [i, j]
        edges_j += [j, i]

    edge_index = torch.tensor([edges_i, edges_j], dtype=torch.long)
    x = F.one_hot(node_labels, num_classes=len(valid_atomic_nums)).float() 
    return Data(x=x, edge_index=edge_index)

# -------------------------------- LMDB UTILS  -------------------------------- #

class LMDBDataset:
    def __init__(self, db_path, split="train"):
        self.db_path = os.path.join(db_path, split+".lmdb")
        assert os.path.isfile(self.db_path), "{} not found".format(self.db_path)
        env = self.connect_db(self.db_path)
        self.dataset_size = read(env, "size")

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
    
    def load_idx(self, idx):
        if not hasattr(self, "env"):
            self.connect_db(self.db_path, save_to_self=True)
        data = read(self.env, str(idx))
        return data

    @lru_cache()
    def __getitem__(self, idx):
        if not hasattr(self, "env"):
            self.connect_db(self.db_path, save_to_self=True)
        datapoint_pickled = self.env.begin().get(f"{idx}".encode("ascii"))
        data = pickle.loads(datapoint_pickled)
        return data
# -------------------------------- LMDB UTILS  -------------------------------- #

def open_db(path, split, mapsize=1099511627776, delete=True):
    file = os.path.join(path, f"{split}.lmdb")
    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.exists(file) and delete:
        os.remove(file)
    env = lmdb.open(
                    file,
                    subdir=False,
                    readonly=False,
                    lock=False,
                    readahead=False,
                    meminit=False,
                    map_size=mapsize
                    )
    write_size(env, 0)
    return env

def read(env,key):
    return pickle.loads(env.begin().get(key.encode("ascii")))

def write(env,key,value):
    with env.begin(write=True) as txn:
        txn.put(key.encode("ascii"), pickle.dumps(value))
        
def read_size(env):
    return read(env, "size")

def write_size(env, size):
    write(env, "size", size)
    
def add_data_list(data_list, env):
    n = read_size(env)     # type: ignore
    with env.begin(write=True) as txn:
        for k, data in enumerate(data_list):
            key = f"{n+k}".encode("ascii")
            txn.put(key, pickle.dumps(data))
    write_size(env, n + len(data_list)) 

