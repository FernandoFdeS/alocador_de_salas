from classes.Horario import Horario
from classes.Disciplina import Disciplina
from classes.Sala import Sala
from extrai_salas import ExtraiSalas
from extrai_horarios_aula import ExtraiHorariosAula
from gera_matriz_distancia import GeraMatrizDistancia
from gera_planilha_saida import GeraPlanilhaSaida
from verifica_solucao import VerificaSolucao
import gurobipy as gp
from gurobipy import GRB

def main(arquivo_horarios,arquivo_salas,arquivo_salas_preferenciais):
    salas = ExtraiSalas(arquivo_salas).extrai_salas()
    salasLista = list(salas.keys())
    matriz_dist = GeraMatrizDistancia(salas).gera_matriz()
    disciplinas,horarios,fases,cursos = ExtraiHorariosAula(arquivo_horarios,arquivo_salas_preferenciais).extrai_horarios_aula()
 
    # Criando o modelo
    m = gp.Model()

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
    w = m.addVars(salasLista,cursos,vtype=gp.GRB.BINARY,name="w")
    t = {}
    for si in salasLista:
        for sj in salasLista:
            if salasLista.index(si)<salasLista.index(sj):
                for c in cursos:
                    t[si,sj,c] = m.addVar(vtype=gp.GRB.BINARY,name=f"t[{si}, {sj}, {c}]")

    z = m.addVars(salasLista,fases,vtype=gp.GRB.BINARY,name="v")
    v = {}
    for si in salasLista:
        for sj in salasLista:
            if salasLista.index(si)<salasLista.index(sj):
                for f in fases:
                    v[si,sj,f] = m.addVar(vtype=gp.GRB.BINARY,name=f"v[{si}, {sj}, {f}]")

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
            vet_alocacoes.append((1 - gp.quicksum(x[d,s,h] for s in salas)))

    # Funcao objetivo
    m.setObjective(gp.quicksum(y[d,s] for d in disciplinas for s in salas)*M1 +
                gp.quicksum(vet_salas_preferenciais)*M2 +
                gp.quicksum(vet_alocacoes)*M3 +
                gp.quicksum(matriz_dist[salasLista.index(si)][salasLista.index(sj)] * v[si,sj,f] for si in salas for sj in salas 
                     if salasLista.index(si) < salasLista.index(sj) for f in fases)*M4+
                gp.quicksum(z[s,f]for s in salas for f in fases)*M4+
                gp.quicksum(matriz_dist[salasLista.index(si)][salasLista.index(sj)] * t[si,sj,c] for si in salas for sj in salas 
                           if salasLista.index(si) < salasLista.index(sj) for c in cursos)*M5,
    sense=gp.GRB.MINIMIZE
    )

    ## == Restricoes

    # No máximo uma disciplina (turma) pode ser alocada a uma sala em um determinado horário:
    c1 = m.addConstrs(
        gp.quicksum(x[d, s, h] for d in disciplinas if h in disciplinas[d].horarios_agrupamento()) <= 1
        for s in salas for h in horarios
    )

    # No máximo uma sala pode ser alocada a uma disciplina em um determinado horário
    c2 = m.addConstrs( 
        gp.quicksum(x[d,s,h] for s in salas ) <= 1 for d in disciplinas for h in disciplinas[d].horarios_agrupamento()
    )

    # TODO Melhorar o tratamento dos dados de uma disciplina considerando que
    # ela pode ser um agrupamento (ex.: uso dos metodos max_alunos_agrupamento
    # e horarios_agrupamento)
    # Uma sala não pode ser alocada a uma disciplina cujo número de alunos ultrapasse a sua capacidade:
    c3 = m.addConstrs(
        x[d,s,h] * disciplinas[d].max_alunos_agrupamento() <= salas[s].capacidade for d in disciplinas for s in salas for h in disciplinas[d].horarios_agrupamento())


    # Uma sala é alocada a uma disciplina se a sala é alocada à disciplina em algum horário:
    c4 = m.addConstrs(
        y[d,s] >= x[d,s,h] for d in disciplinas for s in salas for h in disciplinas[d].horarios_agrupamento())
    

    # Uma sala é aloacada a uma fase (e curso) se a sala é aloaca à uma disciplina dessa mesma fase em algum horário
    c5 = m.addConstrs(
        z[s,f] >= x[d,s,h] for d in disciplinas for s in salasLista for h in disciplinas[d].horarios_agrupamento() for f in fases if fases[f].fase == disciplinas[d].fase and fases[f].curso == disciplinas[d].curso
    )

    # Indica as duplas de salas aloacadas para uma mesma fase que serão usadas no somatório de distância de salas alocadas a determinada fase
    c6 = m.addConstrs(
        v[si,sj,f] >= (z[si,f]+z[sj,f] - 1) for si in salasLista for sj in salasLista if salasLista.index(si) < salasLista.index(sj) for f in fases 
    )

    # Uma sala é alocada a um curso se a sala é alocada à uma disciplina desse mesmo curso em algum horário.
    c7 = m.addConstrs(
        w[s,disciplinas[d].curso] >= x[d,s,h] for d in disciplinas for s in salasLista for h in disciplinas[d].horarios_agrupamento()
    )

    # Indica as duplas de salas alocadas para um mesmo curso  que serão usadas no somatório de distância de salas alocadas a determinado curso
    c8 = m.addConstrs(
        t[si,sj,c] >= (w[si,c]+w[sj,c] - 1) for si in salasLista for sj in salasLista if salasLista.index(si) < salasLista.index(sj) for c in cursos 
    )
    
    m.setParam('VarsName', 1)
    m.setParam(GRB.Param.TimeLimit, 25200) # Tempo limite de 7 horas
    m.optimize()

    # # Para salvar valores da solução
    # m.write("solution.sol")

    # # Para utilizar solução salva :
    # m.Params.MIPGap = 0.05
    # m.update()
    # m.read("solution.sol")
    # m.optimize()

    if m.status == gp.GRB.OPTIMAL:
        print("Solução ótima encontrada.")       
    else:
        print("Solução -> não <- ótima.")


    conflitos = VerificaSolucao(disciplinas,salas,horarios,x).verifica_conflito_turno()

    GeraPlanilhaSaida(disciplinas,salas,horarios,x,"./web/static/dados/","planilha_alocacoes.xlsx").cria_tabela_alocacoes(conflitos)
    GeraPlanilhaSaida(disciplinas,salas,horarios,x,"./web/static/dados/","planilha_alocacoes.xlsx").exporta_alocacoes()

