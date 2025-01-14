#!/bin/bash

# Download ALCHEMY dataset and convery to SMILES
echo "Downloading SMILES files"
python ./scripts/download_ALCHEMY.py

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs.py --dataset_name ALCHEMY --splitter random --split_percentage 0.9 0.05 0.05 --map_size 800000000
