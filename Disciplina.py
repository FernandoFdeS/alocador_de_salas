class Disciplina:
    def __init__(self,curso,alunos,horarios,salasPreferenciais,fase):
        self.curso = curso
        self.alunos = alunos
        self.horarios = horarios
        self.salasPreferenciais = salasPreferenciais
        self.fase = fase
    
    def abreviacao(self):
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
        if self.curso in abreviacao:
            return abreviacao[self.curso]
        else: # no caso das optativas
            return self.curso
    
    def formata_saida(self):
        if self.fase != 0:
            return (self.abreviacao()+" - "+str(self.fase))
        else:
            return (self.abreviacao()+" - opt")
        
