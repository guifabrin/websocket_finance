from .crud_handler import CrudHandler
import json
import hashlib
from ....decorators import handler_decorator


class UsersHandler(CrudHandler):

    @handler_decorator.HandlerDecorator.handle()
    def post(self, key):
        user = json.loads(self.request.body)
        user['password'] = hashlib.md5(user['password'].encode()).hexdigest()
        return self.repository.save(user)
