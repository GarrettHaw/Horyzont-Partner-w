# =============================================================================
# HORYZONT PARTNERÓW - RASPBERRY PI DEPLOYMENT GUIDE
# =============================================================================

## 📦 ZAWARTOŚĆ PAKIETU

1. **setup_pi.sh** - Główny skrypt instalacyjny
2. **setup_cloudflare.sh** - Konfiguracja dostępu z zewnątrz
3. **backup.sh** - Skrypt kopii zapasowej
4. **requirements.txt** - Lista pakietów Python
5. **README_RASPBERRY_PI.md** - Ten plik

---

## 🚀 INSTALACJA KROK PO KROKU

### ETAP 1: Przygotowanie Raspberry Pi

#### 1. Zainstaluj system operacyjny
- Pobierz **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
- Wybierz: **Raspberry Pi OS Lite (64-bit)**
- Podczas instalacji:
  - ✅ Włącz SSH
  - ✅ Ustaw nazwę użytkownika i hasło
  - ✅ Skonfiguruj WiFi (jeśli używasz)
- Wgraj system na kartę microSD i włóż do Pi

#### 2. Pierwsze uruchomienie
```bash
# Z Windows PowerShell, znajdź IP Raspberry Pi:
# (lub sprawdź w routerze)
arp -a | findstr b8-27-eb

# Połącz się przez SSH:
ssh pi@192.168.x.x
# (zmień IP na swoje, hasło: to co ustawiłeś w Imager)
```

---

### ETAP 2: Przeniesienie plików na Raspberry Pi

#### Opcja A: SCP (z Windows)
```powershell
# Z PowerShell w katalogu projektu:
scp -r * pi@192.168.x.x:/home/pi/horyzont_temp/
```

#### Opcja B: Git (ZALECANE)
```bash
# Na Raspberry Pi:
git clone https://github.com/twoj-uzytkownik/horyzont.git
cd horyzont

# Lub jeśli używasz prywatnego repo:
git clone https://twoj-token@github.com/twoj-uzytkownik/horyzont.git
```

#### Opcja C: USB Pendrive
```bash
# Włóż pendrive do Pi, zamontuj:
sudo mount /dev/sda1 /mnt
cp -r /mnt/horyzont/* ~/horyzont/
sudo umount /mnt
```

---

### ETAP 3: Uruchomienie instalacji

```bash
# Przejdź do katalogu:
cd ~/horyzont

# Nadaj uprawnienia wykonywania:
chmod +x setup_pi.sh setup_cloudflare.sh backup.sh

# URUCHOM INSTALACJĘ:
bash setup_pi.sh
```

**Instalacja zajmie 10-20 minut**. Skrypt automatycznie:
- Zaktualizuje system
- Zainstaluje wszystkie zależności
- Skonfiguruje Python virtual environment
- Zainstaluje pakiety Python
- Utworzy systemd service (auto-start)
- Skonfiguruje Nginx (opcjonalnie)
- Skonfiguruje firewall (opcjonalnie)

---

### ETAP 4: Konfiguracja kluczy API

```bash
# Utwórz plik .env:
nano ~/horyzont/.env
```

Dodaj swoje klucze:
```
GEMINI_API_KEY=twoj_klucz_gemini
OPENAI_API_KEY=twoj_klucz_openai
ANTHROPIC_API_KEY=twoj_klucz_anthropic
TRADING212_API_KEY=twoj_klucz_trading212
```

Zapisz: `Ctrl+O`, `Enter`, wyjdź: `Ctrl+X`

**ALTERNATYWNIE** - edytuj `streamlit_app.py` i wklej klucze bezpośrednio.

---

### ETAP 5: Uruchomienie aplikacji

```bash
# Uruchom service:
sudo systemctl start horyzont

# Sprawdź status:
sudo systemctl status horyzont

# Zobacz logi:
sudo journalctl -u horyzont -f
```

