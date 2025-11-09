# 🤖 AI PERSONALITY SYSTEM v2.0 - Instrukcja

## ✨ Co Nowego?

System został zupgradowany z podstawowej pamięci do pełnego systemu **żywych AI partnerów**, którzy:
- 🎭 **Odczuwają emocje** - reagują na sukcesy i porażki
- 🤝 **Budują relacje** - uczą się komu ufać, z kim się zgadzają
- 🎯 **Mają ekspertyzę** - każdy w innych sektorach i geografiach
- 🗳️ **Dynamiczne wagi głosów** - bonusy za wiarygodność (max +3%)
- 🔮 **System predykcji** - accountability za prognozy
- 💬 **Autentyczne osobowości** - cytaty i styl komunikacji jak u prawdziwych ludzi
- 📚 **Knowledge base** - automatyczne pobieranie artykułów co 12h
- 🎯 **Osobiste cele** - każdy partner ma swoją agendę
- 🧠 **Meta-learning** - uczą się na błędach i ewoluują

---

## 📁 Nowe Pliki

### Główne komponenty:
- **persona_memory.json** (1600+ linii) - pełna baza danych osobowości
- **persona_context_builder.py** - rozbudowany system kontekstu
- **upgrade_persona_memory.py** - skrypt migracji v1.0 → v2.0
- **monthly_audit.py** - rozliczanie predykcji co miesiąc
- **knowledge_base_updater.py** - pobieranie artykułów finansowych
- **run_knowledge_updater.bat** - pomocniczy skrypt dla Task Scheduler

