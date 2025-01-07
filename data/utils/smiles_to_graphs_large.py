from smiles_to_graphs import smiles2graph
import pickle
from numpy import random
import argparse
import lmdb
import os 
import pandas as pd

def add_smiles_list(env,smiles_list,train_percentage,valid_percentage):
    
    n_invalid = 0
    n_train = 0
    n_valid = 0
    
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
                data = pickle.dumps(graph)
                split = random.choice(["train", "valid"], p=[train_percentage, valid_percentage])
                key = split+f"_{i}"
                txn.put(key.encode("ascii"), data)
                if split == "train":
                    n_train += 1
                else:
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
    
    file = f"graphs/{dataset_name}.lmdb"

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
        map_size=1099511627776
    )
        
    dir = f'smiles/{dataset_name}'
    files = os.listdir(dir)

    from tqdm import tqdm
    from multiprocessing import Pool

    n_threads = 8

    if n_threads == 1:
        
        n_invalid_total = 0
        n_train_total = 0
        n_valid_total = 0

        for file in tqdm(files):
            smiles_list = pd.read_csv(os.path.join(dir, file)).values[:, 0]
            n_invalid, n_train, n_valid = add_smiles_list(env, smiles_list, train_percentage=train_percentage, valid_percentage=valid_percentage)
            n_invalid_total += n_invalid
            n_train_total += n_train
            n_valid_total += n_valid
    else:
        
        def process_file(file):
            smiles_list = pd.read_csv(os.path.join(dir, file)).values[:, 0]
            return add_smiles_list(env, smiles_list, train_percentage=train_percentage, valid_percentage=valid_percentage)
        
        with Pool(n_threads) as p:
            results = list(tqdm(p.imap(process_file, files), total=len(files)))
            
        n_invalid_total = sum([r[0] for r in results])
        n_train_total = sum([r[1] for r in results])
        n_valid_total = sum([r[2] for r in results])
        
    print(f"Total number of invalid SMILES: {n_invalid_total}")
    print(f"Total number of training graphs: {n_train_total}")
    print(f"Total number of validation graphs: {n_valid_total}")
    
    with env.begin(write=True) as txn:
        txn.put("train_size".encode("ascii"), pickle.dumps(n_train_total))
        txn.put("valid_size".encode("ascii"), pickle.dumps(n_valid_total))
