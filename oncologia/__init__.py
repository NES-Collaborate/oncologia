from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "oncologia"  # TODO: generate secret key

app.config["APP_NAME"] = __name__.capitalize()

# app factory
exts = ["database", "session", "jija_utils"]
for ext in exts:
    module = __import__(f"{__name__}.extensions.{ext}", fromlist=[ext])
    module.init_app(app)

views = ["auth", "home", "patient", "api", "plots"]
for view in views:
    module = __import__(f"{__name__}.views.{view}", fromlist=[view])
    app.register_blueprint(module.bp)
