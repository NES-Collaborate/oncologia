from flask import Blueprint, flash, redirect, render_template, request, url_for

bp = Blueprint("patient", __name__, url_prefix="/patient")

from oncologia.extensions.models import Patient


@bp.route("/")
def profile():
    patient_id = request.args.get("id")

    patient = Patient.query.filter_by(ghc=patient_id).first()
    if not patient:
        flash("Paciente com ID especificado não encontrado.", "error")
        return redirect(url_for("home.index"))

    return render_template("/patient/profile.html", patient=patient)
