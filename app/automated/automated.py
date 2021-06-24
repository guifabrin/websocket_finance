import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from app.models import Transaction

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


def _banco_do_brasil_login(driver, agencia, conta, senha):
    driver.get("https://www2.bancobrasil.com.br/aapf/login.html?1624286762470#/acesso-aapf-agencia-conta-1")
    WebDriverWait(driver, 5).until(
        expected_conditions.visibility_of_element_located((By.ID, "dependenciaOrigem")))
    driver.find_element(By.ID, "dependenciaOrigem").send_keys(agencia)
    WebDriverWait(driver, 5).until(
        expected_conditions.visibility_of_element_located((By.ID, "numeroContratoOrigem")))
    driver.find_element(By.ID, "numeroContratoOrigem").send_keys(conta)
    driver.find_element(By.ID, "botaoEnviar").click()
    WebDriverWait(driver, 5).until(
        expected_conditions.visibility_of_element_located((By.ID, "senhaConta")))
    driver.find_element(By.ID, "senhaConta").send_keys(senha)
    try:
        driver.find_element(By.ID, "botaoEnviar").click()
    except Exception as err_button_sent:
        print('Possible not an error - button sent', _banco_do_brasil_login.__name__, err_button_sent)
    time.sleep(3)
    WebDriverWait(driver, 5).until(
        expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".menu-completo > .menu-itens")))


def banco_do_brasil(agencia, conta, senha):
    transactions = []
    driver = webdriver.Chrome('./app/automated/chromedriver.exe')
    try:
        _banco_do_brasil_login(driver, agencia, conta, senha)
        driver.execute_script("document.querySelector(\'[codigo=\"32456\"]\').click()")
        WebDriverWait(driver, 5).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#tabelaExtrato")))
        lines = driver.find_element(By.ID, "tabelaExtrato").find_elements_by_css_selector('tr')
        for line in lines:
            columns = line.find_elements_by_css_selector('td')
            if len(columns) >= 4:
                try:
                    value, credito_debito = columns[4].get_attribute('innerText').split(' ')
                    multiplier = -1 if credito_debito == 'D' else 1
                    transaction = Transaction()
                    transaction.value = _parse_brl_to_float(value) * multiplier
                    transaction.description = _clean_description(columns[2].get_attribute('innerText'))
                    transaction.date = _parse_dd_mm_yyyy(columns[0].get_attribute('innerText'))
                    if transaction.description not in ['Saldo Anterior']:
                        transactions.append(transaction)
                except Exception as error_inline:
                    print('Possible not an error - inline', banco_do_brasil.__name__, str(error_inline))
    except Exception as error:
        print('Error', banco_do_brasil.__name__, str(error))
    driver.quit()
    return transactions


def banco_do_brasil_cdb(agencia, conta, senha):
    driver = webdriver.Chrome('./app/automated/chromedriver.exe')
    try:
        _banco_do_brasil_login(driver, agencia, conta, senha)
        driver.execute_script("document.querySelector(\'[codigo=\"33130\"]\').click()")
        WebDriverWait(driver, 5).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#botaoContinua")))
        driver.find_element(By.ID, "botaoContinua").click()
        WebDriverWait(driver, 5).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#botaoContinua2")))
        driver.find_element(By.ID, "botaoContinua2").click()
        WebDriverWait(driver, 5).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, ".transacao-corpo  table:nth-child(6)")))
        lines = driver.find_element(By.CSS_SELECTOR,
                                    ".transacao-corpo  table:nth-child(6)").find_elements_by_css_selector('tr')
        for line in lines:
            if "Saldo liquido projetado" in line.get_attribute('innerText').replace('\xa0', ' '):
                non_blank_items = list(
                    filter(lambda s: s != "", line.get_attribute('innerText').replace('\xa0', ' ').split(' ')))
                replaced_items = list(
                    map(lambda s: s.replace('\n', '').replace('\t', '').replace('.', '').replace(',', '.'),
                        non_blank_items))
                return float(replaced_items[len(replaced_items) - 1])
    except Exception as error:
        print('Error', banco_do_brasil_cdb.__name__, str(error))
    driver.quit()
    return None


