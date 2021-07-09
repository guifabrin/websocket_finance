import os
from datetime import datetime

from jsmin import jsmin
from selenium.webdriver.common.by import By
from app.models import  Captha
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import time

with open(os.path.dirname(__file__) + '/sodexo_alimentacao.js') as js_file:
    minified = jsmin(js_file.read())

def get(driver, cartao, cpf, captha_repository):
    driver.get("https://saldocartao.sodexo.com.br/saldocartao/consultaSaldo.do?operation=setUp")
    driver.find_element(By.ID, "5;2;4").click()
    driver.execute_script("$('#cpf').val('"+cpf+"')")
    driver.execute_script("$('#cardNumber').val('"+cartao+"')")
    driver.execute_script(minified)
    captha = Captha()
    captha.base64_url = driver.execute_script("return window.getDataUrl(document.querySelector('#imagem'))")
    id = captha_repository.save(captha).id
    while not captha.result:
        captha = captha_repository.get_by_id(id)
        time.sleep(1)
    driver.find_element(By.ID, "hiddenField").send_keys(captha.result)
    driver.execute_script("$('[name=cardBalanceForm]').submit()")
    linhas = list(
        map(lambda tr: tr.find_elements_by_css_selector('td'), driver.find_elements_by_css_selector('#gridSaldo tr')))
    transactions = []
    for linha in linhas:
        if len(linha)<5:
            continue
        dd, mm, yyyy = linha[0].text.split('/')
        valor = linha[1].text.replace('.', '').replace(',', '.')
        credito = linha[2].text == 'CRÉDITO'
        descricao = linha[4].text
        transactions.append({
            'date': yyyy+'-'+mm+'-'+dd+ "T00:00:00.000Z",
            'description': descricao,
            'value': float(valor)*(1 if credito else -1)
        })
    return {
        'transactions': transactions,
        'cards': []
    }
