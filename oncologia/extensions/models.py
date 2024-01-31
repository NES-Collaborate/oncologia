import enum
import json
from datetime import date, datetime
from random import choices
from typing import List

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
        ForeignKey("user.id"), nullable=False
    )
    due_date: Mapped[datetime] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[PendencyStatus] = mapped_column(nullable=False)

    # relationships
    type: Mapped[PendencyType] = relationship(
        "PendencyType", backref="pendencies_type", foreign_keys=[type_id]
    )
    # TODO: Create a relationship with "Patient" table instead
    patient: Mapped["User"] = relationship(
        "User", backref="pendencies_patient", foreign_keys=[patient_id]
    )


class PhoneNumber(db.Model):
    __tablename__ = "phone_number"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(nullable=False)
    is_wpp: Mapped[bool] = mapped_column(nullable=False, default=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("patient.ghc"), nullable=False
    )


class Patient(db.Model):
    __tablename__ = "patient"

    ghc: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    date_of_birth: Mapped[date] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    race: Mapped[str] = mapped_column(nullable=False)
    cpf: Mapped[str]
    address: Mapped[str]
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)
    phones: Mapped[List[PhoneNumber]] = relationship(
        PhoneNumber, backref="patient"
    )

    cns: Mapped[str]


class TumorCharacterization(db.Model):
    __tablename__ = "tumor_characterization"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_ghc: Mapped[int] = mapped_column(ForeignKey("patient.ghc"))
    primary_tumor_location: Mapped[str] = mapped_column(nullable=False)
    histological_type_primary_tumor: Mapped[str]
    staging: Mapped[str]
    location_distant_metastasis: Mapped[str]

    patient = relationship("Patient", backref="tumor_characterization")


class DiagnosisCharacterization(db.Model):
    __tablename__ = "diagnosis_characterization"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_ghc: Mapped[int] = mapped_column(ForeignKey("patient.ghc"))
    primary_date_conclusion: Mapped[date] = mapped_column(nullable=False)
    entry_poin: Mapped[str] = mapped_column(nullable=False)
    entray_team: Mapped[str] = mapped_column(nullable=False)
    date_diagnosis: Mapped[date] = mapped_column(nullable=False)
    diagnostic_examination: Mapped[str] = mapped_column(nullable=False)
    diagnosis_location: Mapped[str] = mapped_column(nullable=False)

    patient = relationship("Patient", backref="diagnosis_characterization")


class EntryPoin(db.Model):
    __tablename__ = "entry_poin"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


class EntreyTeam(db.Model):
    __tablename__ = "entry_team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


class TumosrGroup(db.Model):
    __tablename__ = "tumor_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


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
    print(json.dumps(user_data, indent=4))
