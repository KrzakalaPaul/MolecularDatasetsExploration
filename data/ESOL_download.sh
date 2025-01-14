# URL
URL="https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/delaney-processed.csv"

# Download raw files
echo "Downloading raw files"
wget $URL -O raw/ESOL.csv

# Process raw files
echo "Processing raw files"
python ./scripts/preprocessing_ESOL.py
rm raw/ESOL.csv

# Use RDKit to: 1) Remove invalid smiles, 2) Split the dataset, 3) Convert smiles to graphs
echo "Processing smiles with RDKit..."
python ./utils/smiles_to_graphs.py --dataset_name ESOL --splitter random --split_percentage 0.9 0.05 0.05 --map_size 5000000
