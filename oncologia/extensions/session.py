from flask import Flask

from flask_session import Session

sesh = Session()


def init_app(app: Flask):
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = False

    sesh.init_app(app)
