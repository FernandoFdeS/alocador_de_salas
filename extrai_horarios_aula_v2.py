import pandas as pd
import re
from classes.Disciplina import Disciplina
from classes.Fase import Fase
from classes.Horario import Horario
from datetime import datetime

class ExtraiHorariosAulaV2:
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
        cursos=["ADM","AGRO","CC","CS","ENF","EAS","FIL","GEO","HIS","LET","MAT","MED","PED"]
        for curso in cursos:
            for i in range(11):
                fases[(curso+"_"+str(i))]=Fase(curso,i)
        fases[(curso+"_"+str(12))]=Fase("MEDICINA",int(12))
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
    
    def parse_periodo_duraca(self, periodo_duracao):
        periodo_duracao = periodo_duracao.strip('()')
        start_date_str, end_date_str = periodo_duracao.split(' - ')
        start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
        end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
        return start_date, end_date

    def verfica_sobreposicao(self, periodo_duracao1, periodo_duracao2):
        start1, end1 = self.parse_periodo_duraca(periodo_duracao1)
        start2, end2 = self.parse_periodo_duraca(periodo_duracao2)
        return start1 <= end2 and start2 <= end1

    def tem_alguma_sobreposicao(self, dict_datas1, dict_datas2):
        dict_datas1=dict_datas1[0]
        dict_datas2=dict_datas2[0]
        for chave1,valor1 in dict_datas1.items():
            for chave2,valor2 in dict_datas2.items():
                for faixa1 in valor1:
                    for faixa2 in valor2:
                        if ((faixa1 in faixa2) or (faixa2  in faixa1)):
                            if self.verfica_sobreposicao(chave1, chave2):
                                #Debug
                                print()
                                print("overlap")
                                print(chave1,valor1)
                                print(chave2,valor2)
                                return True
        return False


    def extrai_horarios_aula(self):
        salas_preferenciais = self.cria_salas_preferenciais()
        horarios_fixos = self.cria_horarios()
        fases,todos_cursos=self.cria_fases()

        disciplinas = dict()

        # TODO Receber como entrada um dado que indique se as disciplinas de
        # um curso podem ser agrupadas ou nao. Isto deve depender da logica de
        # agrupamento se aplicar ou nao as disciplinas do curso
        cursos_nao_agrupar=["ENGENHARIA AMBIENTAL E SANITÁRIA"]
        # TODO Receber como entrada um dado que indique se determinadas
        # disciplinas podem ser agrupadas ou nao. Isto deve depender da logica
        # de agrupamento se aplicar ou nao a estas disciplinas
        codigos_nao_agrupar=[]
        agrupamentos = dict()
        agrupados=0

        padrao_horario = r"(\d+)([A-Za-z]+)(\d+)"
        padrao_periodo_duracao = r'\(\d{2}/\d{2}/\d{4} - \d{2}/\d{2}/\d{4}\)'
        padrao_horarios_aula = r'\d+[A-Z]\d+'
        periodo_map = dict()
        periodo_map["M"]=0
        periodo_map["T"]=6
        periodo_map["N"]=12
        controleTurmas=dict()
        # TODO Tratar o caso em que os dados de entrada nao contem a coluna 'vagas'
        dados = pd.read_excel(self.arquivoHorarios, usecols=['cod','ch_ccr','curso', 'fase', 'horario', 'vagas', 'nome_ccr'])

        for indice, linha in dados.iterrows():
            
            codigo = linha['cod']

            # Nos nao vem o numero das turmas
            # Entao vamos criar um controle artificial para definir o numero das turmas
            # De uma mesma disciplina.
            if(codigo in controleTurmas):
                controleTurmas[codigo]= controleTurmas[codigo]+1
            else:
                controleTurmas[codigo]=1

            # Pegamos apenas o primeiro valor da fase
            fase = linha['fase']
            fase=str(fase).split(";")

            # Pegamos o numero de alunos da turma
            alunos = linha['vagas']
            nome_ccr = linha['nome_ccr']
            ch_ccr = linha['ch_ccr']
            horario_string = linha['horario']

            # Tratando os cursos para verificar se eh uma fusao ou nao
            fusao=0
            cursos = linha['curso']
            cursos=cursos.split(";")
            nome_curso=''
            if(len(cursos)>=2):
                fusao=1
                nome_curso = "FUSAO : "
                for index,curso in enumerate(cursos): 
                    if(index==0):
                        nome_curso=nome_curso+curso
                    else:
                        nome_curso=nome_curso+" + "+curso
            else:
                nome_curso=cursos[0]

            # Extraindo os horarios e transformando em um vetor 
            # com os diferentes horarios que a disciplina tem
            horarios = linha['horario']
            horarios = horarios.split(",")
            todos_horarios_aula=[]
            periodo_duracao=dict()
            for horario in horarios:
                horario=horario.strip()
                horarios_splitado=re.findall(r'\S+', horario)
                # Pegando os periodos (em dias) em que as aulas ocorrem (Ex: 08/07/2024 -  19/10/2024) -> periodoDuracao
                # Como temos que comprar somente as sobreposições de periodos que acontecem no mesmo momento da semana, vamos armazenar a faixa de horarios da discplina também
                # ...
                periodos_duracao=re.findall(padrao_periodo_duracao,horario)
                horarios_periodo=re.findall(padrao_horarios_aula,horario)
                #Exemplo: Chave -> (12/04/2024 - 14/05/2024) | Valor -> ["4T345","6V1234"] (faixas do periodo de duração)
                periodo_duracao[(periodos_duracao[0])]=horarios_periodo
                #periodo_duracao[(periodos_duracao[0])]="".join(horarios_periodo)

                for horario_splitado in horarios_splitado:                    
                    if not horario_splitado[0].isdigit():
                        break
                   
                    if (horario_splitado not in todos_horarios_aula):   
                        todos_horarios_aula.append(horario_splitado)
            
            # Criando os objetos referentes aos horarios das disciplinas
            string_todos_horarios_aula="".join(todos_horarios_aula)
            horario_aula=dict()
            
            for horario in todos_horarios_aula:
                dias=""
                periodo=""
                faixas=""
                resultado = re.match(padrao_horario,horario)
                dias=resultado.group(1)
                periodos=resultado.group(2)
                faixas=resultado.group(3)
                for dia in dias:
                    for periodo in periodos:
                        for faixa in faixas:
                            dia_horario= int(dia)
                            faixa_horario = (int(periodo_map[periodo]))+int(faixa)
                            horario_aula["Horario_{}_{}".format(dia_horario,faixa_horario)]=Horario(dia_horario,faixa_horario)
            
            
            # Pegando as salas preferenciais da disciplina/turma
            sp = []
            if  cursos[0] in salas_preferenciais:
                    sp = salas_preferenciais[cursos[0]]
            if  codigo in salas_preferenciais:
                    sp = salas_preferenciais[codigo]

            # Criando objeto da disciplina
            disciplina = Disciplina(nome_curso,nome_ccr,ch_ccr,alunos,horario_aula,horario_string,periodo_duracao,sp,fase,str(codigo+"_"+str(controleTurmas[codigo])),fusao)
 
            # Agrupamento
            verifica_chave=0
            vai_agrupar=0
            if(nome_curso not in cursos_nao_agrupar and codigo not in codigos_nao_agrupar and vai_agrupar==0 and verifica_chave==0 and int(fase[0])!=0 and fusao==0):
                if(nome_curso=="AGRONOMIA"):
                    chave_agrupamento=codigo+"_"+periodo+"_"+dia
                else:
                    chave_agrupamento=nome_curso+"_"+str(int(fase[0]))+"_"+str(string_todos_horarios_aula)

                for chave in agrupamentos:
                    if (agrupamentos[chave].split("_")[0] in codigos_nao_agrupar):
                        continue

                    fase_chave = chave.split("_")[0]+chave.split("_")[1]
                    fase_chave_agrupamento = chave_agrupamento.split("_")[0]+chave_agrupamento.split("_")[1]
                    horario_chave = chave.split("_")[2]
                    horario_chave_agrupamento = chave_agrupamento.split("_")[2]

                    if (fase_chave!=fase_chave_agrupamento):
                        continue

                    for horario in todos_horarios_aula:
                        if horario in horario_chave:
                            if(not self.tem_alguma_sobreposicao(disciplina.periodoDuracao,disciplinas[agrupamentos[chave]].periodoDuracao)):
                                #para debug
                                print("Agrupamento Rolou!")
                                vai_agrupar=1
                                verifica_chave=1
                                chave_agrupamento=chave
                                break
                            #para debug
                            else:
                                print(disciplina.curso,disciplina.cod,disciplinas[agrupamentos[chave]].cod)
                    if vai_agrupar==1 and verifica_chave ==1:
                        break                

            if(vai_agrupar==0):
                chave_agrupamento=nome_curso+"_"+str(int(fase[0]))+"_"+str(string_todos_horarios_aula)
                agrupamentos[chave_agrupamento]=codigo+"_"+str(controleTurmas[codigo])
            verifica_chave=1

            if vai_agrupar==1:
                agrupados+=1
                print("Curso: ",disciplina.nome_completo_curso)
                print("Esta disciplina: " + disciplina.cod+" | " + str(len(disciplina.horarios)) + " | " + str(disciplina.alunos))
                print("Outra disciplina: " + agrupamentos[chave_agrupamento] + " | "+ str(len(disciplinas[agrupamentos[chave_agrupamento]].horarios)) + " | " + str(disciplinas[agrupamentos[chave_agrupamento]].alunos))
                
                if((len(disciplinas[agrupamentos[chave_agrupamento]].horarios))>=len(disciplina.horarios)):
                    disciplinas[agrupamentos[chave_agrupamento]].agrupamento.append(disciplina)
                    print("Agrupamento: " + disciplinas[agrupamentos[chave_agrupamento]].cod + " | " + str(len(disciplinas[agrupamentos[chave_agrupamento]].horarios_agrupamento())) + " | " + str(disciplinas[agrupamentos[chave_agrupamento]].max_alunos_agrupamento()))
                else:
                    disciplina.agrupamento.append(disciplinas[agrupamentos[chave_agrupamento]])
                    disciplinas[disciplina.cod]=disciplina
                    del(disciplinas[agrupamentos[chave_agrupamento]])
                    print("Agrupamento: " + disciplinas[disciplina.cod].cod + " | " + str(len(disciplinas[disciplina.cod].horarios_agrupamento())) + " | " + str(disciplinas[disciplina.cod].max_alunos_agrupamento()))
                print("===")

            else:
                disciplinas[codigo+"_"+str(controleTurmas[codigo])]=disciplina
  
        # print(horario,horario_aula[horario].dia,horario_aula[horario].faixa)  # disciplina = Disciplina(nome_curso,alunos,horario_aula,sp,fase,str(cod_aula+"_"+nome_curso),fusao)
       
        print("Agrupamentos: ",agrupados)
        return disciplinas,horarios_fixos,fases,todos_cursos
       

