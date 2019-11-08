from typing import List, Dict, Tuple

import numpy as np
import pandas as pd


def party_distances(df: pd.DataFrame, answers: pd.DataFrame, **kwargs) -> Dict[str, List[Tuple[str, float]]]:
    """
    Calculate party distances.
    """

    group = kwargs.get("group", "party")
    parties = list(df[group].unique())

    n = len(parties)

    means = pd.DataFrame([], columns=answers.columns)
    # Empty matrix to store distances.
    distances = np.array([[[np.int(-1), np.float(5)]] * n ] * n )

    # Return dictionary
    r = {}

    for party in parties:
        # Calculate party average positions
        idx = df[df[group] == party].index
        means = means.append(answers.loc[idx].mean(), ignore_index=True)

    # Calculate distances between parties
    for i in range(n):
        for l in range(i + 1, n):
            diff = means.iloc[i] - means.iloc[l]
            distance = diff.map(np.abs).mean()
            distances[i, l] = (l, distance)
            distances[l, i] = (i, distance)

    for i, d in enumerate(distances):
        # Sort distance matrixes
        _d = sorted(d, key=lambda x: x[1])
        # Generate list with readable names
        r[parties[i]] = [(parties[int(i[0])], i[1]) for i in _d if i[0] >= 0]

    return r