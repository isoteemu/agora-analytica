
import pandas as pd
import numpy as np
import importlib

def measure_distances(df: pd.DataFrame, limit=-1, method="linear") -> pd.DataFrame:

    calc = importlib.import_module(f".{method}", __package__)

    candidates = df
    if limit > 0:
        candidates = df.head(limit)

    distances = pd.DataFrame({
        "source": pd.Series(dtype='int64'),
        "distance": pd.Series(dtype='float'),
        "target": pd.Series(dtype='int64')
        })

    for i in range(candidates.shape[0]):
        offset = i + 1
        for l in range(offset, candidates.shape[0]):
            source = df.loc[i]
            target = df.loc[l]

            distance = calc.distance(source, target, df)
            distances = distances.append(pd.Series([np.int(i), distance, np.int(l)], index=distances.columns, dtype='object'), ignore_index=True)

    return distances.astype({"source": "int64", "target": "int64"})

