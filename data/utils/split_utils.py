import argparse
import pandas as pd
import numpy as np
from rdkit.Chem.Scaffolds.MurckoScaffold import MurckoScaffoldSmiles


class Splitter:

    def __init__(self, train_percentage, valid_percentage, test_percentage):

        assert train_percentage + valid_percentage + test_percentage == 1

        self.train_percentage = train_percentage
        self.valid_percentage = valid_percentage
        self.test_percentage = test_percentage
        self.indices = []

    def add(self, idx, smiles):
        # Use to add a new data point to the splitter
        self.indices.append(idx)

    def split(self):
        self.train_indices = ...
        self.valid_indices = ...
        self.test_indices = ...


class RandomSplitter(Splitter):

    def split(self):
        np.random.shuffle(self.indices)
        n = len(self.indices)
        n_test = int(self.test_percentage * n)
        n_valid = int(self.valid_percentage * n)
        n_train = n - n_valid - n_test

        self.train_indices = self.indices[:n_train]
        self.valid_indices = self.indices[n_train : n_train + n_valid]
        self.test_indices = self.indices[n_train + n_valid :]


class ScaffoldSplitter(Splitter):

    def __init__(
        self, train_percentage, valid_percentage, test_percentage
    ):
        super().__init__(
            train_percentage, valid_percentage, test_percentage
        )

        self.scaffolds = {}

    def add(self, idx, smiles):
        scaffold = MurckoScaffoldSmiles(smiles)
        if scaffold not in self.scaffolds:
            self.scaffolds[scaffold] = [idx]
        self.scaffolds[scaffold].append(idx)
        self.indices.append(idx)

    def split(self):
        scaffold_indices = list(self.scaffolds.values())
        np.random.shuffle(scaffold_indices)

        self.train_indices = []
        self.valid_indices = []
        self.test_indices = []

        n = len(self.indices)
        n_test = int(self.test_percentage * n)
        n_valid = int(self.valid_percentage * n)
        n_train = n - n_valid - n_test

        for scaffold_group in scaffold_indices:
            if len(self.train_indices) + len(scaffold_group) <= n_train:
                self.train_indices.extend(scaffold_group)
            elif len(self.valid_indices) + len(scaffold_group) <= n_valid:
                self.valid_indices.extend(scaffold_group)
            else:
                self.test_indices.extend(scaffold_group)


if __name__ == "__main__":

    dataset_size = 1000
    train_percentage = 0.8
    valid_percentage = 0.1
    test_percentage = 0.1
    invalid_percentage = 0.1

    splitter = RandomSplitter(train_percentage, valid_percentage, test_percentage)

    for i in range(dataset_size):
        invalid = np.random.rand() < invalid_percentage
        if not invalid:
            splitter.add(i, None)
    splitter.split()

    print(len(splitter.train_indices))
    print(len(splitter.valid_indices))
    print(len(splitter.test_indices))
