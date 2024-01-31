from datetime import datetime

from flask import Blueprint, render_template

from oncologia.extensions.models import Pendency, PendencyStatus
from oncologia.utils import login_required

bp = Blueprint("home", __name__)


@bp.route("/")
@login_required
def index():
    pendencies = Pendency.query.filter(
        Pendency.due_date < datetime.now(),
        Pendency.status == PendencyStatus.pending,
    ).all()
    context = {"pendencies": pendencies}
    return render_template("home/index.html", **context)
