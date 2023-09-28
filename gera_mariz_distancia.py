import pandas as pd

# Salas hardcorded por enquanto
salas= [
    "201-A", "202-A", "203-A", "204-A", "205-A", "206-A", "207-A", "208-A", "209-A", "210-A",
    "301-A", "302-A", "303-A", "304-A", "305-A", "306-A", "307-A", "308-A", "309-A",
    "401-A", "407-A", "408-A", "408-B", "105-B", "108-B",
    "201-B", "202-B", "203-B", "204-B", "205-B", "206-B", "207-B", "208-B", "209-B", "210-B",
    "301-B", "302-B", "303-B", "304-B", "305-B", "308-B", "309-B", "310-B",
    "103-C", "105-C", "215-C", "216-C", "217-C", "218-C",
    "302-C", "311-C", "311-DE", "109-DE", "110-DE"
]
 
matriz = [['-' for coluna in range(len(salas))] for linha in range(len(salas))]

# Regra de distância
# Mesmo bloco:
# |Numero Sala 1 - Numero da Sala 2|
# Bloco diferente
# |Numero Sala 1 - Numero da Sala 2 * 10| (Mas se for dos espaços ajeitados é * 100) 

for linha in range(len(salas)):
    sala1 = salas[linha]
    sala1 = sala1.split("-")
    num_sala1 = int(sala1[0])
    bloco_sala1 = sala1[1]
    #print(num_sala1,bloco_sala1)
    for coluna in range (len(salas)):
        sala2 = salas[coluna]
        sala2 = sala2.split("-")
        num_sala2 = int(sala2[0])
        bloco_sala2 = sala2[1]
        if bloco_sala1 != bloco_sala2:
            multiplicador=10
            if bloco_sala2 == "DE":
                multiplicador=100
            num_sala2*=multiplicador    
        distancia = abs(num_sala1 - num_sala2)
        matriz[linha][coluna]=distancia

df = pd.DataFrame(matriz, columns=salas, index=salas)
nome_arquivo = "matriz_distancia.csv"
df.to_csv(nome_arquivo, index=True)
