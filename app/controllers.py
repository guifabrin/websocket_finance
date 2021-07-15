import time

from app.automated.automated import Automated
from app.repositories.base_repository import BaseRepository
from app.models import Notification, User, Transaction, Account, Invoice, Captha, UserConfig
import json
from enum import Enum
import datetime
from app.helpers.date import get_year_periods


class MessageResponseEnum(Enum):
    USER = 0
    ACCOUNTS = 1
    YEAR = 2
    NOTIFICATIONS = 3
    AUTOMATED = 4
    TRANSACTIONS = 6
    INVOICES = 7


class LoginResponseEnum(Enum):
    SUCCESS = 0
    ERROR = 1


class TransactionTypeEnum(Enum):
    COMMON = 0
    INVOICE = 1


user_repository = BaseRepository(entity=User)
notification_repository = BaseRepository(entity=Notification)


def notify(entity):
    notification = Notification()
    notification.date = datetime.datetime.now()
    notification.table = type(entity).__name__
    notification.entity_id = entity.id
    notification.method = 'save'
    notification.seen = False
    notification_repository.save(notification)
    if type(entity).__name__ == 'Captha':
        return send_notifications_all()
    send_notifications(str(entity.user.id))


transactions_repository = BaseRepository(entity=Transaction, def_notification=notify)
accounts_repository = BaseRepository(entity=Account, def_notification=notify)
invoice_repository = BaseRepository(entity=Invoice, def_notification=notify)
captcha_repository = BaseRepository(entity=Captha, def_notification=notify)
user_configs_repository = BaseRepository(entity=UserConfig, def_notification=notify)


def auto_sync():
    while True:
        accounts = accounts_repository.get_all()
        for account in accounts:
            if account.automated_args and not account.automated_body:
                Automated(transactions_repository, user_repository, invoice_repository,
                          accounts_repository, captcha_repository).run(account)
                time.sleep(60 * 5)
        time.sleep(60 * 60)


def send_automated_status(str_user_id, account_id, status):
    for socket in sockets[str_user_id]:
        send(socket, {
            'code': MessageResponseEnum.AUTOMATED.value,
            'account_id': account_id,
            'status': status
        })


def send_notifications_all():
    for attr, value in sockets.items():
        send_notifications(attr)


def send_notifications(str_user_id):
    notifications = notification_repository.get_all()
    not_seen_notifications = list(filter(lambda notification: not notification.seen, notifications))
    transactions_notifications = []
    invoice_notifications = []
    for notification in not_seen_notifications:
        if notification.table == 'Transaction':
            transaction = transactions_repository.get_by_id(notification.entity_id)
            if transaction is not None and str(transaction.user.id) == str_user_id:
                transactions_notifications.append({
                    'notification': notification.to_dict(),
                    'transaction': transaction.to_dict()
                })
        if notification.table == 'Invoice':
            invoice = invoice_repository.get_by_id(notification.entity_id)
            if invoice is not None and str(invoice.user.id) == str_user_id:
                invoice_notifications.append({
                    'notification': notification.to_dict(),
                    'invoice': invoice.to_dict()
                })
    captchas = captcha_repository.get_all()
    captcha_notifications = list(
        map(lambda captcha: captcha.to_dict(), filter(lambda captcha: not captcha.result, captchas)))
    for socket in sockets[str_user_id]:
        send(socket, {
            'code': MessageResponseEnum.NOTIFICATIONS.value,
            'transactions': transactions_notifications,
            'invoices': invoice_notifications,
            'captchas': captcha_notifications
        })


def send(websocket, object):
    websocket.sendMessage(json.dumps(object))


