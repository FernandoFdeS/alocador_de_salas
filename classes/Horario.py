class Horario:
    def __init__(self,dia,faixa):
        self.dia = dia
        self.faixa = faixa

    def converte_horario(self):
        # Conversão de horário do padrão do sigaa para a o padrão utilizado na tabela de saída.
        dia=dict()
        dia[2]="SEG"
        dia[3]="TER"
        dia[4]="QUA"
        dia[5]="QUI"
        dia[6]="SEX"
        dia[7]="SAB"
        return str(dia[self.dia]+"-"+self.get_periodo())
    
    def get_faixa_convertida(self):
        if self.faixa <= 6:
            return self.faixa
        elif self.faixa>6 and self.faixa<=12:
            return self.faixa - 6
        else:
            return self.faixa - 12
    
    def get_periodo(self):
        if self.faixa <= 6:
            return "M"
        elif self.faixa>6 and self.faixa<=12:
            return "V"
        else:
            return "N"
    
