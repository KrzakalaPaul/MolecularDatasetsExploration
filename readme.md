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

