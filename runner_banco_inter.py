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
from app.models import Transaction, Account, Invoice, User, Notification
from app.repositories.base_repository import BaseRepository
main_notification_repository = BaseRepository(entity=Notification)
main_user_repository = BaseRepository(entity=User, notification_repository = main_notification_repository)
main_transactions_repository = BaseRepository(entity=Transaction, notification_repository = main_notification_repository)
main_accounts_repository = BaseRepository(entity=Account, notification_repository = main_notification_repository)
main_invoice_repository = BaseRepository(entity=Invoice, notification_repository = main_notification_repository)

if __name__ == "__main__":
    Automated(main_transactions_repository, main_user_repository, main_invoice_repository,
              main_accounts_repository).run(main_accounts_repository.get_by_id(26), "767078")