def banco_do_brasil_cc(agencia, conta, senha):
    transactions = []
    driver = webdriver.Chrome('./app/automated/chromedriver.exe')
    try:
        _banco_do_brasil_login(driver, agencia, conta, senha)
        driver.execute_script("document.querySelector(\'[codigo=\"32715\"]\').click()")
        WebDriverWait(driver, 5).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#carousel-cartoes img")))
        cards = driver.find_elements(By.CSS_SELECTOR, "#carousel-cartoes img")
        index = -1
        for _ in cards:
            try:
                index = index + 1
                driver.execute_script("buscaFaturas(" + str(index) + ");")
                time.sleep(2)
                WebDriverWait(driver, 5).until(
                    expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".lancamentos")))
                releases = driver.find_elements(By.CSS_SELECTOR, ".lancamentos")
                for release in releases:
                    lines = release.find_elements_by_css_selector('tr')
                    for line in lines:
                        if line.get_attribute('innerText') is None:
                            continue
                        columns = line.find_elements_by_css_selector('td')
                        if len(columns) >= 4:
                            try:
                                transaction = Transaction()
                                transaction.value = _parse_brl_to_float(columns[4].get_attribute('innerText')) * -1
                                transaction.description = _clean_description(columns[1].get_attribute('innerText'))
                                transaction.date = _parse_dd_mm(columns[0].get_attribute('innerText'))
                                transaction.paid = True
                                if transaction.description not in ['Saldo Anterior']:
                                    transactions.append(transaction)
                            except Exception as error_inline:
                                print('Possible not an error - inline', banco_do_brasil_cc.__name__, str(error_inline))
            except Exception as error_card:
                print('Possible not an error - card', banco_do_brasil_cc.__name__, str(error_card))
    except Exception as error:
        print('Error', banco_do_brasil_cc.__name__, str(error))
    driver.quit()
    return transactions


def caixa(usuario, senha):
    transactions = []
    driver = webdriver.Chrome('./app/automated/chromedriver.exe')
    try:
        driver.get("https://internetbanking.caixa.gov.br/sinbc/#!nb/login")
        time.sleep(3)
        WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.ID, "nomeUsuario")))
        driver.find_element(By.ID, "nomeUsuario").send_keys(usuario)
        driver.find_element(By.ID, "btnLogin").click()
        time.sleep(3)
        WebDriverWait(driver, 5).until(
            expected_conditions.visibility_of_element_located((By.ID, "lnkInitials")))
        driver.find_element(By.ID, "lnkInitials").click()
        time.sleep(3)
        WebDriverWait(driver, 5).until(
            expected_conditions.visibility_of_element_located((By.ID, "password")))
        driver.execute_script("document.querySelector(\'#password\').value=\'" + senha.replace('\n', '') + "\'")
        driver.find_element(By.ID, "btnConfirmar").click()
        time.sleep(5)
        try:
            driver.execute_script("document.getElementById('modal-campanha').remove();")
        except Exception as error_modal:
            print('Possible not an error - modal', caixa.__name__, str(error_modal))
        time.sleep(5)
        driver.find_element(By.CSS_SELECTOR, "li:nth-child(1) .sup > .icone-menu").click()
        time.sleep(5)
        driver.find_element(By.LINK_TEXT, "Extrato").click()
        time.sleep(5)
        lines = driver.find_element(By.CSS_SELECTOR, ".movimentacao").find_elements_by_css_selector('tr')
        for line in lines:
            columns = line.find_elements_by_css_selector('td')
            if len(columns) >= 4:
                try:
                    str_value, credito_debito = columns[3].get_attribute('innerText').split(' ')
                    multiplier = -1 if credito_debito == 'D' else 1
                    transaction = Transaction()
                    transaction.value = _parse_brl_to_float(str_value) * multiplier
                    transaction.description = _clean_description(columns[2].get_attribute('innerText'))
                    transaction.date = _parse_dd_mm_yyyy(columns[0].get_attribute('innerText'))
                    if transaction.description not in ['Saldo Anterior']:
                        transactions.append(transaction)
                except Exception as error_inline:
                    print('Possible not an error - inline', caixa.__name__, str(error_inline))
    except Exception as error:
        print('Error', caixa.__name__, str(error))
    driver.quit()
    return transactions


