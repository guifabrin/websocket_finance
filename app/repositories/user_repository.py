from .base_repository import BaseRepository
from ..models.user import User


class UserRepository(BaseRepository):
    entity = User
