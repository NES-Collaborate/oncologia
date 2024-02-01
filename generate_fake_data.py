from datetime import date, datetime

import pandas as pd

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

df = pd.read_csv('data/data_oncology.csv')

def create_fake_data_from_df(df):
    with app.app_context():
        total = len(df)
        for _, row in df.iterrows():
            print(f"Inserting patient {_}/{total}...", end="\r", flush=True)
            new_entry_team = EntryTeam.query.filter_by(name=row['Equipe de Entrada']).first()
            if not new_entry_team:
                new_entry_team = EntryTeam(name=row['Equipe de Entrada'])
            new_entry_poin = EntryPoin.query.filter_by(name=row['Porta de Entrada']).first()
            if not new_entry_poin:
                new_entry_poin = EntryPoin(name=row['Porta de Entrada'])

            new_tumor_group = TumorGroup.query.filter_by(name=row['GRUPO DE TUMOR']).first()
            if not new_tumor_group:
                new_tumor_group = TumorGroup(name=row['GRUPO DE TUMOR'])

            new_exam_type = ExamType.query.filter_by(name="Exame de Sangue").first()
            if not new_exam_type:
                new_exam_type = ExamType(name="Exame de Sangue")
            
            new_phone_number1 = PhoneNumber(number="5582994011841", is_wpp=True)

            new_tumor_characterization = TumorCharacterization(
                histological_type_primary_tumor=str(row['LOCAL']),
                staging="outro",
                location_distant_metastasis="Localização da metástase a distância (teste)",
                tumor_group=new_tumor_group,
            )


            new_diagnosis_characterization = DiagnosisCharacterization(
                primary_date_consult=datetime.strptime(row['Data Diagnóstico'], '%m/%d/%Y').date() if not pd.isna(row['Data Diagnóstico']) else date(2000, 1, 1),
                entry_poin=new_entry_poin,
                entry_team=new_entry_team,
                diagnosis_exam=new_exam_type,
                diagnosis_date=datetime.strptime(row['Data Diagnóstico'], '%m/%d/%Y').date() if not pd.isna(row['Data Diagnóstico']) else date(2000, 1, 1),
                diagnosis_location=DiagnosisLocation.extern if row["Diagnóstico Interno / Externo"] == "Fora" else DiagnosisLocation.intern,
            )

            new_patient = Patient(
                ghc=int(row['*']),  # Supondo que GHC seja um número
                name="Adeildo Rabello Antônio Costa",
                birthday=date(2006, 1, 1),
                gender=row['Sexo'],
                race="Preto", 
                cpf="00000000000", 
                city="Maceió", 
                state="AL", 
                phones=[new_phone_number1],
                tumor_characterization=new_tumor_characterization,
                diagnosis_characterization=new_diagnosis_characterization,
                cns="12344 (teste)",
            )

            db.session.add(new_patient)
            db.session.commit()
        print("\nDone.")

if __name__ == "__main__":
    create_fake_data_from_df(df)

