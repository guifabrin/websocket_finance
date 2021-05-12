import functools
from http import HTTPStatus
import json

from .base_handler import BaseHandler
from ....exceptions.entity_not_found import EntityNotFound


class CrudHandler(BaseHandler):

    repository = NotImplementedError

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

    @handle()
    def get(self, key):
        if not key:
            return self.repository.get_all()
        else:
            return self.repository.get_by_id(key)

    @handle()
    def post(self, key):
        return self.repository.save(json.loads(self.request.body))

    @handle()
    def put(self, key):
        return self.repository.put(key, json.loads(self.request.body))

    @handle()
    def delete(self, key):
        return self.repository.delete(key)
