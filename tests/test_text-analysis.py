import pytest

from agora_analytica.analytics import text


@pytest.fixture(scope="module")
def text_tokenizer():
    tokenizer = text.VoikkoTokenizer("fi")
    return tokenizer


def test_nimisana_preference(text_tokenizer):
    """ Nimisana is preferred class for baseforms """
    assert list(text_tokenizer.tokenize("uskoa")) == ["usko"]

