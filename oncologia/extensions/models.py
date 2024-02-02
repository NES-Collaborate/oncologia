import enum
import json
from datetime import date, datetime
from random import choices
from typing import List, Optional

from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from oncologia import app
from oncologia.extensions.database import db


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k == "password":
                v = hashpw(v.encode(), gensalt()).decode("utf-8")
            setattr(self, k, v)

    def checkpw(self, password: str):
        return checkpw(password.encode(), self.password.encode())


class PendencyType(db.Model):
    __tablename__ = "pendency_type"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, name: str):
        self.name = name


class PendencyStatus(enum.Enum):
    pending = 1
    done = 2
    canceled = 3


class Pendency(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_id: Mapped[int] = mapped_column(
        ForeignKey("pendency_type.id"), nullable=False
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.ghc"), nullable=False
    )
    due_date: Mapped[datetime] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[PendencyStatus] = mapped_column(nullable=False)

    # relationships
    type: Mapped[PendencyType] = relationship(
        "PendencyType", backref="pendencies_type", foreign_keys=[type_id]
    )

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class PhoneNumber(db.Model):
    __tablename__ = "phone_number"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(nullable=False)
    is_wpp: Mapped[bool] = mapped_column(nullable=False, default=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("patient.ghc"), nullable=False
    )

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class Patient(db.Model):
    __tablename__ = "patient"

    ghc: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    birthday: Mapped[date] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    race: Mapped[str] = mapped_column(nullable=False)
    cpf: Mapped[str] = mapped_column(nullable=True)
    address: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=False)
    cns: Mapped[str] = mapped_column(nullable=True)
    state: Mapped[str] = mapped_column(nullable=False)
    phones: Mapped[List[PhoneNumber]] = relationship(
        PhoneNumber,
        backref="patient_phone",
    )
    tumor_characterization_id: Mapped[int] = mapped_column(
        ForeignKey("tumor_characterization.id"), nullable=False
    )
    diagnosis_characterization_id: Mapped[int] = mapped_column(
        ForeignKey("diagnosis_characterization.id"), nullable=False
    )

    # relationships
    tumor_characterization = relationship(
        "TumorCharacterization",
        uselist=False,
        foreign_keys=[tumor_characterization_id],
    )

    diagnosis_characterization = relationship(
        "DiagnosisCharacterization",
        uselist=False,
        foreign_keys=[diagnosis_characterization_id],
    )
    pendencies = db.relationship(
        "Pendency",
        backref="patient",
        lazy=True,
        order_by=Pendency.due_date.asc(),
    )
    statuses = relationship(
        "Status",
        backref="patient",
        lazy=True,
        order_by="Status.created_at.desc()",
    )

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not self.statuses:
            self.statuses = [Status(type=StatusType.default)]

    def to_json(self):
        labels = {
            "ghc": "GHC",
            "name": "Nome",
            "birthday": "Data de Nascimento",
            "gender": "Sexo",
            "race": "Raça",
            "cpf": "CPF",
            "address": "Endereço",
            "city": "Cidade",
            "state": "Estado",
            "phones": "Telefones",
        }
        data = {
            labels.get(c.name, c.name): getattr(self, c.name)
            for c in getattr(self, "__table__").columns
            if c.name
            not in (
                "tumor_characterization_id",
                "diagnosis_characterization_id",
                "phones",
                "pendencies",
            )
        }

        data[labels["phones"]] = ",".join(
            [f"{p.number} (wpp: {p.is_wpp})" for p in self.phones]
        )

        data.update(self.tumor_characterization.to_json())
        data.update(self.diagnosis_characterization.to_json())
        return data


class TumorCharacterization(db.Model):
    __tablename__ = "tumor_characterization"

    id: Mapped[int] = mapped_column(primary_key=True)
    histological_type_primary_tumor: Mapped[Optional[str]] = mapped_column(
        nullable=True,
    )
    staging: Mapped[Optional[str]] = mapped_column(nullable=True)
    location_distant_metastasis: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )

    tumor_group_id: Mapped[int] = mapped_column(
        ForeignKey("tumor_group.id"), nullable=False
    )
    tumor_group = relationship("TumorGroup", uselist=False)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        data = {
            "Local do Tumor Primário": f"{self.tumor_group.name} ({self.tumor_group.id})",
            "Tipo Histológico do Tumor Primário (CID)": self.histological_type_primary_tumor,
            "Estadiamento (TNM)": self.staging,
            "Localização da Metastase a Distância": self.location_distant_metastasis,
        }
        return data


