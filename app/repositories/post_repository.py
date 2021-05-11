from .base_repository import BaseRepository
from ..models.post import Post


class PostRepository(BaseRepository):
    entity = Post
