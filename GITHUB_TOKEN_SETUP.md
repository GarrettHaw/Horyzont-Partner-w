# 🔑 Konfiguracja GITHUB_TOKEN

## Krok 1: Wygeneruj Personal Access Token

1. **Idź na GitHub:**
   - https://github.com/settings/tokens

2. **Kliknij "Generate new token" → "Generate new token (classic)"**

3. **Wypełnij formularz:**
   - **Note:** `Horyzont Partners - Streamlit Sync`
   - **Expiration:** `No expiration` (lub 90 days)
   - **Select scopes:** ✅ Zaznacz tylko:
     - `repo` (Full control of private repositories)
       - ✅ repo:status
       - ✅ repo_deployment
       - ✅ public_repo
       - ✅ repo:invite
       - ✅ security_events

4. **Kliknij "Generate token"**

5. **SKOPIUJ TOKEN** (pokazuje się tylko raz!)
   - Format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - Zapisz w bezpiecznym miejscu

---

## Krok 2: Dodaj do Streamlit Cloud Secrets

1. **Idź na Streamlit Cloud:**
   - https://share.streamlit.io/

2. **Wybierz swoją aplikację** (Horyzont Partners)

3. **Kliknij ⚙️ Settings → Secrets**

4. **Dodaj na końcu pliku secrets.toml:**

```toml
# GitHub API - automatyczna synchronizacja danych
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

5. **Kliknij "Save"**

6. **Poczekaj 30 sekund** na restart aplikacji

---

## Krok 3: Testuj!

1. **Odśwież aplikację** w przeglądarce
2. **Dodaj jakieś dane** (np. wypłatę)
3. **W sidebar kliknij "💾 Zapisz teraz"**
4. **Powinno pokazać:**
   ```
   ✅ Synchronizacja uruchomiona! 
   Sprawdź status w GitHub Actions.
   ```

5. **Sprawdź GitHub Actions:**
   - https://github.com/GarrettHaw/Horyzont-Partner-w/actions
   - Powinien być nowy workflow run "Sync Data Files"

---

## ✅ Gotowe!

Od teraz:
- Kliknij "💾 Zapisz teraz" → instant sync!
- Nie musisz ręcznie otwierać GitHub Actions
- Dane zapisują się w <1 minutę

---

## 🔒 Bezpieczeństwo

- Token ma dostęp TYLKO do Twojego repo
- Streamlit Secrets są szyfrowane
- Token można zawsze zresetować w GitHub Settings
- Nigdy nie udostępniaj tokena publicznie!

---

## ❓ Problemy?

**Błąd 401 (Unauthorized):**
- Token wygasł lub jest nieprawidłowy
- Wygeneruj nowy token

**Błąd 404 (Not Found):**
- Sprawdź czy workflow `sync_data.yml` istnieje
- Upewnij się że token ma scope `repo`

**Timeout:**
- GitHub API może być przeciążony
- Spróbuj ponownie za chwilę
