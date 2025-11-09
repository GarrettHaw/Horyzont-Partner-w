# 🍓 RASPBERRY PI 5 DEPLOYMENT PACKAGE

## 📦 ZAWARTOŚĆ PAKIETU

Właśnie stworzyłem kompletny package do wdrożenia Twojej aplikacji na Raspberry Pi 5!

### 🔧 Skrypty instalacyjne:
1. **setup_pi.sh** - Główny skrypt instalacyjny (auto-install wszystkiego)
2. **setup_cloudflare.sh** - Konfiguracja dostępu z zewnątrz (Cloudflare Tunnel)
3. **backup.sh** - Automatyczne kopie zapasowe
4. **start.sh** - Szybkie uruchomienie aplikacji
5. **stop.sh** - Zatrzymanie aplikacji

### 📚 Dokumentacja:
1. **README_RASPBERRY_PI.md** - Pełna dokumentacja (100+ linii instrukcji)
2. **FIRST_STEPS.md** - Szybki start (10 minut do działającej aplikacji)
3. **.env.template** - Template dla kluczy API

### 📋 Konfiguracja:
1. **requirements.txt** - Lista wszystkich pakietów Python

---

## 🚀 JAK ZACZĄĆ?

### OPCJA 1: Szybki start (polecane)
Otwórz: **FIRST_STEPS.md** i postępuj krok po kroku (10 minut)

### OPCJA 2: Pełna dokumentacja
Otwórz: **README_RASPBERRY_PI.md** dla szczegółowych instrukcji

---

## 📝 CO ZROBI AUTOMATYCZNY INSTALLER?

**setup_pi.sh** (20 minut):
- ✅ Zaktualizuje system
- ✅ Zainstaluje Python, Nginx, Git
- ✅ Utworzy virtual environment
- ✅ Zainstaluje wszystkie pakiety (streamlit, pandas, numpy, plotly, etc.)
- ✅ Skonfiguruje systemd service (auto-start przy restarcie)
- ✅ Skonfiguruje Nginx reverse proxy (opcjonalnie)
- ✅ Skonfiguruje firewall (opcjonalnie)
- ✅ Wszystko gotowe do działania!

---

## 🌐 CLOUDFLARE TUNNEL - DOSTĘP Z ZEWNĄTRZ

**setup_cloudflare.sh** (10 minut):
- ✅ Instaluje cloudflared
- ✅ Loguje do Cloudflare (darmowe konto)
- ✅ Tworzy tunel
- ✅ Konfiguruje DNS (jeśli masz domenę)
- ✅ Daje URL: `https://twoja-app.trycloudflare.com`
- ✅ 100% bezpieczne (żaden port nie jest otwarty w routerze!)
- ✅ Auto-start przy restarcie Pi

**KORZYŚCI:**
- 🌍 Dostęp z telefonu poza domem
- 🔒 HTTPS automatycznie
- 🛡️ DDoS protection od Cloudflare
- 💰 100% darmowe
- ⚡ Szybkie jak lokalnie

---

## 💾 AUTOMATYCZNE BACKUPY

**backup.sh**:
- Tworzy kopię zapasową całego projektu
- Kompresuje do .tar.gz
- Zachowuje ostatnie 7 backupów
- Można dodać do crontab (codziennie o 2:00)

```bash
# Backup teraz:
bash backup.sh

# Auto-backup codziennie:
crontab -e
# Dodaj: 0 2 * * * ~/horyzont/backup.sh
```

---

## 🎯 WYMAGANIA SPRZĘTOWE

### ✅ ZALECANE (TO MASZ!):
- **Raspberry Pi 5 8GB** - idealny!
- Karta microSD 128GB (min. 64GB)
- Oficjalny zasilacz USB-C 27W
- Obudowa z wentylatorem (chłodzenie)

### 💰 KOSZT:
- Sprzęt: ~$120 jednorazowo
- Energia: ~$3/miesiąc
- **RAZEM: $3/miesiąc** (vs VPS $5-10/mies)

---

## 📊 FUNKCJE

Po instalacji Twoja aplikacja będzie:
- ✅ Działać 24/7 na Raspberry Pi
- ✅ Auto-start przy każdym restarcie
- ✅ Dostępna w sieci lokalnej
- ✅ Dostępna z internetu (Cloudflare Tunnel)
- ✅ Trading212 API działa (Twoje IP!)
- ✅ Wszystkie dane lokalnie (prywatność)
- ✅ Automatyczne backupy
- ✅ Monitoring przez systemd
- ✅ Logi dostępne

---

## 🔐 BEZPIECZEŃSTWO

**Co jest zabezpieczone:**
- ✅ SSH z hasłem
- ✅ Firewall (ufw) - tylko SSH, HTTP, HTTPS
- ✅ Cloudflare Tunnel (zero otwartych portów)
- ✅ HTTPS z certyfikatem SSL
- ✅ Klucze API w pliku .env (nie w repo)
- ✅ credentials.json lokalnie (nie w Git)

---

## 📱 DOSTĘP

### W DOMU:
```
http://192.168.x.x:8501
lub (z Nginx)
http://192.168.x.x
```

### Z ZEWNĄTRZ (po setup Cloudflare):
```
https://horyzont-xyz.trycloudflare.com
lub (jeśli masz domenę)
https://horyzont.twojadomena.com
```

### Z TELEFONU:
- W domu: to samo co powyżej
- Poza domem: URL z Cloudflare

---

## 🛠️ ZARZĄDZANIE

### Podstawowe komendy:
```bash
# Uruchom
sudo systemctl start horyzont

# Zatrzymaj
sudo systemctl stop horyzont

# Restart
sudo systemctl restart horyzont

# Status
sudo systemctl status horyzont

# Logi na żywo
sudo journalctl -u horyzont -f

# Backup
bash backup.sh
```

### Aktualizacja kodu:
```bash
cd ~/horyzont
# Wklej nowe pliki lub:
git pull
# Restart:
sudo systemctl restart horyzont
```

---

## 🆘 WSPARCIE

### Jeśli coś nie działa:

1. **Sprawdź logi:**
   ```bash
   sudo journalctl -u horyzont -n 100
   ```

2. **Test ręczny:**
   ```bash
   cd ~/horyzont
   source venv/bin/activate
   streamlit run streamlit_app.py
   ```

3. **Sprawdź dokumentację:**
   - FIRST_STEPS.md → sekcja "Problemy?"
   - README_RASPBERRY_PI.md → "Rozwiązywanie problemów"

4. **Restart systemu:**
   ```bash
   sudo reboot
   ```

---

## ✅ PODSUMOWANIE

Masz teraz:
- 🎯 Gotowy pakiet instalacyjny
- 📚 Pełną dokumentację
- 🔧 Automatyczne skrypty
- 🌐 Dostęp z internetu (Cloudflare)
- 💾 System backupów
- 🛡️ Zabezpieczenia

**NASTĘPNE KROKI:**
1. Zamów Raspberry Pi 5 8GB + akcesoria
2. Zainstaluj system (Raspberry Pi Imager)
3. Uruchom `bash setup_pi.sh`
4. GOTOWE! ✅

**Czas do działającej aplikacji: 30-40 minut**
(20 min instalacja + 10 min Cloudflare)

---

## 🎉 GRATULACJE!

Masz profesjonalny setup produkcyjny dla swojej aplikacji finansowej!

**Więcej informacji:**
- Pełna docs: README_RASPBERRY_PI.md
- Szybki start: FIRST_STEPS.md
- Support: sprawdź sekcję "Rozwiązywanie problemów"

**Good luck!** 🚀
