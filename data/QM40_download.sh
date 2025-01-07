#!/bin/bash

# URL
URL="https://figshare.com/ndownloader/files/47535647"

# Download raw files
echo "Downloading raw files"
wget $URL -O raw/QM40_compressed.zip
unzip raw/QM40_compressed.zip -d ./raw/QM40_uncompressed
mv raw/QM40_uncompressed/QM40\ dataset/QM40_main.csv raw/QM40.csv
rm raw/QM40_uncompressed -r
rm raw/QM40_compressed.zip

# Convert to smiles csv
echo "Preprocessing raw files"
python ./scripts/preprocessing_QM40.py
rm raw/QM40.csv

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs.py --dataset_name QM40 --splitter random --split_percentage 0.9 0.05 0.05 --map_size 300000000


