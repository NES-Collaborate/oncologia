from flask import Flask

# app factory
from oncologia.extensions.database import init_app as init_app_db
from oncologia.extensions.session import init_app as init_app_session

app = Flask(__name__)
app.config["SECRET_KEY"] = "oncologia"  # TODO: generate secret key

app.config["APP_NAME"] = __name__.capitalize()

init_app_db(app)
init_app_session(app)

views = ["auth", "home"]
for view in views:
    module = __import__(f"{__name__}.views.{view}", fromlist=[view])
    app.register_blueprint(module.bp)
