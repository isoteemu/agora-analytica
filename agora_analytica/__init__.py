from os import getcwd
from os.path import abspath, join


def instance_path() -> str:
    """
        Return instance path.
    """
    path = [getcwd(), "instance"]

    return abspath(join(*path))
