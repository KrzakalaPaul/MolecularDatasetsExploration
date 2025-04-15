#!/bin/bash

# URL
URL="https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/CID-SMILES.gz"

# Download raw files
if [ ! -f data/raw/PUBCHEM.csv ]; then
    echo "Downloading raw files"
    wget $URL -O data/raw/PUBCHEM.csv.gz
    gzip data/raw/PUBCHEM.csv.gz -d
else
    echo "File already exists, skipping download"
fi

# Process raw files 
python PUBCHEM_preprocessing.py --n_smiles_max 10000