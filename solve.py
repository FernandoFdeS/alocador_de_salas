from classes.Horario import Horario
from classes.Disciplina import Disciplina
from classes.Sala import Sala
from extrai_salas import ExtraiSalas
from extrai_horarios_aula import ExtraiHorariosAula
from gera_matriz_distancia import GeraMatrizDistancia
from gera_planilha_saida import GeraPlanilhaSaida
import gurobipy as gp
from gurobipy import GRB

def main(arquivo_horarios,arquivo_salas,arquivo_salas_preferenciais):
    print(arquivo_salas)
    salas = ExtraiSalas(arquivo_salas).extrai_salas()
    salasLista = list(salas.keys())
    # salas = ExtraiSalas("./dados/salas_testes.csv").extrai_salas()
    matriz_dist = GeraMatrizDistancia(salas).gera_matriz()
    disciplinas,horarios,fases,cursos = ExtraiHorariosAula(arquivo_horarios,arquivo_salas_preferenciais).extrai_horarios_aula()
 
    # Criando o modelo
    m = gp.Model()

    print(len(disciplinas))

    # Variaveis de ajuste de peso
    M1 = 250
    M2 = 150
    M3 = 2000
    M4 = 5
    M5 = 0.5

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

    # v = m.addVars(salasLista,fases,vtype=gp.GRB.BINARY,name="v")
    # u = {}
    # for si in salasLista:
    #     for sj in salasLista:
    #         if salasLista.index(si)<salasLista.index(sj):
    #             for f in fases:
    #                 u[si,sj,f] = m.addVar(vtype=gp.GRB.BINARY,name=f"u[{si}, {sj}, {f}]")

    # Cria vetor de variaveis das salas preferenciais
    vet_salas_preferenciais=[]

    for d in disciplinas:
        for h in disciplinas[d].horarios:
            for s in salas:
                if s not in disciplinas[d].salasPreferenciais:
                    #print(s+" não é sala preferencial")
                    vet_salas_preferenciais.append(x[d,s,h])
    
    # Cria vetor das alocacoes das salas
    vet_alocacoes=[]
    for d in disciplinas:
        for h in disciplinas[d].horarios:
            vet_alocacoes.append((1 - gp.quicksum(x[d,s,h] for s in salas)))

    # Funcao objetivo
    m.setObjective(gp.quicksum(y[d,s] for d in disciplinas for s in salas)*M1 +
                gp.quicksum(vet_salas_preferenciais)*M2 +
                gp.quicksum(vet_alocacoes)*M3 +
                # gp.quicksum(matriz_dist[salasLista.index(si)][salasLista.index(sj)] * u[si,sj,f] for si in salas for sj in salas 
                #     if salasLista.index(si) < salasLista.index(sj) for f in fases)*M4+
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
    
    # # # Contagem de alocações por fase de curso
    # # c6 = m.addConstrs(
    # #      z[s,f] >= x[d,s,h] for d in disciplinas for s in salas for h in disciplinas[d].horarios for f in fases if fases[f].fase == disciplinas[d].fase and fases[f].curso == disciplinas[d].curso)


    # Uma sala é alocada a um cusro se a sala é alocada à uma disciplina desse mesmo curso em algum horário.
    c7 = m.addConstrs(
        w[s,disciplinas[d].curso] >= x[d,s,h] for d in disciplinas for s in salasLista for h in disciplinas[d].horarios 
        #w[s,c] >= x[d,s,h] for d in disciplinas for s in salasLista for h in disciplinas[d].horarios for c in cursos if c == disciplinas[d].curso
    )

    c8 = m.addConstrs(
        t[si,sj,c] >= (w[si,c]+w[sj,c] - 1) for si in salasLista for sj in salasLista if salasLista.index(si) < salasLista.index(sj) for c in cursos 
    )

    # c9 = m.addConstrs(
    #     v[s,f] >= x[d,s,h] for d in disciplinas for s in salasLista for h in disciplinas[d].horarios for f in fases if fases[f].fase == disciplinas[d].fase and fases[f].curso == disciplinas[d].curso
    # )

    # c10 = m.addConstrs(
    #     u[si,sj,f] >= (v[si,f]+v[sj,f] - 1) for si in salasLista for sj in salasLista if salasLista.index(si) < salasLista.index(sj) for f in fases 
    # )

    m.optimize()

    if m.status == gp.GRB.OPTIMAL:
        print("Solução ótima encontrada.")       
      
        # GeraPlanilhaSaida(disciplinas,salas,horarios,x).exporta_alocacoes()
    else:
        print("Solução -> não <- ótima.")

    # print(M1,M2,M3,M4,M5)
    # for c in cursos:
    #     for si in salasLista:
    #         for sj in salasLista:
    #             if salasLista.index(si)<salasLista.index(sj):                
    #                 if(round(t[si,sj,c].X)==1):
    #                     print(c,si+"-"+sj," | Dist: "+str(matriz_dist[salasLista.index(si)][salasLista.index(sj)]))
    
    # for d in disciplinas:
    #     for h in disciplinas[d].horarios:
    #         for s in disciplinas[d].salasPreferenciais:
    #                 if(x[d,s,h].X == 1):
    #                     print("Alocação em sala preferencial: "+d,s,h)


    GeraPlanilhaSaida(disciplinas,salas,horarios,x,"./web/static/dados/","planilha_alocacoes.xlsx").exporta_alocacoes()

