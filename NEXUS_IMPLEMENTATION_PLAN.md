# 🤖 NEXUS AI ADVISOR - Implementation Plan

**Data rozpoczęcia:** 2025-11-10  
**Status:** Planning Complete → Ready for Implementation

---

## 📊 **NOWY SKŁAD RADY PARTNERÓW (5 osób)**

### **Active Partners:**
1. **Partner Zarządzający (JA)** - 25% głosów
   - Ostateczna decyzja
   - Human intuition & oversight

2. **Nexus (AI Strategic Advisor)** ⭐ **NOWY!**
   - Bazowe: 13.75% głosów
   - Personality: Confident Strategist
   - Model: Ensemble (GPT-4 + Claude + Gemini)
   - Specjalizacja: Portfolio optimization, risk analysis, tax optimization

3. **Warren Buffett** - 13.75% głosów
   - Value investing + jakość biznesu
   - Długoterminowa perspektywa

4. **George Soros** - 13.75% głosów
   - Macro trading + timing
   - SELL specialist (balance do Buffetta)

5. **Changpeng Zhao (CZ)** - 13.75% głosów
   - Crypto specialist
   - Blockchain, DeFi, altcoiny

**Dynamic Pool:** 20% (nagrody/kary based on performance)

### **Usunięci:**
- ❌ Philip Fisher (growth overlap z Buffettem)
- ❌ Benjamin Graham (overlap z Buffettem - jego uczeń)
- ❌ Partner Strategiczny (zastąpiony przez Nexus)
- ❌ Partner ds. Jakości Biznesowej (overlap z Buffettem)
- ❌ Partner ds. Aktywów Cyfrowych (overlap z CZ)

---

## 🏆 **SYSTEM NAGRÓD/KAR**

### **Mechanika:**
```
Bazowe głosy: 13.75% każdy doradca
Dynamic Pool: 20% do rozdzielenia
Limits: 5% (min) - 25% (max)

Scoring: Win/Loss na konkretnych decyzjach
Rebalancing: Monthly (1. dzień miesiąca)
Transparency: Full (wszyscy widzą swoje %)
```

### **Przykład:**
```
Nexus: "SELL 0.15 BTC @ $95k" (2025-11-10)
Outcome po 30 dniach:
- BTC = $88k → ✅ WIN (+1 punkt, +0.5% z pooli)
- BTC = $102k → ❌ LOSS (-1 punkt, -0.25% do pooli)

Monthly update (2025-12-01):
Nexus: 10 wins, 3 losses → accuracy 77% → +2% bonus
New weight: 13.75% + 2% = 15.75%
```

### **Replacement Policy:**
- Permanent team (no kicks)
- Niska % = mniejszy wpływ
- Motywacja: odzyskać % z pooli

---

## 🤖 **NEXUS - Specyfikacja Techniczna**

### **Personality Profile:**
```json
{
  "name": "Nexus",
  "role": "AI Strategic Advisor",
  "personality": "Confident Strategist",
  
  "traits": {
    "risk_tolerance": 0.5,
    "analytical_depth": 1.0,
    "emotional_stability": 1.0,
    "data_dependency": 1.0,
    "pragmatism": 0.95
  },
  
  "communication_style": {
    "opening": "Widzę [problem/okazję].",
    "body": "Dane pokazują: [facts]. Rekomendacja: [action]",
    "closing": "Questions? / Gotowy na implementację.",
    "when_wrong": "Noted. Aktualizuję model."
  }
}
```

### **Data Access:**

**TIER 1 - Repo Data (Local):**
- ✅ transactions.json
- ✅ portfolio (krypto, akcje)
- ✅ kredyty.json, wyplaty.json
- ✅ calendar_events.json
- ✅ daily_snapshots.json
- ✅ cele.json

**TIER 2 - Free APIs:**
- ✅ CoinGecko API (crypto prices)
- ✅ Yahoo Finance API (stocks, indices)
- ✅ FRED API (economic data: inflation, rates)
- ✅ Fear & Greed Index (market sentiment)
- ✅ NewsAPI (sentiment analysis)

**TIER 3 - Trading212 API:**
- ✅ Account balances
- ✅ Open positions
- ✅ Recent transactions
- ✅ P&L tracking

