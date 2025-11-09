# ✅ POST-UPGRADE CHECKLIST

## 🎉 Gratulacje! System v2.0 jest gotowy!

Przed pełnym użytkowaniem sprawdź poniższe punkty:

---

## 1. ✅ Weryfikacja Instalacji

### Pliki Utworzone
- [ ] `persona_context_builder.py` (327 linii)
- [ ] `knowledge_base_updater.py` (353 linie)
- [ ] `upgrade_persona_memory.py` (skrypt migracji)
- [ ] `run_knowledge_updater.bat` (helper)
- [ ] `AI_PERSONALITY_SYSTEM_V2.md` (dokumentacja)
- [ ] `UPGRADE_SUMMARY_V2.md` (podsumowanie)
- [ ] `QUICK_REFERENCE_V2.md` (quick ref)
- [ ] `knowledge_base/articles.json` (9 artykułów)
- [ ] `logs/` folder

### Pliki Zmodyfikowane
- [ ] `persona_memory.json` (1626 linii, było ~220)
- [ ] `gra_rpg.py` (dodane v2.0 imports)
- [ ] `streamlit_app.py` (TAB 7 rozbudowany)
- [ ] `monthly_audit.py` (v2.0 featury)

### Backupy
- [ ] `persona_memory_backup_20251021_173914.json` istnieje

---

## 2. ✅ Testy Funkcjonalności

### Test 1: Context Builder
```powershell
python persona_context_builder.py
```
**Oczekiwany output**: 
- Kontekst Benjamina Grahama (~1344 chars)
- Kontekst Warrena Buffetta (~1344 chars)
- Brak błędów

**Status**: [ ] Działa | [ ] Problem

---

### Test 2: Knowledge Base
```powershell
python knowledge_base_updater.py
```
**Oczekiwany output**:
```
======================================================================
📰 KNOWLEDGE BASE AUTO-UPDATE
...
✅ Pobrano X nowych artykułów
✅ Zapisano Y artykułów do knowledge_base\articles.json
======================================================================
```

**Status**: [ ] Działa | [ ] Problem

---

### Test 3: Imports v2.0
```powershell
python -c "from persona_context_builder import build_enhanced_context, get_emotional_modifier; print('✅ v2.0 imports OK')"
```
**Oczekiwany output**: `✅ v2.0 imports OK`

**Status**: [ ] Działa | [ ] Problem

---

### Test 4: Streamlit (TAB 7)
1. Uruchom: `streamlit run streamlit_app.py`
2. Otwórz przeglądarkę: http://localhost:8501
3. Przejdź do TAB 7 "🏆 Track Record AI"
4. Sprawdź sekcje:
   - [ ] Ranking Wiarygodności (leaderboard)
   - [ ] Historia Decyzji (tabela)
   - [ ] Ewolucja Charakteru (radar chart)
   - [ ] 🎭 Stan Emocjonalny (NOWE v2.0)
   - [ ] 🤝 Relacje z Partnerami (NOWE v2.0)
   - [ ] 🗳️ Siła Głosu w Radzie (NOWE v2.0)
   - [ ] 🎯 Obszary Ekspertyzy (NOWE v2.0)
   - [ ] 🎯 Osobista Agenda (NOWE v2.0)
   - [ ] 💬 Styl Komunikacji (NOWE v2.0)

**Status**: [ ] Wszystko działa | [ ] Problemy: ________________

---

### Test 5: AI Partner (with v2.0 context)
1. W dowolnym TAB z chatem
2. Zadaj pytanie Benjaminowi Grahamowi
3. Sprawdź czy odpowiedź:
   - [ ] Jest w jego stylu (konserwatywna, technical)
   - [ ] Zawiera catchphrase ("Margin of safety")
   - [ ] Odnosi się do jego stanu emocjonalnego
   - [ ] Wspomina o jego celu ("Zero capital loss")

**Status**: [ ] Działa świetnie | [ ] Wymaga poprawek

---

## 3. ✅ Konfiguracja Task Scheduler

### Task #1: Knowledge Base (co 12h)

**Kroki**:
1. Win + R → `taskschd.msc` → Enter
2. "Create Basic Task"
3. Nazwa: `Knowledge Base Auto-Update`
4. Opis: `Automatic article fetching every 12 hours`
5. Trigger: **Daily** at 06:00 AM
6. Advanced → ☑ "Repeat task every" → **12 hours**
7. Duration: **1 day**
8. Action: **Start a program**
   - Program/script: `C:\Users\alech\Desktop\Horyzont Partnerów\run_knowledge_updater.bat`
9. Finish
10. Right-click task → Properties → Settings:
    - ☑ "Run task as soon as possible after scheduled start is missed"
    - ☑ "Stop task if it runs longer than" → **30 minutes**

**Status**: [ ] Skonfigurowane | [ ] TODO

---

### Task #2: Monthly Audit (1. dnia miesiąca)

**Kroki**:
1. Win + R → `taskschd.msc` → Enter
2. "Create Basic Task"
3. Nazwa: `AI Partners Monthly Audit`
4. Opis: `Evaluate predictions and update credibility scores`
5. Trigger: **Monthly** → Day **1** at **09:00 AM**
6. Action: **Start a program**
   - Program/script: `python.exe`
   - Arguments: `monthly_audit.py`
   - Start in: `C:\Users\alech\Desktop\Horyzont Partnerów`
7. Finish

**Status**: [ ] Skonfigurowane | [ ] TODO

---

## 4. ✅ Pierwsza Decyzja (Test Flow)

### Scenariusz: Zapisz pierwszą decyzję i rozlicz ją

1. **Zadaj pytanie AI**:
   - Otwórz dowolny TAB z chatem
   - Wybierz partnera (np. Warren Buffett)
   - Zapytaj: "Co sądzisz o AAPL? Czy powinienem kupić?"

