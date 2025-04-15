#!/bin/bash

# URL
URL="https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/CID-SMILES.gz"

# Download raw files
echo "Downloading raw files"
wget $URL -O data/raw/PUBCHEM.csv.gz
gzip data/raw/PUBCHEM.csv.gz -d 
