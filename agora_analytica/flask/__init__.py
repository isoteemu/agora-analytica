from flask import Flask
from flask.logging import default_handler
from flask_babel import Babel, get_locale

import os
import logging

from .. import instance_path, config

logger = logging.getLogger(__name__)


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

    app = Flask(name, instance_path=kwargs.get("instance_path", None), instance_relative_config=True)

    kwargs.setdefault("CHARSET", "utf-8")
    kwargs.setdefault("DEBUG", False)
    kwargs.setdefault("BABEL_DEFAULT_LOCALE", "fi")
    kwargs.setdefault("BABEL_DEFAULT_TIMEZONE", u"Europe/Helsinki")

    app.config.update(config())

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if not app.config.get("SECRET_KEY"):
        key_file = app.instance_path / "secret_key"

        try:
            with open(key_file, 'rb') as fd:
                app.config['SECRET_KEY'] = fd.read()
        except Exception as e:
            app.logger.exception(e)
            app.logger.info("Generating new SECRET_KEY %s", key_file)
            app.config['SECRET_KEY'] = os.urandom(64)
            with open(key_file, 'wb') as fd:
                fd.write(app.config['SECRET_KEY'])

    Babel(app)
    app.jinja_env.globals.update(get_locale=get_locale)

    logger = logging.getLogger(name)
    logger.addHandler(default_handler)

    @app.context_processor
    def inject_branding():
        return dict(branding=app.config['branding'])

    return app


if __name__ == "agora_analytica.flask":

    app = setup_app(__name__, instance_path=instance_path())

    dev = app.config.get('ENV') == "development"

    @app.context_processor
    def inject_debug():
        return dict(dev=dev)

    if dev:
        # If running on development setup, compile sass files on fly
        try:
            from sassutils.wsgi import SassMiddleware

            app.wsgi_app = SassMiddleware(app.wsgi_app, {
                __name__: ('static/sass', 'static/css', '/static/css')
            })
        except ImportError as e:
            logger.exception(e)
            logger.warning("Could not import sassutil for dynamic scss file compilation.")

    from . import views
    views.app_init(app)
