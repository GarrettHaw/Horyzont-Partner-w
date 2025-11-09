# 🚀 Przewodnik po Zaawansowanych Funkcjach - Horyzont Partnerów

## 📅 Data: 24 października 2025

---

## 🎯 Nowe Funkcjonalności

System został rozbudowany o **11 zaawansowanych funkcji** w 4 głównych modułach:

### 📦 Nowe Moduły

1. **`alert_system.py`** - System alertów i notyfikacji
2. **`benchmark_comparison.py`** - Porównanie z indeksami rynkowymi
3. **`goal_analytics.py`** - Analiza i predykcja celów finansowych
4. **`news_aggregator.py`** - **NOWE!** Automatyczne pobieranie newsów finansowych

---

## 📰 4. NEWS AGGREGATOR - Automatyczne Newsy dla Partnerów

### Źródła newsów:

#### 🎯 Trading212 / yfinance - Newsy o Twoich spółkach
- **Co robi:** Pobiera newsy dla każdego tickera z Twojego portfela
- **Źródła:** Yahoo Finance News API (przez yfinance)
- **Priorytet:** Najwyższy (relevance=10) - bo dotyczą TWOICH aktywów

#### 🌍 Google News RSS - Ogólne trendy rynkowe
- **Co robi:** Skanuje Google News dla keywords finansowych
- **Keywords:** 
  - Fed rate decision
  - Stock market
  - Inflation report
  - Crypto market
  - Dividend stocks
- **Priorytet:** Średni (relevance=7) - kontekst makroekonomiczny

### Automatyzacja:

#### Cache i TTL:
- **Cache:** 6 godzin (automatyczne odświeżanie)
- **Plik:** `news_cache.json`
- **Knowledge Base:** `knowledge_base/articles.json` (max 100 artykułów)

#### Ranking i filtrowanie:
1. **Usuwa duplikaty** (ten sam tytuł)
2. **Sortuje:** najpierw Twoje spółki (🎯), potem trendy rynkowe (🌍)
3. **Top 20** najważniejszych trafia do knowledge base
4. **Top 5** trafia do promptu dla partnerów AI

### Użycie CLI:

```powershell
# Pobierz i zapisz najnowsze newsy
python news_aggregator.py update

# Wymuś update (ignoruj cache)
python news_aggregator.py update --force

# Pokaż ostatnie newsy (10 artykułów)
python news_aggregator.py show

# Format dla AI partnera (5 artykułów)
python news_aggregator.py ai-format

# Wyczyść cache
python news_aggregator.py clear
```

### Windows Task Scheduler:

Dodaj zadanie uruchamiające `run_news_update.bat` co 6 godzin:
- 06:00
- 12:00
- 18:00
- 00:00

### Struktura `knowledge_base/articles.json`:

```json
{
  "articles": [
    {
      "id": "gnews_abc123",
      "date": "2025-10-24T14:30:00",
      "title": "Inflation Hits 3% in September",
      "source": "US News Money",
      "url": "https://...",
      "summary": "Inflation data shows...",
      "ticker": null,
      "type": "market_trend",
      "keyword": "inflation report",
      "relevance": 7,
      "added_at": "2025-10-24T15:00:00"
    },
    {
      "id": "t212_AAPL_xyz789",
      "date": "2025-10-24T10:15:00",
      "title": "Apple Q3 Earnings Beat Estimates",
      "source": "Yahoo Finance",
      "url": "https://...",
      "summary": "Apple reported...",
      "ticker": "AAPL",
      "type": "portfolio",
      "relevance": 10,
      "added_at": "2025-10-24T15:00:00"
    }
  ],
  "last_update": "2025-10-24T15:00:00"
}
```

### Integracja z Partnerami AI:

**Automatyczna!** Każdy partner dostaje w prompcie:

```
📰 NAJNOWSZE ARTYKUŁY FINANSOWE (ostatnie 24h):

1. 🎯 [TWOJA SPÓŁKA: AAPL]
   Tytuł: Apple Q3 Earnings Beat Estimates
   Źródło: Yahoo Finance | Data: 2025-10-24

2. 🌍 [TREND RYNKOWY]
   Tytuł: Inflation Hits 3% in September
   Źródło: US News Money | Data: 2025-10-24
...
```

