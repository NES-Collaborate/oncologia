from flask import Blueprint, render_template

from oncologia.utils import login_required

bp = Blueprint("home", __name__)


@bp.route("/")
@login_required
def index():
    return render_template("home/index.html")
