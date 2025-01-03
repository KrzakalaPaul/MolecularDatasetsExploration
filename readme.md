# Datasets

## Large Supervised Datasets (for end2end training)

- **QM9**: Downloaded using [MoleculeNet link](https://moleculenet.org/datasets-1) 
- **QM40**: Downloaded from [Figshare](https://figshare.com/articles/dataset/QM40_A_More_Realistic_QM_Dataset_for_Machine_Learning_in_Molecular_Science/25993060/1?file=47535647)
- **ZINC-250k**: Downloaded from [Kaggle](https://www.kaggle.com/datasets/basu369victor/zinc250k?resource=download)
- **PCBA**: Downloaded using [MoleculeNet link](https://moleculenet.org/datasets-1) 
- **Alchemy**: Downloaded on [Hugging Face](https://huggingface.co/datasets/graphs-datasets/alchemy) + rdkit to get the smiles

## Unsupervised Datasets (for pretraining)

- **ZINC 20**: Select tranches manually from [ZINC 20](https://zinc20.docking.org/) + run script
- **PubChem**: Using [PubChemPy](https://pubchempy.readthedocs.io/en/latest/)
- **GDBMedChem**: (TO DO)
- **GDB-N**: (TO DO)

## Small Supervised Datasets (for transfer learning)

- **MoleculeNet**: Provides a full suite of tasks

## Notes

- Alchemy < GDBMedChem < GDB-17
- QM40 < ZINC 20