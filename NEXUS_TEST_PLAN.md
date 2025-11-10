# 🧪 NEXUS SYSTEM - Test Plan & Validation Checklist

## 📋 Overview
Complete testing plan dla systemu Nexus AI i wszystkich nowych features (November 2025).

---

## ✅ Test Checklist

### 1️⃣ Nexus AI Engine - Core Functionality

#### 1.1 Single Mode (Gemini)
- [ ] **Import test**: `from nexus_ai_engine import get_nexus_engine`
- [ ] **Initialization**: Nexus engine startuje bez błędów
- [ ] **Status check**: `nexus.get_status()` zwraca poprawne dane
- [ ] **Response generation**: Nexus generuje odpowiedź na test prompt
- [ ] **Performance tracking**: Queries counter increases, avg_response_time updates

**Test Command:**
```bash
python nexus_ai_engine.py
```

**Expected Output:**
```
✅ Nexus AI Engine initialized
Mode: single
Gemini client: OK
Test response: [odpowiedź Gemini]
```

#### 1.2 Ensemble Eligibility
- [ ] **Check eligibility**: `nexus.check_ensemble_eligibility()` działa
- [ ] **Initial state**: Powinno być False (brak danych scoring)
- [ ] **Threshold logic**: 65% accuracy + 30 days checked correctly

#### 1.3 User Rating System
- [ ] **Add rating**: `nexus.add_user_satisfaction_rating(0.8, "Good")` zapisuje
- [ ] **Quality score update**: avg quality score się zmienia
- [ ] **Ratings list**: ratings append do listy

---

### 2️⃣ Streamlit Integration - Nexus UI

#### 2.1 Partner Selection
- [ ] **Nexus w dropdown**: Widoczny w liście partnerów (💬 Partnerzy)
- [ ] **PERSONAS loading**: gra_rpg.py ładuje z persona_memory.json
- [ ] **4 AI partners**: Nexus, Warren, Soros, CZ wszystkie widoczne

**Test Steps:**
1. Uruchom streamlit: `streamlit run streamlit_app.py --server.port 8503`
2. Przejdź do 💬 Partnerzy
3. Sprawdź dropdown - powinno być 5 opcji: Wszyscy, Nexus, Warren Buffett, George Soros, CZ

#### 2.2 Nexus Status Widget
- [ ] **Widget visibility**: Pojawia się gdy wybrano Nexus
- [ ] **Mode indicator**: Pokazuje "SINGLE" lub "ENSEMBLE"
- [ ] **Performance metrics**: Queries, Avg Time wyświetlane
- [ ] **Ensemble button**: Pojawia się gdy eligible
- [ ] **Rating buttons**: 👍 😐 👎 działają

#### 2.3 Chat z Nexusem
- [ ] **Send message**: Wiadomość do Nexusa wysyła się
- [ ] **Routing**: send_to_ai_partner() rozpoznaje Nexus (model_engine='nexus')
- [ ] **Response**: Nexus zwraca odpowiedź
- [ ] **Context passing**: Portfolio context przekazany
- [ ] **Error handling**: Fallback działa gdy Nexus fail

**Test Prompt:**
```
Jaki jest obecny stan mojego portfela i czy powinienem coś zmienić?
```

---

### 3️⃣ Advisor Scoring System

#### 3.1 CLI Tool
- [ ] **Leaderboard**: `python advisor_scoring_manager.py leaderboard`
- [ ] **Add prediction**: `python advisor_scoring_manager.py add-prediction`
- [ ] **Evaluate**: `python advisor_scoring_manager.py evaluate`
- [ ] **Rebalance**: `python advisor_scoring_manager.py rebalance`

**Test Commands:**
```bash
# 1. Zobacz leaderboard
python advisor_scoring_manager.py leaderboard

# 2. Dodaj test prediction dla Nexusa
python advisor_scoring_manager.py add-prediction

# 3. Oceń (win)
python advisor_scoring_manager.py evaluate

# 4. Rebalance wag
python advisor_scoring_manager.py rebalance
```

#### 3.2 Scoring Data
- [ ] **advisor_scoring.json exists**: Plik istnieje
- [ ] **All 4 AI partners**: Nexus, Warren, Soros, CZ w pliku
- [ ] **Prediction structure**: predictions[], accuracy_rate, dynamic_weight
- [ ] **Win/Loss tracking**: Liczniki działają

---

### 4️⃣ Voting Weights UI (Streamlit)

#### 4.1 Zakładka ⚖️ Voting Weights
- [ ] **Tab visible**: Zakładka widoczna w menu
- [ ] **Leaderboard renders**: Tabela z partnerami i wagami
- [ ] **Chart display**: Plotly chart z wagami
- [ ] **Accuracy display**: % accuracy dla każdego partnera

