"""
Dummy module for generating fixed - or random - distances.
"""

from numpy.random import randint
from numpy import abs, int
import pandas as pd


def distance(source: pd.Series, target: pd.Series, answers: pd.DataFrame, answer_scale=5, answer_source=None, answer_target=None):

    def _maybe_random(answer: int) -> int:
        """ Return either :param:`answer` or random number in `answer_scale` """
        return answer if answer is not None else randint(0, answer_scale)

    answer_source = _maybe_random(answer_source)
    answer_target = _maybe_random(answer_target)

    return abs(answer_source - answer_target)
