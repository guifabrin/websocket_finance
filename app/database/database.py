from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///../tornado_api_finance_automated/database.sqlite",
                       connect_args={'check_same_thread': False})

Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def clean():
    Base.metadata.drop_all(engine)


def create():
    Base.metadata.create_all(engine)
