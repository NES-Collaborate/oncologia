from functools import wraps

import requests
from flask import flash, redirect, session, url_for


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
