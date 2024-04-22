class VerificaSolucao:
    def __init__ (self, disciplinas,salas, horarios,x):
        self.disciplinas = disciplinas
        self.salas= salas
        self.horarios = horarios
        self.x = x 

    # Função para verificar se alguma disciplina usa mais de uma sala em um mesmo dia e turno (aula "quebrada" em 2 ou mais salas)
    def verifica_conflito_turno(self):
        listaAlocacoesTurno={}
        for d in self.disciplinas:
            for s in self.salas:
                    for h in self.disciplinas[d].horarios_agrupamento():
                        if(round(self.x[d,s,h].X))==1:

                            chave = d+"-"+self.horarios[h].converte_horario()

                            if chave in listaAlocacoesTurno and s not in listaAlocacoesTurno[chave]:
                                listaAlocacoesTurno[chave].append(s) 
                            elif chave not in listaAlocacoesTurno:
                                listaAlocacoesTurno[chave]=[] 
                                listaAlocacoesTurno[chave].append(s) 

        for disciplinaTurno, salas in listaAlocacoesTurno.items():
            # print(disciplinaTurno,salas)
            if len(salas) > 1:
                print("Disciplina com aula quebrada: "+disciplinaTurno)

        print("Solução verificada!")