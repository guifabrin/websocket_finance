window.pybancodobrasil = {
    extratos: {
        counter: 0,
        results: [],
        methods: {
            goto: () => {
                document.querySelector('[codigo="32456"]').click()
            },
            get: (month, year) => {
                window.pybancodobrasil.extratos.counter++;
                $.ajaxApf({
                    atualizaContadorSessao: true,
                    cache: false,
                    funcaoSucesso: (data) => {
                        try {
                            if (data) {
                                const table = $(data).find('table#tabelaExtrato')[0]
                                if (table)
                                    window.pybancodobrasil.extratos.results = [...window.pybancodobrasil.extratos.results, ...window.pybancodobrasil.extratos.methods.table2Json(table)];
                            }
                        } catch (error) {
                            console.log(error)
                        }
                        window.pybancodobrasil.extratos.counter--;
                    },
                    funcaoErro: () => {
                        window.pybancodobrasil.extratos.counter--;
                    },
                    parametros: {
                        ambienteLayout: "internoTransacao",
                        confirma: "sim",
                        periodo: `00${month.padStart(2, '0')}${year}`,
                        tipoConta: "",
                        novoLayout: "sim"
                    },
                    simbolo: "30151696898430647187469639762490",
                    tiporetorno: "html",
                    type: "post",
                    url: "/aapf/extrato/009-00-N.jsp"
                })
            },
            table2Json: (table) => {
                var data = [];
                for (var i = 1; i < table.rows.length; i++) {
                    var tableRow = table.rows[i];
                    var rowData = [];
                    for (var j = 0; j < tableRow.cells.length; j++) {
                        rowData.push(tableRow.cells[j].innerText);;
                    }
                    data.push(rowData);
                }
                for (let index in data) {
                    if (data[index].length < 4) {
                        delete data[index];
                    } else {
                        if (!data[index][4]) {
                            delete data[index]
                        }
                    }
                }
                return window.pybancodobrasil.extratos.methods.parse(data.filter(item => item));
            },
            parse(array) {
                const parsed = [];
                for (let [data, a, descricao, b, valor] of array) {
                    if (descricao == 'Saldo Anterior') {
                        continue;
                    }
                    const [dd, mm, yyyy] = data.split('/');
                    const [strvalor, cd] = valor.split(' ');
                    parsed.push({
                        date: new Date(`${yyyy}-${mm}-${dd}`),
                        value: parseFloat(strvalor.replace('.', '').replace(',', '.')) * (cd == 'C' ? 1 : -1),
                        description: descricao
                    })
                }
                return parsed;
            },
        }
    },
    faturas: {
        cartoes: [],
        done: false,
        methods: {
            goto: () => {
                document.querySelector('[codigo="32715"]').click()
            },
            cartoes: () => {
                return document.querySelector('#carousel-cartoes').childElementCount;
            },
            faturas: () => {
                return document.querySelectorAll('[indicetabs]').length;
            },
            buscaFaturas: (indice) => {
                var url = "/aapf/cartao/v119-01e2.jsp?indice=" + indice;
                var req = configura();
                req.open("GET", url, true);
                req.onreadystatechange = function () {
                    if (req.readyState == 4) {
                        let len = $(req.responseText).find('li').size();
                        window.pybancodobrasil.faturas.methods.buscaExtrato(indice, 0, len, () => {
                            if ((indice + 1) < window.pybancodobrasil.faturas.methods.cartoes()) {
                                window.pybancodobrasil.faturas.methods.buscaFaturas(indice + 1)
                            } else {
                                window.pybancodobrasil.faturas.done = true
                            }
                        })

                    }
                };
                req.send(null);
            },
            buscaExtrato: (cartao, ind, len, fnEnd) => {
                var indice = ind;
                try {
                    var url = "/aapf/cartao/v119-01e3.jsp?indice=" + indice + "&pagina=normal";
                    var req = configura();
                    req.open("GET", url, true);
                    req.onreadystatechange = function () {
                        if (req.readyState == 4) {
                            const result = window.pybancodobrasil.faturas.methods.parse(req.responseText)
                            if (result && result.values.length) {
                                if (!window.pybancodobrasil.faturas.cartoes[cartao]) {
                                    window.pybancodobrasil.faturas.cartoes[cartao] = []
                                }
                                window.pybancodobrasil.faturas.cartoes[cartao].push(result)
                            }
                            if ((ind + 1) < len) {
                                window.pybancodobrasil.faturas.methods.buscaExtrato(cartao, ind + 1, len, fnEnd);
                            } else {
                                fnEnd();
                            }
                        }
                    };
                    req.send(null);
                } catch (e) {
                }
            },
            table2Json: (table) => {
                var data = [];
                for (var i = 1; i < table.rows.length; i++) {
                    var tableRow = table.rows[i];
                    var rowData = [];
                    for (var j = 0; j < tableRow.cells.length; j++) {
                        rowData.push(tableRow.cells[j].innerText);;
                    }
                    data.push(rowData);
                }
                for (let index in data) {
                    if (data[index].length != 4) {
                        delete data[index];
                    } else {
                        if (!data[index][3] || data[index][0] == " " || data[index][3] == " ") {
                            delete data[index]
                        }
                    }
                }
                return window.pybancodobrasil.faturas.methods.parseValues(data);
            },
            parseValues(array) {
                const values = [];
                for (let data of array) {
                    try {
                        const [dd, mm] = data[0].split('/');
                        const description = data[1]
                        const value = parseFloat(data[3].replace('.', '').replace(',', '.')) * -1;
                        if (!value) {
                            continue;
                        }
                        values.push({
                            date: new Date(`2021-${(parseInt(mm) + '').padStart(2, '0')}-${dd}`),
                            description,
                            value,
                        })
                    } catch (e) { }
                }
                return values;
            },
            parse: (data) => {
                const $el = $(data).find('.textoIdCartao')[1]
                if (!$el) {
                    return;
                }
                const cardNumber = $(data).find('.textoIdCartao')[1].innerText;
                const tables = $(data).find('table').toArray()
                let values = [];
                for (const table of tables) {
                    const nvalues = window.pybancodobrasil.faturas.methods.table2Json(table);
                    if (nvalues && nvalues.length)
                        values = [...values, ...nvalues];
                }
                const [dd, mm, yyyy] = $(data).find('.dadosAtencaoDestaque')[0].innerText.split('/')
                return {
                    values,
                    cardNumber,
                    date: new Date(`${yyyy}-${mm}-10`)
                }
            }
        }
    }
}