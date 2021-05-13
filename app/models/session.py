from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

from ..database.database import Base
from .user import User


class Session(Base, SerializerMixin):

    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey(User.username))
    created = Column(DateTime, default=datetime.utcnow)
    uuid = Column(String)
