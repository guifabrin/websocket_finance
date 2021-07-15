import datetime
import json
from contextlib import contextmanager

from ..models import Notification
from ..database.database import Session


class BaseRepository:
    entity = NotImplementedError
    def_notification = NotImplementedError

    def __init__(self, entity, def_notification=None):
        self.entity = entity
        self.def_notification = def_notification

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
            # session.close()
            pass

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
            # session.close()
            pass

    def get_by(self, parameter, value):
        with self.command_session_scope() as session:
            result = session.query(self.entity).filter(getattr(self.entity, parameter) == value).all()
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
        if self.def_notification is not None:
            self.def_notification(entity)
        return entity

    def put(self, entity_id, values):
        with self.command_session_scope() as session:
            _entity = session.query(self.entity).get(entity_id)
            _entity.update(values)
            return True
