import pytest

from pathlib import Path

from agora_analytica import instance_path
from agora_analytica.loaders.utils import generate_names


def test_instancepath():
    path = instance_path()
    assert isinstance(path, Path)
    assert path.is_dir()


def test_namegen():
    """
    Test name generation.
    """
    
    for n in [x**x for x in range(1, 5)]:
        names = generate_names(n)
        assert len(names) == n
        assert len(set(names)) == n, "Namegen produced same name multiple times"


