import os
import smtplib
import ssl
import random
import configparser
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))  # Numeri uniti senza spazi

# Genera OTP e lo invia via email
def send_email(recipient_email, otp_code):
    try:
        logger.info("[DEBUG] Inizio invio OTP...")

        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), "config_otp.ini"))

        sender_email = config.get("EMAIL", "Sender")
        sender_password = config.get("EMAIL", "Password")
        subject = config.get("EMAIL", "Subject")
        smtp_server = config.get("EMAIL", "SMTP_Server")
        smtp_port = config.getint("EMAIL", "SMTP_Port")
        
        # Sicurezza per tipi bytearray
        for var in [sender_email, sender_password, recipient_email, subject]:
            if isinstance(var, bytearray):
                var = var.decode()
                
        # Contenuto HTML stilizzato
        email_content = f"""
        <html>
        <head>
            <meta charset=\"UTF-8\">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    color: #333;
                    background-color: #f4f4f4;
                    padding: 20px;
                    margin: 0;
                }}
                .container {{
                    max-width: 600px;
                    background: white;
                    padding: 40px 20px;
                    margin: 40px auto;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                h2 {{
                    color: #4A90E2;
                    font-size: 26px;
                    margin-bottom: 20px;
                }}
                .otp-text {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #333;
                    background: #eef5ff;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    display: inline-block;
                }}
                .instructions, .footer {{
                    font-size: 16px;
                    margin-top: 20px;
                    color: #555;
                    line-height: 1.5;
                    text-align: center;
                    display: block;
                    clear: both;
                }}
                .footer {{
                    font-size: 12px;
                    color: #aaa;
                }}
            </style>
        </head>
        <body>
            <div class=\"container\">
                <h2>🔐 Il tuo OTP di 6 cifre</h2>
                <p class=\"otp-text\">{otp_code}</p>
                <p class=\"instructions\">Il tuo codice OTP è valido per 10 minuti. Usalo per completare il processo di verifica.</p>
                <div class=\"footer\">
                    <p>Se non hai richiesto questo codice, ignora questa email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        # Composizione email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(email_content, 'html'))
        
        # Invio via SMTP SSL
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        logger.info(f"✅ OTP inviato correttamente.")
        return True

    except Exception as e:
        logger.error(f"❌ Errore invio email OTP: {type(e).__name__}: {e}")
        return False