import argparse
import numpy as np
import pickle
import lmdb
from rdkit.Chem import MolFromSmiles
import pandas as pd
import os
from time import perf_counter
from multiprocessing import Pool
from .split_utils import RandomSplitter, ScaffoldSplitter
from rdkit import RDLogger

valid_atomic_nums = list(range(1, 119)) + ["ukn"]
valid_bond_types = ["SINGLE", "DOUBLE", "TRIPLE", "AROMATIC", "ukn"]


def safe_index(l, e):
    """
    Return index of element e in list l. If e is not present, return the last index
    """
    try:
        return l.index(e)
    except:
        return len(l) - 1


def smiles2graph(smiles, max_atoms=50):
    RDLogger.DisableLog('rdApp.*')
    mol = MolFromSmiles(smiles)
    if mol is None:
        return None
    atom_atomic_nums = []
    for atom in mol.GetAtoms():
        atom_atomic_nums.append(safe_index(valid_atomic_nums, atom.GetAtomicNum()))
    atom_atomic_nums = np.array(atom_atomic_nums, dtype=np.uint8)
    
    if len(atom_atomic_nums) >= max_atoms:
        return None

    if len(mol.GetBonds()) > 0:  # mol has bonds
        edges_list = []
        edge_features_list = []
        for bond in mol.GetBonds():
            i = bond.GetBeginAtomIdx()
            j = bond.GetEndAtomIdx()

            edge_feature = str(bond.GetBondType())
            edge_feature = safe_index(valid_bond_types, edge_feature)

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

    graph = {
        "atom_atomic_nums": atom_atomic_nums,
        "edge_index": edge_index,
        "edge_attr": edge_attr,
    }

    return graph


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Parse command line arguments for dataset splitting."
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        required=True,
        help="Raw dataset name. Should be in raw/[dataset_name].csv",
    )
    parser.add_argument(
        "--splitter",
        type=str,
        required=True,
        choices=["random", "scaffold"],
        help="Type of splitter to use.",
    )
    parser.add_argument(
        "--split_percentage",
        type=float,
        nargs=3,
        required=True,
        help="Split percentages for train, validation, and test sets.",
    )
    parser.add_argument(
        "--map_size_in_Ko", type=int, required=True, help="Map size in kilobytes."
    )
    parser.add_argument("--n_threads", type=int, default=1, help="Number of threads.")
    args = parser.parse_args()

    csv_path = f"smiles/{args.dataset_name}.csv"
    csv = pd.read_csv(csv_path)

    smiles_list = csv["smiles"].tolist()
    csv = csv.drop(columns="smiles")

    file = f"graphs/{args.dataset_name}.lmdb"
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
        map_size=args.map_size_in_Ko * 1024,
    )

    splitter = ScaffoldSplitter(*args.split_percentage) if args.splitter == "scaffold" else RandomSplitter(*args.split_percentage)
    
    start_time = perf_counter()

    with env.begin(write=True) as txn:

        n_invalid = 0
        for i, smiles in enumerate(smiles_list):

            # Convert SMILES to graph
            graph = smiles2graph(smiles)

            # If SMILES gives valid molecule save it, otherwise skip
            if graph is None:
                n_invalid += 1
                continue
            else:
                targets = csv.iloc[i].values
                data = pickle.dumps((graph, targets))
                splitter.add(idx=i, smiles=smiles)
                txn.put(f"{i}".encode("ascii"), data)

        splitter.split()
        
        txn.put("train_size".encode("ascii"), pickle.dumps(len(splitter.train_indices)))
        txn.put("valid_size".encode("ascii"), pickle.dumps(len(splitter.valid_indices)))
        txn.put("test_size".encode("ascii"), pickle.dumps(len(splitter.test_indices)))

        # Create train, validation, and test sets
        for i, j in enumerate(splitter.train_indices):
            data = pickle.loads(txn.pop(f"{j}".encode("ascii")))
            txn.put(f"train_{i}".encode("ascii"), pickle.dumps(data))

        for i, j in enumerate(splitter.valid_indices):
            data = pickle.loads(txn.pop(f"{j}".encode("ascii")))
            txn.put(f"valid_{i}".encode("ascii"), pickle.dumps(data))

        for i, j in enumerate(splitter.test_indices):
            data = pickle.loads(txn.pop(f"{j}".encode("ascii")))
            txn.put(f"test_{i}".encode("ascii"), pickle.dumps(data))
            
    end_time = perf_counter()
    print(
        f"...done, took {end_time - start_time:.2f} seconds, removed {n_invalid} invalid SMILES."
    )
    print(f"Train: {len(splitter.train_indices)}")
    print(f"Valid: {len(splitter.valid_indices)}")
    print(f"Test: {len(splitter.test_indices)}")
    env.close()
