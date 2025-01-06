import requests

"""
max_mw = 300
chunck_size = 100
pointer = 0
factor = 0.5

all_smiles = []

while pointer < max_mw:

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/molecular_weight/range/{pointer}/{pointer+chunck_size}/property/SMILES/TXT"
    response = requests.get(url)
    if response.status_code == 200:
        smiles_list = response.text.splitlines()
        all_smiles.extend(smiles_list)
        print(
            f"Retrieved {len(smiles_list)} data  for range {pointer, pointer+chunck_size}"
        )
        pointer += chunck_size
    elif response.status_code == 404:
        print(f"No data found for range {pointer, pointer+chunck_size}, skipping")
    elif response.status_code == 504:
        print(
            f"Timout error for range{pointer, pointer+chunck_size}, reducing chunk size"
        )
        chunck_size = int(chunck_size * factor)
    else:
        print(
            f"Error {response.status_code} for range {pointer, pointer+chunck_size}, skipping"
        )
        pointer += 1

    print("")
    print("Total smiles retrieved:", len(all_smiles))
    print("Next range:", pointer, pointer + chunck_size)
    print("")
"""

max_mw = 400
pointer = 300

all_smiles = []

while pointer < max_mw:

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/molecular_weight/range/{pointer}/{pointer+1}/property/SMILES/TXT"
    response = requests.get(url)
    if response.status_code == 200:
        smiles_list = response.text.splitlines()
        all_smiles.extend(smiles_list)
        print(f"Retrieved {len(smiles_list)} data  for mw = {pointer}")
    elif response.status_code == 404:
        print(f"No data found for mw = {pointer}, skipping")
    elif response.status_code == 504:
        print(f"Timout error for mw = {pointer}, skipping")
    else:
        print(f"Error {response.status_code} for mw = {pointer}, skipping")
    pointer += 1

    print("")
    print("Total smiles retrieved:", len(all_smiles))
    print("")
