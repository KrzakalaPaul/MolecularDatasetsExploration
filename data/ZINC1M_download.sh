#!/bin/bash

# URL
URL="https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/zinc15_1M_2D.tar.gz"

# Download raw files
echo "Downloading raw files"
wget --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" $URL -O raw/ZINC1M.tar.gz
gzip raw/ZINC1M.tar.gz -d 
tar -xvf raw/ZINC1M.tar -C raw/
mv raw/zinc15_1M_2D.csv raw/ZINC1M.csv
rm raw/ZINC1M.tar

# Convert to smiles csv
echo "Preprocessing raw files..."
python ./scripts/preprocessing_ZINCM.py --size 1M --chunk_size 100000
rm raw/ZINC1M.csv

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs_bigdata.py --dataset_name ZINC1M --split_percentage 0.99 0.01 --n_threads 8