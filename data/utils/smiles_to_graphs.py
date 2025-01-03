import argparse
import numpy as np
import pickle
import lmdb
from rdkit.Chem import MolFromSmiles
import pandas as pd
import os
from time import perf_counter
from multiprocessing import Pool

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


def smiles2graph(smiles):

    mol = MolFromSmiles(smiles)
    atom_atomic_nums = []
    for atom in mol.GetAtoms():
        atom_atomic_nums.append(safe_index(valid_atomic_nums, atom.GetAtomicNum()))
    atom_atomic_nums = np.array(atom_atomic_nums, dtype=np.uint8)

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

    return atom_atomic_nums, edge_index, edge_attr


def process_smiles(smiles):
    atom_atomic_nums, edge_index, edge_attr = smiles2graph(smiles)
    graph_data = {
        "atom_atomic_nums": atom_atomic_nums,
        "edge_index": edge_index,
        "edge_attr": edge_attr,
    }
    return graph_data


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert SMILES to graphs.")
    parser.add_argument(
        "--dataset_name",
        type=str,
        required=True,
        help="Smiles dataset name. Should be in smiles/[dataset_name].csv",
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

    start_time = perf_counter()

    with env.begin(write=True) as txn:

        if args.n_threads == 1:
            # Single process version
            for i, smiles in enumerate(smiles_list):
                graph_data = process_smiles(smiles)
                targets = csv.iloc[i].values
                data = pickle.dumps((graph_data, targets))
                txn.put(f"{i}".encode("ascii"), data)
        else:
            # Multi process version
            with Pool() as pool:
                for i, graph_data in enumerate(
                    pool.imap_unordered(process_smiles, smiles_list)
                ):
                    targets = csv.iloc[i].values
                data = pickle.dumps((graph_data, targets))
                txn.put(f"{i}".encode("ascii"), data)

    end_time = perf_counter()
    print(
        f"Conversion of {args.dataset_name} to graph with rdkit done, took {end_time - start_time:.2f} seconds"
    )
    env.close()
