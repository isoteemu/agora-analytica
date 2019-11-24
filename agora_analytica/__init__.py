import os

from pathlib import Path
from configparser import ConfigParser

def instance_path() -> Path:
    """
        Return instance path.
    """

    default = Path.cwd() / "instance"
    _path = os.environ.get("INSTANCE_PATH", default)

    path = Path(_path)

    return path.resolve()


def config() -> ConfigParser:
    """
    Default config.

    Config object is NOT GLOBAL, and changes will not be stored.
    """

    # Read config file from module directory.
    settings = ConfigParser()
    settings.read((Path(__file__) / ".." / "app.cfg").resolve())

    # Read config from instance path
    settings.read((instance_path() / "app.cfg").resolve())

    return settings