**Jeśli wszystko działa:**
```bash
# Włącz auto-start:
sudo systemctl enable horyzont
```

---

### ETAP 6: Test dostępu lokalnego

```bash
# Znajdź IP Raspberry Pi:
hostname -I

# W przeglądarce na Windows otwórz:
# http://TWOJE_PI_IP:8501
# Przykład: http://192.168.1.100:8501
```

✅ Powinieneś zobaczyć aplikację Horyzont Partnerów!

---

### ETAP 7: Konfiguracja dostępu z zewnątrz (Cloudflare Tunnel)

```bash
# Uruchom skrypt:
bash setup_cloudflare.sh
```

Skrypt:
1. Zainstaluje cloudflared
2. Zaloguje Cię do Cloudflare (otworzy przeglądarkę)
3. Utworzy tunel
4. Skonfiguruje DNS (jeśli masz domenę)
5. Uruchomi tunel jako service

**Po zakończeniu dostaniesz URL typu:**
- Z domeną: `https://horyzont.twojadomena.com`
- Bez domeny: `https://xyz.trycloudflare.com`

✅ Teraz możesz wchodzić na aplikację z DOWOLNEGO miejsca!

---

### ETAP 8: Konfiguracja automatycznych backupów (OPCJONALNIE)

```bash
# Test backupu:
bash backup.sh

# Dodaj do crontab (backup codziennie o 2:00):
crontab -e

# Dodaj linię:
0 2 * * * /home/pi/horyzont/backup.sh

# Backupy będą w: ~/horyzont_backups/
```

---

## 🔧 ZARZĄDZANIE APLIKACJĄ

### Przydatne komendy:

```bash
# Restart aplikacji
sudo systemctl restart horyzont

# Zatrzymaj aplikację
sudo systemctl stop horyzont

# Uruchom aplikację
sudo systemctl start horyzont

# Status aplikacji
sudo systemctl status horyzont

# Logi na żywo
sudo journalctl -u horyzont -f

# Logi ostatnie 100 linii
sudo journalctl -u horyzont -n 100

# Wyłącz auto-start
sudo systemctl disable horyzont

# Restart tunelu Cloudflare
sudo systemctl restart cloudflared

# Status tunelu
sudo systemctl status cloudflared
```

### Aktualizacja kodu:

```bash
cd ~/horyzont

# Jeśli używasz Git:
git pull

# Restart aplikacji:
sudo systemctl restart horyzont
```

### Przywracanie z backupu:

```bash
cd ~/horyzont_backups

# Lista backupów:
ls -lh

# Rozpakuj backup:
tar -xzf horyzont_backup_YYYYMMDD_HHMMSS.tar.gz -C ~/horyzont_restored/

# Skopiuj pliki:
cp -r ~/horyzont_restored/* ~/horyzont/

# Restart:
sudo systemctl restart horyzont
```

---

## 🐛 ROZWIĄZYWANIE PROBLEMÓW

### Aplikacja nie startuje:

```bash
# Zobacz logi:
sudo journalctl -u horyzont -n 100

# Sprawdź czy Python działa:
cd ~/horyzont
source venv/bin/activate
python streamlit_app.py

# Sprawdź czy wszystkie pliki są na miejscu:
ls -la ~/horyzont/
```

### Cloudflare Tunnel nie działa:

```bash
# Sprawdź status:
sudo systemctl status cloudflared

# Logi tunelu:
sudo journalctl -u cloudflared -n 50

# Restart tunelu:
sudo systemctl restart cloudflared
```

### Błąd "Module not found":

```bash
cd ~/horyzont
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart horyzont
```

### Aplikacja wolna:

```bash
# Sprawdź RAM:
free -h

# Sprawdź CPU:
htop

# Jeśli brakuje RAM, zamknij inne procesy
# Lub zwiększ swap:
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Zmień CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 📊 MONITORING

### Sprawdzanie zdrowia systemu:

```bash
# Temperatura CPU:
vcgencmd measure_temp

