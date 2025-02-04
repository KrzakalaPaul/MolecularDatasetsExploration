from smiles_to_graphs import smiles2graph, open_db, add_labels_to_db
import pickle
from numpy import random
import argparse
import os 
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
import lmdb
from multiprocessing import cpu_count

def add_size_to_db(env, size):
    with env.begin(write=True) as txn:
        txn.put("size".encode("ascii"), str(size).encode("ascii"))
        
def get_size_from_db(env):
    with env.begin() as txn:
        return int(txn.get("size".encode("ascii")).decode("ascii"))

def concat_db(env, env_to_concat):
    previous_size = get_size_from_db(env)
    with env.begin(write=True) as txn1:
        size_to_add = get_size_from_db(env_to_concat)
        with env_to_concat.begin(write=True) as txn2:
            for i in range(size_to_add):
                data = txn2.get(f"{i}".encode("ascii"))
                txn1.put(f"{previous_size+i}".encode("ascii"), data)
    add_size_to_db(env, previous_size + size_to_add)
            
def add_smiles_list(env_train, env_valid, smiles_list,train_percentage,valid_percentage):
    
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
                    key = f"{n_train}".encode("ascii")
                    txn_train.put(key, data)
                    n_train += 1
                else:
                    key = f"{n_valid}".encode("ascii")
                    txn_valid.put(key, data)
                    n_valid += 1
        
    add_size_to_db(env_train, n_train)
    add_size_to_db(env_valid, n_valid)
    
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
   
    args = parser.parse_args()
    
    dataset_name = args.dataset_name
    train_percentage, valid_percentage = args.split_percentage
    n_threads = cpu_count()
    
    smiles_path = f"smiles/{dataset_name}"
    smiles_files = os.listdir(smiles_path)

    path = f"graphs/{dataset_name}"
    if n_threads == 1:
        
        n_invalid_total = 0
        n_train_total = 0
        n_valid_total = 0
        
        for idx in tqdm(range(len(smiles_files))):
            file = smiles_files[idx]
            smiles_list = pd.read_csv(os.path.join(smiles_path, file)).values[:, 0]

            env_train = open_db(path, f"train_{idx}")
            env_valid = open_db(path, f"valid_{idx}")
            
            n_invalid, n_train, n_valid = add_smiles_list(env_train, env_valid, smiles_list, train_percentage=train_percentage, valid_percentage=valid_percentage)
            n_invalid_total += n_invalid
            n_train_total += n_train
            n_valid_total += n_valid
            
            env_train.close()
            env_valid.close()
    else:
        
        def process_file(idx):
            file = smiles_files[idx]
            smiles_list = pd.read_csv(os.path.join(smiles_path, file)).values[:, 0]
            env_train = open_db(path, f"train_{idx}")
            env_valid = open_db(path, f"valid_{idx}")
            result = add_smiles_list(
                env_train, env_valid, 
                smiles_list, 
                train_percentage=train_percentage, 
                valid_percentage=valid_percentage
            )
            env_train.close()
            env_valid.close()
            return result  
            
        with Pool(n_threads) as p:
            results = list(tqdm(p.imap(process_file, range(len(smiles_files))), total=len(smiles_files)))

        n_invalid_total = sum([r[0] for r in results])
        n_train_total = sum([r[1] for r in results])
        n_valid_total = sum([r[2] for r in results])
        
    print(f"Total number of invalid SMILES: {n_invalid_total}")
    print(f"Total number of training graphs: {n_train_total}")
    print(f"Total number of validation graphs: {n_valid_total}")
    
    # Concatenate all the chunks
    env_train = open_db(path, "train")
    add_size_to_db(env_train, 0)
    add_labels_to_db(env_train)
    env_valid = open_db(path, "valid")
    add_size_to_db(env_valid, 0)
    add_labels_to_db(env_valid)
        
    previous_size = int(env_train.begin().get("size".encode("ascii")).decode("ascii"))
    
    for idx in range(len(smiles_files)):
        env_train_chunk = open_db(path, f"train_{idx}", delete=False)
        concat_db(env_train, env_train_chunk)
        env_train_chunk.close()
        os.remove(f"{path}/train_{idx}.lmdb")
        
        env_valid_chunk = open_db(path, f"valid_{idx}", delete=False)
        concat_db(env_valid, env_valid_chunk)
        env_valid_chunk.close()
        os.remove(f"{path}/valid_{idx}.lmdb")
