#!/bin/bash

# URL
URL="https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/zinc15_250K_2D.tar.gz"

# Download raw files
echo "Downloading raw files"
wget --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" $URL -O raw/ZINC250k.tar.gz
gzip raw/ZINC250k.tar.gz -d 
tar -xvf raw/ZINC250k.tar -C raw/ZINC250k
mv raw/zinc15_250K_2D.csv smiles/ZINC250k.csv
rm -r raw/ZINC250k
rm raw/ZINC250k.tar
rm raw/ZINC250k.tar.gz