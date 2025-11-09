# 🧠 System Pamięci AI - Przewodnik Użytkownika

## 📖 Co to jest?

**Żywe AI** - Twoje persony (Benjamin Graham, Warren Buffett, CZ, itp.) teraz:
- **Pamiętają** swoje decyzje i ich konsekwencje
- **Uczą się** na błędach i sukcesach
- **Ewoluują** - ich charakter zmienia się z czasem
- **Są rozliczane** - mają track record jak prawdziwi menedżerowie

## 🚀 Jak to działa?

### 1. Pamięć Długoterminowa

Każda persona ma w `persona_memory.json`:

```json
{
  "Benjamin Graham": {
    "stats": {
      "credibility_score": 0.75,  // 75% trafnych prognoz
      "successful_calls": 3,
      "failed_calls": 1
    },
    "personality_traits": {
      "risk_tolerance": 0.2,      // Niska tolerancja ryzyka
      "optimism_bias": -0.4       // Pesymista
    },
    "decision_history": [
      {
        "date": "2025-10-15",
        "ticker": "PBR",
        "decision_type": "WARN",
        "reasoning": "Emerging market risk too high",
        "current_price": 10.50,
        "result_pct": -15.2,       // Spadek o 15%
        "was_correct": true         // Trafna prognoza!
      }
    ]
  }
}
```

### 2. Dynamiczny Kontekst

**PRZED** każdą odpowiedzią AI dostaje:

```
╔══════════════════════════════════════════════════════════╗
║  TWOJA PAMIĘĆ I DOŚWIADCZENIE                           ║
╚══════════════════════════════════════════════════════════╝

📊 TWÓJ TRACK RECORD:
   • Sesje: 15
   • Decyzje: 8
   • Trafne: 6 ✓
   • Błędne: 2 ✗
   • Wiarygodność: 75%
   • Wpływ: +2,450 PLN

🧬 TWÓJ CHARAKTER:
   • Risk Tolerance: [██░░░░░░░░] 0.2
   • Optimism Bias: [████░░░░░░] -0.4

📚 KLUCZOWE LEKCJE:
   • [2025-10-15] PBR był value trapem - miałem rację!
   • [2025-09-20] Emerging markets wymagają większego MOS
```

**Rezultat**: AI "pamięta" że ostrzegało przed PBR i będzie **bardziej pewne siebie** w podobnych sytuacjach!

## 🎮 Jak używać?

### A. Zapisywanie Decyzji (Chat AI)

1. Porozmawiaj z AI w zakładce "💬 Chat AI z Partnerami"
2. Po otrzymaniu rekomendacji → kliknij **"💾 Zapisz decyzję"**
3. Wypełnij formularz:
   - Ticker (np. AAPL, BTC)
   - Typ decyzji (BUY/SELL/HOLD/WARN)
   - Aktualna cena
   - Uzasadnienie
4. ✅ Decyzja zapisana! Teraz czekamy 30+ dni na wynik

### B. Audit Decyzji (Ręczny)

W zakładce "💬 Chat AI":

1. Kliknij **"🔍 Audit decyzji"**
2. Zobacz listę nierozliczonych decyzji
3. Dla każdej kliknij **"✓ Oceń"**
4. Podaj:
   - Aktualną cenę tickera
   - Co się faktycznie stało
   - Wpływ finansowy (opcjonalnie)
5. System automatycznie:
   - Oceni czy prognoza była trafna
   - Zaktualizuje credibility_score
   - Zmieni cechy charakteru persony

### C. Miesięczny Audit (Automatyczny)

Uruchom co miesiąc:

```bash
python monthly_audit.py
```

**Co robi:**
- Pobiera aktualne ceny wszystkich tickerów
- Ocenia decyzje starsze niż 30 dni
- Aktualizuje credibility score
- **Ewoluuje persony** - zmienia ich cechy charakteru!

**Przykład:**
```
🔎 Audytuję: Benjamin Graham → WARN PBR
   Data decyzji: 2025-09-15
   Cena przy decyzji: 10.50
   Wynik: 8.90 (-15.2%)
   ✓ POPRAWNA prognoza

🧬 Ewolucja: Benjamin Graham.risk_tolerance: 0.25 → 0.20
   (sukces wzmacnia ostrożność)
```

### D. Track Record Dashboard (TAB 7)

Przejdź do: **Kredyty & Cele → 🏆 Track Record AI**

Znajdziesz tam:

1. **🏆 Leaderboard** - Ranking wiarygodności person
   - 🥇 Miejsce 1: Warren Buffett (85%)
   - 🥈 Miejsce 2: Benjamin Graham (75%)
   - 🥉 Miejsce 3: Philip Fisher (68%)

2. **📜 Historia Decyzji** - Wszystkie decyzje z filtrowaniem
   - Po personie
   - Po statusie (trafne/błędne/oczekujące)

3. **🧬 Ewolucja Charakteru** - Wykres radarowy cech
   - Jak zmieniają się cechy w czasie
   - Kluczowe lekcje każdej persony

