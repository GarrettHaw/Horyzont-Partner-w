# 📊 Trading212 API - Integracja

## ✅ Trading212 API jest już zaimplementowane!

Aplikacja automatycznie pobiera dane z Trading212 jeśli podasz API key.

---

## 🔑 Jak uzyskać Trading212 API Key?

### ⚠️ WAŻNE: Trading212 API - Ograniczenia

**Trading212 API jest dostępne TYLKO dla:**
- Kont **Trading212 CFD** (nie Invest/ISA)
- Lub w trybie **demo/practice**

**Jeśli masz Trading212 Invest:** Użyj Google Sheets jako źródło danych (już zaimplementowane).

---

### Dla Trading212 CFD/Demo:

1. **Zaloguj się do Trading212**: https://www.trading212.com/
2. Przejdź do **Settings** (Ustawienia)
3. Znajdź sekcję **API** lub **API Keys**
4. Kliknij **Generate API Key**
5. Skopiuj wygenerowany klucz

---

## 🚀 Konfiguracja w Streamlit Cloud

### W Streamlit Cloud → Settings → Secrets:

```toml
# Dodaj tę linię:
TRADING212_API_KEY = "twoj-prawdziwy-klucz-api"
```

---

## 🏠 Konfiguracja lokalna (opcjonalnie)

Jeśli chcesz testować lokalnie, stwórz plik `.env`:

```bash
# .env
TRADING212_API_KEY=twoj-prawdziwy-klucz-api
```

**Plik `.env` jest już dodany do `.gitignore` - NIE trafi na GitHub! 🔒**

---

## 🔄 Jak to działa?

### Automatyczna detekcja:

```python
if TRADING212_API_KEY:
    # Używa Trading212 API do pobierania pozycji
    print("✓ Trading212 API włączone")
else:
    # Używa Google Sheets jako backup
    print("⚠️ Używam Google Sheets")
```

### Funkcje Trading212 API:
- ✅ Pobieranie aktualnych pozycji
- ✅ Ceny na żywo
- ✅ Historia transakcji
- ✅ Wartość portfela w czasie rzeczywistym
- ✅ Zyski/straty

---

## 📋 Alternatywa: Google Sheets

**Jeśli NIE masz Trading212 API (np. konto Invest):**

Aplikacja automatycznie użyje Google Sheets jako źródła danych:
1. Ręcznie wprowadzasz pozycje do arkusza
2. Aplikacja pobiera dane z arkusza
3. Ceny live pobiera z Yahoo Finance (yfinance)

**To już jest zaimplementowane i działa!**

---

## 🎯 Priorytety danych:

1. **Trading212 API** (jeśli klucz podany) - najnowsze dane
2. **Google Sheets** (fallback) - ręcznie wprowadzone
3. **yfinance** (zawsze) - ceny rynkowe live

---

## 🔧 Testowanie

Aby przetestować czy API działa:

```python
# W streamlit_app.py lub gra_rpg.py
if TRADING212_ENABLED:
    print("Trading212: WŁĄCZONE ✓")
    # Pobiera dane z API
else:
    print("Trading212: WYŁĄCZONE - używam Google Sheets")
```

---

## ❓ FAQ

### Q: Mam Trading212 Invest - czy mogę użyć API?
**A:** Niestety nie - Trading212 API działa tylko dla CFD. Użyj Google Sheets.

### Q: Czy Trading212 API jest darmowe?
**A:** Tak, jeśli masz konto Trading212 CFD.

### Q: Co jeśli nie podam Trading212 API key?
**A:** Aplikacja automatycznie użyje Google Sheets - wszystko zadziała!

### Q: Czy mogę używać obu jednocześnie?
**A:** Tak! Trading212 API jako główne źródło, Google Sheets jako backup.

---

## 🔒 Bezpieczeństwo

- ✅ Klucz API **NIGDY** nie trafia na GitHub
- ✅ Przechowywany tylko w Streamlit Cloud Secrets
- ✅ Szyfrowane połączenie HTTPS
- ✅ Można odwołać klucz w każdej chwili w Trading212

---

## 📞 Potrzebujesz pomocy?

- Trading212 API Docs: https://t212public-api-docs.redoc.ly/
- Trading212 Support: https://www.trading212.com/contact
