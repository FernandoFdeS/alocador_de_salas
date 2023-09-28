class Disciplina:
    def __init__(self,curso,alunos,horarios,salasPreferenciais,fase,cod,fusao):
        self.curso = curso
        self.alunos = alunos
        self.horarios = horarios
        self.salasPreferenciais = salasPreferenciais
        self.fase = int(fase[0])
        self.cod = cod
        self.fusao=fusao
        if(fusao==1): # Tratando o "nome" das Fusoes
            cursos_fusao=''
            nome_curso=curso.split(":")
            nome_curso=nome_curso[1]
            nome_curso=nome_curso.split("+")
            for index,c in enumerate(nome_curso):
                if index == 0:
                    cursos_fusao = self.abreviacao(c.strip())+" - "+fase[index]
                else:
                    cursos_fusao=cursos_fusao+" + "+self.abreviacao(c.strip())+" - "+fase[index]
            self.curso = cursos_fusao
            
    
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
    
    def formata_saida(self):
        if (self.abreviacao(self.curso)==self.curso): # Para as fusões.
            return (self.curso+" ("+self.cod+")")
        if self.fase != 0:
            return (self.abreviacao(self.curso)+" - "+str(self.fase)+" ("+self.cod+")")
        else:
            return (self.abreviacao(self.curso)+" - opt ("+self.cod+")")
        
