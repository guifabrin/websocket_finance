import os
import time
from datetime import datetime

from jsmin import jsmin
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

now = datetime.now()

with open(os.path.dirname(__file__) + '/banco_do_brasil.js') as js_file:
    minified = jsmin(js_file.read())


def __login(driver, agencia, conta, senha):
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
        print('Possible not an error - button sent', __login.__name__, err_button_sent)
    time.sleep(3)
    WebDriverWait(driver, 5).until(
        expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".menu-completo > .menu-itens")))


def __extratos(driver, fromyear=1993):
    try:
        driver.execute_script(minified)
        driver.execute_script("window.pybancodobrasil.extratos.methods.goto()")
        for year in range(fromyear, now.year + 1):
            for month in range(1, 13):
                if year == now.year and month > now.month:
                    break
                driver.execute_script(
                    'window.pybancodobrasil.extratos.methods.get(\'' + str(month) + '\', \'' + str(year) + '\')')
        counter = 1
        while counter > 0:
            counter = driver.execute_script('return window.pybancodobrasil.extratos.counter')
            time.sleep(0.3)
        time.sleep(1)
        return driver.execute_script('return window.pybancodobrasil.extratos.results')
    except Exception as error:
        print('Error', __extratos.__name__, str(error))
    return []


def __faturas(driver):
    try:
        driver.execute_script(minified)
        driver.execute_script("window.pybancodobrasil.faturas.methods.goto()")
        time.sleep(0.3)
        driver.execute_script("window.pybancodobrasil.faturas.methods.buscaFaturas(0)")
        done = False
        while not done:
            done = driver.execute_script('return window.pybancodobrasil.faturas.done')
        time.sleep(1)
        return driver.execute_script('return window.pybancodobrasil.faturas.cartoes')
    except Exception as error:
        print('Error', __faturas.__name__, str(error))
    return []


def __cdb(driver):
    driver.execute_script(minified)
    try:
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
        print('Error', __cdb.__name__, str(error))
    return None


def get(driver, agencia, conta, senha):
    __login(driver, agencia, conta, senha)
    return {
        'transactions': __extratos(driver, 1993),
        'cards': __faturas(driver),
        'cdb': __cdb(driver)
    }
