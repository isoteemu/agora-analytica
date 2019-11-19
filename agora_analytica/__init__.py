import os

from pathlib import Path


def instance_path() -> Path:
    """
        Return instance path.
    """

    default = Path.cwd() / "instance"
    _path = os.environ.get("INSTANCE_PATH", default)

    path = Path(_path)

    return path.resolve()
