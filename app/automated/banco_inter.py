import os
from datetime import datetime

from jsmin import jsmin
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

now = datetime.now()

with open(os.path.dirname(__file__) + '/banco_inter.js') as js_file:
    minjs = jsmin(js_file.read())


def __login(driver, conta, senha, isafe):
    driver.get("https://internetbanking.bancointer.com.br/")
    driver.maximize_window()
    driver.execute_script(minjs)
    driver.find_element(By.ID, "loginv20170605").click()
    driver.find_element(By.ID, "loginv20170605").send_keys(conta)
    driver.find_element(By.NAME, "j_idt35").click()
    driver.find_element(By.ID, "j_idt159").click()
    driver.execute_script(minjs)
    driver.execute_script("window.pybancointer.login.methods.password(\"" + senha.replace('\n', '') + "\");")
    WebDriverWait(driver, 15).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".grid-35")))
    driver.find_element(By.ID, "codigoAutorizacaoAOTP").send_keys(str(isafe))
    driver.find_element(By.ID, "confirmarCodigoTransacaoAOTP").click()
    WebDriverWait(driver, 15).until(
        expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#j_idt106\\3A 4\\3Aj_idt109 span")))


def __faturas(driver):
    driver.find_element(By.CSS_SELECTOR, "#j_idt106\\3A 4\\3Aj_idt109 span").click()
    driver.execute_script(
        "mojarra.jsfcljs(document.getElementById('frmMenus'),{'j_idt106:4:j_idt115:0:j_idt117':'j_idt106:4:j_idt115:0:j_idt117'},'');")
    WebDriverWait(driver, 15).until(
        expected_conditions.visibility_of_element_located((By.NAME, "j_idt146:0:j_idt298")))
    driver.find_element(By.NAME, "j_idt146:0:j_idt298").click()
    driver.find_element(By.NAME, "j_idt210").click()
    driver.execute_script(minjs)
    driver.execute_script("window.pybancointer.faturas.methods.get();")
    WebDriverWait(driver, 100).until(
        expected_conditions.visibility_of_element_located((By.ID, "result")))
    return driver.execute_script("return window.pybancointer.faturas.cartoes")


def __extrato(driver):
    driver.find_element(By.CSS_SELECTOR, "#j_idt106\\:0\\:j_idt109 span").click()
    driver.execute_script(
        "mojarra.jsfcljs(document.getElementById('frmMenus'),{'j_idt106:0:j_idt115:0:j_idt117':'j_idt106:0:j_idt115:0:j_idt117'},'');")
    WebDriverWait(driver, 100).until(
        expected_conditions.visibility_of_element_located((By.ID, "form\\:periodoExtrato")))
    driver.execute_script("$('#form\\:periodoExtrato').val(\"NOVENTA\")")
    driver.execute_script("$('#form\\:periodoExtrato').change()")
    driver.execute_script("$('[name=\"form:j_idt147\"]').click()")
    driver.execute_script(minjs)
    WebDriverWait(driver, 100).until(
        expected_conditions.visibility_of_element_located((By.ID, "result")))
    return driver.execute_script("returnwindow.pybancointer.extrato.results")


def get(driver, conta, senha, isafe):
    __login(driver, conta, senha, isafe)
    return {
        'transactions': [],  # __extrato(driver),
        'cards': __faturas(driver)
    }
