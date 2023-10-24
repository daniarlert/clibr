import tomllib
from pathlib import Path

import typer
from sqlmodel import Session, SQLModel, create_engine


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load()

        return cls._instance

    def load(self):
        with open("./pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            poetry = data["tool"]["poetry"]

            self.app_name = poetry["name"]
            self.app_version = poetry["version"]
            self.app_description = poetry["description"]

        self.app_dir = typer.get_app_dir(self.app_name)
        self.db_path: Path = Path(self.app_dir) / "clibr.db"
        Path(self.app_dir).mkdir(parents=True, exist_ok=True)

        sqlite_url = f"sqlite:///{self.db_path}"
        self.db_engine = create_engine(sqlite_url)
        SQLModel.metadata.create_all(self.db_engine)

        self.session = Session(self.db_engine)

    def close(self):
        self.session.close_all()
