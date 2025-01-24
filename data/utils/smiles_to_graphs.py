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
from scipy.sparse import csgraph, csr_matrix

valid_atomic_nums = [6, 8, 7, 17, 16, 9, 35, 15, 53, 14, 11, 33, 80, 50, 5, 20, 19, 30, 26, 34, 13, 29, 12, 82, 24, 27, 1, 28, 56, 78, 25, "ukn"]
valid_bond_types = ["SINGLE", "DOUBLE", "TRIPLE", "AROMATIC", "ukn"]

logger = logging.getLogger(__name__)

def add_labels_to_db(env):
    with env.begin(write=True) as txn:
        txn.put("node_labels".encode("ascii"), str(valid_atomic_nums).encode("ascii"))
        txn.put("edge_labels".encode("ascii"), str(["None"]+valid_bond_types).encode("ascii"))

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

def safe_index(l, e):
    """
    Return index of element e in list l. If e is not present, return the last index
    """
    try:
        return l.index(e)
    except:
        return len(l) - 1


def smiles2graph(smiles, max_size=32):
    RDLogger.DisableLog('rdApp.*')
    mol = MolFromSmiles(smiles)
    if mol is None:
        return None
    node_labels = []
    for atom in mol.GetAtoms():
        node_labels.append(safe_index(valid_atomic_nums, atom.GetAtomicNum()))
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

        edge_labels.append(safe_index(valid_bond_types, bondtype)+1)
        edge_labels.append(safe_index(valid_bond_types, bondtype)+1)

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
            
            add_labels_to_db(env_split)    
            
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
