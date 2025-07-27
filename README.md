# NFC Kassensystem mit FastAPI

## Projektstruktur
- `app/` enthält die FastAPI-Anwendung (Backend)
- `app/static/` enthält HTML, CSS und JavaScript (Frontend)
- `app/routers/` enthält die API-Endpunkte
- `app/utils/` enthält Hilfsfunktionen (z.B. Logging)
- `init_db.py` initialisiert die Datenbank
- `testData.py` fügt Demodaten hinzu (optional)
- `requirements.txt` enthält die Python-Abhängigkeiten
- `Dockerfile` für den einfachen Start mit Docker

---

## Schnellstart auf einem neuen Ubuntu-PC

### 1. Docker installieren

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. Projekt von GitHub klonen

```bash
git clone https://github.com/KimSchehl/nfc-kasse.git
cd nfc-kasse
```

### 3. Docker-Image bauen und starten

**Mit Demodaten:**
```bash
docker build --build-arg DEFAULT_DATA=yes -t kasse .
docker run -p 5000:5000 kasse
```

**Ohne Demodaten:**
```bash
docker build -t kasse .
docker run -p 5000:5000 kasse
```

---

## System aufrufen

Öffne im Browser:  
[http://localhost:5000](http://localhost:5000)

---

## Hinweise

- Die Datenbank wird beim ersten Start automatisch angelegt.
- Die Demodaten sind optional und helfen beim Testen.
- Für die Entwicklung kannst du auch das Skript `run.sh` nutzen:
  ```bash
  ./run.sh
  ```
- Die wichtigsten Einstellungen und Benutzerverwaltung findest du im Menü „Einstellungen“ im Webinterface.

---

## Weitere Infos

- `.gitignore` sorgt dafür, dass temporäre Dateien, Datenbanken und virtuelle Umgebungen nicht ins Repository gelangen.
- `requirements.txt` listet alle benötigten Python-Pakete auf. Installiere sie mit:
  ```bash
  pip install -r requirements.txt
  ```
- `Dockerfile` enthält Anweisungen zum Erstellen des Docker-Images.
