import datetime
from abc import ABC

import basicauth
from tornado.web import RequestHandler

from app.automated.automated import Automated

now = datetime.datetime.now()

AutomatedHandlerStatic = None


class AutomatedHandler(RequestHandler, ABC):
    transaction_repository = NotImplementedError
    user_repository = NotImplementedError
    invoice_repository = NotImplementedError
    accounts_repository = NotImplementedError

    def auth_value(self):
        email, password = basicauth.decode(self.request.headers['Authorization'])
        user = self.user_repository.get_by('email', email)
        if user and password.encode('utf-8') == user.password.encode('utf-8'):
            return user
        return None

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET, PUT, DELETE, OPTIONS')
        self.set_header("Access-Control-Allow-Headers", "access-control-allow-origin,authorization,content-type")

    def initialize(self, transaction_repository, user_repository, invoice_repository, accounts_repository):
        self.transaction_repository = transaction_repository
        self.user_repository = user_repository
        self.invoice_repository = invoice_repository
        self.accounts_repository = accounts_repository

    def options(self, _):
        self.set_status(204)
        self.finish()

    def post(self, account_id):
        user = self.auth_value()
        if user is None:
            return self.set_status(401)
        account = self.accounts_repository.get_by_id(int(account_id))
        if account is None or account.user.id is not user.id:
            return self.set_status(401)
        Automated(self.transaction_repository, self.user_repository, self.invoice_repository,
                  self.accounts_repository).run(account, self.request.body)
        self.set_status(200)
        self.finish()
