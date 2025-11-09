# 🚀 QUICK START - Streamlit Dashboard

## Start w 30 sekund

```powershell
# 1. Uruchom dashboard
streamlit run streamlit_app.py

# 2. Otworzy się automatycznie w przeglądarce
# http://localhost:8501
```

## 🎯 Pierwsze kroki

### 1. Zobacz Dashboard
- Główna strona pokazuje metryki portfela
- Progress bars celów strategicznych
- Top 10 holdings (prawdziwe dane!)

### 2. Przetestuj Chat AI
```
Kliknij: 💬 Partnerzy
Napisz: "Co sądzisz o moim portfelu?"
Wybierz: Wszyscy lub konkretnego partnera
Czekaj: AI wygeneruje prawdziwe odpowiedzi!
```

### 3. Włącz Dark Mode
```
Kliknij: 🌙 (prawy górny róg)
→ Zmienia się na ciemny motyw
Kliknij: ☀️ aby wrócić do jasnego
```

### 4. Zobacz Timeline
```
Kliknij: 🕐 Timeline
Wymaga: Minimum 2 snapshoty w historii
Jeśli brak: Uruchom gra_rpg.py → status (kilka razy)
```

### 5. Generuj Raport Excel
```
Dashboard → 📄 Generuj Raport Excel
Czekaj: Spinner
Kliknij: ⬇️ Pobierz raport
Gotowe: Plik Excel w Downloads!
```

### 6. Testuj Symulacje
```
Kliknij: 🎮 Symulacje
Tab: Scenariusze Rynkowe
Wybierz: Bullish lub Bearish
Zobacz: Wpływ na portfel
```

### 7. Konfiguruj Ustawienia
```
Kliknij: ⚙️ Ustawienia
Włącz: Auto-refresh (np. co 60s)
Zmień: Cache TTL (np. 10 min)
Włącz: Powiadomienia
Zapisz: Ustawienia do JSON
```

## 💡 Pro Tips

### Skróty klawiszowe
- `R` - Rerun aplikacji
- `C` - Wyczyść cache

### Najlepsze praktyki
1. **Uruchom gra_rpg.py regularnie** - zbieraj historię dla Timeline
2. **Włącz Auto-refresh** - zawsze aktualne dane
3. **Dark mode wieczorem** - oczy będą wdzięczne
4. **Eksportuj Excel przed decyzjami** - miej backup danych

### Testowanie AI Chat
Przykłady pytań:
```
"Czy zwiększyć ekspozycję na krypto?"
"Co sądzicie o sprzedaży AAPL?"
"Jak oceniacie leverage 16.6%?"
"Proponuję kupno 10 akcji PBR - głosujemy?"
```

## 🔧 Rozwiązywanie problemów

### Dashboard nie działa?
```powershell
# Sprawdź czy Streamlit jest zainstalowany
pip list | findstr streamlit

# Reinstall jeśli potrzeba
pip install --upgrade streamlit
```

### Brak danych w Timeline?
```powershell
# Uruchom główny program kilka razy
python gra_rpg.py
# W programie wpisz: status
# Powtórz 2-3 razy
```

### AI nie odpowiada?
```
✅ Sprawdź .env - czy API keys są ustawione
✅ Zobacz terminal - czy są błędy
✅ Poczekaj chwilę - Gemini ma rate limiting
```

## 📱 Wszystkie strony w skrócie

| Strona | Co robi | Czas potrzebny |
|--------|---------|----------------|
| 📊 Dashboard | Metryki, wykresy, top holdings | Natychmiastowy |
| 💬 Partnerzy | Chat z AI (prawdziwy!) | ~5s na odpowiedź |
| 📈 Analiza | Sharpe, VaR, Risk Score | Wymaga historii |
| 🕐 Timeline | Animated charts | Wymaga ≥2 snapshots |
| 🎮 Symulacje | Bullish/Bearish/Transakcje | Natychmiastowy |
| ⚙️ Ustawienia | Theme, auto-refresh, export | Natychmiastowy |

## 🎊 Gotowe!

Dashboard jest w pełni funkcjonalny. Wszystko co planujesz - zrealizowane!

**Enjoy!** 🚀

---

**Quick Links:**
- Dokumentacja pełna: `STREAMLIT_FULL_FEATURES.md`
- Dokumentacja podstawowa: `STREAMLIT_README.md`
- Main program: `gra_rpg.py`
