import datetime

from flask import Flask
from wtforms import BooleanField
from wtforms.fields.form import FormField


def _get_nav_pages():
    return [
        ("home.index", "Home", "home"),
        ("patient.create", "Adicionar Paciente", "user-plus"),
        ("home.search_patient", "Buscar Pacientes", "search"),
    ]


def _get_types(_type: str):
    types = {"form_field": FormField, "boolean_field": BooleanField}
    return types.get(_type, type(None))


def _clsx(*args):
    base = []
    for arg in args:
        if isinstance(arg, str) and arg:
            base.append(arg)
        elif isinstance(arg, (list, tuple)) and len(arg) == 2 and arg[1]:
            base.append(arg[0])
        elif isinstance(arg, dict) and all(arg.values()):
            base.extend(list(arg.keys()))
        else:
            pass
    return " ".join(base)


def _translator(text: str):
    translations = {
        "extern": "Externo",
        "intern": "Interno",
        "pending": "Pendente",
        "done": "Concluído",
        "canceled": "Cancelado",
    }
    return translations.get(text, text)


utils = {
    "get_navigation_pages": _get_nav_pages,
    "today": lambda: datetime.datetime.now().strftime("%d/%m/%Y"),
    "isinstance": isinstance,
    "types": _get_types,
    "clsx": _clsx,
    "translator": _translator,
    "all": all,
}


def init_app(app: Flask):
    app.jinja_env.globals.update(**utils)
