import logging

import pandas as pd
import numpy as np
import json

from typing import List

from .. import instance_path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Linear questions (1-5). Can be detected automatically.
linear_space = []

multiselect_space = []

def load_dataset(path = instance_path(), questions_file = "questions-6435463884701696.json", answers_file = "results-6668674686517248.json"):
    with open(path / questions_file) as f:
        questions = json.load(f)

    with open(path / answers_file) as f:
        answers = json.load(f)

    df = pd.DataFrame([], columns=["name", "party", "number", "age", "gender", "image", "description"])

    for i, candidate in enumerate(answers['children']):
        data = candidate.get("target_data", candidate.get("data", {}))
        c_data = {
            "name": data['name'],
            "party": data['vaaliliitto'],
            "number": data['no'],
            "age": data['age'],
            "gender": data['gender'],
            "image": data['image'],
            "description": data['text'],
        }
        df.loc[i] = c_data

    for q in questions['children']:
        col = q['title'].strip()
        q_type = q['type']
        if q_type == "question-free-text":
            d_type = str
        elif q_type == "question-1d-diagram":
            d_type = float
            linear_space.append(col)
        elif q_type == "question-sm-choice":
            d_type = "object"
            multiselect_space.append(col)
        else:
            logger.warning("Skipping unhandled question %s of type %s", col, q_type)
            continue

        df[col] = pd.Series(None, dtype=d_type)

        for i, candidate in enumerate(answers['children']):
            candidate_answers = candidate.get("target_values", {})
            q_id = str(q['id']) 
            if q_id not in candidate_answers:
                logger.debug("Candidate not answered question")
                continue

            if q_type == "question-sm-choice":
                _ans = candidate['target_values'][q_id]
                choice_ans = _ans.split(";") if _ans else np.NaN
                df.at[i, col] = choice_ans
            else:
                df.at[i, col] = d_type(candidate['target_values'][q_id])

    return df


def linear_answers(df) -> pd.DataFrame:
    return _get_answers(df, linear_space)


def multiselect_answers(df) -> pd.DataFrame:
    return _get_answers(df, multiselect_space)


def _get_answers(df: pd.DataFrame, cols: List):
    answers = pd.DataFrame(index=df.index, columns=[])
    for col in cols:
        matrix = df.loc[:, col]
        answers = answers.join(matrix)

    return answers


if __name__ == "__main__":
    df = load_dataset()
    print(multiselect_answers(df))
