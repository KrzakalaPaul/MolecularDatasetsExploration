import pandas as pd
import argparse
import os 

def parse_args():
    parser = argparse.ArgumentParser(description="Preprocess PUBCHEM data")
    parser.add_argument("--chunk_size", type=int, default=1000000, help="Chunk size for reading the data")
    return parser.parse_args()

args = parse_args()
chunk_size = args.chunk_size    
# Load and process SMILES in chunks to avoid out of memory error
chunk_iter = pd.read_csv("raw/PUBCHEM.csv", chunksize=chunk_size, sep='\t')

os.makedirs("smiles/PUBCHEM", exist_ok=True)

for chunk_id, chunk in enumerate(chunk_iter):
    chunk.drop(columns=chunk.columns[0], inplace=True)
    chunk.to_csv(f"smiles/PUBCHEM/{chunk_id}.csv", index=False)
