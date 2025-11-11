# 🤖 AI Models Summary - Horyzont Partnerów

## Current AI Model Usage (Updated: 2025-01-19)

### 🎯 **Strategy: Separate API per Partner = Maximum Capacity**
- **Total Daily Capacity**: **200 requests/day** (4 API accounts × 50 each)
- **Old Setup**: 50 requests shared → **New Setup**: 200 requests distributed

---

## Active AI Partners Configuration

| Partner | AI Model | API Provider | API Account | Daily Limit | Purpose |
|---------|----------|--------------|-------------|-------------|---------|
| **Warren Buffett** | Gemini 2.5 Pro | Google | Główne konto | **50 req/day** | Value investing, długie analizy |
| **George Soros** | Gemini 2.5 Pro | Google | Główne konto | **50 req/day** | Macro trading, refleksywność rynku |
| **Nexus AI** | Gemini 2.5 Pro | Google | **Konto Nexus** | **50 req/day** | Agregacja perspektyw, meta-analiza |
| **CZ (Changpeng Zhao)** | Llama-4-Scout | OpenRouter | OpenRouter | **50 req/day** | Crypto/blockchain strategie |

**Note**: Warren + Soros dzielą 50 req/day (konto główne), Nexus ma osobne 50 req/day (konto Nexus)

---

## Technical Implementation

### 1. **Warren Buffett + George Soros** → Gemini 2.5 Pro (Główne konto)
```python
'model_engine': 'gemini'
# Model: gemini-2.5-pro
# API Key: GOOGLE_API_KEY (st.secrets)
# Limit: 50 requests/day WSPÓLNY dla obu partnerów
# Routing: generuj_odpowiedz_ai() → genai.GenerativeModel()
```
**Why Gemini 2.5 Pro?** Najnowszy model Google, świetny do analiz value investing i makro.

### 2. **Nexus** → Gemini 2.5 Pro (Osobne konto)
```python
'model_engine': 'gemini'
# Model: gemini-2.5-pro
# API Key: GOOGLE_API_KEY_NEXUS (st.secrets)
# Limit: 50 requests/day OSOBNY dla Nexusa
# Routing: generuj_odpowiedz_ai() → genai.GenerativeModel()
# Tracking: gemini_nexus (osobny counter)
```
**Why separate?** Nexus generuje autonomous conversations często, potrzebuje osobnego limitu.

### 3. **CZ (Changpeng Zhao)** → OpenRouter (Llama-4-Scout)
```python
'model_engine': 'openrouter_mixtral'
# Model: meta-llama/llama-4-scout:free
# API Key: OPENROUTER_API_KEY (st.secrets)
# Limit: 50 requests/day
# Routing: generuj_odpowiedz_ai() → OpenAI client (base_url=openrouter.ai)
```
**Why OpenRouter?** Darmowy Llama-4 idealny do crypto/tech. CZ potrzebuje nowoczesnych modeli open-source.

### 4. **Claude (INACTIVE)** → Warren Buffett (temporary disabled)
```python
# 'model_engine': 'claude'  # DISABLED: brak kredytów
# Warren tymczasowo używa Gemini (główne konto)
```
**Status**: Inactive - brak kredytów w koncie Anthropic. Warren używa Gemini.

---

## API Keys Required (Streamlit Secrets)

```toml
# .streamlit/secrets.toml
GOOGLE_API_KEY = "AIza..."              # Gemini główne konto (Warren + Soros)
GOOGLE_API_KEY_NEXUS = "AIza..."        # Gemini konto Nexus (osobny limit!)
OPENROUTER_API_KEY = "sk-or-..."        # OpenRouter (CZ)
# ANTHROPIC_API_KEY = "sk-ant-..."      # Claude (inactive - brak kredytów)
```

---

## Cost & Limits Analysis

| API | Account | Free Tier | Daily Limit | Assigned Partners |
|-----|---------|-----------|-------------|-------------------|
| **Google Gemini** | Główne | ✅ Yes | 50 req/day | Warren + Soros (shared) |
| **Google Gemini** | Nexus | ✅ Yes | 50 req/day | Nexus (exclusive) |
| **OpenRouter** | Main | ✅ Yes (free models) | 50 req/day | CZ (exclusive) |
| **Anthropic Claude** | Main | ❌ No credits | 0 req/day | None (inactive) |

**Total Free Capacity**: 150 requests/day aktywne (50 + 50 + 50)

**Distribution**:
- 50 req/day: Warren + Soros (może być bottleneck jeśli obaj aktywni)
- 50 req/day: Nexus (autonomous conversations)
- 50 req/day: CZ (crypto analysis)

---

## Migration History

- **2025-01-18**: Dodano OpenRouter support, migrated CZ
- **2025-01-19**: 
  - Dodano Claude support (nieaktywny - brak kredytów)
  - Updated Gemini: gemini-pro → gemini-2.5-pro
  - **Dodano osobne konto Gemini dla Nexusa (GOOGLE_API_KEY_NEXUS)**
  - Warren temporary na Gemini (Claude inactive)
- **Previous**: Wszyscy na Gemini (1 API, 50 req/day shared)
- **Current**: 3 aktywne API (2× Gemini + 1× OpenRouter = 150 req/day)

---

## Code References

- **Main routing**: `streamlit_app.py` → `generuj_odpowiedz_ai()` (lines 452-548)
  - Line 526-532: Wybór klucza Gemini (Nexus vs inni)
  - Line 541-545: Tracking (gemini vs gemini_nexus)
- **Partner config**: `streamlit_app.py` → `load_personas_from_memory_json()` (lines 585-604)
- **API tracking**: `api_usage_tracker.py` → tracks per-API usage

---

## Testing Checklist

- [ ] Warren Buffett response (Gemini główne konto)
- [ ] George Soros response (Gemini główne konto)
- [ ] Nexus response (Gemini konto Nexus - osobny limit!)
- [ ] CZ response (OpenRouter)
- [ ] API usage tracking shows 3 separate counters (gemini, gemini_nexus, openai)

---

**Last Updated**: 2025-01-19 by GitHub Copilot  
**Config Version**: 2.1 (Dual Gemini + OpenRouter)
