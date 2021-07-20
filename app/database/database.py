from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql

engine = create_engine("mysql+pymysql://root:924687Gui$@localhost:3306/dracma?charset=utf8mb4" ,
                        pool_size=20000, max_overflow=0)

Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def clean():
    Base.metadata.drop_all(engine)


def create():
    Base.metadata.create_all(engine)
