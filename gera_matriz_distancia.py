import pandas as pd
class GeraMatrizDistancia:
    def __init__ (self, salas):
        self.salas = salas
     
    def gera_matriz(self):
        matriz = [['-' for coluna in range(len(self.salas))] for linha in range(len(self.salas))]
        for linha in self.salas:
            #print(linha)
            sala1 = linha
            sala1 = sala1.split("-")
            num_sala1 = int(sala1[0])
            bloco_sala1 = sala1[1]
            #print(num_sala1,bloco_sala1)            
            for coluna in self.salas:
                bloco_diferente=0
                sala2 = coluna
                sala2 = sala2.split("-")
                num_sala2 = int(sala2[0])
                bloco_sala2 = sala2[1]
                if bloco_sala1 != bloco_sala2:
                    bloco_diferente=50
                    if bloco_sala2 == "C":
                        bloco_diferente=100
                    if bloco_sala2 == "DE":
                        bloco_diferente=150
                dif_andares = abs((num_sala1//100) - (num_sala2//100))              
                dif_salas= abs((num_sala1%100)-(num_sala2%100))
                if dif_salas==9:
                    dif_salas=1
                distancia =  dif_salas+(dif_andares*10)+bloco_diferente
                # Distancia = 
                # Diferença do número da sala (ultimos dois digitos) (se der 9 trocamos pra 1) (para poder aproximar as salas _10 das salas _01)
                # Diferença de andar * 10
                # Diferença de bloco = + 50 no valor total (se for do "bloco" dos espaços ajeitados(DE) + 150)

                matriz[list(self.salas).index(linha)][list(self.salas).index(coluna)]=distancia

        df = pd.DataFrame(matriz, columns=self.salas, index=self.salas)
        nome_arquivo = "matriz_distancia.csv"
        df.to_csv(nome_arquivo, index=True) # Cria CSV para facilitar a visualização das distâncias gerada
        return matriz
