from sqlmodel import create_engine, Session
from app.settings import settings
from fastapi import Depends
from typing import Annotated


db_url = (f'postgresql://{settings.postgres_user}:{settings.postgres_password}@'
          f'{settings.postgres_server}:{settings.postgres_port}/{settings.postgres_db}')


engine = create_engine(db_url)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
