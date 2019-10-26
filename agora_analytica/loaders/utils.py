
from os import getcwd
from os.path import abspath, join

import logging

import pandas as pd
import numpy as np

import string

from .. import instance_path


def _instance_path(f=None):
    """
    Path for file.
    """
    path = [instance_path]
    if f is not None:
        path.append(f)

    return abspath(join(*path))

"""
Name files.

..see:
    https://www.avoindata.fi/data/fi/dataset/none
"""

FIRST_NAMES = _instance_path("etunimitilasto-2019-08-07-vrk.xlsx")
LAST_NAMES = _instance_path("sukunimitilasto-2019-08-07-vrk.xlsx")


def generate_names(count=1, first_names=FIRST_NAMES, last_names=LAST_NAMES):
    """ Generate random names.

    :param count:       How many names to generate.
    :param first_names: Excel file name to read for first names.
    :param last_names:  Excel file name to read for last names.

    :return: list       List of names
    """

    names = []

    try:
        data_first = pd.read_excel(first_names)
        data_last = pd.read_excel(last_names)

        # Calculate propabilites for selection.
        weighted_first = data_first.iloc[:, 1] / data_first.iloc[:, 1].sum()
        weighted_last = data_last.iloc[:, 1] / data_last.iloc[:, 1].sum()

        sampled = zip(
            np.random.choice(data_first.iloc[:, 0], size=count, p=weighted_first),
            np.random.choice(data_last.iloc[:, 0], size=count, p=weighted_last)
        )

        names = [" ".join(i) for i in sampled]
    except FileNotFoundError as e:
        logging.debug("Generating dummy names, could not find file:", e)
        names = generate_dummy_names(count)

    return names


def generate_dummy_names(count=1):
    """
    Generate list of random strings.
    """
    return [" ".join([_generate_dummy_string(), _generate_dummy_string()]) for _ in range(count)]


def _generate_dummy_string():
    """
    Generate random string
    """
    chars = list(string.ascii_lowercase)

    return "".join(np.random.choice(chars) for x in range(np.random.randint(3, 12))).capitalize()


if __name__ == "__main__":
    print(generate_names(5))
