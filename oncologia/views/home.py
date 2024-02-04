from datetime import datetime

from flask import Blueprint, render_template, request

from oncologia.extensions.models import Pendency, PendencyStatus
from oncologia.utils import login_required, search_patient_query

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


@bp.route("/search-patient")
@login_required
def search_patient():
    q = request.args.get("q")
    page = request.args.get("p", 1, type=int)
    per_page = 10

    query = search_patient_query(q)
    patients = query.paginate(page=page, per_page=per_page)
    return render_template("home/search_patient.html", patients=patients)
