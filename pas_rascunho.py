from Horario import Horario
from Aula import Aula
from Sala import Sala

import gurobipy as gp
from gurobipy import GRB

# Modelo de resolução do PAS com restrições e dados de entrada do exemplo dado
# na página 18 do TCC

# OBS: Por enquanto o modelo não ta nem aí se ocorre troca de salas no meio das aulas


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
    horarios_aula4["Horário_{}".format(idx+1)]=vet_horarios[idx]

aula4 = Aula(30,horarios_aula4)
vet_aulas.append(aula4)

aulas = dict()
for idx,aula in enumerate(range(len(vet_aulas))):
    aulas["Aula_{}".format(idx+1)]=vet_aulas[idx]


# Inicializa Salas

vet_salas = [Sala(30),Sala(45),Sala(50),Sala(40)]

salas = dict()
for idx,sala in enumerate(range(len(vet_salas))):
    salas["Sala_{}".format(idx+1)]=vet_salas[idx]
    
# Criando o modelo
m = gp.Model()

# Variaveis
x = m.addVars(aulas,salas,horarios,vtype=gp.GRB.BINARY, name="x")

# Funcao obj
m.setObjective(gp.quicksum(x[a,s,h] for a in aulas for s in salas for h in aulas[a].horarios),
   sense=gp.GRB.MAXIMIZE
)

# Restricoes

# Apenas uma aula por sala por horário
c1 = m.addConstrs( 
    gp.quicksum(x[a,s,h] for a in aulas) <= 1 for s in salas for h in horarios
)

# Uma mesma aula não pode ocorrer simultaneamente em 2 salas diferentes.
c2 = m.addConstrs( 
    gp.quicksum(x[a,s,h] for s in salas ) <= 1 for a in aulas for h in horarios
)

# Restrição de capacidade
c3 = m.addConstrs(
    x[a,s,h] * aulas[a].alunos <= salas[s].capacidade for a in aulas for s in salas for h in horarios)

m.optimize()

print("Alocações")
for a in aulas:    
    for h in horarios:
        for s in salas:
            if(round(x[a,s,h].X))==1:
                print(a,h,s,(salas[s].capacidade-aulas[a].alunos))

