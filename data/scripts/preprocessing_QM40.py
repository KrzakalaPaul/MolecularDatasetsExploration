import pandas as pd

df = pd.read_csv('QM40.csv')

# Remove every column except regression target and SMILES   
df = df.drop(columns=['Zinc_id'])

# Rename "smile" column to "smiles"
df = df.rename(columns={'smile': 'smiles'})

# Save the preprocessed data
df.to_csv('QM40.csv', index=False)