import hashlib
import json
import threading
import time
import traceback
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from app.automated import banco_do_brasil, banco_inter, banco_caixa, banco_nu, sodexo_alimentacao, picpay
from app.models import Transaction, Account, Invoice

now = datetime.now()


def _parse_brl_to_float(str_value):
    return float(str_value.replace('\xa0', '').replace('.', '').replace(',', '.').replace('R$', ''))


def _parse_dd_mm_yyyy(str_value):
    dd, mm, yyyy = str_value.replace('\xa0', '').split('/')
    return datetime.fromisoformat(yyyy + '-' + mm + '-' + dd)


def _parse_dd_mm(str_value):
    dd, mm = str_value.replace('\xa0', '').split('/')
    return datetime.fromisoformat(str(now.year) + '-' + mm + '-' + dd)


def _clean_description(str_description):
    return str_description.replace('\xa0', '').replace("\n", " ")


class Automated:
    transaction_repository = NotImplementedError
    user_repository = NotImplementedError
    invoice_repository = NotImplementedError
    accounts_repository = NotImplementedError
    captcha_repository = NotImplementedError

    def __init__(self, transaction_repository, user_repository, invoice_repository, accounts_repository,
                 captcha_repository):
        self.transaction_repository = transaction_repository
        self.user_repository = user_repository
        self.invoice_repository = invoice_repository
        self.accounts_repository = accounts_repository
        self.captcha_repository = captcha_repository

    def run(self, account, body="", def_end=None):
        args = account.automated_args.split(',')
        method = getattr(self, args.pop(0))
        try:
            method(args, account, body, def_end)
        except:
            print(traceback.print_exc())

    def driver(self):
        driver = webdriver.Chrome('C:/chromedriver.exe')
        return driver

    def parse(self, result, saccount, driver=None):
        user = self.user_repository.get_by_id(saccount.user.id)
        print('Resolved', saccount.description, driver)
        transactions = result['transactions']
        cards = result['cards']
        automated_ids = list(map(lambda item: item.automated_id, saccount.transactions))
        for transaction in transactions:
            try:
                sautomated_id = transaction.get('automated_id', None)
                automated_id = hashlib.md5(json.dumps(transaction, sort_keys=True).encode(
                    "utf-8")).hexdigest() if sautomated_id is None else sautomated_id
                if automated_id in automated_ids:
                    continue
                stransaction = Transaction()
                stransaction.account_id = saccount.id
                stransaction.automated_id = automated_id
                if transaction['date'] is None:
                    continue
                stransaction.date = datetime.strptime(transaction['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                stransaction.description = transaction['description']
                stransaction.value = transaction['value']
                stransaction.paid = True
                print(self.transaction_repository.save(stransaction))
            except Exception:
                print(traceback.print_exc())
        for card in cards:
            for invoice in card:
                saccount_invoices = list(
                    filter(lambda account: account.description == invoice['cardNumber'], user.accounts))
                if len(saccount_invoices) == 0:
                    saccount_invoice = Account()
                    saccount_invoice.user_id = saccount.user.id
                    saccount_invoice.is_credit_card = True
                    saccount_invoice.prefer_debit_account_id = saccount.id
                    saccount_invoice.description = invoice['cardNumber']
                    print(self.accounts_repository.save(saccount_invoice))
                else:
                    saccount_invoice = saccount_invoices[0]

                automated_ids = list(map(lambda item: item.automated_id, saccount_invoice._transactions))
                stransactions = []
                for data in invoice['values']:
                    if data['date'] is None:
                        continue
                    sautomated_id = data.get('automated_id', None)
                    automated_id = hashlib.md5(json.dumps(data, sort_keys=True).encode(
                        "utf-8")).hexdigest() if sautomated_id is None else sautomated_id
                    if automated_id in automated_ids:
                        continue
                    automated_ids.append(automated_id)
                    stransaction = Transaction()
                    stransaction.account_id = saccount_invoice.id
                    stransaction.automated_id = automated_id
                    stransaction.date = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    stransaction.description = data['description']
                    stransaction.value = data['value']
                    stransaction.paid = True
                    stransactions.append(stransaction)
                if len(stransactions) == 0:
                    continue
                dates = list(map(lambda transaction: transaction.date, stransactions))
                min_date = min(dates)
                max_date = max(dates)
                middle_date = datetime.strptime(invoice['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                sinvoices = list(filter(lambda sinvoice: (sinvoice.debit_date - middle_date.date()).days == 0,
                                        saccount_invoice.invoices))
                if len(sinvoices) == 0:
                    sinvoice = Invoice()
                    sinvoice.debit_date = middle_date
                    sinvoice.date_init = min_date
                    sinvoice.date_end = max_date
                    sinvoice.account_id = saccount_invoice.id
                    sinvoice.description = 'Automated'
                    print(self.invoice_repository.save(sinvoice))
                else:
                    sinvoice = sinvoices[0]
                for stransaction in stransactions:
                    stransaction.invoice_id = sinvoice.id
                    print(self.transaction_repository.save(stransaction))

        if result.get('cdb', None) is None:
            if driver is not None:
                driver.close()
            return
        saccounts_cdb = list(
            filter(lambda
                       account: account.description == 'CDB Automated' and saccount.id == account.prefer_debit_account_id,
                   user.accounts))
        if len(saccounts_cdb) == 0:
            saccount_cdb = Account()
            saccount_cdb.user_id = saccount.user.id
            saccount_cdb.prefer_debit_account_id = saccount.id
            saccount_cdb.description = 'CDB Automated'
            print(self.accounts_repository.save(saccount_cdb))
        else:
            saccount_cdb = saccounts_cdb[0]
        transactions = saccount_cdb.transactions
        applied = sum(list(map(lambda l_transaction: l_transaction.value, transactions)))
        rest = result['cdb'] - applied
        if rest != 0:
            transaction = Transaction()
            transaction.account_id = saccount_cdb.id
            transaction.value = rest
            transaction.description = 'Automated CDB update'
            transaction.date = datetime.now()
            transaction.paid = True
            print(self.transaction_repository.save(transaction))
        if driver is not None:
            driver.close()

    def sync_banco_do_brasil(self, args, saccount, _, def_end):
        agency, account, password = args
        driver = self.driver()
        result = banco_do_brasil.get(driver, agency, account, password)
        self.parse(result, saccount, driver)
        if def_end is not None:
            def_end()

    def sync_picpay(self, args, saccount, _, def_end):
        email, password = args
        result = picpay.get(email, password)
        self.parse(result, saccount)
        if def_end is not None:
            def_end()

    def sync_banco_inter(self, args, saccount, isafe, def_end):
        account, password = args
        driver = self.driver()
        result = banco_inter.get(driver, account, password, isafe)
        self.parse(result, saccount, driver)
        if def_end is not None:
            def_end()

    def sync_banco_caixa(self, args, saccount, _, def_end):
        username, password = args
        driver = self.driver()
        result = banco_caixa.get(driver, username, password)
        self.parse(result, saccount, driver)
        if def_end is not None:
            def_end()

    def sync_banco_nuconta(self, args, saccount, _, def_end):
        cpf, password = args
        result = banco_nu.get(cpf, password)
        self.parse(result, saccount)
        if def_end is not None:
            def_end()

    def sync_sodexo_alimentacao(self, args, saccount, _, def_end):
        cartao, cpf = args
        driver = self.driver()
        result = sodexo_alimentacao.get(driver, cartao, cpf, self.captcha_repository)
        self.parse(result, saccount, driver)
        if def_end is not None:
            def_end()

    def sync_banco_itau(self, args, saccount, _, def_end):
        agency, account, password = args
        transactions = self.banco_itau(agency, account, password)
        stored_transactions = saccount.transactions
        for transaction in transactions:
            contains = False
            for stored_transaction in stored_transactions:
                if stored_transaction.value == transaction.value and (
                        transaction.date.date() - stored_transaction.date).days == 0:
                    if not stored_transaction.paid:
                        stored_transaction.paid = True
                        print(self.transaction_repository.save(stored_transaction))
                    contains = True
                    break
            if not contains:
                transaction.account_id = saccount.id
                transaction.paid = True
                print(self.transaction_repository.save(transaction))
        if def_end is not None:
            def_end()

    def banco_itau(self, agencia, conta, senha):
        transactions = []
        driver = self.driver()
        try:
            driver.get("https://www.itau.com.br/")
            driver.set_window_size(1936, 1066)
            WebDriverWait(driver, 30000).until(expected_conditions.visibility_of_element_located((By.ID, "agencia")))
            driver.find_element(By.ID, "agencia").send_keys(agencia)
            driver.find_element(By.ID, "conta").send_keys(conta)
            driver.execute_script(
                "const btn = document.getElementById(\'btnLoginSubmit\');btn.disabled=false;btn.class = \"send active icon-itaufonts_seta_right\"")
            driver.find_element(By.ID, "btnLoginSubmit").click()
            WebDriverWait(driver, 30000).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".tecla:nth-child(1)")))
            driver.execute_script(
                "var senha = \"" + senha + "\"; var i = 0; var fn = () => { if (!senha[i]) { document.querySelector('#acessar').click(); return; } [...document.querySelectorAll(\'.tecla\')].filter(t => t.innerText.indexOf(senha[i]) > -1)[0].click();i++;setTimeout(fn, 100) };setTimeout(fn, 100)")
            time.sleep(5)
            WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.ID, "VerExtrato")))
            driver.find_element(By.ID, "VerExtrato").click()
            WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.ID, "select-55")))
            driver.execute_script(
                "document.querySelector(\"#select-55\").value=90; document.querySelector(\"#select-55\").dispatchEvent(new Event(\"change\"))");
            time.sleep(5)
            lines = driver.find_element(By.CSS_SELECTOR,
                                        "#gridLancamentos-pessoa-fisica").find_elements_by_css_selector(
                'tr')
            for line in lines:
                if line.get_attribute('innerText') is None:
                    continue
                columns = line.find_elements_by_css_selector('td')
                if len(columns) >= 4:
                    try:
                        transaction = Transaction()
                        transaction.value = _parse_brl_to_float(columns[2].get_attribute('innerText'))
                        transaction.description = _clean_description(columns[1].get_attribute('innerText'))
                        transaction.date = _parse_dd_mm_yyyy(columns[0].get_attribute('innerText'))
                        transaction.paid = True
                        transactions.append(transaction)
                    except Exception as error_inline:
                        print('Possible not an error - inline', self.banco_itau.__name__, str(error_inline))
        except Exception as error:
            print('Error', self.banco_itau.__name__, str(error))
        driver.quit()
        return transactions
