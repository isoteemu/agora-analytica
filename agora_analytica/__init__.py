from os import getcwd

from pathlib import Path


def instance_path() -> Path:
    """
        Return instance path.
    """
    path = Path.cwd() / "instance"

    return path
