import numpy as np
import pandas as pd
from . import _get_common_columns

ACCEPTED_TYPES = ["multiselect"]

def distance(source: pd.Series, target: pd.Series, answers: pd.DataFrame,
             answer_scale=5) -> float:

    # Collect columns that source and target have both answered.
    columns = _get_common_columns(source, target, answers)

    distances = np.zeros(len(columns))

    for i, col in enumerate(columns):
        source_ans = set(source[col])
        target_ans = set(target[col])

        selected_n = len(source_ans) + len(target_ans)
        if selected_n == 0:
            m = 0
        else:
            # Get different answers proportion to all answers
            m = len( source_ans ^ target_ans ) / selected_n

        distances[i] = (answer_scale - 1) * m

    mean = distances.mean() or np.float(0)
    return mean if not np.isnan(mean) else np.float(0)

