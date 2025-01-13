import pandas as pd
import argparse
import os

# Argument parser for dataset size
parser = argparse.ArgumentParser(description="Preprocess ZINC dataset")
parser.add_argument("--size", type=str, required=True)
parser.add_argument("--chunk_size", type=int, default=1000000, help="Chunk size for reading the data")

args = parser.parse_args()
size = args.size
chunk_size = args.chunk_size    

# Load and process SMILES in chunks to avoid out of memory error
chunk_iter = pd.read_csv(f"raw/ZINC{size}.csv", chunksize=chunk_size)
os.makedirs(f"smiles/ZINC{size}", exist_ok=True)

for chunk_id, chunk in enumerate(chunk_iter):
    chunk.drop(columns=["zinc_id","purchasable","tranche_name"], inplace=True)
    chunk.to_csv(f"smiles/ZINC{size}/{chunk_id}.csv", index=False)