**Partner może:**
- Odnieść się do newsów w odpowiedzi
- Powiązać news z pytaniem użytkownika
- Sugerować działania na podstawie newsów

### Przykład rozmowy:

**User:** "Co sądzisz o moim portfelu?"

**Partner Adam:** "Widziałem news o Apple - Q3 earnings beat expectations! Masz 5 akcji AAPL, to świetna wiadomość. Wartość powinna wzrosnąć. Jednocześnie inflacja się utrzymuje na 3%, co może wpłynąć na decyzje Fed o stopach..."

---

## 🔔 1. SYSTEM ALERTÓW I NOTYFIKACJI

### Lokalizacja: `🔔 Alerty i Notyfikacje` (Menu → AI & Strategia)

### Funkcje:

#### 🆕 Automatyczne Wykrywanie Nowych Pozycji
- **Co robi:** Porównuje ostatnie 2 snapshoty i wykrywa nowe aktywa
- **Przykład:** "🆕 Znaleziono nowy asset: AAPL - 10 akcji po $150.00"
- **Dane:** ticker, typ (stock/crypto), ilość, cena zakupu, data dodania

#### 📈 Alerty Znaczących Zmian Cen (>10%)
- **Co robi:** Wykrywa gdy cena aktywa zmienia się o więcej niż 10% między snapshotami
- **Przykład:** "🔴📉 TSLA: -15.3% ($250.00 → $211.75)"
- **Dane:** poprzednia cena, aktualna cena, % zmiana, timestamp

#### 💳 Zbliżające się Terminy Płatności Kredytów
- **Co robi:** Sprawdza `kredyty.json` i wykrywa terminy za 7/3/1 dni
- **Przykład:** "🔴 Płatność kredytu za 1 dzień - Kredyt mieszkaniowy: 2500 PLN"
- **Ważność:** 
  - 🟡 7 dni przed = info
  - 🟠 3 dni przed = warning
  - 🔴 1 dzień przed = critical

#### 🎯 Notyfikacje Osiągniętych Celów
- **Co robi:** Wykrywa gdy cel finansowy osiągnie 100%+
- **Przykład:** "🎉 Cel osiągnięty: Fundusz Awaryjny (10,500 / 10,000 PLN)"
- **Bonus:** Zapisuje do `goal_achievements.json` + balony w UI! 🎈

### Użycie CLI:

```powershell
# Uruchom wszystkie detektory
python alert_system.py run

# Zobacz historię alertów (ostatnie 10)
python alert_system.py history

# Wyczyść historię
python alert_system.py clear
```

### Struktura pliku `alerts.json`:
```json
{
  "history": [
    {
      "id": 1,
      "timestamp": "2025-10-23T14:30:00",
      "type": "new_position",
      "severity": "info",
      "title": "🆕 Nowa akcja: AAPL",
      "message": "Dodano 10 akcji Apple Inc. po $150.00",
      "read": false,
      "metadata": {
        "ticker": "AAPL",
        "type": "stock",
        "quantity": 10,
        "price": 150.0
      }
    }
  ]
}
```

---

## 📊 2. PORÓWNANIE Z BENCHMARKAMI

### Lokalizacja: `🕐 Timeline` → Tab "🏆 Porównanie z Benchmarkami"

### Funkcje:

#### Wykresy Porównawcze (Overlayed Lines)
- **Co porównuje:**
  - 💼 Twój Portfel (czerwona linia, gruba)
  - 📈 S&P 500 (^GSPC) - niebieski
  - 📊 WIG20 (^W20.PL) - pomarańczowy
  - ₿ Bitcoin (BTC-USD) - zielony

- **Normalizacja:** Wszystkie serie zaczynają od 100 punktów
- **Okres:** Od pierwszego snapshota do dziś
- **Cache:** 1 godzina (auto-refresh)

