import pandas as pd

# Concatenate the splits into one file
splits = {'train': 'train_data.csv', 'validation': 'valid_data.csv', 'test': 'test_data.csv'}
df_train = pd.read_csv("hf://datasets/HR-machine/QM9-Dataset/" + splits["train"])
df_test = pd.read_csv("hf://datasets/HR-machine/QM9-Dataset/" + splits["test"])
df_valid = pd.read_csv("hf://datasets/HR-machine/QM9-Dataset/" + splits["validation"])
df = pd.concat([df_train, df_test, df_valid])

# Remove every column except regression target and SMILES   
df.drop(columns=["mol_id"], inplace=True)

# Save 
df.to_csv("QM9.csv", index=False)