from classes.Horario import Horario
from classes.Disciplina import Disciplina
from classes.Sala import Sala
from extrai_salas import ExtraiSalas
from extrai_horarios_aula import ExtraiHorariosAula
from gera_matriz_distancia import GeraMatrizDistancia
from gera_planilha_saida import GeraPlanilhaSaida
import gurobipy as gp
from gurobipy import GRB

def main():
    salas = ExtraiSalas("./dados/salas_2023_2.csv").extrai_salas()
    salasLista = list(salas.keys())
    # salas = ExtraiSalas("./dados/salas_testes.csv").extrai_salas()
    matriz_dist = GeraMatrizDistancia(salas).gera_matriz()
    disciplinas,horarios,fases,cursos = ExtraiHorariosAula("./dados/horarios.xlsx").extrai_horarios_aula()
 
    # Criando o modelo
    m = gp.Model()

    # Variaveis de ajuste de peso
    M1 = 200
    M2 = 100
    M3 = 1000
    M4 = 100
    M5 = 1

    # Variaveis
    x = {}
    for d in disciplinas:
        for h in disciplinas[d].horarios:
            for s in salas:
                x[d, s, h] = m.addVar(vtype=gp.GRB.BINARY, name=f"x[{d}, {s}, {h}]")
    y = m.addVars(disciplinas,salas,vtype=gp.GRB.INTEGER, name="y")
    z = m.addVars(salas,fases,vtype=gp.GRB.BINARY,name="z")
    w = m.addVars(salasLista,cursos,vtype=gp.GRB.BINARY,name="w")
    t = {}
    for si in salasLista:
        for sj in salasLista:
            if salasLista.index(si)<salasLista.index(sj):
                for c in cursos:
                    t[si,sj,c] = m.addVar(vtype=gp.GRB.BINARY,name=f"t[{si}, {sj}, {c}]")

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
            vet_alocacoes.append(M3*(1 - gp.quicksum(x[d,s,h] for s in salas)))

    # Funcao objetivo
    m.setObjective(gp.quicksum(y[d,s] for d in disciplinas for s in salas)*M1 +
                gp.quicksum(vet_salas_preferenciais)*M2 +
                gp.quicksum(vet_alocacoes) +
                gp.quicksum(z[s,f]for s in salas for f in fases)*M4+
                gp.quicksum(matriz_dist[salasLista.index(si)][salasLista.index(sj)] * t[si,sj,c] for si in salas for sj in salas 
                           if salasLista.index(si) < salasLista.index(sj) for c in cursos)*M5,
    sense=gp.GRB.MINIMIZE
    )

    ## == Restricoes

    # No máximo uma disciplina (turma) pode ser alocada a uma sala em um determinado horário:
    c1 = m.addConstrs(
        gp.quicksum(x[d, s, h] for d in disciplinas if h in disciplinas[d].horarios) <= 1
        for s in salas for h in horarios
    )

    # No máximo uma sala pode ser alocada a uma disciplina em um determinado horário
    c2 = m.addConstrs( 
        gp.quicksum(x[d,s,h] for s in salas ) <= 1 for d in disciplinas for h in disciplinas[d].horarios
    )

    # Uma sala não pode ser alocada a uma disciplina cujo número de alunos ultrapasse a sua capacidade:
    c4 = m.addConstrs(
        x[d,s,h] * disciplinas[d].alunos <= salas[s].capacidade for d in disciplinas for s in salas for h in disciplinas[d].horarios)


    # Uma sala é alocada a uma disciplina se a sala é alocada à disciplina em algum horário:
    c5 = m.addConstrs(
        y[d,s] >= x[d,s,h] for d in disciplinas for s in salas for h in disciplinas[d].horarios)
    
    # Contagem de alocações por fase de curso
    c6 = m.addConstrs(
         z[s,f] >= x[d,s,h] for d in disciplinas for s in salas for h in disciplinas[d].horarios for f in fases if fases[f].fase == disciplinas[d].fase and fases[f].curso == disciplinas[d].curso)
         #z[s,disciplinas[d].get_fase()] >= x[d,s,h] for d in disciplinas for s in salas for h in disciplinas[d].horarios)

    # Uma sala é alocada a um cusro se a sala é alocada à uma disciplina desse mesmo curso em algum horário.
    c7 = m.addConstrs(
        w[s,disciplinas[d].curso] >= x[d,s,h] for d in disciplinas for s in salasLista for h in disciplinas[d].horarios 
        #w[s,c] >= x[d,s,h] for d in disciplinas for s in salasLista for h in disciplinas[d].horarios for c in cursos if c == disciplinas[h].curso
    )

    c8 = m.addConstrs(
        t[si,sj,c] >= (w[si,c]+w[sj,c] - 1) for si in salasLista for sj in salasLista if salasLista.index(si) < salasLista.index(sj) for c in cursos 
    )

    m.optimize()

    if m.status == gp.GRB.OPTIMAL:
        print("Solução ótima encontrada.")
        print(M1,M2,M3,M4,M5)
        #(disciplinas,salas,horarios,x)
        # for si in salasLista:
        #     for sj in salasLista:
        #         if salasLista.index(si)<salasLista.index(sj):
        #             for c in cursos:
        #                 if( round(t[si,sj,c].X)==1):
        #                     print(c,si+"-"+sj," | Dist: "+str(matriz_dist[salasLista.index(si)][salasLista.index(sj)]))
        GeraPlanilhaSaida(disciplinas,salas,horarios,x).exporta_alocacoes()
    else:
        print("O modelo é inviável.")
        GeraPlanilhaSaida(disciplinas,salas,horarios,x).exporta_alocacoes()

main()