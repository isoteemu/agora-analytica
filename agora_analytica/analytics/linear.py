import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def distance(source: pd.Series, target: pd.Series, answers: pd.DataFrame,
        answer_scale=5, bias_min=0.2, bias_max=2.0) -> np.float:
    """ Calculate distance between targets.

    Uses less common answers to skew bias.

    :param scale: (optional) Scale on which questions are asked, starting from 1. Defaults to 5.
    :param bias_min: (optional) float Minimum allowed bias.
    :param bias_max: (optional) float Maximum allowed bias
     """

    # Stores distances, and is used to calculate mean value.
    distances = pd.Series()

    # Collect columns that source and target have both answered.
    columns = set(source.dropna().index).intersection(set(target.dropna().index))

    # Go through answers, and calculate answer distances from source to target
    for col in columns:

        # Collect answers into unique set.
        answers_set = set([
            np.int(source[col]),
            np.int(target[col])
        ])

        # Create boolean list of people who answered similarry to current `answers_set`
        similar_filter = answers[col].isin(answers_set)

        # Calculate similar and different answers
        similar_count = answers[col][similar_filter].count() / len(answers_set)
        different_count = answers[col][~similar_filter].count() / (answer_scale - len(answers_set))

        #logger.debug("Similar %s Different %s", similar_count, different_count)

        # Calculate bias
        bias = np.float(min(bias_max, max(bias_min, different_count / similar_count)))

        # Calculate distance between answers with bias.
        distance = np.abs(np.int(source[col]) - np.int(target[col])) * bias

        distances = distances.append(pd.Series([distance]), ignore_index=True)

    distance_mean = distances.mean()
    return distance_mean
