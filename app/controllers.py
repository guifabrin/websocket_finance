import time

from app.automated.automated import Automated
from app.repository import BaseRepository
from app.models import User, Transaction, Account, Invoice, Captha, UserConfig
import json
from enum import Enum
import datetime
from app.helpers import get_year_periods


class MessageResponseEnum(Enum):
    USER = 0
    ACCOUNTS = 1
    YEAR = 2
    AUTOMATED = 4
    TRANSACTIONS = 6
    INVOICES = 7
    TRANSACTION = 8
    ACCOUNT = 11
    UPDATE = 12


class LoginResponseEnum(Enum):
    SUCCESS = 0
    ERROR = 1


class TransactionTypeEnum(Enum):
    COMMON = 0
    INVOICE = 1


class CrudStatus(Enum):
    ADD_EDIT = 0
    REMOVE = 1


user_repository = BaseRepository(entity=User)

transactions_repository = BaseRepository(entity=Transaction)
accounts_repository = BaseRepository(entity=Account)
invoice_repository = BaseRepository(entity=Invoice)
captcha_repository = BaseRepository(entity=Captha)
user_configs_repository = BaseRepository(entity=UserConfig)


def auto_sync():
    while True:
        time.sleep(60 * 60)
        accounts = accounts_repository.get_all()
        for account in accounts:
            if account.automated_args and not account.automated_body:
                Automated(transactions_repository, user_repository, invoice_repository,
                          accounts_repository, captcha_repository).run(account)
                time.sleep(60 * 5)


def send_automated_status(str_user_id, account_id, status):
    for socket in sockets[str_user_id]:
        send(socket, {
            'code': MessageResponseEnum.AUTOMATED.value,
            'account_id': account_id,
            'status': status
        })


def send(websocket, obj):
    websocket.sendMessage(json.dumps(obj))


def map_accounts(user, year):
    init, end = get_year_periods(year)
    dictionaries = []
    accounts = sorted(user.accounts, key=lambda lacc: lacc.sort_sum, reverse=True)
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
                error = account.value_error if account.value_error is not None else 0
                values.append(error + sum(map(lambda transaction: transaction.value, filtered_paid)))
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


def func_year(parsed, websocket, user):
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


def finish(user, account):
    send_automated_status(
        str(user.id),
        account.id,
        'finish'
    )


def func_automated(parsed, websocket, user):
    accounts = list(filter(lambda lacc: lacc.id == parsed['id'], user.accounts))
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
            lambda: finish(user, account))


def func_captcha(parsed, websocket, user):
    captcha_repository.put(parsed['id'], parsed)


def func_transactions(parsed, websocket, user):
    accounts = list(filter(lambda account: account.id == parsed['accountId'], user.accounts))
    if len(accounts) > 0:
        if parsed['type'] == TransactionTypeEnum.INVOICE.value:
            invoices = list(filter(lambda invoice: invoice.id == parsed['invoiceId'], accounts[0].invoices))
            if len(invoices) > 0:
                transactions = sorted(invoices[0].transactions, key=lambda transaction: transaction.date, reverse=True)
                transactions = list(map(lambda transaction: transaction.to_dict(), transactions))
                send(websocket, {
                    'code': MessageResponseEnum.TRANSACTIONS.value,
                    'transactions': transactions
                })
        elif parsed['type'] == TransactionTypeEnum.COMMON.value:
            init, end = get_year_periods(parsed['year'])
            filtered = filter(lambda transaction: init[parsed['month'] - 1].date() <= transaction.date <= end[
                parsed['month'] - 1].date(), accounts[0].transactions)
            transactions = sorted(filtered, key=lambda transaction: transaction.date, reverse=True)
            transactions = list(map(lambda transaction: transaction.to_dict(), transactions))
            send(websocket, {
                'code': MessageResponseEnum.TRANSACTIONS.value,
                'transactions': transactions
            })


