from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = StringField(
        "Senha", validators=[DataRequired()], render_kw={"type": "password"}
    )
