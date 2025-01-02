import pandas as pd
import lmdb
import pickle
import os
from multiprocessing import Pool
from time import perf_counter
from rdkit import Chem
import numpy as np
import json

map_size_KO = 100000  # Setting to high values is not a problem on Linux, as map_size is virtual memory (this is not the case on Windows)
max_samples = None
n_threads = 1

valid_atomic_nums = list(range(1, 119)) + ["ukn"]
valid_bond_types = ["SINGLE", "DOUBLE", "TRIPLE", "AROMATIC", "ukn"]

valid_features_dic = {
    "atomomic_nums": valid_atomic_nums,
    "bond_types": valid_bond_types,
}

with open("valid_features_dic.json", "w") as f:
    json.dump(valid_features_dic, f)


def safe_index(l, e):
    """
    Return index of element e in list l. If e is not present, return the last index
    """
    try:
        return l.index(e)
    except:
        return len(l) - 1


def smiles2graph(smiles):

    mol = Chem.MolFromSmiles(smiles)
    atom_atomic_nums = []
    for atom in mol.GetAtoms():
        atom_atomic_nums.append(
            safe_index(valid_features_dic["atomomic_nums"], atom.GetAtomicNum())
        )
    atom_atomic_nums = np.array(atom_atomic_nums, dtype=np.uint8)

    if len(mol.GetBonds()) > 0:  # mol has bonds
        edges_list = []
        edge_features_list = []
        for bond in mol.GetBonds():
            i = bond.GetBeginAtomIdx()
            j = bond.GetEndAtomIdx()

            edge_feature = str(bond.GetBondType())
            edge_feature = safe_index(valid_features_dic["bond_types"], edge_feature)

            # add edges in both directions
            edges_list.append((i, j))
            edge_features_list.append(edge_feature)
            edges_list.append((j, i))
            edge_features_list.append(edge_feature)

        # data.edge_index: Graph connectivity in COO format with shape [2, num_edges]
        edge_index = np.array(edges_list, dtype=np.uint8).T

        # data.edge_attr: Edge feature matrix with shape [num_edges, num_edge_features]
        edge_attr = np.array(edge_features_list, dtype=np.uint8)

    else:  # mol has no bonds
        edge_index = np.empty((2, 0), dtype=np.uint8)
        edge_attr = np.empty((0, 1), dtype=np.uint8)

    return atom_atomic_nums, edge_index, edge_attr


def process_smiles(smiles):
    atom_atomic_nums, edge_index, edge_attr = smiles2graph(smiles)
    graph_data = {
        "atom_atomic_nums": atom_atomic_nums,
        "edge_index": edge_index,
        "edge_attr": edge_attr,
    }
    return pickle.dumps(graph_data, protocol=-1)


if __name__ == "__main__":

    smiles_list = pd.read_csv("data/QM9.csv")["smiles"].values
    if max_samples is not None:
        smiles_list = smiles_list[:max_samples]

    file = "data/QM9.lmdb"

    if os.path.exists(file):
        os.remove(file)

    env = lmdb.open(
        file,
        subdir=False,
        readonly=False,
        lock=False,
        readahead=False,
        meminit=False,
        max_readers=1,
        map_size=map_size_KO * 1024,
    )

    start_time = perf_counter()

    with env.begin(write=True) as txn:

        if n_threads == 1:
            # Single process version
            for i, smiles in enumerate(smiles_list):
                graph_data = process_smiles(smiles)
                txn.put(f"{i}".encode("ascii"), graph_data)
        else:
            # Multi process version
            with Pool() as pool:
                for i, graph_data in enumerate(
                    pool.imap_unordered(process_smiles, smiles_list)
                ):
                    txn.put(f"{i}".encode("ascii"), graph_data)

    end_time = perf_counter()
    print(f"{end_time - start_time:.2f} seconds")
    env.close()
