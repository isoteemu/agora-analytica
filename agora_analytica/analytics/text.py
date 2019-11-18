from voikko.libvoikko import Voikko
import re

from itertools import chain
from typing import List
import logging

from cachetools import cached

logger = logging.getLogger(__name__)


class VoikkoTokenizer():
    """ Tokenize text """
    def __init__(self, lang="fi"):
        self.voikko = Voikko(lang)
        self.regex_words = re.compile(r"""
            (\w+-\w+|\w*)          # Get all word characters
            |(?::[\w]*)      # ignore word characters after colon
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

        @cached({})
        def _stem(word: str) -> List[str]:
            """ Return :type:`list` of stemmed words.

            If word is found on voikko dataset, uses suggestion to lookup for first candidate.
            """
            nonlocal err_count

            # See: https://github.com/voikko/voikko-sklearn/blob/master/voikko_sklearn.py
            FINNISH_STOPWORD_CLASSES = ["huudahdussana", "seikkasana", "lukusana", "asemosana", "sidesana", "suhdesana", "kieltosana"]

            analysis = self.voikko.analyze(word)

            if not analysis:
                err_count += 1

                # Get first suggestion.
                suggested, *xs = self.voikko.suggest(word) or [None]
                logger.debug(f"Voikko did not found word {word!r}; suggested spelling: {suggested!r}")

                if suggested is not None:
                    if use_suggestions:
                        return self.tokenize_paragraph(suggested, use_suggestions=False)
                    else:
                        analysis = self.voikko.analyze(word)
                else:
                    # No matches.
                    analysis = []

            _word = None
            for _word in analysis:
                # Find first suitable iteration of word.
                _class = _word.get("CLASS", None)
                if _class not in FINNISH_STOPWORD_CLASSES:
                    return [_word.get('BASEFORM').lower()]

            # Fall back to given word.
            return [word.lower()]

        # Create list of words from string, separating from non-word characters.
        r = [x for x in re.findall(self.regex_words, sentence.lower()) if x != ""]

        r = [x for x in chain(*map(_stem, r)) if x]
        if len(r) * self.err_treshold < err_count:
            # Too many spelling errors. Presume incorrect language, and disregard paragraph.
            logger.debug("Too many spelling errors: %d out of %d", err_count, len(r))
            return []

        return r
