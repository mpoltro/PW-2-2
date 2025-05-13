import mysql.connector
from mysql.connector import Error
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Funzione per creare una connessione al database UsersDB
def create_usersdb_connection():
    try:
        connection = mysql.connector.connect(
            host='db',
            user='flaskuser',
            password='flaskpass',
            database='usersdb',
        )
        return connection
    except Error as e:
        logger.error(f"Errore durante la connessione a UsersDB: {e}")
        return None

# Funzione per creare una connessione al database LogsDB
def create_logsdb_connection():
    try:
        connection = mysql.connector.connect(
            host='db1',
            user='flaskuser',
            password='flaskpass',
            database='logsdb',
        )
        return connection
    except Error as e:
        logger.error(f"Errore durante la connessione a LogsDB: {e}")
        return None
