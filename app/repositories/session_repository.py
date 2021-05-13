from .base_repository import BaseRepository
from ..models.session import Session


class SessionRepository(BaseRepository):
    entity = Session
