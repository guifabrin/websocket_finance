import os
from tika import parser

result = [os.path.join(dp, f) for dp, dn, filenames in os.walk('.\\notas_corretagem') for f in filenames if os.path.splitext(f)[1] == '.pdf']

all = []
for filename in result:
    raw = parser.from_file(filename)
    lines = raw['content'].split('\n')
    lines = list(filter(lambda line: '1-BOVESPA' in line, lines))
    for line in lines:
        splitted = line.split(' ')
        compra_venda = splitted[1]
        valor = splitted[len(splitted)-3]
        qtd = splitted[len(splitted)-4]
        desc = ''
        for i in range(3, len(splitted)-7):
            desc += splitted[i]+' '
        print(compra_venda, valor, qtd, desc)

print(all)