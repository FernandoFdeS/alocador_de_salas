import pandas as pd
import numpy as np

class GeraPlanilhaSaida:
    def __init__ (self, disciplinas,salas, horarios,x):
        self.disciplinas = disciplinas
        self.salas= salas
        self.horarios = horarios
        self.x = x # a famigerada varaivel de decisao

    # Utilizado pra "debug".
    def cria_csv_alocacoes(self):
        alocacoes=[]
        #print("Disciplina  | Horário | Sala | Capacidade restante")
        for d in self.disciplinas:
            for s in self.salas:
                for h in self.disciplinas[d].horarios:
                    #print(x[d,s,h].X)
                    if(round(self.x[d,s,h].X))==1:
                        #print(d,h,s,(self.salas[s].capacidade-self.disciplinas[d].alunos))
                        alocacoes.append([self.disciplinas[d].curso,d, h, s, (self.salas[s].capacidade-self.disciplinas[d].alunos)])

        # Criar um DataFrame com as informações
        df = pd.DataFrame(alocacoes, columns=["Curso", "Disciplina", "Horario", "Sala", "Capacidade Restante"])

        # Salvar o DataFrame em um arquivo CSV
        nome_arquivo = "tabela_alocacoes.csv"
        df.to_csv(nome_arquivo, index=False)
    
    def exporta_alocacoes(self): 
        disciplinas_nao_alocadas = self.disciplinas.copy()
        disciplinas_qtd_alocacoes = dict()
        
        alocacoes=[]

        # Coluna de horarios utilizado para criação da matriz usada para geração do aqruivo final
        coluna_horarios=["SEG-M","TER-M","QUA-M","QUI-M","SEX-M","SAB-M","SEG-V","TER-V","QUA-V","QUI-V","SEX-V","SAB-V","SEG-N","TER-N","QUA-N","QUI-N","SEX-N","SAB-N"]
        
        # Coluna de horarios utilizados como header no arquivo de saída para facilitar a compreensão
        coluna_horarios_csv=[["MATUTINO","-","-","-","-","-","VESPERTINO","-","-","-","-","-","NOTURNO","-","-","-","-","-"],
                        ["SEG","TER","QUA","QUI","SEX","SAB","SEG","TER","QUA","QUI","SEX","SAB","SEG","TER","QUA","QUI","SEX","SAB"]]

        linha_salas=[]
        for s in self.salas:
            linha_salas.append(s)    

        matriz = [['-' for coluna in range(len(coluna_horarios))] for linha in range(len(linha_salas))]

        for d in self.disciplinas:
            disciplinas_qtd_alocacoes[d]=0
            for s in self.salas:
                for h in self.disciplinas[d].horarios:
                    if(round(self.x[d,s,h].X))==1:
                        disciplinas_qtd_alocacoes[d] += 1

        ## Mostra a relação entre alocações feitas/ quantidade de horarios  
        # for d in disciplinas:
        #     print(d+" "+str(disciplinas_qtd_alocacoes[d])+"/"+str(len(disciplinas[d].horarios)))

        # Preenche a matriz das alocações que sera utilizada no arquivo de saida
        for d in self.disciplinas:
            if disciplinas_qtd_alocacoes[d] != len(self.disciplinas[d].horarios):
                continue
            else:
                del disciplinas_nao_alocadas[d]
            for s in self.salas:
                for h in self.disciplinas[d].horarios:
                    if(round(self.x[d,s,h].X))==1:
                        linha = linha_salas.index(s)
                        coluna=(coluna_horarios.index(self.horarios[h].converte_horario()))
                        if(matriz[linha][coluna]=='-'):
                            matriz[linha][coluna] = self.disciplinas[d].formata_saida()
                        elif (self.disciplinas[d].formata_saida() not in matriz[linha][coluna]):
                            matriz[linha][coluna] = matriz[linha][coluna] +" | "+self.disciplinas[d].formata_saida()
        
        # Gera vetor de disciplinas não alocadas para ser usado no arquivo de saida
        vet_nao_alocadas=[]
        for d in disciplinas_nao_alocadas:
            vet_nao_alocadas.append(self.disciplinas[d].formata_saida())
        qtdNaoAlocadas=("Não Alocadas ("+str(len(disciplinas_nao_alocadas))+")") 
        
        
        # Cria um DataFrame com rótulos personalizados
        while(len(vet_nao_alocadas)<len(self.salas)):
            vet_nao_alocadas.append("-")
        indexes = pd.MultiIndex.from_arrays([vet_nao_alocadas,self.salas],names=[qtdNaoAlocadas,'Salas'])
        df = pd.DataFrame(matriz, columns=coluna_horarios_csv, index=indexes)
        nome_arquivo = "planilha_alocacoes.csv"
        df.to_csv(nome_arquivo, index=True)

        # Verifica se todas as disciplinas foram alocadas
        if(len(disciplinas_nao_alocadas))==0:
            print("Alocações realizadas com sucesso!")
        else:
            print("Disciplinas alocadas: "+str((len(self.disciplinas)-len(disciplinas_nao_alocadas)))+"/"+str(len(self.disciplinas)))

