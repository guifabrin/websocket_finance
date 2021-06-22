
import sched
import time

import tornado.httpserver
import tornado.ioloop
import tornado.web

from app.database.database import create
from app.handlers.v1 import CrudHandler, UsersHandler, AutomatedHandler
from app.models import Transaction, Account, Invoice, Role, RoleUser

from app.repositories.base_repository import BaseRepository
from app.repositories.user_repository import UserRepository
s = sched.scheduler(time.time, time.sleep)

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
        (r"/api/v1/automated/?(.*)?", AutomatedHandler,
         dict(transaction_repository=main_transactions_repository, user_repository=main_user_repository, invoice_repository=main_invoice_repository, accounts_repository=main_accounts_repository)),
    ], **settings)

if __name__ == "__main__":
    for proc in process_iter():
        for conns in proc.connections(kind='inet'):
            if conns.laddr.port == 8888:
                proc.send_signal(SIGTERM)  # or SIGKILL
                print("Kill sign sent to program using " + str(conns.laddr))
    create()
    app = make_app()
    # x = threading.Thread(target=run_automated, args=(1,))
    # x.start()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    print("Listening into 8888")
