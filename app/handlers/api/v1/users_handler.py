from .crud_handler import CrudHandler
import json
import hashlib
import functools
from http import HTTPStatus
from ....exceptions.entity_not_found import EntityNotFound


class UsersHandler(CrudHandler):

    def initialize(self, repository):
        self.repository = repository
# pylint: disable=no-method-argument

    def handle():
        def decorator(function):
            @functools.wraps(function)
            def wrapper(self, *args):
                try:
                    result = function(self, *args)
                    self.write_response(
                        status_code=HTTPStatus.OK, result=result)
                except EntityNotFound:
                    self.write_error(status_code=HTTPStatus.NOT_FOUND,
                                     message="entity not found")
                except Exception as err:
                    self.write_error(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                     message=str(err))
            return wrapper
        return decorator

    def post(self, key):
        user = json.loads(self.request.body)
        user['password'] = hashlib.md5(user['password'].encode()).hexdigest()
        return self.repository.save(user)