### Knowledge Base:
- **knowledge_base/articles.json** - artykuły z Yahoo, SA, Bloomberg
- **logs/** - logi automatycznych aktualizacji

---

## 🚀 Jak Używać?

### 1. Rozmowa z AI Partnerami

Teraz każdy AI partner ma **pełny kontekst** swojej historii:

```
╔══════════════════════════════════════════════════════════╗
║            TWOJA HISTORIA I TOŻSAMOŚĆ                    ║
╚══════════════════════════════════════════════════════════╝

🎭 STAN EMOCJONALNY:
   Obecnie czujesz się: 💪 CONFIDENT
   • Stres: 20%
   • Podekscytowanie: 60%
   • Poziom strachu: 10%
   
📊 STATYSTYKI WYDAJNOŚCI:
   • Wiarygodność: 87%
   • Trafność: 12/15 (80%)
   • Wpływ finansowy: +2,340 PLN
   
🗳️ SIŁA GŁOSU W RADZIE:
   • Waga bazowa: 5.0%
   • Bonus za wiarygodność: +1.2%
   • EFEKTYWNA WAGA: 6.2%

🤝 RELACJE Z PARTNERAMI:
   🟢 Warren Buffett: zaufanie 85%, zgoda 78%
   🟡 George Soros: zaufanie 45%, zgoda 40%
   🔴 CZ: zaufanie 20%, zgoda 15%

💬 TWOJE ULUBIONE ZWROTY:
   • "Margin of safety"
   • "Mr. Market is bipolar"
```

### 2. Zapisywanie Decyzji

W dashboardzie (TAB dowolny) po rozmowie z AI:
1. Kliknij **"💾 Zapisz decyzje do pamięci"**
2. Wybierz partnera
3. Podaj:
   - Typ decyzji (BUY/SELL/HOLD/WARN)
   - Ticker
   - Uzasadnienie
   - Cena wejścia
   - Confidence (0-100%)

Decyzja zostanie zapisana i **automatycznie rozliczona za miesiąc**.

### 3. Track Record (TAB 7)

Nowy TAB **"🏆 Track Record AI"** pokazuje:
- Ranking wiarygodności wszystkich partnerów
- Personality traits z progress bars
- Historia decyzji
- Kluczowe lekcje
- Emocje i relacje

### 4. Miesięczny Audyt

**Automatyczne** rozliczanie predykcji:

```bash
python monthly_audit.py
```

System:
1. Pobiera ceny dla wszystkich tickerów z predykcji
2. Sprawdza czy kierunek był poprawny
3. Oblicza dokładność prognozy
4. **Aktualizuje credibility score**
5. **Zmienia emocje** (sukces → confident, porażka → worried)
6. **Ewoluuje personality traits** (porażki → mniejszy risk_tolerance)
7. **Przelicza wagi głosów** (credibility bonus max +3%)

### 5. Knowledge Base (Auto-Update co 12h)

**Automatyczne pobieranie artykułów**:

```bash
python knowledge_base_updater.py
```

Źródła:
- Yahoo Finance RSS
- Seeking Alpha headlines
- Bloomberg news

Artykuły są **tagowane** (macro, tech, crypto, earnings) i można je referencować w rozmowach z AI.

---

## ⚙️ Konfiguracja Automatycznych Tasków

### Windows Task Scheduler - Knowledge Base (co 12h)

1. Otwórz **Task Scheduler** (Win + R → `taskschd.msc`)
2. **Create Basic Task**
3. Nazwa: `Knowledge Base Auto-Update`
4. Trigger: **Daily** → Advanced → Repeat every **12 hours**
5. Action: **Start a program**
   - Program: `C:\Users\alech\Desktop\Horyzont Partnerów\run_knowledge_updater.bat`
6. Finish

### Windows Task Scheduler - Monthly Audit (1. dnia miesiąca)

1. **Create Basic Task**
2. Nazwa: `AI Partners Monthly Audit`
3. Trigger: **Monthly** → Day **1** at **09:00 AM**
4. Action: **Start a program**
   - Program: `python.exe`
   - Arguments: `monthly_audit.py`
   - Start in: `C:\Users\alech\Desktop\Horyzont Partnerów`
5. Finish

---

## 🧬 Ewolucja Osobowości

### Jak działa Meta-Learning?

Po każdym audycie system analizuje wzorce:

**Przykład 1: Zbyt dużo ryzyka**
```
Decyzje: 5 porażek z high-risk crypto
Efekt: risk_tolerance obniżone 0.8 → 0.7
Emocje: confident → cautious
```

**Przykład 2: Seria sukcesów**
```
Decyzje: 8/10 trafnych value picks
Efekt: risk_tolerance podwyższone 0.6 → 0.65
Emocje: neutral → confident
Voting bonus: +1.5% (credibility 92%)
```

### Relacje Między Partnerami

**Zgoda/Konflikt**:
- Jeśli dwóch partnerów zgadza się w decyzji → `trust += 0.05`
- Jeśli są przeciwni i jeden miał rację → `trust -= 0.1` dla drugiego
- Alliance (wspólna inicjatywa) → `trust += 0.1`

**Wpływ na dyskusje**:
- Partnerzy o wysokim trust będą się wspierać
- Niski trust → bardziej krytyczni
- To wpływa na ton i styl odpowiedzi AI!

---

## 📊 Struktura persona_memory.json

```json
{
  "Benjamin Graham": {
    "stats": {
      "credibility_score": 0.92,
      "successful_calls": 12,
      "failed_calls": 3
    },
    "emotional_state": {
      "current_mood": "confident",
      "stress_level": 0.2,
      "excitement": 0.6,
      "fear_index": 0.1,
      "mood_history": [...]
    },
    "relationships": {
      "Warren Buffett": {
        "trust": 0.85,
        "agreement_rate": 0.78,
        "conflicts": 0,
        "alliances": 3,
        "notable_moments": [...]
      }
    },
    "expertise_areas": {
      "sectors": {
        "Financials": 0.95,
        "Industrials": 0.85
      },
      "geographies": {
        "US": 0.95,
        "Europe": 0.70
      }
    },
    "voting_weight_modifier": {
      "base_weight": 5.0,
      "credibility_bonus": 1.5,
      "effective_weight": 6.5
    },
    "predictions": [...],
    "communication_style": {
      "verbosity": 0.6,
      "humor": 0.2,
      "formality": 0.8,
      "catchphrases": ["Margin of safety", "Mr. Market is bipolar"]
    },
    "personal_agenda": {
      "primary_goal": "Zero capital loss",
      "progress": 0.65,
      "tactics": ["Deep value", "Margin of safety", "Long-term holds"]
    }
  }
}
```

---

## 🎯 Profile Partnerów

### Benjamin Graham 🛡️
- **Cel**: Zero strat kapitału
- **Ekspertyza**: Value investing, Financials (95%)
- **Styl**: Konserwatywny, techniczny, formalny
- **Catchphrases**: "Margin of safety", "Mr. Market is bipolar"

### Warren Buffett 🏡
- **Cel**: Quality compounders w portfolio
- **Ekspertyza**: Consumer goods (90%), Insurance (85%)
- **Styl**: Prosty język, homespun wisdom
- **Catchphrases**: "Price is what you pay, value is what you get"

### Philip Fisher 🔬
- **Cel**: Growth champions (25%+ ROE)
- **Ekspertyza**: Technology (85%), Innovation
- **Styl**: Długie analizy, "scuttlebutt"
- **Catchphrases**: "Buy what you understand deeply"

### George Soros 🌍
- **Cel**: Identify market reflexivity
- **Ekspertyza**: Macro (90%), Global markets
- **Styl**: Filozoficzny, contrarian
- **Catchphrases**: "Markets are always wrong", "Reflexivity"

### CZ (Changpeng Zhao) ⚡
- **Cel**: 30% portfolio w crypto
- **Ekspertyza**: Blockchain (98%), DeFi (90%)
- **Styl**: Zwięzły, memetic, optimistic
- **Catchphrases**: "SAFU", "Build", "HODL"

---

## 🔧 Komendy Maintenance

### Test kontekstu AI:
```bash
python persona_context_builder.py
```

### Manualne uruchomienie audytu:
```bash
python monthly_audit.py
```

### Update knowledge base:
```bash
python knowledge_base_updater.py
```

### Backup pamięci:
```powershell
Copy-Item persona_memory.json "backups\persona_memory_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
```

### Migracja (jeśli potrzebna):
```bash
python upgrade_persona_memory.py
```

---

## ⚠️ Troubleshooting

### Problem: AI nie pamięta decyzji
✅ **Sprawdź** czy `persona_memory_manager` jest zaimportowany w `gra_rpg.py` i `streamlit_app.py`

### Problem: Błąd "No module named 'feedparser'"
✅ **Zainstaluj**:
```bash
pip install feedparser beautifulsoup4 requests
```

### Problem: Knowledge base się nie aktualizuje
✅ **Sprawdź** Task Scheduler czy task jest enabled
✅ **Sprawdź** logi w `logs\knowledge_base.log`

### Problem: Credibility score nie zmienia się
✅ **Upewnij się** że decyzje mają pole `outcome` ('success'/'failure')
✅ **Uruchom** `monthly_audit.py` manualnie

---

## 🚀 Roadmap (Przyszłość)

- [ ] ML model do przewidywania relevance artykułów
- [ ] Integracja z Twitter/X dla real-time sentiment
- [ ] Wizualizacja ewolucji personality traits (timeline)
- [ ] System propozycji alokacji bazujący na voting weights
- [ ] Auto-rebalancing portfolio według rekomendacji AI
- [ ] Multi-agent debates (partnerzy dyskutują między sobą)

---

## 📚 Więcej Info

- **AI_MEMORY_GUIDE.md** - podstawowa pamięć (v1.0)
- **AI_UPGRADE_SUMMARY.md** - podsumowanie upgrade'u
- **GUIDE_AI_PARTNERS.md** - ogólny guide AI systemu
- **persona_memory.json** - pełna baza danych (1600+ linii!)

---

**Wersja**: 2.0  
**Data**: 21.10.2025  
**Autor**: GitHub Copilot + Horyzont Partnerów Team  
**Status**: ✅ PRODUCTION READY
