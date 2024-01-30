import datetime

from flask import Flask


def __get_nav_pages():
    return [
        ("home.index", "Home", "home"),
        ("auth.login", "Login", "lock"),
    ]


utils = {
    "get_navigation_pages": __get_nav_pages,
    "today": lambda: datetime.datetime.now().strftime("%d/%m/%Y"),
}


def init_app(app: Flask):
    app.jinja_env.globals.update(**utils)
