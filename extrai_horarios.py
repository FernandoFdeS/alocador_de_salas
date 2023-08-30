import pandas as pd
import re
from Aula import Aula
from Horario import Horario

dados = pd.read_excel("./dados/horarios.xlsx")
dados = dados.iloc[:, 1]
horarios = ""
padrao = r"(\d+)([A-Za-z]+)(\d+)"

for dado in dados:
    horarios = dado.split("/")
    horarios = horarios[0].split("-")
    horarios = horarios[-1].split(":")
    horarios = horarios[1]
    horarios = horarios[:-3]
    horarios = horarios.split()
    # print(horario)
    for horario in horarios:
        dias=""
        periodo=""
        faixas=""
        resultado = re.match(padrao,horario)
        dias=resultado.group(1)
        periodo=resultado.group(2)
        faixas=resultado.group(3)
        print(dias,periodo,faixas)