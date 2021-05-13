import json

from ....decorators import handler_decorator
from .base_handler import BaseHandler


class CrudHandler(BaseHandler):

    repository = NotImplementedError

    def initialize(self, repository):
        self.repository = repository

    @handler_decorator.HandlerDecorator.handle()
    def get(self, key):
        if not key:
            return self.repository.get_all()
        else:
            return self.repository.get_by_id(key)

    @handler_decorator.HandlerDecorator.handle()
    def post(self, key):
        return self.repository.save(json.loads(self.request.body))

    @handler_decorator.HandlerDecorator.handle()
    def put(self, key):
        return self.repository.put(key, json.loads(self.request.body))

    @handler_decorator.HandlerDecorator.handle()
    def delete(self, key):
        return self.repository.delete(key)