# Użycie RAM:
free -h

# Użycie dysku:
df -h

# Load average:
uptime

# Top procesy:
htop
```

### Automatyczne powiadomienia o błędach (OPCJONALNIE):

```bash
# Dodaj do crontaba skrypt sprawdzający:
*/15 * * * * systemctl is-active --quiet horyzont || echo "Horyzont down!" | mail -s "Alert" twoj@email.com
```

---

## 🔐 BEZPIECZEŃSTWO

### Podstawowe zabezpieczenia:

```bash
# 1. Zmień domyślne hasło:
passwd

# 2. Aktualizuj system regularnie:
sudo apt update && sudo apt upgrade -y

# 3. Firewall (jeśli nie zrobiłeś w setup_pi.sh):
sudo apt install ufw
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 4. Fail2ban (ochrona SSH):
sudo apt install fail2ban
sudo systemctl enable fail2ban

# 5. Wyłącz root login przez SSH:
sudo nano /etc/ssh/sshd_config
# Ustaw: PermitRootLogin no
sudo systemctl restart ssh
```

### Backup credentials:

```bash
# Skopiuj credentials.json w bezpieczne miejsce:
cp ~/horyzont/credentials.json ~/credentials_backup.json

# Lub wyślij do siebie emailem
```

---

## 📈 OPTYMALIZACJA WYDAJNOŚCI

### Dla Raspberry Pi 5 8GB:

```bash
# 1. Overclock (OPCJONALNIE, ryzykowne):
sudo nano /boot/config.txt
# Dodaj:
# over_voltage=6
# arm_freq=2600

# 2. GPU Memory (zmniejsz jeśli nie używasz GUI):
sudo raspi-config
# Advanced Options → Memory Split → 16

# 3. Disable unused services:
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# 4. Streamlit optimization:
nano ~/horyzont/.streamlit/config.toml
# Dodaj:
[server]
maxUploadSize = 200
enableXsrfProtection = false
enableCORS = false
```

---

## 🎓 DODATKOWE ZASOBY

- **Raspberry Pi Documentation**: https://www.raspberrypi.com/documentation/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Cloudflare Tunnel Docs**: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **systemd Tutorial**: https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units

---

## 📞 WSPARCIE

Jeśli napotkasz problemy:

1. Sprawdź logi: `sudo journalctl -u horyzont -n 100`
2. Sprawdź sekcję "Rozwiązywanie problemów" powyżej
3. Zrestartuj system: `sudo reboot`
4. Przywróć z backupu

---

## ✅ CHECKLIST INSTALACJI

- [ ] System operacyjny zainstalowany
- [ ] SSH skonfigurowany
- [ ] Pliki projektu przeniesione
- [ ] setup_pi.sh wykonany pomyślnie
- [ ] Klucze API skonfigurowane
- [ ] Service uruchomiony (`sudo systemctl status horyzont`)
- [ ] Dostęp lokalny działa (http://PI_IP:8501)
- [ ] Cloudflare Tunnel skonfigurowany (opcjonalnie)
- [ ] Dostęp zewnętrzny działa (opcjonalnie)
- [ ] Auto-start włączony (`sudo systemctl enable horyzont`)
- [ ] Pierwszy backup wykonany (`bash backup.sh`)
- [ ] Firewall skonfigurowany

---

## 🎉 GRATULACJE!

Twoja aplikacja **Horyzont Partnerów** działa teraz 24/7 na Raspberry Pi!

**Możesz:**
- ✅ Korzystać z aplikacji w domu
- ✅ Korzystać z dowolnego miejsca (Cloudflare Tunnel)
- ✅ Mieć pewność że dane są bezpieczne lokalnie
- ✅ Trading212 API działa bez problemu
- ✅ Automatyczne backupy chronią Twoje dane

**Enjoy!** 🚀
