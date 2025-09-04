
#!/bin/bash
# Automatisches Setup und Start für nfc-kasse mit HTTPS und nginx

set -e


# 1. Docker installieren (falls nicht vorhanden)
if ! command -v docker &> /dev/null; then
    echo "Installiere Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# 2. Nginx und Certbot installieren
echo "Installiere nginx und certbot..."
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# 3. Docker-Image bauen
echo "Baue Docker-Image..."
sudo docker build -t nfc-kasse .

# 4. Container starten (Port 8000)
PORT=8000
sudo docker rm -f nfc-kasse-container 2>/dev/null || true
sudo docker run -d --name nfc-kasse-container -p 8000:8000 nfc-kasse
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
echo "Fordere Let's Encrypt Zertifikat für $DOMAIN an..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN --redirect

# 7. IP-Adresse ermitteln
IP=$(hostname -I | awk '{print $1}')

sleep 2

# 8. Ausgabe der Netzwerkadresse
echo "\nDie Anwendung ist erreichbar unter: https://$DOMAIN (oder https://$IP falls DNS richtig gesetzt)"
echo "(Prozess-ID: $APP_PID)"
