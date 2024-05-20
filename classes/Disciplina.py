from classes.Horario import Horario
import re

class Disciplina:
    def __init__(self,curso,nome_ccr,ch_ccr,alunos,horarios,horarioString,periodoDuracao,salasPreferenciais,fase,cod,fusao):
        self.curso = self.abreviacao(curso)
        self.nome_completo_curso = curso
        self.nome_ccr = nome_ccr
        self.ch_ccr = ch_ccr
        self.alunos = alunos
        self.horarios = horarios
        self.horarioString = horarioString,
        self.periodoDuracao = periodoDuracao,
        # Aqui vai um novo atributo, uma lista com os incio e termino das aulas, vamos chamar de periodoDuracao
        self.salasPreferenciais = salasPreferenciais
        self.fase = int(fase[0])
        self.cod = cod
        self.agrupamento = []
        self.fusao=fusao
        if("-" in curso):
            self.nome=curso
            self.curso=curso.split("-")
            self.curso=self.curso[0]
            self.curso=self.curso.strip()
            self.curso=self.abreviacao(self.curso)
        if(fusao==1): # Tratando o "nome" das Fusoes
            nome_curso=curso.split(":")
            nome_curso=nome_curso[1]
            nome_curso=nome_curso.split("+")
            self.curso=nome_curso[0]
            self.curso=self.curso[1:-1]
            self.curso=self.curso.strip()
            self.curso=self.abreviacao(self.curso)
            for index,c in enumerate(nome_curso):
                if index == 0:
                    cursos_fusao = self.abreviacao(c.strip())+" - "+fase[index]
                else:
                    cursos_fusao=cursos_fusao+" + "+self.abreviacao(c.strip())+" - "+fase[index]
            self.nome = cursos_fusao
        else:
            self.nome=self.curso
            
    
    def abreviacao(self,curso):
        abreviacao = dict()
        abreviacao["ADMINISTRAÇÃO"]="ADM"
        abreviacao["AGRONOMIA"]="AGRO"
        abreviacao["CIÊNCIA DA COMPUTAÇÃO"]="CC"
        abreviacao["CIÊNCIAS SOCIAIS"]="CS"
        abreviacao["ENFERMAGEM"]="ENF"
        abreviacao["ENGENHARIA AMBIENTAL E SANITÁRIA"]="EAS"
        abreviacao["FILOSOFIA"]="FIL"
        abreviacao["GEOGRAFIA"]="GEO"
        abreviacao["HISTÓRIA"]="HIS"
        abreviacao["LETRAS"]="LET"
        abreviacao["MATEMÁTICA"]="MAT"
        abreviacao["MEDICINA"]="MED"
        abreviacao["PEDAGOGIA"]="PED"
        if curso in abreviacao:
            return abreviacao[curso]
        else: # no caso das optativas
            return curso
    
    def formata_saida(self,horario_planilha):
        if (self.fusao==1): # Para as fusões.
            return ("FUSAO"+ self.nome+" ("+self.cod+")")
        
        if(len(self.agrupamento)>0):
            string_final = self.abreviacao(self.curso)+" - "+str(self.fase)+" ("+self.cod
            for agrupamento in self.agrupamento:
                for horario in agrupamento.horarios:
                    faixa=horario.split("_")[2]
                    dia=horario.split("_")[1]
                    obj=Horario(int(dia),int(faixa))
                    if(obj.converte_horario()==horario_planilha):
                        string_final+= " - AGRUPAMENTO "+agrupamento.cod
                        break
                    else:
                        del obj
            string_final+=") "
            #print(string_final)
            return string_final
        
        if self.fase != 0:
            return (self.abreviacao(self.curso)+" - "+str(self.fase)+" ("+self.cod+")")
        else:
            return (self.abreviacao(self.curso)+" - opt ("+self.cod+")")

    def max_alunos_agrupamento(self):
        if (len(self.agrupamento) == 0):
            return self.alunos

        return max(self.alunos, max(disciplina.alunos for disciplina in self.agrupamento))

    def horarios_agrupamento(self):
        if (len(self.agrupamento) == 0):
            return self.horarios
        
        horarios = dict(self.horarios)
        for disciplina in self.agrupamento:
            horarios.update(disciplina.horarios)
        return horarios
