# 🏢 Horyzont Partnerów - Streamlit Dashboard

Interaktywny dashboard do zarządzania portfelem inwestycyjnym z AI Partnerami.

## 🚀 Uruchomienie

### Szybki start
```powershell
streamlit run streamlit_app.py
```

Dashboard otworzy się automatycznie w przeglądarce na `http://localhost:8501`

## 📱 Funkcjonalności

### 📊 Dashboard (Strona główna)
- **Metryki portfela** - Wartość netto, leverage, liczba pozycji, dochód pasywny
- **Wykresy interaktywne** - Struktura portfela, alokacja aktywów
- **Progress bars** - Wizualizacja postępu w realizacji celów:
  - Spłata długów
  - Rezerwa gotówkowa
  - Filar surowcowy (PBR)
  - Financial Independence
- **Top Holdings** - Tabela z najważniejszymi pozycjami

### 💬 Partnerzy
- **Chat z AI** - Interaktywna rozmowa z Partnerami
- **Wybór partnera** - Rozmawiaj z konkretnym partnerem lub wszystkimi naraz
- **Tryby odpowiedzi** - Zwięzły, Normalny, Szczegółowy
- **Fight Club** - Włącz/wyłącz konflikty między Partnerami
- **Szybkie akcje**:
  - 🗳️ Rozpocznij głosowanie
  - 🎯 Poproś o doradztwo
  - 🧹 Wyczyść chat

### 📈 Analiza
- **Metryki ryzyka**:
  - 📊 Sharpe Ratio - Stosunek zwrotu do ryzyka
  - 📉 Sortino Ratio - Uwzględnia tylko straty
  - ⚠️ Max Drawdown - Największy spadek
  - 💔 VaR (95%) - Value at Risk
  - 🌊 Zmienność roczna
  - 💰 Całkowity zwrot
  - 📈 Beta - Korelacja z S&P 500
- **Ocena ryzyka** - Risk score 0-100 z rekomendacjami
- **Wykres historii** - Wartość portfela w czasie

### 🎮 Symulacje
- **Scenariusze rynkowe**:
  - 🐂 Bullish - Wzrost o 20%
  - 🐻 Bearish - Spadek o 20%
- **Symulacja transakcji**:
  - 🛒 Kupno akcji/krypto
  - 💸 Sprzedaż z obliczeniem zysku/straty
- **Reset** - Powrót do stanu początkowego

### ⚙️ Ustawienia
- 🎨 Motyw aplikacji
- 🔔 Powiadomienia
- 📊 Czas cache danych

## 🎨 Funkcje UI

### Automatyczne odświeżanie
Dashboard automatycznie wykrywa zmiany w pliku i proponuje reload.

### Cache danych
Dane portfela są cache'owane na 5 minut. Użyj przycisku "🔄 Odśwież Dane" aby wymusić reload.

### Responsywność
Dashboard jest w pełni responsywny - działa na desktopie, tablecie i telefonie.

## 📊 Integracja z głównym programem

Dashboard korzysta z tych samych modułów co główny program:
- `gra_rpg.py` - Główna logika, pobieranie danych
- `risk_analytics.py` - Metryki ryzyka
- `portfolio_simulator.py` - Symulator scenariuszy
- `animated_timeline.py` - Wizualizacje (TODO)

## 🔧 Wymagania

```
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
```

## 💡 Tips & Tricks

### Skróty klawiszowe
- `R` - Rerun aplikacji
- `C` - Wyczyść cache
- `?` - Pokaż skróty

### Debugowanie
Włącz tryb debug dodając do `~/.streamlit/config.toml`:
```toml
[runner]
fastReruns = true

[logger]
level = "debug"
```

### Multi-user
Streamlit wspiera wielu użytkowników jednocześnie. Każdy użytkownik ma własną sesję (st.session_state).

## 🚀 Deploy (Opcjonalnie)

### Streamlit Cloud (FREE)
1. Push kod na GitHub
2. Połącz repo na https://streamlit.io/cloud
3. Deploy automatycznie!

### Własny serwer
```powershell
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

## 📝 TODO

- [ ] Integracja z prawdziwą AI (obecnie mock responses)
- [ ] Real-time updates z Trading212 API
- [ ] Eksport raportów do Excel z dashboardu
- [ ] Notyfikacje desktop
- [ ] Dark mode
- [ ] Porównanie scenariuszy (zakładka w Symulacjach)
- [ ] Historia transakcji
- [ ] Kalkulatory (FIRE, DCA, itp.)

## 🐛 Znane problemy

1. **"Nie można załadować modułów"** - Upewnij się że `gra_rpg.py` działa poprawnie
2. **Brak danych historycznych** - Uruchom `gra_rpg.py` z komendą `status` kilka razy
3. **Import errors** - Sprawdź czy wszystkie zależności są zainstalowane

## 📞 Wsparcie

Jeśli dashboard nie działa:
1. Sprawdź terminal z błędami
2. Upewnij się że główny program działa
3. Wyczyść cache: Streamlit menu (☰) → Clear cache

## 🎉 Enjoy!

Dashboard został stworzony aby ułatwić zarządzanie portfelem i interakcję z AI Partnerami!
