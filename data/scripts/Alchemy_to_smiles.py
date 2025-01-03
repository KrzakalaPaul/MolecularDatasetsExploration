import pandas as pd
from rdkit import Chem
import rdkit

feat_to_atomic_num = {0: 6, 1: 7, 2: 8, 3: 16, 4: 9, 5: 17}
feat_to_bond_type = {0: Chem.BondType.SINGLE, 1: Chem.BondType.AROMATIC, 2: Chem.BondType.DOUBLE, 3: Chem.BondType.TRIPLE}
    

# Convert edge_index and node_feat to a molecule
def create_molecule(edge_index, node_feat, edge_attr):
    
    # Mapping from atomic number to atom type (order: C, N, O, S, F, Cl)
    mol = Chem.RWMol()
    atom_map = {}
    
    # Add atoms
    for i, feat in enumerate(node_feat):
        feat = int(feat.argmax())
        atomic_num = feat_to_atomic_num[feat]
        atom = Chem.Atom(atomic_num)  # Assuming one-hot encoding for atom types
        atom_idx = mol.AddAtom(atom)
        atom_map[i] = atom_idx
    
    # Add bonds
    for start, end, type in zip(edge_index[0], edge_index[1], edge_attr):
        type = int(type.argmax())
        bond_type = feat_to_bond_type[type]
        if mol.GetBondBetweenAtoms(atom_map[start], atom_map[end]) is None:
            mol.AddBond(atom_map[start], atom_map[end], bond_type)
    
    return mol

def get_smiles(mol):
    return Chem.MolToSmiles(mol)

def is_valid(mol):
    # Check if the molecule is valid
    if mol is not None and Chem.SanitizeMol(mol, catchErrors=True) == Chem.SanitizeFlags.SANITIZE_NONE:
        return 1
    else:
        return 0
    
def sanitize(mol):
    return Chem.SanitizeMol(mol, catchErrors=True)

if __name__ == "__main__":
    
    # Load the dataset
    df = pd.read_parquet("hf://datasets/graphs-datasets/alchemy/data/full-00000-of-00001-0d58e2f53308c508.parquet")
    
    # Get smiles for each molecule
    smiles = []
    valids = 0
    for i in range(len(df)):
        rdkit.RDLogger.DisableLog('rdApp.*')
        mol = create_molecule(df.edge_index[i], df.node_feat[i], df.edge_attr[i])
        if is_valid(mol):
            valids += 1
        else:
            sanitize(mol)
        smiles.append(get_smiles(mol))
    print(f"Valid molecules: {valids}/{len(df)}")
    
    # Format csv
    columns = {"smiles": smiles}
    for i in range(12):
        columns[f"y{i}"] = df['y'].apply(lambda x: x[0][i])
    csv = pd.DataFrame(columns)
    
    # Save the csv
    csv.to_csv("alchemy.csv", index=False)