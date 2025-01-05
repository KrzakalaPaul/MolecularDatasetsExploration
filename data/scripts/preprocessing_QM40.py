import pandas as pd

# Load QM40 dataset
df = pd.read_csv("raw/QM40.csv")

# Remove every column except regression target and SMILES
df.drop(columns=["Zinc_id"], inplace=True)
df = df.rename(columns={"smile": "smiles"})

# Save
df.to_csv("smiles/QM40.csv", index=False)
