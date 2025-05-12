## Prerequisiti

  

  

  

-  **Python**: 3.10.12

  

  

  

-  **Pip**: 22.0.2

  

  

  

## Installazione

  

  

  

### Installare `pip` su Ubuntu

  

  

  

Se non hai `pip` e stai usando Ubuntu, puoi installarlo utilizzando lo script `get-pip.py`.

  

  

  

#### Passaggi:

  

  

  

1.  **Scarica lo script `get-pip.py`:**

  

  

Prima, devi scaricare il file `get-pip.py`. Puoi farlo utilizzando `curl` o `wget`:

  

  

  

- Con `curl`:

  

  

```bash
curl  https://bootstrap.pypa.io/get-pip.py  -o  get-pip.py
```

  

  

  

- Con `wget`:
  
```bash
wget  https://bootstrap.pypa.io/get-pip.py
```

  

  

  

2.  **Installa `pip` eseguendo il file `get-pip.py`:**

  

  

Una volta scaricato il file, esegui il comando per installare `pip`:

  

  

  

Python 3.x:

  

  

```bash
python3  get-pip.py
```

  

  

  

Se necessario, puoi anche usare `sudo` su Ubuntu per avere i permessi di amministratore:

  

  

  

```bash
sudo  python3  get-pip.py
```

  

  

  

#### Verifica l'installazione di `pip`:

  

  

  

Dopo l'installazione, puoi verificare che `pip` sia stato correttamente installato con il comando:

  

  

  

```bash
pip  --version
```

  

## Creare un ambiente virtuale in Python su Ubuntu

  

  

#### Passaggi

  

  

1.  **Installa**  `venv` (se non è già installato) `venv` è il modulo ufficiale di Python per la creazione di ambienti virtuali. Su Ubuntu, `venv` dovrebbe essere già incluso con Python 3. Tuttavia, se non fosse presente, puoi installarlo con:

  

```bash
sudo  apt  install  python3-venv
```

  

  

2.  **Crea l'ambiente virtuale**

  

```bash
python3  -m  venv  venv
```

  

  

3.  **Attiva l'ambiente virtuale**

  

```bash
source  venv/bin/activate
```

  

Una volta attivato, il prompt del terminale cambierà per indicare che sei dentro l'ambiente virtuale. Di solito, mostrerà qualcosa come `(myenv)` prima del prompt.

  

  

## Installare le dipendenze

  

  

1.**Le dipendenze** di un progetto Python sono generalmente elencate in un file chiamato `requirements.txt`. Per installare tutte le dipendenze all'interno dell'ambiente virtuale, usa il comando `pip`:

  

```bash
pip  install  -r  requirements.txt
```

  

  

## Eseguire lo script

  

Una volta installata le librerie ed aver attivato l'ambiente virtuale, puoi eseguire lo script usando il comando Python:

  

  

```bash
python  Slowdoris.py
```

  

Se usi Python 3, e hai entrambi Python 2.x e 3.x installati, potrebbe essere necessario usare:

  

  

```bash
python3  Slowdoris.py
```

  

## Interazione con lo script:

  

Lo script ti chiederà delle informazioni in input. Quando eseguirai lo script, ti verranno chiesti i seguenti dati:

- Indirizzo IP del target: L'indirizzo IP del server web che vuoi attaccare con Slowloris. 
- Porta del target: La porta del server web di destinazione (solitamente 80 per HTTP o 443 per HTTPS). 
```bash 
Inserisci l'indirizzo IP del target: 192.168.1.100 
Inserisci la porta del target (solitamente 80 o 443): 80
```

## Esecuzione dell'attacco Slowloris

Dopo aver inserito l'indirizzo IP e la porta del target, lo script tenterà di eseguire un attacco Slowloris inviando un gran numero di richieste HTTP parziali per cercare di esaurire le risorse del server.

## Osservazioni durante l'esecuzione

Durante l'esecuzione dello script, potresti vedere messaggi che indicano la creazione di nuovi socket e l'invio di intestazioni. L'obiettivo è mantenere queste connessioni attive il più a lungo possibile.

```bash
[+] Attacco in corso su 192.168.1.100:80 con 500 socket... 
[+] Socket 1 creato. 
[+] Intestazione inviata. 
[+] Socket 2 creato. 
[+] Intestazione inviata. 
[+] Socket 3 creato. 
[+] Intestazione inviata. 
... 
[+] Mantendo attivi 2500 socket... 
[+] Ricreazione del socket... 
[+] Intestazione inviata. 
... 
[-] Attacco interrotto dall'utente. 
[*] Chiusura di tutti i socket...
```
