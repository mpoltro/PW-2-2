#!/bin/sh

# Variabili d'ambiente
HOST=$MYSQL_HOST
USER=$MYSQL_USER
PASS=$MYSQL_PASSWORD
DB1=$MYSQL_DB1
DB2=$MYSQL_DB2

# Funzione di controllo singolo DB
check_db() {
  DB_NAME=$1
  until mysql -h "$HOST" -u "$USER" -p"$PASS" -e "USE $DB_NAME"; do
    echo "In attesa che MySQL sia pronto per il database '$DB_NAME'..."
    sleep 5
  done
  echo "✅ Connessione al database '$DB_NAME' riuscita."
}

# Controlla entrambi i database
check_db "$DB1"
check_db "$DB2"

# Una volta che MySQL è pronto per entrambi i DB, esegue l'app
exec "$@"
