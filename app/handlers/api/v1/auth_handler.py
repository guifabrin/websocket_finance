import json

from .base_handler import BaseHandler
import hashlib
import uuid
from http import HTTPStatus


class AuthHandler(BaseHandler):

    user_repository = NotImplementedError
    session_repository = NotImplementedError

    def initialize(self, user_repository, session_repository):
        self.user_repository = user_repository
        self.session_repository = session_repository

    def post(self, key):
        auth = json.loads(self.request.body)
        user = self.user_repository.get_by_id(auth['username'])
        if (user.password == hashlib.md5(auth['password'].encode()).hexdigest()):
            s_uuid = str(uuid.uuid4())
            self.session_repository.save({
                'uuid': s_uuid,
                'username': auth['username']
            })
            self.write_response(status_code=HTTPStatus.OK, result=s_uuid)
        else:
            self.write_error(status_code=HTTPStatus.UNAUTHORIZED)
