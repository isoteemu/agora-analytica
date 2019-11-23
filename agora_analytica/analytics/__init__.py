"""

Analytics Modules
=================

Defines common api for measuring distances between candidates.

"""

from ..data import DataSetInstance

import pandas as pd
import numpy as np
import importlib

import logging

from typing import List

ACCEPTED_TYPES = {
    "linear": "linear_answers",
    "multiselect": "multiselect_answers"
}

logger = logging.getLogger(__name__)


def measure_distances(df: DataSetInstance, methods: List = ["linear", "multiselect"], **kwargs) -> pd.DataFrame:
    """
    Measure distance between candidates.

    Asymptotic behaviour is `O((N - 1) * N/2 - 1)`.

    :param df: :class:`pandas.DataFrame` which is processed by row basis.
               Asymptotic behavior is exponential.
    :param limit: How many rows from :param:`df` to process.
                  Values less than 1 is interpret as "all".
    :param method: Module names to use. Should be on :module:`agora_analytica.analytics.<method>`
    :param **kwargs: Optional arguments to be passed for method module.

    :return: Returns :class:`pandas.DataFrame` instance, with rows `source`, `distance` and `target`
    """

    calcs = {method: importlib.import_module(f".{method}", __package__) for method in methods}

    # Collect required answer types
    answer_types = set([])
    for m in calcs:
        answer_types = answer_types.union(calcs[m].ACCEPTED_TYPES)

    answers = {}
    questions_n = 0
    for answer_type in answer_types:
        # Fetch all answer types, requested used by calculation modules.
        if answer_type in answers:
            continue

        answers[answer_type] = getattr(df, ACCEPTED_TYPES[answer_type])()

        # Remember how many columns there are in total.
        questions_n += len(answers[answer_type].columns)

    # Define return structure.
    # `source` and `target` are pointers to dataframe indexes. 
    # `distance` indicates calculated distance value between `source` and
    # `target`.
    distances = pd.DataFrame({
        "source": pd.Series(dtype='int64'),
        "distance": pd.Series(dtype='float'),
        "target": pd.Series(dtype='int64')
    })

    # O(N*N) processing for calculating distances.
    for i in range(df.shape[0]):
        # Offset is passed so already processed entries aren't
        # processed multiple times.
        offset = i + 1
        for l in range(offset, df.shape[0]):
            source = df.iloc[i]
            target = df.iloc[l]

            # Loop through all requested calculation methods, and calculate
            # distance
            distance = np.float(0)
            for method in calcs:
                # Invoke calculation method, and calculate distance
                calc = calcs[method]

                # Calculate how many columns this distance is proportional to.
                weight = questions_n * len(answers[method].columns)
                distance += calc.distance(source, target, answers[method], **kwargs) / weight

            _d = pd.Series([np.int(i), distance, np.int(l)], index=distances.columns, dtype='object')
            distances = distances.append(_d, ignore_index=True)

    return distances


def _get_common_columns(source: pd.Series, target: pd.Series, answers: pd.DataFrame) -> List:
    """ Collect columns that source and target have both answered."""

    # Get intersection answer columns both source and target have answered

    questions = set(answers.columns)
    source_ans = set(source.dropna().index)
    target_ans = set(target.dropna().index)

    columns = questions & (source_ans & target_ans)

    if len(columns) == 0:
        raise ValueError("Zero common columns.")

    return list(columns)
