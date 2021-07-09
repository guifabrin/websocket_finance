window.pybancointer = {
    login: {
        methods: {
            password: (password) => {
                index = 0;
                tries = 0;
                fn = () => {
                    try {
                        if (!password[index]) {
                            document.querySelector('[title="Confirmar"]').click();
                            return;
                        }
                        title = `[title='${password[index]}']`;
                        if ($(title)[0]) {
                            $(title).click();
                            index++;
                        } else {
                            tries++;
                            if (tries % 4 == 0)
                                document.querySelector('[name="j_idt65:0:j_idt67"]').click();
                            if (tries % 4 == 1)
                                document.querySelector('[name="j_idt65:0:j_idt67"').click();
                            if (tries % 4 == 2)
                                document.querySelector('[name="j_idt69:1:j_idt73"').click();
                            if (tries % 4 == 3)
                                document.querySelector('[name="j_idt87:7:j_idt88"').click();
                        }
                    } catch (e) { }
                    setTimeout(fn, 500);
                }
                setTimeout(fn, 500);
            }
        },

    },
    extrato:
    {
        results: [],
        methods: {
            get: () => {
                var settings = {
                    "async": true,
                    "crossDomain": true,
                    "url": "https://internetbanking.bancointer.com.br/contacorrente/extratoContaCorrente.jsf",
                    "method": "POST",
                    "headers": {
                        "content-type": "application/x-www-form-urlencoded",
                        "cache-control": "no-cache",
                        "postman-token": "b8087418-9e89-cf1a-be85-5bfc167deefc"
                    },
                    "data": {
                        "j_idt151": "j_idt151",
                        "javax.faces.ViewState": $(`[name="javax.faces.ViewState"]`)[0].value,
                        "j_idt151:j_idt158": "j_idt151:j_idt158"
                    }
                }

                $.ajax(settings).done(function (response) {
                    if (response.startsWith(' Extrato Conta Corrente ')) {
                        for (var i = 8; i < linhas.length; i++) {
                            var [data, desc1, desc2, valor] = linhas[i].split(';')
                            var [dd, mm, yyyy] = data.split('/')
                            if (!valor) {
                                continue;
                            }
                            var value = valor.replace('.', '').replace(',', '.')
                            window.pybancointer.extrato.results.push({
                                date: new Date(`${yyyy}-${mm}-${dd}`),
                                description: desc1 + ' ' + desc2,
                                value: parseFloat(value) * -1
                            })
                        }
                    }

                    var elemento = document.createElement('div');
                    elemento.id = 'result'
                    elemento.innerText = JSON.stringify(window.pybancointer.faturas.cartoes);
                    document.body.appendChild(elemento)
                });
            }
        }
    },
    faturas: {
        cartoes: [],
        methods: {
            get: () => {
                var faturas = $('[name=j_idt203] option').map((index, item) => item.value).toArray()
                var fn = (index) => {
                    if (!faturas[index]) {
                        var elemento = document.createElement('div');
                        elemento.id = 'result'
                        elemento.innerText = JSON.stringify(window.pybancointer.faturas.cartoes);
                        document.body.appendChild(elemento)
                        return;
                    }
                    var settings = {
                        "async": true,
                        "crossDomain": true,
                        "url": "https://internetbanking.bancointer.com.br/cartao/integracao/cartaoExtratoFatura.jsf",
                        "method": "POST",
                        "headers": {
                            "content-type": "application/x-www-form-urlencoded",
                            "cache-control": "no-cache",
                            "postman-token": "91023060-96e9-b7d7-e460-18a815366974"
                        },
                        "data": {
                            "j_idt126": "j_idt126",
                            "javax.faces.ViewState": $(`[name="javax.faces.ViewState"]`)[0].value,
                            "console": "FATURA",
                            "j_idt203": faturas[index],
                            "j_idt210": "Aguarde..."
                        }
                    }
                    $.ajax(settings).done(function (response) {
                        var settings = {
                            "async": true,
                            "crossDomain": true,
                            "url": "https://internetbanking.bancointer.com.br/cartao/integracao/cartaoExtratoFatura.jsf",
                            "method": "POST",
                            "headers": {
                                "content-type": "application/x-www-form-urlencoded",
                                "cache-control": "no-cache",
                                "postman-token": "bd33e533-36b2-ba42-191f-bfb5c7aa8121"
                            },
                            "data": {
                                "j_idt126": "j_idt126",
                                "javax.faces.ViewState": $(`[name="javax.faces.ViewState"]`)[0].value,
                                "console": "FATURA",
                                "j_idt203": faturas[index],
                                "j_idt256": "j_idt256"
                            }
                        }
                        $.ajax(settings).done(function (response) {
                            if (response.startsWith(' Fatura')) {
                                var linhas = response.split('\n');
                                var cardNumber = linhas[2].split(';')[1]
                                var debitDate = linhas[4].split(';')[1]
                                var [dddd, ddmm, ddyyyy] = debitDate.split('/')
                                var values = []
                                for (var i = 8; i < linhas.length; i++) {
                                    var [data, desc1, desc2, valor] = linhas[i].split(';')
                                    var [dd, mm, yyyy] = data.split('/')
                                    if (!valor) {
                                        continue;
                                    }
                                    var value = valor.replace('.', '').replace(',', '.')
                                    values.push({
                                        date: new Date(`${yyyy}-${mm}-${dd}`),
                                        description: desc1 + ' ' + desc2,
                                        value: parseFloat(value) * -1
                                    })
                                }
                                window.pybancointer.faturas.cartoes.push([{
                                    values,
                                    cardNumber,
                                    date: new Date(`${ddyyyy}-${ddmm}-${dddd}`)
                                }])
                            } else if (response.startsWith('<!DOCTYPE html>')) {
                                const [dddd, ddmm, ddyyyy] = $(response).find('table tr').toArray().filter(tr=>tr.innerText.indexOf('Vencimento')>-1)[0].children[1].innerText.trim().split('/')
                                const linhas = $(response).find('table tr.ui-widget-content').toArray().map(tr => [...tr.children].map(td=>td.innerText).join(';'))
                                const cardNumber = $(response).find('.numeroCartao').text().trim()
                                var values = []
                                debugger
                                for (var i = 0; i < linhas.length; i++) {
                                    var [_, desc1, desc2, data, valor] = linhas[i].split(';')
                                    var [dd, mm, yyyy] = data.split('/')
                                    if (!valor) {
                                        continue;
                                    }
                                    var value = valor.replace('.', '').replace(',', '.').replace('R$', '')
                                    values.push({
                                        date: new Date(`${yyyy}-${mm}-${dd}`),
                                        description: desc1 + ' ' + desc2,
                                        value: parseFloat(value) * -1
                                    })
                                }
                                window.pybancointer.faturas.cartoes.push([{
                                    values,
                                    cardNumber,
                                    date: new Date(`${ddyyyy}-${ddmm}-${dddd}`)
                                }])
                            }
                            setTimeout(() => {
                                fn(index + 1)
                            }, 1000)
                        });
                    });
                }
                setTimeout(() => {
                    fn(0)
                }, 1000)
            }
        }
    }
}