def map_accounts(user, year):
    init, end = get_year_periods(year)
    dictionaries = []
    accounts = user.accounts

    accounts = sorted(user.accounts, key=lambda account: account.sort_sum, reverse=True)
    for account in accounts:
        dictionary = account.to_dict()
        values = []
        values_not_paid = []
        invoices = []
        for month in range(12):
            dt_init = init[month]
            dt_end = end[month]
            if not account.is_credit_card:
                filtered_paid = filter(lambda transaction: transaction.date <= dt_end.date() and transaction.paid,
                                       account.transactions)
                filtered_not_paid = filter(
                    lambda transaction: transaction.date <= dt_end.date() and not transaction.paid,
                    account.transactions)
                values.append(sum(map(lambda transaction: transaction.value, filtered_paid)))
                values_not_paid.append(sum(map(lambda transaction: transaction.value, filtered_not_paid)))
            else:
                filtered = filter(lambda invoice: dt_init.date() <= invoice.debit_date <= dt_end.date(),
                                  account.invoices)
                invoices.append(list(map(lambda invoice: invoice.to_dict(), filtered)))
        dictionary['invoices'] = invoices
        dictionary['values'] = values
        dictionary['values_not_paid'] = values_not_paid
        dictionaries.append(dictionary)
    return dictionaries


def year(parsed, websocket, user):
    send(websocket, {
        'code': MessageResponseEnum.USER.value,
        'user': user.to_dict()
    })
    send(websocket, {
        'code': MessageResponseEnum.YEAR.value,
        'year': parsed['year']
    })
    send(websocket, {
        'code': MessageResponseEnum.ACCOUNTS.value,
        'accounts': map_accounts(user, parsed['year'])
    })
    send_notifications(str(user.id))


def automated(parsed, websocket, user):
    accounts = list(filter(lambda account: account.id == parsed['id'], user.accounts))
    for account in accounts:
        send_automated_status(str(user.id), account.id, 'init')
        Automated(
            transactions_repository,
            user_repository,
            invoice_repository,
            accounts_repository,
            captcha_repository
        ).run(
            account,
            parsed['body'],
            lambda: send_automated_status(
                str(user.id),
                account.id,
                'finish'
            ))


def captcha(parsed, websocket, user):
    captcha_repository.put(parsed['id'], parsed)
    send_notifications_all()


def transactions(parsed, websocket, user):
    accounts = list(filter(lambda account: account.id == parsed['accountId'], user.accounts))
    if len(accounts) > 0:
        if parsed['type'] == TransactionTypeEnum.INVOICE.value:
            invoices = list(filter(lambda invoice: invoice.id == parsed['invoiceId'], accounts[0].invoices))
            if len(invoices) > 0:
                transactions = list(map(lambda transaction: transaction.to_dict(), invoices[0].transactions))
                send(websocket, {
                    'code': MessageResponseEnum.TRANSACTIONS.value,
                    'transactions': transactions
                })
        elif parsed['type'] == TransactionTypeEnum.COMMON.value:
            init, end = get_year_periods(parsed['year'])
            filtered = filter(lambda transaction: init[parsed['month'] - 1].date() <= transaction.date <= end[
                parsed['month'] - 1].date(), accounts[0].transactions)
            transactions = list(map(lambda transaction: transaction.to_dict(), filtered))
            send(websocket, {
                'code': MessageResponseEnum.TRANSACTIONS.value,
                'transactions': transactions
            })


def invoices(parsed, websocket, user):
    accounts = list(filter(lambda account: account.id == parsed['accountId'], user.accounts))
    if len(accounts) > 0:
        invoices = list(map(lambda invoice: invoice.to_dict(), accounts[0].invoices))
        send(websocket, {
            'code': MessageResponseEnum.INVOICES.value,
            'invoices': invoices
        })


def configs(parsed, websocket, user):
    list_configs = list(filter(lambda config: config.config_id == parsed['id'], user.configs))
    user_configs_repository.put(list_configs[0].id, parsed)


mapped = {
    2: year,
    4: automated,
    5: captcha,
    6: transactions,
    7: invoices,
    8: configs
}

sockets = {

}


def process(parsed, websocket, user):
    str_user_id = str(user.id)
    if not hasattr(sockets, str_user_id):
        sockets[str_user_id] = []
    sockets[str_user_id].append(websocket)
    return mapped[parsed['code']](parsed, websocket, user)
