#!/bin/bash
# =============================================================================
# HORYZONT PARTNERÓW - RASPBERRY PI 5 SETUP SCRIPT
# =============================================================================
# Ten skrypt automatycznie instaluje i konfiguruje całe środowisko
# Uruchom: bash setup_pi.sh
# =============================================================================

set -e  # Zatrzymaj przy błędzie

echo "🍓 =========================================="
echo "🍓  HORYZONT PARTNERÓW - RASPBERRY PI SETUP"
echo "🍓 =========================================="
echo ""

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# =============================================================================
# KROK 1: Sprawdzenie systemu
# =============================================================================
print_step "Krok 1/10: Sprawdzanie systemu..."

# Sprawdź czy to Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "To nie wygląda na Raspberry Pi, ale kontynuuję..."
fi

# Sprawdź RAM
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM" -lt 4 ]; then
    print_warning "Masz mniej niż 4GB RAM. Aplikacja może być wolna."
else
    print_success "RAM: ${TOTAL_RAM}GB - wystarczająco!"
fi

# Sprawdź wolne miejsce
FREE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$FREE_SPACE" -lt 10 ]; then
    print_error "Za mało wolnego miejsca (${FREE_SPACE}GB). Potrzeba min. 10GB."
    exit 1
else
    print_success "Wolne miejsce: ${FREE_SPACE}GB"
fi

# =============================================================================
# KROK 2: Aktualizacja systemu
# =============================================================================
print_step "Krok 2/10: Aktualizacja systemu..."
sudo apt update
sudo apt upgrade -y
print_success "System zaktualizowany"

# =============================================================================
# KROK 3: Instalacja zależności systemowych
# =============================================================================
print_step "Krok 3/10: Instalacja zależności..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    nginx \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    libatlas-base-dev

print_success "Zależności zainstalowane"

# =============================================================================
# KROK 4: Utworzenie katalogu projektu
# =============================================================================
print_step "Krok 4/10: Tworzenie katalogu projektu..."

PROJECT_DIR="$HOME/horyzont"
if [ -d "$PROJECT_DIR" ]; then
    print_warning "Katalog $PROJECT_DIR już istnieje"
    read -p "Czy chcesz go usunąć i utworzyć na nowo? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
        print_success "Stary katalog usunięty"
    else
        print_error "Anulowano. Usuń ręcznie katalog i uruchom ponownie."
        exit 1
    fi
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
print_success "Katalog projektu utworzony: $PROJECT_DIR"

# =============================================================================
# KROK 5: Python Virtual Environment
# =============================================================================
print_step "Krok 5/10: Tworzenie środowiska Python..."

python3 -m venv venv
source venv/bin/activate

print_success "Virtual environment utworzony"

# =============================================================================
# KROK 6: Instalacja pakietów Python
# =============================================================================
print_step "Krok 6/10: Instalacja pakietów Python (to może chwilę potrwać)..."

# Upgrade pip
pip install --upgrade pip

# Instalacja z requirements.txt (jeśli istnieje)
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    print_warning "Brak requirements.txt, instaluję pakiety ręcznie..."
    pip install streamlit pandas numpy plotly requests scipy \
                google-api-python-client google-auth-httplib2 google-auth-oauthlib \
                anthropic google-generativeai openai yfinance pytz python-dateutil
fi

print_success "Pakiety Python zainstalowane"

# =============================================================================
# KROK 7: Konfiguracja Systemd Service
# =============================================================================
print_step "Krok 7/10: Konfiguracja auto-startu (systemd)..."

SERVICE_FILE="/etc/systemd/system/horyzont.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Horyzont Partnerów - Streamlit Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable horyzont.service

print_success "Systemd service skonfigurowany"
print_warning "Service zostanie uruchomiony po skopiowaniu plików projektu"

# =============================================================================
# KROK 8: Konfiguracja Nginx (opcjonalna)
# =============================================================================
print_step "Krok 8/10: Konfiguracja Nginx reverse proxy..."

read -p "Czy chcesz skonfigurować Nginx? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    NGINX_CONF="/etc/nginx/sites-available/horyzont"
    
    sudo tee $NGINX_CONF > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
EOF

    sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl restart nginx
    
    print_success "Nginx skonfigurowany (port 80 → 8501)"
