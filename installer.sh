#!/bin/bash
# NFC-Kasse Installer - supports Docker container and native installation
# Configuration variables - modify these as needed

# GLOBAL VARIABLES
installMode="prod"  # Options: "prod" (Docker container) or "dev" (native installation)
TestData="y"        # Options: "y" (yes, install test data) or "n" (no test data)

set -e

echo "=== NFC-Kasse Installer ==="
echo "Install Mode: $installMode"
echo "Test Data: $TestData"
echo "=========================="

if [ "$installMode" = "prod" ]; then
    echo "Starting Docker container installation..."
    
    # 1. Docker installieren (falls nicht vorhanden)
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        sudo apt-get update
        sudo apt-get install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
    else
        echo "Docker is already installed."
    fi

    # 2. Nginx und Certbot installieren
    echo "Installing nginx and certbot..."
    sudo apt-get update
    sudo apt-get install -y nginx certbot python3-certbot-nginx

    # 3. Docker-Image bauen (mit oder ohne Test-Daten)
    echo "Building Docker image..."
    if [ "$TestData" = "y" ]; then
        sudo docker build --build-arg DEFAULT_DATA=yes -t nfc-kasse .
    else
        sudo docker build -t nfc-kasse .
    fi

    # 4. Container starten (Port 5000, wie im Dockerfile definiert)
    PORT=5000
    sudo docker rm -f nfc-kasse-container 2>/dev/null || true
    sudo docker run -d --name nfc-kasse-container -p $PORT:5000 nfc-kasse
    APP_PID=$(sudo docker inspect --format '{{.State.Pid}}' nfc-kasse-container)

    # 5. Nginx als Reverse Proxy konfigurieren
    DOMAIN="nfc-kasse.de"
    NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"
    sudo bash -c "cat > $NGINX_CONF" <<EOL
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL
    sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx

    # 6. Let's Encrypt Zertifikat holen
    echo "Requesting Let's Encrypt certificate for $DOMAIN..."
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN --redirect

    # 7. IP-Adresse ermitteln
    IP=$(hostname -I | awk '{print $1}')

    sleep 2

    # 8. Ausgabe der Netzwerkadresse
    echo ""
    echo "=== DOCKER INSTALLATION COMPLETE ==="
    echo "Application is accessible at: https://$DOMAIN (or https://$IP if DNS is configured correctly)"
    echo "Container Process ID: $APP_PID"
    echo "====================================="

elif [ "$installMode" = "dev" ]; then
    echo "Starting native development installation..."
    
    # 1. Python3 und pip installieren (falls nicht vorhanden)
    if ! command -v python3 &> /dev/null; then
        echo "Installing Python3..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    else
        echo "Python3 is already installed."
    fi

    # 2. Virtual Environment erstellen
    echo "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate

    # 3. Dependencies installieren
    echo "Installing Python dependencies..."
    pip install --no-cache-dir -r requirements.txt

    # 4. Datenbank initialisieren
    echo "Initializing database..."
    python init_db.py

    # 5. Test-Daten hinzufügen (falls gewünscht)
    if [ "$TestData" = "y" ]; then
        echo "Adding test data..."
        python testData.py
    else
        echo "Skipping test data installation."
    fi

    # 6. Permissions für Datenbank setzen
    chmod 664 kasse.db 2>/dev/null || true

    # 7. IP-Adresse ermitteln
    IP=$(hostname -I | awk '{print $1}')

    echo ""
    echo "=== NATIVE INSTALLATION COMPLETE ==="
    echo "To start the application, run:"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload"
    echo ""
    echo "Or use the provided run script:"
    echo "  ./run.sh"
    echo ""
    echo "Application will be accessible at:"
    echo "  http://localhost:5000"
    echo "  http://$IP:5000"
    echo ""
    echo "Database file: kasse.db (you can edit directly with SQLite tools)"
    echo "Code location: $(pwd) (you can edit with Visual Studio Code)"
    echo "====================================="

else
    echo "Error: Invalid installMode '$installMode'. Use 'prod' for Docker or 'dev' for native installation."
    exit 1
fi

echo ""
echo "Installation completed successfully!"