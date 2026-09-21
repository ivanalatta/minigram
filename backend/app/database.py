from sqlmodel import Session, SQLModel, create_engine

from .config import DATABASE_URL

# SQLite exige check_same_thread=False porque FastAPI atiende
# cada request en un hilo distinto. Con Postgres no aplica.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependencia de FastAPI: abre una sesión por request y la cierra al terminar."""
    with Session(engine) as session:
        yield session
