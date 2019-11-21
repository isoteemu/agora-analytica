from .. import instance_path

import re

import pandas as pd
import numpy as np
import joblib

from stop_words import get_stop_words
from voikko.libvoikko import Voikko

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA

from itertools import chain
from typing import List, Dict
import logging

from cachetools import cached

logger = logging.getLogger(__name__)


class VoikkoTokenizer():

    """ Tokenize text """
    def __init__(self, lang="fi"):
        self.stem_map = {}
        self.voikko = Voikko(lang)
        self.regex_words = re.compile(r"""
            (\w+-(?:\w+)+  # Get wordcharacters conjucated by dash (-)
            |\w{1,}        # OR all word characters len() > 1
            )|(?::[\w]*)   # ignore word characters after colon
        """, re.VERBOSE + re.MULTILINE)
        self.err_treshold = 0.5

    def tokenize(self, text: str) -> List[str]:
        """ Return list of words """
        # Split into paragraphs.
        paragraphs = text.splitlines()
        tokens = chain(*map(self.tokenize_paragraph, paragraphs))
        return tokens

    def tokenize_paragraph(self, sentence, use_suggestions=True):
        """ Tokenize words using :class:`~Voikko`

        ..todo:
            - Detect abbrevations from CAPITAL letters.

        :param use_suggestions:  Should stemming use spell checking.
        """

        # Spell check mistake counters
        err_count = 0

        def _stem(word: str) -> List[str]:
            """ Return :type:`list` of stemmed words.

            If word is found on voikko dataset, uses suggestion to lookup for first candidate.
            """
            nonlocal err_count

            # See: https://github.com/voikko/voikko-sklearn/blob/master/voikko_sklearn.py
            FINNISH_STOPWORD_CLASSES = ["huudahdussana", "seikkasana", "lukusana", "asemosana", "sidesana", "suhdesana", "kieltosana"]

            # Check for previous stemming result
            stemmed_word = self.stem_map.get(word, None)
            if stemmed_word is not None:
                return [stemmed_word]

            analysis = self.voikko.analyze(word)

            if not analysis:
                # If analyze didn't produce results, try spellcheking
                err_count += 1
                analysis = []

                if use_suggestions:
                    # Get first suggestion.
                    suggested, *xs = self.voikko.suggest(word) or [None]
                    logger.debug(f"Voikko did not found word {word!r}; suggested spelling: {suggested!r}")

                    if suggested is not None:
                        # return tokenized suggestion - It can be two or more words.
                        return self.tokenize_paragraph(suggested, use_suggestions=False)

            for _word in analysis:
                # Find first suitable iteration of word.
                _class = _word.get("CLASS", None)
                if _class not in FINNISH_STOPWORD_CLASSES:
                    baseform = _word.get('BASEFORM').lower()
                    self.stem_map[word] = baseform
                    return [baseform]

            # Fall back to given word.
            self.stem_map[word] = word.lower()
            return [word.lower()]

        # Create list of words from string, separating from non-word characters.
        r = [x for x in re.findall(self.regex_words, sentence.lower()) if x != ""]

        r = [x for x in chain(*map(_stem, r)) if x]
        if len(r) * self.err_treshold < err_count:
            # Too many spelling errors. Presume incorrect language, and disregard paragraph.
            logger.debug("Too many spelling errors: %d out of %d", err_count, len(r))
            return []

        return r


__tokenizer = VoikkoTokenizer()

def tokenizer(word):
    return __tokenizer.tokenize(word)

class TextTopics():
    def __init__(self,
                 df: pd.DataFrame,
                 number_topics=50,
                 instance_path=instance_path()):
        self._instance_path = instance_path
        self.number_topics = number_topics
        self.stop_words: List = get_stop_words("fi")
        self._count_vector: CountVectorizer = None
        self._lda: LDA = None
        self.init(df)

    def init(self, df):
        if self._count_vector and self._lda:
            return True
        f_words = self.instance_path() / "word.dat"
        f_lda = self.instance_path() / "lda.dat"

        try:
            self._count_vector = joblib.load(f_words)
            self._lda = joblib.load(f_lda)
        except FileNotFoundError:
            texts = [x for x in df.to_numpy().flatten() if x is not np.NaN]

            # Setup word count vector
            self._count_vector = CountVectorizer(
                tokenizer=tokenizer,
                stop_words=self.stop_words
            )
            count_data = self._count_vector.fit_transform(texts)

            self._lda = LDA(n_components=self.number_topics, n_jobs=-1)
            self._lda.fit(count_data)

            joblib.dump(self._count_vector, f_words)
            joblib.dump(self._lda, f_lda)

    def instance_path(self):
        path = self._instance_path / "lda" / str(self.number_topics)
        path.mkdir(exist_ok=True, parents=True)
        return path

    def compare_series(self, source, target):

        # Convert them into tuples, so they can be cached.
        _source = tuple(source.dropna())
        _target = tuple(target.dropna())
        source_topics = self._get_topics(_source)
        target_topics = self._get_topics(_target)

        diffs = source_topics - target_topics

        topic_max = np.argmax(diffs)
        topic_min = np.argmin(diffs)

        source_topic = self.find_topic_word(_source, topic_max)
        target_topic = self.find_topic_word(_target, topic_min)

        return ((topic_max, source_topic), (topic_min, target_topic))

    @cached({})
    def _get_topics(self, source):
        source_count = self._count_vector.transform(source)
        return self._lda.transform(source_count).mean(axis=0)

    @cached({})
    def find_topic_word(self, text: List, topic_id):
        source = pd.Series(tokenizer("\n\n".join(text))).value_counts()

        words = pd.Series(self.topic_words(topic_id))
        counts = source * words

        return "%s (%d)" % (counts.sort_values(ascending=False).axes[0][0], topic_id)



    @cached({})
    def topic_words(self, id: int) -> Dict[int, str]:
        words = self.vector_words()
        topic_words = self._lda.components_[id].argsort()[::-1]

        return {words[i]: self._lda.components_[id][i] for i in topic_words}

    @cached({})
    def vector_words(self) -> List:
        return self._count_vector.get_feature_names()


def analyze_text(df: pd.DataFrame, topic_number=50):
    pass
