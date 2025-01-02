# Datasets 

Large Supervised Datasets :

QM9, downloaded from https://huggingface.co/datasets/yairschiff/qm9 (Source https://moldis-group.github.io/curatedQM9/ + rdkit)
QM40, downloaded from https://figshare.com/articles/dataset/QM40_A_More_Realistic_QM_Dataset_for_Machine_Learning_in_Molecular_Science/25993060/1?file=47535647
ZINC-250k, downloaded from https://www.kaggle.com/datasets/basu369victor/zinc250k?resource=download
ogbg-molpcba, native on OGB (https://ogb.stanford.edu/docs/graphprop/)
Alchemy (https://huggingface.co/datasets/graphs-datasets/alchemy + rdkit to get the smiles)

Small Supervised Datasets (for transformer learning) :

OGB provides a full suite of tasks

Unsupervised Datasets (for pretraining) :

ZINC 20 from (Select tranches manually from https://zinc20.docking.org/ + run script)
PubChem (Using https://pubchempy.readthedocs.io/en/latest/)
GDBMedChem (?)
GDB-N (?)

Notes: Alchemy < GDBMedChem < GDB-17

TO DO: SMILES -> Precompute input with rdkit -> Save to LMBD

https://github.com/deepmodeling/Uni-Mol/blob/14e7e0e29d1f242ab00e12449a3bab5408180f51/unimol/notebooks/unimol_mol_repr_demo.ipynb
https://github.com/deepmodeling/Uni-Mol/blob/14e7e0e29d1f242ab00e12449a3bab5408180f51/unimol/unimol/data/lmdb_dataset.py
https://stackoverflow.com/questions/53576113/most-efficient-way-to-use-a-large-data-set-for-pytorch