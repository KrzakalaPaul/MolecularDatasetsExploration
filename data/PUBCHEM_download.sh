#!/bin/bash

# Download all smilles by chuncks
echo "Downloading SMILES files (this may take a while)"
python ./scripts/download_pubchem.py --chunk_size 1000000
