import json
from random import choices

from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy.orm import Mapped, mapped_column

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
