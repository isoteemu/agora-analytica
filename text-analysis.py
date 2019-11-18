from agora_analytica.data import yle_2019 as dataset
from agora_analytica.analytics.text import VoikkoTokenizer
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

text_df = dataset.load_dataset().text_answers()
number_topics = 10

lda = object()
vectorizer = object()
words = list()

tokenizer = VoikkoTokenizer()


def _tokenizer(word):
    return tokenizer.tokenize(word)


try:
    lda = joblib.load(LDA_FILE)
    vectorizer = joblib.load(WORDS_FILE)
    words = vectorizer.get_feature_names()

except Exception as e:
    logger.exception(e)

    texts = [x for x in text_df.to_numpy().flatten() if x is not np.NaN]

    stop_words = get_stop_words("fi")
    stop_words += ["tulla", "opiskelija", "kyy", "kaikki"]

    vectorizer = CountVectorizer(tokenizer=_tokenizer,
                                 stop_words=stop_words,
                                 lowercase=False)

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
