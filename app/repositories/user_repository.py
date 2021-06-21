from .base_repository import BaseRepository
from ..models import User


class UserRepository(BaseRepository):

    def __init__(self):
        self.entity = User
