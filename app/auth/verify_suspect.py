import hashlib
import requests
import mysql.connector
import os
import smtplib
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from flask import request

# Configurazione Database foto
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "flaskuser"),
    "password": os.getenv("DB_PASSWORD", "flaskpass"),
    "database": os.getenv("DB_NAME", "logsdb"),
}

# Funzione per ottenere la connessione al database
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Funzione per ottenere informazioni IP
def get_ip_info():
    try:
        # Recupera IP corretto
        forwarded_for = request.headers.get('X-Forwarded-For', '')
        real_ip = request.headers.get('X-Real-IP', '')
        
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        elif real_ip:
            client_ip = real_ip
        else:
            client_ip = request.remote_addr or "0.0.0.0"

        # Chiama ip-api.com
        geo_response = requests.get(f"http://ip-api.com/json/{client_ip}")
        if geo_response.status_code == 200:
            geo_data = geo_response.json()
        else:
            geo_data = {"error": "Errore nella richiesta API"}

        # Aggiunge l'IP effettivo
        geo_data["IP Address"] = client_ip
        return geo_data

    except Exception as e:
        return {
            "error": f"Errore: {str(e)}",
            "IP Address": request.remote_addr or "0.0.0.0"
        }

# Funzione per calcolare l'hash
def generate_hash(data):
    hash_object = hashlib.sha256()
    hash_object.update(data.encode())
    return hash_object.hexdigest()

# Funzione per formattare il contenuto dell'email
def format_email_content(ip_data):
    # Legge il file di configurazione per ottenere il corpo del messaggio
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "config_access_suspect.ini"), encoding="utf-8")
    body_text = config.get("EMAIL", "Body")

    # Crea la tabella solo con valori non vuoti
    table_rows = "".join(f"""
        <tr>
            <td><strong>{key}</strong></td>
            <td>{value}</td>
        </tr>
    """ for key, value in ip_data.items() if value and key != "Body")  # Escludiamo vuoti e "Body"

    # Corpo dell'email con un layout moderno
    email_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f6f9;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 100%;
                max-width: 650px;
                background: #ffffff;
                margin: 30px auto;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            h2 {{
                font-size: 24px;
                color: #2c3e50;
                text-align: center;
                margin-bottom: 20px;
            }}
            .body-text {{
                font-size: 16px;
                background-color: #e1f5fe;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 25px;
                text-align: center;
                font-weight: bold;
                color: #0277bd;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th {{
                background-color: #0277bd; /* Azzurro precedente */
                color: #ffffff;
                padding: 12px;
                font-size: 14px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            td {{
                padding: 12px;
                text-align: center; /* Contenuti centrati */
                border: 1px solid #ddd;
                font-size: 14px;
                background-color: #fafafa;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            .footer {{
                margin-top: 40px;
                font-size: 12px;
                color: #777;
                text-align: center;
            }}
            .footer a {{
                color: #0277bd;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔍 Dettagli dell'Indirizzo IP</h2>
            <p class="body-text">{body_text}</p>
            <table>
                <tr>
                    <th>Parametro</th>
                    <th>Valore</th>
                </tr>
                {table_rows}
            </table>
            <div class="footer">
                <p>Se non riconosci questi dettagli o hai domande, non esitare a <a href="mailto:no-reply@dreamteam.mavist.eu">contattarci</a>.</p>
                <p>&copy; 2025 TheDreamTeam. Tutti i diritti riservati.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return email_content

# Funzione per inviare l'email
def send_email(ip_data, email):
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), "config_access_suspect.ini"), encoding="utf-8")

        sender_email = config.get("EMAIL", "Sender")
        recipient_email = email
        subject = config.get("EMAIL", "Subject")
        smtp_server = config.get("EMAIL", "SMTP_Server")
        smtp_port = config.getint("EMAIL", "SMTP_Port")
        smtp_user = config.get("EMAIL", "SMTP_User")
        smtp_password = config.get("EMAIL", "SMTP_Password")

        email_content = format_email_content(ip_data)

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipient_email)
        msg["Subject"] = subject
        msg.attach(MIMEText(email_content, "html"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        logging.info("Email inviata con successo!")

    except Exception as e:
        logging.error(f"Errore nell'invio dell'email: {e}")

# Funzione per confrontare gli hash degli IP nel database
def compare_ip_hash(user_id, email):
    try:
        ip_data = get_ip_info()

        if "error" in ip_data:
            logging.warning(f"Errore nel recupero dati IP: {ip_data['error']}")
            return False

        current_ip = ip_data["IP Address"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        logging.info("Connessione al database effettuata.")

        # Recupera tutti gli IP precedenti per l'utente
        cursor.execute("SELECT IP_Address FROM Access_Events WHERE user_Id = %s", (user_id,))
        rows = cursor.fetchall()

        if not rows:
            return False

        # Conta quante volte l'IP attuale compare
        ip_count = sum(1 for row in rows if row['IP_Address'] == current_ip)

        suspicious = 1 <= ip_count <= 2

        if suspicious:
            send_email(ip_data, email)

        return suspicious

    except Exception as e:
        logging.error(f"Errore nella funzione: {str(e)}")
        return False


