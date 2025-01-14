#!/bin/bash

# URL
URL="https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/qm9.csv"

# Download raw files
echo "Downloading raw files"
wget $URL -O raw/QM9.csv

# Convert to smiles csv
echo "Preprocessing raw files..."
python ./scripts/preprocessing_QM9.py
rm raw/QM9.csv

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs.py --dataset_name QM9 --splitter random --split_percentage 0.9 0.05 0.05 --map_size 700000000
