import pandas as pd
from Sala import Sala

class ExtraiSalas:
    def __init__ (self, arquivo):
        self.arquivo =arquivo

    def extrai_salas(self):
        dados = pd.read_csv(self.arquivo, encoding="UTF-8" , sep = ",", usecols=["SALAS","CADEIRAS"])
        blocoAtual = ""
        numeroSala = ""
        vet_salas=[]
        nome_salas=[]

        for index, row in dados.iterrows():
            sala = str(row["SALAS"])

            if(sala.find("BLOCO")==0):
                blocoAtual=sala.split(" ")[1] # Pegando o Bloco da Sala
            else:        
                numeroSala=sala.split(" ")[0]

            cadeiras = row["CADEIRAS"]
            if(pd.isna(sala) or pd.isna(cadeiras)):
                continue
            cadeiras=int(cadeiras)
            vet_salas.append(Sala(cadeiras))
            nome_salas.append((numeroSala+"-"+blocoAtual))

        salas = dict()
        for idx,sala in enumerate(range(len(vet_salas))):
            salas[nome_salas[idx]]=vet_salas[idx]

        # for sala in salas:
        #     print (sala, salas[sala].capacidade)
        return salas
