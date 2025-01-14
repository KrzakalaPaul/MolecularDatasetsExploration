#!/bin/bash

# URL
URL="https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/HIV.csv"

# Download raw files
echo "Downloading raw files"
wget $URL -O raw/HIV.csv

# Convert to smiles csv
echo "Preprocessing raw files"
python ./scripts/preprocessing_HIV.py
rm raw/HIV.csv

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs.py --dataset_name HIV --splitter random --split_percentage 0.9 0.05 0.05 --map_size 350000000


