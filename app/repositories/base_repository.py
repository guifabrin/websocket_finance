from contextlib import contextmanager

from ..exceptions.entity_not_found import EntityNotFound
from ..database.database import Session


class BaseRepository():

    entity = NotImplementedError

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

    def get_all(self):
        with self.query_session_scope() as session:
            return session.query(self.entity).all()

    def get_by_id(self, entity_id):
        with self.command_session_scope() as session:
            result = session.query(self.entity).get(entity_id)
            if not result:
                raise EntityNotFound
            return result

    def save(self, entity):
        with self.command_session_scope() as session:
            return session.add(self.entity(**entity))

    def put(self, entity_id, entity):
        with self.command_session_scope() as session:
            _entity = session.query(self.entity).get(entity_id)
            if not _entity:
                raise EntityNotFound
            _entity.update(self.entity(**entity))
            return True

    def delete(self, entity_id):
        with self.command_session_scope() as session:
            entity = session.query(self.entity).get(entity_id)
            if not entity:
                raise EntityNotFound
            session.delete(entity)
            return True
