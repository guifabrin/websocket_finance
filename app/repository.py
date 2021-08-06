from contextlib import contextmanager

from app.database import session


class BaseRepository:
    entity = NotImplementedError

    def __init__(self, entity):
        self.entity = entity

    def get_by(self, parameter, value):
        return session.query(self.entity).filter(getattr(self.entity, parameter) == value).all()

    def get_by_id(self, entity_id):
        return session.query(self.entity).get(entity_id)

    def get_all(self):
        return session.query(self.entity).all()

    def save(self, entity):
        session.add(entity)
        try:
            session.commit()
        except:
            session.rollback()
        session.flush()
        return entity

    def put(self, entity_id, values):
        _entity = session.query(self.entity).get(entity_id)
        _entity.update(values)
        session.commit()
        return True

    def delete(self, entity_id):
        entity = session.query(self.entity).get(entity_id)
        session.delete(entity)
        session.commit()
        return True
