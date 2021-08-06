from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine("sqlite:///database.sqlite")

session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


def clean():
    Base.metadata.drop_all(engine)


def create():
    Base.metadata.create_all(engine)
