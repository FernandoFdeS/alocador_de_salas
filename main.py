from Horario import Horario
from Disciplina import Disciplina
from Sala import Sala
import extrai_horarios_aula as h_a
import extrai_salas as s
import pandas as pd
import gurobipy as gp
from gurobipy import GRB

disciplinas = h_a.disciplinas
horarios = h_a.horarios_fixos
salas = s.salas
# Criando o modelo
m = gp.Model()
m.setParam('TimeLimit',300)

# Variaveis
x = {}
for d in disciplinas:
    for h in disciplinas[d].horarios:
        for s in salas:
            x[d, s, h] = m.addVar(vtype=gp.GRB.BINARY, name=f"x[{d}, {s}, {h}]")
y = m.addVars(disciplinas,salas,vtype=gp.GRB.INTEGER, name="y")


# Descomenta daqui pra baixo --------------

vet_salas_preferenciais=[]

for d in disciplinas:
    for h in disciplinas[d].horarios:
        for s in salas:
            if s not in disciplinas[d].salasPreferenciais:
                vet_salas_preferenciais.append(x[d,s,h])

# Funcao obj
m.setObjective(gp.quicksum(y[d,s] for d in disciplinas for s in salas) +
               gp.quicksum(vet_salas_preferenciais),
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

# No mínimo uma sala deve ser alocada a uma disciplina em um determinado horário
c3 = m.addConstrs( 
    gp.quicksum(x[d,s,h] for s in salas ) >= 1 for d in disciplinas for h in disciplinas[d].horarios
)

# Uma sala não pode ser alocada a uma disciplina cujo número de alunos ultrapasse a sua capacidade:
c4 = m.addConstrs(
    x[d,s,h] * disciplinas[d].alunos <= salas[s].capacidade for d in disciplinas for s in salas for h in disciplinas[d].horarios)


# Uma sala é alocada a uma disciplina se a sala é alocada à disciplina em algum horário:
c5 = m.addConstrs(
    y[d,s] >= x[d,s,h] for d in disciplinas for s in salas for h in disciplinas[d].horarios)

m.optimize()

alocacoes=[]

if m.status == gp.GRB.OPTIMAL:
    print("Solução ótima encontrada.")
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
    print("Alocações realizadas com sucesso!")
else:
    print("O modelo é inviável.")