import time
import logging
from db import create_usersdb_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('UAWatcher')

# Funzione per eliminare gli accessi scaduti
# (più di 12 mesi)
def cleanup_expired_user_accesses():
    """Elimina gli accessi dopo 12 mesi"""
    conn = None
    try:
        conn = create_usersdb_connection()
        if not conn:
            logger.error("Database connection failed")
            return False

        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM User_Accesses 
                WHERE Created_At < NOW() - INTERVAL 12 MONTH
            """)
            deleted = cursor.rowcount
            conn.commit()
            
        if deleted > 0:
            logger.info(f"Deleted {deleted} expired User_Accesses")
        return True
        
    except Exception as e:
        logger.error(f"Accesses cleanup error: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

# Funzione per avviare il watcher in background
def start_user_accesses_watcher():
    """Avvia il watcher in background"""
    logger.info("Starting User_Accesses watcher...")
    while True:
        cleanup_expired_user_accesses()
        time.sleep(60)