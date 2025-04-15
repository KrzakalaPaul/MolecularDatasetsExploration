import pandas as pd
from utils import smiles2graph as smiles2graph_0
from utils import open_db, add_data_list, write
from functools import partial
from multiprocessing import Pool
from multiprocessing import cpu_count
from tqdm import tqdm
import yaml
from sklearn.model_selection import train_test_split
import argparse

if __name__ == "__main__":
    print("Running PUBCHEM preprocessing script...")
    # Argument parser
    parser = argparse.ArgumentParser(description="PUBCHEM preprocessing script")
    parser.add_argument("--n_smiles_max", type=int, default=1000000, help="Maximum number of SMILES to process")
    parser.add_argument("--train_size", type=float, default=0.9, help="Proportion of data to use for training")
    parser.add_argument("--n_smiles_per_cpu", type=int, default=2048, help="Load smiles by chunks of size n_cpus x n_smiles_per_cpu")
    parser.add_argument("--csv_path", type=str, default='data/raw/PUBCHEM.csv', help="Path to smiles csv file")
    parser.add_argument("--data_path", type=str, default='data/graphs/PUBCHEM', help="Path to smiles csv file")
    args = parser.parse_args()

    # Assign parsed arguments to variables
    train_size = args.train_size
    csv_path = args.csv_path
    data_path = args.data_path
    n_smiles_max = args.n_smiles_max
    n_smiles_per_cpu = args.n_smiles_per_cpu

    # Get smiles2graph function
    with open('smiles2graph_config.yaml', "r") as file:
        smiles2graph_config = yaml.safe_load(file)
    smiles2graph = partial(smiles2graph_0, max_size = smiles2graph_config['max_size'], valid_atomic_nums = smiles2graph_config['valid_atomic_nums'], valid_bond_types = smiles2graph_config['valid_bond_types'])

    # Open lmdb database
    env_train = open_db(data_path, 'train', mapsize=1099511627776, delete=True)
    env_test = open_db(data_path, 'test', mapsize=1099511627776, delete=True)

    # Load smiles csv (by chunks)
    n_threads = cpu_count() 
    chunk_size = n_threads*n_smiles_per_cpu
    n_chunks = n_smiles_max // chunk_size + 1
    chunk_iter = pd.read_csv(csv_path, chunksize=chunk_size, sep='\t',index_col=0, header=None, nrows = n_smiles_max)

    # main loop
    for chunk in tqdm(chunk_iter, total=n_chunks, unit="chunk", desc="Processing smiles by chunks of size {}".format(chunk_size)):
        smiles_list = chunk.iloc[:, 0].values
        # Convert SMILES to graphs using smiles2graph + multiprocessing
        with Pool(processes=n_threads) as pool:
            graphs = list(pool.imap(smiles2graph, smiles_list))
        # Remove invalid graphs
        graphs = [g for g in graphs if g is not None]
        # Split graphs into train and test sets
        graphs_train, graphs_test = train_test_split(graphs, train_size=train_size, random_state=42)
        
        add_data_list(data_list = graphs_train, env = env_train)
        add_data_list(data_list = graphs_test, env = env_test)
        
    # Close lmdb database
    write(env_train, key = 'metadata', value = 'Some metadata')
    write(env_test, key = 'metadata', value = 'Some metadata')
    env_train.close()
    env_test.close()
