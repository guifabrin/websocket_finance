from .crud_handler import CrudHandler
import json
import hashlib
from ....exceptions.entity_not_found import EntityNotFound


class UsersHandler(CrudHandler):

    @CrudHandler.handle()
    def post(self):
        user = json.loads(self.request.body)
        user['password'] = hashlib.md5(user['password'].encode()).hexdigest()
        return self.repository.save(user)
