from sqlalchemy import Table, Column, Integer, String
from sqlalchemy_serializer import SerializerMixin

from ..database.database import Base


class User(Base, SerializerMixin):

    __tablename__ = "users"

    username = Column(String, unique=True, primary_key=True)
    password = Column(String)

    def update(self, other):
        self.username = other.username
        self.password = other.password

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.username == other.username and \
            self.password == other.password
