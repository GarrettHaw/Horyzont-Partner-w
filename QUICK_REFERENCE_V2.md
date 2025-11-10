# 🚀 QUICK REFERENCE - AI Personality System v2.0 + Nexus

## 📋 Podstawowe Komendy

### Testy i Diagnostyka
```powershell
# Test systemu v2.0
python -c "from persona_context_builder import build_enhanced_context; print('✅ OK')"

# Test Nexus AI Engine
python nexus_ai_engine.py

# Zobacz kontekst AI
python persona_context_builder.py

# Sprawdź knowledge base
python knowledge_base_updater.py

# Audyt miesięczny
python monthly_audit.py

# Autonomous Conversation (test)
python autonomous_conversation_engine.py

# Advisor Scoring
python advisor_scoring_manager.py leaderboard
```

### Backup i Maintenance
```powershell
# Backup pamięci
Copy-Item persona_memory.json "persona_memory_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

# Sprawdź rozmiar pliku
(Get-Item persona_memory.json).Length / 1KB
```

---

## 🎭 Profile Partnerów (Quick Ref) - UPDATED 5 Partners

| Persona | API | Risk | Voting | Goal |
|---------|-----|------|--------|------|
| **Nexus AI** 🤖 | Gemini/Ensemble | 0.5 | 13.75% | Best meta-advisor |
| **Warren Buffett** 🏡 | Gemini | 0.5 | 13.75% | Quality compounders |
| **George Soros** 🌍 | OpenRouter Mixtral | 0.6 | 13.75% | System inefficiencies |
| **CZ** ⚡ | OpenRouter GLM | 0.8 | 13.75% | Decentralized finance |
| **JA (Human)** 👔 | - | 0.6 | 25% | Sustainable growth |

**IMPORTANT:** Reorganizacja z 10 → 5 partnerów (November 2025)

---

## 🤖 Nexus AI - Quick Commands

### Status Check
```python
from nexus_ai_engine import get_nexus_engine
nexus = get_nexus_engine()
status = nexus.get_status()
print(f"Mode: {status['mode']}")  # 'single' or 'ensemble'
print(f"Queries: {status['performance']['total_queries_handled']}")
```

### Activate Ensemble (when eligible)
```python
eligible, reason = nexus.check_ensemble_eligibility()
if eligible:
    success, msg = nexus.activate_ensemble(user_approved=True)
```

### Add User Rating
```python
# After getting response from Nexus
nexus.add_user_satisfaction_rating(rating=0.8, feedback="Great analysis!")
# rating: 0.2 (👎), 0.5 (😐), 0.8 (👍)
```

---

## 📊 Voting Weight System - DYNAMIC

```
Base Weight (persona_memory.json): 
- JA (Human): 25%
- Nexus: 13.75%
- Warren Buffett: 13.75%
- George Soros: 13.75%
- CZ: 13.75%

Dynamic Adjustment (advisor_scoring.json):
- Accuracy >70% → Weight increases (max 25%)
- Accuracy <50% → Weight decreases (min 5%)
- Monthly rebalancing: 1st day of month

Formula:
new_weight = base_weight * (accuracy_rate / 0.65)
# 0.65 is the baseline threshold
```

### Check Current Weights
```python
from streamlit_app import get_current_voting_weights
weights = get_current_voting_weights()
for partner, weight in weights.items():
    print(f"{partner}: {weight}%")
```

---

## 🎯 Mood System

### Moods
| Mood | Emoji | Trigger |
|------|-------|---------|
| **excited** | 🔥 | Big win (>500 PLN) |
| **confident** | 💪 | Multiple wins |
| **optimistic** | 😊 | Small win |
| **neutral** | 😐 | Default |
| **cautious** | 🤔 | High market volatility |
| **worried** | 😟 | Small loss |
| **fearful** | 😰 | Big loss (>1000 PLN) |
| **angry** | 😠 | Failed prediction |
| **disappointed** | 😞 | Missed opportunity |

### Mood Affects
- **excited** → More aggressive recommendations, higher risk tolerance
- **fearful** → Conservative moves, recommends cash
- **confident** → Bold calls, references past wins
- **worried** → Extra cautious, mentions concerns frequently

---

## 🤝 Relationship Dynamics

### Trust Levels
- 🟢 **High (>70%)**: "I agree with [Partner]", supportive tone
- 🟡 **Medium (40-70%)**: Neutral, objective analysis
- 🔴 **Low (<40%)**: "I disagree with [Partner]", contrarian stance

### Trust Changes
```python
Agreement on decision: trust += 0.05
Disagreement (one correct): trust -= 0.1
Alliance (joint proposal): trust += 0.1
Conflict (opposing views): trust -= 0.05
```

---

## 📚 Knowledge Base

### Update Frequency
⏰ **Every 12 hours** (via Task Scheduler)

