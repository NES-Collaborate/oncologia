import io
from http import HTTPStatus

import pandas as pd
from flask import Blueprint, jsonify, request, send_file

from oncologia.extensions.database import db
from oncologia.extensions.models import Pendency, PendencyStatus
from oncologia.utils import login_required, search_patient_query

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.put("/pendency/<pendency_id>")
@login_required
def update_pendency(pendency_id: int):
    pendency = Pendency.query.get_or_404(pendency_id)
    body = request.get_json()
    status = body.get("status")

    if status is None:
        return (
            jsonify({"status": False, "message": "Status is required"}),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        status_enum = PendencyStatus(status)
    except ValueError:
        return (
            jsonify({"status": False, "message": "Invalid status"}),
            HTTPStatus.BAD_REQUEST,
        )

    pendency.status = status_enum
    db.session.commit()

    return (
        jsonify({"status": True, "message": "Pendency updated"}),
        HTTPStatus.OK,
    )


@bp.get("/download-patients")
@login_required
def download_patients():
    q = request.args.get("q")
    query = search_patient_query(q)
    patients = query.all()

    df = pd.DataFrame([patient.to_json() for patient in patients])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)
    return send_file(
        buffer, as_attachment=True, download_name=f"pacientes.xlsx"
    )
