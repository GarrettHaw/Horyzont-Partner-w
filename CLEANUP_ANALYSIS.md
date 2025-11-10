# 🧹 ANALIZA PLIKÓW - CO USUNĄĆ

## ✅ PLIKI UŻYWANE (ZACHOWAĆ)

### Core System Files
- ✅ `streamlit_app.py` - główna aplikacja
- ✅ `gra_rpg.py` - core logic
- ✅ `requirements.txt` - dependencies

### Nexus System (NOWE - ZACHOWAĆ)
- ✅ `nexus_ai_engine.py` - Nexus AI
- ✅ `advisor_scoring_manager.py` - scoring CLI
- ✅ `advisor_scoring.json` - dane scoring
- ✅ `persona_memory.json` - single source of truth
- ✅ `persona_context_builder.py` - AI context
- ✅ `persona_memory_manager.py` - memory management

### AI & Memory (UŻYWANE)
- ✅ `api_usage_tracker.py` - używane przez streamlit + gra_rpg
- ✅ `autonomous_conversation_engine.py` - używane (Nexus enhanced)
- ✅ `autonomous_conversations.json` - dane rozmów
- ✅ `autonomous_topics_config.json` - tematy rozmów

### Portfolio & Analytics (UŻYWANE)
- ✅ `analiza_portfela.py` - używane przez gra_rpg
- ✅ `dashboard_wizualizacje.py` - używane przez gra_rpg
- ✅ `portfolio_simulator.py` - używane przez gra_rpg
- ✅ `risk_analytics.py` - używane przez streamlit + gra_rpg
- ✅ `animated_timeline.py` - używane przez streamlit + gra_rpg
- ✅ `cache_manager.py` - używane przez gra_rpg
- ✅ `async_data_manager.py` - używane przez gra_rpg

### Data & Config (UŻYWANE)
- ✅ `cele.json` - cele finansowe
- ✅ `kredyty.json` - dane kredytów
- ✅ `krypto.json` - portfel krypto
- ✅ `kodeks_spolki.txt` - kodeks
- ✅ `api_limits_config.json` - limity API
- ✅ `api_usage.json` - tracking API
- ✅ `credentials.json` - Google Sheets
- ✅ `.env` - environment variables

### Crypto (UŻYWANE)
- ✅ `crypto_portfolio_manager.py` - używane przez streamlit
- ✅ `crypto_cache.json` - cache
- ✅ `crypto_metadata_cache.json` - metadata
- ✅ `crypto_prices_cache.json` - ceny

### Email & Notifications (UŻYWANE)
- ✅ `email_notifier.py` - używane przez streamlit
- ✅ `consultation_system.py` - używane przez streamlit
- ✅ `alert_system.py` - alerty
- ✅ `notification_config.json` - config

### Daily/Monthly Tools (UŻYWANE)
- ✅ `daily_snapshot.py` - daily snapshots
- ✅ `daily_snapshots.json` - dane
- ✅ `monthly_snapshot.json` - monthly dane
- ✅ `monthly_audit.py` - audyt

### Excel & Reports (UŻYWANE)
- ✅ `excel_reporter.py` - używane przez streamlit
- ✅ `portfolio_history.json` - historia

### Knowledge Base (UŻYWANE)
- ✅ `knowledge_base_updater.py` - aktualizacje
- ✅ `knowledge_base/` - folder z bazą

### Persistence (UŻYWANE)
- ✅ `persistent_storage.py` - używane przez streamlit
- ✅ `partner_conversations.json` - konwersacje

### Cache Files (UŻYWANE)
- ✅ `yfinance_cache.json` - cache YFinance
- ✅ `trading212_cache.json` - cache Trading212
- ✅ `benchmark_cache.json` - benchmark
- ✅ `cache_migrated.flag` - flaga migracji

### User Data (UŻYWANE)
- ✅ `user_preferences.json` - preferencje
- ✅ `wydatki.json` - wydatki
- ✅ `wyplaty.json` - wypłaty
- ✅ `partner_conversations.json` - rozmowy

