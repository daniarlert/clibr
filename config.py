import tomllib
from pathlib import Path

import typer
from sqlmodel import SQLModel, create_engine


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

            self.APP_NAME = poetry["name"]
            self.APP_VERSIOn = poetry["version"]
            self.APP_SHORT_DESCRIPTION = poetry["description"]

        self.DEBUG = False

        self.APP_DIR = typer.get_app_dir(self.APP_NAME)
        self.DB_PATH: Path = Path(self.APP_DIR) / "clibr.db"
        Path(self.APP_DIR).mkdir(parents=True, exist_ok=True)

        sqlite_url = f"sqlite:///{self.DB_PATH}"
        self.DB_ENGINE = create_engine(sqlite_url)
        SQLModel.metadata.create_all(self.DB_ENGINE)