#### Statystyki Porównawcze
```
💼 Twój Portfel: +12.5% (14 dni)
🟢 S&P 500: +8.2% (+4.3%)     ← lepszy o 4.3%
🔴 WIG20: +15.1% (-2.6%)      ← gorszy o 2.6%
🟢 Bitcoin: +5.8% (+6.7%)     ← lepszy o 6.7%
```

### Użycie CLI:

```powershell
# Szybkie statystyki
python benchmark_comparison.py

# Przygotuj dane do porównania
python benchmark_comparison.py compare

# Szczegółowe statystyki
python benchmark_comparison.py stats

# Wyczyść cache benchmarków
python benchmark_comparison.py clear-cache
```

### Struktura cache `benchmark_cache.json`:
```json
{
  "SP500_20251019": {
    "timestamp": "2025-10-23T14:00:00",
    "data": {
      "Close": {
        "2025-10-19": 4500.0,
        "2025-10-20": 4520.5
      }
    }
  }
}
```

---

## 🎯 3. ANALIZA I PREDYKCJA CELÓW

### Lokalizacja: `🔔 Alerty` → Tab "🎯 Cele"

### Funkcje:

#### 🔮 Predykcja Osiągnięcia Celów
- **Metoda:** Linear regression na bazie historycznych snapshots
- **Wymaga:** Minimum 3 snapshoty
- **Przykład:** "Za 45 dni osiągniesz cel 'Nowy Laptop' (pewność: HIGH, R²=0.92)"
- **Dane:**
  - Przewidywana data osiągnięcia
  - Liczba dni do celu
  - Tempo dzienne (PLN/dzień)
  - Confidence level (high/medium/low)
  - R² (jakość dopasowania)

#### 💰 Rekomendacje Oszczędzania
- **Co robi:** Oblicza ile trzeba odkładać miesięcznie/dziennie
- **Przykład:** "Musisz odkładać 500 PLN/miesiąc (16.67 PLN/dzień) aby osiągnąć cel 'Wakacje' do 2026-06-01"
- **Parametr:** Deadline w miesiącach (slider 1-36)

#### 📜 Historia Modyfikacji Celów
- **Logowanie:** Automatyczne przy każdej zmianie celu
- **Struktura:**
  ```json
  {
    "id": 1,
    "timestamp": "2025-10-23T14:00:00",
    "goal_id": "fundusz_awaryjny",
    "action": "modified",
    "user": "Adam",
    "old_value": {"cel": 10000, "aktualnie": 5000},
    "new_value": {"cel": 12000, "aktualnie": 5500},
    "reason": "Podwyższenie celu po analizie wydatków"
  }
  ```

### Użycie CLI:

```powershell
# Predykcje wszystkich celów
python goal_analytics.py predict

# Rekomendacje (domyślnie 12 miesięcy)
python goal_analytics.py recommend

# Rekomendacje dla 6 miesięcy
python goal_analytics.py recommend 6

# Historia zmian (wszystkie cele)
python goal_analytics.py history

# Historia konkretnego celu
python goal_analytics.py history fundusz_awaryjny
```

### Funkcja logowania zmian:
```python
from goal_analytics import log_goal_change

# Przykład użycia
log_goal_change(
    goal_id="fundusz_awaryjny",
    action="modified",  # created, modified, deleted, progress_update
    user="Adam",
    old_value={"cel": 10000, "aktualnie": 5000},
    new_value={"cel": 12000, "aktualnie": 5500},
    reason="Podwyższenie celu po analizie wydatków"
)
```

---

## 🎮 JAK UŻYWAĆ?

### 1. Uruchom Streamlit
```powershell
streamlit run streamlit_app.py
```

### 2. Przejdź do zakładki "🔔 Alerty i Notyfikacje"
- Menu → **🤖 AI & Strategia** → **🔔 Alerty i Notyfikacje**

### 3. Kliknij "🔄 Skanuj Teraz"
- System automatycznie:
  - ✅ Sprawdzi nowe pozycje
  - ✅ Wykryje znaczące zmiany cen
  - ✅ Sprawdzi terminy kredytów
  - ✅ Zweryfikuje osiągnięcia celów

