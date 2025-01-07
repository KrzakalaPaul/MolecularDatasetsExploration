import argparse
import numpy as np
import pickle
from tqdm import tqdm
from rdkit.Chem import MolFromSmiles
import pandas as pd
import os
from time import perf_counter
from split_utils import RandomSplitter, ScaffoldSplitter
from rdkit import RDLogger
import lmdb
import logging

logger = logging.getLogger(__name__)

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
    return env
 
 
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
        "--map_size", type=int, required=True, help="Map size in kilobytes."
    )
    args = parser.parse_args()
    
    # Get dataset name and split percentages from command line arguments
    dataset_name = args.dataset_name
    split_percentage = args.split_percentage
    
    # Load the dataset from CSV file
    csv_path = f"smiles/{args.dataset_name}.csv"
    targets = pd.read_csv(csv_path)

    # Extract SMILES strings and remove the column from targets
    smiles_list = targets["smiles"].tolist()
    targets.drop(columns="smiles", inplace=True)
    
    # Open a temporary LMDB database to store the graphs
    path = f"graphs/{args.dataset_name}"
    split = "temp"
    env_temp = open_db(path, split, args.map_size)
    
    # Initialize the splitter based on the chosen type
    splitter = ScaffoldSplitter(*split_percentage) if args.splitter == "scaffold" else RandomSplitter(*split_percentage)
    
    start_time = perf_counter()

    with env_temp.begin(write=True) as txn_temp:
        n_invalid = 0
        for i, smiles in enumerate(tqdm(smiles_list, desc="Processing SMILES")):
            # Convert SMILES to graph
            graph = smiles2graph(smiles)

            # If SMILES gives valid molecule save it, otherwise skip
            if graph is None:
                n_invalid += 1
                continue
            else:
                target = targets.iloc[i].values
                data = pickle.dumps((graph, target))
                splitter.add(idx=i, smiles=smiles)
                txn_temp.put(f"{i}".encode("ascii"), data)

        # Perform the dataset split
        splitter.split()
        
        # Save the split datasets into separate LMDB files
        for split, split_percentage in zip(["train", "valid", "test"], split_percentage):
            path = f"graphs/{args.dataset_name}"
            map_size = int(args.map_size * split_percentage)
            env_split = open_db(path, split, map_size)
            
            indices = getattr(splitter, f"{split}_indices")
            
            with env_split.begin(write=True) as txn_split:
                for i, j in enumerate(indices):
                    data = pickle.loads(txn_temp.pop(f"{j}".encode("ascii")))
                    txn_split.put(f"{i}".encode("ascii"), pickle.dumps(data))
            
                txn_split.put("size".encode("ascii"), str(len(indices)).encode("ascii"))
            
    # Remove the temporary LMDB database
    temp_db_path = f"graphs/{args.dataset_name}/temp.lmdb"
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)

    end_time = perf_counter()
    print(
        f"...done, took {end_time - start_time:.2f} seconds, removed {n_invalid} invalid SMILES."
    )
    print(f"Train: {len(splitter.train_indices)}")
    print(f"Valid: {len(splitter.valid_indices)}")
    print(f"Test: {len(splitter.test_indices)}")
