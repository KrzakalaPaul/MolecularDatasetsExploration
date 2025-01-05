#!/bin/bash

# URL
URL="https://storage.googleapis.com/kaggle-data-sets/2028384/3362731/compressed/250k_rndm_zinc_drugs_clean_3.csv.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20250103%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250103T172212Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=460cf06fb679ee2226f35d6498a91c15aefa5c647218e5ee44d5c790b32b1e7e8fb1754ff8b7743d12957e7196a112aa6265883b8424c9902c1683ab99653b567371ab580e847829682b75df6f4bbf9149cd9ed5de4c12535ff141aefd9397f32ce3f29fb0fa6fee06ff4c8176adf8bb91b92b49d3fccf9605b7c8998078bb0bdf59500ad0521719746e34204eb098699a03c409d21d248982828546351db750f68935a92bb229e5c4a0cbf0ede5bba0f6c770ef15ae978b229cddb8f18e7c6396b899a426e59981020cbc126e20b9ae7f93b823f11e974e6fc72ae68fa8413a5e3bc1e2544c49b3caaa14af67fa02d970c10cb36b32287c93c8ad99cdb45eb5"

# Download raw files
echo "Downloading raw files"
wget $URL -O raw/ZINC250_compressed.zip
unzip raw/ZINC250_compressed.zip -d raw
mv raw/250k_rndm_zinc_drugs_clean_3.csv smiles/ZINC250.csv
rm raw/ZINC250.csv
rm raw/ZINC250_compressed -r
rm raw/ZINC250_compressed.zip

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs.py --dataset_name QM9 --splitter random --split_percentage 0.9 0.05 0.05 --map_size_in_Ko 4000000
rm smiles/ZINC250.csv