### 4. Przeglądaj 5 tabów:
1. **📊 Wszystkie** - historia wszystkich alertów z filtrowaniem
2. **🆕 Nowe Pozycje** - lista nowo dodanych aktywów
3. **📈 Zmiany Cen** - aktywa ze zmianą >10%
4. **💳 Kredyty** - zbliżające się terminy płatności
5. **🎯 Cele** - predykcje i rekomendacje oszczędzania

### 5. Zobacz Timeline z Benchmarkami
- Menu → **📈 Analiza & Historia** → **🕐 Timeline**
- Tab: **🏆 Porównanie z Benchmarkami**
- Automatyczne pobieranie danych S&P500, WIG20, Bitcoin

---

## ⚙️ KONFIGURACJA

### Próg alertów cenowych:
```python
# alert_system.py, linia 18
PRICE_CHANGE_THRESHOLD = 10.0  # procent (domyślnie 10%)
```

### Dni ostrzeżeń dla kredytów:
```python
# alert_system.py, linia 19
LOAN_WARNING_DAYS = [7, 3, 1]  # ostrzeżenia za 7, 3 i 1 dzień przed
```

### Cache benchmarków:
```python
# benchmark_comparison.py, linia 19
CACHE_TTL_HOURS = 1  # 1 godzina (domyślnie)
```

### Automatyczne skanowanie:
Dodaj do Windows Task Scheduler:
```batch
cd "C:\Users\alech\Desktop\Horyzont Partnerów"
python alert_system.py run
```
**Sugerowany harmonogram:** Codziennie o 21:05 (5 min po daily snapshot)

---

## 📂 PLIKI DANYCH

| Plik | Opis | Format |
|------|------|--------|
| `alerts.json` | Historia wszystkich alertów | JSON |
| `goal_achievements.json` | Osiągnięte cele | JSON |
| `cele_history.json` | Historia modyfikacji celów | JSON |
| `benchmark_cache.json` | Cache danych rynkowych | JSON |

---

## 🐛 ROZWIĄZYWANIE PROBLEMÓW

### Problem: "Za mało danych do predykcji"
**Rozwiązanie:** Potrzebujesz minimum 3 snapshoty. Uruchom:
```powershell
python daily_snapshot.py
```

### Problem: "Błąd pobierania benchmarku"
**Rozwiązanie:** Sprawdź połączenie z internetem. Cache wygasa po 1h.

### Problem: "Brak alertów mimo zmian"
**Rozwiązanie:** Uruchom ręcznie:
```powershell
python alert_system.py run
```

### Problem: Streamlit nie widzi modułów
**Rozwiązanie:** Upewnij się że:
- `alert_system.py` istnieje w katalogu głównym
- `benchmark_comparison.py` istnieje
- `goal_analytics.py` istnieje
- `scipy` zainstalowany: `pip install scipy`

---

## 📊 PRZYKŁADY UŻYCIA

### Scenario 1: Monitorowanie Nowych Inwestycji
```powershell
# Krok 1: Dodaj nową pozycję w Trading212
# Krok 2: Poczekaj na daily snapshot (21:00) lub utwórz ręcznie
python daily_snapshot.py

# Krok 3: Uruchom detektor
python alert_system.py run

# Wynik: "🆕 Nowa akcja: MSFT - 5 akcji po $350.00"
```

### Scenario 2: Analiza Wydajności vs Rynek
```powershell
# Otwórz Streamlit → Timeline → Tab "Porównanie z Benchmarkami"
# Zobacz: Twój portfel vs S&P500/WIG20/Bitcoin
# Statystyki pokazują czy bijesz rynek!
```

### Scenario 3: Planowanie Oszczędzania
```powershell
# CLI:
python goal_analytics.py recommend 6

# Lub w Streamlit:
# Alerty → Tab "Cele" → Sekcja "Rekomendacje Oszczędzania"
# Ustaw slider: 6 miesięcy
# Wynik: "Musisz odkładać 833 PLN/miesiąc (27.77 PLN/dzień)"
```

---

## 🎨 SCREENSHOTY (Opis UI)