def func_invoices(parsed, websocket, user):
    accounts = list(filter(lambda account: account.id == parsed['accountId'], user.accounts))
    if len(accounts) > 0:
        invoices = list(map(lambda invoice: invoice.to_dict(), accounts[0].invoices))
        send(websocket, {
            'code': MessageResponseEnum.INVOICES.value,
            'invoices': invoices
        })


def func_configs(parsed, websocket, user):
    list_configs = list(filter(lambda config: config.config_id == parsed['id'], user.configs))
    user_configs_repository.put(list_configs[0].id, parsed)


def func_transaction(parsed, websocket, user):
    accounts = list(filter(lambda account: account.id == parsed['accountId'], user.accounts))
    if len(accounts) > 0:
        if parsed['status'] == CrudStatus.ADD_EDIT.value:
            if 'id' in parsed:
                t = transactions_repository.get_by_id(parsed['id'])
                if t is not None and t.account_id == parsed['accountId']:
                    transactions_repository.put(parsed['id'], parsed['values'])
            else:
                t = Transaction()
                t.description = parsed['values']['description']
                t.paid = parsed['values']['paid'] if 'paid' in parsed['values'] else False
                t.invoice_id = parsed['values']['invoice_id'] if 'invoice_id' in parsed['values'] else None
                t.account_id = parsed['values']['account_id']
                t.value = parsed['values']['value']
                t.date = datetime.datetime.strptime(parsed['values']['date'], '%Y-%m-%d')
                transactions_repository.save(t)
        elif parsed['status'] == CrudStatus.REMOVE.value:
            t = transactions_repository.get_by_id(parsed['id'])
            if t is not None and t.account_id == parsed['accountId']:
                transactions_repository.delete(parsed['id'])
        send(websocket, {
            'code': MessageResponseEnum.UPDATE.value
        })


def func_account(parsed, websocket, user):
    if parsed['status'] == CrudStatus.ADD_EDIT.value:
        if 'id' in parsed['value']:
            accounts_repository.put(parsed['value']['id'], parsed['value'])
        else:
            account = Account()
            account.description = parsed['value']['description']
            account.is_credit_card = parsed['value']['is_credit_card'] if 'is_credit_card' in parsed['value'] else False
            account.ignore = parsed['value']['ignore'] if 'ignore' in parsed['value'] else False
            account.automated_args = parsed['value']['automated_args'] if 'automated_args' in parsed['value'] else ''
            account.automated_body = parsed['value']['automated_body'] if 'automated_body' in parsed[
                'value'] else False
            account.user_id = user.id
            accounts_repository.save(account)
    elif parsed['status'] == CrudStatus.REMOVE.value:
        accounts_repository.delete(parsed['value']['id'])
    send(websocket, {
        'code': MessageResponseEnum.UPDATE.value
    })


def func_invoice(parsed, websocket, user):
    if parsed['status'] == CrudStatus.ADD_EDIT.value:
        if 'id' in parsed['values']:
            invoice_repository.put(parsed['values']['id'], parsed['values'])
        else:
            invoice = Invoice()
            invoice.description = parsed['values']['description']
            invoice.account_id = parsed['values']['account_id']
            invoice.debit_date = datetime.datetime.strptime(parsed['values']['debit_date'], '%Y-%m-%d')
            invoice_repository.save(invoice)
    elif parsed['status'] == CrudStatus.REMOVE.value:
        invoice_repository.delete(parsed['id'])
    send(websocket, {
        'code': MessageResponseEnum.UPDATE.value
    })


func_mapped = {
    2: func_year,
    4: func_automated,
    5: func_captcha,
    6: func_transactions,
    7: func_invoices,
    8: func_configs,
    9: func_transaction,
    11: func_account,
    13: func_invoice
}

sockets = {}


def process(parsed, websocket, user):
    str_user_id = str(user.id)
    if not hasattr(sockets, str_user_id):
        sockets[str_user_id] = []
    sockets[str_user_id].append(websocket)
    if not parsed['code'] in func_mapped:
        print("Code", parsed['code'], "not implemented")
        return
    return func_mapped[parsed['code']](parsed, websocket, user)
