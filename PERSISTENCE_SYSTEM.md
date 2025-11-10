# 💾 System Persystencji Danych

## 🎯 Problem: Streamlit Cloud ma tylko read-only filesystem

**Streamlit Cloud NIE MOŻE zapisywać plików** - każdy restart aplikacji kasuje lokalne zmiany.

**Rozwiązanie:** 3-tier persistence system z GitHub jako "bazą danych"

---

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────┐
│  1. SESSION STATE (RAM)                             │
│  ✅ Najszybsze - dane dostępne natychmiast          │
│  ❌ Znika po zamknięciu przeglądarki                │
└─────────────────────────────────────────────────────┘
                    ↓ zapisz
┌─────────────────────────────────────────────────────┐
│  2. SYNC QUEUE (session_state)                      │
│  📦 Kolejka plików do synchronizacji                │
│  💾 Widoczna w sidebar "Oczekujące pliki"          │
└─────────────────────────────────────────────────────┘
                    ↓ co godzinę
┌─────────────────────────────────────────────────────┐
│  3. GITHUB REPOSITORY                               │
│  ✅ Trwałe przechowywanie                           │
│  ✅ Historia zmian (git commits)                    │
│  ✅ Backup wszystkich danych                        │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Co jest zapisywane (12 plików)

### **Krytyczne - Dane użytkownika:**
1. **wyplaty.json** - Wypłaty właściciela
2. **wydatki.json** - Wydatki firmy
3. **kredyty.json** - Kredyty i długi
4. **cele.json** - Cele finansowe
5. **krypto.json** - Portfolio kryptowalut

### **Pamięć AI - Wiedza partnerów:**
6. **persona_memory.json** - Długoterminowa pamięć partnerów (NIEOGRANICZONA)
7. **partner_conversations.json** - Bieżące rozmowy z partnerami
8. **autonomous_conversations.json** - Autonomiczne dyskusje AI

### **Konfiguracja i Historia:**
9. **notification_config.json** - Ustawienia powiadomień email
10. **daily_snapshots.json** - Snapshoty portfela
11. **portfolio_history.json** - Historia inwestycji
12. **api_usage.json** - Statystyki użycia API

---

## 🔄 Jak działa synchronizacja?

### **Automatyczna (co godzinę):**
```
GitHub Actions workflow: sync_data.yml
Harmonogram: cron '0 * * * *' (każda pełna godzina)

Kroki:
1. Uruchom sync_data.py
2. Sprawdź wszystkie 12 plików
3. Commituj zmiany do repo
4. Message: "🔄 Auto-sync: 2025-11-09 15:00 UTC"
```

### **Manualna (przycisk):**
```
Sidebar → "💾 Zapisz teraz"
Wymaga: GITHUB_TOKEN w secrets
Efekt: Natychmiastowa synchronizacja przez GitHub API
```

### **Backup (download):**
```
Sidebar → "📥 Pobierz backup"
Efekt: ZIP ze wszystkimi oczekującymi plikami
Bezpieczeństwo: Lokalna kopia bez czekania na sync
```

---

## 🧠 Pamięć AI Partnerów - Specjalne funkcje

### **Nieograniczona wiedza:**
- ❌ **BRAK LIMITU** rozmów (poprzednio 100)
- ✅ Każda rozmowa jest zapisana na zawsze
- ✅ Partnerzy uczą się z całej historii

### **Głęboki kontekst:**
- 📚 **20 ostatnich rozmów** w kontekście (poprzednio 5)
- 📝 **Pełne teksty** zamiast skrótów
- 💼 **Snapshoty portfela** z każdej rozmowy
- 📊 **Statystyki** - total_messages, first/last interaction

### **Format pamięci:**
```json
{
  "Michael_Burry": {
    "partner_name": "Michael Burry",
    "conversations": [
      {
        "timestamp": "2025-11-09T14:23:45",
        "user_message": "Czy powinienem sprzedać Bitcoin?",
        "ai_response": "Pamiętaj że mówiłeś mi...",
        "portfolio_snapshot": {
          "total_value": 145230,
          "debt": 23400
        }
      }
    ],
    "statistics": {
      "total_messages": 237,
      "first_interaction": "2025-01-15T10:00:00",
      "last_interaction": "2025-11-09T14:23:45"
    }
  }
}
```