def banco_inter_cc(conta, senha, isafe):
    transactions = []
    driver = webdriver.Chrome('./app/automated/chromedriver.exe')
    try:
        driver.get("https://internetbanking.bancointer.com.br/")
        driver.set_window_size(1305, 883)
        driver.find_element(By.ID, "loginv20170605").click()
        driver.find_element(By.ID, "loginv20170605").send_keys(conta)
        driver.find_element(By.NAME, "j_idt35").click()
        driver.find_element(By.ID, "j_idt159").click()
        driver.execute_script(
            "pass=\"" + senha.replace('\n',
                                      '') + "\",i=0,b=!0,fn=(()=>{pass[i]?(j=document.querySelector(\'[title=\"\'+pass[i]+\'\"]\'),j?(console.log(pass[i]),j.click(),i++):(console.log(\"err \"+pass[i]),document.querySelector(\'[title=\"▲\"]\')&&document.querySelector(\'[title=\"▲\"]\').click(),j=document.querySelector(\'[title=\"\'+pass[i]+\'\"]\'),j?(console.log(pass[i]),j.click(),i++):(console.log(\"err2 \"+pass[i]),document.querySelector(\'[title=\"ABC\"]\')?document.querySelector(\'[title=\"ABC\"]\').click():document.querySelector(\'[title=\"!?.\"]\').click(),j=document.querySelector(\'[title=\"\'+pass[i]+\'\"]\'),j?(console.log(pass[i]),j.click(),i++):console.log(\"err3 \"+pass[i]))),setTimeout(fn,300)):document.querySelector(\'[title=\"Confirmar\"]\').click()}),setTimeout(fn,300);")
        WebDriverWait(driver, 5).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".grid-35")))
        driver.find_element(By.ID, "codigoAutorizacaoAOTP").send_keys(isafe)
        driver.find_element(By.ID, "confirmarCodigoTransacaoAOTP").click()
        WebDriverWait(driver, 5).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#j_idt106\\3A 4\\3Aj_idt109 span")))
        driver.find_element(By.CSS_SELECTOR, "#j_idt106\\3A 4\\3Aj_idt109 span").click()
        element = driver.find_element(By.CSS_SELECTOR, "#j_idt106\\3A 4\\3Aj_idt109 span")
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        driver.find_element(By.CSS_SELECTOR, ".cf:nth-child(1) a").click()
        driver.find_element(By.NAME, "j_idt146:0:j_idt298").click()
        driver.find_element(By.NAME, "j_idt210").click()
        lines = driver.find_element(By.CSS_SELECTOR, "[role=\"grid\"]").find_elements_by_css_selector('tr')
        for line in lines:
            if line.get_attribute('innerText') is None:
                continue
            columns = line.find_elements_by_css_selector('td')
            if len(columns) >= 4:
                try:
                    transaction = Transaction()
                    transaction.value = _parse_brl_to_float(columns[4].get_attribute('innerText')) * -1
                    transaction.description = _clean_description(columns[1].get_attribute('innerText'))
                    transaction.date = _parse_dd_mm_yyyy(columns[3].get_attribute('innerText'))
                    transaction.paid = True
                    transactions.append(transaction)
                except Exception as error_inline:
                    print('Possible not an error - inline', banco_inter_cc.__name__, str(error_inline))
    except Exception as error:
        print('Error', banco_inter_cc.__name__, str(error))
    driver.quit()
    return transactions
