import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

class EmailSender:
    def __init__(self):
        # Pegando configurações do .env
        load_dotenv()

        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT'))

    def send_email(self, email_destino, assunto, corpo, anexos):
        msg = EmailMessage()
        msg['From'] = self.email_user
        msg['To'] = email_destino
        msg['Subject'] = assunto
        msg.set_content(corpo)

        for anexo in anexos:
            with open(anexo, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(anexo)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls() 
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            print('E-mail enviado com sucesso!')
        except Exception as e:
            print(f'Erro ao enviar e-mail: {e}')

