from flask import Blueprint, flash, redirect, render_template, request, url_for

from oncologia.extensions.database import db
from oncologia.extensions.models import (
    DiagnosisCharacterization,
    DiagnosisLocation,
    EntryPoin,
    EntryTeam,
    ExamType,
    Patient,
    Pendency,
    PendencyStatus,
    PendencyType,
    PhoneNumber,
    TumorCharacterization,
    TumorGroup,
)
from oncologia.forms import PatientForm, PendencyForm
from oncologia.utils import login_required

bp = Blueprint("patient", __name__, url_prefix="/patient")


@bp.route("/")
@login_required
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


@bp.route("/create", methods=["POST", "GET"])
@login_required
def create():
    form = PatientForm()

    def POST():
        if not form.validate_on_submit():
            flash("Erro ao adicionar paciente", "error")
            return

        # Tumor Characterization
        tumor_group = TumorGroup.query.filter_by(
            id=form.tumor_characterization.tumor_group.data
        ).first()

        if not tumor_group:
            tumor_group = TumorGroup(
                name=form.tumor_characterization.tumor_group.data
            )
        tumor_characterization_data = {
            k: v for k, v in form.tumor_characterization.data.items()
        }
        tumor_characterization_data.update({"tumor_group": tumor_group})
        tumor_characterization = TumorCharacterization(
            **tumor_characterization_data
        )

        # Diagnosis Characterization
        diagnosis_characterization_data = {
            k: v for k, v in form.diagnosis_characterization.data.items()
        }
        entry_poin = EntryPoin.query.filter_by(
            id=form.diagnosis_characterization.entry_poin.data
        ).first()
        if not entry_poin:
            entry_poin = EntryPoin(
                name=form.diagnosis_characterization.entry_poin.data
            )

        entry_team = EntryTeam.query.filter_by(
            id=form.diagnosis_characterization.entry_team.data
        ).first()
        if not entry_team:
            entry_team = EntryTeam(
                name=form.diagnosis_characterization.entry_team.data
            )

        diagnosis_exam = ExamType.query.filter_by(
            id=form.diagnosis_characterization.diagnosis_exam.data
        ).first()
        if not diagnosis_exam:
            diagnosis_exam = ExamType(
                name=form.diagnosis_characterization.diagnosis_exam.data
            )

        diagnosis_location = DiagnosisLocation(
            int(form.diagnosis_characterization.diagnosis_location.data)
        )  # TODO: dont trust in this conversion.

        diagnosis_characterization_data.update(
            {
                "entry_poin": entry_poin,
                "entry_team": entry_team,
                "diagnosis_exam": diagnosis_exam,
                "diagnosis_location": diagnosis_location,
            }
        )

        diagnosis_characterization = DiagnosisCharacterization(
            **diagnosis_characterization_data
        )

        # Pacient
        patient_data = {
            k: v
            for k, v in form.data.items()
            if k
            not in (
                "tumor_characterization",
                "diagnosis_characterization",
                "phone_1",
                "phone_2",
            )
        }

        phones = [
            PhoneNumber(**form.data[k])
            for k in form.data.keys()
            if k.startswith("phone") and form.data[k]["number"]
        ]

        patient_data.update(
            {
                "phones": phones,
                "tumor_characterization": tumor_characterization,
                "diagnosis_characterization": diagnosis_characterization,
            }
        )

        patient = Patient(**patient_data)
        db.session.add(patient)
        db.session.commit()
        flash("Paciente adicionado com sucesso", "success")

    returnerd = locals().get(request.method, lambda: None)()
    return (
        render_template("patient/create.html", form=form)
        if not returnerd
        else returnerd
    )
