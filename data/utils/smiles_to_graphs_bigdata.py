from smiles_to_graphs import smiles2graph, open_db
import pickle
from numpy import random
import argparse
import os 
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
import lmdb

def format_db(env, n_chunks):
    i = 0
    with env.begin(write=True) as txn:
        for chunk_idx in range(n_chunks):
            j = 0
            key = f"{chunk_idx}/{j}".encode("ascii")
            value = txn.get(key)
            
            while value is not None:
                
                new_key = f"{i}".encode("ascii")
                txn.put(new_key, value)
                txn.delete(key)
                
                i += 1
                j += 1
                key = f"{chunk_idx}/{j}".encode("ascii")
                value = txn.get(key)
        txn.put("size".encode("ascii"), str(i).encode("ascii"))
            
def add_smiles_list(env_train, env_valid, smiles_list,train_percentage,valid_percentage,chunk_idx):
    
    n_invalid = 0
    n_train = 0
    n_valid = 0
    
    with env_train.begin(write=True) as txn_train, env_valid.begin(write=True) as txn_valid:
        
        n_invalid = 0
        for smiles in smiles_list:

            # Convert SMILES to graph
            graph = smiles2graph(smiles)

            # If SMILES gives valid molecule save it, otherwise skip
            if graph is None:
                n_invalid += 1
                continue
            else:
                data = pickle.dumps(graph)
                split = random.choice(["train", "valid"], p=[train_percentage, valid_percentage])
                if split == "train":
                    key = f"{chunk_idx}/{n_train}".encode("ascii")
                    txn_train.put(key, data)
                    n_train += 1
                else:
                    key = f"{chunk_idx}/{n_valid}".encode("ascii")
                    txn_valid.put(key, data)
                    n_valid += 1
    
    return n_invalid, n_train, n_valid

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
        "--split_percentage",
        type=float,
        nargs=2,
        required=True,
        help="Split percentages for train and validation sets.",
    )
    parser.add_argument("--n_threads", type=int, default=8, help="Number of threads.")
    args = parser.parse_args()
    
    dataset_name = args.dataset_name
    train_percentage, valid_percentage = args.split_percentage
    n_threads = args.n_threads  
    
    path = f"graphs/{dataset_name}"
    # Create the database
    env_train = open_db(path, "train")
    env_valid = open_db(path, "valid")
        
    smiles_path = f"smiles/{dataset_name}"
    smiles_files = os.listdir(smiles_path)

    if n_threads == 1:
        
        n_invalid_total = 0
        n_train_total = 0
        n_valid_total = 0
        
        for idx in tqdm(range(len(smiles_files))):
            file = smiles_files[idx]
            smiles_list = pd.read_csv(os.path.join(smiles_path, file)).values[:, 0]
            n_invalid, n_train, n_valid = add_smiles_list(env_train, env_valid, smiles_list, train_percentage=train_percentage, valid_percentage=valid_percentage, chunk_idx=idx)
            n_invalid_total += n_invalid
            n_train_total += n_train
            n_valid_total += n_valid
    else:
        
        def process_file(idx):
            file = smiles_files[idx]
            smiles_list = pd.read_csv(os.path.join(smiles_path, file)).values[:, 0]
            result = add_smiles_list(
                env_train, env_valid, 
                smiles_list, 
                train_percentage=train_percentage, 
                valid_percentage=valid_percentage, 
                chunk_idx=idx
            )
            return result  
            
        with Pool(n_threads) as p:
            results = list(tqdm(p.imap(process_file, range(len(smiles_files))), total=len(smiles_files)))

            
        n_invalid_total = sum([r[0] for r in results])
        n_train_total = sum([r[1] for r in results])
        n_valid_total = sum([r[2] for r in results])
        
    print(f"Total number of invalid SMILES: {n_invalid_total}")
    print(f"Total number of training graphs: {n_train_total}")
    print(f"Total number of validation graphs: {n_valid_total}")
    
    
    format_db(env_train, n_chunks=len(smiles_files))
    format_db(env_valid, n_chunks=len(smiles_files))
    
    