from flask import Flask
from flask.logging import default_handler

import os
import logging

from .. import instance_path


def setup_app(name=__name__, **kwargs) -> Flask:
    r"""
    Setup Flask environment
    :param CHARSET:
    :param SECRET_KEY:
    :param DEBUG:
    :param BABEL_DEFAULT_LOCALE:
    :param BABEL_DEFAULT_TIMEZONE:
    :param DATABASE:
    """

    app = Flask(name, instance_relative_config=True)

    kwargs.setdefault("CHARSET", "utf-8")
    kwargs.setdefault("DEBUG", False)
    kwargs.setdefault("BABEL_DEFAULT_LOCALE", "fi")
    kwargs.setdefault("BABEL_DEFAULT_TIMEZONE", u"Europe/Helsinki")

    app.config.update(kwargs)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if not app.config.get("SECRET_KEY"):
        key_file = os.path.join(app.instance_path, "secret_key")

        try:
            with open(key_file, 'rb') as fd:
                app.config['SECRET_KEY'] = fd.read()
        except Exception as e:
            app.logger.exception(e)
            app.logger.info("Generating new SECRET_KEY %s", key_file)
            app.config['SECRET_KEY'] = os.urandom(64)
            with open(key_file, 'wb') as fd:
                fd.write(app.config['SECRET_KEY'])

    #Babel(app)
    #app.jinja_env.globals.update(get_locale=get_locale)

    logger = logging.getLogger(name)
    logger.addHandler(default_handler)

    return app


if __name__ == "agora_analytica.flask":

    app = setup_app(__name__, instance_path=instance_path())

    from . import views
    views.app_init(app)
