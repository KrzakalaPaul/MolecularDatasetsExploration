#!/bin/bash

# URL
URL="https://figshare.com/ndownloader/files/47535647"

# Download 
echo "Downloading raw files"
wget $URL -O raw/QM40_compressed.zip
unzip raw/QM40_compressed.zip -d ./raw/QM40_uncompressed
mv raw/QM40_uncompressed/QM40\ dataset/QM40_main.csv raw/QM40.csv
rm raw/QM40_uncompressed -r

# Preprocess
echo "Preprocessing raw files"
python ./scripts/preprocessing_QM40.py

# Split (and remove unvalid smiles)
echo "Split datasets and remove invalid smiles"
python ./utils/split.py --dataset_name QM40 --splitter random --split_percentage 0.9 0.05 0.05

# Convert to graphs 
echo "Convert smiles to graphs with RDKit"
python ./utils/smiles_to_graphs.py --dataset_name QM40_train --map_size_in_Ko 1000000
python ./utils/smiles_to_graphs.py --dataset_name QM40_valid --map_size_in_Ko 100000
python ./utils/smiles_to_graphs.py --dataset_name QM40_test --map_size_in_Ko 100000

# Clean up
echo "Clean up"
rm raw/QM40.csv
rm smiles/QM40_train.csv
rm smiles/QM40_valid.csv
rm smiles/QM40_test.csv
