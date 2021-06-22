from contextlib import contextmanager

from ..database.database import Session
from ..exceptions.entity_not_found import EntityNotFound


class BaseRepository:
    entity = NotImplementedError

    def __init__(self, entity):
        self.entity = entity

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

    def get_all(self, user=None):
        with self.query_session_scope() as session:
            all = session.query(self.entity).all()
            if user:
                if len(list(filter(lambda role: role.id == 1, user.roles))) > 0:
                    return all
                return list(filter(lambda item: item.user_id == user.id, all))
            else:
                return all

    def get_by(self, parameter, value, user=None, b_raise=True):
        with self.command_session_scope() as session:
            if user:
                result = session.query(self.entity).filter(
                    getattr(self.entity, parameter) == value and self.entity.user == user).scalar()
            else:
                result = session.query(self.entity).filter(getattr(self.entity, parameter) == value).scalar()
            if not result and b_raise:
                raise EntityNotFound
            elif not result and not b_raise:
                return None
            return result

    def get_by_id(self, entity_id, user=None):
        with self.command_session_scope() as session:
            if user:
                if hasattr(self.entity, 'user'):
                    list_transactions = list(
                        filter(lambda transaction: transaction.id == int(entity_id), self.get_all(user)));
                    if len(list_transactions) > 0:
                        result = list_transactions[0]
                elif len(list(filter(lambda role: role.id == 1, user.roles))) > 0:
                    result = session.query(self.entity).get(entity_id)
            if not result:
                raise EntityNotFound
            return result

    def get_by_id_root(self, entity_id):
        with self.command_session_scope() as session:
            result = session.query(self.entity).get(entity_id)
            if not result:
                raise EntityNotFound
            return result

    def save(self, entity, user=None):
        with self.command_session_scope() as session:
            flushed = self.entity(**entity)
            if user:
                flushed.user = user
            session.add(flushed)
            session.flush()
            return flushed

    def save_root(self, entity):
        with self.command_session_scope() as session:
            session.add(entity)
            session.flush()
            return entity

    def put(self, entity_id, entity, user):
        _entity = self.get_by_id(entity_id, user)
        if not _entity:
            raise EntityNotFound
        _entity.update(self.entity(**entity))
        with self.command_session_scope() as session:
            session.query(self.entity).filter(self.entity.id == _entity.id).update(entity)
            session.flush()
        return True

    def delete(self, entity_id, user):
        with self.command_session_scope() as session:
            entity = self.get_by_id(entity_id, user)
            if not entity:
                raise EntityNotFound
            session.delete(entity)
            return True
