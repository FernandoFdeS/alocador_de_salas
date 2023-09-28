import pandas as pd
class GeraMatrizDistancia:
    def __init__ (self, salas):
        self.salas = salas
     
    def gera_matriz(self):
        matriz = [['-' for coluna in range(len(self.salas))] for linha in range(len(self.salas))]

        # Regra de distância
        # Mesmo bloco:
        # |Numero Sala 1 - Numero da Sala 2|
        # Bloco diferente
        # |Numero Sala 1 - Numero da Sala 2 * 10| (Mas se for dos espaços ajeitados é * 100) 

        for linha in self.salas:
            #print(linha)
            sala1 = linha
            sala1 = sala1.split("-")
            num_sala1 = int(sala1[0])
            bloco_sala1 = sala1[1]
            #print(num_sala1,bloco_sala1)
            for coluna in self.salas:
                sala2 = coluna
                sala2 = sala2.split("-")
                num_sala2 = int(sala2[0])
                bloco_sala2 = sala2[1]
                if bloco_sala1 != bloco_sala2:
                    multiplicador=10
                    if bloco_sala2 == "DE":
                        multiplicador=100
                    num_sala2*=multiplicador    
                distancia = abs(num_sala1 - num_sala2)
                matriz[list(self.salas).index(linha)][list(self.salas).index(coluna)]=distancia

        df = pd.DataFrame(matriz, columns=self.salas, index=self.salas)
        nome_arquivo = "matriz_distancia.csv"
        df.to_csv(nome_arquivo, index=True) # Cria CSV para facilitar a visualização das distâncias gerada
        return matriz
