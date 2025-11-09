#!/bin/bash
# =============================================================================
# CLOUDFLARE TUNNEL SETUP - Bezpieczny dostęp z zewnątrz
# =============================================================================
# Uruchom: bash setup_cloudflare.sh
# =============================================================================

set -e

echo "☁️  =========================================="
echo "☁️   CLOUDFLARE TUNNEL SETUP"
echo "☁️  =========================================="
echo ""

# Kolory
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# =============================================================================
# KROK 1: Instalacja cloudflared
# =============================================================================
print_step "Instalacja cloudflared..."

# Wykryj architekturę
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
elif [ "$ARCH" = "armv7l" ]; then
    CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
else
    print_warning "Nieznana architektura: $ARCH, próbuję arm64..."
    CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
fi

wget -O cloudflared $CLOUDFLARED_URL
sudo mv cloudflared /usr/local/bin/
sudo chmod +x /usr/local/bin/cloudflared

print_success "cloudflared zainstalowany"

# =============================================================================
# KROK 2: Logowanie do Cloudflare
# =============================================================================
print_step "Logowanie do Cloudflare..."

cat <<EOF

📝 INSTRUKCJE:

1. W przeglądarce otworzy się strona Cloudflare
2. Zaloguj się swoim kontem Cloudflare (lub utwórz darmowe)
3. Autoryzuj cloudflared
4. Zamknij przeglądarkę i wróć tutaj

Gotowy? Naciśnij Enter aby kontynuować...
EOF

read

cloudflared tunnel login

print_success "Zalogowano do Cloudflare"

# =============================================================================
# KROK 3: Utworzenie tunelu
# =============================================================================
print_step "Tworzenie tunelu..."

read -p "Podaj nazwę tunelu (np. 'horyzont'): " TUNNEL_NAME
TUNNEL_NAME=${TUNNEL_NAME:-horyzont}

cloudflared tunnel create $TUNNEL_NAME

print_success "Tunel utworzony: $TUNNEL_NAME"

# =============================================================================
# KROK 4: Konfiguracja tunelu
# =============================================================================
print_step "Konfiguracja tunelu..."

TUNNEL_ID=$(cloudflared tunnel list | grep $TUNNEL_NAME | awk '{print $1}')

mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml <<EOF
tunnel: $TUNNEL_ID
credentials-file: /home/$USER/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: $TUNNEL_NAME.yourdomain.com
    service: http://localhost:8501
  - service: http_status:404
EOF

print_success "Konfiguracja zapisana"

# =============================================================================
# KROK 5: Routing DNS
# =============================================================================
print_step "Konfiguracja DNS..."

cat <<EOF

🌐 OPCJE DNS:

1️⃣  Jeśli masz WŁASNĄ DOMENĘ:
   cloudflared tunnel route dns $TUNNEL_NAME horyzont.twojadomena.com
   
2️⃣  Jeśli NIE MASZ domeny:
   Użyj darmowego URL: https://twoj-tunel.trycloudflare.com
   (będzie wygenerowany przy pierwszym uruchomieniu)

Czy masz własną domenę? (y/n): 
EOF

read -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Podaj domenę (np. horyzont.mojadomena.com): " DOMAIN
    cloudflared tunnel route dns $TUNNEL_NAME $DOMAIN
    print_success "DNS skonfigurowany: https://$DOMAIN"
    TUNNEL_URL="https://$DOMAIN"
else
    print_warning "Użyjesz darmowego URL .trycloudflare.com"
    TUNNEL_URL="https://[będzie wygenerowany przy starcie]"
fi

# =============================================================================
# KROK 6: Systemd service dla tunelu
# =============================================================================
print_step "Konfiguracja auto-startu tunelu..."

sudo cloudflared service install

print_success "Tunel będzie uruchamiany automatycznie przy starcie systemu"

# =============================================================================
# KROK 7: Uruchomienie tunelu
# =============================================================================
print_step "Uruchamianie tunelu..."

sudo systemctl start cloudflared
sudo systemctl enable cloudflared

print_success "Tunel uruchomiony!"

# =============================================================================
# PODSUMOWANIE
# =============================================================================

cat <<EOF

🎉 ========================================
🎉  CLOUDFLARE TUNNEL SKONFIGUROWANY!
🎉 ========================================

📋 INFORMACJE:

Nazwa tunelu: $TUNNEL_NAME
Tunnel ID: $TUNNEL_ID
URL: $TUNNEL_URL

🔧 PRZYDATNE KOMENDY:

# Status tunelu
sudo systemctl status cloudflared

# Restart tunelu
sudo systemctl restart cloudflared

# Logi tunelu
sudo journalctl -u cloudflared -f

# Lista tuneli
cloudflared tunnel list

# Info o tunelu
cloudflared tunnel info $TUNNEL_NAME

🌐 DOSTĘP:

Twoja aplikacja jest teraz dostępna z DOWOLNEGO miejsca na świecie:
$TUNNEL_URL

✅ HTTPS automatycznie skonfigurowany
✅ Certyfikat SSL od Cloudflare
✅ Żaden port nie jest otwarty w routerze
✅ DDoS protection
✅ 100% darmowe

📱 MOŻESZ TERAZ:
- Otworzyć aplikację na telefonie (poza domem)
- Udostępnić link znajomym
- Korzystać z dowolnego miejsca na świecie

EOF

print_success "Setup Cloudflare zakończony!"

# Zapisz info
cat > ~/cloudflare_info.txt <<EOF
Cloudflare Tunnel Info
======================
Tunnel Name: $TUNNEL_NAME
Tunnel ID: $TUNNEL_ID
URL: $TUNNEL_URL
Config: ~/.cloudflared/config.yml
Credentials: ~/.cloudflared/$TUNNEL_ID.json

Created: $(date)
EOF

print_success "Info zapisane: ~/cloudflare_info.txt"
