from functools import wraps
from typing import Optional

import requests
from flask import flash, redirect, session, url_for
from sqlalchemy import or_

from oncologia.extensions.models import Patient


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
