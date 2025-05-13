import os
import sys
from pathlib import Path
from user_agents import parse
from dotenv import load_dotenv
from auth.send_password_email import send_password_email, generate_secure_password

# --- Local Imports ---
from db import create_usersdb_connection, create_logsdb_connection
from utils.security import hash_password, hash_otp, check_otp_hash
from crypto_utils import aes_ecb_encrypt, aes_ecb_decrypt, aes_gcm_decrypt
from auth.mail_otp import send_email, generate_otp
from auth.verify_suspect import compare_ip_hash, get_ip_info

# --- Standard Imports ---
import logging
from datetime import datetime, timedelta
import secrets
from functools import wraps
import csv
from io import StringIO
import threading
from watcher import start_otp_watcher
from User_Access_Watcher import start_user_accesses_watcher

# --- Third-Party Imports ---
from flask import (
    Flask,
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_from_directory,
    session,
    Response,
)
from flask_login import (
    current_user,
    LoginManager,
    UserMixin,
    login_user,
    login_required,
)

app_dir = str(Path(__file__).parent.resolve())

# --- Aggiunge la directory dell'app a sys.path per importare moduli locali ---
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

auth = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

# --- Configurazione del logger ---
threading.Thread(target=start_otp_watcher, daemon=True).start()
threading.Thread(target=start_user_accesses_watcher, daemon=True).start()

# --- Inizializzazione app ---
load_dotenv()
app = Flask(__name__)

# --- Configurazione o recupero della chiave segreta ---
app.secret_key = aes_gcm_decrypt(os.environ.get("SECRET_KEY")) or (
    secrets.token_urlsafe(32)
    if aes_gcm_decrypt(os.environ.get("FLASK_ENV")) == "development"
    else None
)

# --- Se manca la chiave segreta, lancia un errore ---
if not app.secret_key:
    raise RuntimeError(
        "❌ SECRET_KEY mancante. Impostala nel file .env o tra le variabili d'ambiente."
    )

# Imposta il livello di log
app.logger.setLevel(logging.INFO)

# Login manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

# Modello utente
# Definisce il modello utente per Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password=None, role=None):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

# --- Funzione per caricare l'utente ---
# Questa funzione viene chiamata da Flask-Login per caricare l'utente
@login_manager.user_loader
def load_user(user_id):
    conn = create_usersdb_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, password, role FROM Users WHERE id = %s", (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return User(row["id"], row["username"], row["password"], row["role"])
    finally:
        cursor.close()
        conn.close()
    return None

