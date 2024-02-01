from datetime import date

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, FormField, SelectField, StringField
from wtforms.validators import DataRequired

from oncologia.extensions.models import (
    EntryPoin,
    EntryTeam,
    ExamType,
    TumorGroup,
)
from oncologia.utils import get_website_agent


class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = StringField(
        "Senha", validators=[DataRequired()], render_kw={"type": "password"}
    )


class PhoneForm(FlaskForm):
    number = StringField(
        "Telefone",
        validators=[DataRequired(message="O telefone é obrigatório")],
        render_kw={"placeholder": "(00) 00000-0000"},
    )
    is_wpp = BooleanField("Whatsapp?", default=False)


class TumorCharacterizationForm(FlaskForm):
    tumor_group = SelectField(
        "Local do Tumor Primário",
        choices=[],
        validators=[DataRequired()],
        render_kw={"data-loader": "TumorGroup"},
    )
    histological_type_primary_tumor = StringField(
        "Tipo Histológico do Tumor Pirmário (CID)",
    )
    staging = StringField("Estadiamento (TNM)")
    location_distant_metastasis = StringField(
        "Localização da Metástase a Distância"
    )

    def __init__(self, *args, **kwargs):
        super(TumorCharacterizationForm, self).__init__(*args, **kwargs)
        self.__load_tumor_groups()

    def __load_tumor_groups(self):
        setattr(
            self.tumor_group,
            "choices",
            [
                (tumor_group.id, tumor_group.name)
                for tumor_group in TumorGroup.query.all()
            ],
        )


class DiagnosisCharacterizationForm(FlaskForm):
    primary_date_consult = DateField(
        "Data 1ª Consulta no Hospital",
        validators=[DataRequired()],
    )
    entry_poin = SelectField(
        "Porta de Entrada",
        choices=[],
        validators=[DataRequired()],
        render_kw={"data-loader": "EntryPoin"},
    )
    entry_team = SelectField(
        "Equipe de Entrada",
        choices=[],
        validators=[DataRequired()],
        render_kw={"data-loader": "EntryTeam"},
    )
    diagnosis_date = DateField(
        "Data do Diagnóstico",
        validators=[DataRequired("Campo obrigatório")],
    )
    diagnosis_exam = SelectField(
        "Exame no Diagnóstico",
        choices=[],
        validators=[DataRequired()],
        render_kw={"data-loader": "ExamType"},
    )
    diagnosis_location = SelectField(
        "Local do Diagnóstico",
        choices=[("1", "Interno"), ("2", "Externo")],
        validators=[DataRequired()],
    )

    def __init__(self, *args, **kwargs):
        super(DiagnosisCharacterizationForm, self).__init__(*args, **kwargs)
        self.__load_entry_poin()
        self.__load_entry_team()
        self.__load_exam_type()

    def __load_exam_type(self):
        setattr(
            self.diagnosis_exam,
            "choices",
            [(exam.id, exam.name) for exam in ExamType.query.all()],
        )

    def __load_entry_poin(self):
        setattr(
            self.entry_poin,
            "choices",
            [(entry.id, entry.name) for entry in EntryPoin.query.all()],
        )

    def __load_entry_team(self):
        setattr(
            self.entry_team,
            "choices",
            [(team.id, team.name) for team in EntryTeam.query.all()],
        )


class PatientForm(FlaskForm):
    ghc = StringField(
        "HGC", validators=[DataRequired(message="O HGC é obrigatório")]
    )
    name = StringField(
        "Nome", validators=[DataRequired(message="O nome é obrigatório")]
    )
    birthday = DateField(
        "Data de Nascimento",
        validators=[DataRequired(message="A data de nascimento é obrigatória")],
        # default=date(2000, 1, 1),
        # format="%d/%m/%Y",
        render_kw={"placeholder": "dd/mm/YYYY"},
    )

    gender = SelectField(
        "Sexo",
        choices=[("M", "Masculino"), ("F", "Feminino")],
        validators=[DataRequired()],
    )
    race = SelectField(
        "Raça",
        choices=[
            ("Branca", "Branca"),
            ("Preta", "Preta"),
            ("Amarela", "Amarela"),
            ("Parda", "Parda"),
            ("Indígena", "Indígena"),
            ("Não Informado", "Não Informado"),
            ("Ignorado", "Ignorado"),
        ],
        validators=[DataRequired()],
        default="Não Informado",
    )
    cpf = StringField("CPF")
    address = StringField("Endereço")
    city = StringField(
        "Cidade",
        # choices=[],
        validators=[DataRequired()],
        render_kw={"class": "city-selector"},
    )
    state = SelectField(
        "Estado",
        choices=[],
        validators=[DataRequired()],
        render_kw={"class": "state-selector"},
    )
    phone_1 = FormField(PhoneForm, label="Telefone 1")
    phone_2 = FormField(PhoneForm, label="Telefone 2")
    tumor_characterization = FormField(
        TumorCharacterizationForm, label="Carecterização do Tumor"
    )
    diagnosis_characterization = FormField(
        DiagnosisCharacterizationForm, label="Caraterização do Diagnóstico"
    )

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        self.__load_states()

    def __load_states(self):
        setattr(self.state, "choices", self.get_state_choices())

    def get_state_choices(self):
        sesh = get_website_agent()
        response = sesh.get(
            "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
        )
        if response.status_code == 200:
            states = response.json()
            return [
                (state["id"], f"{state['nome']} ({state['sigla']})")
                for state in states
            ]
        return []
