# **DREAM TEAM PROJECT** 💻🌟  

**Il progetto che rivoluziona la gestione degli accessi e alla sala server!**  
Monitora login, gestisci utenti, statistiche e visualizzazioni con dashboard avanzate, grafici dinamici e temi personalizzabili.

---

## **🚀 COME FARE PARTIRE IL PROGETTO**  

### **📋 Prerequisiti**  
Assicurati di avere:  
- **Docker + Docker Compose** ([Guida ufficiale](https://docs.docker.com/get-docker/))
- **Make (opzionale ma consigliato)**

---

### **⚙️ Setup con Docker**  

#### **1. Clona il repository**  
```bash
git clone https://github.com/DreamTeamOrg/dream-team-project.git
cd dream-team-project
```

#### **2. Avvia i container**  
```bash
docker-compose up --build
```
- L'app sarà disponibile su `http://localhost:5000`
- PhpMyAdmin accessibile su `http://localhost:8080` (login: flaskuser / flaskpass)

---

### **🎮 Funzionalità Principali**
- Login e logout con log automatici
- Gestione utenti (admin/user/guest)
- Statistiche accessi: totali, per giorno, per ora
- Dashboard con grafici dinamici (Chart.js)
- Tema chiaro/scuro con toggle
- PhpMyAdmin per visualizzazione DB

---

## 🖼 **Screenshot**  

### **Login Page**

![Screenshot 2025-04-16 173321](https://github.com/user-attachments/assets/f9bf26c2-e3e9-4a17-aff7-416ebd65277a)

##

### **Dashboard**

![Screenshot 2025-04-30 162834](https://github.com/user-attachments/assets/ed23ee77-14fa-4801-8feb-e62b84573be3)
![Screenshot 2025-04-30 162844](https://github.com/user-attachments/assets/89ff2875-29c6-46f3-8ef7-4a13eed582e3)

##

### **Users Page**

![Screenshot 2025-04-30 162905](https://github.com/user-attachments/assets/f1c8afe9-92d8-4221-abae-c43cc042230c)
![Screenshot 2025-04-30 162856](https://github.com/user-attachments/assets/9cbfc781-058e-4aba-beb8-d7b30970bb72)

---

## **🔧 COMANDI UTILI (Docker)**  

| Comando | Descrizione |  
|---------|------------|  
| `docker-compose up` | Avvia il progetto |  
| `docker-compose down` | Ferma i container |  
| `docker-compose logs -f` | Mostra i log live |  
| `docker exec -it nome_container bash` | Entra nel container |  

---

## **🌍 STRUTTURA DEL PROGETTO**
```
dream-team-project/
├── app.py                  # App Flask principale
├── db.py                   # Connessione e inizializzazione MySQL
├── docker-compose.yml      # Configurazione container
├── Dockerfile              # Build dell'immagine Flask
├── wait-for-mysql.sh       # Script di attesa MySQL
├── static/                 # CSS, JS, immagini
├── templates/              # HTML e Jinja2
├── requirements.txt        # Dipendenze
└── README.md               # Questo file 😎
```

---

## **💡 Temi disponibili**  
- `light.css` → Tema chiaro professionale
- `dark.css` → Tema scuro moderno
- Selezionabile dall'interfaccia con toggle

---

## **🤝 COME CONTRIBUIRE**  
1. **Fork** il progetto  
2. Crea un branch: `git checkout -b feature/qualcosa`  
3. Fai commit: `git commit -m "feat: nuova funzione"`  
4. Push: `git push origin feature/qualcosa`  
5. **Apri una Pull Request** 🎉  

---

## **📜 LICENZA**  
MIT License - Open source, libero utilizzo 🙌

---

**💖 Grazie per far parte del DREAM TEAM!**  
*"Insieme, vinciamo ogni sfida... e ogni login!"* 📹💻  

---

### 🔥 **Extra**  
- **Hai problemi?** Apri una [issue](https://github.com/DreamTeamOrg/dream-team-project/issues)  
- **Vuoi suggerimenti o aiuto?** Scrivici su Telegram!  

