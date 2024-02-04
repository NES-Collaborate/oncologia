import datetime

from flask import Flask
from wtforms import BooleanField
from wtforms.fields.form import FormField

from oncologia.extensions.models import DiagnosisLocation, Patient, StatusType


def _get_nav_pages():
    return [
        ("home.index", "Home", "home"),
        ("patient.create", "Adicionar Paciente", "user-plus"),
        ("home.search_patient", "Buscar Pacientes", "search"),
        ("plots.index", "Graficos", "bar-chart-3"),
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


def _status_fields(status: StatusType):
    data = {
        StatusType.in_treatment_treated: [
            {
                "name": "Data do 1º Tratamento",
                "getter": lambda s: (
                    s.date_primary_treatment.strftime("%d/%m/%Y")
                ),
            },
            {
                "name": "Tipo de Tratamento",
                "getter": lambda s: s.type_treatment.name,
            },
            {
                "name": "Equipe de Tratamento",
                "getter": lambda s: f"{s.entry_team.name} ({s.entry_team.id})",
            },
            {
                "name": "Complemento",
                "getter": lambda s: s.complement or "N/A",
            },
            {
                "name": "Tempo para iniciar tratamento (dias)",
                "getter": lambda s: (
                    s.date_primary_treatment
                    - getattr(
                        Patient.query.filter_by(ghc=s.patient_ghc).first(),
                        "diagnosis_characterization",
                    ).diagnosis_date
                ).days,
            },
            {
                "name": "Tempo para chegada a partir do Diagnóstico (dias)",
                "getter": lambda s: (
                    (
                        getattr(
                            Patient.query.filter_by(ghc=s.patient_ghc).first(),
                            "diagnosis_characterization",
                        ).primary_date_consult
                        - s.date_primary_treatment
                    ).days
                    if getattr(
                        Patient.query.filter_by(ghc=s.patient_ghc).first(),
                        "diagnosis_characterization",
                    ).diagnosis_location
                    == DiagnosisLocation.extern
                    else "N/A"
                ),
            },
            {
                "name": "Tempo para Radioterapia (dias)",
                "getter": lambda s: s.time_radiotherapy or "N/A",
            },
        ],
        StatusType.non_melanoma_skin: [],
        StatusType.death: [
            {
                "name": "Data da Morte",
                "getter": lambda s: s.date_death.strftime("%d/%m/%Y"),
            },
            {
                "name": "Local da Morte",
                "getter": lambda s: _translator(
                    getattr(s, "place_death", "N/A")
                ),
            },
        ],
        StatusType.palliative_care: [
            {
                "name": "Data de Definição",
                "getter": lambda s: s.date_definition.strftime("%d/%m/%Y"),
            },
            {
                "name": "Equipe de Tratamento",
                "getter": lambda s: f"{s.entry_team.name} ({s.entry_team.id})",
            },
        ],
        StatusType.conservative_treatment: [],
        StatusType.abandonment_refusal: [
            {
                "name": "Data de Definição",
                "getter": lambda s: s.definition_date.strftime("%d/%m/%Y"),
            },
            {
                "name": "Observação",
                "getter": lambda s: getattr(s, "note", "N/A"),
            },
        ],
        StatusType.treatment_unable_treat: [],
        StatusType.default: [
            {
                "name": "Aviso",
                "getter": lambda s: "Este é o Status Padrão de um Paciente.",
            },
        ],
    }

    data.update(
        {
            StatusType.non_melanoma_skin: data[StatusType.in_treatment_treated],
            StatusType.conservative_treatment: data[StatusType.palliative_care],
            StatusType.treatment_unable_treat: data[
                StatusType.abandonment_refusal
            ],
        }
    )
    return data[status]


utils = {
    "get_navigation_pages": _get_nav_pages,
    "today": lambda: datetime.datetime.now().strftime("%d/%m/%Y"),
    "isinstance": isinstance,
    "types": _get_types,
    "clsx": _clsx,
    "translator": _translator,
    "all": all,
    "status_fields": _status_fields,
}


def init_app(app: Flask):
    app.jinja_env.globals.update(**utils)
