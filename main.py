from Horario import Horario
from Disciplina import Disciplina
from Sala import Sala
from extrai_salas import ExtraiSalas
from extrai_horarios_aula import ExtraiHorariosAula
import pandas as pd
import gurobipy as gp
import numpy as np
from gurobipy import GRB

# Utilizado mais pra "debug".
def cria_csv_alocacoes(disciplinas,salas,horaraios,x):

    alocacoes=[]
    #print("Disciplina  | Horário | Sala | Capacidade restante")
    for d in disciplinas:
        for s in salas:
            for h in disciplinas[d].horarios:
                #print(x[d,s,h].X)
                if(round(x[d,s,h].X))==1:
                    #print(d,h,s,(salas[s].capacidade-disciplinas[d].alunos))
                    alocacoes.append([disciplinas[d].curso,d, h, s, (salas[s].capacidade-disciplinas[d].alunos)])

    # Criar um DataFrame com as informações
    df = pd.DataFrame(alocacoes, columns=["Curso", "Disciplina", "Horario", "Sala", "Capacidade Restante"])

    # Salvar o DataFrame em um arquivo CSV
    nome_arquivo = "alocacoes.csv"
    df.to_csv(nome_arquivo, index=False)

# Gera arquivo de saida final.
def exporta_alocacoes(disciplinas,salas,horarios,x):
    
    disciplinas_nao_alocadas = disciplinas.copy()
    disciplinas_qtd_alocacoes = dict()
    
    alocacoes=[]
    linhas=[]

    coluna_horarios=["SEG-M","TER-M","QUA-M","QUI-M","SEX-M","SAB-M","SEG-V","TER-V","QUA-V","QUI-V","SEX-V","SAB-V","SEG-N","TER-N","QUA-N","QUI-N","SEX-N","SAB-N","Não Alocadas"]

    linha_salas=[]
    for s in salas:
        linha_salas.append(s)    

    matriz = [['-' for coluna in range(len(coluna_horarios))] for linha in range(len(linha_salas))]

    for d in disciplinas:
        disciplinas_qtd_alocacoes[d]=0
        for s in salas:
            for h in disciplinas[d].horarios:
                if(round(x[d,s,h].X))==1:
                    disciplinas_qtd_alocacoes[d] += 1

    ## Mostra a relação entre alocações feitas/ quantidade de horarios  
    # for d in disciplinas:
    #     print(d+" "+str(disciplinas_qtd_alocacoes[d])+"/"+str(len(disciplinas[d].horarios)))

    for d in disciplinas:
        if disciplinas_qtd_alocacoes[d] != len(disciplinas[d].horarios):
            continue
        else:
            del disciplinas_nao_alocadas[d]
        for s in salas:
            for h in disciplinas[d].horarios:
                if(round(x[d,s,h].X))==1:
                    linha = linha_salas.index(s)
                    coluna=(coluna_horarios.index(horarios[h].converte_horario()))
                    if(matriz[linha][coluna]=='-'):
                        matriz[linha][coluna] = disciplinas[d].formata_saida()
                    elif (disciplinas[d].formata_saida() not in matriz[linha][coluna]):
                        matriz[linha][coluna] = matriz[linha][coluna] +" | "+disciplinas[d].formata_saida()
    
    for index,d in enumerate(disciplinas_nao_alocadas):
        if(index<len(linha_salas)):
            matriz[index][coluna_horarios.index("Não Alocadas")]=disciplinas[d].formata_saida()

    coluna_horarios[coluna_horarios.index("Não Alocadas")]=("Não Alocadas ("+str(len(disciplinas_nao_alocadas))+")") 
        
    df = pd.DataFrame(matriz)

    # Criar um DataFrame com rótulos personalizados
    df = pd.DataFrame(matriz, columns=coluna_horarios, index=linha_salas)

    # Exibir o DataFrame personalizado
    nome_arquivo = "alocacoes_final.csv"
    df.to_csv(nome_arquivo, index=True)

    if(len(disciplinas_nao_alocadas))==0:
        print("Alocações realizadas com sucesso!")
    else:
        print("Disciplinas alocadas: "+str((len(disciplinas)-len(disciplinas_nao_alocadas)))+"/"+str(len(disciplinas)))
         

