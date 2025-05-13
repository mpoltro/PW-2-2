import os
import smtplib
import ssl
import random
import string
import configparser
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Funzione per generare una password sicura
def generate_secure_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    characters = characters.replace('"', '').replace("'", '').replace("\\", '')  # Opzionale: rimuove caratteri problematici
    return ''.join(random.SystemRandom().choice(characters) for _ in range(length))

# Funzione per inviare la password via email
def send_password_email(recipient_email, generated_password):
    try:
        logger.info("[DEBUG] Inizio invio password...")

        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), "config_password.ini"))

        sender_email = config.get("EMAIL", "Sender")
        sender_password = config.get("EMAIL", "Password")
        subject = config.get("EMAIL", "Subject")
        smtp_server = config.get("EMAIL", "SMTP_Server")
        smtp_port = config.getint("EMAIL", "SMTP_Port")

        # Sicurezza per tipi bytearray
        for var in [sender_email, sender_password, recipient_email, subject]:
            if isinstance(var, bytearray):
                var = var.decode()

        # HTML email content
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
                .password-text {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #333;
                    background: #eef5ff;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 20px 0;
                    display: inline-block;
                    word-break: break-all;
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
                <h2>🔐 La tua nuova password sicura</h2>
                <p class=\"password-text\">{generated_password}</p>
                <p class=\"instructions\">Usa questa password per accedere al tuo account.</p>
                <div class=\"footer\">
                    <p>Se non hai richiesto questa password, contatta immediatamente il supporto.</p>
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

        # Invio via SMTP
        # Connessione SMTP corretta con starttls
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            logger.info("[DEBUG] Login SMTP...")
            server.login(sender_email, sender_password)
            logger.info("[DEBUG] Invio email...")
            server.sendmail(sender_email, recipient_email, msg.as_string())

        logger.info(f"✅ Password inviata correttamente a {recipient_email}")

        logger.info("sender email: %s recipient email: %s subject: %s", sender_email, recipient_email, subject)
        return True

    except Exception as e:
        logger.error(f"❌ Errore invio email: {type(e).__name__}: {e}")
        return False