### Tab "📊 Wszystkie Alerty"
```
┌─────────────────────────────────────────────────┐
│ 💡 System automatycznie wykrywa ważne wydarzenia│
│                                    [🔄 Skanuj]  │
├─────────────────────────────────────────────────┤
│ Filtry: [Typ ▼] [Ważność ▼] ☑ Pokaż przeczytane│
│                                                 │
│ ⚠️ MSFT: +12.5%                        🔵 NOWY  │
│ 2025-10-23 14:30 | $320.00 → $360.00           │
│ ─────────────────────────────────────────────── │
│ ℹ️ Nowa akcja: AAPL                   🔵 NOWY  │
│ 2025-10-23 10:15 | 10 akcji po $150.00        │
└─────────────────────────────────────────────────┘
```

### Tab "🎯 Cele" - Predykcje
```
┌─────────────────────────────────────────────────┐
│ 📌 Fundusz Awaryjny - 75%                       │
│ ┌─────────┬──────────┬───────────┐             │
│ │ Postęp  │ Za ile   │ Pewność   │             │
│ │ 75.0%   │ 45 dni   │ HIGH 🟢   │             │
│ │ [████████░░]                   │             │
│ └─────────┴──────────┴───────────┘             │
│ 📈 Tempo: 166.67 PLN/dzień                     │
└─────────────────────────────────────────────────┘
```

### Timeline - Porównanie
```
┌─────────────────────────────────────────────────┐
│ 🏆 Twój Portfel vs Rynek                        │
│ 💡 Znormalizowane do 100 punktów                │
│                                                 │
│ 150 ┤     ╭──── Twój Portfel (czerwony)        │
│     │    ╭╯                                     │
│ 100 ├───╯  ┄┄ S&P500 (niebieski)               │
│     │    ┄╯  ┄┄ WIG20 (pomarańczowy)           │
│  50 └─────────────────────────────────────────  │
│     Oct19  Oct21  Oct23                         │
│                                                 │
│ 💼 Twój: +12.5% | 🟢 S&P: +8.2% (+4.3%)        │
└─────────────────────────────────────────────────┘
```

---

## 🚀 ROADMAP (Przyszłe Funkcje)

### Planowane:
- [ ] Email notifications (integracja z `email_notifier.py`)
- [ ] Desktop notifications (Windows Toast)
- [ ] Custom alert rules (użytkownik definiuje progi)
- [ ] Alert dla pojedynczych pozycji (np. "powiadom gdy AAPL >$200")
- [ ] Eksport alertów do PDF/Excel
- [ ] Dashboard z metrykami alertów
- [ ] Integracja z Telegram Bot
- [ ] Machine learning dla lepszych predykcji

---

## 📝 NOTATKI DLA DEWELOPERÓW

### Dodawanie nowego typu alertu:

1. **W `alert_system.py`:**
```python
def detect_my_alert() -> List[Dict]:
    """Nowy detektor"""
    # Logika wykrywania
    
    # Dodaj alert
    add_alert(
        alert_type="my_alert_type",
        title="🔥 Mój Alert",
        message="Szczegóły...",
        severity="warning",
        metadata={"custom": "data"}
    )
    
    return []
```

2. **Dodaj do `run_all_detectors()`:**
```python
results["my_alerts"] = detect_my_alert()
```

3. **Dodaj tab w Streamlit** (`show_alerts_page()`):
```python
with tab_new:
    st.subheader("🔥 Moje Alerty")
    alerts = [a for a in history if a.get('type') == 'my_alert_type']
    # Wyświetl...
```

---

## 📞 WSPARCIE

Jeśli masz problemy:
1. Sprawdź logi w konsoli
2. Upewnij się że wszystkie moduły są zainstalowane: `pip install scipy yfinance pandas numpy`
3. Sprawdź czy pliki JSON istnieją i są poprawne
4. Uruchom `python alert_system.py run` ręcznie aby zobaczyć błędy

---

**Wersja:** 1.0  
**Data:** 23 października 2025  
**Autor:** GitHub Copilot dla Horyzont Partnerów

🎉 **Miłego użytkowania!** 🚀
