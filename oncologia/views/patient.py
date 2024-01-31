from flask import Blueprint, request

bp = Blueprint("patient", __name__, url_prefix="/patient")


@bp.route("/profile")
def profile():
    patient_id = request.args.get("id")

    return f"Profile {patient_id}"
