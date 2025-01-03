#!/bin/bash

# URL
URL="https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/qm9.csv"

# Download 
echo "Downloading raw files"
wget $URL -O raw/QM9.csv

# Preprocess
echo "Preprocessing raw files"
python ./scripts/preprocessing_QM9.py

# Split (and remove unvalid smiles)
echo "Split datasets and remove invalid smiles"
python ./utils/split.py --dataset_name QM9 --splitter random --split_percentage 0.9 0.05 0.05

# Convert to graphs 
echo "Convert smiles to graphs with RDKit"
python ./utils/smiles_to_graphs.py --dataset_name QM9_train --map_size_in_Ko 100000
python ./utils/smiles_to_graphs.py --dataset_name QM9_valid --map_size_in_Ko 10000
python ./utils/smiles_to_graphs.py --dataset_name QM9_test --map_size_in_Ko 10000

# Clean up
echo "Clean up"
rm raw/QM9.csv
rm smiles/QM9_train.csv
rm smiles/QM9_valid.csv
rm smiles/QM9_test.csv