2. **Zapisz decyzję**:
   - [ ] Kliknij "💾 Zapisz decyzje do pamięci"
   - [ ] Wypełnij:
     - Typ: `BUY`
     - Ticker: `AAPL`
     - Cena: (aktualna cena AAPL, np. 175.50)
     - Confidence: `75`
     - Uzasadnienie: (skopiuj z odpowiedzi AI)
   - [ ] Zapisz

3. **Sprawdź w persona_memory.json**:
   ```powershell
   cat persona_memory.json | Select-String "AAPL"
   ```
   - [ ] Decyzja jest zapisana

4. **Symuluj miesięczny audyt** (za 30 dni):
   - Ręcznie zmień `due_date` w persona_memory.json na dzisiejszą datę
   - Uruchom: `python monthly_audit.py`
   - [ ] Credibility się zmieniło
   - [ ] Emotional state zaktualizowany
   - [ ] Voting weight bonus obliczony

**Status**: [ ] Test przeszedł | [ ] Problem: ________________

---

## 5. ✅ Dokumentacja

### Przeczytaj kluczowe pliki:
- [ ] `AI_PERSONALITY_SYSTEM_V2.md` (pełna instrukcja)
- [ ] `UPGRADE_SUMMARY_V2.md` (co zostało zrobione)
- [ ] `QUICK_REFERENCE_V2.md` (quick ref)

### Zrozum koncepty:
- [ ] Jak działają emotions (mood, stress, fear)
- [ ] Jak działają relationships (trust, agreement_rate)
- [ ] Jak działa voting weight bonus (credibility → +/- %)
- [ ] Jak działa monthly audit (auto-evaluation)
- [ ] Jak działa knowledge base (auto-update co 12h)

**Status**: [ ] Przeczytane | [ ] TODO

---

## 6. ✅ Backup Strategy

### Automatyczne backupy (opcjonalne)

**Windows Backup Script** (uruchamiaj raz w tygodniu):
```powershell
# backup_persona_memory.ps1
$date = Get-Date -Format 'yyyyMMdd_HHmmss'
$source = "persona_memory.json"
$dest = "backups\persona_memory_$date.json"

New-Item -Path "backups" -ItemType Directory -Force
Copy-Item $source $dest
Write-Host "✅ Backup utworzony: $dest"

# Usuń backupy starsze niż 30 dni
Get-ChildItem "backups\*.json" | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item
```

**Status**: [ ] Skonfiguowane | [ ] TODO

---

## 7. ✅ Optymalizacja (Opcjonalne)

### Jeśli plik persona_memory.json rośnie >5000 linii:
- [ ] Rozważ migrację do SQLite
- [ ] Archiwizuj stare decyzje (>6 miesięcy)
- [ ] Ogranicz mood_history do 10 (obecnie 20)

### Jeśli token usage jest zbyt wysoki:
- [ ] Zmniejsz limit w `build_enhanced_context(name, limit=3)`
- [ ] Skróć catchphrases (max 2 zamiast 3)
- [ ] Ogranicz knowledge base do 5 artykułów

**Status**: [ ] Nie potrzeba | [ ] TODO

---

## 8. ⚠️ Known Issues

### Możliwe Problemy:

1. **Plotly warnings** (niski priorytet):
   - Deprecated keyword arguments
   - Nie wpływa na funkcjonalność
   - Fix: Znajdź wszystkie `st.plotly_chart()` i dodaj `config={...}`

2. **Seeking Alpha scraping**:
   - Może się zepsuć jeśli zmienią HTML
   - Fix: Zaktualizuj selektory w `knowledge_base_updater.py`

3. **Progress bar crashes** (FIXED):
   - Było: Negative values w traits → crash
   - Jest: Normalizacja do [0, 1] range

**Status**: [ ] Aware | [ ] Need more info

---

## 🎉 Final Check

### Wszystko gotowe?
- [ ] Wszystkie testy przeszły ✅
- [ ] Task Scheduler skonfigurowany ✅
- [ ] Dokumentacja przeczytana ✅
- [ ] Backup strategy zaplanowana ✅
- [ ] Pierwsza decyzja zapisana i rozliczona ✅

### Jeśli TAK → System jest **PRODUCTION READY** 🚀

### Jeśli NIE → Sprawdź sekcje z problemami i:
1. Zobacz `QUICK_REFERENCE_V2.md` → Troubleshooting
2. Sprawdź logi: `logs\knowledge_base.log`
3. Przetestuj manualnie każdy feature
4. W razie problemów: rollback do backupu

---

## 📞 Support

### Gdzie szukać pomocy?
- **Dokumentacja**: `AI_PERSONALITY_SYSTEM_V2.md`
- **Quick Ref**: `QUICK_REFERENCE_V2.md`
- **Upgrade Summary**: `UPGRADE_SUMMARY_V2.md`

### Rollback (jeśli coś poszło nie tak):
```powershell
# Przywróć backup
Copy-Item persona_memory_backup_20251021_173914.json persona_memory.json

# Restart Streamlit
# Ctrl+C w terminalu, potem:
streamlit run streamlit_app.py
```

---

**Checklist Version**: 1.0  
**Date**: 21.10.2025  
**System Version**: v2.0  
**Status**: Ready for Production ✅

---

## 🚀 Next Steps

Po ukończeniu checklisty:
1. **Użyj systemu** przez tydzień i monitoruj
2. **Sprawdź logi** po pierwszej auto-aktualizacji (12h)
3. **Poczekaj na pierwszy audit** (1. dnia miesiąca)
4. **Enjoy** żyjące AI persony! 🎊

**Powodzenia!** 🎉
