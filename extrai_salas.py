import pandas as pd
from Sala import Sala

dados = pd.read_csv("./dados/salas.csv", encoding="UTF-8" , sep = ",", usecols=["BLOCO","CADEIRAS"])
blocoAtual = ""
numeroSala = ""
vet_salas=[]

for index, row in dados.iterrows():
    sala = str(row["BLOCO"])

    if(sala.find("BLOCO")==0):
        blocoAtual=sala.split(" ")[1] # Pegando o Bloco da Sala
    else:        
        numeroSala=sala.split(" ")[0]

    cadeiras = row["CADEIRAS"]
    if(pd.isna(sala) or pd.isna(cadeiras)):
        continue
    # Salas especiais ("Espaços Ajeitados") não tem número de cadeiras definidas no csv, então são ignoradas.
    cadeiras=int(cadeiras)
    vet_salas.append(Sala(cadeiras,(numeroSala+"-"+blocoAtual)))

salas = dict()
for idx,sala in enumerate(range(len(vet_salas))):
    salas["Sala_{}".format(idx+1)]=vet_salas[idx]
