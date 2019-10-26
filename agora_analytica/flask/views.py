from flask import (
    Blueprint,
    current_app,
    render_template,
    send_from_directory
)

bp = Blueprint("", __name__)

def app_init(app):
    with app.app_context():
        app.register_blueprint(bp)

@bp.route('/')
def index():
    return render_template("main.html", data=[])

@bp.route('/api/links.json')
def data_links():
    return send_from_directory(current_app.instance_path, "links.json")

@bp.route('/api/nodes.json')
def data_nodes():
    return send_from_directory(current_app.instance_path, "nodes.json")