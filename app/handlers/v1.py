from tornado.web import RequestHandler

from abc import ABC

import basicauth
from app.exceptions.not_allowed import NotAllowed
import json

import bcrypt
from ..decorators import handler_decorator
from app.models import Transaction


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


from app.automated.automated import banco_do_brasil, banco_do_brasil_cc, caixa, banco_inter_cc, banco_do_brasil_cdb
import os.path
from app.models import Invoice
import datetime
import threading


class AutomatedHandler(RequestHandler):
    transaction_repository = NotImplementedError
    user_repository = NotImplementedError
    invoice_repository = NotImplementedError
    accounts_repository = NotImplementedError

    def set_default_headers(self):
        self.set_header("access-control-allow-origin", "*")
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET, PUT, DELETE, OPTIONS')
        # HEADERS!
        self.set_header("Access-Control-Allow-Headers", "access-control-allow-origin,authorization,content-type")

    def initialize(self, transaction_repository, user_repository, invoice_repository, accounts_repository):
        self.transaction_repository = transaction_repository
        self.user_repository = user_repository
        self.invoice_repository = invoice_repository
        self.accounts_repository = accounts_repository

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

    def options(self, key):
        self.set_status(204)
        self.finish()

    def post(self, account_id):
        self.run_automated(int(account_id), str(self.request.body))
        self.set_status(204)
        self.finish()

    def sync_banco_do_brasil(self, agency, account, password, account_id):
        transactions = banco_do_brasil(agency, account, password)
        transactions2 = self.accounts_repository.get_by_id_root(account_id).transactions
        for transaction in transactions:
            contains = False
            for transaction2 in transactions2:
                if transaction2.value == transaction.value and (transaction.date.date() - transaction2.date).days == 0:
                    contains = True
                    break
            if not contains:
                transaction.account_id = account_id
                transaction.paid = True
                print(self.transaction_repository.save_root(transaction))

    def sync_banco_do_brasil_cdb(self, agency, account, password, account_id):
        value = banco_do_brasil_cdb(agency, account, password)
        if value is None:
            return
        ssum = sum(list(map(lambda t: t.value, self.accounts_repository.get_by_id_root(account_id).transactions)))
        rest = value - ssum
        if rest != 0:
            t = Transaction()
            t.account_id = account_id;
            t.value = rest
            t.description = 'Automated CDB update'
            t.date = datetime.datetime.now()
            t.paid = True
            print(self.transaction_repository.save_root(t))

    def sync_banco_do_brasil_cc(self, agency, account, password, account_id):
        transactions = banco_do_brasil_cc(agency, account, password)
        account = self.accounts_repository.get_by_id_root(account_id)

        for transaction in transactions:
            invoice = None
            if transaction.value > 0:
                now = datetime.datetime.now()
                endYearEnd = endYear = now.year
                endMonthEnd = endMonth = now.month
                if (now.month == 12):
                    endMonthEnd = -1
                    endYearEnd = now.year + 1
                dateInit = datetime.datetime(now.year, now.month, 1, 0, 0, 0);
                dateEnd = datetime.datetime(endYearEnd, endMonthEnd + 1, 1, 0, 0, 0);
                invoices = list(
                    filter(lambda invoice: dateInit.date() <= invoice.debit_date < dateEnd.date(), account.invoices))
                if len(invoices) == 0:
                    invoice = Invoice()
                    invoice.debit_date = dateInit + (dateEnd - dateInit) / 2
                    invoice.description = 'Automated'
                    invoice.date_init = dateInit
                    invoice.date_end = dateEnd
                    invoice.account = account
                    print(self.invoice_repository.save_root(invoice))
                else:
                    invoice = invoices[0]
            else:
                now = datetime.datetime.now()
                endYear = now.year
                endMonth = now.month
                if (now.month == 12):
                    endMonth = -1
                    endYear = now.year + 1
                dateInit = datetime.datetime(now.year, now.month + 1, 1, 0, 0, 0);
                dateEnd = datetime.datetime(endYear, endMonth + 2, 1, 0, 0, 0);
                invoices = list(
                    filter(lambda invoice: dateInit.date() <= invoice.debit_date < dateEnd.date(), account.invoices))
                if len(invoices) == 0:
                    invoice = Invoice()
                    invoice.debit_date = dateInit + (dateEnd - dateInit) / 2
                    invoice.description = 'Automated'
                    invoice.date_init = dateInit
                    invoice.date_end = dateEnd
                    invoice.account = account
                    print(self.invoice_repository.save_root(invoice))
                else:
                    invoice = invoices[0]

            transactions2 = invoice.transactions
            contains = False
            for transaction2 in transactions2:
                if transaction2.value == transaction.value and (transaction.date.date() - transaction2.date).days == 0:
                    contains = True
                    break
            if not contains:
                transaction.account_id = account_id
                transaction.paid = True
                transaction.invoice = invoice
                print(self.transaction_repository.save_root(transaction))

    def sync_caixa(self, username, password, account_id):
        transactions = caixa(username, password)
        transactions2 = self.accounts_repository.get_by_id_root(account_id).transactions
        for transaction in transactions:
            contains = False
            for transaction2 in transactions2:
                if transaction2.value == transaction.value and (transaction.date.date() - transaction2.date).days == 0:
                    contains = True
                    break
            if not contains:
                transaction.account_id = account_id
                transaction.paid = True
                print(self.transaction_repository.save_root(transaction))

    def sync_banco_inter_cc(self, agency, password, account_id, isafe):
        transactions = banco_inter_cc(agency, password, isafe)
        account = self.accounts_repository.get_by_id_root(account_id)
        now = datetime.datetime.now()
        endYear = now.year
        endMonth = now.month
        if (now.month == 12):
            endMonth = -1
            endYear = now.year + 1
        dateInit = datetime.datetime(now.year, now.month + 1, 1, 0, 0, 0);
        dateEnd = datetime.datetime(endYear, endMonth + 2, 1, 0, 0, 0);
        invoices = list(
            filter(lambda invoice: dateInit.date() <= invoice.debit_date < dateEnd.date(), account.invoices))
        if len(invoices) == 0:
            invoice = Invoice()
            invoice.debit_date = dateInit + (dateEnd - dateInit) / 2
            invoice.description = 'Automated'
            invoice.date_init = dateInit
            invoice.date_end = dateEnd
            invoice.account = account
            print(self.invoice_repository.save_root(invoice))
        else:
            invoice = invoices[0]
        transactions2 = invoice.transactions
        for transaction in transactions:
            contains = False
            for transaction2 in transactions2:
                if transaction2.value == transaction.value and (transaction.date.date() - transaction2.date).days == 0:
                    contains = True
                    break
            if not contains:
                transaction.account_id = account_id
                transaction.paid = True
                transaction.invoice = invoice
                print(self.transaction_repository.save_root(transaction))

    def run_automated(self, account_id, extra):
        filename = ".automated"
        if not os.path.isfile(filename):
            return
        with open(filename) as f:
            content = f.readlines()
        for line in content:
            args = line.split(',')
            if args[1] != '' and account_id != int(args[1]):
                continue
            try:
                if args[0] == 'caixa':
                    self.sync_caixa(args[2], args[3], int(args[1]))
                elif args[0] == 'banco_do_brasil':
                    self.sync_banco_do_brasil(args[2], args[3], args[4], int(args[1]))
                elif args[0] == 'banco_do_brasil_cc':
                    self.sync_banco_do_brasil_cc(args[2], args[3], args[4], int(args[1]))
                elif args[0] == 'banco_do_brasil_cdb':
                    self.sync_banco_do_brasil_cdb(args[2], args[3], args[4], int(args[1]))
                elif args[0] == 'banco_inter_cc':
                    self.sync_banco_inter_cc(args[2], args[3], int(args[1]), extra)
            except Exception as e:
                print('Error', e, args)
