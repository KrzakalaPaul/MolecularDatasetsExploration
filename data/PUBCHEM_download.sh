#!/bin/bash

# URL
URL="https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/CID-SMILES.gz"

# Download raw files
echo "Downloading raw files"
wget $URL -O raw/PUBCHEM.csv.gz
gzip raw/PUBCHEM.csv.gz -d 

# Split in chuncks 
echo "Processing raw files..."
python ./scripts/preprocessing_PUBCHEM.py --chunk_size 1000000

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs_bigdata.py --dataset_name PUBCHEM --split_percentage 0.99 0.01 