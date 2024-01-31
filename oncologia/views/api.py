from http import HTTPStatus

from flask import Blueprint, jsonify, request

from oncologia.extensions.database import db
from oncologia.extensions.models import Pendency, PendencyStatus
from oncologia.utils import login_required

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
