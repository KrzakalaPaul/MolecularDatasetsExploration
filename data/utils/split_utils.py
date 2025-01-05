import argparse
import pandas as pd
import numpy as np
from rdkit.Chem.Scaffolds.MurckoScaffold import MurckoScaffoldSmiles


class OnlineSplitter:

    def __init__(
        self, max_dataset_size, train_percentage, valid_percentage, test_percentage
    ):

        if train_percentage + valid_percentage + test_percentage != 1.0:
            raise ValueError("Train, validation, and test percentages must sum to 1.0")

        self.probs = np.array([train_percentage, valid_percentage, test_percentage])
        self.n_train_max = int(train_percentage * max_dataset_size)
        self.n_train = 0
        self.n_valid_max = int(valid_percentage * max_dataset_size)
        self.n_valid = 0
        self.n_test_max = int(test_percentage * max_dataset_size)
        self.n_test = 0

    def get_random_split(self):
        return np.random.choice(["train", "valid", "test"], p=self.probs)

    def get_split(self, idx, smiles):
        return ...

    def __call__(self, idx=None, smiles=None):
        split = self.get_split(idx, smiles)
        # TO DO: update probs to stay closer to the target split percentages
        return split


class RandomSplitter(OnlineSplitter):

    def get_split(self, idx, smiles):
        split = self.get_random_split()
        return split


class ScaffoldSplitter(OnlineSplitter):

    def __init__(
        self, dataset_size, train_percentage, valid_percentage, test_percentage
    ):
        super().__init__(
            dataset_size, train_percentage, valid_percentage, test_percentage
        )

        self.scaffolds = {}

    def get_split(self, idx, smiles):
        scaffold = MurckoScaffoldSmiles(smiles)
        if scaffold not in self.scaffolds:
            split = self.get_random_split()
            self.scaffolds[scaffold] = split
        else:
            split = self.scaffolds[scaffold]
        return split


if __name__ == "__main__":

    dataset_size = 1000
    train_percentage = 0.8
    valid_percentage = 0.1
    test_percentage = 0.1
    invalid_percentage = 0.1

    splitter = RandomSplitter(
        dataset_size, train_percentage, valid_percentage, test_percentage
    )

    for i in range(dataset_size):
        invalid = np.random.rand() < invalid_percentage
        if not invalid:
            splitter(i)

    print(splitter.n_train)
    print(splitter.n_valid)
    print(splitter.n_test)
