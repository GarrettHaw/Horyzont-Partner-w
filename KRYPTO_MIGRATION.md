# 🔄 Migracja Krypto - Google Sheets → Lokalne JSON

**Data:** 20 października 2025

## ✅ Co się zmieniło?

System zarządzania kryptowalutami został **całkowicie przeniesiony** z Google Sheets do lokalnego pliku `krypto.json`.

### Przed zmianą:
- ❌ Dane pobierane z arkusza Google Sheets "Krypto"
- ❌ Ryzyko duplikatów
- ❌ Brak kontroli nad danymi
- ❌ Zależność od połączenia internetowego

### Po zmianie:
- ✅ Wszystkie dane w `krypto.json` (lokalnie)
- ✅ Pełna kontrola nad pozycjami
- ✅ Brak duplikatów
- ✅ Szybkie zarządzanie w zakładce "₿ Krypto"

---

## 📂 Struktura danych

### Plik: `krypto.json`

```json
{
  "krypto": [
    {
      "id": "1760985273.184567",
      "symbol": "BTC",
      "ilosc": 0.5,
      "cena_zakupu_usd": 35000.00,
      "platforma": "Binance",
      "status": "Earn",
      "apy": 5.0,
      "notatki": "Auto-invest włączony",
      "data_dodania": "2025-10-20T..."
    }
  ]
}
```

### Pola:

| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| `id` | string | Unikalny identyfikator (timestamp) | ✅ |
| `symbol` | string | Ticker kryptowaluty (BTC, ETH, BNB...) | ✅ |
| `ilosc` | float | Ilość posiadanych monet (8 miejsc dziesiętnych) | ✅ |
| `cena_zakupu_usd` | float | Średnia cena zakupu w USD | ✅ |
| `platforma` | string | Giełda (Binance, Gate.io, MEXC...) | ✅ |
| `status` | string | Status (Spot, Earn, Launchpool, Staking...) | ❌ |
| `apy` | float | Roczny procent zysku (jeśli dotyczy) | ❌ |
| `notatki` | string | Dodatkowe informacje | ❌ |
| `data_dodania` | ISO8601 | Data dodania pozycji | ✅ (auto) |

---

## 🚀 Jak używać?

### 1. Dodawanie kryptowaluty

1. Przejdź do **"💳 Kredyty"** → Zakładka **"₿ Krypto"**
2. Wypełnij formularz:
   - Symbol (np. BTC, ETH, BNB)
   - Ilość (z dokładnością do 8 miejsc po przecinku)
   - Średnia cena zakupu w USD
   - Platforma (wybierz z listy)
   - Status (opcjonalnie)
   - APY % (opcjonalnie - dla Earn/Staking)
   - Notatki (opcjonalnie)
3. Kliknij **"💾 Zapisz Kryptowalutę"**

### 2. Edycja pozycji

- Kliknij **✏️** przy wybranej pozycji
- Zmień ilość lub cenę zakupu
- Zapisz zmiany

### 3. Usuwanie pozycji

- Kliknij **🗑️** przy wybranej pozycji
- Potwierdź klikając ponownie

---

## 📊 Funkcje

### Statystyki:
- 💰 **Wartość zakupu** - suma według ceny zakupu (nie aktualna cena rynkowa)
- 🔢 **Liczba aktywów** - ile różnych pozycji
- 🏦 **Platformy** - ile różnych giełd
- 📈 **Średnie APY** - średni zysk z Earn/Staking

### Grupowanie:
- Automatyczne grupowanie po symbolach (np. wszystkie pozycje BTC razem)
- Podział po platformach w panelu statystyk

### Filtrowanie:
- Filtruj pozycje po platformie
- Zobacz tylko wybrane giełdy

### Wizualizacja:
- 📊 Wykres kołowy - podział portfela po symbolach

---

## 🔄 Integracja z Dashboard

System automatycznie:
1. **Ładuje dane** z `krypto.json` przy starcie aplikacji
2. **Oblicza wartość portfela** według cen zakupu
3. **Wyświetla w głównym wykresie** jako osobną kategorię "Krypto"
4. **Przekazuje do AI Advisors** - pełne dane pozycji dla analizy

---

## ⚠️ Ważne uwagi

### Wartość portfela:
- System **NIE POBIERA** aktualnych cen z rynku
- Wartość obliczana jako: `ilość × średnia cena zakupu`
- To jest wartość **ZAKUPU**, nie aktualna wartość rynkowa

### Aktualizacja cen:
- Jeśli chcesz zaktualizować cenę zakupu - edytuj pozycję ręcznie
- Możesz dodać tę samą kryptowalutę wiele razy (z różnych zakupów)
- System automatycznie policzy średnią wartość

### Backup:
- `krypto.json` to zwykły plik tekstowy
- Możesz go skopiować jako backup
- Możesz edytować ręcznie w edytorze tekstu

---

## 🔧 Kod

### Funkcje pomocnicze (streamlit_app.py):

```python
def load_krypto():
    """Wczytaj kryptowaluty z pliku JSON"""
    try:
        with open('krypto.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('krypto', [])
    except FileNotFoundError:
        return []

def save_krypto(krypto):
    """Zapisz kryptowaluty do pliku JSON"""
    try:
        with open('krypto.json', 'w', encoding='utf-8') as f:
            json.dump({'krypto': krypto}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Błąd zapisu krypto: {e}")
        return False
```

### Pobieranie w gra_rpg.py:

```python
# KRYPTO - Z LOKALNEGO PLIKU JSON
print("  💰 Pobieram dane krypto z lokalnego pliku...")
try:
    with open('krypto.json', 'r', encoding='utf-8') as f:
        krypto_data = json.load(f)
        krypto_lista = krypto_data.get('krypto', [])
    
    suma_krypto_usd = 0
    liczba_pozycji_krypto = len(krypto_lista)
    
    for k in krypto_lista:
        wartosc = k['ilosc'] * k['cena_zakupu_usd']
        suma_krypto_usd += wartosc
    
    print(f"  ✓ Krypto wczytane z krypto.json: {suma_krypto_usd:.2f} USD")
except FileNotFoundError:
    print("  ⚠️ Plik krypto.json nie istnieje")
    suma_krypto_usd = 0
    liczba_pozycji_krypto = 0
```

---

## 📝 Changelog

### [2025-10-20] - Migracja do lokalnego JSON
- ✅ Utworzono `krypto.json`
- ✅ Dodano funkcje `load_krypto()` i `save_krypto()`
- ✅ Dodano TAB 6 "₿ Krypto" z pełnym UI
- ✅ Zaktualizowano `pobierz_stan_spolki()` w `gra_rpg.py`
- ✅ Usunięto zależność od Google Sheets dla krypto
- ✅ Dodano 10 platform do wyboru
- ✅ Dodano 9 statusów pozycji
- ✅ Dodano obsługę APY
- ✅ Dodano wizualizację i statystyki

---

## 🎯 Następne kroki (opcjonalne)

1. **API integracja** - pobieranie aktualnych cen z CoinGecko/CoinMarketCap
2. **Historyczne snapshoty** - zapisywanie wartości portfela w czasie
3. **Alerts** - powiadomienia o zmianach cen
4. **Portfolio rebalancing** - sugestie realokacji

---

**Status:** ✅ **ZAKOŃCZONE** - System w pełni funkcjonalny i gotowy do użycia!
