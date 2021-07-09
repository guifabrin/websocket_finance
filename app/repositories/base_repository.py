import datetime
import json
from contextlib import contextmanager

from ..models import Notification
from ..database.database import Session


class BaseRepository:
    entity = NotImplementedError
    notification_repository = NotImplementedError

    def __init__(self, entity, notification_repository = None):
        self.entity = entity
        self.notification_repository = notification_repository

    @contextmanager
    def command_session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = Session()
        try:
            yield session
            session.commit()
        except Exception as err:
            session.rollback()
            raise
        finally:
            session.expunge_all()
            session.close()

    @contextmanager
    def query_session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = Session()
        session.expire_on_commit = False
        try:
            yield session
        except Exception as err:
            raise
        finally:
            session.close()

    def get_by(self, parameter, value):
        with self.command_session_scope() as session:
            result = session.query(self.entity).filter(getattr(self.entity, parameter) == value).scalar()
            session.commit()
            return result

    def get_by_id(self, entity_id):
        with self.command_session_scope() as session:
            result = session.query(self.entity).get(entity_id)
            return result

    def get_all(self):
        with self.command_session_scope() as session:
            result = session.query(self.entity).all()
            return result

    def save(self, entity):
        with self.command_session_scope() as session:
            session.add(entity)
            session.flush()
        if self.notification_repository is not None:
            notification = Notification()
            notification.date = datetime.datetime.now()
            notification.table = type(entity).__name__
            notification.entity_id = entity.id
            notification.method = 'save'
            notification.seen = False
            self.notification_repository.save(notification)
        return entity
