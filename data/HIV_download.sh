#!/bin/bash

# URL
URL="https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/HIV.csv"

# Download 
echo "Downloading raw files"
wget $URL -O raw/HIV.csv

# Preprocess
echo "Preprocessing raw files"
python ./scripts/preprocessing_HIV.py

# Split (and remove unvalid smiles)
echo "Split datasets and remove invalid smiles"
python ./utils/split.py --dataset_name HIV --splitter random --split_percentage 0.9 0.05 0.05

# Convert to graphs 
echo "Convert smiles to graphs with RDKit"
python ./utils/smiles_to_graphs.py --dataset_name HIV_train --map_size_in_Ko 100000
python ./utils/smiles_to_graphs.py --dataset_name HIV_valid --map_size_in_Ko 10000
python ./utils/smiles_to_graphs.py --dataset_name HIV_test --map_size_in_Ko 10000

# Clean up
echo "Clean up"
rm raw/HIV.csv
rm smiles/HIV_train.csv
rm smiles/HIV_valid.csv
rm smiles/HIV_test.csv