import logging
from typing import Tuple

import pandas as pd
import numpy as np

from cachetools import cached
from cachetools.keys import hashkey

logger = logging.getLogger(__name__)


def distance(source: pd.Series, target: pd.Series, answers: pd.DataFrame,
             answer_scale=5, bias_min=0.2, bias_max=2.0) -> float:
    """ Calculate distance between targets.

    Uses less common answers to skew bias.

    :param scale: (optional) Scale on which questions are asked, starting from 1. Defaults to 5.
    :param bias_min: (optional) float Minimum allowed bias.
    :param bias_max: (optional) float Maximum allowed bias
    """

    # Collect columns that source and target have both answered.
    columns = set(source.dropna().index).intersection(set(target.dropna().index))

    # Stores distances, and is used to calculate mean value.
    distances = np.zeros(len(columns))

    # Go through answers, and calculate answer distances from source to target
    for i, col in enumerate(columns):

        # Collect answers into unique set.
        answers_set = tuple(set([
            np.int(source[col]),
            np.int(target[col])
        ]))

        # Calculate similar and different answers
        similar_count, different_count = _similar_counts(col, answers, answers_set)

        similar_ratio = similar_count / len(answers_set)
        different_ratio = different_count / (answer_scale - len(answers_set))

        # Calculate bias
        bias = np.float(min(bias_max, max(bias_min, different_ratio / similar_ratio)))

        # Calculate distance between answers with bias.
        distance = np.abs(np.int(source[col]) - np.int(target[col])) * bias
        distances[i] = distance

    distance_mean = distances.mean() or 0
    return distance_mean if not np.isnan(distance_mean) else np.float(0)


@cached(cache={}, key=lambda column, answers, answer_set: hashkey(column, answer_set))
def _similar_counts(column: str, answers: pd.DataFrame, answers_set: Tuple[int]) -> Tuple[np.int, np.int]:
    """
    Similar and different answers.

    :return: Tuple of different and similar answers
    """

    # Create boolean list of people who answered similarly to current `answers_set`
    similar_filter = answers[column].isin(answers_set)

    # Calculate similar and different answers
    similar_count = answers[column].dropna()[similar_filter].count()
    different_count = answers[column].dropna()[~similar_filter].count()
    logger.debug("'%s': Similar/Different: %i / %i", column, similar_count, different_count)

    return (similar_count, different_count)
