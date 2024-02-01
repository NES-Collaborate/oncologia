from oncologia import app
from oncologia.extensions.database import db
from oncologia.extensions.models import EntryPoin, EntryTeam, ExamType, TumorGroup

with app.test_request_context():
    print("Inserting exam types...")

    exam_types = [
        ExamType(name="Anatomopatológico"),
        ExamType(name="Imunohistoquímica"),
        ExamType(name="Imagem"),
        ExamType(name="Outros"),
    ]

    db.session.add_all(exam_types)
    db.session.commit()



    print('Inserting entry poins...')

    entry_poins = [

        EntryPoin(name="Ambulatório"),
        EntryPoin(name="Emergência HCR"),
        EntryPoin(name="Emergência HNSC"),
        EntryPoin(name="Emergência HF"),
        EntryPoin(name="Emergência UPA MS"),
        EntryPoin(name="Transferência"),
    ]

    db.session.add_all(entry_poins)
    db.session.commit()



    print('Inserting entry teams...')

    entry_teams = [
        EntryTeam(name="Cuidados paliativos"),
        EntryTeam(name="Otorrinolaringologia"),
        EntryTeam(name="Cardiologia"),
        EntryTeam(name="Cirurgia Vascular"),
        EntryTeam(name="Gastroenterologia"),
        EntryTeam(name="Cirurgia oncológica"),
        EntryTeam(name="Oncologia clínica"),
        EntryTeam(name="Mastologia"),
        EntryTeam(name="Ginecologia"),
        EntryTeam(name="Urologia"),
        EntryTeam(name="Cirurgia Torácica"),
        EntryTeam(name="Pneumologia"),
        EntryTeam(name="Radiologia Intervencionista"),
        EntryTeam(name="Dermatologia"),
        EntryTeam(name="Odontologia"),
        EntryTeam(name="Oftalmologia"),
        EntryTeam(name="Hematologia"),
        EntryTeam(name="Neurocirurgia"),
        EntryTeam(name="Neurologia"),
        EntryTeam(name="Endocrinologia"),
        EntryTeam(name="Proctologia"),
        EntryTeam(name="Cirurgia do aparelho digestivo"),
        EntryTeam(name="Cirurgia Plástica"),
        EntryTeam(name="Medicina interna"),
        EntryTeam(name="Infectologia"),


    ]


    db.session.add_all(entry_teams)
    db.session.commit()

    print('Inserting tumor groups...')

    tumor_groups = [
        TumorGroup(name="Cabeça e Pescoço"),
        TumorGroup(name="Colorretal"),
        TumorGroup(name="Cutâneo"),
        TumorGroup(name="Digestivo alto"),
        TumorGroup(name="Endocrinológico"),
        TumorGroup(name="Ginecológico"),
        TumorGroup(name="Hematológico"),
        TumorGroup(name="Hepato-Pancreato-Biliar"),
        TumorGroup(name="Mama"),
        TumorGroup(name="Pulmão e Tórax"),
        TumorGroup(name="Sarcoma"),
        TumorGroup(name="SNC"),
        TumorGroup(name="Urológico"),
        TumorGroup(name="Sincrônico"),
        TumorGroup(name="Oftalmológico"),

    ]

    db.session.add_all(tumor_groups)
    db.session.commit()

    