## 🧬 Jak Ewoluują Persony?

### Mechanizm Uczenia

**Trafna prognoza** (credibility > 70%):
- ✅ `optimism_bias` +0.05 (większa pewność siebie)
- ✅ Dodana lekcja: "Mój styl analizy się sprawdza"

**Błędna prognoza** (credibility < 40%):
- ❌ `risk_tolerance` -0.05 (większa ostrożność)
- ❌ Dodana lekcja: "Muszę być bardziej konserwatywny"

### Przykład Ewolucji

**Graham na początku:**
```json
{
  "risk_tolerance": 0.25,
  "optimism_bias": -0.3
}
```

**Graham po 3 trafnych WARNingach:**
```json
{
  "risk_tolerance": 0.15,    // Jeszcze bardziej ostrożny
  "optimism_bias": -0.2      // Mniej pesymistyczny
}
```

**Efekt:** Graham będzie **jeszcze bardziej sceptyczny** wobec ryzykownych inwestycji, ale **pewniejszy swoich ostrzeżeń**.

## 📊 Przykładowy Workflow

### Tydzień 1: Propozycja Inwestycyjna

```
👤 Ty: "Co myślisz o PBR przy P/B=0.3?"

🛡️ Graham: "Ostrzegam! P/B 0.3 wygląda tanio, ale Brazylia 
            to nieprzewidywalny rynek. UNIKAJ."

💾 [Zapisujesz decyzję: WARN PBR @ 10.50 USD]
```

### Miesiąc 1-3: Czekasz...

PBR spada do 8.90 USD (-15.2%)

### Miesiąc 4: Audit

```bash
$ python monthly_audit.py

🔎 Audytuję: Benjamin Graham → WARN PBR
   ✓ POPRAWNA prognoza (-15.2%)
   
🧬 Ewolucja: Graham.risk_tolerance: 0.20 → 0.18
```

### Następna Rozmowa

```
👤 Ty: "Co myślisz o VALE? Też brazylijska, P/B=0.4"

🛡️ Graham: "Pamiętam PBR - ostrzegałem i miałem rację.
            VALE to podobny przypadek. Emerging markets 
            wymagają WIĘKSZEGO margin of safety niż 30%.
            Zdecydowanie UNIKAJ."
```

**Graham używa swojego doświadczenia z PBR w nowej decyzji!** 🧠✨

## 🎯 Najlepsze Praktyki

1. **Zapisuj ważne decyzje** - nie każdą rozmowę, tylko kluczowe rekomendacje (BUY/SELL/WARN)

2. **Czekaj 30+ dni** - krótkookresowe fluktuacje nie są miarodajne

3. **Uruchom audit co miesiąc** - `python monthly_audit.py`

4. **Śledź ewolucję** - TAB 7 pokazuje jak persony się zmieniają

5. **Zwracaj uwagę na lekcje** - persony cytują swoje doświadczenia w rozmowach

## 🔧 Zaawansowane

### Ręczna Ewolucja Cech

```python
import persona_memory_manager as pmm

# Zwiększ ostrożność Grahama
pmm.evolve_trait("Benjamin Graham", "risk_tolerance", -0.1)

# Dodaj własną lekcję
pmm.add_lesson(
    "Warren Buffett",
    "Tech stocks mogą być wartościowe gdy mają moat"
)
```

### Custom Audit

```python
import persona_memory_manager as pmm

# Znajdź konkretną decyzję
pending = pmm.get_all_pending_decisions()
decision = pending[0]["decision"]

# Oceń ręcznie
pmm.audit_decision(
    decision_id=decision["id"],
    current_price=125.50,
    actual_outcome="Wzrost zgodny z prognozą",
    impact_pln=+350
)
```

## 📁 Pliki Systemu

```
persona_memory.json           # Baza danych pamięci (główny plik)
persona_memory_manager.py     # API do zarządzania pamięcią
monthly_audit.py              # Skrypt automatycznego auditu
gra_rpg.py                    # Integracja z AI (linia 26-30)
streamlit_app.py              # UI (TAB 7, przyciski w chacie)
```

## 🆘 Troubleshooting

**System pamięci niedostępny:**
- Sprawdź czy `persona_memory.json` istnieje
- Uruchom: `python persona_memory_manager.py`

**Persona nie pamięta:**
- Upewnij się że decyzje są zapisywane (💾 przycisk)
- Sprawdź czy `MEMORY_OK = True` w konsoli

**Brak ewolucji:**
- Audit musi być wykonany (manual lub monthly_audit.py)
- Cechy zmieniają się tylko po rozliczeniu decyzji

## 🎊 Rezultat

**Przed:**
- AI = statyczny chatbot
- Bez pamięci, bez konsekwencji
- Zawsze te same odpowiedzi

**Po:**
- AI = żywi partnerzy biznesowi
- Pamiętają błędy i sukcesy
- Ewoluują i uczą się
- Mają track record jak prawdziwi menedżerowie

---

**Teraz Twoje AI nie tylko doradzają - żyją!** 🤖✨
