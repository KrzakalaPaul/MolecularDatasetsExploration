#!/bin/bash

# URL
URL="https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/zinc15_250k_2D.tar.gz"

# Download raw files
echo "Downloading raw files"
wget --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" $URL -O raw/ZINC250k.tar.gz
gzip raw/ZINC250k.tar.gz -d 
tar -xvf raw/ZINC250k.tar -C raw/
mv raw/zinc15_250k_2D.csv raw/ZINC250k.csv
rm raw/ZINC250k.tar

# Convert to smiles csv
echo "Preprocessing raw files..."
python ./scripts/preprocessing_ZINC250k.py 
rm raw/ZINC250k.csv

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs.py --dataset_name ZINC250k --splitter random --split_percentage 0.9 0.05 0.05 --map_size 4000000000
