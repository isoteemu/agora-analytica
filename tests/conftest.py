import pytest

from agora_analytica import instance_path as _instance_path


@pytest.fixture(scope="session", autouse=True)
def instance_path():
    return _instance_path()

