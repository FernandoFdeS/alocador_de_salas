import pandas as pd
import re
from classes.Disciplina import Disciplina
from classes.Fase import Fase
from classes.Horario import Horario

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
        cursos=["ADMINISTRAÇÃO","AGRONOMIA","CIÊNCIA DA COMPUTAÇÃO","CIÊNCIAS SOCIAIS","ENFERMAGEM","ENGENHARIA AMBIENTAL E SANITÁRIA","FILOSOFIA","GEOGRAFIA","HISTÓRIA","LETRAS","MATEMÁTICA","MEDICINA","PEDAGOGIA"]
        for curso in cursos:
            for i in range(11):
                fases[curso+"_"+str(i)]=Fase(curso,i)
        fases[curso+"_"+str(12)]=Fase("MEDICINA",int(12))
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
        salas_preferenciais = self.cria_salas_preferenciais()
        horarios_fixos = self.cria_horarios()
        fases,todos_cursos=self.cria_fases()

        disciplinas = dict()

        # TODO Receber como entrada um dado que indique se as disciplinas de
        # um curso podem ser agrupadas ou nao. Isto deve depender da logica de
        # agrupamento se aplicar ou nao as disciplinas do curso
        cursos_nao_agrupar=["CIÊNCIA DA COMPUTAÇÃO","ENGENHARIA AMBIENTAL E SANITÁRIA","ENFERMAGEM"]
        # TODO Receber como entrada um dado que indique se determinadas
        # disciplinas podem ser agrupadas ou nao. Isto deve depender da logica
        # de agrupamento se aplicar ou nao a estas disciplinas
        codigos_nao_agrupar=["GLA356","GLA357","GLA363"]
        agrupamentos = dict()
        agrupados=0

        padrao_horario = r"(\d+)([A-Za-z]+)(\d+)"
        periodo_map = dict()
        periodo_map["M"]=0
        periodo_map["T"]=6
        periodo_map["N"]=12
        controleTurmas=dict()
        # TODO Tratar o caso em que os dados de entrada nao contem a coluna 'vagas'
        dados = pd.read_excel(self.arquivoHorarios, usecols=['cod', 'curso', 'fase', 'horario', 'vagas'])

        for indice, linha in dados.iterrows():
            
            codigo = linha['cod']

            # Nos arquivos dos semestres de 2023.1 pra tras nao vem o numero das turmas
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
            for horario in horarios:
                horario=horario.strip()
                #h =  horario.split(" ")[0]
                horarios_splitado=re.findall(r'\S+', horario)
                for horario_splitado in horarios_splitado:
                    if not horario_splitado[0].isdigit():
                        break
                    if (horario_splitado not in todos_horarios_aula):   
                        todos_horarios_aula.append(horario_splitado)
            
            # Agora sim, criando os objetos referentes aos horarios das disciplinas
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
            
            # Lidando com o agrupamento de disciplinas
            # (Nao vou explicar como funciona pq nem eu sei)

            verifica_chave=0
            vai_agrupar=0
            # print(codigo+"_"+periodo+"_"+dia)
            # print(fase[0])
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
                    
                    # if(len(horario_chave)<len(horario_chave_agrupamento)):
                    #     backup=horario_chave
                    #     horario_chave=horario_chave_agrupamento
                    #     horario_chave_agrupamento=backup
                    for horario in todos_horarios_aula:
                        if horario in horario_chave:
                            vai_agrupar=1
                            verifica_chave=1
                            chave_agrupamento=chave
                            break
                    if vai_agrupar==1 and verifica_chave ==1:
                        break
                
                else:
                    agrupamentos[chave_agrupamento]=codigo+"_"+str(controleTurmas[codigo])
            if(vai_agrupar==0):
                chave_agrupamento=nome_curso+"_"+str(int(fase[0]))+"_"+str(string_todos_horarios_aula)
                agrupamentos[chave_agrupamento]=codigo+"_"+str(controleTurmas[codigo])
            verifica_chave=1

            # Pegando as salas preferenciais da disciplina/turma
            sp = []
            if  cursos[0] in salas_preferenciais:
                    sp = salas_preferenciais[cursos[0]]
            if  codigo in salas_preferenciais:
                    sp = salas_preferenciais[codigo]

            # Criando objeto da disciplina
            disciplina = Disciplina(nome_curso,alunos,horario_aula,sp,fase,str(codigo+"_"+str(controleTurmas[codigo])),fusao)

            if vai_agrupar==1:
                agrupados+=1

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
  

            

            # print(f'Código: {codigo,controleTurmas[codigo]}, Curso: {nome_curso}, Fase: {fase}, Núm. de alunos: {alunos}, Horário: {todos_horarios_aula}')
            # print(string_todos_horarios_aula)
            # for horario in horario_aula:
            #     print(horario,horario_aula[horario].dia,horario_aula[horario].faixa)  # disciplina = Disciplina(nome_curso,alunos,horario_aula,sp,fase,str(cod_aula+"_"+nome_curso),fusao)
       
        print("Agrupamentos: ",agrupados)
        return disciplinas,horarios_fixos,fases,todos_cursos
       

