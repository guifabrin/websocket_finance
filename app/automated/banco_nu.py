from datetime import datetime, timedelta

from pynubank import Nubank


def __login(cpf, senha):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, 'certificados/nubank/' + cpf + '.p12')
    return nu


def __extratos(nu):
    statements = nu.get_account_statements()
    transactions = []
    for statement in statements:
        multiplier = 1
        debit_list = ['TransferOutEvent', 'BillPaymentEvent', 'BarcodePaymentEvent', 'PixTransferOutEvent',
                      'DebitPurchaseEvent', 'DebitWithdrawalEvent', 'BarcodePaymentEvent']
        if statement['__typename'] in debit_list:
            multiplier = -1
        if 'amount' not  in statement:
            print(statement)
            continue
        transactions.append({
            'value': statement['amount'] * multiplier,
            'automated_id': statement['id'],
            'description': statement['title'] + " " + statement['detail'],
            'date': statement['postDate'] + "T00:00:00.000Z"
        })
    return transactions


def __faturas(nu):
    bills = nu.get_bills()
    feed = nu.get_card_feed()
    statements = list(filter(lambda x: x['category'] == 'transaction', feed['events']))
    payments = list(filter(lambda x: x['category'] == 'payment', feed['events']))
    results = []
    transactions = []
    for statement in statements:
        count = statement['details']['charges']['count'] if 'charges' in statement['details'] else 1
        for i in range(count):
            date = datetime.fromisoformat(statement['time'].split('T')[0])
            if i != 0:
                date += timedelta(hours=+i * 24 * 30)
            description = statement['description'] if count == 1 else statement['description'] + " " + str(
                i + 1) + "/" + str(count)
            transactions.append({
                'automated_id': statement['id'] + "_" + str(i),
                'value': statement['amount'] / -100 / count,
                'description': description,
                'date': str(date.year) + '-' + str(date.month) + '-' + str(date.day) + "T00:00:00.000Z",
                'isodate': date
            })
    for statement in payments:
        transactions.append({
            'automated_id': statement['id'],
            'value': statement['amount'] / 100,
            'description': statement['title'],
            'date': statement['time'].split('T')[0] + "T00:00:00.000Z",
            'isodate': datetime.fromisoformat(statement['time'].split('T')[0])
        })
    for bill in bills:
        date_init = datetime.fromisoformat(bill['summary']['open_date'])
        date_end = datetime.fromisoformat(bill['summary']['close_date'])
        itransactions = []
        for transaction in transactions:
            if date_init <= transaction['isodate'] < date_end:
                itransactions.append(transaction)
        results.append([{
            'cardNumber': 'NuBank',
            'date': bill['summary']['effective_due_date'] + "T00:00:00.000Z",
            'values': itransactions
        }])
    return results


def get(cpf, senha):
    nu = __login(cpf, senha)
    return {
        'transactions': __extratos(nu),
        'cards': __faturas(nu)
    }
