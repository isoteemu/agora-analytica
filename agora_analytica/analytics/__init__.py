"""

Analytics Modules
=================

Defines common api for measuring distances between candidates.

"""

import pandas as pd
import numpy as np
import importlib

def measure_distances(df: pd.DataFrame, limit=-1, method="linear", **kwargs) -> pd.DataFrame:
    """
    Measure distance between candidates. 

    :param df: :class:`pandas.DataFrame` which is processed by row basis.
               Asymptotic behavior is exponential.
    :param limit: How many rows from :param:`df` to process.
                  Values less than 1 is interpret as "all".
    :param method: Module name to use. Should be on :module:`agora_analytica.analytics.<method>`
    :param **kwargs: Optional arguments to be passed for method module.

    :return: Returns :class:`pandas.DataFrame` instance, with rows `source`, `distance` and `target`
    """

    calc = importlib.import_module(f".{method}", __package__)

    candidates = df
    if limit > 0:
        candidates = df.head(limit)

    # Define return structure.
    distances = pd.DataFrame({
        "source": pd.Series(dtype='int64'),
        "distance": pd.Series(dtype='float'),
        "target": pd.Series(dtype='int64')
        })

    # O(N*N) processing for calculating distances.
    for i in range(candidates.shape[0]):
        # Offset is passed so already processed entries aren't 
        # processed multiple times.
        offset = i + 1
        for l in range(offset, candidates.shape[0]):
            source = df.loc[i]
            target = df.loc[l]

            distance = calc.distance(source, target, df, **kwargs)
            distances = distances.append(pd.Series([np.int(i), distance, np.int(l)], index=distances.columns, dtype='object'), ignore_index=True)

    return distances