### Folders (UŻYWANE)
- ✅ `weekly_reports/` - raporty tygodniowe
- ✅ `raporty_miesieczne/` - raporty miesięczne
- ✅ `partner_memories/` - pamięci partnerów
- ✅ `sesje/` - sesje
- ✅ `logs/` - logi
- ✅ `.streamlit/` - config Streamlit
- ✅ `.github/` - GitHub Actions
- ✅ `__pycache__/` - Python cache

---

## ❌ PLIKI DO USUNIĘCIA (NIEUŻYWANE/STARE)

### Old Documentation (ZDUPLIKOWANE/PRZESTARZAŁE)
- ❌ `ADVANCED_FEATURES_GUIDE.md` - stara dokumentacja
- ❌ `AI_MEMORY_GUIDE.md` - przestarzała
- ❌ `AI_PERSONALITY_SYSTEM_V2.md` - zastąpiona przez GUIDE_AI_PARTNERS.md
- ❌ `AI_UPGRADE_SUMMARY.md` - historia, niepotrzebna
- ❌ `CRYPTO_TAB_UPGRADE_COMPLETE.md` - historia upgradu
- ❌ `CRYPTO_UPGRADE_GUIDE.md` - upgrade guide (done)
- ❌ `DAILY_SNAPSHOT_COMPLETE.md` - upgrade complete
- ❌ `DAILY_SNAPSHOT_GUIDE.md` - guide (done)
- ❌ `DASHBOARD_UPGRADE_COMPLETE.md` - upgrade done
- ❌ `DEPLOYMENT_GUIDE.md` - może zachować?
- ❌ `DEPLOYMENT_PACKAGE_INFO.md` - info package
- ❌ `FINAL_PRODUCTION_SUMMARY.md` - summary
- ❌ `FIRST_STEPS.md` - pierwsze kroki (stare)
- ❌ `GOOGLE_SHEETS_MIGRATION.md` - migration done
- ❌ `KRYPTO_MIGRATION.md` - migration done
- ❌ `PERSISTENCE_SYSTEM.md` - może zachować?
- ❌ `POST_UPGRADE_CHECKLIST.md` - checklist (done)
- ❌ `PODSUMOWANIE_PROGRAMU.md` - summary
- ❌ `STREAMLIT_FULL_FEATURES.md` - features list
- ❌ `STREAMLIT_README.md` - README
- ❌ `UPGRADE_SUMMARY_V2.md` - upgrade summary
- ❌ `CO_BEDZIE_WYSLANE.md` - temp file
- ❌ `GITHUB_TOKEN_SETUP.md` - setup done
- ❌ `TRADING212_INTEGRATION.md` - integration done
- ❌ `NEXUS_IMPLEMENTATION_PLAN.md` - plan (DONE!)

### Old Memory/Persona Files (ZASTĄPIONE)
- ❌ `advisor_memory.py` - stary system
- ❌ `advisor_memory_old.py` - bardzo stary
- ❌ `.partner_memory_template.json` - template (niepotrzebny)
- ❌ `finalna_konfiguracja_person.txt` - ZASTĄPIONE przez persona_memory.json
- ❌ `kodeks_spolki_backup_20251024_175926.txt` - backup
- ❌ `persona_memory_backup_20251110_160939.json` - backup
- ❌ `NOWE_skompilowane_persony.txt` - stare
- ❌ `kompilator_pamieci.py` - stary kompilator
- ❌ `rebuild_personas.py` - rebuild tool (done)
- ❌ `upgrade_persona_memory.py` - upgrade tool (done)

### Test/Fix Scripts (JEDNORAZOWE)
- ❌ `test_imports.py` - test (może zostawić do debugowania?)
- ❌ `test_loader_minimal.py` - test
- ❌ `test_personas_load.py` - test
- ❌ `check_plotly.py` - jednorazowy test
- ❌ `fix_emoji.py` - jednorazowa naprawa
- ❌ `fix_emoji_routing.py` - fix
- ❌ `fix_emoji_routing2.py` - fix
- ❌ `fix_emoji_routing3.py` - fix
- ❌ `fix_json_encoding.py` - fix
- ❌ `fix_messages.py` - fix
- ❌ `fix_plotly.py` - fix
- ❌ `fix_width.py` - fix

