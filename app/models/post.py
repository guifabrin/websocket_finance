from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

from ..database.database import Base
from .user import User


class Post(Base, SerializerMixin):

    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String, ForeignKey(User.username))
    created = Column(DateTime, default=datetime.utcnow)
    title = Column(String)
    body = Column(String)

    def update(self, other):
        self.title = other.title
        self.body = other.body

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.post_id == other.post_id and \
            self.author == other.author and \
            self.created == other.created and \
            self.title == other.title and \
            self.body == other.body
