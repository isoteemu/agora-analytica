from agora_analytica.data import jyy_ed_2019 as dataset
from agora_analytica import instance_path

import numpy as np
from pyLDAvis import sklearn as sklearn_lda
import pyLDAvis

import sys
import re

import joblib
from itertools import chain
from cachetools import cached

from stop_words import get_stop_words
from voikko.libvoikko import Voikko

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def _instance_path():
    path = instance_path() / "lda"
    path.mkdir(exist_ok=True)
    return path


LDA_FILE = _instance_path() / "LDA.dat"
WORDS_FILE = _instance_path() / "words.dat"


def tokenize(sentence: str, use_suggestions=True) -> list:
    """ Tokenize words using :class:`~Voikko`

    ..todo:
        - Detect abbrevations from CAPITAL letters.

    :param use_suggestions:  Should stemming use spell checking.
    """
    skip_words = [""]

    # Match words.
    # Skip suffixes idicated by `:`
    r = [x for x in re.findall(r'([\w]{0,}(?:[\w]+))', sentence.lower()) if x not in skip_words]

    # Set up stemmer
    v = Voikko("fi")

    def _stem(word) -> list:
        """ Return :type:`list` of stemmed words.

        If word is found on voikko dataset, uses suggestion to lookup for first
        possible correct candidate.
        """

        # See: https://github.com/voikko/voikko-sklearn/blob/master/voikko_sklearn.py
        FINNISH_STOPWORD_CLASSES = ["huudahdussana", "seikkasana", "lukusana", "asemosana", "sidesana", "suhdesana", "kieltosana"]
        # TODO: Käy kaikki löydetyt sanamuodot läpi.
        analysis = v.analyze(word)
        if not analysis:
            # Get first suggestion.
            suggested, *xs = v.suggest(word) or [None]
            logger.debug(f"Voikko did not found word {word!r}; suggested spelling: {suggested!r}")

            if suggested is not None:
                if use_suggestions:
                    return tokenize(suggested, use_suggestions=False)
                else:
                    analysis = v.analyze(word)
            else:
                # No matches.
                analysis = [{}]

        r = analysis[0] if analysis else {}

        if r.get("CLASS") in FINNISH_STOPWORD_CLASSES:
            return [None]

        return [r.get("BASEFORM", word.lower())]

    r = [x for x in chain(*map(_stem, r)) if x]

    return r


text_df = dataset.load_dataset().text_answers()
number_topics = 10

lda = object()
vectorizer = object()
words = list()

try:
    lda = joblib.load(LDA_FILE)
    vectorizer = joblib.load(WORDS_FILE)
    words = vectorizer.get_feature_names()

except Exception as e:
    logger.exception(e)

    texts = [x for x in text_df.to_numpy().flatten() if x is not np.NaN]

    stop_words = get_stop_words("fi")
    stop_words += ["tulla", "opiskelija", "kyy", "kaikki"]

    vectorizer = CountVectorizer(tokenizer=tokenize,
                                 stop_words=stop_words)

    count_data = vectorizer.fit_transform(texts)

    lda = LDA(n_components=number_topics, n_jobs=-1)
    lda.fit(count_data)
    words = vectorizer.get_feature_names()

    LDAvis_prepared = sklearn_lda.prepare(lda, count_data, vectorizer)
    pyLDAvis.save_html(LDAvis_prepared, str(_instance_path() / "pyldavis.html"))

    joblib.dump(lda, LDA_FILE)
    joblib.dump(vectorizer, WORDS_FILE)

number_words = 15

suitable_topic_classes = ["nimisana"]

topic_labels = {}
topics = np.array([x.argsort()[::-1] for x in lda.components_])

v = Voikko("fi")
def _is_suitable_label(word) -> bool:
    r = v.analyze(word) or []
    for w in r:
        if w.get("CLASS") in ["nimisana"]:
            return True
        else:
            logger.debug("%s CLASS is %s", word, w.get("CLASS"))
    return False

i = 0
while len(topic_labels) < number_topics:

    _topic_words = list(map(lambda x: words[x], topics[:, i]))

    for l, word in enumerate(_topic_words):
        print(word)
        if l in topic_labels:
            # topic has already label
            pass
        elif word in topic_labels.values():
            # Word already exists
            pass
        elif _topic_words.count(word) == 1 and _is_suitable_label(word):
            # Set label for topic
            topic_labels[l] = word
    i += 1

for topic_idx, topic in enumerate(lda.components_):
    print("\nTopic %s:" % topic_labels[topic_idx])

    print([words[i] for i in topic.argsort()[:-number_words - 1:-1]])


text = text_df.sample(n=1).iloc[0].dropna()
test_count = vectorizer.transform(text)

print([str(x) for x in text])
m = lda.transform(test_count).mean(axis=0)
print("Max:", topic_labels[np.argmax(m)])
print(m)