### Utility Scripts (NIEUŻYWANE?)
- ❌ `benchmark_comparison.py` - benchmark (nieużywane?)
- ❌ `generate_hash.py` - generator hash (jednorazowy)
- ❌ `generator_celow.py` - generator celów (nieużywany?)
- ❌ `github_api.py` - GitHub API (nieużywane?)
- ❌ `news_aggregator.py` - agregator news (nieużywany?)
- ❌ `portfolio_analyzer.py` - analyzer (duplikat z analiza_portfela.py?)
- ❌ `sync_data.py` - sync (nieużywany?)
- ❌ `tworca_streszczenia.py` - twórca (nieużywany?)
- ❌ `goal_analytics.py` - analytics (nieużywane?)

### HTML Files (STARE DASHBOARDY)
- ❌ `dashboard_inwestycyjny.html` - stary dashboard
- ❌ `dashboard_wykres_1.html` - stary wykres
- ❌ `dashboard_wykres_2.html` - stary wykres
- ❌ `dashboard_wykres_3.html` - stary wykres

### Bash/Shell Scripts (RASPBERRY PI - niepotrzebne na Windows?)
- ❌ `backup.sh` - backup script
- ❌ `setup_cloudflare.sh` - cloudflare setup
- ❌ `setup_pi.sh` - raspberry pi setup
- ❌ `start.sh` - start script
- ❌ `stop.sh` - stop script

### Bat Files (Windows - ZACHOWAĆ jeśli używane)
- ⚠️ `run_daily_snapshot.bat` - czy używane?
- ⚠️ `run_dashboard.bat` - czy używane?
- ⚠️ `run_knowledge_updater.bat` - czy używane?
- ⚠️ `run_news_update.bat` - czy używane?
- ⚠️ `sprawdz_pliki.bat` - czy używane?

### Temp/Log Files
- ❌ `gemini_last_call.txt` - temp log
- ❌ `glowne_streszczenie.txt` - streszczenie
- ❌ `historia_firmy.txt` - historia
- ❌ `kronika_spotkan.txt` - kronika
- ❌ `Nowy Dokument tekstowy.txt` - temp file
- ❌ `raport_portfela_20251019_190038.xlsx` - stary raport
- ❌ `compliance_log.json` - log (czy używany?)

### Documentation to KEEP
- ✅ `README.md` - główny README
- ✅ `GUIDE_AI_PARTNERS.md` - aktualny guide
- ✅ `QUICK_REFERENCE_V2.md` - quick ref
- ✅ `QUICK_START.md` - quick start
- ✅ `NEXUS_TEST_PLAN.md` - test plan (NOWY!)
- ✅ `START_HERE.md` - start here
- ⚠️ `README_RASPBERRY_PI.md` - Pi readme (zachować?)

### Other
- ✅ `.env.template` - template (ZACHOWAĆ)
- ✅ `.gitignore` - git config
- ✅ `packages.txt` - packages list
- ⚠️ `.devcontainer/` - dev container (używane?)
- ⚠️ `.venv/` - virtual env (lokalne)
- ⚠️ `.vscode/` - VS Code settings (lokalne)

---

## 📊 PODSUMOWANIE

**Do usunięcia:** ~60 plików
**Do zachowania:** ~80 plików/folderów
**Do sprawdzenia z Tobą:** ~10 plików (.bat, compliance_log.json, etc.)

**Pytania:**
1. Czy używasz plików `.bat` do uruchamiania rzeczy?
2. Czy `compliance_log.json` jest potrzebny?
3. Czy chcesz zachować `README_RASPBERRY_PI.md`?
4. Czy `.devcontainer/` jest używany?
