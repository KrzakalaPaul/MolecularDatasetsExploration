from .smiles_to_graphs import smiles2graph
import pickle
from numpy import random

def add_smiles_list(env,smiles_list,train_percentage,test_percentage):
    
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
                split = random.choice(["train", "valid"], p=[train_percentage, test_percentage])
                key = split+f"_{i}"
                txn.put(key.encode("ascii"), data)
    
    return n_invalid