def main():
    salas = ExtraiSalas("./dados/salas_2023_2.csv").extrai_salas()
    disciplinas, horarios,fases = ExtraiHorariosAula("./dados/horarios.xlsx").extrai_horarios_aula()

    # Criando o modelo
    m = gp.Model()
    M = 1000

    # Variaveis
    x = {}
    for d in disciplinas:
        for h in disciplinas[d].horarios:
            for s in salas:
                x[d, s, h] = m.addVar(vtype=gp.GRB.BINARY, name=f"x[{d}, {s}, {h}]")
    y = m.addVars(disciplinas,salas,vtype=gp.GRB.INTEGER, name="y")
    z = m.addVars(salas,fases,vtype=gp.GRB.INTEGER,name="z")

    # Cria vetor de variaveis das salas preferenciais
    vet_salas_preferenciais=[]

    for d in disciplinas:
        for h in disciplinas[d].horarios:
            for s in salas:
                if s not in disciplinas[d].salasPreferenciais:
                    vet_salas_preferenciais.append(x[d,s,h])
    
    # Cria vetor das alocacoes das salas
    vet_alocacoes=[]
    for d in disciplinas:
        for h in disciplinas[d].horarios:
            vet_alocacoes.append(M*(1 - gp.quicksum(x[d,s,h] for s in salas)))

    # Funcao obj
    m.setObjective(gp.quicksum(y[d,s] for d in disciplinas for s in salas) +
                gp.quicksum(vet_salas_preferenciais) +
                gp.quicksum(vet_alocacoes) +
                gp.quicksum(z[s,f]for s in salas for f in fases),
    sense=gp.GRB.MINIMIZE
    )


    # Restricoes

    # No máximo uma disciplina (turma) pode ser alocada a uma sala em um determinado horário:
    c1 = m.addConstrs(
        gp.quicksum(x[d, s, h] for d in disciplinas if h in disciplinas[d].horarios) <= 1
        for s in salas for h in horarios
    )

    # No máximo uma sala pode ser alocada a uma disciplina em um determinado horário
    c2 = m.addConstrs( 
        gp.quicksum(x[d,s,h] for s in salas ) <= 1 for d in disciplinas for h in disciplinas[d].horarios
    )

    # No mínimo uma sala deve ser alocada a uma disciplina em um determinado horário - Movida para a função objetivo
    #c3 = m.addConstrs( 
    #    gp.quicksum(x[d,s,h] for s in salas ) >= 1 for d in disciplinas for h in disciplinas[d].horarios
    #)

    # Uma sala não pode ser alocada a uma disciplina cujo número de alunos ultrapasse a sua capacidade:
    c4 = m.addConstrs(
        x[d,s,h] * disciplinas[d].alunos <= salas[s].capacidade for d in disciplinas for s in salas for h in disciplinas[d].horarios)


    # Uma sala é alocada a uma disciplina se a sala é alocada à disciplina em algum horário:
    c5 = m.addConstrs(
        y[d,s] >= x[d,s,h] for d in disciplinas for s in salas for h in disciplinas[d].horarios)
    
    # Contagem de alocações por fase de curso
    c6 = m.addConstrs(
        z[s,f] >= x[d,s,h] for d in disciplinas for s in salas for h in disciplinas[d].horarios for f in fases if fases[f].fase == disciplinas[d].fase and fases[f].curso == disciplinas[d].curso)

    m.optimize()

    if m.status == gp.GRB.OPTIMAL:
        print("Solução ótima encontrada.")
        cria_csv_alocacoes(disciplinas,salas,horarios,x)
        exporta_alocacoes(disciplinas,salas,horarios,x)
    else:
        print("O modelo é inviável.")

main()