# --- Funzione per verificare il ruolo ---
# Questa funzione è un decoratore che verifica se l'utente ha il ruolo richiesto
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in allowed_roles:
                log_event(
                    "warning",
                    "Tentativo accesso non autorizzato",
                    "security",
                    getattr(current_user, "id", None),
                    None
                )
                flash("Accesso riservato agli utenti autorizzati.", "danger")
                return redirect(url_for("dashboard"))  # Cambia se serve
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Funzione per loggare eventi nel database
# Questa funzione registra eventi di accesso, errori e avvisi nel database
def log_event(event_type, description, action, user_id=None, conn=None):
    try:
        if conn is None:
            conn = create_logsdb_connection()
            created_conn = True
        else:
            created_conn = False

        cursor = conn.cursor()

        table_map = {"success": "Success", "error": "Errors", "warning": "Warnings"}

        if event_type not in table_map:
            print("Tipo di evento non valido.")
            return

        query = f"INSERT INTO {table_map[event_type]} (Description, Action, Date_Time, User_Id) VALUES (%s, %s, %s, %s)"

        cursor.execute(query, (description, action, datetime.now() + timedelta(hours = 2), user_id))
        conn.commit()

    except Exception as e:
        print(f"Errore durante il logging: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            if created_conn:
                conn.close()


# === FUNZIONI RUOLO COLORE, CLASSE, LABEL ===
def get_role_color(role):
    if role == "admin":
        return "rgba(54, 162, 235, 1)"
    elif role == "user":
        return "rgba(75, 192, 192, 1)"
    elif role == "guest":
        return "rgba(255, 159, 64, 1)"
    return "#000000"


def get_role_label(role):
    mapping = {"admin": "Amministratore", "user": "Utente", "guest": "Ospite"}
    return mapping.get(role, "Sconosciuto")


def get_role_class(role):
    return {"admin": "Amministratore", "user": "Utente", "guest": "Ospite"}.get(
        role, "Default"
    )

# Funzione per loggare eventi di accesso
# Questa funzione registra eventi di accesso nel database
def log_access_event(logs_cursor, user_id, status, is_api_check=False):
    # Recupera IP reale da header se presente
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    real_ip = request.headers.get('X-Real-IP', '')

    # Gestione dell'IP: prende il primo IP se X-Forwarded-For ha una lista
    if forwarded_for:
        ip = forwarded_for.split(',')[0].strip()
    elif real_ip:
        ip = real_ip
    else:
        ip = request.remote_addr or "0.0.0.0"

    device_info = str(parse(request.headers.get("User-Agent", "Unknown")))
    geo = get_ip_info()  # Passa l'IP giusto al geolocalizzatore

    logs_cursor.execute("""
        INSERT INTO Access_Events (
            Status, IP_Address, Device_Info, Location,
            API_Check, User_Id, Country, CountryCode, Region,
            RegionName, City, Latitude, Longitude,
            Timezone, ISP, AS_Organization, Query
        ) VALUES (%s, %s, %s, %s,
                  %s, %s, %s, %s, %s,
                  %s, %s, %s, %s,
                  %s, %s, %s, %s)
    """, (
        status,
        geo.get("IP Address", ip),
        device_info,
        f"{geo.get('city', '')}, {geo.get('regionName', '')}",
        is_api_check,
        user_id,
        geo.get("country", ""),
        geo.get("countryCode", ""),
        geo.get("region", ""),
        geo.get("regionName", ""),
        geo.get("city", ""),
        geo.get("lat", 0.0),
        geo.get("lon", 0.0),
        geo.get("timezone", ""),
        geo.get("isp", ""),
        geo.get("org", ""),
        geo.get("query", geo.get("IP Address", ip))
    ))

# Registra funzioni in Jinja
app.jinja_env.globals.update(get_role_class=get_role_class)
app.jinja_env.globals.update(get_role_color=get_role_color)
app.jinja_env.globals.update(get_role_label=get_role_label)

# Blueprint
auth = Blueprint("auth", __name__)
auth = Blueprint("auth", __name__)

# --- Carica la chiave PEPPER ---
PEPPER = aes_gcm_decrypt(os.environ.get("PEPPER"))
if not PEPPER:
    raise RuntimeError(
        "❌ PEPPER mancante. Impostalo nel file .env o tra le variabili d'ambiente."
    )

# --- Funzione per la gestione della privacy ---
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# --- Funzione per la gestione dei login ---
# Questa funzione gestisce il login degli utenti
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]

        conn = create_usersdb_connection()
        logs_conn = create_logsdb_connection()

        if not conn or not logs_conn:
            logger.error("❌ Errore connessione database")
            return jsonify({"error": "Errore di connessione"}), 500
        try:
            cursor = conn.cursor(dictionary=True)
            logs_cursor = logs_conn.cursor()

            cursor.execute(
                "SELECT id, username, password, role, salt, email FROM Users WHERE email = %s",
                (aes_ecb_encrypt(email),),
            )
            user = cursor.fetchone()

            if user:
                expected_hash = hash_password(
                    password, bytes.fromhex(user["salt"]), PEPPER
                )
                # Verifica se l'hash della password corrisponde
                if expected_hash == user["password"]:
                    entrato = False
                    # Controllo IP sospetto
                    if compare_ip_hash(user["id"], aes_ecb_decrypt(user["email"])) != False:
                        entrato = True
                        log_access_event(logs_cursor, user["id"], "sospetto", is_api_check=False)
                        logs_conn.commit()

                    # Sessione temporanea
                    session["pending_user"] = {
                        "id": user["id"],
                        "username": user["username"],
                        "password": user["password"],
                        "role": user["role"],
                    }

                    # Pulizia codici OTP vecchi
                    cursor.execute(
                        """
                        DELETE FROM Authenticated
                        WHERE User_Id = %s OR Created_At < NOW() - INTERVAL 10 MINUTE
                        """,
                        (user["id"],),
                    )

                    otp = generate_otp()
                    cursor.execute(
                        """
                        INSERT INTO Authenticated (Code, Uso, Created_At, User_Id)
                        VALUES (%s, 0, NOW(), %s)
                        """,
                        (hash_otp(otp), user["id"]),
                    )

                    conn.commit()

                    # Logging accesso autorizzato
                    if not entrato:
                        log_access_event(logs_cursor, user["id"], "autorizzato", is_api_check=False)
                    logs_conn.commit()

                    # Invio OTP
                    if not send_email(aes_ecb_decrypt(user["email"]), otp):
                        logger.error("❌ Errore invio OTP via email")
                        return jsonify({"error": "Errore nell'invio dell'OTP via email"}), 500

                    return jsonify({"show_otp_modal": True})
                else:
                    # Logging accesso negato
                    log_access_event(logs_cursor, user["id"], "negato", is_api_check=False)
                    logs_conn.commit()
                    logger.warning("❗ Credenziali errate per email %s", email)
                    return jsonify({"error": "Credenziali errate"}), 401
            else:
                # Logging accesso negato
                log_access_event(logs_cursor, 0, "negato", is_api_check=False)
                logs_conn.commit()
                logger.warning("❗ Utente non trovato: %s", email)
                return jsonify({"error": "Utente non trovato"}), 401

        except Exception as e:
            logger.error("❌ Errore durante il login: %s", str(e))
            return jsonify({"error": "Errore interno del server"}), 500

        finally:
            cursor.close()
            conn.close()
            logs_cursor.close()
            logs_conn.close()

    return render_template("login.html")