#### 4.2 Prediction History
- [ ] **Table shows**: Historia przewidywań wyświetlana
- [ ] **Filters work**: Data range, partner filter
- [ ] **Status badges**: Pending/Win/Loss badges

#### 4.3 Rebalancing History
- [ ] **Monthly logs**: Historia rebalancingu
- [ ] **Weight changes**: Before/After weights
- [ ] **Chart**: Timeline weight changes

---

### 5️⃣ Autonomous Conversations

#### 5.1 Engine Core
- [ ] **Engine init**: `AutonomousConversationEngine()` startuje
- [ ] **Nexus import**: Engine importuje nexus_ai_engine
- [ ] **Topic selection**: select_topic() zwraca temat
- [ ] **Participants**: select_participants() zwraca 4 AI (bez JA!)
- [ ] **Budget check**: API budget checking działa

**Test Command:**
```bash
python autonomous_conversation_engine.py
```

**Expected:**
- Rozmowa 12 wiadomości
- 4 partnerzy rotują
- Summary wygenerowane
- Nexus meta-analysis wykonana

#### 5.2 Nexus jako Moderator
- [ ] **Special handling**: Nexus w call_ai_partner() ma własną logikę
- [ ] **Moderator prompt**: Nexus dostaje prompt o syntezie perspektyw
- [ ] **Context passing**: previous_messages przekazane
- [ ] **Response quality**: Nexus syntetyzuje a nie tylko komentuje

#### 5.3 Nowe Tematy
- [ ] **nexus_meta_discussion**: Temat o efektywności Rady
- [ ] **ai_voting_weights**: Temat o systemie scoring
- [ ] **knowledge_gaps**: Temat o lukach wiedzy

---

### 6️⃣ Nexus Enhanced Features

#### 6.1 Meta-Analysis
- [ ] **Function exists**: `nexus_meta_analysis()` zdefiniowana
- [ ] **Analysis generation**: Zwraca dict z analizą
- [ ] **Fields complete**: main_themes, consensus, disagreements, partner_scores, insights
- [ ] **Auto-run**: Wykonuje się automatycznie po rozmowie
- [ ] **Saved**: meta_analysis zapisana w conversation JSON

**Test:**
1. Uruchom autonomous conversation
2. Sprawdź `autonomous_conversations.json`
3. Ostatnia rozmowa powinna mieć pole `nexus_meta_analysis`

#### 6.2 Voting Simulation
- [ ] **Function exists**: `nexus_voting_simulation()` zdefiniowana
- [ ] **Question input**: Przyjmuje decision_question
- [ ] **Vote prediction**: Zwraca głosy partnerów (ZA/PRZECIW/WSTRZYMUJĘ)
- [ ] **Confidence scores**: Każdy głos ma confidence
- [ ] **Arguments**: key_arguments_for i _against
- [ ] **Nexus recommendation**: Własna rekomendacja

**Test in Streamlit:**
1. Przejdź do 🤖 Autonomous Conversations
2. Otwórz zakończoną rozmowę (expander)
3. Scroll do "🗳️ Nexus Voting Simulation"
4. Wpisz pytanie: "Czy zwiększyć krypto do 30%?"
5. Kliknij "🗳️ Symuluj głosowanie"
6. Sprawdź wyniki

#### 6.3 Knowledge Synthesis
- [ ] **Function exists**: `nexus_knowledge_synthesis()` zdefiniowana
- [ ] **Multi-conversation**: Analizuje N ostatnich rozmów
- [ ] **Query answering**: Odpowiada na pytanie bazując na historii
- [ ] **Source citation**: Wymienia rozmowy użyte w analizie

**Test in Streamlit:**
1. Przejdź do 🤖 Autonomous Conversations
2. Rozwiń "📚 Nexus Knowledge Synthesis"
3. Wpisz: "Jakie są główne obawy Rady w ostatnich dyskusjach?"
4. Wybierz 3-5 rozmów
5. Kliknij "🤖 Zapytaj Nexusa"
6. Sprawdź odpowiedź

---

### 7️⃣ UI Integration - Streamlit Pages

#### 7.1 Autonomous Conversations Page
- [ ] **Status section**: API budgets wyświetlane
- [ ] **Run button**: 🚀 Uruchom nową rozmowę działa
- [ ] **Conversation list**: Historia rozmów visible
- [ ] **Filters**: Topic, date, min messages filters
- [ ] **Expanders**: Każda rozmowa w expander
- [ ] **AI Summary**: Summary section z sentiment badge
- [ ] **Nexus Meta-Analysis section**: Pełna meta-analysis wyświetlana
- [ ] **Voting Simulation UI**: Interactive voting simulation
- [ ] **Knowledge Synthesis UI**: Query interface

#### 7.2 Error Handling
- [ ] **Nexus unavailable**: Graceful degradation gdy brak Nexus
- [ ] **API limits**: Komunikaty gdy brak budżetu
- [ ] **Import errors**: Friendly error messages
- [ ] **Empty data**: Proper handling gdy brak rozmów

