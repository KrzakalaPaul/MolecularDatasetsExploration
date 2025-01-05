import pandas as pd

# Load QM9 dataset
df = pd.read_csv("raw/QM9.csv")

# Remove every column except regression target and SMILES
df.drop(columns=["mol_id"], inplace=True)

# Save
df.to_csv("smiles/QM9.csv", index=False)
