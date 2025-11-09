# 📸 Daily Snapshot System - Instrukcja

## Przegląd
Automatyczny system codziennych zapisów stanu portfela (daily snapshots). Rejestruje wartość aktywów, zobowiązań i net worth każdego dnia o ustalonej godzinie.

## Cechy Systemu

### ✅ Co jest zapisywane
- **Akcje**: Wartość USD/PLN, liczba pozycji, cash
- **Kryptowaluty**: Wartość USD/PLN, liczba pozycji
- **Zobowiązania**: Suma kredytów PLN
- **Kurs USD/PLN**: Aktualny z NBP API
- **Net Worth**: Wartość netto (aktywa - zobowiązania)

### ⏰ Kiedy
- **Domyślnie**: 21:00 każdego dnia
- **Deduplikacja**: 1 snapshot na dzień (nadpisuje jeśli uruchomiony kilka razy)
- **Rotacja**: Automatyczne usuwanie starszych niż 365 dni

### 📊 Gdzie
- **Plik**: `daily_snapshots.json`
- **Format**: JSON array z timestampami
- **Widoczność**: TAB "📸 Snapshots" w Streamlit

## Użycie

### 1. Ręczne uruchomienie
```bash
# Zwykły snapshot
python daily_snapshot.py

# Statystyki
python daily_snapshot.py stats

# Sprawdź czy trzeba snapshot
python daily_snapshot.py check
```

### 2. Z Streamlit
- Otwórz TAB **📸 Snapshots**
- Kliknij **"📸 Utwórz snapshot TERAZ"**
- Zobacz wykresy i historię

### 3. Automatyczne (Windows Task Scheduler)

**Krok 1: Otwórz Task Scheduler**
```
Win + R → taskschd.msc
```

**Krok 2: Create Basic Task**
- Name: `Portfolio Daily Snapshot`
- Description: `Codzienne zapisywanie stanu portfela o 21:00`

**Krok 3: Trigger**
- Daily
- Start: Dzisiaj o 21:00
- Recur every: 1 days

**Krok 4: Action**
- Start a program
- Program/script: `C:\Users\alech\Desktop\Horyzont Partnerów\run_daily_snapshot.bat`
- Start in: `C:\Users\alech\Desktop\Horyzont Partnerów`

**Krok 5: Settings**
- ✅ Run whether user is logged on or not
- ✅ Run with highest privileges
- ✅ If task fails, restart every: 1 minute (Max 3 times)

**Krok 6: Test**
```bash
# Uruchom ręcznie task
Right-click → Run
```

## Widoki w Streamlit

### TAB 1: Wykresy 📈
1. **Net Worth Over Time** - wykres liniowy wartości netto
2. **Składowe Portfela** - stacked area (akcje + crypto + zobowiązania)
3. **Zmiana %** - od pierwszego snapshotu

### TAB 2: Historia Tabela 📊
- Kompletna tabela wszystkich snapshots
- Sortowanie: najnowsze na górze
- Export do CSV

### TAB 3: Szczegóły Ostatniego 🎯
- Pełne info o ostatnim snapshot
- Breakdown: akcje, crypto, zobowiązania
- Raw JSON

### TAB 4: Zarządzanie ⚙️
- Tworzenie snapshot on-demand
- Status: czy pora na dzienny snapshot
- Instrukcje Windows Task Scheduler
- Opcja usunięcia wszystkich (niebezpieczne!)

## Integracje

### Trading212 API
```python
# Automatycznie używa credentials.json
{
  "trading212_api_key": "YOUR_KEY_HERE"
}
```

### Crypto Portfolio Manager
```python
# Automatycznie wykrywa krypto.json
# Pobiera live prices z CoinGecko/MEXC/Gate.io
```

### NBP API (Kurs PLN)
```python
# Fallback: 3.65 jeśli API nie działa
```

## Statystyki

### Przykładowy output
```
📊 STATYSTYKI DAILY SNAPSHOTS
============================================================
📈 Liczba snapshots: 45
📅 Pierwszy: 2025-09-01
📅 Ostatni: 2025-10-21
⏱️  Dni śledzenia: 50
💎 Net Worth pierwszy: 18,245.00 PLN
💎 Net Worth ostatni: 21,061.27 PLN
📊 Zmiana: +15.43%
⚡ Avg snapshots/tydzień: 6.3
```

## Troubleshooting

### ❌ "Brak Trading212 API key"
**Rozwiązanie:**
```json
// credentials.json
{
  "trading212_api_key": "YOUR_API_KEY"
}
```

### ❌ "Brak danych do zapisania"
**Przyczyna:** Brak krypto.json I credentials.json

**Rozwiązanie:**
- Upewnij się że istnieje przynajmniej `krypto.json` lub `kredyty.json`

### ❌ "Błąd wczytywania historii"
**Rozwiązanie:**
```bash
# Sprawdź czy daily_snapshots.json jest valid JSON
python -m json.tool daily_snapshots.json
```

### ⚠️ Duplikaty tego samego dnia
**Nie szkodzi!** System automatycznie deduplikuje - zostawia tylko najnowszy snapshot z danego dnia.

### 🔄 Jak zresetować historię
1. Otwórz Streamlit → 📸 Snapshots → Zarządzanie
2. Sekcja "Niebezpieczna Strefa"
3. Kliknij 2x "USUŃ WSZYSTKIE SNAPSHOTS"

## Pliki Systemowe

### `daily_snapshot.py`
Główny moduł z logiką zapisywania

### `run_daily_snapshot.bat`
Wrapper dla Windows Task Scheduler

### `daily_snapshots.json`
Baza danych snapshots (JSON array)

### `DAILY_SNAPSHOT_GUIDE.md`
Ten dokument

## Best Practices

### ✅ DO
- Uruchamiaj o tej samej godzinie każdego dnia (21:00)
- Regularnie sprawdzaj TAB Snapshots w Streamlit
- Exportuj CSV co miesiąc jako backup
- Testuj Windows Task przed pierwszym automatycznym uruchomieniem

### ❌ DON'T
- Nie edytuj ręcznie `daily_snapshots.json` (ryzyko corruption)
- Nie zmieniaj czasu uruchomienia zbyt często
- Nie usuwaj historii bez backupu

## Przyszłe Ulepszenia (Roadmap)

- [ ] Email notification po snapshot (opcjonalne)
- [ ] Google Sheets export
- [ ] Porównanie month-over-month
- [ ] Alerty jeśli net worth spadnie >5%
- [ ] Integracja z monthly_audit.py
- [ ] Backup do cloud (Google Drive)

## Kontakt
W razie problemów sprawdź logi w terminalu lub otwórz issue.

---
*Last updated: 2025-10-21*
*Version: 1.0*
