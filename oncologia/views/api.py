import io
from http import HTTPStatus

import pandas as pd
from flask import Blueprint, jsonify, request, send_file
from matplotlib import use as use_matplotlib

from oncologia.extensions.database import db
from oncologia.extensions.jija_utils import _translator
from oncologia.extensions.models import (
    Patient,
    Pendency,
    PendencyStatus,
    StatusType,
)
from oncologia.utils import (
    create_separate_figure,
    login_required,
    save_figure_to_buffer,
    search_patient_query,
)

use_matplotlib("agg")
bp = Blueprint("api", __name__, url_prefix="/api")


@bp.put("/pendency/<pendency_id>")
@login_required
def update_pendency(pendency_id: int):
    pendency = Pendency.query.get_or_404(pendency_id)
    body = request.get_json()
    status = body.get("status")

    if status is None:
        return (
            jsonify({"status": False, "message": "Status is required"}),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        status_enum = PendencyStatus(status)
    except ValueError:
        return (
            jsonify({"status": False, "message": "Invalid status"}),
            HTTPStatus.BAD_REQUEST,
        )

    pendency.status = status_enum
    db.session.commit()

    return (
        jsonify({"status": True, "message": "Pendency updated"}),
        HTTPStatus.OK,
    )


@bp.get("/download-patients")
@login_required
def download_patients():
    q = request.args.get("q")
    query = search_patient_query(q)
    patients = query.all()

    df = pd.DataFrame([patient.to_json() for patient in patients])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)
    return send_file(
        buffer, as_attachment=True, download_name=f"pacientes.xlsx"
    )


@bp.get("/plot-bar-tumor-group")
@login_required
def plot_bar_tumor_group():
    patients = Patient.query.all()
    patients_specified = [
        patient
        for patient in patients
        if patient.statuses[0].type == StatusType.in_treatment_treated
    ]

    df_data = [
        {
            "Tempo de TTO": (
                patient.statuses[0].date_primary_treatment
                - patient.diagnosis_characterization.diagnosis_date
            ).days,
            "GRUPO DE TUMOR": patient.tumor_characterization.tumor_group.name,
        }
        for patient in patients_specified
    ]

    df = pd.DataFrame(df_data)

    df = df.dropna(subset=["Tempo de TTO"])
    df["Tempo de TTO"] = pd.to_numeric(df["Tempo de TTO"], errors="coerce")

    bins = range(0, 200, 10)
    df["interval"] = pd.cut(df["Tempo de TTO"], bins=bins, right=False)
    grouped_data = (
        df.groupby(["interval", "GRUPO DE TUMOR"]).size().unstack(fill_value=0)
    )

    fig = create_separate_figure()
    ax = fig.add_subplot(111)
    grouped_data.plot(kind="bar", stacked=True, colormap="tab20", ax=ax)

    # Set labels and title
    ax.set_xlabel("Intervalos (em dias)")
    ax.set_ylabel("Número de pacientes")
    ax.set_title("Grupo de Tumores por tempo até 1º tratamento")

    # Display the legend
    ax.legend(title="GRUPO DE TUMOR")

    return jsonify(
        {
            "content": save_figure_to_buffer(fig),
        }
    )


@bp.get("/plot-pie-chart")
@login_required
def plot_pie_chart():
    command, arg = map(str.lower, request.args.get("command", "Até 60").split())
    patients = Patient.query.all()
    patients_specified = [
        patient
        for patient in patients
        if patient.statuses[0].type == StatusType.in_treatment_treated
    ]

    df_data = [
        {
            "Tempo de TTO": (
                patient.statuses[0].date_primary_treatment
                - patient.diagnosis_characterization.diagnosis_date
            ).days,
            "GRUPO DE TUMOR": patient.tumor_characterization.tumor_group.name,
        }
        for patient in patients_specified
    ]
    df = pd.DataFrame(df_data)

    if command == "de":
        filtered_df = df[(df["Tempo de TTO"] >= int(arg))]
        count_tumores = filtered_df["GRUPO DE TUMOR"].value_counts()
    elif command == "até":
        filtered_df = df[(df["Tempo de TTO"] <= int(arg))]
        count_tumores = filtered_df["GRUPO DE TUMOR"].value_counts()
    else:
        return jsonify({"status": False, "message": "Command invalid"})

    fig = create_separate_figure()
    ax = fig.add_subplot(111)
    count_tumores.plot(kind="pie", stacked=True, colormap="Paired", ax=ax)
    ax.set_title(f"GRUPO DE TUMOR | {arg} dias")

    return jsonify(
        {
            "content": save_figure_to_buffer(fig),
        }
    )


