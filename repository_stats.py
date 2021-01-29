import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta




def pega_periodo(since, until):
    counter = Counter()
    os.environ['_GIT_SINCE']=since
    os.environ['_GIT_UNTIL']=until
    out = subprocess.run(['git-quick-stats',  '-T'], stdout=subprocess.PIPE).stdout
    lines = out.decode().split('\n')
    usuario_atual = ''
    for line in lines:
        line = line.strip()
        posi_chave = line.find('<')
        if posi_chave != -1:
            usuario_atual = line[0:posi_chave].strip()
        posi_changed = line.find('changed:')
        if posi_changed != -1:
            qtde = int(line.split()[2].strip())
            counter[usuario_atual] += qtde
    return counter


def pega_projeto(caminho):
    resultado = dict()
    os.chdir(caminho)
    dataincial = datetime(2017, 7, 1)
    datafinal = datetime.today()
    delta_meses = (datafinal.year - dataincial.year) * 12 + datafinal.month - dataincial.month
    for months in range(delta_meses + 1):
        date_since = dataincial + relativedelta(months=months)
        date_until = date_since + relativedelta(months=1)
        since = datetime.strftime(date_since, '%Y-%m-%d')
        until = datetime.strftime(date_until, '%Y-%m-%d')
        counter = pega_periodo(since, until)
        # print(since, until, counter)
        resultado[since] = counter
    return resultado

projetos = {'ajna_bot': '/home/ivan/PycharmProjects/ajna_bot',
            'bhadrasana2': '/home/ivan/PycharmProjects/bhadrasana2',
            'virasana': '/home/ivan/pybr/ajna/virasana',
            'ajnaapi': '/home/ivan/pybr/ajna_api'}

path = os.path.dirname(os.path.abspath(__file__))
out_filename = os.path.join(path, 'git_stats.csv')


todos_usuarios = set()
resultados = {}
for projeto, caminho in projetos.items():
    resultado = pega_projeto(caminho)
    print(projeto, resultado)
    for since, counter in resultado.items():
        for usuario, qtde in counter.items():
            todos_usuarios.add(usuario)
    resultados[projeto] = resultado
print(todos_usuarios)
datas = sorted(list(resultados['ajna_bot'].keys()))
cabecalho = ['usuario', *datas]
with open(out_filename, 'w') as file_out:
    # print(', '.join(cabecalho))
    file_out.write(', '.join(cabecalho) + '\n')
    for projeto, _ in projetos.items():
        resultado = resultados[projeto]
        # print(projeto)
        file_out.write(projeto + '\n')
        for usuario in todos_usuarios:
            linha = [usuario]
            for data in datas:
                counter = resultado[data]
                linha.append(str(counter.get(usuario, 0)))
            # print(linha)
            # print(','.join(linha))
            file_out.write(','.join(linha) + '\n')


