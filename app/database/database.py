from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///database.sqlite")

Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def clean():
    Base.metadata.drop_all(engine)


def create():
    Base.metadata.create_all(engine)
