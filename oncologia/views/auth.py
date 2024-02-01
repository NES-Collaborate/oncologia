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
from oncologia.forms import LoginForm

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if session.get("user_id"):
        return redirect(url_for("home.index"))

    def POST():
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if not user or not user.checkpw(form.password.data):
                flash("Usuário e/ou Senha inválidos", "error")
                return
            session["user_id"] = getattr(user, "id")
            flash("Login efetuado com sucesso", "success")
            return redirect(url_for("home.index"))

    returned = locals().get(request.method, lambda: None)()
    if returned:
        return returned
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
def logout():
    session.pop("user_id")
    return redirect(url_for("auth.login"))
