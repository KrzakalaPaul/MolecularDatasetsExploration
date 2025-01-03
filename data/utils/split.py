import argparse
import pandas as pd
import numpy as np
from rdkit_utils import is_valid_smiles, get_scaffold


class Splitter:

    def __init__(self, train_percentage, valid_percentage, test_percentage):

        if train_percentage + valid_percentage + test_percentage != 1.0:
            raise ValueError("Train, validation, and test percentages must sum to 1.0")

        self.train_percentage = train_percentage
        self.valid_percentage = valid_percentage
        self.test_percentage = test_percentage

    def split_indices(self, dataframe):
        raise NotImplementedError

    def __call__(self, dataframe):
        train_indices, valid_indices, test_indices = self.split_indices(dataframe)
        train = dataframe.iloc[train_indices]
        valid = dataframe.iloc[valid_indices]
        test = dataframe.iloc[test_indices]
        return train, valid, test


class RandomSplitter(Splitter):

    def split_indices(self, dataframe):
        train_end = int(self.train_percentage * len(dataframe))
        valid_end = int(
            (self.train_percentage + self.valid_percentage) * len(dataframe)
        )

        shuffled_indices = np.random.permutation(len(dataframe))
        train_indices = shuffled_indices[:train_end]
        valid_indices = shuffled_indices[train_end:valid_end]
        test_indices = shuffled_indices[valid_end:]

        return train_indices, valid_indices, test_indices


class ScaffoldSplitter(Splitter):

    def get_scaffold_sets(self, dataframe):

        smiles = dataframe["smiles"].values
        scaffolds = {}

        for ind, smile in enumerate(smiles):
            scaffold = get_scaffold(smile)
            if scaffold is not None:
                if scaffold not in scaffolds:
                    scaffolds[scaffold] = [ind]
                else:
                    scaffolds[scaffold].append(ind)

        scaffolds = {key: sorted(value) for key, value in scaffolds.items()}
        scaffold_sets = [
            scaffold_set
            for (scaffold, scaffold_set) in sorted(
                scaffolds.items(), key=lambda x: (len(x[1]), x[1][0]), reverse=True
            )
        ]
        return scaffold_sets

    def split_indices(self, dataframe):

        scaffold_sets = self.get_scaffold_sets(dataframe)
        train_indices, valid_indices, test_indices = [], [], []

        for scaffold_set in scaffold_sets:
            if len(train_indices) + len(scaffold_set) <= self.train_percentage * len(
                dataframe
            ):
                train_indices += scaffold_set
            elif len(valid_indices) + len(scaffold_set) <= (
                self.train_percentage + self.valid_percentage
            ) * len(dataframe):
                valid_indices += scaffold_set
            else:
                test_indices += scaffold_set

        return train_indices, valid_indices, test_indices


def check_valid_smiles(smiles):

    invalid_indices = []
    for idx, smile in enumerate(smiles):
        if not is_valid_smiles(smile):
            invalid_indices.append(idx)

    return invalid_indices


if __name__ == "__main__":

    def parse_arguments():
        parser = argparse.ArgumentParser(
            description="Parse command line arguments for dataset splitting."
        )
        parser.add_argument(
            "--dataset_name",
            type=str,
            required=True,
            help="Raw dataset name. Should be in raw/[dataset_name].csv",
        )
        parser.add_argument(
            "--splitter",
            type=str,
            required=True,
            choices=["random", "scaffold"],
            help="Type of splitter to use.",
        )
        parser.add_argument(
            "--split_percentage",
            type=float,
            nargs=3,
            required=True,
            help="Split percentages for train, validation, and test sets.",
        )

        args = parser.parse_args()
        return args

    args = parse_arguments()

    csv_path = f"raw/{args.dataset_name}.csv"
    csv = pd.read_csv(csv_path)

    invalid_indices = check_valid_smiles(csv["smiles"])

    print(
        f"Found {len(invalid_indices)} invalid SMILES strings. ({len(invalid_indices)/len(csv)*100:.2f}%)"
    )

    # Remove invalid SMILES strings
    csv = csv.drop(invalid_indices)

    if args.splitter == "random":
        splitter = RandomSplitter(*args.split_percentage)
    elif args.splitter == "scaffold":
        splitter = ScaffoldSplitter(*args.split_percentage)

    # Split the dataset
    train, valid, test = splitter(csv)

    # Save the split datasets
    train.to_csv(f"smiles/{args.dataset_name}_train.csv", index=False)
    valid.to_csv(f"smiles/{args.dataset_name}_valid.csv", index=False)
    test.to_csv(f"smiles/{args.dataset_name}_test.csv", index=False)
