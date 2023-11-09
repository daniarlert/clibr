from abc import ABC, abstractmethod

from sqlmodel import Session, SQLModel, select


class BaseRepository(ABC):
    def __init__(self, model_type: SQLModel) -> None:
        self.model_type = model_type

    def get_by_id(self, session: Session, id: int) -> SQLModel | None:
        stmt = select(self.model_type).where(self.model_type.id == id)
        return session.exec(stmt).first()

    @abstractmethod
    def add(self, session: Session, entity) -> None:
        pass

    @abstractmethod
    def update(self, session: Session, entity) -> None:
        pass

    def delete(self, session: Session, id: int) -> None:
        item = self.get_by_id(session, id)
        session.delete(item)

    @abstractmethod
    def list(self, session: Session) -> list[SQLModel]:
        pass
