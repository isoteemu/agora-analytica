from random_word import RandomWords

import numpy as np

def contextual_differences(candidate_1, candidate_2) -> list:
    """
    This function should calculate different wordpairs
    :rtype: list or tuple
    """

    r = RandomWords()
    words = [x.lower() for x in r.get_random_words(limit=2)]


    return words


if __name__ == "__main__":
    print(contextual_differences("foo", "bar"))
