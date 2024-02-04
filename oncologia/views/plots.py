from flask import Blueprint, render_template

from oncologia.utils import login_required

bp = Blueprint("plots", __name__, url_prefix="/plots")


@bp.route("/")
@login_required
def index():
    plots = [
        {
            "title": "Grupo de Tumores por tempo até 1º tratamento",
            "endpoint": "api.plot_bar_tumor_group",
        },
        {
            "title": "Tipo de Tumor por tempo até 1º tratamento",
            "endpoint": "api.plot_pie_chart",
        },
        {
            "title": "Tempo do 1º tratamento em relação a entrada",
            "endpoint": "api.plot_entry_poin_status",
        },
        {
            "title": "Porcentagem de diagnosticos no GHC e Fora por Grupo de Tumor",
            "endpoint": "api.plot_disgnosis_per_tumor",
        },
    ]
    return render_template("plots/index.html", plots=plots)
