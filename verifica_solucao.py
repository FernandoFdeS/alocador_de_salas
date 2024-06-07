class VerificaSolucao:
    def __init__ (self, disciplinas,salas, horarios,x):
        self.disciplinas = disciplinas
        self.salas= salas
        self.horarios = horarios
        self.x = x 

    def verifica_repeticao(self, blocoHorarios):
        horarios = []

        # Pegando apenas os horários
        for item in blocoHorarios:
            indice_hifen = item.find('-')            
            horario = item[indice_hifen+1:]
            horarios.append(horario)

        # Verifica se há repetição em pelo menos um caractere entre todos as faixas de horario
        for i in range(len(horarios)):
            for j in range(i+1, len(horarios)):
                for char in horarios[i]:
                    if char in horarios[j]:
                        return True
        
        return False

    # Função para verificar se uma sala aloca duas disciplinas no mesmo dia/turno com horários que se sobrepõe
    def verifica_conflito_turno(self):
        # Chave = sala-turno. Ex: 201-A-SEG-V.
        # Valor = cod_disciplina-faixas. Ex: GEX201_2-56.
        # Indicando que, na Sala 201, na Segunda-feira de tarde, a disciplina GEX201 tem aula nas faixas de horário 5 e 6. 
        listaAlocacoesTurno={}
        conflitos=[]
        for d in self.disciplinas:
            for s in self.salas:
                for h_alocacao in self.disciplinas[d].horarios_agrupamento():
                    if(round(self.x[d,s,h_alocacao].X))==1:

                        stringFaixasHorario=''
                        valor=''
                        #Pegando todos os horários da disciplina com o mesmo dia e turno do horário em que ela foi alocada 
                        for horario in self.disciplinas[d].horarios_agrupamento():
                            if (self.horarios[horario].get_periodo() == self.horarios[h_alocacao].get_periodo() and
                            self.horarios[horario].dia == self.horarios[h_alocacao].dia):
                                stringFaixasHorario = stringFaixasHorario + str(self.horarios[horario].get_faixa_convertida())

                        chave = s+"-"+self.horarios[h_alocacao].converte_horario()
                        valor = d+"-"+stringFaixasHorario

                        if chave in listaAlocacoesTurno and valor not in listaAlocacoesTurno[chave]:
                            listaAlocacoesTurno[chave].append(valor) 
                        elif chave not in listaAlocacoesTurno:
                            listaAlocacoesTurno[chave]=[] 
                            listaAlocacoesTurno[chave].append(valor) 

        # Percorre a lista das alocações feitas e verifica se, em salas/turnos
        # com mais de uma alocação os horários alocadas de sobrepõe (conflitam)
        for salaTurno,blocoHorarios in listaAlocacoesTurno.items():
            if(len(blocoHorarios)>1):
                if(self.verifica_repeticao(blocoHorarios)):
                    conflitos.append([salaTurno,blocoHorarios])
                    print("Atenção!")
                    print("Conflito identificado nas alocações da SALA-TURNO:  ",salaTurno)
                    print("DISCIPLINA-FAIXA_HORARIO conflitantes:  ",blocoHorarios)
                    print("Não esqueça de verificar se as disciplinas envolvidas no conflito tem agrupamentos.")
                    print()

        print("Solução verificada.")
        return conflitos