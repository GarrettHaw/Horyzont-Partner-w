# 🤖 Modele AI używane przez Partnerów

## Przegląd Systemu

### **Główny Model: Google Gemini Pro**
Wszyscy partnerzy AI (z wyjątkiem Nexus) używają **Google Gemini Pro** jako podstawowego silnika AI.

---

## Podział według Partnerów

### 1. **Nexus** 🤖
- **Model**: Niestandardowy (Nexus AI Engine)
- **Ścieżka**: `nexus_ai_engine.py` → dedykowany silnik
- **Fallback**: Gemini Pro (gdy Nexus zawiedzie)
- **Specjalizacja**: Meta-analiza, koordynacja Rady, głosowania
- **Kod koloru**: Cyan (`\033[96m`)

### 2. **Warren Buffett** 🎯
- **Model**: Google Gemini Pro
- **System Instruction**: Ton value investing, long-term perspective
- **Specjalizacja**: Value investing, fundamentals, long-term strategy
- **Kod koloru**: Zielony (`\033[92m`)

### 3. **George Soros** 🌍
- **Model**: Google Gemini Pro
- **System Instruction**: Ton macro trading, reflexivity theory
- **Specjalizacja**: Makroekonomia, geopolityka, timing rynkowy
- **Kod koloru**: Czerwony (`\033[91m`)

### 4. **Changpeng Zhao (CZ)** ₿
- **Model**: OpenRouter - Llama-4-scout (Mixtral) :free
- **Provider**: OpenRouter.ai
- **System Instruction**: Ton crypto innovation, risk management
- **Specjalizacja**: Kryptowaluty, blockchain, tech innovation
- **Kod koloru**: Biały (`\033[97m`)
- **Koszt**: DARMOWY (free tier OpenRouter)

### 5. **Inni Partnerzy** (jeśli dodani)
- **Model**: Google Gemini Pro (domyślnie)
- **Konfiguracja**: Z `persona_memory.json`
- **Kod koloru**: Niebieski (`\033[94m`)

---

## Architektura Wywołań

```
User Input
    ↓
send_to_ai_partner(partner_name, message)
    ↓
    ├─→ [Nexus?] → nexus_ai_engine.py → Nexus AI → Response
    │       ↓ (jeśli błąd)
    │       └─→ Fallback do Gemini Pro
    │
    └─→ [Inni] → generuj_odpowiedz_ai()
            ↓
        Google Gemini Pro API
            ↓
        persona_name + prompt → Response
```

---

## Funkcje i Pliki

| Funkcja | Plik | Opis |
|---------|------|------|
| `send_to_ai_partner()` | `streamlit_app.py:648` | Główna funkcja wysyłki do partnera |
| `generuj_odpowiedz_ai()` | `streamlit_app.py:452` | Routing do Gemini/OpenRouter |
| `send_to_all_partners()` | `streamlit_app.py:2976` | Generator - wysyła do wszystkich po kolei |
| `NexusAIEngine` | `nexus_ai_engine.py` | Dedykowany silnik dla Nexus |

---

## Konfiguracja API

### Google Gemini Pro
- **API Key**: `st.secrets["GOOGLE_API_KEY"]` lub `os.getenv("GOOGLE_API_KEY")`
- **Model**: `gemini-pro`
- **Tracking**: Wszystkie wywołania są śledzone w `api_usage_tracker.py`

### OpenRouter (CZ)
- **API Key**: `st.secrets["OPENROUTER_API_KEY"]` lub `os.getenv("OPENROUTER_API_KEY")`
- **Model**: `meta-llama/llama-4-scout:free` (Mixtral)
- **Koszt**: DARMOWY
- **Tracking**: Śledzone jako "openai" w `api_usage_tracker.py`

### Nexus
- **Własny silnik**: Może używać różnych modeli wewnętrznie
- **Fallback**: Automatyczny powrót do Gemini Pro przy błędzie

---

## System Pamięci

### Persona Memory (`persona_memory.json`)
- Przechowuje długoterminową pamięć każdego partnera
- **Struktura**:
  - `communication_style`: Ton i styl komunikacji
  - `expertise`: Specjalizacje
  - `relationships`: Relacje z innymi partnerami
  - `voting_weight`: Waga głosu w głosowaniach
  - `meta`: Metadane sesji

### Pamięć v2.0 (`persona_memory_manager.py`)
- Rozbudowany kontekst z emocjami
- Relacje między partnerami
- Wagi głosowania
- Historia interakcji

---

## Koszty API (orientacyjne)

**Google Gemini Pro** (bezpłatny tier):
- 60 zapytań/minutę
- 1500 zapytań/dzień
- Darmowy do pewnego limitu

**Tracking kosztów**:
- Wszystkie wywołania logowane w `api_usage_tracker.py`
- Monitoring limitów w `api_limits_config.json`

---

## Przyszłe Rozszerzenia

Możliwe dodanie innych modeli:
- **Claude (Anthropic)** - dla bardziej analitycznych partnerów
- **GPT-4 (OpenAI)** - dla specyficznych case'ów
- **Mixtral/Llama** - lokalne modele dla prywatności

Obecnie infrastruktura jest gotowa - wystarczy dodać obsługę w `generuj_odpowiedz_ai()`.

---

**Ostatnia aktualizacja**: 2025-11-11
