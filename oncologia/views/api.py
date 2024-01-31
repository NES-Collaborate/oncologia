from flask import Blueprint, jsonify, request

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.put("/pendency/<pendency_id>")
def update_pendency(pendency_id):
    return jsonify({"pendency_id": pendency_id})
