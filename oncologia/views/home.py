from flask import Blueprint

from oncologia.utils import login_required

bp = Blueprint("home", __name__)


@bp.route("/")
@login_required
def index():
    return "Oncologia APP"
