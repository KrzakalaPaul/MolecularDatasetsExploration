import pandas as pd

# Load HIV dataset
df = pd.read_csv("raw/HIV.csv")

# Remove every column except regression target and SMILES
df.drop(columns=["activity"], inplace=True)

# Save
df.to_csv("smiles/HIV.csv", index=False)
