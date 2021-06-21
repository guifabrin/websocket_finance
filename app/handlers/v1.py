from tornado.web import RequestHandler

from abc import ABC

import basicauth
from app.exceptions.not_allowed import NotAllowed
import json

import bcrypt
from ..decorators import handler_decorator


class BaseHandler(RequestHandler):

    def set_default_headers(self):
        self.set_header("access-control-allow-origin", "*")
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET, PUT, DELETE, OPTIONS')
        # HEADERS!
        self.set_header("Access-Control-Allow-Headers", "access-control-allow-origin,authorization,content-type")

    def options(self, keu):
        # no body
        self.set_status(204)
        self.finish()

    def write_error(self, status_code, message=None):
        self.set_status(status_code)
        if message:
            self.finish(json.dumps({
                "message": message
            }))
        elif status_code:
            self.set_status(status_code)
            self.finish()

    def write_response(self, status_code, result=None):
        self.set_status(status_code)
        if result:
            self.finish(self.to_json(result))
        elif status_code:
            self.set_status(status_code)
            self.finish()

    def to_json(self, result):
        try:
            if type(result) is list:
                serializable_result = [row.to_dict() for row in result]
            else:
                serializable_result = result.to_dict()
            return json.dumps(serializable_result)
        except:
            return json.dumps(result)

class CrudHandler(BaseHandler, ABC):
    repository = NotImplementedError
    user_repository = NotImplementedError

    def initialize(self, repository, user_repository=None):
        self.repository = repository
        self.user_repository = user_repository

    def b_auth(self):
        return self.user_repository is not None

    def auth_value(self):
        if self.b_auth:
            try:
                email, password = basicauth.decode(self.request.headers['Authorization'])
                user = self.user_repository.get_by('email', email)
                password_bytes = user.password if isinstance(user.password, bytes) else user.password.encode('utf-8')
                if user and bcrypt.checkpw(password.encode('utf-8'), password_bytes):
                    return user
                else:
                    raise NotAllowed
            except:
                raise NotAllowed
        else:
            return None

    @handler_decorator.handle()
    def get(self, key):
        if not key:
            return self.repository.get_all(self.auth_value())
        else:
            return self.repository.get_by_id(key, self.auth_value())

    @handler_decorator.handle()
    def post(self, key):
        return self.repository.save(json.loads(self.request.body), self.auth_value())

    @handler_decorator.handle()
    def put(self, key):
        return self.repository.put(key, json.loads(self.request.body), self.auth_value())

    @handler_decorator.handle()
    def delete(self, key):
        return self.repository.delete(key, self.auth_value())


class UsersHandler(CrudHandler):

    def data_received(self, chunk):
        pass

    @handler_decorator.handle()
    def post(self, key):
        user = json.loads(self.request.body)
        user['password'] = bcrypt.hashpw(user['password'].encode(), bcrypt.gensalt())
        return self.repository.save(user)
