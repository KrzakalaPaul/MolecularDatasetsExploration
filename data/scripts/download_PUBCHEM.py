from io import StringIO
from requests import post
import pandas as pd
from tqdm import tqdm
import os
import argparse

def get_smiles(cid_min, cid_max, max_heavy_atom_count = 32):

    cid_list = str(list(range(cid_min, cid_max)))[1:-1]
    cid_list = cid_list.replace(' ', '')
    url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/property/HeavyAtomCount,SMILES/csv'
    data = {'cid': cid_list}
    response = post(url, data=data)
    dataframe = pd.read_csv(StringIO(response.text), index_col=0)
    dataframe = dataframe.dropna()
    dataframe = dataframe[dataframe['HeavyAtomCount'] <= max_heavy_atom_count]
    dataframe.rename(columns={"SMILES": "smiles"}, inplace=True)
    smiles = dataframe['smiles']
    
    return smiles

def exist(cid):
    url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/HeavyAtomCount,SMILES/csv'
    response = post(url)
    dataframe = pd.read_csv(StringIO(response.text), index_col=0)
    return not(dataframe.isnull().values.any())

def binary_search(cid_min, cid_max):
    while cid_min <= cid_max:
        mid = (cid_min + cid_max) // 2
        if exist(mid):
            cid_min = mid + 1
        else:
            cid_max = mid - 1
    return cid_max

def get_largest_cid(cid_min = 100000000, cid_max = 200000000):
    assert(exist(cid_min))
    assert(not exist(cid_max))
    largest_cid = binary_search(cid_min, cid_max)
    assert exist(largest_cid)
    return largest_cid

if __name__ == '__main__':

    os.makedirs('smiles/PUBCHEM', exist_ok=True)

    parser = argparse.ArgumentParser(description='Download SMILES from PubChem.')
    parser.add_argument('--chunk_size', type=int, default=10**6, help='Size of each chunk of CIDs to process.')
    parser.add_argument('--max_heavy_atom_count', type=int, default=32, help='Maximum number of heavy atoms in a molecule.')
    parser.add_argument('--max_dataset_size', type=int, default=None, help='Maximum number of SMILES to collect.')

    args = parser.parse_args()

    chunk_size = args.chunk_size
    max_heavy_atom_count = args.max_heavy_atom_count
    max_dataset_size = args.max_dataset_size
    os.makedirs('smiles/PUBCHEM', exist_ok=True)
    
    largest_cid = 172640030 #get_largest_cid()
    print('largest_cid:', largest_cid)

    stop = False
    pointer = 1
    n_collected = 0
    n_chunks = largest_cid // chunk_size 

    for i in tqdm(range(n_chunks)):
        if max_dataset_size is not None and n_collected >= max_dataset_size:
            break
        cid_min = pointer 
        cid_max = pointer + chunk_size
        smiles = get_smiles(cid_min, cid_max, max_heavy_atom_count = max_heavy_atom_count)
        n_collected += len(smiles)
        smiles.to_csv(f'smiles/PUBCHEM/{cid_min}-{cid_max}.csv', index=False)
        pointer += chunk_size
        print('Total smiles collected:', n_collected)