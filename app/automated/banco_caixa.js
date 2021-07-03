window.pycaixa = {
    extratos: {
        counter: 0,
        results: [],
        methods: {
            get: () => {
                var nowYear = new Date().getFullYear()
                for (var year = nowYear - 1; year < nowYear + 1; year++) {
                    for (var month = 1; month < 13; month++) {
                        window.pycaixa.extratos.counter++;
                        var settings = {
                            "async": true,
                            "crossDomain": true,
                            "url": "https://internetbanking.caixa.gov.br/SIIBC/data_extrato.processa?ajax=false&nocache=1625503909493",
                            "method": "POST",
                            "headers": {
                                "content-type": "application/x-www-form-urlencoded",
                                "cache-control": "no-cache",
                                "postman-token": "ffa9f441-083b-41f7-8935-b7d891804e40"
                            },
                            "data": {
                                "config": "%7B%22request%22:%7B%7D,%22session%22:%7B%7D,%22todos%22:%7B%7D%7D",
                                "token": $('#token').val(),
                                "extratoEmArquivo": "false",
                                "hdnFormatoArquivo": "",
                                "hdnDataInicio": `01/${(month + '').padStart(2, '0')}/${year}`,
                                "hdnDataFinal": `31/${(month + '').padStart(2, '0')}/${year}`,
                                "hdnMoneyExtrato": "2",
                                "rdoTipoExtrato": "O",
                                "sltOutroMes": "1",
                                "txtDataInicio": "",
                                "txtDataFinal": "",
                                "rdoFormatoExtrato": "",
                                "siperResourceCorrente": $('#contaSelecionada strong').toArray().map(item => item.innerText).join('').replace('-', '')
                            }
                        }
                        $.ajax(settings).done(function (response) {
                            try {
                                $(response).find('tr').toArray().filter(tr => tr.classList.contains('even') || tr.classList.contains('odd')).map(tr => {
                                    var valor = tr.childNodes[7].innerText;
                                    var multiplicador = valor.indexOf('D') > -1 ? -1 : 1;
                                    var value = parseFloat(valor.replace('D', '').replace('C', '').replace('.', '').replace(',', '.')) * multiplicador
                                    var [dd, mm, yyyy] = tr.childNodes[1].innerText.split('/');
                                    window.pycaixa.extratos.results.push({
                                        date: new Date(`${yyyy}-${mm}-${dd}`),
                                        description: tr.childNodes[3].innerText + ' ' + tr.childNodes[5].innerText,
                                        value
                                    })
                                })
                            } catch (e) { }
                            window.pycaixa.extratos.counter--;
                        });
                    }
                }
            }
        }
    }
}