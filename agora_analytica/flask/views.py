from flask import (
    Blueprint,
    current_app,
    render_template,
    send_from_directory,
    make_response
)

from agora_analytica.data import yle_2019
bp = Blueprint("", __name__)


def app_init(app):
    """ Set up module for Flask app """
    with app.app_context():
        app.register_blueprint(bp)


@bp.route('/')
def index():
    """ Default page """
    return render_template("main.html", data=[])

@bp.route('/_lda')
def show_lda():
    """ Debug function. Show Generated LDA """
    return send_from_directory(current_app.instance_path, "lda/10/ldavis.html")

# Following functions are placeholders.
@bp.route('/api/links.json')
def data_links():
    return send_from_directory(current_app.instance_path, "links.json")

@bp.route('/api/node/<id>.json')
def node_getinfo(id):
    # /api/node/4234.json
    df = yle_2019.load_dataset()
    id = int(id)
    ehdokas = df.loc[id]

    r = make_response(ehdokas.to_json(), 200)
    r.mimetype = "application/json"
    return r

@bp.route('/api/nodes.json')
def data_nodes():
    return send_from_directory(current_app.instance_path, "nodes.json")


@bp.route('/api/parties.json')
def data_parties():
    return send_from_directory(current_app.instance_path, "parties.json")
