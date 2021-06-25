# Tornado API Finance Automated
Esse projeto visa estudar uma integração com Tornado, SQLite e Selenium.
Tem como objetivo estruturar uma forma de sincronizar automaticamente contas
correntes e cartões de crédito visto que os bancos por si só não disponibilizam
API's próprias para pessoa física.

## Atenção: Use por sua conta e risco.

## Como funciona
Atualmente é possível sincronizar os lançamentos do mês corrente apenas das contas:
- Banco do Brasil [conta corrente]
- Banco do Brasil [cartões de crédito]
- Caixa Federal [conta corrente]
- Banco Inter [cartões de crédito]

## Configuração
- Adicionar `chromedriver.exe` em app/automated/
- em `.automated` <- arquivo ignorado configurar o seguinte:
```buildoutcfg
caixa,account_id,usuario,senha
banco_do_brasil,account_id,agencia,conta,senha
banco_do_brasil_cc,account_id,agencia,conta,senha
banco_do_brasil_cdb,account_id,agencia,conta,senha
banco_inter_cc,agencia,conta,senha
```
- Instalar python 3.9.5
- Executar `pip install -r requirements.txt`
- Executar: `main.py runserve`

Requisitar um post para `/api/v1/automated/account_id` passando no body no caso do banco inter o código isafe

## Vue front-end
https://github.com/guifabrin/vue_finance