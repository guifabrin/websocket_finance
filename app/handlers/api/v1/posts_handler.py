from .crud_handler import CrudHandler
import base64
from http import HTTPStatus


class PostsHandler(CrudHandler):

    repository = NotImplementedError
    session_repository = NotImplementedError

    def initialize(self, repository, session_repository):
        self.repository = repository
        self.session_repository = session_repository

    def get(self, key):
        try:
            token_bytes = self.request.headers.get(
                'Authorization').encode('utf-8')
            user_token = base64.b64decode(
                token_bytes).decode('utf-8').split(sep=':')
            result = [session for session in self.session_repository.get_all(
            ) if session.uuid == user_token[1] and session.username == user_token[0]]
            if len(result) > 0:
                return super().get(key)
        finally:
            self.write_response(HTTPStatus.UNAUTHORIZED)
