# 🚀 Deployment do Streamlit Cloud - Przewodnik

## 📋 Wymagania wstępne
1. Konto GitHub (bezpłatne): https://github.com/join
2. Konto Streamlit Cloud (bezpłatne): https://share.streamlit.io/signup

---

## 📂 KROK 1: Przygotowanie repozytorium GitHub

### Opcja A: Przez GitHub Desktop (łatwiejsza)
1. Pobierz i zainstaluj **GitHub Desktop**: https://desktop.github.com/
2. Uruchom GitHub Desktop i zaloguj się na swoje konto GitHub
3. Kliknij **File → Add Local Repository**
4. Wybierz folder: `C:\Users\Arek Lech\Desktop\Horyzont Partnerów`
5. Jeśli pojawi się błąd "not a git repository", kliknij **Create a repository**
6. Wypełnij:
   - Name: `horyzont-partnerow`
   - Description: `Investment portfolio management dashboard`
   - ✅ Zaznacz "Initialize this repository with a README"
7. Kliknij **Create Repository**
8. W GitHub Desktop zobaczysz listę plików do commit
9. W polu "Summary" wpisz: `Initial commit - Horyzont Partnerów`
10. Kliknij **Commit to main**
11. Kliknij **Publish repository** (górny prawy róg)
12. ⚠️ **WAŻNE**: Odznacz "Keep this code private" TYLKO jeśli nie masz wrażliwych danych
    - Jeśli chcesz publiczne: odznacz
    - Jeśli chcesz prywatne: zostaw zaznaczone (wymaga GitHub Pro lub darmowy dla studentów)
13. Kliknij **Publish Repository**

### Opcja B: Przez Git Command Line
```bash
# Zainstaluj Git: https://git-scm.com/download/win

cd "C:\Users\Arek Lech\Desktop\Horyzont Partnerów"
git init
git add .
git commit -m "Initial commit - Horyzont Partnerów"
git branch -M main
git remote add origin https://github.com/TWOJA-NAZWA/horyzont-partnerow.git
git push -u origin main
```

---

## ☁️ KROK 2: Deployment na Streamlit Cloud

1. **Zaloguj się do Streamlit Cloud**: https://share.streamlit.io/
2. Kliknij **"New app"** (prawy górny róg)
3. Wypełnij formularz:
   - **Repository**: wybierz `TWOJA-NAZWA/horyzont-partnerow`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL** (opcjonalne): wybierz własną nazwę, np. `horyzont-partnerow`
4. Kliknij **"Advanced settings"** (na dole)
5. **Python version**: 3.11
6. Kliknij **"Deploy!"**

⏳ **Deployment potrwa 5-10 minut**. Streamlit Cloud zainstaluje wszystkie zależności.

---

## 🔑 KROK 3: Konfiguracja Secrets (API Keys)

### WAŻNE: Bez tego aplikacja nie będzie działać!

1. Po wdrożeniu, w Streamlit Cloud Dashboard:
2. Znajdź swoją aplikację
3. Kliknij **⚙️ Settings** (ikona koła zębatego)
4. Wybierz **"Secrets"** z menu po lewej
5. Skopiuj zawartość z `.streamlit/secrets.toml.template`
6. **Wypełnij prawdziwe wartości API keys**:

```toml
# Twoje prawdziwe klucze API
ANTHROPIC_API_KEY = "sk-ant-api03-..."  # Z https://console.anthropic.com/
GOOGLE_API_KEY = "AIzaSy..."            # Z https://makersuite.google.com/app/apikey
OPENAI_API_KEY = "sk-..."               # Z https://platform.openai.com/api-keys

# Trading212 API (opcjonalne - jeśli masz konto Trading212)
# Pobierz z: Trading212 → Settings → API (Equity)
TRADING212_API_KEY = "twoj-trading212-key"

# Jeśli używasz Google Sheets - skopiuj zawartość credentials.json:
[gcp_service_account]
type = "service_account"
project_id = "twoj-projekt"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\nXXX\n-----END PRIVATE KEY-----\n"
client_email = "xxx@xxx.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

7. Kliknij **"Save"**
8. Aplikacja automatycznie się zrestartuje

---

## 📝 KROK 4: Modyfikacja kodu dla Cloud (jeśli potrzeba)

Sprawdź w `streamlit_app.py` czy ścieżki do plików są względne, nie bezwzględne:

```python
# ✅ DOBRZE (względna ścieżka)
with open("cele.json", "r") as f:
    cele = json.load(f)

# ❌ ŹLE (bezwzględna ścieżka - nie będzie działać w cloud)
with open("C:/Users/Arek/Desktop/cele.json", "r") as f:
    cele = json.load(f)
```

---

## 🎯 Gotowe!

Twoja aplikacja będzie dostępna pod adresem:
```
https://TWOJA-NAZWA-horyzont-partnerow.streamlit.app
```

### Korzyści z Streamlit Cloud:
- ✅ Dostęp z każdego urządzenia z przeglądarką
- ✅ Automatyczne aktualizacje po każdym push do GitHub
- ✅ Darmowy hosting (limit: 1GB RAM)
- ✅ HTTPS i bezpieczne przechowywanie secrets
- ✅ Monitoring i logi

---

## 🔄 Aktualizacja aplikacji w przyszłości

### Przez GitHub Desktop:
1. Wprowadź zmiany w plikach lokalnie
2. Otwórz GitHub Desktop
3. Zobaczysz listę zmian
4. Wpisz opis zmian w "Summary"
5. Kliknij **"Commit to main"**
6. Kliknij **"Push origin"**
7. Streamlit Cloud automatycznie zaktualizuje aplikację (1-2 min)

### Przez Git:
```bash
git add .
git commit -m "Opis zmian"
git push
```

---

## ⚠️ Rozwiązywanie problemów

### Aplikacja nie startuje - "Module not found"
- Sprawdź czy wszystkie pakiety są w `requirements.txt`
- Kliknij "Reboot app" w Streamlit Cloud

### Błąd "API Key not found"
- Sprawdź sekcję Secrets w Settings
- Upewnij się że nazwy zmiennych się zgadzają

### Aplikacja działa wolno
- Darmowy tier ma limit 1GB RAM
- Rozważ cache'owanie danych z `@st.cache_data`

### Chcę zmienić adres URL
- Settings → General → App URL

---

## 📞 Potrzebujesz pomocy?
- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- Forum: https://discuss.streamlit.io/
- GitHub Issues: w swoim repozytorium
