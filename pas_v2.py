from Horario import Horario
from Aula import Aula
from Sala import Sala

import gurobipy as gp
from gurobipy import GRB


# Modelo de resolução do PAS com restrições e dados de entrada do exemplo dado
# na página 18 do TCC

# Inicializa horarios

vet_horarios=[]
for i in range(1):
    for j in range(6):
        vet_horarios.append(Horario(i+1,j+1))

horarios = dict()
for idx,horario in enumerate(range(len(vet_horarios))):
    horarios["Horário_{}".format(idx+1)]=vet_horarios[idx]

# Inicializa Aulas

vet_aulas=[]

horarios_aula1 = dict()
for idx,horario in enumerate(range(6)):
    horarios_aula1["Horário_{}".format(idx+1)]=vet_horarios[idx]

aula1 = Aula(40,horarios_aula1)
vet_aulas.append(aula1)

horarios_aula2 = dict()
for idx,horario in enumerate(range(6)):
    horarios_aula2["Horário_{}".format(idx+1)]=vet_horarios[idx]

aula2 = Aula(45,horarios_aula2)
vet_aulas.append(aula2)

horarios_aula3 = dict()
for idx,horario in enumerate(range(4)):
    horarios_aula3["Horário_{}".format(idx+1)]=vet_horarios[idx]

aula3 = Aula(30,horarios_aula3)
vet_aulas.append(aula3)

horarios_aula4 = dict()
for idx,horario in enumerate(range(4,6)):
    horarios_aula4["Horário_{}".format(idx+5)]=vet_horarios[idx]

aula4 = Aula(30,horarios_aula4)
vet_aulas.append(aula4)

disciplinas = dict()
for idx,aula in enumerate(range(len(vet_aulas))):
    disciplinas["Disciplina_{}".format(idx+1)]=vet_aulas[idx]

# Inicializa Salas

vet_salas = [Sala(30),Sala(45),Sala(50),Sala(40)]

salas = dict()
for idx,sala in enumerate(range(len(vet_salas))):
    salas["Sala_{}".format(idx+1)]=vet_salas[idx]

# Criando o modelo
m = gp.Model()

# Variaveis
x = {}
for d in disciplinas:
    for h in disciplinas[d].horarios:
        for s in salas:
            x[d, s, h] = m.addVar(vtype=gp.GRB.BINARY, name=f"x[{d}, {s}, {h}]")

y = m.addVars(disciplinas,salas,vtype=gp.GRB.INTEGER, name="y")

# Funcao obj
m.setObjective(gp.quicksum(y[d,s] for d in disciplinas for s in salas),
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

print("Alocações")
print("Disciplina  | Horário | Sala | Capacidade restante")
for d in disciplinas:
    for s in salas:
        for h in disciplinas[d].horarios:
            #print(x[d,s,h].X)
            if(round(x[d,s,h].X))==1:
                print(d,h,s,(salas[s].capacidade-disciplinas[d].alunos))