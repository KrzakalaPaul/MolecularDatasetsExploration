#!/bin/bash

# Download all smilles by chuncks
echo "Downloading SMILES files (this can take approximately 1 hour)"
python ./scripts/download_pubchem.py --chunk_size 1000000

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs_large.py --dataset_name PUBCHEM --split_percentage 0.9 0.01 