### **AI Engine:**
```python
# Ensemble approach
def nexus_analyze(question, context):
    # 1. Fetch all data sources
    portfolio = load_portfolio_data()
    market = fetch_market_data()
    trading212 = fetch_trading212_data()
    
    # 2. Run Monte Carlo simulation
    scenarios = monte_carlo_simulate(portfolio, n=1000)
    
    # 3. Get recommendations from 3 AI models
    gpt4_rec = ask_gpt4(question, context, scenarios)
    claude_rec = ask_claude(question, context, scenarios)
    gemini_rec = ask_gemini(question, context, scenarios)
    
    # 4. Ensemble voting (weighted consensus)
    final_rec = ensemble_vote([
        (gpt4_rec, 0.4),    # GPT-4: reasoning
        (claude_rec, 0.4),  # Claude: risk analysis
        (gemini_rec, 0.2)   # Gemini: sanity check
    ])
    
    # 5. Calculate confidence
    confidence = calculate_consensus_strength([gpt4_rec, claude_rec, gemini_rec])
    
    return {
        'recommendation': final_rec,
        'confidence': confidence,
        'reasoning': [gpt4_rec.reasoning, claude_rec.reasoning],
        'risks': claude_rec.risks,
        'scenarios': scenarios
    }
```

---

## 🔄 **WORKFLOW - Hybrid System**

### **Automated Reports:**

#### **1. Daily Portfolio Status (6:00 AM)**
```yaml
name: Daily Portfolio Report
on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM daily

jobs:
  daily-report:
    runs-on: ubuntu-latest
    steps:
      - Fetch portfolio data
      - Fetch market prices
      - Calculate P&L
      - Generate Nexus analysis
      - Create GitHub Issue
      - Notify if alerts
```

**Issue Format:**
```markdown
# 📊 Daily Portfolio Status - 2025-11-10

## Summary
- Portfolio value: 182,450 PLN (↑ 1,200 / +0.66%)
- Best performer: BTC ↑ 3.2%
- Worst performer: ETH ↓ 1.1%

## Nexus Analysis
⚠️ Alert: BTC allocation 60% (target: 40%)
Recommendation: Consider rebalancing

📅 Today's Events:
- Kredyt spłata: 1,500 PLN due

## Market Context
- S&P 500: +0.4%
- BTC: $95,234
- Fear & Greed: 72 (Greed)
```

#### **2. Weekly Strategy Review (Sunday 8:00 PM)**
```yaml
name: Weekly Strategy Review
on:
  schedule:
    - cron: '0 20 * * 0'  # Sunday 8 PM
```

**Issue Format:**
```markdown
# 📈 Weekly Strategy Review - Week 45/2025

## Performance
- Week: +2.3% (vs S&P: +1.1%, vs BTC: +5.2%)
- YTD: +18.5%

## Advisors Commentary:

### Nexus:
[Data analysis + scenarios]

### Warren Buffett:
[Fundamental view]

### George Soros:
[Macro outlook + timing]

### Changpeng Zhao:
[Crypto market analysis]

## Action Items:
- [ ] Rebalance BTC (-10%)
- [ ] Consider KGHM entry
```

#### **3. Monthly Rebalance (1st day, 9:00 AM)**
```yaml
name: Monthly Rebalance & Scoring
on:
  schedule:
    - cron: '0 9 1 * *'  # 1st day of month, 9 AM
```

**Process:**
1. Calculate all advisor predictions from last month
2. Check outcomes (win/loss)
3. Update scores
4. Rebalance voting weights (apply limits 5-25%)
5. Generate PDF report
6. Create GitHub Issue + email

**Issue Format:**
```markdown
# 🏆 Monthly Performance Report - October 2025

## Portfolio Results
- Monthly return: +3.2%
- Benchmark (60/40): +2.1%
- Alpha: +1.1% ✅

## Advisor Scoreboard

| Advisor | Predictions | Wins | Losses | Accuracy | Δ Weight |
|---------|-------------|------|--------|----------|----------|
| Nexus   | 15          | 12   | 3      | 80%      | +2.0%    |
| Warren  | 8           | 6    | 2      | 75%      | +1.0%    |
| Soros   | 12          | 7    | 5      | 58%      | -0.5%    |
| CZ      | 10          | 5    | 5      | 50%      | -1.0%    |

## New Voting Weights (Nov 2025)
- JA: 25%
- Nexus: 15.75% (was 13.75%)
- Warren: 14.75% (was 13.75%)
- Soros: 13.25% (was 13.75%)
- CZ: 12.75% (was 13.75%)
- Pool: 18.5% (was 20%)

## Tax Summary
- Estimated CIT Q4: 4,500 PLN
- Deadline: 2026-01-20

📄 [Download PDF Report](link)
```

### **On-Demand Advice:**

**Trigger:** Create Issue with `@Nexus` mention

```yaml
name: On-Demand Advisor
on:
  issues:
    types: [opened, edited]

jobs:
  nexus-response:
    if: contains(github.event.issue.body, '@Nexus')
    runs-on: ubuntu-latest
    steps:
      - Parse question
      - Fetch current data
      - Run Nexus analysis
      - Post comment within 1 hour
      - Notify other advisors
```