class DiagnosisLocation(enum.Enum):
    intern = 1
    extern = 2


class DiagnosisCharacterization(db.Model):
    __tablename__ = "diagnosis_characterization"

    id: Mapped[int] = mapped_column(primary_key=True)

    primary_date_consult: Mapped[date] = mapped_column(nullable=False)
    entry_poin_id: Mapped[int] = mapped_column(
        ForeignKey("entry_poin.id"), nullable=False
    )
    entry_team_id: Mapped[int] = mapped_column(
        ForeignKey("entry_team.id"), nullable=False
    )
    diagnosis_exam_id: Mapped[int] = mapped_column(
        ForeignKey("exam_type.id"), nullable=False
    )
    diagnosis_date: Mapped[date] = mapped_column(nullable=False)
    diagnosis_location: Mapped[DiagnosisLocation] = mapped_column(
        nullable=False
    )

    entry_poin = relationship("EntryPoin", uselist=False)
    entry_team = relationship("EntryTeam", uselist=False)
    diagnosis_exam = relationship("ExamType", uselist=False)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        data = {
            "Data 1a Consulta no Hospital": self.primary_date_consult.strftime(
                "%d/%m/%Y"
            ),
            "Data do Diagnóstico": self.diagnosis_date.strftime("%d/%m/%Y"),
            "Local do Diagnóstico": self.diagnosis_location.value,
            "Exame no Diagnóstico": self.diagnosis_exam.name,
            "Equipe de Entrada": f"{self.entry_team.name} ({self.entry_team.id})",
            "Porta de Entrada": f"{self.entry_poin.name} ({self.entry_poin.id})",
        }
        return data


class ExamType(db.Model):
    """Tipo de exame."""

    __tablename__ = "exam_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, name: str):
        self.name = name


class EntryPoin(db.Model):
    """Porta de entrada."""

    __tablename__ = "entry_poin"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, name: str):
        self.name = name


class EntryTeam(db.Model):
    """Equipe de entrada."""

    __tablename__ = "entry_team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, name: str):
        self.name = name


class TumorGroup(db.Model):
    """Grupo de tumor."""

    __tablename__ = "tumor_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, name: str):
        self.name = name


class TypeTreatment(db.Model):
    """Tipo de tratamento."""

    __tablename__ = "type_treatment"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __init__(self, name: str):
        self.name = name


class StatusType(enum.Enum):
    in_treatment_treaties = "Em Tratamento/Tratados"
    non_melanoma_skin = "Pele Não Melanoma"
    death = "Óbito"
    palliative_care = "Cuidado Paliativo"
    conservative_treatment = "Tratamento Conservador"
    abandonment_refusal = "Abandono ou Recusa de Tratamento"
    treatment_unable_treat = "Sem Condições de Tratamento"
    default = "Aguardando Tratamento"


class Status(db.Model):
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(primary_key=True)
    ghc_patient_ghc: Mapped[int] = mapped_column(ForeignKey("patient.ghc"))
    type: Mapped[StatusType]
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now()
    )
    date_primary_treatment: Mapped[Optional[date]]
    type_treatment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("type_treatment.id")
    )
    entry_team_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("entry_team.id")
    )
    complement: Mapped[Optional[str]]
    time_start_treatment: Mapped[Optional[int]]
    time_arrial_treatment: Mapped[Optional[int]]
    time_radiotherapy: Mapped[Optional[int]]
    date_death: Mapped[Optional[date]]
    place_death: Mapped[Optional[DiagnosisLocation]]
    definition_date: Mapped[Optional[date]]
    note: Mapped[Optional[str]]

    type_treatment: Mapped["TypeTreatment"] = relationship(
        "TypeTreatment", backref="statuses", foreign_keys=[type_treatment_id]
    )
    entry_team: Mapped["EntryTeam"] = relationship(
        "EntryTeam", backref="statuses", foreign_keys=[entry_team_id]
    )

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@app.cli.command("init-db")
def init_db():
    db.drop_all()
    db.create_all()
    user_data = {
        "username": "admin",
        "password": "".join(choices("0123456789abcdef", k=16)),
        "name": "Administrador",
    }

    user = User(**user_data)
    db.session.add(user)
    db.session.commit()
    app.logger.info("Database initialized")
    json.dump(
        user_data, open("credentials.json", "w"), indent=4, ensure_ascii=False
    )
    print(json.dumps(user_data, indent=4))
