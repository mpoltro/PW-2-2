import time
import logging
from db import create_usersdb_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('otp_watcher')

# Funzione per eliminare gli OTP scaduti
# (più di 10 minuti)
def cleanup_expired_otp():
    """Elimina gli OTP scaduti dalla tabella Authenticated"""
    conn = None
    try:
        conn = create_usersdb_connection()
        if not conn:
            logger.error("Database connection failed")
            return False

        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Authenticated 
                WHERE Created_At < NOW() - INTERVAL 10 MINUTE
            """)
            deleted = cursor.rowcount
            conn.commit()
            
        if deleted > 0:
            logger.info(f"Deleted {deleted} expired OTPs")
        return True
        
    except Exception as e:
        logger.error(f"OTP cleanup error: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

# Funzione per avviare il watcher in background
# (ogni 60 secondi)
def start_otp_watcher():
    """Avvia il watcher in background"""
    logger.info("Starting OTP watcher...")
    while True:
        cleanup_expired_otp()
        time.sleep(60)