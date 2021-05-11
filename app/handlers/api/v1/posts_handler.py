from .crud_handler import CrudHandler


class PostsHandler(CrudHandler):
    def initialize(self, repository):
        self.repository = repository
