"""

Analytics Modules
=================

Defines common api for measuring distances between candidates.

"""

import pandas as pd
import numpy as np

import importlib
from functools import reduce

import logging

import asyncio
from os import sched_getaffinity

logger = logging.getLogger(__name__)


async def measure_distances(df: pd.DataFrame, method="linear", threads=-1, **kwargs) -> pd.DataFrame:
    """
    Measure distance between candidates.

    :param df: :class:`pandas.DataFrame` which is processed by row basis.
               Asymptotic behavior is exponential.
    :param limit: How many rows from :param:`df` to process.
                  Values less than 1 is interpret as "all".
    :param method: Module name to use. Should be on :module:`agora_analytica.analytics.<method>`
    :param threads: Number of simultaneous tasks to use. `-1` to execute on all cpus.
    :param **kwargs: Optional arguments to be passed for method module.

    :return: Returns :class:`pandas.DataFrame` instance, with rows `source`, `distance` and `target`
    """

    if threads == -1:
        threads = len(sched_getaffinity(0))

    distances_struct = pd.DataFrame({
        "source": pd.Series(dtype='int64'),
        "distance": pd.Series(dtype='float'),
        "target": pd.Series(dtype='int64')
    })

    async def _measure_distance(df: pd.DataFrame, i: int, step: int):
        """ Inner recursive function for calculating distances """
        source = df.iloc[i]

        logger.debug("[Thread]: Calculating distaces from %i with step %i", i, step)

        distances = distances_struct.copy()
        offset = i + 1
        index = df.index[i]
        for l in range(offset, N):
            target = df.iloc[l]

            distance = calc.distance(source, target, df, **kwargs)
            distances = distances.append(pd.Series([index, distance, df.index[l]], index=distances.columns, dtype='object'), ignore_index=True)

        next_i = (i + step)
        if N > next_i:
            return distances.append(await _measure_distance(df, next_i, step), ignore_index=True)
        else:
            return distances

    calc = importlib.import_module(f".{method}", __package__)
    N = df.shape[0]

    threads = min(N, threads)
    logging.debug("Measuring distances on %i threads", threads)

    tasks = await asyncio.gather(*[
        _measure_distance(df, i, step=threads) for i in range(threads)
    ])

    # combine results from tasks
    distances = reduce(lambda x, y: x.append(y, ignore_index=True), tasks, distances_struct.copy())

    return distances