# --- Funzione per il resend degli OTP in caso fosse scaduto ---
# Questa funzione invia un nuovo OTP all'utente
@auth.route("/resend-otp", methods=["POST"])
def resend_otp():
    user_data = session.get("pending_user")
    if not user_data:
        logger.error("❌ Sessione utente non valida per resend-otp")
        return jsonify({"success": False, "error": "Sessione non valida"}), 400

    conn = create_usersdb_connection()
    if not conn:
        return jsonify({"success": False, "error": "Errore di connessione al database"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT Email FROM Users WHERE id = %s",
            (user_data["id"],)
        )
        user_db = cursor.fetchone()
        
        if not user_db:
            return jsonify({"success": False, "error": "Utente non trovato"}), 404

        cursor.execute(
            "DELETE FROM Authenticated WHERE User_Id = %s OR Created_At < NOW() - INTERVAL 10 MINUTE",
            (user_data["id"],)
        )

        otp = generate_otp()
        cursor.execute(
            "INSERT INTO Authenticated (Code, Uso, Created_At, User_Id) VALUES (%s, 0, NOW(), %s)",
            (hash_otp(otp), user_data["id"])
        )

        decrypted_email = aes_ecb_decrypt(user_db["Email"])
        if not send_email(decrypted_email, otp):
            logger.error("❌ Errore invio OTP durante resend")
            return jsonify({"success": False, "error": "Errore nell'invio dell'email"}), 500

        conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Errore resend-otp: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Errore interno del server"}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if conn and conn.is_connected(): conn.close()

# --- Funzione per la verifica dell'OTP ---
# Questa funzione verifica l'OTP inserito dall'utente
@auth.route("/verify-otp", methods=["POST"])
def verify_otp():
    try:
        user_data = session.get("pending_user")
        if not user_data:
            logger.error("Nessun utente in attesa di verifica OTP")
            return jsonify({"error": "Sessione non valida"}), 401

        data = request.get_json()
        entered_otp = data.get("otp", "").strip()
        user_ip = request.remote_addr
        user_agent = request.headers.get("User-Agent", "Unknown")
        user_id = user_data["id"]

        conn = create_usersdb_connection()
        logs_conn = create_logsdb_connection()
        if not conn or not logs_conn:
            logger.error("Connessione database fallita")
            return jsonify({"error": "Errore di connessione al database"}), 500

        try:
            cursor = conn.cursor(dictionary=True)
            logs_cursor = logs_conn.cursor()

            cursor.execute("""
                DELETE FROM Authenticated 
                WHERE Created_At < NOW() - INTERVAL 10 MINUTE
            """)
            conn.commit()

            cursor.execute("""
                SELECT Id, Code, Uso, Created_At
                FROM Authenticated
                WHERE User_Id = %s
                  AND Created_At >= NOW() - INTERVAL 10 MINUTE
                ORDER BY Created_At DESC
                LIMIT 1
            """, (user_id,))
            otp_data = cursor.fetchone()

            if not otp_data:
                logs_cursor.execute("""
                    INSERT INTO Access_Events 
                    (Status, IP_Address, Device_Info, Location, API_Check, Created_At, User_Id)
                    VALUES ('OTP scaduto', %s, %s, 'unknown', 1, NOW(), %s)
                """, (user_ip, user_agent, user_id))
                logs_conn.commit()
                return jsonify({"error": "OTP scaduto o non trovato"}), 401

            if check_otp_hash(entered_otp, otp_data["Code"]):
                user = User(user_data["id"], user_data["username"], role=user_data["role"])
                login_user(user)

                logs_cursor.execute("""
                    INSERT INTO Access_Events 
                    (Status, IP_Address, Device_Info, Location, API_Check, Created_At, User_Id)
                    VALUES ('autorizzato', %s, %s, 'unknown', 1, NOW(), %s)
                """, (user_ip, user_agent, user_id))

                cursor.execute("DELETE FROM Authenticated WHERE User_Id = %s", (user_id,))

                conn.commit()
                logs_conn.commit()
                return jsonify({"success": True})

            else:
                new_uso = otp_data["Uso"] + 1
                cursor.execute("""
                    UPDATE Authenticated SET Uso = %s WHERE Id = %s
                """, (new_uso, otp_data["Id"]))
                
                if new_uso >= 5:
                    cursor.execute("DELETE FROM Authenticated WHERE Id = %s", (otp_data["Id"],))
                
                conn.commit()

                logs_cursor.execute("""
                    INSERT INTO Access_Events 
                    (Status, IP_Address, Device_Info, Location, API_Check, Created_At, User_Id)
                    VALUES ('negato', %s, %s, 'unknown', 1, NOW(), %s)
                """, (user_ip, user_agent, user_id))
                logs_conn.commit()

                logger.warning(f"Tentativo fallito per user_id={user_id}")
                return jsonify({"error": "OTP errato"}), 401

        except Exception as e:
            conn.rollback()
            logs_conn.rollback()
            logger.error(f"Errore durante verifica OTP: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Errore critico in verify-otp: {str(e)}")
        return jsonify({"error": "Errore interno del server"}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'logs_cursor' in locals(): logs_cursor.close()
        if conn and conn.is_connected(): conn.close()
        if logs_conn and logs_conn.is_connected(): logs_conn.close()

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)

# --- Funzione di rotta generica ---
# Questa funzione gestisce la rotta principale dell'app
@app.route("/")
@login_required
def dashboard():
    log_event("success", "Accesso a Dashboard", "Navigazione", current_user.id)
    return render_template("dashboard.html")

# --- Funzione per la gestione degli accessi ---
# Questa funzione ritorna gli accessi degli utenti e le statistiche
@app.route("/api/accessi")
@login_required
def get_accessi():
    conn = create_usersdb_connection()
    if not conn:
        log_event("error", "Connessione al database fallita", "api", current_user.id)
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        is_guest = current_user.role == "guest"
        user_filter = "WHERE b.User_Id = %s" if is_guest else ""

        # Statistiche totali
        cursor.execute(
            f"""
            SELECT 
                COUNT(*) AS totali,
                SUM(CASE WHEN ua.Status = 'riuscito' THEN 1 ELSE 0 END) AS riusciti,
                SUM(CASE WHEN ua.Status = 'fallito' THEN 1 ELSE 0 END) AS falliti
            FROM User_Accesses ua
            JOIN Badges b ON ua.Badge_Id = b.Id
            {user_filter}
            """,
            (current_user.id,) if is_guest else None
        )
        stats = cursor.fetchone()

        # Statistiche oggi
        cursor.execute(
            f"""
            SELECT 
                COUNT(*) AS oggi_totali,
                SUM(CASE WHEN ua.Status = 'riuscito' THEN 1 ELSE 0 END) AS oggi_riusciti,
                SUM(CASE WHEN ua.Status = 'fallito' THEN 1 ELSE 0 END) AS oggi_falliti
            FROM User_Accesses ua
            JOIN Badges b ON ua.Badge_Id = b.Id
            WHERE DATE(ua.Created_At) = CURDATE()
            {"AND b.User_Id = %s" if is_guest else ""}
            """,
            (current_user.id,) if is_guest else None
        )
        oggi_stats = cursor.fetchone()

        # Accessi recenti
        cursor.execute(
            f"""
            SELECT u.Username, ua.Status, ua.Created_At, b.Location_Name
            FROM User_Accesses ua
            JOIN Badges b ON ua.Badge_Id = b.Id
            JOIN Users u ON b.User_Id = u.Id
            {"WHERE b.User_Id = %s" if is_guest else ""}
            ORDER BY ua.Created_At DESC
            LIMIT 10
            """,
            (current_user.id,) if is_guest else None
        )
        accessi_recenti = cursor.fetchall()

        # Accessi settimanali per giorno
        cursor.execute(
            f"""
            SELECT 
                DATE(ua.Created_At) AS giorno,
                COUNT(*) AS totali,
                SUM(CASE WHEN ua.Status = 'riuscito' THEN 1 ELSE 0 END) AS riusciti,
                SUM(CASE WHEN ua.Status = 'fallito' THEN 1 ELSE 0 END) AS falliti
            FROM User_Accesses ua
            JOIN Badges b ON ua.Badge_Id = b.Id
            WHERE ua.Created_At >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            {"AND b.User_Id = %s" if is_guest else ""}
            GROUP BY DATE(ua.Created_At)
            ORDER BY giorno
            """,
            (current_user.id,) if is_guest else None
        )
        accessi_settimanali = cursor.fetchall()

        # Accessi per utente
        if is_guest:
            cursor.execute(
                """
                SELECT u.Username AS username, COUNT(*) AS count
                FROM User_Accesses ua
                JOIN Badges b ON ua.Badge_Id = b.Id
                JOIN Users u ON b.User_Id = u.Id
                WHERE b.User_Id = %s
                GROUP BY u.Username
                """,
                (current_user.id,)
            )
        else:
            cursor.execute(
                """
                SELECT u.Username AS username, COUNT(*) AS count
                FROM User_Accesses ua
                JOIN Badges b ON ua.Badge_Id = b.Id
                JOIN Users u ON b.User_Id = u.Id
                GROUP BY u.Username
                ORDER BY count DESC
                """
            )
        accessi_per_utente = cursor.fetchall()

        return jsonify(
            {
                "stats": stats,
                "oggi_stats": oggi_stats,
                "accessi_recenti": accessi_recenti,
                "accessi_settimanali": accessi_settimanali,
                "accessi_per_utente": accessi_per_utente,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    except Exception as e:
        log_event("error", f"Errore API accessi: {str(e)}", "api", current_user.id)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# --- Funzione per la gestione delle statistiche aggregate ---
# Questa funzione ritorna le statistiche aggregate degli accessi
@app.route("/api/stats/aggregate")
@login_required
def get_aggregate_stats():
    conn_logs = create_logsdb_connection()
    conn_users = create_usersdb_connection()

    if not conn_logs or not conn_users:
        log_event("error", "Connessione ai database fallita", "api", current_user.id)
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor_logs = conn_logs.cursor(dictionary=True)
        cursor_users = conn_users.cursor(dictionary=True)

        # Accessi per ora
        cursor_logs.execute("""
            SELECT HOUR(Created_At) as ora, COUNT(*) as totali
            FROM Access_Events
            GROUP BY HOUR(Created_At)
            ORDER BY ora
        """)
        accessi_per_ora = cursor_logs.fetchall()

        # Accessi per giorno della settimana
        cursor_logs.execute("""
            SELECT DAYNAME(Created_At) as giorno, COUNT(*) as totali
            FROM Access_Events
            GROUP BY DAYNAME(Created_At), DAYOFWEEK(Created_At)
            ORDER BY DAYOFWEEK(Created_At)
        """)
        accessi_per_giorno = cursor_logs.fetchall()

        # Accessi di oggi per utente con CONVERT_TZ
        cursor_logs.execute("""
            SELECT User_Id, COUNT(*) as count
            FROM Access_Events
            WHERE DATE(CONVERT_TZ(Created_At, '+00:00', '+02:00')) = CURDATE()
            GROUP BY User_Id
        """)
        oggi_accessi_raw = cursor_logs.fetchall()

        # Mappa utenti
        user_ids = [row['User_Id'] for row in oggi_accessi_raw]
        user_map = {}
        if user_ids:
            format_strings = ','.join(['%s'] * len(user_ids))
            cursor_users.execute(f"""SELECT id, username FROM Users WHERE id IN ({format_strings})""", tuple(user_ids))
            for row in cursor_users.fetchall():
                user_map[row['id']] = row['username']
        accessi_oggi_per_utente = [
            { "username": user_map.get(row["User_Id"], f"ID {row['User_Id']}"), "count": row["count"] }
            for row in oggi_accessi_raw
        ]

        return jsonify({
            "accessi_per_ora": accessi_per_ora,
            "accessi_per_giorno": accessi_per_giorno,
            "accessi_oggi_per_utente": accessi_oggi_per_utente
        })
    except Exception as e:
        log_event("error", f"Errore API aggregate: {str(e)}", "api", current_user.id)
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor_logs.close()
        cursor_users.close()
        conn_logs.close()
        conn_users.close()

# --- Funzione per la gestione degli utenti ---
# Questa funzione gestisce la visualizzazione e la creazione di utenti
@auth.route("/users", methods=["GET", "POST"])
@login_required
@role_required("admin")
def users():

    conn_users = create_usersdb_connection()
    conn_logs = create_logsdb_connection()

    if not conn_users or not conn_logs:
        log_event(
            "error", "Connessione al database fallita", "database", current_user.id
        )
        flash("Errore di connessione al database", "danger")
        return redirect(url_for("dashboard"))

    try:
        cursor_users = conn_users.cursor(dictionary=True)
        cursor_logs = conn_logs.cursor(dictionary=True)

        # Verifico se si vuole creare un nuovo utente
        if request.method == "POST":
            username = request.form.get("Username", "").strip()
            password = generate_secure_password()
            role = request.form.get("role", "user").strip()
            email = request.form.get("email", "").strip()

            logger.info(f"Creazione utente: {username} con ruolo {role}")

            try:
                salt = os.urandom(32)
                hexed_salt = salt.hex()
                password_hash = hash_password(password, salt, PEPPER)
                encrypted_email = aes_ecb_encrypt(email)
            
                cursor_users.execute(
                    """
                    INSERT INTO Users (Email, Username, Password, Salt, Role)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        encrypted_email,
                        username,
                        password_hash,
                        hexed_salt,
                        role
                    )
                )
                logger.info(f"Utente {username} creato con successo")
                send_password_email(email, password)

                # Ottieni ID utente appena creato
                conn_users.commit()
                cursor_users.execute("SELECT LAST_INSERT_ID() AS id")
                user_id = cursor_users.fetchone()["id"]
                
                # Gestione badge
                location_name = request.form.get("location", "").strip()

                location_mapping = {
                    "Lepida": ("Italia", "Bologna", "Lepida"),
                    "Bigari": ("Italia", "Bologna", "Bigari"),
                    "Agrigento": ("Italia", "Ferrara", "Agrigento"),
                    "Centro": ("Italia", "Ferrara", "Centro")
                }

                if location_name in location_mapping:
                    nation, location, loc_name = location_mapping[location_name]
                    cursor_users.execute(
                        """
                        INSERT INTO Badges (Nation, Location, Location_Name, User_Id)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (nation, location, loc_name, user_id)
                    )
                    
                # Gestione upload foto
                photo = request.files.get("photo")
                
                # Creazione della cartella di upload
                # Qesta è la cartella dove verranno salvate le foto per essere passate al server dell' ESP32
                UPLOAD_FOLDER = os.path.join(os.getcwd(), "output/")
                ALLOWED_EXTENSIONS = {"jpg"}

                def allowed_file(filename):
                    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

                # Verifica se il file è valido
                # Se l'utente ha caricato una foto, crea un file con il nome dell'utente
                # e salva la foto nella cartella di upload
                if photo:
                    if allowed_file(photo.filename):
                        filename = f"{user_id}.jpg"
                        if not os.path.exists(UPLOAD_FOLDER):
                            os.makedirs(UPLOAD_FOLDER)
                        file_path = os.path.join(UPLOAD_FOLDER, filename)
                        photo.save(file_path)
                        instruction_path = os.path.join(UPLOAD_FOLDER, "instruction.txt")
                        with open(instruction_path, "w") as f:
                            f.write(f"add {filename}\n")
                        
                        cursor_users.execute(
                            """
                            INSERT INTO Photos (Name, Path, User_Id)
                            VALUES (%s, %s, %s)
                            """,
                            (filename, "tanto va tolto", user_id)
                        )
                        conn_users.commit()
                    else:
                        logger.warning("Formato file non valido. Solo .jpg accettati.")
                else:
                    logger.warning("Nessuna foto caricata.")

                # Log dell'operazione
                if role == "admin":
                    log_event(
                        "warning",
                        f"Creato nuovo admin: {username}",
                        "admin_operations",
                        current_user.id,
                        conn_logs,
                    )
                    flash(f"Creato nuovo amministratore: {username}", "success")
                else:
                    log_event(
                        "success",
                        f"Creato utente {username} (ruolo: {role})",
                        "user_management",
                        current_user.id,
                        conn_logs,
                    )
                    flash(f"Creato utente {username} completato", "success")

            except Exception as e:
                conn_users.rollback()
                log_event(
                    "error",
                    f"Errore creazione utente {username}: {str(e)}",
                    "user_management",
                    current_user.id,
                    conn_logs,
                )
                flash(f"Errore durante la creazione dell'utente: {str(e)}", "danger")

        # Recupera gli utenti esistenti
        cursor_users.execute(
            """
            SELECT id, Username, role, Updated_At as last_login 
            FROM Users 
            ORDER BY Username
        """
        )
        users = cursor_users.fetchall()

        # Recupera la distribuzione dei ruoli
        cursor_users.execute(
            """
            SELECT Role, COUNT(*) as count 
            FROM Users 
            GROUP BY Role
        """
        )
        role_data = cursor_users.fetchall()

        # Crea un dizionario per la distribuzione dei ruoli        
        role_distribution = {
            "admin": next((r["count"] for r in role_data if r["Role"] == "admin"), 0),
            "user": next((r["count"] for r in role_data if r["Role"] == "user"), 0),
            "guest": next((r["count"] for r in role_data if r["Role"] == "guest"), 0),
        }

        # Recupera gli accessi giornalieri
        cursor_logs.execute(
            """
            SELECT Username as username, COUNT(*) as count
            FROM Logs
            WHERE Date_Time >= CURDATE()
            GROUP BY Username
        """
        )
        daily_access = cursor_logs.fetchall()

        return render_template(
            "users.html",
            users=users,
            role_distribution=role_distribution,
            daily_access=daily_access,
            get_role_color=get_role_color,
            get_role_label=get_role_label,
        )

    except Exception as e:
        log_event(
            "error",
            f"Errore grave in gestione utenti: {str(e)}",
            "system",
            current_user.id,
            conn_logs,
        )
        flash("Si è verificato un errore imprevisto", "danger")
        return redirect(url_for("dashboard"))

    finally:
        if "cursor_users" in locals():
            cursor_users.close()
        if "cursor_logs" in locals():
            cursor_logs.close()
        if conn_users and conn_users.is_connected():
            conn_users.close()
        if conn_logs and conn_logs.is_connected():
            conn_logs.close()


# --- Funzione per la gestione della cronologia degli accessi ---
# Questa funzione mostra la cronologia degli accessi
@auth.route("/history")
@login_required
def history():
    conn = create_usersdb_connection()
    if not conn:
        flash("Errore di connessione al database", "danger")
        return redirect(url_for("auth.login"))

    try:
        log_event("success", "Accesso ad Accessi", "Navigazione", current_user.id)
        cursor = conn.cursor(dictionary=True)

        if current_user.role == "guest":
            # Mostra solo i log associati all'utente corrente tramite Badges.User_Id
            cursor.execute(
                """
                SELECT 
                    u.Username, 
                    ua.Status, 
                    b.Nation, 
                    b.Location, 
                    b.Location_Name, 
                    ua.Created_At AS data_accesso
                FROM User_Accesses ua
                JOIN Badges b ON ua.Badge_Id = b.Id
                JOIN Users u ON b.User_Id = u.Id
                WHERE b.User_Id = %s
                ORDER BY ua.Created_At DESC
                """,
                (current_user.id,)
            )
        else:
            # Mostra tutti i log per admin/user
            cursor.execute(
                """
                SELECT 
                    u.Username, 
                    ua.Status, 
                    b.Nation, 
                    b.Location, 
                    b.Location_Name, 
                    ua.Created_At AS data_accesso
                FROM User_Accesses ua
                JOIN Badges b ON ua.Badge_Id = b.Id
                JOIN Users u ON b.User_Id = u.Id
                ORDER BY ua.Created_At DESC
                """
            )

        logs = cursor.fetchall()
        return render_template("history.html", logs=logs)

    finally:
        cursor.close()
        conn.close()

# --- Funzione per la gestione dei log sospetti ---
# Questa funzione mostra i log sospetti
@app.route("/suspicious_logins")
@login_required
def suspicious_logins():
    conn = create_logsdb_connection()
    if not conn:
        flash("Database connection error", "danger")
        return redirect(url_for("auth.login"))
    try:
        log_event("success", "Accesso a Login Sospetti", "Navigazione", current_user.id)
        cursor = conn.cursor(dictionary=True)
        
        if current_user.role == "guest":
            # Query per utenti guest (solo i loro accessi autorizzati)
            cursor.execute("""
                SELECT *, DATE_ADD(Created_At, INTERVAL 2 HOUR) AS Created_At_Adjusted 
                FROM Access_Events 
                WHERE Status = 'autorizzato' 
                AND User_Id = %s
                ORDER BY Created_At_Adjusted DESC
            """, (current_user.id,))
            authorized_accesses = cursor.fetchall()
            
            # Query per utenti guest (solo i loro accessi negati)
            cursor.execute("""
                SELECT *, DATE_ADD(Created_At, INTERVAL 2 HOUR) AS Created_At_Adjusted 
                FROM Access_Events 
                WHERE Status = 'negato' 
                AND User_Id = %s
                ORDER BY Created_At_Adjusted DESC
            """, (current_user.id,))
            denied_accesses = cursor.fetchall()
        else:
            # Query per admin/utenti normali (tutti gli accessi)
            cursor.execute("""
                SELECT *, DATE_ADD(Created_At, INTERVAL 2 HOUR) AS Created_At_Adjusted 
                FROM Access_Events 
                WHERE Status = 'autorizzato'
                ORDER BY Created_At_Adjusted DESC
            """)
            authorized_accesses = cursor.fetchall()
            
            # Query per admin/utenti normali (tutti gli accessi negati)
            cursor.execute("""
                SELECT *, DATE_ADD(Created_At, INTERVAL 2 HOUR) AS Created_At_Adjusted 
                FROM Access_Events 
                WHERE Status = 'negato'
                ORDER BY Created_At_Adjusted DESC
            """)
            denied_accesses = cursor.fetchall()

        return render_template("suspicious_logins.html", 
                            authorized_accesses=authorized_accesses,
                            denied_accesses=denied_accesses)
    finally:
        cursor.close()
        conn.close()

# --- Funzione per la gestione delle anomalie ---
# Questa funzione mostra le anomalie nei log
@app.route("/anomalies")
@login_required
@role_required("admin")
def anomalies():
    conn = create_logsdb_connection()
    if not conn:
        flash("Database connection error", "danger")
        return redirect(url_for("auth.login"))

    try:
        log_event("success", "Accesso ad Anomalie", "Navigazione", current_user.id)
        cursor = conn.cursor(dictionary=True)
        # Query per admin/utenti normali (tutti i log)
        cursor.execute("""
            SELECT * 
            FROM Success 
            ORDER BY Date_Time DESC
        """)
        success_logs = cursor.fetchall()
        
        cursor.execute("""
            SELECT * 
            FROM Warnings 
            ORDER BY Date_Time DESC
        """)
        warning_logs = cursor.fetchall()
        
        cursor.execute("""
            SELECT * 
            FROM Errors 
            ORDER BY Date_Time DESC
        """)
        error_logs = cursor.fetchall()
        
        return render_template("anomalies.html", 
                             success_logs=success_logs,
                             warning_logs=warning_logs,
                             error_logs=error_logs)
    finally:
        cursor.close()
        conn.close()

# --- Funzione per il download dei log ---
# Questa funzione permette di scaricare i log in formato CSV
@app.route("/scarica_logs", methods=["GET"])
@login_required
@role_required("admin")
def scarica_logs():
    conn = create_usersdb_connection()
    if not conn:
        flash("Errore di connessione al database", "danger")
        return redirect(url_for("dashboard"))

    try:
        log_event("success", "Download logs", "esportazione", current_user.id)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                u.Username, 
                ua.Status, 
                ua.Created_At, 
                b.Nation, 
                b.Location, 
                b.Location_Name
            FROM User_Accesses ua
            JOIN Badges b ON ua.Badge_Id = b.Id
            JOIN Users u ON b.User_Id = u.Id
            ORDER BY ua.Created_At DESC
        """
        )
        accessi = cursor.fetchall()

        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["Utente", "Stato", "Nazione", "Paese", "Luogo", "Data"])

        for row in accessi:
            writer.writerow(
                [
                    row["Username"],
                    row["Status"],
                    row["Nation"],
                    row["Location"],
                    row["Location_Name"],
                    row["Created_At"].strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        output.seek(0)
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"access_logs_{current_time}.csv"

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        log_event(
            "error", f"Errore download logs: {str(e)}", "esportazione", current_user.id
        )
        flash(f"Errore durante la generazione del file: {str(e)}", "danger")
        return redirect(url_for("dashboard"))
    finally:
        cursor.close()
        conn.close()

# --- Funzione per il logout ---
# Questa funzione gestisce il logout dell'utente
@app.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        log_event("success", "Logout", "Autenticazione", current_user.id)
    session.clear()
    return redirect(url_for("auth.login"))

# --- Funzione per l'eliminazione degli utenti ---
# Questa funzione elimina un utente dal database
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@role_required("admin")
def delete_user(user_id):
    try:
        conn = create_usersdb_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Users WHERE Id = %s", (user_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Utente non trovato'}), 404
        
        # Elimina anche la foto associata nell'altro server
        UPLOAD_FOLDER = os.path.join(os.getcwd(), "output/")
        instruction_path = os.path.join(UPLOAD_FOLDER, "instruction.txt")
        filename = f"{user_id}.jpg"
        with open(instruction_path, "w") as f:
            f.write(f"delete {filename}\n")
        return jsonify({'success': True, 'message': 'Utente eliminato con successo'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Errore del server: {str(e)}'}), 500

    finally:
        cursor.close()
        conn.close()

# --- Funzione per l'aggiornamento degli utenti ---
# Questa funzione aggiorna le informazioni di un utente
@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT'])
@login_required
@role_required("admin")
def update_user(user_id):
    conn = create_usersdb_connection()
    cursor = conn.cursor(dictionary=True)

    # "seleziona" l'utente
    if request.method == 'GET':
        cursor.execute("""
            SELECT Username, Email, Role FROM Users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()

        if user:
            return jsonify({
                "username": user["Username"],
                "role": user["Role"],
            })
        return jsonify({"error": "User not found"}), 404
    
    # "aggiorna" l'utente
    elif request.method == 'PUT':
        cursor.execute("""
            SELECT Username, Email, Role FROM Users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        data = request.get_json()
        username = data["username"]
        role = data["role"]
        generate_password = str(data.get("password")).lower() in ["1", "true", "on"]

        update_fields = ["Username = %s", "Role = %s"]
        update_values = [username, role]

        generate_password = data.get("password", False)
       
        # Se l'utente ha selezionato di generare una nuova password
        # Genera una nuova password e la invia all'email dell'utente
        if generate_password:
            new_pass = generate_secure_password()
            salt = os.urandom(32)
            hashed = hash_password(new_pass, salt, PEPPER)
            update_fields += ["Password = %s", "Salt = %s"]
            update_values += [hashed, salt.hex()]
            send_password_email(aes_ecb_decrypt(user["Email"]), new_pass)

        update_values.append(user_id)
        cursor.execute(
            f"UPDATE Users SET {', '.join(update_fields)} WHERE id = %s",
            tuple(update_values)
        )

        conn.commit()
        return jsonify({"success": True})

# Registra il blueprint
app.register_blueprint(auth)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)