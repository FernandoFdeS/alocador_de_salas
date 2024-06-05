from solve import main

horarios="./dados/horarios_teste.xlsx"
salas="./dados/salas_2024_1.csv"
salas_preferenciais="./dados/salas_preferenciais_2024.1.xlsx"

main(arquivo_horarios=horarios,arquivo_salas=salas,arquivo_salas_preferenciais=salas_preferenciais)

# Atenção, como estamos usando o solve.py para resolver o problema
# as planilhas geradas são salvas na no caminho /web/static/dados