---

## ⚙️ Konfiguracja

### **1. Wymagane sekrety (Streamlit Cloud):**
```toml
# .streamlit/secrets.toml

# Dla manualnego syncu (opcjonalne)
GITHUB_TOKEN = "ghp_xxxxx"  

# Inne (jeśli używasz)
GOOGLE_API_KEY = "..."
TRADING212_API_KEY = "..."
```

### **2. Uprawnienia GitHub Actions:**
W `.github/workflows/*.yml`:
```yaml
permissions:
  contents: write  # Potrzebne do commit
```

---

## 🚨 Ostrzeżenie przed zamknięciem

JavaScript `beforeunload` alert:
```javascript
window.addEventListener('beforeunload', (e) => {
  e.preventDefault();
  return 'Masz niezapisane zmiany! Kliknij "💾 Zapisz teraz"';
});
```

**Zachowanie:**
- Przeglądarka pokaże alert przy zamykaniu
- Dane w session_state przetrwają refresh
- Dane znikną przy zamknięciu przeglądarki
- Użytkownik ma szansę kliknąć "Zapisz teraz"

---

## 📊 Monitoring

### **Sidebar widget:**
```
┌─────────────────────────────────────┐
│ 💾 SYNCHRONIZACJA DANYCH            │
├─────────────────────────────────────┤
│ ⏰ Ostatnia: 2025-11-09 14:00 UTC   │
│ 📦 Oczekujące pliki: 3              │
│                                     │
│ [💾 Zapisz teraz] [📥 Pobierz]     │
└─────────────────────────────────────┘
```

### **Logi GitHub Actions:**
https://github.com/GarrettHaw/Horyzont-Partner-w/actions

---

## 🛠️ Troubleshooting

### **"Dane zniknęły po restarcie"**
- ✅ Sprawdź czy GitHub Actions działają
- ✅ Zobacz logi: Settings → Actions
- ✅ Pobierz backup (📥) i sprawdź zawartość

### **"Przycisk 'Zapisz teraz' nie działa"**
- ❌ Brak GITHUB_TOKEN w secrets
- ✅ Dodaj według GITHUB_TOKEN_SETUP.md
- ✅ Użyj manualnego triggera na GitHub

### **"Sync nie commituje"**
- ⚠️ Brak zmian w plikach
- ✅ Git sprawdza diff - commituje tylko zmiany
- ✅ Zobacz workflow logs

---

## 🎓 Dla programistów

### **Użycie w kodzie:**
```python
from persistent_storage import load_persistent_data, save_persistent_data

# Zapis
data = {'kredyty': [{'kwota': 5000}]}
save_persistent_data('kredyty.json', data)

# Odczyt
kredyty = load_persistent_data('kredyty.json')
if kredyty is None:
    kredyty = {'kredyty': []}
```

### **Fallback pattern:**
```python
if PERSISTENT_OK:
    data = load_persistent_data('file.json')
else:
    # Lokalny development
    with open('file.json', 'r') as f:
        data = json.load(f)
```

### **Auto-save pattern:**
```python
def add_message(msg):
    st.session_state.messages.append(msg)
    if PERSISTENT_OK:
        save_persistent_data('messages.json', 
                           st.session_state.messages)
```

---

## ✅ Checklist wdrożenia

- [x] persistent_storage.py zaimportowany
- [x] PERSISTENT_FILES lista zaktualizowana (12 plików)
- [x] sync_data.py z poprawnymi default structures
- [x] .github/workflows/sync_data.yml z harmonogramem
- [x] Wszystkie save_* funkcje używają save_persistent_data()
- [x] Wszystkie load_* funkcje używają load_persistent_data()
- [x] Sidebar widget pokazuje status syncu
- [x] JavaScript beforeunload warning
- [x] GITHUB_TOKEN_SETUP.md dokumentacja

---

**System gotowy! 🚀**

Dane są bezpieczne, partnerzy pamiętają wszystko, synchronizacja działa automatycznie.
