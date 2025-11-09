# 🍓 RASPBERRY PI 5 - PIERWSZE KROKI

## ⚡ SZYBKI START (10 minut)

### 1️⃣ PRZYGOTUJ RASPBERRY PI
```bash
# Połącz się przez SSH:
ssh pi@192.168.x.x
```

### 2️⃣ PRZENIEŚ PLIKI
```bash
# Opcja A - SCP z Windows:
# (w PowerShell na Windows)
scp -r "C:\Users\alech\Desktop\Horyzont Partnerów\*" pi@192.168.x.x:/home/pi/horyzont/

# Opcja B - Git:
git clone https://github.com/twoj-repo/horyzont.git ~/horyzont
```

### 3️⃣ URUCHOM INSTALACJĘ
```bash
cd ~/horyzont
chmod +x *.sh
bash setup_pi.sh
```

**Odpowiedz na pytania** (Nginx: TAK, Firewall: TAK)

### 4️⃣ DODAJ KLUCZE API
```bash
nano ~/horyzont/.env
```

Wklej:
```
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
TRADING212_API_KEY=your_key
```

Zapisz: `Ctrl+O`, `Enter`, `Ctrl+X`

### 5️⃣ URUCHOM APLIKACJĘ
```bash
sudo systemctl start horyzont
sudo systemctl status horyzont
```

### 6️⃣ OTWÓRZ W PRZEGLĄDARCE
```
http://[IP_RASPBERRY_PI]:8501
```

✅ **DZIAŁA!**

---

## 🌍 DOSTĘP Z ZEWNĄTRZ (opcjonalnie)

```bash
bash setup_cloudflare.sh
```

Otrzymasz URL: `https://xyz.trycloudflare.com`

---

## 📱 PRZYDATNE KOMENDY

```bash
# Restart
sudo systemctl restart horyzont

# Logi na żywo
sudo journalctl -u horyzont -f

# Backup
bash backup.sh

# Status
sudo systemctl status horyzont
```

---

## 🆘 PROBLEMY?

Sprawdź: **README_RASPBERRY_PI.md** → sekcja "Rozwiązywanie problemów"

---

## ✅ CHECKLIST

- [ ] Raspberry Pi włączony i połączony z siecią
- [ ] SSH działa
- [ ] Pliki przeniesione
- [ ] setup_pi.sh wykonany
- [ ] Klucze API dodane
- [ ] Service uruchomiony
- [ ] Aplikacja otwarta w przeglądarce

**GOTOWE!** 🎉
