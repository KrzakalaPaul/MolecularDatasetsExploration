import pandas as pd
import argparse

size = '250k'

# Load HIV dataset
df = pd.read_csv(f"raw/ZINC{size}.csv")

# Remove every column except regression target and SMILES
df.drop(columns=["zinc_id","purchasable","tranche_name"], inplace=True)

# Save
df.to_csv(f"smiles/ZINC{size}.csv", index=False)
