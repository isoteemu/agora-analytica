
from os import getcwd
from os.path import abspath, join

import pandas as pd
import numpy as np

# Get relative dir
_instance_path = lambda f: abspath(join(getcwd(), "instance", f))

""" 
Name files.

..see:
    https://www.avoindata.fi/data/fi/dataset/none
"""

FIRST_NAMES = _instance_path("etunimitilasto-2019-08-07-vrk.xlsx")
LAST_NAMES = _instance_path("sukunimitilasto-2019-08-07-vrk.xlsx")


def generate_names(count=1, first_names=FIRST_NAMES, last_names=LAST_NAMES) -> list:
    """ Generate random names.

    :param count:       How many names to generate.
    :param first_names: Excel file name to read for first names.
    :param last_names:  Excel file name to read for last names.

    :return: list       List of names
    """

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
    return names

if __name__ == "__main__":
    print(generate_names(1))
