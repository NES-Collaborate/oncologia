import io
from base64 import b64encode
from functools import wraps
from typing import Optional

import requests
from flask import flash, redirect, session, url_for
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from sqlalchemy import or_

from oncologia.extensions.models import Patient, StatusType


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Faça login antes de acessar esta página!", "error")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


def get_website_agent() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Mozilla/5.0 @nes-collaborate/oncologia"}
    )
    return session


def search_patient_query(q: Optional[str] = None):
    query = Patient.query
    if q:
        query = query.filter(
            or_(
                Patient.name.like(f"%{q}%"),
                Patient.ghc == q,
                Patient.cpf.like(f"%{q}%"),
                Patient.cns.like(f"%{q}%"),
            )
        )
    return query


def get_status_type_form(status_type: StatusType):
    from oncologia.forms import (
        AbandonmentRefusalTreatmentUnableTreatForm,
        DeathForm,
        DefaultStatusForm,
        InTreatmentTreatedNonMelanomaSkinForm,
        PalliatievCareConservativeTreatmentForm,
    )

    data = {
        StatusType.in_treatment_treated: InTreatmentTreatedNonMelanomaSkinForm,
        StatusType.non_melanoma_skin: InTreatmentTreatedNonMelanomaSkinForm,
        StatusType.death: DeathForm,
        StatusType.palliative_care: PalliatievCareConservativeTreatmentForm,
        StatusType.conservative_treatment: PalliatievCareConservativeTreatmentForm,
        StatusType.abandonment_refusal: AbandonmentRefusalTreatmentUnableTreatForm,
        StatusType.treatment_unable_treat: AbandonmentRefusalTreatmentUnableTreatForm,
        StatusType.default: DefaultStatusForm,
    }
    return data[status_type]


def create_separate_figure():
    fig = Figure()
    FigureCanvas(fig)
    return fig


def save_figure_to_buffer(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    return (
        f'data:image/png;base64,{b64encode(buffer.getvalue()).decode("utf-8")}'
    )
