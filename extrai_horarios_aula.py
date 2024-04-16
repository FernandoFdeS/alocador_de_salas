import pandas as pd
import re
from classes.Disciplina import Disciplina
from classes.Fase import Fase
from classes.Horario import Horario

class ExtraiHorariosAula:
    def __init__ (self, arquivoHorarios, arquivoSalasPreferenciais):
        self.arquivoHorarios = arquivoHorarios
        self.arquivoSalasPreferenciais = arquivoSalasPreferenciais

    def cria_horarios(self):
        horarios_fixos = dict()
        for i in range(6):
            for j in range(16):
                horarios_fixos["Horario_"+(str(i+2))+"_"+(str(j+1))]=(Horario(i+2,j+1))
        return horarios_fixos
    
    def cria_fases(self):
        fases=dict()
        cursos=["ADMINISTRAÇÃO","AGRONOMIA","CIÊNCIA DA COMPUTAÇÃO","CIÊNCIAS SOCIAIS","ENFERMAGEM","ENGENHARIA AMBIENTAL E SANITÁRIA","FILOSOFIA","GEOGRAFIA","HISTÓRIA","LETRAS","MATEMÁTICA","MEDICINA","PEDAGOGIA"]
        for curso in cursos:
            for i in range(11):
                fases[curso+"_"+str(i)]=Fase(curso,i)
        return fases,cursos

    # Pega as salas preferenciais do arquivo.
    def cria_salas_preferenciais(self):        
        salas_preferenciais_dict = dict()
        dados = pd.read_excel(self.arquivoSalasPreferenciais);
        indices = dados.iloc[:, 0]
        salas_preferenciais = dados.iloc[:, 1]

        for index, salas in zip(indices,salas_preferenciais):
            salas=salas.split(",")
            for indexSala,sala in enumerate(salas):
                salas[indexSala]=sala.strip()
            salas_preferenciais_dict[index]=salas 
   

        return salas_preferenciais_dict


    def extrai_horarios_aula(self):
        dados = pd.read_excel(self.arquivoHorarios, header=None)

        nao_agrupar=["CIÊNCIA DA COMPUTAÇÃO","ENGENHARIA AMBIENTAL E SANITÁRIA"]        
        agrupamentos = dict()
        agrupados=0

        salas_preferenciais = self.cria_salas_preferenciais()
        horarios_fixos = self.cria_horarios()
        fases,cursos=self.cria_fases()

        nomes_cursos = dados.iloc[:, 0]
        horarios_disciplina = dados.iloc[:, 1]
        horarios = ""
        cod_aula= ""
        n_turma = ""
        padrao = r"(\d+)([A-Za-z]+)(\d+)"
        padrao_n_turma = r"Turma:(\d+)"
        padrao_n_fase = r'(\d+)º'
        periodo_map = dict()
        periodo_map["M"]=0
        periodo_map["T"]=6
        periodo_map["N"]=12

        disciplinas = dict()

        for nome_curso, horario_disciplina in zip(nomes_cursos,horarios_disciplina):
            vai_agrupar=0
            verifica_chave=0
            nome_ccr = horario_disciplina.split("-")
            nome_ccr = nome_ccr[1].split("(")
            nome_crr = nome_ccr[0]
            cod_aula = horario_disciplina.split("-")
            cod_aula = cod_aula[0]
            cod_aula = cod_aula[:-1]
            turma = re.search(padrao_n_turma,horario_disciplina)
            n_turma = turma.group(1)
            horarios = horario_disciplina.split("/")
            horarios = horarios[0].split("-")
            horarios = horarios[-1].split(":")
            horarios = horarios[1]
            horarios = horarios[:-3]
            todos_horarios = horarios
            todos_horarios = todos_horarios.replace(" ", "")
            horarios = horarios.split()
            horario_aula=dict()

            fusao=0
            if "FUSÃO" in nome_curso:
                fusao=1

                 
            fase_disciplina=re.findall(padrao_n_fase,horario_disciplina)
            if fase_disciplina:
                fase=fase_disciplina
            else:
                fase=[0] # optativas não tem fase, então serão colocadas como fase 0

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

                        if(nome_curso not in nao_agrupar and vai_agrupar==0 and verifica_chave==0 and fase!=[0] and fusao==0):
                            if(nome_curso=="AGRONOMIA"):
                                chave_agrupamento=cod_aula+"_"+periodo+"_"+dia
                            else:
                                chave_agrupamento=nome_curso+"_"+str(int(fase[0]))+"_"+str(todos_horarios)
                            for chave in agrupamentos:
                                fase_chave = chave.split("_")[0]+chave.split("_")[1]
                                fase_chave_agrupamento = chave_agrupamento.split("_")[0]+chave_agrupamento.split("_")[1]
                                horario_chave = chave.split("_")[2]
                                horario_chave_agrupamento = chave_agrupamento.split("_")[2]

                                if (fase_chave!=fase_chave_agrupamento):
                                    continue
                                
                                if(len(horario_chave)<len(horario_chave_agrupamento)):
                                    backup=horario_chave
                                    horario_chave=horario_chave_agrupamento
                                    horario_chave_agrupamento=backup

                                if horario_chave_agrupamento in horario_chave:
                                    vai_agrupar=1
                                    verifica_chave=1
                                    # verifica
                                    # print("Chave agrupamento: "+chave_agrupamento)
                                    # print("Chave: "+chave)
                                    chave_agrupamento=chave
                                    break
                            else:
                                agrupamentos[chave_agrupamento]=cod_aula+"_"+n_turma
                        verifica_chave=1

                        for faixa in faixas:
                            dia_horario= int(dia)
                            faixa_horario = (int(periodo_map[periodo]))+int(faixa)
                            horario_aula["Horario_{}_{}".format(dia_horario,faixa_horario)]=Horario(dia_horario,faixa_horario)
                
            sp = []
            if nome_curso in salas_preferenciais:
                sp = salas_preferenciais[nome_curso]
            if cod_aula in salas_preferenciais:
                sp = salas_preferenciais[cod_aula]


       

            disciplina = Disciplina(nome_curso,nome_crr,25,horario_aula,sp,fase,str(cod_aula+"_"+n_turma),fusao) # não tem o tamanho da turma nos horários

            if vai_agrupar==1:
                agrupados+=1

                # print("Esta disciplina: " + disciplina.cod+" | " + str(len(disciplina.horarios)))
                # print("Outra disciplina: " + agrupamentos[chave_agrupamento] + " | "+ str(len(disciplinas[agrupamentos[chave_agrupamento]].horarios)))
                # print("===")
                if((len(disciplinas[agrupamentos[chave_agrupamento]].horarios))>=len(disciplina.horarios)):
                    disciplinas[agrupamentos[chave_agrupamento]].agrupamento.append(disciplina)
                else:
                    disciplina.agrupamento.append(disciplinas[agrupamentos[chave_agrupamento]])
                    disciplinas[disciplina.cod]=disciplina
                    del(disciplinas[agrupamentos[chave_agrupamento]])

            else:
                disciplinas[cod_aula+"_"+n_turma]=disciplina
        print("Agrupamentos: ",agrupados)

        return disciplinas,horarios_fixos,fases,cursos

