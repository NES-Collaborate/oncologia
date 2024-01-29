from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Faça login antes de acessar esta página!", "error")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper
