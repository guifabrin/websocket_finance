import threading
import time
from signal import SIGTERM

import tornado.httpserver
import tornado.ioloop
import tornado.web
from psutil import process_iter

from app.automated.automated import Automated
from app.database.database import create
from app.handlers.v1 import AutomatedHandler
from app.models import Transaction, Account, Invoice, User
from app.repositories.base_repository import BaseRepository

main_user_repository = BaseRepository(entity=User)
main_transactions_repository = BaseRepository(entity=Transaction)
main_accounts_repository = BaseRepository(entity=Account)
main_invoice_repository = BaseRepository(entity=Invoice)


def make_app():
    settings = {
        'debug': True,
    }
    return tornado.web.Application([
        (r"/api/v1/automated/?(.*)?", AutomatedHandler,
         dict(transaction_repository=main_transactions_repository, user_repository=main_user_repository,
              invoice_repository=main_invoice_repository, accounts_repository=main_accounts_repository)),
    ], **settings)


app = make_app()


def auto_sync():
    while True:
        accounts = main_accounts_repository.get_all()
        for account in accounts:
            if account.automated_args and not account.automated_body:
                Automated(main_transactions_repository, main_user_repository, main_invoice_repository,
                          main_accounts_repository).run(account)
                time.sleep(60 * 5)
        time.sleep(60 * 60)


if __name__ == "__main__":
    for proc in process_iter():
        for conns in proc.connections(kind='inet'):
            if conns.laddr.port == 8888:
                proc.send_signal(SIGTERM)
                print("Kill sign sent to program using " + str(conns.laddr))
    create()
    try:
        x = threading.Thread(target=auto_sync, args=())
        x.start()
    except Exception as e:
        print('Error', e)
    app.listen(8990)
    tornado.ioloop.IOLoop.current().start()
    print("Listening into 8990")
