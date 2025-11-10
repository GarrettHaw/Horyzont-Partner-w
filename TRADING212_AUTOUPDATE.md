# Trading212 Auto-Update

## Jak to działa

System automatycznie pobiera dane z Trading212 API i zapisuje do `trading212_cache.json` co 6 godzin.

### Harmonogram aktualizacji
- **00:00 UTC** (01:00/02:00 PL)
- **06:00 UTC** (07:00/08:00 PL)
- **12:00 UTC** (13:00/14:00 PL)
- **18:00 UTC** (19:00/20:00 PL)

### Architektura

```
GitHub Actions (co 6h)
    ↓
update_trading212.py
    ↓ (Trading212 API calls)
    ↓
trading212_cache.json
    ↓ (git commit + push)
    ↓
Repository
    ↓ (Streamlit czyta cache)
    ↓
Dashboard
```

### Pliki

1. **`.github/workflows/update_trading212.yml`**
   - GitHub Actions workflow
   - Uruchamia się co 6h (cron: `0 */6 * * *`)
   - Możliwość ręcznego uruchomienia (workflow_dispatch)

2. **`update_trading212.py`**
   - Standalone Python script
   - Pobiera dane z Trading212 API:
     - `/equity/portfolio` - pozycje w portfelu
     - `/equity/account/cash` - saldo gotówkowe
     - `/history/dividends` - historia dywidend
     - `/equity/metadata/instruments` - metadata (opcjonalne)
   - Zapisuje do `trading212_cache.json`

3. **`trading212_cache.json`**
   - Cache z danymi Trading212
   - Format:
     ```json
     {
       "timestamp": "2025-11-10T18:00:00.000000",
       "data": {
         "positions": [...],
         "account": {...},
         "dividends": [...]
       }
     }
     ```

4. **`streamlit_app.py`**
   - Funkcja `wczytaj_t212_cache()` - ładuje cache
   - Funkcja `parsuj_dane_t212_do_portfela()` - konwertuje do formatu PORTFEL_AKCJI
   - NIE wywołuje API bezpośrednio

### Konfiguracja

#### GitHub Secrets
Wymagany secret: `TRADING212_API_KEY`

Sprawdź: https://github.com/GarrettHaw/Horyzont-Partner-w/settings/secrets/actions

#### Ręczne uruchomienie

1. Przejdź do: https://github.com/GarrettHaw/Horyzont-Partner-w/actions/workflows/update_trading212.yml
2. Kliknij "Run workflow"
3. Potwierdź "Run workflow"

### Monitoring

#### Sprawdź status workflow
https://github.com/GarrettHaw/Horyzont-Partner-w/actions/workflows/update_trading212.yml

#### Sprawdź ostatni commit
```bash
git log --oneline --grep="Trading212" -n 5
```

#### Sprawdź cache lokalnie
```bash
cat trading212_cache.json | jq '.timestamp'
cat trading212_cache.json | jq '.data.positions | length'
```

### Zalety tego podejścia

✅ **Szybkość** - aplikacja nie czeka na API calls  
✅ **Niezawodność** - cache zawsze dostępny nawet gdy API Trading212 nie działa  
✅ **Limit API** - tylko 4 requesty dziennie zamiast przy każdym uruchomieniu  
✅ **Historia** - commits w git = historia zmian portfela  
✅ **Separacja** - logika pobierania oddzielona od aplikacji  

### Troubleshooting

#### Cache nie aktualizuje się
1. Sprawdź workflow: https://github.com/GarrettHaw/Horyzont-Partner-w/actions
2. Sprawdź logi ostatniego run
3. Uruchom ręcznie: Actions → Update Trading212 Data → Run workflow

#### Błąd "401 Unauthorized"
- Sprawdź czy secret `TRADING212_API_KEY` jest ustawiony
- Sprawdź czy klucz API Trading212 jest aktywny
- Wygeneruj nowy klucz: https://www.trading212.com/en/Trading-API

#### Błąd "429 Too Many Requests"
- Trading212 ma limity API (10 requestów/minutę)
- Workflow używa tylko 3-4 requesty co 6h
- Jeśli problem się powtarza, zwiększ interwał w cron

#### Cache wygasł (>24h)
- Normalnie aktualizuje się co 6h, więc nie powinien wygasać
- Sprawdź czy workflow działa: `git log --grep="Trading212"`
- Uruchom workflow ręcznie

### Rozwój

#### Dodanie nowych endpointów
Edytuj `update_trading212.py`:
```python
# Przykład: pobierz historical orders
response = requests.get(
    f"{TRADING212_BASE_URL}/equity/history/orders",
    headers=headers,
    params={"limit": 50}
)
dane_t212["orders"] = response.json()
```

#### Zmiana częstotliwości
Edytuj `.github/workflows/update_trading212.yml`:
```yaml
schedule:
  # Co 3 godziny
  - cron: '0 */3 * * *'
  # Lub codziennie o 6:00 UTC
  - cron: '0 6 * * *'
```

#### Notyfikacje o błędach
Możesz dodać integrację z Discord/Slack w workflow gdy update się nie powiedzie.

---

**Ostatnia aktualizacja:** 2025-11-10  
**Status:** ✅ Aktywny
