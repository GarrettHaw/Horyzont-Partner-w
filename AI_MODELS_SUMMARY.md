# 🤖 AI Models Summary - Horyzont Partnerów

## Current AI Model Usage (Updated: 2025-01-19)

### 🎯 **Strategy: Separate API per Partner = Maximum Capacity**
- **Total Daily Capacity**: **150 requests/day** (3 partners × 50 each)
- **Old Setup**: 50 requests shared → **New Setup**: 150 requests distributed

---

## Active AI Partners Configuration

| Partner | AI Model | API Provider | Daily Limit | Purpose |
|---------|----------|--------------|-------------|---------|
| **Warren Buffett** | Claude 3.5 Sonnet | Anthropic | **50 req/day** | Value investing, długie analizy |
| **George Soros** | Gemini Pro | Google | **50 req/day** | Macro trading, refleksywność rynku |
| **CZ (Changpeng Zhao)** | Llama-4-Scout | OpenRouter | **50 req/day** | Crypto/blockchain strategie |
| **Nexus AI** | Custom Engine | Internal | Unlimited* | Agregacja perspektyw, meta-analiza |

*Nexus używa własnego silnika `nexus_ai_engine.py` z możliwym fallback do Gemini

---

## Technical Implementation

### 1. **Warren Buffett** → Claude (Anthropic)
```python
'model_engine': 'claude'
# Model: claude-3-5-sonnet-20241022
# API Key: ANTHROPIC_API_KEY (st.secrets)
# Routing: generuj_odpowiedz_ai() → anthropic.messages.create()
```
**Why Claude?**: Najlepszy do długich, przemyślanych analiz fundamentalnych. Warren potrzebuje kontekstu do value investing.

### 2. **George Soros** → Gemini Pro
```python
'model_engine': 'gemini'
# Model: gemini-pro
# API Key: GOOGLE_API_KEY (st.secrets)
# Routing: generuj_odpowiedz_ai() → genai.GenerativeModel()
```
**Why Gemini?**: Szybki, dobry do dynamicznych analiz makro. Soros potrzebuje refleksów na zmiany rynkowe.

### 3. **CZ (Changpeng Zhao)** → OpenRouter (Llama-4-Scout)
```python
'model_engine': 'openrouter_mixtral'
# Model: meta-llama/llama-4-scout:free
# API Key: OPENROUTER_API_KEY (st.secrets)
# Routing: generuj_odpowiedz_ai() → OpenAI client (base_url=openrouter.ai)
```
**Why OpenRouter?**: Darmowy Llama-4 idealny do crypto/tech. CZ potrzebuje nowoczesnych modeli open-source.

### 4. **Nexus** → Custom Engine
```python
# nexus_ai_engine.py - własna implementacja
# Może używać kombinacji modeli lub logiki przepływowej
```
**Why Custom?**: Nexus agreguje perspektywy wszystkich partnerów, potrzebuje elastyczności.

---

## API Keys Required (Streamlit Secrets)

```toml
# .streamlit/secrets.toml
ANTHROPIC_API_KEY = "sk-ant-..."     # Claude (Warren)
GOOGLE_API_KEY = "AIza..."           # Gemini (Soros)
OPENROUTER_API_KEY = "sk-or-..."    # OpenRouter (CZ)
```

---

## Cost & Limits Analysis

| API | Free Tier | Daily Limit | Cost per 1M tokens (if exceeded) |
|-----|-----------|-------------|----------------------------------|
| **Anthropic Claude** | ✅ Yes | 50 req/day | ~$3-15 |
| **Google Gemini** | ✅ Yes | 50 req/day | $0.50-1.50 |
| **OpenRouter** | ✅ Yes (free models) | 50 req/day | $0 (free tier) |

**Total Free Capacity**: 150 requests/day = ~5 requests/hour continuously

---

## Migration History

- **2025-01-18**: Dodano OpenRouter support, migrated CZ
- **2025-01-19**: Dodano Claude support, migrated Warren Buffett
- **Previous**: Wszyscy na Gemini (1 API, 50 req/day shared)
- **Current**: 3 API providers (3×50 = 150 req/day total)

---

## Code References

- **Main routing**: `streamlit_app.py` → `generuj_odpowiedz_ai()` (lines 452-540)
- **Partner config**: `streamlit_app.py` → `load_personas_from_memory_json()` (lines 550-607)
- **API tracking**: `api_usage_tracker.py` → tracks per-API usage

---

## Testing Checklist

- [ ] Warren Buffett response (Claude)
- [ ] George Soros response (Gemini)
- [ ] CZ response (OpenRouter)
- [ ] Nexus autonomous conversation
- [ ] API usage tracking shows separate counters

---

**Last Updated**: 2025-01-19 by GitHub Copilot  
**Config Version**: 2.0 (Multi-API)
