import pandas as pd
import argparse

# Argument parser for dataset size
parser = argparse.ArgumentParser(description="Preprocess ZINC dataset")
parser.add_argument("--size", type=str, required=True)
args = parser.parse_args()
size = args.size

# Load HIV dataset
df = pd.read_csv(f"raw/ZINC{size}.csv")

# Remove every column except regression target and SMILES
df.drop(columns=["zinc_id","purchasable","tranche_name"], inplace=True)

# Save
df.to_csv("smiles/ZINC{size}.csv", index=False)
