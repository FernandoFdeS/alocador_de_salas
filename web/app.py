import os
import sys
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) )

from flask import Flask, render_template, request, jsonify, redirect, url_for
from solve import main
from envia_email import EmailSender  
app = Flask(__name__)

global wait
global processamento
global email
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

    global email
    email=request.form["email"]

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
    print("Enviando para: "+ email)
    email_sender = EmailSender()
    email_destino = 'alocadotron@uffs.edu.br'
    assunto = 'Alocação de salas'
    corpo = 'Olá, o processo de alocação foi concluído. Seguem anexo a planilha e a tabela de alocação gerados.'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    planilha = os.path.join(base_dir, 'static', 'dados', 'planilha_alocacoes.xlsx')
    tabela = os.path.join(base_dir, 'static', 'dados', 'tabela_alocacoes.xlsx')
    anexos = [planilha,tabela]
    email_sender.send_email(email_destino, assunto, corpo, anexos)


@app.route('/check_status')
def check_status():
    global processamento
    global wait
    return jsonify({'complete': processamento,
                    'wait': wait})

@app.route('/wait')
def wait():
    return render_template("wait.html")

@app.route('/finish')
def finish():
    global processamento
    global wait
    processamento = False
    wait = False
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run()