---

### 8️⃣ GitHub Actions Workflows

#### 8.1 Monthly Rebalancing Workflow
- [ ] **File exists**: `.github/workflows/monthly-rebalancing.yml`
- [ ] **Schedule**: Cron 1st day każdego miesiąca
- [ ] **Manual trigger**: workflow_dispatch enabled
- [ ] **Steps complete**: Checkout, Python setup, install deps, rebalance, commit, push
- [ ] **Issue creation**: Tworzy issue z raportem

#### 8.2 Daily Conversation Workflow (Optional)
- [ ] **File exists**: `.github/workflows/daily-conversation.yml`
- [ ] **Schedule**: Daily 18:00 UTC
- [ ] **Disabled by default**: Schedule commented lub manual only
- [ ] **API secrets**: Uses GITHUB_SECRETS correctly

---

### 9️⃣ Documentation

#### 9.1 GUIDE_AI_PARTNERS.md
- [ ] **Nexus section**: Opis Nexusa dodany
- [ ] **Single vs Ensemble**: Wyjaśnione
- [ ] **Autonomous Conversations**: Sekcja z instrukcjami
- [ ] **Voting Weights**: Opis systemu scoring
- [ ] **Meta-Analysis**: Jak używać
- [ ] **Voting Simulation**: Przykłady
- [ ] **Knowledge Synthesis**: Use cases

#### 9.2 QUICK_REFERENCE_V2.md
- [ ] **5 Partners table**: Updated 10→5
- [ ] **Nexus commands**: Quick reference
- [ ] **Scoring commands**: CLI commands listed
- [ ] **API mappings**: Gemini, OpenRouter correct

---

## 🚀 Quick Test Sequence (5 min)

```bash
# 1. Test Nexus Engine
python nexus_ai_engine.py

# 2. Test PERSONAS loading
python -c "from gra_rpg import PERSONAS; print(f'Loaded: {list(PERSONAS.keys())}')"

# 3. Test Advisor Scoring
python advisor_scoring_manager.py leaderboard

# 4. Test Autonomous (jeśli masz API budget)
python autonomous_conversation_engine.py

# 5. Uruchom Streamlit
streamlit run streamlit_app.py --server.port 8503
```

**W Streamlit sprawdź:**
1. ✅ Nexus w dropdown (💬 Partnerzy)
2. ✅ Nexus Status Widget widoczny
3. ✅ Chat z Nexusem działa
4. ✅ ⚖️ Voting Weights tab
5. ✅ 🤖 Autonomous Conversations tab
6. ✅ Voting Simulation interactive
7. ✅ Knowledge Synthesis query

---

## 📊 Success Criteria

**System PASSED jeśli:**
- ✅ Wszystkie 4 AI partners (Nexus, Warren, Soros, CZ) widoczne
- ✅ Nexus generuje odpowiedzi w single mode
- ✅ Autonomous conversations działają z Nexus meta-analysis
- ✅ Voting simulation zwraca sensowne przewidywania
- ✅ Knowledge synthesis odpowiada na queries
- ✅ UI nie ma critical errors
- ✅ GitHub Actions workflows są valid YAML

**Known Limitations (OK):**
- Ensemble mode: Inactive (requires 65% accuracy + 30 days)
- Claude/GPT-4: Nie zainicjalizowane (tylko Gemini w single mode)
- API budgets: Może być 0/40 autonomous calls (to normalne)

---

## 🐛 Common Issues & Solutions

### Issue: "Nexus nie widoczny w dropdown"
**Solution:** 
```bash
# Sprawdź czy PERSONAS załadowane poprawnie
python -c "from gra_rpg import PERSONAS; print('Nexus' in PERSONAS)"
# Powinno być: True
```

### Issue: "AttributeError: module 'nexus_ai_engine' has no attribute 'get_nexus_engine'"
**Solution:**
```bash
# Sprawdź syntax errors
python -m py_compile nexus_ai_engine.py
```

### Issue: "No module named 'nexus_ai_engine'"
**Solution:**
Upewnij się że `nexus_ai_engine.py` jest w tym samym folderze co `streamlit_app.py`.

### Issue: "API budget exceeded"
**Solution:**
To normalne! Autonomous conversations mają dzienny limit. Sprawdź:
```bash
python -c "from api_usage_tracker import get_tracker; get_tracker().print_status()"
```

---

## ✅ Final Validation

Po zakończeniu wszystkich testów, wypełnij:

- [ ] **All core features work** (Nexus chat, scoring, autonomous)
- [ ] **No critical bugs** (może być minor issues)
- [ ] **Documentation accurate** (guides match reality)
- [ ] **GitHub workflows valid** (YAML syntax OK)
- [ ] **Ready for production** (safe to use daily)

**Sign-off Date:** _____________

**Notes:** 
_______________________________________
_______________________________________
