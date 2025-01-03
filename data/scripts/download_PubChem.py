import pubchempy as pcp
import csv

def download_smiles_by_heavy_atoms(max_heavy_atoms, output_file):
    """
    Downloads SMILES strings for molecules with a specified maximum number of heavy atoms.
    
    Parameters:
    - max_heavy_atoms: Maximum number of heavy atoms (e.g., 10).
    - output_file: Path to save the SMILES strings (CSV format).
    """
    # Open the file to save results
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["CID", "SMILES", "Molecular Formula"])  # Write header

        # Iterate through heavy atom counts up to max_heavy_atoms
        for num_atoms in range(1, max_heavy_atoms + 1):
            print(f"Searching for molecules with {num_atoms} heavy atoms...")
            # Query PubChem for molecules with the given heavy atom count
            compounds = pcp.get_compounds(f"heavy_atom_count={num_atoms}", "query")

            # Write the SMILES strings and other details to the file
            for compound in compounds:
                if compound.isomeric_smiles:  # Ensure SMILES is available
                    writer.writerow([compound.cid, compound.isomeric_smiles, compound.molecular_formula])
                    print(f"Saved CID {compound.cid}: {compound.isomeric_smiles}")

    print(f"SMILES strings saved to {output_file}")

# Parameters
MAX_HEAVY_ATOMS = 10
OUTPUT_FILE = "molecules_smiles.csv"

# Execute the function
download_smiles_by_heavy_atoms(MAX_HEAVY_ATOMS, OUTPUT_FILE)