import os
import sys
import threading

# Adicione a raiz do projeto ao caminho do módulo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) )

from flask import Flask, render_template, request, jsonify, redirect, url_for
from solve import main
app = Flask(__name__)

global wait
global processamento
wait = False
processamento = False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/solve", methods=['POST'])
def solve():
    # Salvando arquivos.
    arquivo_salas_preferenciais=request.files["salas_preferenciais"]
    arquivo_salas=request.files["salas"]
    arquivo_horarios=request.files["horarios"]

    folder = './web/static/dados/'
    path_salas_preferenciais=folder+"salas_preferenciais.xlsx"
    path_salas=folder+"salas.csv"
    path_horarios=folder+"horarios.xlsx"

    arquivo_salas_preferenciais.save(path_salas_preferenciais)
    arquivo_salas.save(path_salas)
    arquivo_horarios.save(path_horarios)

    # Cria thread para rodar processamento das alocações
    thread = threading.Thread(target=process, args=(path_horarios, path_salas, path_salas_preferenciais))
    thread.start()
    return redirect(url_for('wait'))
    # Retorna view de "espera"
    

def process(path_horarios,path_salas,path_salas_preferenciais):
    global processamento
    global wait
    wait = True
    processamento = False
    main(arquivo_horarios=path_horarios,arquivo_salas=path_salas,arquivo_salas_preferenciais=path_salas_preferenciais)
    processamento = True


@app.route('/check_status')
def check_status():
    global processamento
    global wait
    return jsonify({'complete': processamento,
                    'wait': wait})

@app.route('/wait')
def wait():
    return render_template("wait.html")

if __name__ == "__main__":
    app.run()