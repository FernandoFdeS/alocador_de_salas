import pandas as pd
import re
from Aula import Aula
from Horario import Horario

# Cria horarios
horarios_fixos = dict()
for i in range(6):
    for j in range(16):
        horarios_fixos["Horario_"+(str(i+2))+"_"+(str(j+1))]=(Horario(i+2,j+1))

# for horario in horarios:
#     print(horario,horarios[horario].dia,horarios[horario].faixa)
# print(len(horarios))

# Pega os horarios das aulas
dados = pd.read_excel("./dados/horarios.xlsx", header=None)
dados = dados.iloc[:, 1]
horarios = ""
cod_aula= ""
n_turma = ""
padrao = r"(\d+)([A-Za-z]+)(\d+)"
padrao_n_turma = r"Turma:(\d+)"
periodo_map = dict()
periodo_map["M"]=0
periodo_map["T"]=6
periodo_map["N"]=12

disciplinas = dict()

for dado in dados:
    cod_aula = dado.split("-")
    cod_aula = cod_aula[0]
    cod_aula = cod_aula[:-1]
    turma = re.search(padrao_n_turma,dado)
    n_turma = turma.group(1)
    horarios = dado.split("/")
    horarios = horarios[0].split("-")
    horarios = horarios[-1].split(":")
    horarios = horarios[1]
    horarios = horarios[:-3]
    horarios = horarios.split()
    #print(horario)
    #print(cod_aula+"_"+n_turma)
    #print(turma)
    horario_aula=dict()
    for horario in horarios:
        dias=""
        periodo=""
        faixas=""
        resultado = re.match(padrao,horario)
        dias=resultado.group(1)
        periodos=resultado.group(2)
        faixas=resultado.group(3)

        for dia in dias:
            for periodo in periodos:
                for faixa in faixas:
                    dia_horario= int(dia)
                    faixa_horario = (int(periodo_map[periodo]))+int(faixa)
                    #print( dia_horario,faixa_horario)
                    horario_aula["Horario_{}_{}".format(dia_horario,faixa_horario)]=Horario(dia_horario,faixa_horario)
        

    aula = Aula(30,horario_aula) #não tem o tamanho da turma nos horários
    disciplinas[cod_aula+"_"+n_turma]=aula

# for d in disciplinas:
#     print(d)
#     for h in disciplinas[d].horarios:
#         print(h)
