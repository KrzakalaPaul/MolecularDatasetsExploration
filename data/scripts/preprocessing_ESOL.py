import pandas as pd

# Load HIV dataset
df = pd.read_csv("raw/ESOL.csv")

# Remove every column except regression target and SMILES
df = df[['smiles', 'measured log solubility in mols per litre']]

# Save
df.to_csv("smiles/ESOL.csv", index=False)