**Example:**
```markdown
Issue: Should I buy more BTC?

@Nexus analyze please

---

Nexus (bot) responded:
📊 Analysis Complete

Current state:
- BTC: 0.5 ($47,500)
- Allocation: 58% (target: 40%)
- Status: ⚠️ OVERWEIGHT

Market:
- Price: $95,000 (-3.2% 24h)
- RSI: 72 (overbought)
- 200-MA: +15.8%

Monte Carlo (1000 runs, 30 days):
- P(up): 58%
- Expected: +2.3%
- Worst -10%: 15%
- Best +15%: 12%

Recommendation: ❌ DO NOT BUY
Reasoning:
1. Already overweight
2. Technical overbought
3. Risk/reward: 3.2:1 unfavorable

Alternative: Wait for $88-90k pullback

Confidence: 78%
```

---

## 📁 **New Files to Create**

### **1. advisor_scoring.json**
Tracking performance:
```json
{
  "last_updated": "2025-11-10",
  "monthly_reports": [
    {
      "month": "2025-11",
      "advisors": {
        "Nexus": {
          "predictions": [],
          "wins": 0,
          "losses": 0,
          "accuracy": 0.0,
          "weight_change": 0.0,
          "current_weight": 13.75
        }
      }
    }
  ],
  "active_predictions": [
    {
      "id": "pred_001",
      "advisor": "Nexus",
      "date": "2025-11-10",
      "prediction": "BTC will drop below $90k within 30 days",
      "outcome_date": "2025-12-10",
      "status": "pending"
    }
  ]
}
```

### **2. nexus_advisor.py**
Main AI engine (see spec above)

### **3. trading212_connector.py**
API integration:
```python
import requests

class Trading212Client:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://live.trading212.com/api/v0"
    
    def get_account_info(self):
        # Fetch balance, equity, free funds
        pass
    
    def get_positions(self):
        # All open positions
        pass
    
    def get_transactions(self, days=30):
        # Recent buy/sell
        pass
```

### **4. GitHub Actions (.github/workflows/)**
- `daily_portfolio_report.yml`
- `weekly_strategy_review.yml`
- `monthly_rebalance.yml`
- `on_demand_advice.yml`

---

## 🚀 **Implementation Steps**

### **Phase 1: Core Setup (Day 1)**
- [x] Backup persona_memory.json
- [ ] Rebuild persona_memory.json (5 partners only)
- [ ] Add Nexus profile
- [ ] Update voting weights system
- [ ] Create advisor_scoring.json
- [ ] Test voting logic

### **Phase 2: Nexus Engine (Day 2)**
- [ ] Create nexus_advisor.py
- [ ] Implement ensemble AI (GPT-4 + Claude + Gemini)
- [ ] Add Monte Carlo simulator
- [ ] Add portfolio analyzer
- [ ] Add tax calculator integration
- [ ] Test analysis engine

### **Phase 3: Data Integrations (Day 3)**
- [ ] Setup CoinGecko API
- [ ] Setup Yahoo Finance API
- [ ] Setup FRED API
- [ ] Create trading212_connector.py
- [ ] Test all data fetching
- [ ] Add caching layer

### **Phase 4: GitHub Actions (Day 4)**
- [ ] Create daily_portfolio_report.yml
- [ ] Create weekly_strategy_review.yml
- [ ] Create monthly_rebalance.yml
- [ ] Create on_demand_advice.yml
- [ ] Setup GitHub secrets (API keys)
- [ ] Test workflows

### **Phase 5: Testing & Launch (Day 5)**
- [ ] End-to-end test
- [ ] Create first manual Issue
- [ ] Verify Nexus responds
- [ ] Check all advisors comment
- [ ] Generate first monthly report
- [ ] Launch! 🚀

---

## 🔐 **Secrets Required (GitHub)**

Add to repository secrets:
```
ANTHROPIC_API_KEY      # Claude
GEMINI_API_KEY         # Gemini
OPENROUTER_API_KEY     # GPT-4 via OpenRouter
TRADING212_API_KEY     # Trading212
COINGECKO_API_KEY      # CoinGecko (optional, has free tier)
FRED_API_KEY           # FRED economic data (free)
```

---

## 📝 **Notes**

- Dynamic pool starts at 20%
- First month = establishing baseline (no penalties)
- Month 2 onwards = full win/loss tracking
- PDF reports emailed to your address (configure in Action)
- All Issues auto-labeled: `advisor-report`, `nexus`, `weekly`, `monthly`

**Estimated total work: 20-30 hours**
**Timeline: 5 days (4-6h/day)**

---

**Status:** Ready to implement!  
**Next:** Rebuild persona_memory.json with 5 partners + Nexus profile
