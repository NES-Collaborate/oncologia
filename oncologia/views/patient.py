from flask import Blueprint, render_template, request

bp = Blueprint("patient", __name__, url_prefix="/patient")

from oncologia.extensions.models import Patient


@bp.route("/")
def profile():
    patient_id = request.args.get("id")

    patient = Patient.query.filter_by(ghc=patient_id).first()

    return render_template("/patient/profile.html", patient=patient)