@bp.get("/plot-entry-poin-status")
@login_required
def plot_entry_poin_status():
    tempo_de_tto = request.args.get("tto", 60, type=int)
    patients = Patient.query.all()
    patients_specified = [
        patient
        for patient in patients
        if patient.statuses[0].type == StatusType.in_treatment_treated
    ]
    df = pd.DataFrame(
        [
            {
                "Tempo de TTO": (
                    patient.statuses[0].date_primary_treatment
                    - patient.diagnosis_characterization.diagnosis_date
                ).days,
                "Porta de Entrada": patient.diagnosis_characterization.entry_poin.name,
            }
            for patient in patients_specified
        ]
    )

    more_than = df[df["Tempo de TTO"] >= tempo_de_tto]
    less_than = df[df["Tempo de TTO"] < tempo_de_tto]

    count_more_than = more_than["Porta de Entrada"].value_counts()
    count_less_than = less_than["Porta de Entrada"].value_counts()

    percent_more_than = pd.Series(
        [
            count_more_than[value] / count_more_than.sum()
            for value in count_more_than.index
        ],
        index=count_more_than.index,
    )

    percent_less_than = pd.Series(
        [
            count_less_than[value] / count_less_than.sum()
            for value in count_less_than.index
        ],
        index=count_less_than.index,
    )
    fig = create_separate_figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    labels = df["Porta de Entrada"].unique().tolist()

    ax1.pie(
        percent_more_than,
        labels=[f"{round(i, 2)}%" for i in percent_more_than.unique()],
    )
    ax1.set_title(f"Acima de {tempo_de_tto} dias")

    ax2.pie(
        percent_less_than,
        labels=[f"{round(i, 2)}%" for i in percent_less_than.unique()],
    )
    ax2.set_title(f"Menor que {tempo_de_tto} dias")
    ax1.legend(labels, loc="upper left")

    fig.suptitle("Tempo do 1º tratamento em relação a entrada")
    # plt.tight_layout()

    return jsonify(
        {
            "content": save_figure_to_buffer(fig),
        }
    )


@bp.get("/plot-disgnosis-per-tumor")
@login_required
def plot_disgnosis_per_tumor():
    patients = Patient.query.all()

    df = pd.DataFrame(
        [
            {
                "GRUPO DE TUMOR": patient.tumor_characterization.tumor_group.name,
                "Diagnóstico Interno / Externo": _translator(
                    patient.diagnosis_characterization.diagnosis_location.name
                ),
            }
            for patient in patients
        ]
    )
    df = df.dropna(subset=["GRUPO DE TUMOR", "Diagnóstico Interno / Externo"])
    # group data
    grouped_df = (
        df.groupby(["GRUPO DE TUMOR", "Diagnóstico Interno / Externo"])
        .size()
        .unstack(fill_value=0)
    )
    grouped_df_percentage = grouped_df.div(grouped_df.sum(axis=1), axis=0) * 100

    fig = create_separate_figure()
    ax = fig.add_subplot(111)
    # Plotting the stacked bar graph
    grouped_df_percentage.plot(
        kind="bar", stacked=True, color=["red", "blue"], width=0.8, ax=ax
    )
    ax.set_xlabel("Grupos de Tumores")
    ax.set_ylabel("Percentage")
    ax.set_title("Porcentagem de diagnosticos no GHC e Fora por Grupo de Tumor")
    ax.legend(
        title="Externo/Interno",
        labels=df["Diagnóstico Interno / Externo"].unique(),
    )
    ax.set_ylim(0, 100)

    return jsonify(
        {
            "content": save_figure_to_buffer(fig),
        }
    )