### Sources
- **Yahoo Finance**: Market news, earnings
- **Seeking Alpha**: Analysis, opinions
- **Bloomberg**: Global macro news

### Tags
- `macro` → Fed, interest rates, GDP
- `earnings` → Company results
- `tech` → Apple, Microsoft, Google
- `crypto` → Bitcoin, Ethereum, Binance
- `m&a` → Mergers, acquisitions
- `energy` → Oil, gas, renewables

### Usage in Prompts
AI partners automatically reference recent articles when relevant:
> "Based on recent Yahoo Finance report about Fed rate cuts..."

---

## 🔮 Prediction System

### Recording Prediction
```python
{
  "ticker": "AAPL",
  "direction": "UP",  # UP, DOWN, NEUTRAL
  "entry_price": 175.50,
  "forecast_price": 190.00,
  "confidence": 0.75,  # 0-1
  "timeframe": "3M",
  "reasoning": "Strong iPhone sales...",
  "due_date": "2026-01-21",
  "status": "active"  # active, resolved
}
```

### Monthly Audit Checks
1. Fetches current price
2. Compares direction: `current_price > entry_price`
3. Calculates accuracy: `100 - abs(forecast_change% - actual_change%)`
4. Updates credibility score
5. Changes mood based on result
6. Evolves personality traits
7. Adjusts voting weight bonus

---

## 🧬 Personality Evolution

### Traits That Evolve
- `risk_tolerance` → After losses: -0.05, After wins: +0.05
- `optimism_bias` → After failed predictions: -0.1
- `patience` → After impulsive losses: +0.05

### Learning Patterns
```json
{
  "mistake_categories": {
    "crypto_overallocation": 3,  # Count
    "timing_error": 2
  },
  "improvement_strategies": [
    "Reduce crypto exposure to <20%",
    "Wait for RSI < 30 before buying"
  ]
}
```

---

## ⚙️ Configuration Files

### `persona_memory.json`
**Current size**: 1626 lines  
**Backup frequency**: Before each major operation  
**Location**: Root directory

### `knowledge_base/articles.json`
**Max age**: 14 days (older removed)  
**Current count**: 9 articles  
**Update**: Every 12h via `run_knowledge_updater.bat`

### `monthly_snapshot.json`
**Generated by**: `monthly_audit.py`  
**Contains**: Summary of predictions evaluated, persona results

---

## 🐛 Troubleshooting

### "No module named 'feedparser'"
```powershell
pip install feedparser beautifulsoup4 requests
```

### "MEMORY_V2 not found"
Check imports in `streamlit_app.py` line 30:
```python
from persona_context_builder import build_enhanced_context, get_emotional_modifier
```

### Knowledge base not updating
1. Check Task Scheduler: task enabled?
2. Check logs: `logs\knowledge_base.log`
3. Manual run: `python knowledge_base_updater.py`

### Credibility not changing
1. Ensure decisions have `outcome` field ('success'/'failure')
2. Run `monthly_audit.py` manually
3. Check `persona_memory.json` for updated `credibility_score`

### Progress bar crash (negative values)
Fixed in streamlit_app.py line 4935:
```python
normalized_value = max(0.0, min(1.0, value))
st.progress(normalized_value)
```

---

## 📈 Performance Tips

### Optimize Token Usage
- Limit context: `build_enhanced_context(name, limit=3)` instead of 5
- Reduce verbosity in communication_style
- Shorten catchphrases list

### Reduce File Size
- Archive old decisions (>6 months)
- Limit mood_history to last 10 (currently 20)
- Compress notable_moments in relationships

### Speed Up Knowledge Base
- Reduce max articles per source (currently 10)
- Increase deduplication frequency
- Cache HTTP requests

---

## 🎯 Best Practices

### When Talking to AI Partners
1. ✅ Reference recent portfolio performance
2. ✅ Ask about specific tickers
3. ✅ Request confidence levels
4. ✅ Save important decisions with 💾 button

### After Big Portfolio Changes
1. 🔄 Update emotional states manually if needed
2. 📝 Record key decisions immediately
3. 📊 Check Track Record tab (TAB 7)

### Monthly Routine
1. 📅 1st of month: Run `monthly_audit.py`
2. 📊 Check leaderboard in TAB 7
3. 📈 Review personality evolution
4. 💾 Backup persona_memory.json

---

## 🔗 Related Files

- **Documentation**: `AI_PERSONALITY_SYSTEM_V2.md`
- **Upgrade Summary**: `UPGRADE_SUMMARY_V2.md`
- **Original Guide**: `AI_MEMORY_GUIDE.md`
- **Quick Start**: `QUICK_START.md`

---

**Version**: 2.0  
**Last Updated**: 21.10.2025  
**Status**: Production Ready ✅
