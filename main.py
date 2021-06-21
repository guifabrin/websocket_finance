import datetime
import sched
import threading
import time

import tornado.httpserver
import tornado.ioloop
import tornado.web

from app.database.database import create
from app.handlers.v1 import CrudHandler, UsersHandler
from app.models import Transaction, Account, Invoice, Role, RoleUser
from app.repositories.base_repository import BaseRepository
from app.repositories.user_repository import UserRepository

s = sched.scheduler(time.time, time.sleep)

from app.automated.automated import banco_do_brasil, banco_do_brasil_cc, caixa
import os.path
from psutil import process_iter
from signal import SIGTERM  # or SIGKILL

main_user_repository = UserRepository()
main_transactions_repository = BaseRepository(entity=Transaction)
main_accounts_repository = BaseRepository(entity=Account)
main_invoice_repository = BaseRepository(entity=Invoice)
main_role_repository = BaseRepository(entity=Role)
main_roles_users_repository = BaseRepository(entity=RoleUser)


def make_app():
    settings = {
        'debug': True,
    }
    return tornado.web.Application([
        (r'/api/v1/users/?(.*)?', UsersHandler,
         dict(repository=main_user_repository, user_repository=main_user_repository)),
        (r'/api/v1/transactions/?(.*)?', CrudHandler,
         dict(repository=main_transactions_repository, user_repository=main_user_repository)),
        (r'/api/v1/accounts/?(.*)?', CrudHandler,
         dict(repository=main_accounts_repository, user_repository=main_user_repository)),
        (r'/api/v1/invoices/?(.*)?', CrudHandler,
         dict(repository=main_invoice_repository, user_repository=main_user_repository)),
        (r'/api/v1/roles_users/?(.*)?', CrudHandler,
         dict(repository=main_roles_users_repository, user_repository=main_user_repository)),
        (r'/api/v1/roles/?(.*)?', CrudHandler,
         dict(repository=main_role_repository, user_repository=main_user_repository)),
        (r'/js/(.*)', tornado.web.StaticFileHandler,
         {'path': './dist/scripts'}),
        (r'/css/(.*)', tornado.web.StaticFileHandler,
         {'path': './dist/styles'}),
        (r'/images/(.*)', tornado.web.StaticFileHandler,
         {'path': './dist/images'}),
    ], **settings)


def sync_banco_do_brasil(agency, account, password, account_id):
    transactions = banco_do_brasil(agency, account, password)
    transactions2 = main_accounts_repository.get_by_id_root(account_id).transactions
    for transaction in transactions:
        contains = False
        for transaction2 in transactions2:
            if transaction2.value == transaction.value and (transaction.date.date() - transaction2.date).days == 0:
                contains = True
                break
        if not contains:
            transaction.account_id = account_id
            transaction.paid = True
            print(main_transactions_repository.save_root(transaction))


def sync_banco_do_brasil_cc(agency, account, password, account_id):
    transactions = banco_do_brasil_cc(agency, account, password)
    account = main_accounts_repository.get_by_id_root(account_id)
    now = datetime.datetime.now()
    endYear = now.year
    endMonth = now.month
    if (now.month == 12):
        endMonth = -1
        endYear = now.year + 1
    dateInit = datetime.datetime(now.year, now.month + 1, 1, 0, 0, 0);
    dateEnd = datetime.datetime(endYear, endMonth + 2, 1, 0, 0, 0);
    invoices = list(filter(lambda invoice: dateInit.date() <= invoice.debit_date < dateEnd.date(), account.invoices))
    if len(invoices) == 0:
        invoice = Invoice()
        invoice.debit_date = dateInit + (dateEnd - dateInit) / 2
        invoice.description = 'Automated'
        invoice.date_init = dateInit
        invoice.date_end = dateEnd
        invoice.account = account
        print(main_invoice_repository.save_root(invoice))
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
            print(main_transactions_repository.save_root(transaction))


def sync_caixa(username, password, account_id):
    transactions = caixa(username, password)
    transactions2 = main_accounts_repository.get_by_id_root(account_id).transactions
    for transaction in transactions:
        contains = False
        for transaction2 in transactions2:
            if transaction2.value == transaction.value and (transaction.date.date() - transaction2.date).days == 0:
                contains = True
                break
        if not contains:
            transaction.account_id = account_id
            transaction.paid = True
            print(main_transactions_repository.save_root(transaction))


def run_automated(name):
    while True:
        filename = ".automated"
        if not os.path.isfile(filename):
            return
        with open(filename) as f:
            content = f.readlines()
        for line in content:
            args = line.split(',')
            try:
                if args[0] == 'caixa':
                    sync_caixa(args[2], args[3], int(args[1]))
                elif args[0] == 'banco_do_brasil':
                    sync_banco_do_brasil(args[2], args[3], args[4], int(args[1]))
                elif args[0] == 'banco_do_brasil_cc':
                    sync_banco_do_brasil_cc(args[2], args[3], args[4], int(args[1]))
            except Exception as e:
                print('Error', e)
        time.sleep(60 * 60)


if __name__ == "__main__":
    for proc in process_iter():
        for conns in proc.connections(kind='inet'):
            if conns.laddr.port == 8888:
                proc.send_signal(SIGTERM)  # or SIGKILL
                print("Kill sign sent to program using " + str(conns.laddr))
    create()
    app = make_app()
    x = threading.Thread(target=run_automated, args=(1,))
    x.start()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    print("Listening into 8888")
