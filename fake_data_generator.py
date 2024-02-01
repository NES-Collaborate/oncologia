from datetime import date

from oncologia import app
from oncologia.extensions.database import db
from oncologia.extensions.models import (
    DiagnosisCharacterization,
    DiagnosisLocation,
    EntryPoin,
    EntryTeam,
    ExamType,
    Patient,
    PhoneNumber,
    TumorCharacterization,
    TumorGroup,
)


def create_fake_data():
    with app.app_context():
        new_entry_team = EntryTeam(name="Equipe de Entrada Teste")
        new_entry_poin = EntryPoin(name="Porta de Entrada Teste")
        new_tumor_group = TumorGroup(name="Grupo de Tumor Teste")
        new_exam_type = ExamType(name="Exame de Sangue")
        new_phone_number1 = PhoneNumber(number="5582994011841", is_wpp=True)
        new_tumor_characterization = TumorCharacterization(
            histological_type_primary_tumor="pika",
            staging="outro",
            location_distant_metastasis="teste de localização",
            tumor_group=new_tumor_group,
        )
        new_diagnosis_characterization = DiagnosisCharacterization(
            primary_date_consult=date.today(),
            entry_poin=new_entry_poin,
            entry_team=new_entry_team,
            diagnosis_exam=new_exam_type,
            diagnosis_date=date.today(),
            diagnosis_location=DiagnosisLocation.extern,
        )
        new_patient = Patient(
            ghc=122345,
            name="Felipe Adeildo",
            birthday=date(2008, 8, 8),
            gender="M",
            race="Branca",
            cpf="100448904486",
            city="Maceió",
            state="Alagoas",
            phones=[new_phone_number1],
            tumor_characterization=new_tumor_characterization,
            diagnosis_characterization=new_diagnosis_characterization,
            cns="1234",
        )

        db.session.add(new_patient)
        db.session.commit()


if __name__ == "__main__":
    create_fake_data()
