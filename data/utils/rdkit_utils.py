from rdkit import Chem
from typing import Union
from rdkit.Chem.Scaffolds.MurckoScaffold import MurckoScaffoldSmiles


def is_valid_smiles(smiles):
    """
    Check if a SMILES string is valid.

    Args:
        smiles (str): SMILES string to check.

    Returns:
        bool: Whether the SMILES string is valid.
    """
    return Chem.MolFromSmiles(smiles) is not None


def get_scaffold(smiles: str, include_chirality: bool = False) -> Union[str, None]:
    """Compute the Bemis-Murcko scaffold for a SMILES string.

    Bemis-Murcko scaffolds are described in DOI: 10.1021/jm9602928.
    They are essentially that part of the molecule consisting of
    rings and the linker atoms between them.

    Paramters
    ---------
    smiles: str
        SMILES
    include_chirality: bool, default False
        Whether to include chirality in scaffolds or not.

    Returns
    -------
    str
        The MurckScaffold SMILES from the original SMILES

    References
    ----------
    .. [1] Bemis, Guy W., and Mark A. Murcko. "The properties of known drugs.
        1. Molecular frameworks." Journal of medicinal chemistry 39.15 (1996): 2887-2893.

    Note
    ----
    This function requires RDKit to be installed.
    """

    return MurckoScaffoldSmiles(smiles, includeChirality=include_chirality)
