import pytest

import os.path
import pandas as pd
import numpy as np

from agora_analytica.loaders.yle_2019 import (
    download_dataset,
    load_dataset,
    DATASET_NAME,
    linear_answers,
)


@pytest.fixture(scope="session")
def yle_2019_df(instance_path):
    df = load_dataset(instance_path / DATASET_NAME)
    assert isinstance(df, pd.DataFrame)
    return df


@pytest.mark.skip
def test_download(tmp_path):
    """ Test downloading data from Yle website """

    filepath = tmp_path / "yle_2019.csv"
    df = download_dataset(filepath)

    assert isinstance(df, pd.DataFrame)
    assert filepath.exists()
    assert filepath.is_file()

    assert df.shape == (2437, 213)


def test_yle_data(yle_2019_df):
    """
    Yle data integrity tests.
    """

    # Test for correct ammount of entries.
    assert yle_2019_df.shape[0] == 2437

    # Test for some existing columns
    cols = ["vaalipiiri", "puolue", "nimi"]
    for col in cols:
        assert col in yle_2019_df.columns


def test_linears(yle_2019_df):
    """
    Validate linear ranges to be numeric.
    """

    allowed = [np.int(1), np.int(2), np.int(3), np.int(4), np.int(5), np.NaN]
    linears = linear_answers(yle_2019_df)
    # Generate similar dataframe, but with all True values.
    mask = pd.DataFrame([[True] * linears.shape[1]] * linears.shape[0], columns=linears.columns, index=linears.index)

    assert linears.isin(allowed).equals(mask)


