#!/bin/bash

# URL of the zip file
URL="https://storage.googleapis.com/kaggle-data-sets/2028384/3362731/compressed/250k_rndm_zinc_drugs_clean_3.csv.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20241229%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20241229T155214Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=5d0ce67637e71132f9cbb17803dde004eed13bf861bae48ca48ae21746b3e51b1f5ecf11e3f3fd66a0e577a7c289d86d51d90b4e7fae3a866c63692d2f0ac7f090e63f953251ffdbfac4482458a1eb20b4bdf368e7e6c3d657efbd7184a9754c78417b0038ddcc18a8601052e4091e5977f2642413d7e384c3332c93fdd10b1471f12daf6b2c2cc8540c13a15762228b97fc48d8dc444d2ab914548c36cda65ea2d61a1f57855134aee9e71fabba77ef7e130bbbc697c7e945f5a4bc0f6da4405cdbc10e547f52e5f8f3822d94e9d039d8f2696d34e071398afb6c58847302880cf71fa5dd737001e542f4d6c80e50128072b6131cec7dd667f63452c4db2885"

# Download the zip file
wget $URL -O downloaded_file.zip

# Unzip the downloaded file
unzip downloaded_file.zip -d ./unzipped_files

# Move the unzipped files to the data directory
mv unzipped_files/250k_rndm_zinc_drugs_clean_3.csv ZINC250.csv

# Clean up
rm downloaded_file.zip
rm -r unzipped_files

# Run preprocessing script
python preprocessing_ZINC250.py
