from datetime import datetime

from flask import Blueprint, flash, render_template, request
from sqlalchemy import or_

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
    PhoneNumber,
    TumorCharacterization,
    TumorGroup,
)
from oncologia.forms import PatientForm
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


@bp.route("/add-patient", methods=["POST", "GET"])
@login_required
def add_patient():
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
        render_template("home/add_patient.html", form=form)
        if not returnerd
        else returnerd
    )


@bp.route("/search-patient")
@login_required
def search_patient():
    q = request.args.get("q")
    page = request.args.get("p", 1, type=int)
    per_page = 15

    query = search_patient_query(q)
    patients = query.paginate(page=page, per_page=per_page)
    return render_template("home/search_patient.html", patients=patients)