else
    print_warning "Nginx pominięty. Dostęp bezpośrednio na porcie 8501"
fi

# =============================================================================
# KROK 9: Konfiguracja firewalla (opcjonalna)
# =============================================================================
print_step "Krok 9/10: Konfiguracja firewalla..."

read -p "Czy chcesz skonfigurować firewall (ufw)? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt install -y ufw
    sudo ufw allow 22/tcp    # SSH
    sudo ufw allow 80/tcp    # HTTP
    sudo ufw allow 443/tcp   # HTTPS
    echo "y" | sudo ufw enable
    
    print_success "Firewall skonfigurowany (SSH, HTTP, HTTPS)"
else
    print_warning "Firewall pominięty"
fi

# =============================================================================
# KROK 10: Instrukcje końcowe
# =============================================================================
print_step "Krok 10/10: Finalizacja..."

cat <<EOF

🎉 ========================================
🎉  INSTALACJA ZAKOŃCZONA!
🎉 ========================================

📋 CO TERAZ ZROBIĆ:

1️⃣  SKOPIUJ PLIKI PROJEKTU:
   Przenieś wszystkie pliki z Windows do:
   $PROJECT_DIR
   
   Możesz użyć:
   - scp (z Windows): scp -r "C:\Users\alech\Desktop\Horyzont Partnerów\*" $USER@raspberry-pi-ip:$PROJECT_DIR/
   - Git: push do repo → pull na Pi
   - USB: skopiuj na pendrive → wklej na Pi

2️⃣  UPEWNIJ SIĘ ŻE MASZ:
   ✅ streamlit_app.py
   ✅ gra_rpg.py
   ✅ persona_memory_manager.py
   ✅ finalna_konfiguracja_person.txt
   ✅ kodeks_spolki.txt
   ✅ credentials.json (Google Sheets)
   ✅ Wszystkie pliki JSON (cele.json, krypto.json, etc.)
   ✅ Wszystkie foldery (partner_memories/, knowledge_base/, etc.)

3️⃣  DODAJ KLUCZE API:
   Utwórz plik: $PROJECT_DIR/.env
   I dodaj swoje klucze:
   
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   TRADING212_API_KEY=your_key_here

4️⃣  URUCHOM APLIKACJĘ:
   sudo systemctl start horyzont
   sudo systemctl status horyzont

5️⃣  SPRAWDŹ LOGI:
   sudo journalctl -u horyzont -f

6️⃣  DOSTĘP:
   - W sieci lokalnej: http://$(hostname -I | awk '{print $1}'):8501
   - Przez Nginx: http://$(hostname -I | awk '{print $1}')

📚 PRZYDATNE KOMENDY:

   # Restart aplikacji
   sudo systemctl restart horyzont
   
   # Zatrzymaj aplikację
   sudo systemctl stop horyzont
   
   # Wyłącz auto-start
   sudo systemctl disable horyzont
   
   # Zobacz logi
   sudo journalctl -u horyzont -n 100

🌐 CLOUDFLARE TUNNEL (dostęp z zewnątrz):
   Uruchom skrypt: bash setup_cloudflare.sh
   (będzie utworzony w następnym kroku)

📦 BACKUP:
   Uruchom skrypt: bash backup.sh
   (będzie utworzony w następnym kroku)

EOF

print_success "Setup zakończony pomyślnie!"
print_warning "WAŻNE: Pamiętaj o skopiowaniu plików projektu!"

# Utworzenie skryptu info
cat > "$PROJECT_DIR/INFO.txt" <<EOF
Horyzont Partnerów - Raspberry Pi Installation
===============================================

Data instalacji: $(date)
Katalog projektu: $PROJECT_DIR
Python venv: $PROJECT_DIR/venv
Service: horyzont.service

Komendy:
--------
Start:   sudo systemctl start horyzont
Stop:    sudo systemctl stop horyzont
Restart: sudo systemctl restart horyzont
Status:  sudo systemctl status horyzont
Logi:    sudo journalctl -u horyzont -f

Dostęp lokalny: http://$(hostname -I | awk '{print $1}'):8501
EOF

print_success "Zapisano: $PROJECT_DIR/INFO.txt"
