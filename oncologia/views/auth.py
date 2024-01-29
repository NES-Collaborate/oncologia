from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from oncologia.extensions.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["POST", "GET"])
def login():
    if session.get("user_id"):
        return redirect(url_for("home.index"))

    def POST():
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if not user or not user.checkpw(password):
            return flash("Usuário e/ou Senha inválidos", "error")

        session["user_id"] = user.id
        flash("Login efetuado com sucesso", "success")
        return redirect(url_for("home.index"))

    returned = locals().get(request.method, lambda: None)()
    if returned:
        return returned
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.pop("user_id")
    return redirect(url_for("auth.login"))
