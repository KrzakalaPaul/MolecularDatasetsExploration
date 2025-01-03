#!/bin/bash

# URL
URL="https://storage.googleapis.com/kaggle-data-sets/2028384/3362731/compressed/250k_rndm_zinc_drugs_clean_3.csv.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20250103%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250103T172212Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=460cf06fb679ee2226f35d6498a91c15aefa5c647218e5ee44d5c790b32b1e7e8fb1754ff8b7743d12957e7196a112aa6265883b8424c9902c1683ab99653b567371ab580e847829682b75df6f4bbf9149cd9ed5de4c12535ff141aefd9397f32ce3f29fb0fa6fee06ff4c8176adf8bb91b92b49d3fccf9605b7c8998078bb0bdf59500ad0521719746e34204eb098699a03c409d21d248982828546351db750f68935a92bb229e5c4a0cbf0ede5bba0f6c770ef15ae978b229cddb8f18e7c6396b899a426e59981020cbc126e20b9ae7f93b823f11e974e6fc72ae68fa8413a5e3bc1e2544c49b3caaa14af67fa02d970c10cb36b32287c93c8ad99cdb45eb5"

# Download 
echo "Downloading raw files"
wget $URL -O raw/ZINC250_compressed.zip
unzip raw/ZINC250_compressed.zip -d ./raw/ZINC250_uncompressed
mv raw/ZINC250_uncompressed/250k_rndm_ZINC250_drugs_clean_3.csv raw/ZINC250.csv
rm raw/ZINC250_uncompressed -r

# Split (and remove unvalid smiles)
echo "Split datasets and remove invalid smiles"
python ./utils/split.py --dataset_name ZINC250 --splitter random --split_percentage 0.9 0.05 0.05

# Convert to graphs 
echo "Convert smiles to graphs with RDKit"
python ./utils/smiles_to_graphs.py --dataset_name ZINC250_train --map_size_in_Ko 2000000
python ./utils/smiles_to_graphs.py --dataset_name ZINC250_valid --map_size_in_Ko 200000
python ./utils/smiles_to_graphs.py --dataset_name ZINC250_test --map_size_in_Ko 200000

# Clean up
echo "Clean up"
rm raw/ZINC250.csv
rm smiles/ZINC250_train.csv
rm smiles/ZINC250_valid.csv
rm smiles/ZINC250_test.csv
