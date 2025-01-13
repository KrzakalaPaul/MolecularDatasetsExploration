import pandas as pd

# Load HIV dataset
df = pd.read_csv("raw/BACE.csv")

# Remove every column except regression target and SMILES
df = df[['mol', 'pIC50', 'Class']]
df.rename(columns={'mol': 'smiles'}, inplace=True)

# Save
df.to_csv("smiles/BACE.csv", index=False)
