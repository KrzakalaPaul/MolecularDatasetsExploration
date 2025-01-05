#!/bin/bash

# URL
URL="https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/pcba.csv.gz"

# Download raw files
echo "Downloading raw files"
wget $URL -O raw/pcba.csv.gz
unzip raw/pcba.csv.gz -d raw
mv raw/pcba.csv smiles/PCBA.csv

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs.py --dataset_name PCBA --splitter random --split_percentage 0.9 0.05 0.05 --map_size_in_Ko 4000000
