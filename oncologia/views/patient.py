from flask import Blueprint, flash, redirect, render_template, request, url_for

from oncologia.extensions.database import db
from oncologia.extensions.models import (
    Patient,
    Pendency,
    PendencyStatus,
    PendencyType,
)
from oncologia.forms import PendencyForm
from oncologia.utils import login_required

bp = Blueprint("patient", __name__, url_prefix="/patient")


@bp.route("/")
def profile():
    patient_id = request.args.get("id")

    patient = Patient.query.filter_by(ghc=patient_id).first()
    if not patient:
        flash("Paciente com ID especificado não encontrado.", "error")
        return redirect(url_for("home.index"))

    return render_template("/patient/profile.html", patient=patient)


@bp.route("/add-pendency", methods=["GET", "POST"])
@login_required
def create_pendency():
    patient_id = request.args.get("id")

    form = PendencyForm()

    patient = Patient.query.get(patient_id)  # Obtém o paciente pelo ID
    if not patient:
        flash("Paciente não encontrado.", "error")
        return redirect(url_for("home.index"))

    def POST():
        if form.validate_on_submit():
            pendency_type = PendencyType.query.filter_by(
                id=form.type_ad.data
            ).first()
            if not pendency_type:
                pendency_type = PendencyType(
                    name=form.type_ad.data  # type: ignore [data-isnt-none]
                )

            status_name = form.status.data

            new_pendency = Pendency(
                type=pendency_type,
                due_date=form.date.data,
                description=form.description.data,
                status=PendencyStatus(status_name),
                patient_id=patient_id,
            )

            db.session.add(new_pendency)
            db.session.commit()
            flash("Pendência adicionada com sucesso!", "success")
            return redirect(url_for("patient.profile", id=patient_id))

    returned = locals().get(request.method, lambda: None)()
    if returned:
        return returned
    return render_template(
        "patient/create_pendency.html", form=form, patient_id=patient_id
    )
