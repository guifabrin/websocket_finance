import functools
from http import HTTPStatus
import json

from tornado.web import RequestHandler
from ....exceptions.entity_not_found import EntityNotFound


class CrudHandler(RequestHandler):

    repository = NotImplementedError

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

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Content-Type", "application/json")

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

    @handle()
    def get(self, key):
        if not key:
            return self.repository.get_all()
        else:
            return self.repository.get_by_id(key)

    @handle()
    def post(self):
        return self.repository.save(json.loads(self.request.body))

    @handle()
    def put(self, key):
        return self.repository.put(key, json.loads(self.request.body))

    @handle()
    def delete(self, key):
        return self.repository.delete(key)
