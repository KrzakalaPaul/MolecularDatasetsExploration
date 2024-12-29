#!/bin/bash

# URL of the zip file
URL="https://figshare.com/ndownloader/files/47535647"

# Download the zip file
wget $URL -O downloaded_file.zip

# Unzip the downloaded file
unzip downloaded_file.zip -d ./unzipped_files

# Move the unzipped files to the data directory
mv unzipped_files/QM40\ dataset/QM40_main.csv QM40.csv

# Clean up
rm downloaded_file.zip
rm -r unzipped_files

# Run preprocessing script
python preprocessing_QM40.py


