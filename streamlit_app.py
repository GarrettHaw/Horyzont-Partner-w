"""
🏢 HORYZONT PARTNERÓW - Streamlit Dashboard
Interaktywny dashboard do zarządzania portfelem inwestycyjnym
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import hashlib

# Import systemu persystencji
try:
    from persistent_storage import load_persistent_data, save_persistent_data, show_sync_widget
    PERSISTENT_OK = True
except:
    PERSISTENT_OK = False

# Konfiguracja strony - MUSI być jako pierwsze
st.set_page_config(
    page_title="Horyzont Partnerów",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CONFIGURATION CONSTANTS ===
DEFAULT_USD_PLN_RATE = 3.65  # Default USD/PLN exchange rate

# === SYSTEM LOGOWANIA ===
def check_password():
    """Zwraca True jeśli użytkownik wprowadził poprawne hasło."""
    
    def password_entered():
        """Sprawdza czy hasło jest poprawne."""
        # Hasło zahashowane SHA256 (bezpieczne przechowywanie)
        correct_password_hash = st.secrets.get("PASSWORD_HASH", 
            "c75814b6fdb3b8b95a4619f6cd20d072e5525b7571908993d4398e8b38c5e685")  # Shinobi123!
        
        entered_password = st.session_state["password"]
        entered_hash = hashlib.sha256(entered_password.encode()).hexdigest()
        
        if entered_hash == correct_password_hash:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Usuń hasło z pamięci
        else:
            st.session_state["password_correct"] = False

    # Jeśli już zalogowany, zwróć True
    if st.session_state.get("password_correct", False):
        return True

    # Pokaż ekran logowania
    st.markdown("""
    <div style="text-align: center; padding: 50px 20px;">
        <h1 style="color: #1f77b4;">🔐 HORYZONT PARTNERÓW</h1>
        <p style="font-size: 18px; color: #666;">Zaloguj się aby kontynuować</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "Hasło", 
            type="password", 
            on_change=password_entered, 
            key="password",
            placeholder="Wprowadź hasło dostępu"
        )
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ Nieprawidłowe hasło")
    
    return False

# Sprawdź logowanie PRZED załadowaniem reszty aplikacji
if not check_password():
    st.stop()  # Zatrzymaj wykonywanie jeśli nie zalogowany

# === EKRAN ŁADOWANIA ===
if 'app_loaded' not in st.session_state:
    st.session_state.app_loaded = False

if not st.session_state.app_loaded:
    # Pokaż ekran ładowania
    with st.spinner(''):
        st.markdown("""
        <div style="text-align: center; padding: 100px 20px;">
            <h1 style="color: #1f77b4;">🏢 HORYZONT PARTNERÓW</h1>
            <p style="font-size: 18px; color: #666;">🚀 100% Lazy Loading - start w <5 sekund!</p>
            <p style="font-size: 14px; color: #999;">Wszystkie AI/Sheets załadują się dopiero gdy będą użyte</p>
            <p style="font-size: 12px; color: #aaa;">Gemini: pierwszy chat | Claude/OpenAI: wybór w ustawieniach | Sheets: load danych</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Krok 1: Podstawowe moduły
        status_text.text("📦 Ładowanie modułów podstawowych...")
        progress_bar.progress(20)

# API Usage Tracker
from api_usage_tracker import get_tracker

# Email Notifier (dla Fazy 2)
from email_notifier import get_conversation_notifier

# Consultation System (dla Fazy 2D)
from consultation_system import get_consultation_manager

# Folder dla pamięci długoterminowej
MEMORY_FOLDER = Path("partner_memories")
MEMORY_FOLDER.mkdir(exist_ok=True)

# Importy z głównego programu
if not st.session_state.app_loaded:
    status_text.text("🚀 100% lazy load - bez AI przy starcie!")
    progress_bar.progress(40)

try:
    from gra_rpg import (
        pobierz_stan_spolki,
        wczytaj_cele,
        print_colored,
        generuj_odpowiedz_ai,
        PERSONAS
    )
    
    if not st.session_state.app_loaded:
        status_text.text("📊 Ładowanie modułów analitycznych...")
        progress_bar.progress(60)
    
    from risk_analytics import RiskAnalytics, PortfolioHistory
    from animated_timeline import AnimatedTimeline
    from excel_reporter import ExcelReportGenerator, generate_full_report
    
    if not st.session_state.app_loaded:
        status_text.text("🧠 Inicjalizuję pamięć AI partnerów...")
        progress_bar.progress(80)
    
    import persona_memory_manager as pmm
    from persona_context_builder import build_enhanced_context, get_emotional_modifier, load_persona_memory
    from crypto_portfolio_manager import CryptoPortfolioManager
    
    IMPORTS_OK = True
    MEMORY_OK = True
    MEMORY_V2 = True
    CRYPTO_MANAGER_OK = True
    
    if not st.session_state.app_loaded:
        status_text.text("✅ Gotowe! Uruchamiam dashboard...")
        progress_bar.progress(100)
        st.session_state.app_loaded = True
        st.rerun()
        
except ImportError as e:
    if "persona_memory_manager" in str(e) or "persona_context_builder" in str(e):
        IMPORTS_OK = True
        MEMORY_OK = False
        MEMORY_V2 = False
        CRYPTO_MANAGER_OK = "crypto_portfolio_manager" not in str(e)
        st.warning("⚠️ System pamięci AI niedostępny")
    elif "crypto_portfolio_manager" in str(e):
        IMPORTS_OK = True
        MEMORY_OK = True
        MEMORY_V2 = True
        CRYPTO_MANAGER_OK = False
        st.warning("⚠️ Crypto Portfolio Manager niedostępny - ceny na żywo wyłączone")
    else:
        IMPORTS_OK = False
        MEMORY_OK = False
        MEMORY_V2 = False
        CRYPTO_MANAGER_OK = False
        st.error(f"⚠️ Błąd importu: {e}")
    
    if not st.session_state.app_loaded:
        st.session_state.app_loaded = True
        st.rerun()
        
except Exception as e:
    IMPORTS_OK = False
    MEMORY_OK = False
    MEMORY_V2 = False
    CRYPTO_MANAGER_OK = False
    st.error(f"⚠️ Błąd importu: {e}")
    
    if not st.session_state.app_loaded:
        st.session_state.app_loaded = True
        st.rerun()
    import traceback
    st.code(traceback.format_exc())

# === FUNKCJE DO ZARZĄDZANIA WAGAMI GŁOSU Z KODEKSU ===
def wczytaj_wagi_glosu_z_kodeksu():
    """
    Parsuje kodeks_spolki.txt i zwraca słownik z wagami głosu dla każdego partnera.
    Mapuje nazwy z kodeksu na nazwy w PERSONAS.
    
    Returns:
        dict: {nazwa_partnera: procent_glosu}
    """
    import re
    
    if not os.path.exists('kodeks_spolki.txt'):
        return {}
    
    with open('kodeks_spolki.txt', 'r', encoding='utf-8') as f:
        kodeks = f.read()
    
    # Mapowanie nazw z kodeksu na RZECZYWISTE nazwy w PERSONAS
    # UWAGA: W kodeksie są stare nazwy, w PERSONAS są inne!
    mapping = {
        "Partner Zarządzający (Pan)": "Partner Zarządzający (JA)",
        "Partner Strategiczny (Ja)": "Partner Strategiczny",
        "Partner ds. Jakości Biznesowej": "Partner ds. Jakości Biznesowej",
        "Partner ds. Aktywów Cyfrowych": "Partner ds. Aktywów Cyfrowych",
        "Konsultant Strategiczny ds. Aktywów Cyfrowych": "Changpeng Zhao (CZ)"
    }
    
    wagi = {}
    
    # Szukaj linii z procentami głosu lub wpływu filozoficznego
    pattern = r'(.+?):\s*(\d+)%\s+(?:udziałów w głosach|wpływu filozoficznego)'
    matches = re.findall(pattern, kodeks)
    
    for nazwa_surowa, procent in matches:
        nazwa = nazwa_surowa.strip()
        procent_float = float(procent)
        
        if nazwa in mapping:
            persona_name = mapping[nazwa]
            wagi[persona_name] = procent_float
        elif "Rada Nadzorcza" in nazwa:
            # Rada Nadzorcza 15% - rozdziel równo między członków w PERSONAS
            # W PERSONAS mamy: Benjamin Graham, Philip Fisher, George Soros, Warren Buffett
            rada_nadzorcza = [
                "Benjamin Graham",
                "Philip Fisher", 
                "George Soros",
                "Warren Buffett"
            ]
            na_osobe = procent_float / len(rada_nadzorcza)
            for czlonek in rada_nadzorcza:
                wagi[czlonek] = na_osobe
    
    return wagi

def zapisz_wagi_glosu_do_kodeksu(wagi):
    """
    Zapisuje zaktualizowane wagi głosu z powrotem do kodeksu_spolki.txt.
    
    Args:
        wagi (dict): {nazwa_partnera: procent_glosu}
    """
    import re
    
    if not os.path.exists('kodeks_spolki.txt'):
        st.error("Nie znaleziono pliku kodeks_spolki.txt")
        return False
    
    with open('kodeks_spolki.txt', 'r', encoding='utf-8') as f:
        kodeks = f.read()
    
    # Odwrotne mapowanie - z RZECZYWISTYCH nazw PERSONAS na nazwy w kodeksie
    reverse_mapping = {
        "Partner Zarządzający (JA)": "Partner Zarządzający (Pan)",
        "Partner Strategiczny": "Partner Strategiczny (Ja)",
        "Partner ds. Jakości Biznesowej": "Partner ds. Jakości Biznesowej",
        "Partner ds. Aktywów Cyfrowych": "Partner ds. Aktywów Cyfrowych",
        "Changpeng Zhao (CZ)": "Konsultant Strategiczny ds. Aktywów Cyfrowych"
    }
    
    # Rada Nadzorcza - zsumuj wagi członków (RZECZYWISTE nazwy z PERSONAS)
    rada_nadzorcza = [
        "Benjamin Graham",
        "Philip Fisher",
        "George Soros",
        "Warren Buffett"
    ]
    
    rada_suma = sum(wagi.get(czlonek, 0) for czlonek in rada_nadzorcza)
    
    # Aktualizuj poszczególne linie w kodeksie
    for persona_name, procent in wagi.items():
        if persona_name in reverse_mapping:
            kodeks_name = reverse_mapping[persona_name]
            # Znajdź linię z tą nazwą i zaktualizuj procent
            pattern = rf'({re.escape(kodeks_name)}:\s*)\d+(% udziałów w głosach)'
            kodeks = re.sub(pattern, rf'\g<1>{int(procent)}\g<2>', kodeks)
    
    # Zaktualizuj Radę Nadzorczą (wpływ filozoficzny)
    if rada_suma > 0:
        pattern = r'(Rada Nadzorcza.*?:\s*)\d+(% wpływu filozoficznego)'
        kodeks = re.sub(pattern, rf'\g<1>{int(rada_suma)}\g<2>', kodeks)
    
    # Zapisz zaktualizowany kodeks
    try:
        with open('kodeks_spolki.txt', 'w', encoding='utf-8') as f:
            f.write(kodeks)
        return True
    except Exception as e:
        st.error(f"Błąd zapisu kodeksu: {e}")
        return False

# Funkcje pomocnicze do integracji AI
def send_to_ai_partner(partner_name, message, stan_spolki=None, cele=None, tryb_odpowiedzi="normalny"):
    """Wysyła wiadomość do pojedynczego Partnera AI z pełnym kontekstem jak w gra_rpg.py"""
    try:
        if not IMPORTS_OK:
            return "[Import gra_rpg.py nie powiódł się]"
        
        # Pobierz konfigurację partnera
        persona_config = PERSONAS.get(partner_name, {})
        
        # === KODEKS SPÓŁKI ===
        kodeks = ""
        if os.path.exists('kodeks_spolki.txt'):
            with open('kodeks_spolki.txt', 'r', encoding='utf-8') as f:
                kodeks = f.read()
        
        # === PRZYGOTUJ DANE FINANSOWE ===
        if not stan_spolki:
            stan_spolki = {}
        
        # Podstawowe wartości
        akcje_val = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
        krypto_val = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
        rezerwa_val = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
        dlugi_val = get_suma_kredytow()  # Pobierz z kredyty.json zamiast Google Sheets
        wyplata_info = stan_spolki.get('wyplata', {})
        dostepne = wyplata_info.get('dostepne_na_inwestycje', 0)
        
        # === SZCZEGÓŁY POZYCJI (TOP 10) ===
        pozycje_szczegoly = stan_spolki.get('akcje', {}).get('pozycje', {})
        sorted_pozycje = sorted(
            pozycje_szczegoly.items(),
            key=lambda x: x[1].get('wartosc_total_usd', 0),
            reverse=True
        )
        
        szczegoly_top10 = "\n\n📊 SZCZEGÓŁY TOP 10 POZYCJI W PORTFELU:\n"
        for ticker, dane in sorted_pozycje[:10]:
            szczegoly_top10 += f"• {ticker}:\n"
            szczegoly_top10 += f"  - Ilość: {dane.get('ilosc', 0):.2f} akcji\n"
            szczegoly_top10 += f"  - Wartość: ${dane.get('wartosc_total_usd', 0):.2f} (${dane.get('wartosc_obecna_usd', 0):.2f}/akcja)\n"
            szczegoly_top10 += f"  - Koszt zakupu: ${dane.get('koszt_total_usd', 0):.2f} (${dane.get('cena_zakupu_usd', 0):.2f}/akcja)\n"
            szczegoly_top10 += f"  - Zysk/Strata: ${dane.get('zysk_total_usd', 0):.2f} ({dane.get('zmiana_proc', 0):.1f}%)\n"
        
        # === DANE RYNKOWE ===
        dane_rynkowe_str = "\n\n📈 DANE RYNKOWE (wybrane spółki):\n"
        dane_rynkowe = {}
        if IMPORTS_OK:
            try:
                from gra_rpg import pobierz_stan_spolki
                stan_pelny = pobierz_stan_spolki(cele or {})
                if stan_pelny:
                    dane_rynkowe = stan_pelny.get('PORTFEL_AKCJI', {}).get('Dane_rynkowe', {})
            except Exception as e:
                # Nie ma gra_rpg.py lub błąd ładowania - używaj stan_spolki z parametru
                pass
        
        if dane_rynkowe:
            for ticker, dane in list(dane_rynkowe.items())[:8]:
                pe = dane.get('PE')
                pe_str = f"P/E: {pe:.1f}" if pe and pe > 0 else "P/E: N/A"
                dywidenda = dane.get('dywidenda_roczna', 0)
                dywidenda_str = f"Dywidenda: {dywidenda*100:.1f}%" if dywidenda else "Dywidenda: N/A"
                sektor = dane.get('sektor', 'N/A')
                dane_rynkowe_str += f"• {dane.get('nazwa', ticker)} ({ticker}): {pe_str}, {dywidenda_str}, {sektor}\n"
        else:
            dane_rynkowe_str += "Brak dostępnych danych rynkowych.\n"
        
        # === KONTEKST SKALI ===
        kontekst_skali = f"\n\n⚖️ KONTEKST SKALI:\n"
        kontekst_skali += f"To są prywatne finanse osoby fizycznej.\n"
        kontekst_skali += f"Dostępny kapitał miesięcznie: ~{dostepne:.2f} PLN\n"
        kontekst_skali += f"Wartość netto portfela: {akcje_val + krypto_val + rezerwa_val - dlugi_val:.2f} PLN (Akcje + Krypto + Rezerwa - Zobowiązania)\n"
        
        # === HISTORIA SNAPSHOTS ===
        snapshot_section = ""
        try:
            import daily_snapshot as ds
            history = ds.load_snapshot_history()
            if len(history) >= 2:
                stats = ds.get_snapshot_stats()
                first = history[0]
                last = history[-1]
                
                snapshot_section = f"\n\n📸 HISTORIA PORTFOLIO (DAILY SNAPSHOTS):\n"
                snapshot_section += f"- Okres śledzenia: {stats['first_date']} → {stats['last_date']} ({stats['days_tracked']} dni)\n"
                snapshot_section += f"- Liczba snapshots: {stats['count']}\n"
                snapshot_section += f"- Net Worth PIERWSZY: {first['totals']['net_worth_pln']:.2f} PLN\n"
                snapshot_section += f"- Net Worth OSTATNI: {last['totals']['net_worth_pln']:.2f} PLN\n"
                snapshot_section += f"- Zmiana: {stats['percent_change']:.2f}%\n"
                snapshot_section += f"- Średnio snapshots/tydzień: {stats['avg_per_week']:.1f}\n\n"
                snapshot_section += "OSTATNIE 3 SNAPSHOTS:\n"
                
                for h in history[-3:]:
                    snapshot_section += f"• {h['date_only']}: Net Worth {h['totals']['net_worth_pln']:.2f} PLN "
                    snapshot_section += f"(Akcje: {h['stocks']['value_pln']:.0f} PLN, Krypto: {h['crypto']['value_pln']:.0f} PLN, Długi: {h['debt']['total_pln']:.0f} PLN)\n"
        except:
            pass  # Jeśli brak snapshots lub błąd importu, kontynuuj bez tej sekcji
        
        # === INSTRUKCJE DŁUGOŚCI ODPOWIEDZI ===
        if tryb_odpowiedzi == "zwiezly":
            length_instruction = """
TRYB ODPOWIEDZI: ZWIĘZŁY
- Odpowiedź 2-4 zdania MAX
- Tylko najważniejsze punkty
- Konkretne liczby i wnioski
- Brak rozbudowanych wyjaśnień
"""
        elif tryb_odpowiedzi == "szczegolowy":
            length_instruction = """
TRYB ODPOWIEDZI: SZCZEGÓŁOWY
- Pełna analiza (8-12 zdań)
- Dokładne wyjaśnienia i uzasadnienia
- Odniesienia do konkretnych pozycji
- Rekomendacje krok po kroku
- Cytuj Kodeks gdy stosowne
"""
        else:
            length_instruction = """
TRYB ODPOWIEDZI: NORMALNY
- Odpowiedź 4-6 zdań
- Balans między szczegółami a zwięzłością
- Konkretne dane z portfela
- Praktyczne wnioski
"""
        
        # === PAMIĘĆ DŁUGOTERMINOWA (20 ostatnich rozmów dla lepszego kontekstu) ===
        memory_context = load_memory_context(partner_name, limit=20)
        memory_section = memory_context if memory_context else ""
        
        # === PAMIĘĆ PERSONY (track record i ewolucja) ===
        persona_memory_section = ""
        emotional_hint = ""
        if MEMORY_OK:
            try:
                if MEMORY_V2:
                    # v2.0: Rozbudowany kontekst z emocjami, relacjami, voting weights
                    persona_memory_section = build_enhanced_context(partner_name, limit=5)
                    emotional_hint = get_emotional_modifier(partner_name)
                else:
                    # v1.0: Podstawowy kontekst
                    persona_memory_section = pmm.get_persona_context(partner_name)
                
                pmm.increment_session(partner_name)
            except Exception as e:
                st.warning(f"⚠️ Błąd wczytywania pamięci persony: {e}")
        
        # === MOOD SYSTEM ===
        portfolio_mood = analyze_portfolio_mood(stan_spolki, cele)
        mood_modifier = get_partner_mood_modifier(partner_name, portfolio_mood)
        
        # === KNOWLEDGE BASE ===
        relevant_knowledge = get_relevant_knowledge(message, stan_spolki, partner_name, max_items=2)
        knowledge_section = format_knowledge_for_prompt(relevant_knowledge)
        
        # === PROAKTYWNE ALERTY ===
        alerts = check_portfolio_alerts(stan_spolki, cele)
        alerts_section = ""
        
        if alerts:
            # Dodaj tylko najważniejsze alerty do promptu
            critical_alerts = [a for a in alerts if a["severity"] == "critical"]
            warning_alerts = [a for a in alerts if a["severity"] == "warning"]
            important_alerts = critical_alerts + warning_alerts[:2]  # Max 2 warning
            
            if important_alerts:
                alerts_section = "\n\n🚨 AKTYWNE ALERTY PORTFELA:\n"
                for alert in important_alerts:
                    severity_emoji = "🔴" if alert["severity"] == "critical" else "🟡"
                    alerts_section += f"{severity_emoji} {alert['title']}: {alert['message']}\n"
                    if alert.get('action'):
                        alerts_section += f"   → Rekomendacja: {alert['action']}\n"
                
                alerts_section += "\n⚠️ WAŻNE: Możesz odnieść się do tych alertów w swojej odpowiedzi jeśli są istotne dla pytania użytkownika!\n"
        
        # === NEWSY FINANSOWE ===
        news_section = ""
        try:
            import news_aggregator as na
            news_section = na.format_news_for_ai(limit=5)
        except Exception as e:
            # Jeśli news_aggregator nie działa, pomijamy tę sekcję
            pass
        
        # === BUDOWA PROMPTU (JAK W GRA_RPG.PY) ===
        prompt = f"""{persona_config.get('system_instruction', '')}

KODEKS SPÓŁKI "HORYZONT PARTNERÓW":
    {kodeks}

---
Twoim tajnym celem jest: {persona_config.get('ukryty_cel', 'Wspieranie rozwoju spółki')}
---

{persona_memory_section}

{emotional_hint}

{memory_section}

{mood_modifier}

{alerts_section}

{knowledge_section}

AKTUALNY STAN FINANSOWY SPÓŁKI:

💰 PODSUMOWANIE:
    - Wartość netto: {akcje_val + krypto_val + rezerwa_val - dlugi_val:.2f} PLN (Akcje + Krypto + Rezerwa - Zobowiązania)
- Akcje: {akcje_val:.2f} PLN ({stan_spolki.get('akcje', {}).get('liczba_pozycji', 0)} pozycji)
- Krypto: {krypto_val:.2f} PLN ({stan_spolki.get('krypto', {}).get('liczba_pozycji', 0)} pozycji)
- Rezerwa Gotówkowa: {rezerwa_val:.2f} PLN  
- Zobowiązania: {dlugi_val:.2f} PLN
- Dostępne na inwestycje: {dostepne:.2f} PLN/mies.

{szczegoly_top10}

{dane_rynkowe_str}

{kontekst_skali}

{snapshot_section}

{news_section}

---
{length_instruction}
---

PYTANIE UŻYTKOWNIKA:
    "{message}"

TWOJE ZADANIE:
    Odpowiedz jako członek Zarządu spółki inwestycyjnej:
- Odwołuj się do Kodeksu gdy stosowne (np. "Zgodnie z Artykułem IV §1...")
- Analizuj konkretne liczby z portfela
- Ton profesjonalny ale nie przesadnie korporacyjny
- Wykorzystaj swoją unikalną perspektywę i wiedzę
- Realizuj swój ukryty cel w sposób subtelny
"""
        
        # Wywołaj AI
        response = generuj_odpowiedz_ai(partner_name, prompt)
        
        # Bezpiecznie wydobądź tekst z response (może być string lub obiekt)
        if hasattr(response, 'text'):
            response_text = response.text
        elif isinstance(response, str):
            response_text = response
        else:
            response_text = str(response)
        
        # Zapisz do pamięci długoterminowej
        save_conversation_to_memory(partner_name, message, response_text, stan_spolki)
        
        return response_text, relevant_knowledge
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"[Błąd AI: {str(e)}\n{error_detail}]", []

def save_conversation_to_memory(partner_name, user_message, ai_response, stan_spolki=None):
    """Zapisuje rozmowę do pamięci długoterminowej partnera"""
    try:
        # Załaduj istniejącą pamięć przez persistence system
        if PERSISTENT_OK:
            memory = load_persistent_data('persona_memory.json')
            if memory is None:
                memory = {}
        else:
            # Fallback - odczyt z pliku
            memory_file = MEMORY_FOLDER / f"{partner_name.replace('/', '_').replace(' ', '_')}.json"
            if memory_file.exists():
                with open(memory_file, 'r', encoding='utf-8-sig') as f:
                    memory = json.load(f)
            else:
                memory = {}
        
        # Stwórz strukturę dla partnera jeśli nie istnieje
        partner_key = partner_name.replace('/', '_').replace(' ', '_')
        if partner_key not in memory:
            memory[partner_key] = {
                "partner_name": partner_name,
                "conversations": [],
                "statistics": {
                    "total_messages": 0,
                    "first_interaction": datetime.now().isoformat(),
                    "last_interaction": None,
                    "topics_discussed": []
                },
                "insights": {
                    "user_preferences": [],
                    "recurring_questions": [],
                    "portfolio_changes_noted": []
                }
            }
        
        # Dodaj nową rozmowę
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "ai_response": ai_response,
            "portfolio_snapshot": {
                "total_value": (stan_spolki.get('akcje', {}).get('wartosc_pln', 0) + 
                               stan_spolki.get('krypto', {}).get('wartosc_pln', 0)) if stan_spolki else 0,
                "debt": get_suma_kredytow()  # Pobierz z kredyty.json
            } if stan_spolki else None
        }
        
        memory[partner_key]["conversations"].append(conversation_entry)
        memory[partner_key]["statistics"]["total_messages"] += 1
        memory[partner_key]["statistics"]["last_interaction"] = datetime.now().isoformat()
        
        # USUNIĘTY LIMIT - pamięć długoterminowa powinna kumulować całą wiedzę!
        # Partnerzy uczą się z każdej rozmowy i nigdy nie zapominają
        
        # Zapisz przez persistence system
        if PERSISTENT_OK:
            return save_persistent_data('persona_memory.json', memory)
        else:
            # Fallback - zapis do pliku
            memory_file = MEMORY_FOLDER / f"{partner_name.replace('/', '_').replace(' ', '_')}.json"
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory[partner_key], f, ensure_ascii=False, indent=2)
            return True
            
    except Exception as e:
        print(f"Błąd zapisu pamięci dla {partner_name}: {e}")
        return False

def load_memory_context(partner_name, limit=20):
    """Ładuje kontekst z pamięci długoterminowej partnera"""
    try:
        partner_key = partner_name.replace('/', '_').replace(' ', '_')
        
        # Załaduj przez persistence system
        if PERSISTENT_OK:
            all_memory = load_persistent_data('persona_memory.json')
            if all_memory is None or partner_key not in all_memory:
                return None
            memory = all_memory[partner_key]
        else:
            # Fallback - odczyt z pliku
            memory_file = MEMORY_FOLDER / f"{partner_key}.json"
            if not memory_file.exists():
                return None
            with open(memory_file, 'r', encoding='utf-8-sig') as f:
                memory = json.load(f)
        
        # Pobierz ostatnie N rozmów (domyślnie 20 - więcej kontekstu = lepsza pamięć)
        recent_conversations = memory["conversations"][-limit:] if memory["conversations"] else []
        
        if not recent_conversations:
            return None
        
        # Formatuj kontekst - PEŁNE teksty dla lepszego zrozumienia
        context = "\n\n📚 TWOJA PAMIĘĆ DŁUGOTERMINOWA:\n"
        context += f"Masz {memory['statistics']['total_messages']} rozmów w pamięci. "
        context += f"Oto ostatnie {len(recent_conversations)} rozmów:\n\n"
        
        for conv in recent_conversations:
            date = datetime.fromisoformat(conv['timestamp']).strftime("%Y-%m-%d %H:%M")
            context += f"{'='*60}\n"
            context += f"📅 [{date}]\n\n"
            context += f"👤 Użytkownik:\n{conv['user_message']}\n\n"
            context += f"🤖 Ty odpowiedziałeś:\n{conv['ai_response']}\n\n"
            
            # Dodaj snapshot portfela jeśli istnieje
            if conv.get('portfolio_snapshot'):
                snapshot = conv['portfolio_snapshot']
                context += f"💼 Stan portfela w tamtym momencie:\n"
                context += f"   Wartość: {snapshot.get('total_value', 0):,.0f} PLN\n"
                context += f"   Długi: {snapshot.get('debt', 0):,.0f} PLN\n\n"
        
        context += f"{'='*60}\n\n"
        context += "💡 Wykorzystaj tę wiedzę aby udzielać spersonalizowanych, kontekstowych odpowiedzi!\n"
        
        return context
        
    except Exception as e:
        print(f"Błąd ładowania pamięci dla {partner_name}: {e}")
        return None

def get_memory_statistics(partner_name):
    """Pobiera statystyki pamięci partnera"""
    try:
        partner_key = partner_name.replace('/', '_').replace(' ', '_')
        
        # Załaduj przez persistence system
        if PERSISTENT_OK:
            all_memory = load_persistent_data('persona_memory.json')
            if all_memory is None or partner_key not in all_memory:
                return None
            memory = all_memory[partner_key]
        else:
            # Fallback - odczyt z pliku
            memory_file = MEMORY_FOLDER / f"{partner_key}.json"
            if not memory_file.exists():
                return None
            with open(memory_file, 'r', encoding='utf-8-sig') as f:
                memory = json.load(f)
        
        return memory["statistics"]
    except:
        return None

def analyze_portfolio_mood(stan_spolki, cele=None):
    """Analizuje stan portfela i zwraca nastrój (mood) oraz szczegóły"""
    try:
        if not stan_spolki:
            return {"mood": "neutral", "emoji": "😐", "reason": "Brak danych portfela"}
        
        mood_data = {
            "mood": "neutral",
            "emoji": "😐",
            "score": 0,  # -100 do +100
            "factors": [],
            "warnings": [],
            "highlights": []
        }
        
        # Pobierz dane
        akcje_val = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
        krypto_val = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
        rezerwa_val = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
        dlugi_val = get_suma_kredytow()  # Pobierz z kredyty.json
        pozycje = stan_spolki.get('akcje', {}).get('pozycje', {})
        
        total_assets = akcje_val + krypto_val + rezerwa_val
        net_worth = total_assets - dlugi_val
        
        # === ANALIZA 1: Ogólna performance portfela ===
        if pozycje:
            positions_with_change = [(ticker, data) for ticker, data in pozycje.items() 
                                    if data.get('zmiana_proc') is not None]
            
            if positions_with_change:
                avg_change = sum(p[1].get('zmiana_proc', 0) for p in positions_with_change) / len(positions_with_change)
                
                if avg_change > 15:
                    mood_data["score"] += 40
                    mood_data["highlights"].append(f"🎉 Świetna performance! Średni zysk: +{avg_change:.1f}%")
                elif avg_change > 5:
                    mood_data["score"] += 20
                    mood_data["highlights"].append(f"📈 Dobry wzrost: +{avg_change:.1f}%")
                elif avg_change < -10:
                    mood_data["score"] -= 40
                    mood_data["warnings"].append(f"📉 Portfel spada: {avg_change:.1f}%")
                elif avg_change < -5:
                    mood_data["score"] -= 20
                    mood_data["warnings"].append(f"⚠️ Lekkie spadki: {avg_change:.1f}%")
        
        # === ANALIZA 2: Leverage i ryzyko ===
        if total_assets > 0:
            leverage = (dlugi_val / total_assets) * 100
            
            if leverage > 50:
                mood_data["score"] -= 30
                mood_data["warnings"].append(f"⚠️ WYSOKI leverage: {leverage:.1f}%")
            elif leverage > 30:
                mood_data["score"] -= 15
                mood_data["warnings"].append(f"⚠️ Podwyższony leverage: {leverage:.1f}%")
            elif leverage < 15 and dlugi_val > 0:
                mood_data["score"] += 10
                mood_data["highlights"].append(f"✅ Zdrowy leverage: {leverage:.1f}%")
        
        # === ANALIZA 3: Największe pozycje ===
        if pozycje:
            sorted_pozycje = sorted(pozycje.items(), 
                                   key=lambda x: x[1].get('wartosc_total_usd', 0), 
                                   reverse=True)
            
            # Najlepszy performer
            best = max(positions_with_change, key=lambda x: x[1].get('zmiana_proc', 0)) if positions_with_change else None
            if best and best[1].get('zmiana_proc', 0) > 30:
                mood_data["score"] += 15
                mood_data["highlights"].append(f"🚀 {best[0]}: +{best[1].get('zmiana_proc', 0):.1f}% 🔥")
            
            # Najgorszy performer
            worst = min(positions_with_change, key=lambda x: x[1].get('zmiana_proc', 0)) if positions_with_change else None
            if worst and worst[1].get('zmiana_proc', 0) < -20:
                mood_data["score"] -= 15
                mood_data["warnings"].append(f"💔 {worst[0]}: {worst[1].get('zmiana_proc', 0):.1f}%")
        
        # === ANALIZA 4: Wartość netto ===
        if net_worth > 50000:
            mood_data["score"] += 20
            mood_data["highlights"].append(f"💰 Silna pozycja: {net_worth:.0f} PLN netto")
        elif net_worth < 0:
            mood_data["score"] -= 50
            mood_data["warnings"].append(f"🚨 UJEMNA wartość netto: {net_worth:.0f} PLN")
        
        # === OKREŚL MOOD na podstawie score ===
        final_score = mood_data["score"]
        
        if final_score >= 50:
            mood_data["mood"] = "very_bullish"
            mood_data["emoji"] = "🤩"
            mood_data["description"] = "Świetnie! Portfel rośnie silnie!"
        elif final_score >= 20:
            mood_data["mood"] = "bullish"
            mood_data["emoji"] = "😊"
            mood_data["description"] = "Dobry momentum, wszystko idzie dobrze"
        elif final_score >= -20:
            mood_data["mood"] = "neutral"
            mood_data["emoji"] = "😐"
            mood_data["description"] = "Stabilna sytuacja, bez większych zmian"
        elif final_score >= -50:
            mood_data["mood"] = "cautious"
            mood_data["emoji"] = "😟"
            mood_data["description"] = "Ostrożnie, niektóre sygnały ostrzegawcze"
        else:
            mood_data["mood"] = "bearish"
            mood_data["emoji"] = "😰"
            mood_data["description"] = "Trudny okres, wymaga uwagi i działania"
        
        return mood_data
        
    except Exception as e:
        return {
            "mood": "neutral",
            "emoji": "😐",
            "score": 0,
            "reason": f"Błąd analizy: {str(e)}",
            "factors": [],
            "warnings": [],
            "highlights": []
        }

def check_portfolio_alerts(stan_spolki, cele):
    """
    Sprawdza portfel pod kątem ważnych zdarzeń i zwraca listę alertów.
    
    Returns:
        list: Lista słowników z alertami [{type, severity, title, message, action, data}]
              severity: "critical" (czerwony), "warning" (żółty), "info" (niebieski), "success" (zielony)
    """
    alerts = []
    
    try:
        # Przygotuj dane
        portfel = stan_spolki.get("Pozycje_Portfela", [])
        total_value = stan_spolki.get("Wartosc_netto_portfela", 0)
        total_assets = stan_spolki.get("Aktywa", 0)
        dlugi = get_suma_kredytow()  # Pobierz z kredyty.json zamiast stan_spolki
        
        # === ALERT 1: Duże spadki pozycji (>5% w ostatnim okresie) ===
        for poz in portfel:
            zmiana = poz.get("Zmiana_%", 0)
            ticker = poz.get("Ticker", "???")
            wartosc = poz.get("Wartość", 0)
            udzial = (wartosc / total_value * 100) if total_value > 0 else 0
            
            if zmiana < -5 and udzial > 3:  # Spadek >5% i udział >3%
                alerts.append({
                    "type": "position_drop",
                    "severity": "critical" if zmiana < -10 else "warning",
                    "title": f"📉 Duży spadek: {ticker}",
                    "message": f"{ticker} spadł o {abs(zmiana):.1f}% (udział w portfelu: {udzial:.1f}%)",
                    "action": "Rozważ przeanalizowanie przyczyn spadku",
                    "data": {"ticker": ticker, "change": zmiana, "share": udzial}
                })
            
            # === ALERT 2: Duże wzrosty pozycji (>15%) - realizacja zysków? ===
            if zmiana > 15 and udzial > 5:
                alerts.append({
                    "type": "position_surge",
                    "severity": "info",
                    "title": f"🚀 Mocny wzrost: {ticker}",
                    "message": f"{ticker} urósł o {zmiana:.1f}% (udział: {udzial:.1f}%). Może czas na rebalancing?",
                    "action": "Rozważ częściową realizację zysków",
                    "data": {"ticker": ticker, "change": zmiana, "share": udzial}
                })
            
            # === ALERT 3: Wysokie P/E (>40) dla znaczących pozycji ===
            pe = poz.get("P/E", 0)
            if pe > 40 and udzial > 5:
                alerts.append({
                    "type": "high_valuation",
                    "severity": "warning",
                    "title": f"⚠️ Wysokie P/E: {ticker}",
                    "message": f"{ticker} ma P/E = {pe:.1f} (udział: {udzial:.1f}%). Spółka może być przewartościowana.",
                    "action": "Przeanalizuj fundamenty i potencjał wzrostu",
                    "data": {"ticker": ticker, "pe": pe, "share": udzial}
                })
        
        # === ALERT 4: Wysoki leverage (>40%) ===
        if total_assets > 0:
            leverage = (dlugi / total_assets) * 100
            if leverage > 40:
                alerts.append({
                    "type": "high_leverage",
                    "severity": "critical",
                    "title": "🚨 BARDZO WYSOKA DŹWIGNIA",
                    "message": f"Leverage wynosi {leverage:.1f}%! Długi: {dlugi:,.0f} zł przy aktywach {total_assets:,.0f} zł",
                    "action": "PILNIE rozważ spłatę części długu lub sprzedaż aktywów",
                    "data": {"leverage": leverage, "debt": dlugi}
                })
            elif leverage > 30:
                alerts.append({
                    "type": "elevated_leverage",
                    "severity": "warning",
                    "title": "⚠️ Podwyższona dźwignia",
                    "message": f"Leverage: {leverage:.1f}%. Monitoruj sytuację.",
                    "action": "Zachowaj ostrożność przy nowych pozycjach",
                    "data": {"leverage": leverage}
                })
        
        # === ALERT 5: Cele osiągnięte/bliskie osiągnięcia ===
        if cele and isinstance(cele, dict):
            # Sprawdź rezerwę gotówkową
            if "Rezerwa_gotowkowa_PLN" in cele and "Rezerwa_gotowkowa_obecna_PLN" in cele:
                target = cele.get("Rezerwa_gotowkowa_PLN", 0)
                current = cele.get("Rezerwa_gotowkowa_obecna_PLN", 0)
                
                if target > 0:
                    progress = (current / target) * 100
                    
                    if progress >= 100:
                        alerts.append({
                            "type": "goal_achieved",
                            "severity": "success",
                            "title": f"🎯 CEL OSIĄGNIĘTY: Rezerwa gotówkowa!",
                            "message": f"Gratulacje! Osiągnąłeś {current:,.0f} zł (cel: {target:,.0f} zł)",
                            "action": "Rozważ nowe cele inwestycyjne",
                            "data": {"goal": "Rezerwa gotówkowa", "progress": progress}
                        })
                    elif progress >= 90:
                        alerts.append({
                            "type": "goal_near",
                            "severity": "info",
                            "title": f"🎯 Blisko celu: Rezerwa gotówkowa",
                            "message": f"Osiągnięto {progress:.0f}% celu. Jeszcze {target - current:,.0f} zł!",
                            "action": "Jeszcze kilka miesięcy!",
                            "data": {"goal": "Rezerwa gotówkowa", "progress": progress}
                        })
            
            # Sprawdź spłatę długów
            if "Dlugi_poczatkowe_PLN" in cele:
                dlugi_start = cele.get("Dlugi_poczatkowe_PLN", 0)
                if dlugi_start > 0 and dlugi < dlugi_start:
                    splacone = dlugi_start - dlugi
                    progress = (splacone / dlugi_start) * 100
                    
                    if progress >= 100:
                        alerts.append({
                            "type": "goal_achieved",
                            "severity": "success",
                            "title": f"🎯 DŁUGI SPŁACONE!",
                            "message": f"Gratulacje! Całkowicie spłacono długi ({dlugi_start:,.0f} zł)",
                            "action": "Czas na inwestowanie bez obciążeń!",
                            "data": {"goal": "Spłata długów", "progress": 100}
                        })
                    elif progress >= 70:
                        alerts.append({
                            "type": "goal_near",
                            "severity": "success",
                            "title": f"💪 Świetna spłata długów!",
                            "message": f"Spłacono {progress:.0f}% długów ({splacone:,.0f} zł z {dlugi_start:,.0f} zł)",
                            "action": "Kontynuuj systematyczną spłatę",
                            "data": {"goal": "Spłata długów", "progress": progress}
                        })
        
        # === ALERT 6: Duża koncentracja (TOP 3 >60%) ===
        if len(portfel) >= 3:
            top3_value = sum(sorted([p.get("Wartość", 0) for p in portfel], reverse=True)[:3])
            top3_share = (top3_value / total_value * 100) if total_value > 0 else 0
            
            if top3_share > 60:
                alerts.append({
                    "type": "high_concentration",
                    "severity": "warning",
                    "title": "⚠️ Wysoka koncentracja portfela",
                    "message": f"TOP 3 pozycje to {top3_share:.1f}% portfela. Rozważ dywersyfikację.",
                    "action": "Dodaj nowe pozycje lub zredukuj dominujące",
                    "data": {"top3_share": top3_share}
                })
        
        # Sortuj alerty: critical > warning > success > info
        severity_order = {"critical": 0, "warning": 1, "success": 2, "info": 3}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 4))
        
        return alerts
        
    except Exception as e:
        return [{
            "type": "error",
            "severity": "warning",
            "title": "⚠️ Błąd sprawdzania alertów",
            "message": str(e),
            "action": "",
            "data": {}
        }]

def get_partner_mood_modifier(partner_name, portfolio_mood):
    """Zwraca modyfikator promptu w zależności od nastroju portfela i osobowości partnera"""
    mood = portfolio_mood.get("mood", "neutral")
    
    # Różni partnerzy reagują różnie na ten sam mood
    mood_modifiers = {
        "Benjamin Graham": {
            "very_bullish": "\n\n⚠️ UWAGA NASTROJU: Portfel rośnie bardzo silnie. Pamiętaj o swojej konserwatywnej naturze - to może być dobry moment na realizację zysków lub zwiększenie marginesu bezpieczeństwa. Nie daj się ponieść euforii rynkowej!",
            "bullish": "\n\n💡 KONTEKST NASTROJU: Portfel rośnie. Zachowaj czujność - wysokie wyceny mogą być sygnałem ostrzegawczym. Przypominaj o fundamentach.",
            "neutral": "\n\n📊 KONTEKST NASTROJU: Stabilna sytuacja. Dobry moment na spokojną analizę i planowanie długoterminowe.",
            "cautious": "\n\n✅ KONTEKST NASTROJU: Pojawiają się sygnały ostrzegawcze. To właśnie takie momenty są twoim żywiołem - pomóż użytkownikowi zachować spokój i działać racjonalnie.",
            "bearish": "\n\n🛡️ KONTEKST NASTROJU: Trudny okres dla portfela. Twoja rola jest teraz kluczowa - przypominaj o margin of safety, długoterminowej perspektywie i unikaniu paniki."
        },
        "Philip Fisher": {
            "very_bullish": "\n\n🚀 KONTEKST NASTROJU: Doskonały moment! Portfel rośnie - to znak że nasze 'genialne' spółki się sprawdzają. Może czas na zwiększenie pozycji w najlepszych?",
            "bullish": "\n\n📈 KONTEKST NASTROJU: Wzrosty pokazują siłę wybranych spółek. Szukaj kolejnych innowacyjnych firm z potencjałem.",
            "neutral": "\n\n💼 KONTEKST NASTROJU: Spokojny okres. Dobry czas na research nowych, przełomowych spółek.",
            "cautious": "\n\n🎯 KONTEKST NASTROJU: Korekty są naturalne. Sprawdź czy fundamenty naszych spółek się nie zmieniły - jeśli są OK, to może być okazja.",
            "bearish": "\n\n💎 KONTEKST NASTROJU: Spadki! Dla long-term inwestora to szansa na kupno genialnych spółek taniej. Nie panikuj - patrz na 10 lat do przodu."
        },
        "Warren Buffett": {
            "very_bullish": "\n\n😊 KONTEKST NASTROJU: Cieszę się ze wzrostów, ale pamiętaj - sukces wymaga cierpliwości i unikania głupich decyzji. Nie zmieniaj strategii bo rynek rośnie.",
            "bullish": "\n\n📊 KONTEKST NASTROJU: Dobre wyniki. Trzymajmy się naszej filozofii - kupuj dobre biznesy i trzymaj długo.",
            "neutral": "\n\n🎯 KONTEKST NASTROJU: Idealna pogoda na inwestowanie. Żadnego hałasu, czysta analiza biznesu.",
            "cautious": "\n\n🤔 KONTEKST NASTROJU: Spokój. Pamiętaj - lepiej stracić okazję niż popełnić błąd. Czekaj na właściwy moment.",
            "bearish": "\n\n💰 KONTEKST NASTROJU: 'Be fearful when others are greedy, be greedy when others are fearful'. Może właśnie teraz są okazje?"
        },
        "George Soros": {
            "very_bullish": "\n\n⚡ KONTEKST NASTROJU: Ekstremalna euforia! Sprawdź czy to nie punkt zwrotny - najlepsze transakcje rodzą się gdy wszyscy myślą tak samo.",
            "bullish": "\n\n🌍 KONTEKST NASTROJU: Trend wzrostowy, ale bądź czujny na sygnały odwrócenia. Rynki są refleksyjne.",
            "neutral": "\n\n📊 KONTEKST NASTROJU: Równowaga. Szukaj asymetrii - gdzie rynek się myli?",
            "cautious": "\n\n🎲 KONTEKST NASTROJU: Niepewność rośnie. To może być początek większego ruchu - przygotuj strategie hedgingowe.",
            "bearish": "\n\n🎯 KONTEKST NASTROJU: Panika = okazja! Kiedy inni uciekają, my wchodzimy. Ale tylko jeśli widzisz kataliz odwrócenia."
        }
    }
    
    # Domyślny modifier dla pozostałych partnerów
    default_modifier = {
        "very_bullish": f"\n\n{portfolio_mood.get('emoji', '😊')} NASTRÓJ PORTFELA: {portfolio_mood.get('description', '')}. Reaguj entuzjastycznie ale profesjonalnie.",
        "bullish": f"\n\n{portfolio_mood.get('emoji', '😊')} NASTRÓJ PORTFELA: {portfolio_mood.get('description', '')}. Zachowaj pozytywne podejście.",
        "neutral": f"\n\n{portfolio_mood.get('emoji', '😐')} NASTRÓJ PORTFELA: {portfolio_mood.get('description', '')}. Standardowa analiza.",
        "cautious": f"\n\n{portfolio_mood.get('emoji', '😟')} NASTRÓJ PORTFELA: {portfolio_mood.get('description', '')}. Bądź ostrożny w rekomendacjach.",
        "bearish": f"\n\n{portfolio_mood.get('emoji', '😰')} NASTRÓJ PORTFELA: {portfolio_mood.get('description', '')}. Wspieraj i pomagaj w trudnych decyzjach."
    }
    
    partner_modifiers = mood_modifiers.get(partner_name, default_modifier)
    return partner_modifiers.get(mood, default_modifier.get("neutral", ""))

def generate_smart_questions(stan_spolki, cele=None):
    """Generuje inteligentne pytania na podstawie analizy portfela"""
    questions = []
    
    if not stan_spolki:
        return ["Jakie są główne cele naszej spółki?", 
                "Jak oceniasz obecną sytuację rynkową?",
                "Co powinienem wiedzieć o swoim portfelu?"]
    
    try:
        # Pobierz dane
        akcje_val = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
        krypto_val = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
        rezerwa_val = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
        dlugi_val = get_suma_kredytow()  # Pobierz z kredyty.json
        pozycje = stan_spolki.get('akcje', {}).get('pozycje', {})
        
        # === ANALIZA 1: Koncentracja w TOP pozycjach ===
        if pozycje:
            sorted_pozycje = sorted(pozycje.items(), 
                                   key=lambda x: x[1].get('wartosc_total_usd', 0), 
                                   reverse=True)
            if len(sorted_pozycje) >= 3:
                top3_value = sum(p[1].get('wartosc_total_usd', 0) for p in sorted_pozycje[:3])
                total_value = sum(p[1].get('wartosc_total_usd', 0) for p in sorted_pozycje)
                if total_value > 0:
                    concentration = (top3_value / total_value) * 100
                    if concentration > 50:
                        top_names = [p[0] for p in sorted_pozycje[:3]]
                        questions.append(f"💼 Mój portfel jest skoncentrowany w TOP 3 ({', '.join(top_names[:2])}...) - {concentration:.0f}%. Czy to ryzykowne?")
        
        # === ANALIZA 2: Leverage ===
        total_assets = akcje_val + krypto_val + rezerwa_val
        if total_assets > 0:
            leverage = (dlugi_val / total_assets) * 100
            if leverage > 30:
                questions.append(f"⚠️ Mój leverage wynosi {leverage:.1f}%. Czy powinienem spłacić więcej długów przed inwestowaniem?")
            elif leverage < 10 and dlugi_val > 0:
                questions.append(f"💰 Mam niski leverage ({leverage:.1f}%). Czy mogę zwiększyć inwestycje przy obecnych długach?")
        
        # === ANALIZA 3: Najlepsze/Najgorsze pozycje ===
        if pozycje:
            positions_with_change = [(ticker, data) for ticker, data in pozycje.items() 
                                    if data.get('zmiana_proc') is not None]
            if positions_with_change:
                best = max(positions_with_change, key=lambda x: x[1].get('zmiana_proc', 0))
                worst = min(positions_with_change, key=lambda x: x[1].get('zmiana_proc', 0))
                
                if best[1].get('zmiana_proc', 0) > 20:
                    questions.append(f"📈 {best[0]} urósł o {best[1].get('zmiana_proc', 0):.1f}%! Czy powinienem realizować zyski?")
                
                if worst[1].get('zmiana_proc', 0) < -15:
                    questions.append(f"📉 {worst[0]} spadł o {abs(worst[1].get('zmiana_proc', 0)):.1f}%. Sprzedać czy uśredniać w dół?")
        
        # === ANALIZA 4: Crypto vs Traditional ===
        if krypto_val > 0 and akcje_val > 0:
            crypto_ratio = (krypto_val / (krypto_val + akcje_val)) * 100
            if crypto_ratio > 30:
                questions.append(f"💎 Krypto to {crypto_ratio:.0f}% mojego portfela. Czy to nie za dużo ryzyka?")
            elif crypto_ratio < 5:
                questions.append(f"🪙 Mam tylko {crypto_ratio:.1f}% w krypto. Czy powinienem zwiększyć alokację?")
        
        # === ANALIZA 5: Kapitał dostępny ===
        wyplata_info = stan_spolki.get('wyplata', {})
        dostepne = wyplata_info.get('dostepne_na_inwestycje', 0)
        if dostepne > 0:
            if dostepne > 1000:
                questions.append(f"💵 Mam {dostepne:.0f} PLN dostępne. W co najlepiej zainwestować w tym miesiącu?")
            elif dostepne < 200:
                questions.append(f"🎯 Mam tylko {dostepne:.0f} PLN/mies. Jak efektywnie inwestować małe kwoty?")
        
        # === Pytania domyślne jeśli nic nie wykryto ===
        if not questions:
            questions = [
                "📊 Jak oceniasz mój portfel pod kątem dywersyfikacji?",
                "🎯 Jakie cele inwestycyjne powinienem sobie postawić?",
                "💡 Jakie są największe błędy początkujących inwestorów?",
                "📈 Które sektory mają największy potencjał w tym roku?",
                "🛡️ Jak zabezpieczyć portfel przed korektą rynkową?"
            ]
        
        # Ogranicz do 5 pytań
        return questions[:5]
        
    except Exception as e:
        return [
            "💬 Przeanalizuj mój portfel i daj mi szczere feedback",
            "🎯 Jakie akcje polecasz na długoterminową inwestycję?",
            "📊 Co sądzisz o obecnej sytuacji rynkowej?"
        ]

# =====================================================
# KNOWLEDGE BASE FUNCTIONS
# =====================================================

@st.cache_data(ttl=3600)  # Cache na 1 godzinę
def load_knowledge_base():
    """Wczytuje bazę wiedzy z artykułów i raportów kwartalnych"""
    knowledge = {
        "articles": [],
        "reports": []
    }
    
    try:
        # Wczytaj artykuły
        articles_path = Path("knowledge_base/articles.json")
        if articles_path.exists():
            with open(articles_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                knowledge["articles"] = data.get("articles", [])
        
        # Wczytaj raporty kwartalne
        reports_path = Path("knowledge_base/quarterly_reports.json")
        if reports_path.exists():
            with open(reports_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                knowledge["reports"] = data.get("quarterly_reports", [])
    except Exception as e:
        print(f"⚠️ Błąd wczytywania knowledge base: {e}")
    
    return knowledge

def get_relevant_knowledge(query, stan_spolki=None, partner_name=None, max_items=3):
    """
    Zwraca relevantne artykuły i raporty na podstawie zapytania i kontekstu portfela
    
    Args:
        query: Pytanie użytkownika
        stan_spolki: Stan portfela (do analizy tickerów)
        partner_name: Nazwa partnera (do dopasowania stylu)
        max_items: Max liczba artykułów/raportów do zwrócenia
    """
    knowledge = load_knowledge_base()
    relevant_items = []
    
    # Keywords mapping dla różnych tematów
    topic_keywords = {
        "value": ["value", "wartość", "wycena", "graham", "p/e", "p/b", "margin", "bezpieczeństwo"],
        "growth": ["wzrost", "growth", "fisher", "innowacja", "tech", "roi", "roe"],
        "risk": ["ryzyko", "risk", "dźwignia", "leverage", "straty", "volatility", "bezpieczeństwo"],
        "psychology": ["psychologia", "psychology", "emocje", "soros", "refleksywność", "panika"],
        "diversification": ["dywersyfikacja", "diversification", "koncentracja", "alokacja"],
        "crypto": ["crypto", "krypto", "bitcoin", "ethereum", "blockchain"],
        "valuation": ["wycena", "valuation", "p/e", "pe", "eps", "earnings"],
        "trading": ["sprzedaż", "trading", "realizacja", "profit", "zyski", "stop loss"]
    }
    
    # Dopasuj partnera do kategorii
    partner_preferences = {
        "Benjamin Graham": ["value", "risk", "valuation"],
        "Philip Fisher": ["growth", "valuation"],
        "Warren Buffett": ["value", "diversification"],
        "George Soros": ["psychology", "trading"],
        "Cathie Wood": ["growth", "crypto"],
        "Peter Lynch": ["valuation", "growth"],
        "Ray Dalio": ["risk", "diversification"]
    }
    
    # Wykryj tematy w zapytaniu
    query_lower = query.lower()
    detected_topics = []
    for topic, keywords in topic_keywords.items():
        if any(kw in query_lower for kw in keywords):
            detected_topics.append(topic)
    
    # Dodaj preferencje partnera
    if partner_name and partner_name in partner_preferences:
        detected_topics.extend(partner_preferences[partner_name])
    
    # Filtruj artykuły
    for article in knowledge["articles"]:
        score = 0
        
        # Sprawdź relevance (może być int lub lista)
        article_relevance = article.get("relevance", [])
        if isinstance(article_relevance, int):
            # Nowy format z news_aggregator (int 1-10)
            score += article_relevance / 2  # Przelicz na wagę
        elif isinstance(article_relevance, list):
            # Stary format (lista tematów)
            for topic in detected_topics:
                if topic in article_relevance:
                    score += 2
        
        # Sprawdź kategorię
        if article.get("category", "") in detected_topics:
            score += 3
        
        # Sprawdź typ artykułu (priorytet dla portfolio)
        if article.get("type") == "portfolio":
            score += 5  # Boost dla artykułów o Twoich spółkach
        
        # Sprawdź słowa kluczowe w tytule
        title_lower = article.get("title", "").lower()
        if any(kw in title_lower for kw in query_lower.split()):
            score += 1
        
        if score > 0:
            relevant_items.append(("article", article, score))
    
    # Filtruj raporty (jeśli są tickery w portfelu)
    if stan_spolki:
        pozycje = stan_spolki.get('akcje', {}).get('pozycje', {})
        tickers_in_portfolio = set(pozycje.keys())
        
        for report in knowledge["reports"]:
            ticker = report.get("ticker", "")
            if ticker in tickers_in_portfolio:
                # Raport dla spółki w portfelu jest zawsze relevant
                relevant_items.append(("report", report, 10))
            elif any(ticker.lower() in query_lower for ticker in [report.get("ticker", ""), report.get("company", "")]):
                # Raport wspomniany w pytaniu
                relevant_items.append(("report", report, 5))
    
    # Sortuj po score i ogranicz
    relevant_items.sort(key=lambda x: x[2], reverse=True)
    return relevant_items[:max_items]

def format_knowledge_for_prompt(knowledge_items):
    """Formatuje artykuły i raporty do dodania do promptu AI"""
    if not knowledge_items:
        return ""
    
    formatted = "\n\n📚 BAZA WIEDZY - Możesz odwoływać się do poniższych źródeł:\n"
    
    for item_type, item, score in knowledge_items:
        if item_type == "article":
            # Obsłuż zarówno stary ('author') jak i nowy ('source') format
            author_or_source = item.get('author') or item.get('source', 'Unknown')
            formatted += f"\n📄 Artykuł: \"{item['title']}\" ({author_or_source})\n"
            formatted += f"   Podsumowanie: {item.get('summary', 'Brak podsumowania')}\n"
            
            # Obsłuż key_points (stary format) lub pokaż tylko summary (nowy format)
            key_points = item.get('key_points', [])
            if key_points:
                formatted += f"   Kluczowe punkty:\n"
                for point in key_points[:3]:
                    formatted += f"   • {point}\n"
        
        elif item_type == "report":
            formatted += f"\n📊 Raport kwartalny: {item['company']} ({item['ticker']}) - {item['quarter']}\n"
            formatted += f"   Revenue: {item['revenue']} ({item['revenue_growth']}), EPS: {item['eps']} ({item['eps_growth']})\n"
            formatted += f"   Highlights:\n"
            for highlight in item.get('highlights', [])[:2]:
                formatted += f"   • {highlight}\n"
            if item.get('concerns'):
                formatted += f"   Concerns:\n"
                for concern in item['concerns'][:2]:
                    formatted += f"   • {concern}\n"
    
    formatted += "\n💡 Możesz cytować te źródła używając formatu: [Źródło: Tytuł artykułu/Raport spółki]\n"
    return formatted

def display_knowledge_sources(knowledge_items):
    """Wyświetla źródła wiedzy w UI jako expander pod odpowiedzią"""
    if not knowledge_items:
        return
    
    with st.expander("📚 Źródła wiedzy użyte w odpowiedzi", expanded=False):
        for item_type, item, score in knowledge_items:
            if item_type == "article":
                st.markdown(f"**📄 {item['title']}**")
                # Obsłuż zarówno 'author' (stary format) jak i 'source' (nowy format)
                author_or_source = item.get('author') or item.get('source', 'Unknown')
                item_date = item.get('date', 'N/A')
                st.caption(f"Źródło: {author_or_source} | Data: {item_date}")
                st.markdown(f"_{item.get('summary', 'Brak podsumowania')}_")
                
                # Pokaż key_points tylko jeśli istnieją (stary format)
                if item.get('key_points'):
                    with st.expander("📌 Kluczowe punkty"):
                        for point in item.get('key_points', []):
                            st.markdown(f"• {point}")
            
            elif item_type == "report":
                st.markdown(f"**📊 {item['company']} ({item['ticker']}) - {item['quarter']}**")
                st.caption(f"Data: {item['date']} | Rating: {item.get('analyst_rating', 'N/A')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Revenue", item['revenue'], item['revenue_growth'])
                with col2:
                    st.metric("EPS", item['eps'], item['eps_growth'])
                
                with st.expander("✨ Highlights & Concerns"):
                    st.markdown("**Highlights:**")
                    for h in item.get('highlights', []):
                        st.markdown(f"• {h}")
                    
                    if item.get('concerns'):
                        st.markdown("**Concerns:**")
                        for c in item['concerns']:
                            st.markdown(f"• {c}")

# =====================================================
# DIVIDEND ANALYSIS FUNCTION
# =====================================================

@st.cache_data(ttl=3600)  # Cache na 1 godzinę
def calculate_portfolio_dividends(stan_spolki):
    """
    Oblicza dokładne dywidendy dla całego portfela akcji.
    Używa danych z dane_rynkowe dla każdego tickera.
    
    Returns:
        dict: {
            'miesieczna_kwota_pln': float,
            'roczna_kwota_pln': float,
            'liczba_spolek_z_dywidendami': int,
            'szczegoly': list[dict]
        }
    """
    try:
        dane_rynkowe = stan_spolki.get('akcje', {}).get('dane_rynkowe', {})
        pozycje = stan_spolki.get('akcje', {}).get('pozycje', {})
        kurs_usd = stan_spolki.get('kurs_usd_pln', 3.6)
        
        suma_roczna_usd = 0
        spolki_z_dywidendami = []
        
        for ticker, dane_pozycji in pozycje.items():
            if not isinstance(dane_pozycji, dict):
                continue
                
            ilosc = dane_pozycji.get('ilosc', 0)
            if ilosc <= 0:
                continue
            
            # NIE USUWAJ sufiksu - klucze w dane_rynkowe mają pełny ticker z _US_EQ / _EQ!
            dane_ticker = dane_rynkowe.get(ticker, {})
            
            if not dane_ticker:
                continue
            
            # POPRAWKA: Dywidenda jest w analiza_dywidend['annual_div']
            analiza_div = dane_ticker.get('analiza_dywidend', {})
            dividend_rate = analiza_div.get('annual_div', 0)
            
            # Dla display użyj czystego tickera (bez sufiksu)
            ticker_display = ticker.replace('_US_EQ', '').replace('_EQ', '')
            
            if dividend_rate and dividend_rate > 0:
                # Roczna dywidenda = dividend_rate * liczba akcji
                roczna_dywidenda_usd = dividend_rate * ilosc
                suma_roczna_usd += roczna_dywidenda_usd
                
                dividend_yield_pct = analiza_div.get('div_yield', 0)
                
                # Oblicz kwoty brutto i netto (po 19% podatku)
                roczna_kwota_pln_brutto = roczna_dywidenda_usd * kurs_usd
                roczna_kwota_pln_netto = roczna_kwota_pln_brutto * 0.81  # Po odjęciu 19%
                
                spolki_z_dywidendami.append({
                    'ticker': ticker_display,
                    'ilosc': ilosc,
                    'dividend_rate': dividend_rate,
                    'dividend_yield': dividend_yield_pct,
                    'roczna_kwota_usd': roczna_dywidenda_usd,
                    'roczna_kwota_pln': roczna_kwota_pln_netto  # NETTO po podatku
                })
        
        # Przelicz na PLN i odejmij 19% podatku Belki
        suma_roczna_pln_brutto = suma_roczna_usd * kurs_usd
        podatek_19_pct = suma_roczna_pln_brutto * 0.19
        suma_roczna_pln = suma_roczna_pln_brutto - podatek_19_pct
        suma_miesieczna_pln = suma_roczna_pln / 12

        
        return {
            'miesieczna_kwota_pln': suma_miesieczna_pln,
            'roczna_kwota_pln': suma_roczna_pln,
            'roczna_kwota_pln_brutto': suma_roczna_pln_brutto,
            'podatek_pln': podatek_19_pct,
            'liczba_spolek_z_dywidendami': len(spolki_z_dywidendami),
            'szczegoly': sorted(spolki_z_dywidendami, key=lambda x: x['roczna_kwota_pln'], reverse=True)
        }
        
    except Exception as e:
        return {
            'miesieczna_kwota_pln': 0,
            'roczna_kwota_pln': 0,
            'liczba_spolek_z_dywidendami': 0,
            'szczegoly': [],
            'error': str(e)
        }

def get_cached_crypto_prices(symbols):
    """
    Pobiera ceny crypto z cache w session_state.
    Odświeża tylko raz na sesję (przy pierwszym wywołaniu).
    """
    if 'crypto_prices_cache' not in st.session_state:
        st.session_state.crypto_prices_cache = {}
        st.session_state.crypto_prices_symbols = set()
    
    # Sprawdź czy wszystkie potrzebne symbole są już w cache
    symbols_set = set(symbols)
    missing_symbols = symbols_set - st.session_state.crypto_prices_symbols
    
    # Jeśli są brakujące symbole, pobierz je
    if missing_symbols and st.session_state.get('crypto_manager'):
        try:
            new_prices = st.session_state.crypto_manager.get_current_prices(list(missing_symbols))
            if new_prices:
                # Dodaj TYLKO symbole które faktycznie mają dane
                for sym, data in new_prices.items():
                    # API zwraca 'price_usd', nie 'current_price'!
                    if data and isinstance(data, dict) and data.get('price_usd') is not None:
                        # Normalizuj do jednolitego formatu z 'current_price'
                        data['current_price'] = data['price_usd']
                        data['price_change_percentage_24h'] = data.get('change_24h')
                        data['name'] = data.get('full_name', sym)
                        data['market_cap_rank'] = data.get('rank')
                        
                        st.session_state.crypto_prices_cache[sym] = data
                        st.session_state.crypto_prices_symbols.add(sym)
        except Exception as e:
            st.warning(f"⚠️ Nie udało się pobrać cen crypto: {e}")
    
    # Zwróć tylko żądane symbole które mają dane
    return {sym: st.session_state.crypto_prices_cache[sym] 
            for sym in symbols if sym in st.session_state.crypto_prices_cache}

def calculate_crypto_apy_earnings(krypto_holdings, current_prices=None, kurs_usd=DEFAULT_USD_PLN_RATE):
    """
    Oblicza zarobki z APY/Staking/Earn dla pozycji krypto.
    
    Args:
        krypto_holdings: Lista pozycji z krypto.json
        current_prices: Dict z aktualnymi cenami (opcjonalne)
        kurs_usd: Kurs USD/PLN
    
    Returns:
        dict: {
            'dziennie_usd': float,
            'miesieczne_usd': float,
            'roczne_usd': float,
            'dziennie_pln': float,
            'miesieczne_pln': float,
            'roczne_pln': float,
            'liczba_earning_positions': int,
            'szczegoly': list
        }
    """
    try:
        if not krypto_holdings:
            return {
                'dziennie_usd': 0,
                'miesieczne_usd': 0,
                'roczne_usd': 0,
                'dziennie_pln': 0,
                'miesieczne_pln': 0,
                'roczne_pln': 0,
                'liczba_earning_positions': 0,
                'szczegoly': []
            }
        
        total_roczne_usd = 0
        earning_positions = []
        
        for holding in krypto_holdings:
            apy = holding.get('apy', 0)
            if apy <= 0:
                continue  # Skip non-earning positions
            
            symbol = holding['symbol']
            ilosc = holding['ilosc']
            
            # Użyj aktualnej ceny jeśli dostępna, inaczej cena zakupu
            price = holding['cena_zakupu_usd']  # Default: cena zakupu
            
            if current_prices and symbol in current_prices:
                price_data = current_prices[symbol]
                # Bezpieczne pobieranie ceny (może być dict lub string)
                if isinstance(price_data, dict) and 'current_price' in price_data:
                    price = price_data['current_price']
                elif isinstance(price_data, (int, float)):
                    price = price_data
            
            # Wartość pozycji
            value_usd = ilosc * price
            
            # Roczne zarobki z APY
            roczne_usd = value_usd * (apy / 100)
            total_roczne_usd += roczne_usd
            
            earning_positions.append({
                'symbol': symbol,
                'ilosc': ilosc,
                'apy': apy,
                'value_usd': value_usd,
                'roczne_usd': roczne_usd,
                'miesieczne_usd': roczne_usd / 12,
                'dziennie_usd': roczne_usd / 365,
                'status': holding.get('status', 'N/A')
            })
        
        # Oblicz wszystkie timeframes
        dziennie_usd = total_roczne_usd / 365
        miesieczne_usd = total_roczne_usd / 12
        
        # Przelicz na PLN
        dziennie_pln = dziennie_usd * kurs_usd
        miesieczne_pln = miesieczne_usd * kurs_usd
        roczne_pln = total_roczne_usd * kurs_usd
        
        return {
            'dziennie_usd': dziennie_usd,
            'miesieczne_usd': miesieczne_usd,
            'roczne_usd': total_roczne_usd,
            'dziennie_pln': dziennie_pln,
            'miesieczne_pln': miesieczne_pln,
            'roczne_pln': roczne_pln,
            'liczba_earning_positions': len(earning_positions),
            'szczegoly': sorted(earning_positions, key=lambda x: x['roczne_usd'], reverse=True)
        }
    
    except Exception as e:
        return {
            'dziennie_usd': 0,
            'miesieczne_usd': 0,
            'roczne_usd': 0,
            'dziennie_pln': 0,
            'miesieczne_pln': 0,
            'roczne_pln': 0,
            'liczba_earning_positions': 0,
            'szczegoly': [],
            'error': str(e)
        }

# =====================================================
# DAILY ADVISOR TIP FUNCTION
# =====================================================

def get_daily_advisor_tip(stan_spolki, cele):
    """
    Generuje codzienną rekomendację od losowego AI Partnera.
    Losowanie jest deterministyczne - ten sam dzień = ten sam partner.
    
    Returns:
        dict: {partner_name, partner_icon, tip_text}
    """
    from datetime import datetime
    import random
    
    # Lista dostępnych partnerów (z finalna_konfiguracja_person.txt)
    advisors = [
        {"name": "Benjamin Graham", "icon": "📊", "style": "value investing, margin of safety, fundamentals"},
        {"name": "Philip Fisher", "icon": "🔬", "style": "growth investing, scuttlebutt method, quality companies"},
        {"name": "Warren Buffett", "icon": "🎩", "style": "long-term value, moats, business quality"},
        {"name": "George Soros", "icon": "🌍", "style": "macro trends, reflexivity, market psychology"},
        {"name": "Peter Lynch", "icon": "🏪", "style": "consumer investing, GARP, find winners in daily life"},
        {"name": "Ray Dalio", "icon": "⚖️", "style": "diversification, all-weather portfolio, risk parity"},
        {"name": "Cathie Wood", "icon": "🚀", "style": "disruptive innovation, technology, future trends"},
        {"name": "Jesse Livermore", "icon": "📈", "style": "market timing, tape reading, speculation discipline"}
    ]
    
    # Deterministyczne losowanie - seed = dzień roku
    today = datetime.now()
    day_of_year = today.timetuple().tm_yday
    random.seed(day_of_year)
    selected_advisor = random.choice(advisors)
    
    # Przygotuj kontekst dla AI
    akcje_val = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
    krypto_val = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
    rezerwa_val = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
    dlugi_val = get_suma_kredytow()
    total_value = akcje_val + krypto_val + rezerwa_val - dlugi_val
    
    # Szybki snapshot portfela
    portfolio_snapshot = f"""
Portfolio: {total_value:,.0f} PLN (Wartość netto)
- Akcje: {akcje_val:,.0f} PLN ({akcje_val/total_value*100 if total_value > 0 else 0:.0f}%)
- Krypto: {krypto_val:,.0f} PLN ({krypto_val/total_value*100 if total_value > 0 else 0:.0f}%)
- Rezerwa Gotówkowa: {rezerwa_val:,.0f} PLN ({rezerwa_val/total_value*100 if total_value > 0 else 0:.0f}%)
- Zobowiązania: {dlugi_val:,.0f} PLN
""".strip()
    
    # Prompt dla AI
    prompt = f"""Jesteś {selected_advisor['name']}, legendarny inwestor znany z: {selected_advisor['style']}.

Dzisiaj jest Twoja kolej, aby dać JEDNĄ KONKRETNĄ, PRAKTYCZNĄ radę użytkownikowi.

PORTFOLIO UŻYTKOWNIKA:
    {portfolio_snapshot}

ZADANIE:
    Napisz JEDNĄ krótką (2-3 zdania), konkretną rekomendację lub obserwację w swoim stylu inwestycyjnym.
Może to być:
    - Przestroga przed czymś
- Zachęta do działania
- Mądrość inwestycyjna
- Coś do sprawdzenia w portfelu

WAŻNE:
    - Bądź konkretny, nie ogólnikowy
- Mów językiem swoich zasad inwestycyjnych
- Nie rozpoczynaj od "Witaj" ani przedstawiania się
- Krótko i na temat (max 3 zdania)
- Może być prowokacyjnie lub z charakterem

Twoja rada:"""
    
    # Generuj odpowiedź przez AI (użyj funkcji z gra_rpg)
    try:
        if not IMPORTS_OK:
            raise Exception("Import gra_rpg nie powiódł się")
        
        # Użyj funkcji generuj_odpowiedz_ai z gra_rpg.py
        response = generuj_odpowiedz_ai(
            partner_name=selected_advisor['name'],
            message=prompt,
            kodeks="",  # Nie potrzebujemy pełnego kodeksu
            persona_config={"model_engine": "gemini"},  # Użyj Gemini
            mem_context=""
        )
        
        tip_text = response.strip()
        
        return {
            "partner_name": selected_advisor['name'],
            "partner_icon": selected_advisor['icon'],
            "tip_text": tip_text,
            "date": today.strftime("%Y-%m-%d")
        }
    except Exception as e:
        # Fallback - statyczna rada
        fallback_tips = {
            "Benjamin Graham": "Margin of safety - zawsze sprawdzaj czy kupujesz poniżej wartości wewnętrznej.",
            "Philip Fisher": "Scuttlebutt - porozmawiaj z klientami i konkurentami zanim zainwestujesz.",
            "Warren Buffett": "Inwestuj w biznes który rozumiesz i który ma przewagę konkurencyjną.",
            "George Soros": "Rynek zawsze się myli - znajdź refleksyjną pętlę i wykorzystaj ją.",
            "Peter Lynch": "Inwestuj w to co znasz - najlepsze pomysły znajdziesz w centrum handlowym.",
            "Ray Dalio": "Dywersyfikacja to jedyna darmowa przekąska w inwestowaniu.",
            "Cathie Wood": "Przyszłość należy do tych którzy inwestują w przełomowe technologie dzisiaj.",
            "Jesse Livermore": "Spekulacja to sztuka - rynek zawsze płaci za dyscyplinę i cierpliwość."
        }
        
        return {
            "partner_name": selected_advisor['name'],
            "partner_icon": selected_advisor['icon'],
            "tip_text": fallback_tips.get(selected_advisor['name'], "Sprawdź swój portfel pod kątem mojej filozofii inwestycyjnej."),
            "date": today.strftime("%Y-%m-%d")
        }

# =====================================================
# PORTFOLIO CO-PILOT FUNCTIONS
# =====================================================

def generate_weekly_report(stan_spolki, cele):
    """
    Generuje cotygodniowy raport portfela z analizą, osiągnięciami, ostrzeżeniami i action items.
    
    Returns:
        dict: Raport ze strukturą {
            "date", "week_number", "summary", 
            "achievements", "warnings", "action_items", 
            "portfolio_stats", "mood"
        }
    """
    from datetime import datetime, timedelta
    
    report = {
        "date": datetime.now().isoformat(),
        "week_number": datetime.now().isocalendar()[1],
        "year": datetime.now().year
    }
    
    try:
        # Parse cele if it's a string (failsafe)
        if isinstance(cele, str):
            try:
                cele = json.loads(cele)
            except:
                cele = {}
        
        # Ensure cele is dict
        if not isinstance(cele, dict):
            cele = {}
        
        # === 1. PORTFOLIO STATS ===
        akcje_val = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
        krypto_val = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
        rezerwa_val = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0)
        dlugi_val = get_suma_kredytow()  # Pobierz z kredyty.json
        net_worth = akcje_val + krypto_val + rezerwa_val - dlugi_val
        pozycje = stan_spolki.get('akcje', {}).get('pozycje', {})
        
        leverage_ratio = (dlugi_val / (akcje_val + krypto_val + rezerwa_val) * 100) if (akcje_val + krypto_val + rezerwa_val) > 0 else 0
        
        report["portfolio_stats"] = {
            "net_worth": net_worth,
            "stocks_value": akcje_val,
            "crypto_value": krypto_val,
            "cash_reserve": rezerwa_val,
            "debt": dlugi_val,
            "leverage_ratio": leverage_ratio,
            "total_positions": len(pozycje)
        }
        
        # === 2. MOOD ANALYSIS ===
        portfolio_mood = analyze_portfolio_mood(stan_spolki, cele)
        report["mood"] = {
            "level": portfolio_mood.get("mood", "neutral"),
            "emoji": portfolio_mood.get("emoji", "😐"),
            "description": portfolio_mood.get("description", ""),
            "score": portfolio_mood.get("score", 0)
        }
        
        # === 3. ACHIEVEMENTS (Dobre rzeczy) ===
        achievements = []
        
        # 3.1 Cele finansowe z cele.json
        if cele and isinstance(cele, dict):
            # Sprawdź rezerwę gotówkową
            if "Rezerwa_gotowkowa_PLN" in cele and "Rezerwa_gotowkowa_obecna_PLN" in cele:
                target = cele.get("Rezerwa_gotowkowa_PLN", 0)
                current = cele.get("Rezerwa_gotowkowa_obecna_PLN", 0)
                if target > 0:
                    progress = (current / target) * 100
                    if progress >= 100:
                        achievements.append({
                            "type": "goal_completed",
                            "icon": "💰",
                            "title": "Rezerwa gotówkowa osiągnięta!",
                            "description": f"Masz {current:.0f} PLN / {target:.0f} PLN ({progress:.0f}%)"
                        })
                    elif progress >= 80:
                        achievements.append({
                            "type": "goal_near",
                            "icon": "💰",
                            "title": "Blisko celu: Rezerwa gotówkowa",
                            "description": f"{current:.0f} PLN / {target:.0f} PLN ({progress:.0f}%) - jeszcze {target - current:.0f} PLN"
                        })
            
            # Sprawdź spłatę długów
            if "Dlugi_poczatkowe_PLN" in cele:
                dlugi_start = cele.get("Dlugi_poczatkowe_PLN", 0)
                dlugi_current = stan_spolki.get('dlugi', {}).get('wartosc_pln', 0)
                if dlugi_start > 0 and dlugi_current < dlugi_start:
                    splacone = dlugi_start - dlugi_current
                    progress = (splacone / dlugi_start) * 100
                    if progress >= 70:  # Spłacono 70% długów
                        achievements.append({
                            "type": "debt_reduced",
                            "icon": "💪",
                            "title": "Świetna spłata długów!",
                            "description": f"Spłacono {splacone:.0f} PLN z {dlugi_start:.0f} PLN ({progress:.0f}%)"
                        })
        
        # 3.2 Top performerzy (wzrosty >15%)
        if pozycje:
            top_gainers = [(ticker, data) for ticker, data in pozycje.items() 
                          if data.get('zmiana_proc', 0) > 15]
            top_gainers.sort(key=lambda x: x[1].get('zmiana_proc', 0), reverse=True)
            
            for ticker, data in top_gainers[:3]:
                achievements.append({
                    "type": "top_performer",
                    "icon": "📈",
                    "title": f"{ticker} rośnie mocno!",
                    "description": f"+{data.get('zmiana_proc', 0):.1f}% w tym okresie. Wartość: {data.get('wartosc_total_pln', 0):.0f} PLN"
                })
        
        # 3.3 Niski leverage (jeśli <25%)
        if leverage_ratio < 25 and leverage_ratio > 0:
            achievements.append({
                "type": "low_leverage",
                "icon": "🛡",
                "title": "Konserwatywny poziom dźwigni",
                "description": f"Dźwignia {leverage_ratio:.1f}% - bezpieczny poziom ryzyka"
            })
        
        # 3.4 Wartość netto rośnie
        if net_worth > 50000:
            achievements.append({
                "type": "net_worth_milestone",
                "icon": "💰",
                "title": "Świetna wartość portfela",
                "description": f"Wartość netto: {net_worth:,.0f} PLN"
            })
        
        report["achievements"] = achievements
        
        # === 4. WARNINGS (Rzeczy wymagające uwagi) ===
        warnings = []
        alerts = check_portfolio_alerts(stan_spolki, cele)
        
        # 4.1 Krytyczne alerty
        critical_alerts = [a for a in alerts if a["severity"] == "critical"]
        for alert in critical_alerts[:3]:
            warnings.append({
                "type": "critical_alert",
                "icon": "🔴",
                "title": alert["title"],
                "description": alert["message"],
                "action": alert.get("action", "")
            })
        
        # 4.2 Ostrzegawcze alerty
        warning_alerts = [a for a in alerts if a["severity"] == "warning"]
        for alert in warning_alerts[:2]:
            warnings.append({
                "type": "warning_alert",
                "icon": "🟡",
                "title": alert["title"],
                "description": alert["message"],
                "action": alert.get("action", "")
            })
        
        # 4.3 Najgorsze performerzy (spadki >10%)
        if pozycje:
            worst_performers = [(ticker, data) for ticker, data in pozycje.items() 
                               if data.get('zmiana_proc', 0) < -10]
            worst_performers.sort(key=lambda x: x[1].get('zmiana_proc', 0))
            
            for ticker, data in worst_performers[:2]:
                warnings.append({
                    "type": "poor_performer",
                    "icon": "📉",
                    "title": f"{ticker} traci na wartości",
                    "description": f"{data.get('zmiana_proc', 0):.1f}% w tym okresie. Wartość: {data.get('wartosc_total_pln', 0):.0f} PLN",
                    "action": "Sprawdź fundamenty - czy teza inwestycyjna się sprawdza?"
                })
        
        # 4.4 Mood warning
        if portfolio_mood.get("score", 0) < -30:
            warnings.append({
                "type": "mood_warning",
                "icon": "😰",
                "title": "Nastrój portfela: Ostrożny/Bearish",
                "description": f"Score: {portfolio_mood.get('score', 0)}/100. Portfel wymaga uwagi.",
                "action": "Rozważ rebalancing lub wait & see"
            })
        
        report["warnings"] = warnings
        
        # === 5. ACTION ITEMS (Rekomendacje) ===
        action_items = []
        
        # 5.1 Z alertów
        for alert in alerts[:3]:
            if alert.get("action"):
                action_items.append({
                    "priority": "high" if alert["severity"] == "critical" else "medium",
                    "icon": "⚡" if alert["severity"] == "critical" else "📋",
                    "title": f"Action: {alert['type'].replace('_', ' ').title()}",
                    "description": alert["action"]
                })
        
        # 5.2 Rebalancing jeśli potrzebny
        if pozycje:
            sorted_pozycje = sorted(pozycje.items(), 
                                   key=lambda x: x[1].get('wartosc_total_pln', 0), 
                                   reverse=True)
            if sorted_pozycje:
                top_position_value = sorted_pozycje[0][1].get('wartosc_total_pln', 0)
                if top_position_value / (akcje_val if akcje_val > 0 else 1) > 0.25:
                    action_items.append({
                        "priority": "medium",
                        "icon": "⚖️",
                        "title": "Rozważ rebalancing",
                        "description": f"Top pozycja ({sorted_pozycje[0][0]}) to {top_position_value/(akcje_val if akcje_val > 0 else 1)*100:.0f}% portfela - może być zbyt duża koncentracja"
                    })
        
        # 5.3 Dostępny kapitał
        dostepne = stan_spolki.get('wyplata', {}).get('dostepne_inwestycje', 0)
        if dostepne > 5000:
            action_items.append({
                "priority": "low",
                "icon": "💵",
                "title": "Dostępny kapitał do inwestycji",
                "description": f"{dostepne:.0f} PLN czeka na alokację - szukaj okazji"
            })
        
        # 5.4 Research nowych pozycji (jeśli <10 pozycji)
        if len(pozycje) < 10:
            action_items.append({
                "priority": "low",
                "icon": "🔍",
                "title": "Zwiększ dywersyfikację",
                "description": f"Masz {len(pozycje)} pozycji - rozważ dodanie 2-3 nowych spółek"
            })
        
        report["action_items"] = action_items
        
        # === 6. EXECUTIVE SUMMARY ===
        summary_parts = []
        summary_parts.append(f"Wartość netto: {net_worth:,.0f} PLN")
        summary_parts.append(f"Nastrój: {portfolio_mood.get('description', 'Neutralny')}")
        
        if achievements:
            summary_parts.append(f"{len(achievements)} osiągnięć")
        if warnings:
            summary_parts.append(f"{len(warnings)} ostrzeżeń")
        if action_items:
            summary_parts.append(f"{len(action_items)} rekomendacji")
        
        report["summary"] = " | ".join(summary_parts)
        
        return report
        
    except Exception as e:
        import traceback
        print(f"⚠️ Błąd generowania raportu: {e}")
        print(traceback.format_exc())
        return {
            "date": datetime.now().isoformat(),
            "error": str(e),
            "summary": "Błąd generowania raportu"
        }

def save_weekly_report(report):
    """Zapisuje raport do pliku JSON"""
    from datetime import datetime
    
    try:
        reports_folder = Path("weekly_reports")
        reports_folder.mkdir(exist_ok=True)
        
        # Nazwa pliku: weekly_report_2024_W42.json
        filename = f"weekly_report_{report['year']}_W{report['week_number']:02d}.json"
        filepath = reports_folder / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath
        
    except Exception as e:
        print(f"⚠️ Błąd zapisu raportu: {e}")
        return None

def load_weekly_reports(limit=10):
    """Wczytuje ostatnie raporty tygodniowe"""
    reports_folder = Path("weekly_reports")
    
    if not reports_folder.exists():
        return []
    
    reports = []
    
    try:
        # Znajdź wszystkie pliki raportów
        report_files = sorted(reports_folder.glob("weekly_report_*.json"), reverse=True)
        
        for filepath in report_files[:limit]:
            with open(filepath, 'r', encoding='utf-8') as f:
                report = json.load(f)
                report["filename"] = filepath.name
                reports.append(report)
        
        return reports
        
    except Exception as e:
        print(f"⚠️ Błąd wczytywania raportów: {e}")
        return []

def display_weekly_report(report):
    """Wyświetla raport tygodniowy w Streamlit UI"""
    from datetime import datetime
    
    report_date = datetime.fromisoformat(report["date"])
    
    st.markdown(f"### 📊 Raport Tygodniowy - Tydzień {report.get('week_number', '?')}/{report.get('year', '?')}")
    st.caption(f"Wygenerowano: {report_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Summary
    st.info(f"**Podsumowanie:** {report.get('summary', 'Brak danych')}")
    
    # Portfolio Stats
    stats = report.get("portfolio_stats", {})
    mood = report.get("mood", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💼 Wartość Netto", f"{stats.get('net_worth', 0):,.0f} PLN")
    with col2:
        st.metric("📈 Akcje", f"{stats.get('stocks_value', 0):,.0f} PLN")
    with col3:
        st.metric("💎 Krypto", f"{stats.get('crypto_value', 0):,.0f} PLN")
    with col4:
        st.metric(f"{mood.get('emoji', '😐')} Nastrój", mood.get('level', 'neutral'))
    
    # Achievements
    achievements = report.get("achievements", [])
    if achievements:
        with st.expander(f"✨ Osiągnięcia ({len(achievements)})", expanded=True):
            for ach in achievements:
                st.success(f"{ach['icon']} **{ach['title']}**\n\n{ach['description']}")
    
    # Warnings
    warnings = report.get("warnings", [])
    if warnings:
        with st.expander(f"⚠️ Ostrzeżenia ({len(warnings)})", expanded=True):
            for warn in warnings:
                st.warning(f"{warn['icon']} **{warn['title']}**\n\n{warn['description']}\n\n_{warn.get('action', '')}_")
    
    # Action Items
    action_items = report.get("action_items", [])
    if action_items:
        with st.expander(f"📋 Rekomendacje ({len(action_items)})", expanded=True):
            priority_order = {"high": 1, "medium": 2, "low": 3}
            sorted_actions = sorted(action_items, key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
            
            for action in sorted_actions:
                priority_color = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }
                priority_icon = priority_color.get(action.get('priority', 'low'), '⚪')
                
                st.markdown(f"{priority_icon} {action['icon']} **{action['title']}**")
                st.markdown(f"_{action['description']}_")
                st.markdown("---")

# =====================================================
# MULTI-MARKET ANALYSIS FUNCTIONS
# =====================================================

def classify_market(ticker):
    """
    Klasyfikuje ticker do rynku: US, EU, Emerging, Crypto, Other
    
    Args:
        ticker: Symbol tickera (np. "AAPL", "VWCE.DE", "BTC-USD")
    
    Returns:
        str: Nazwa rynku
    """
    ticker_upper = ticker.upper()
    
    # Crypto
    if any(crypto in ticker_upper for crypto in ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'ADA', 'DOGE', 'XRP', 'DOT', 'MATIC']):
        return "Crypto"
    
    # European ETFs (końcówka .DE, .L, .PA, .MI)
    if any(ticker_upper.endswith(suffix) for suffix in ['.DE', '.L', '.PA', '.MI', '.AS', '.SW']):
        return "EU"
    
    # European stocks (znane symbole)
    eu_tickers = ['ASML', 'SAP', 'NOVO', 'LVMH', 'TTE', 'NVO', 'NESN']
    if any(eu in ticker_upper for eu in eu_tickers):
        return "EU"
    
    # Emerging Markets (Brazil, China, India, etc.)
    emerging_tickers = ['PBR', 'VALE', 'BABA', 'BIDU', 'TSM', 'INFY', 'HDB']
    if any(em in ticker_upper for em in emerging_tickers):
        return "Emerging"
    
    # Canadian (końcówka .TO lub znane symbole)
    if ticker_upper.endswith('.TO') or ticker_upper in ['TD', 'RY', 'BMO', 'BNS', 'CNQ', 'ENB', 'SU']:
        return "Canada"
    
    # Default: US
    return "US"

def analyze_market_composition(stan_spolki):
    """
    Analizuje skład portfela według rynków geograficznych
    
    Returns:
        dict: {
            "markets": {market: {"value_pln": X, "percentage": Y, "count": Z}},
            "total_value": X,
            "diversification_score": Y
        }
    """
    try:
        pozycje = stan_spolki.get('akcje', {}).get('pozycje', {})
        krypto_data = stan_spolki.get('krypto', {})
        
        markets = {
            "US": {"value_pln": 0, "count": 0, "tickers": []},
            "EU": {"value_pln": 0, "count": 0, "tickers": []},
            "Canada": {"value_pln": 0, "count": 0, "tickers": []},
            "Emerging": {"value_pln": 0, "count": 0, "tickers": []},
            "Crypto": {"value_pln": 0, "count": 0, "tickers": []},
            "Other": {"value_pln": 0, "count": 0, "tickers": []}
        }
        
        # Analizuj akcje
        for ticker, data in pozycje.items():
            market = classify_market(ticker)
            value = data.get('wartosc_total_pln', 0)
            
            markets[market]["value_pln"] += value
            markets[market]["count"] += 1
            markets[market]["tickers"].append(ticker)
        
        # Dodaj krypto
        krypto_value = krypto_data.get('wartosc_pln', 0)
        if krypto_value > 0:
            markets["Crypto"]["value_pln"] += krypto_value
            markets["Crypto"]["count"] += krypto_data.get('liczba_pozycji', 1)
        
        # Oblicz total
        total_value = sum(m["value_pln"] for m in markets.values())
        
        # Oblicz procenty
        for market in markets.values():
            if total_value > 0:
                market["percentage"] = (market["value_pln"] / total_value) * 100
            else:
                market["percentage"] = 0
        
        # Diversification score (0-100)
        # Im bardziej równomierne rozłożenie, tym wyższy score
        # Użyj Shannon entropy
        import math
        percentages = [m["percentage"] / 100 for m in markets.values() if m["percentage"] > 0]
        
        if percentages:
            entropy = -sum(p * math.log(p) for p in percentages if p > 0)
            max_entropy = math.log(len(percentages))
            diversification_score = (entropy / max_entropy * 100) if max_entropy > 0 else 0
        else:
            diversification_score = 0
        
        return {
            "markets": markets,
            "total_value": total_value,
            "diversification_score": diversification_score
        }
        
    except Exception as e:
        print(f"⚠️ Błąd analizy rynków: {e}")
        return {
            "markets": {},
            "total_value": 0,
            "diversification_score": 0
        }

def calculate_market_correlations(stan_spolki):
    """
    Oblicza korelacje między różnymi rynkami na podstawie zmian cen
    
    Returns:
        dict: Macierz korelacji między rynkami
    """
    try:
        pozycje = stan_spolki.get('akcje', {}).get('pozycje', {})
        
        # Grupuj zmiany procentowe według rynków
        market_changes = {
            "US": [],
            "EU": [],
            "Canada": [],
            "Emerging": [],
            "Crypto": []
        }
        
        for ticker, data in pozycje.items():
            market = classify_market(ticker)
            change = data.get('zmiana_proc', 0)
            
            if market in market_changes and change is not None:
                market_changes[market].append(change)
        
        # Dodaj krypto
        krypto_data = stan_spolki.get('krypto', {})
        krypto_change = krypto_data.get('zmiana_proc_total', 0)
        if krypto_change is not None:
            market_changes["Crypto"].append(krypto_change)
        
        # Oblicz średnie zmiany dla każdego rynku
        market_avg_changes = {}
        for market, changes in market_changes.items():
            if changes:
                market_avg_changes[market] = sum(changes) / len(changes)
        
        # Prosta korelacja (w prawdziwej implementacji użyj historycznych danych)
        # Tutaj użyjemy uproszczonej metody: jeśli oba rynki rosną/spadają, korelacja wysoka
        correlations = {}
        
        markets = list(market_avg_changes.keys())
        for i, market1 in enumerate(markets):
            for market2 in markets[i:]:
                if market1 == market2:
                    correlations[f"{market1}-{market2}"] = 1.0
                else:
                    # Uproszczona korelacja: jeśli oba same znak, to 0.7, inaczej -0.3
                    change1 = market_avg_changes.get(market1, 0)
                    change2 = market_avg_changes.get(market2, 0)
                    
                    if (change1 > 0 and change2 > 0) or (change1 < 0 and change2 < 0):
                        corr = 0.7  # Pozytywna korelacja
                    else:
                        corr = -0.3  # Negatywna korelacja
                    
                    correlations[f"{market1}-{market2}"] = corr
                    correlations[f"{market2}-{market1}"] = corr
        
        return {
            "correlations": correlations,
            "market_changes": market_avg_changes
        }
        
    except Exception as e:
        print(f"⚠️ Błąd obliczania korelacji: {e}")
        return {
            "correlations": {},
            "market_changes": {}
        }

def generate_market_insights(market_analysis, correlations):
    """
    Generuje insights i rekomendacje na podstawie analizy rynków
    
    Returns:
        list: Lista insights z ikonami, tytułami i opisami
    """
    insights = []
    
    try:
        markets = market_analysis.get("markets", {})
        total_value = market_analysis.get("total_value", 0)
        div_score = market_analysis.get("diversification_score", 0)
        market_changes = correlations.get("market_changes", {})
        
        # 1. Diversification Score
        if div_score > 75:
            insights.append({
                "type": "success",
                "icon": "✅",
                "title": "Świetna dywersyfikacja geograficzna",
                "description": f"Score: {div_score:.0f}/100. Portfel dobrze rozłożony między rynkami."
            })
        elif div_score > 50:
            insights.append({
                "type": "info",
                "icon": "ℹ️",
                "title": "Umiarkowana dywersyfikacja",
                "description": f"Score: {div_score:.0f}/100. Możesz zwiększyć ekspozycję na inne rynki."
            })
        else:
            insights.append({
                "type": "warning",
                "icon": "⚠️",
                "title": "Niska dywersyfikacja geograficzna",
                "description": f"Score: {div_score:.0f}/100. Portfel zbyt skoncentrowany na jednym rynku."
            })
        
        # 2. Dominujący rynek
        if markets:
            sorted_markets = sorted(markets.items(), key=lambda x: x[1]["percentage"], reverse=True)
            if sorted_markets:  # Sprawdź czy lista nie jest pusta
                top_market = sorted_markets[0]
                
                if top_market[1]["percentage"] > 70:
                    insights.append({
                        "type": "warning",
                        "icon": "🌎",
                        "title": f"Nadmierna ekspozycja na {top_market[0]}",
                        "description": f"{top_market[1]['percentage']:.1f}% portfela. Rozważ zwiększenie innych rynków."
                    })
                elif top_market[1]["percentage"] > 50:
                    insights.append({
                        "type": "info",
                        "icon": "🌎",
                        "title": f"Dominacja rynku {top_market[0]}",
                        "description": f"{top_market[1]['percentage']:.1f}% portfela. To może być OK dla Twojej strategii."
                    })
        
        # 3. Crypto exposure
        crypto = markets.get("Crypto", {})
        crypto_pct = crypto.get("percentage", 0)
        
        if crypto_pct > 15:
            insights.append({
                "type": "warning",
                "icon": "⚡",
                "title": "Wysokie ryzyko crypto",
                "description": f"{crypto_pct:.1f}% w krypto. Eksperci zalecają max 10% dla większości inwestorów."
            })
        elif crypto_pct > 5:
            insights.append({
                "type": "info",
                "icon": "💎",
                "title": "Umiarkowana ekspozycja crypto",
                "description": f"{crypto_pct:.1f}% w krypto. W granicach norm (5-10%)."
            })
        elif crypto_pct > 0:
            insights.append({
                "type": "success",
                "icon": "💎",
                "title": "Konserwatywna ekspozycja crypto",
                "description": f"{crypto_pct:.1f}% w krypto. Niskie ryzyko, może brakować potencjału wzrostu."
            })
        
        # 4. Emerging markets
        emerging = markets.get("Emerging", {})
        emerging_pct = emerging.get("percentage", 0)
        
        if emerging_pct < 5 and total_value > 20000:
            insights.append({
                "type": "info",
                "icon": "🌏",
                "title": "Brak emerging markets",
                "description": "Rozważ dodanie ekspozycji na rynki wschodzące (Brazylia, Indie, Chiny) - wyższy potencjał wzrostu."
            })
        
        # 5. Performance po rynkach
        if market_changes:
            try:
                best_market = max(market_changes.items(), key=lambda x: x[1])
                worst_market = min(market_changes.items(), key=lambda x: x[1])
                
                if best_market[1] > 5:
                    insights.append({
                        "type": "success",
                        "icon": "📈",
                        "title": f"Najlepszy rynek: {best_market[0]}",
                        "description": f"+{best_market[1]:.1f}% średnia zmiana. Silne momentum."
                    })
                
                if worst_market[1] < -5:
                    insights.append({
                        "type": "warning",
                        "icon": "📉",
                        "title": f"Najsłabszy rynek: {worst_market[0]}",
                        "description": f"{worst_market[1]:.1f}% średnia zmiana. Sprawdź czy teza inwestycyjna się sprawdza."
                    })
            except ValueError:
                # market_changes było puste
                pass
        
        # 6. Home bias (nadmierna ekspozycja na rynek lokalny - dla Polaków to EU)
        eu = markets.get("EU", {})
        eu_pct = eu.get("percentage", 0)
        
        if eu_pct > 40:
            insights.append({
                "type": "info",
                "icon": "🇪🇺",
                "title": "Home bias (Europa)",
                "description": f"{eu_pct:.1f}% w EU. Globalna dywersyfikacja (więcej US) może być korzystna."
            })
        
        return insights
        
    except Exception as e:
        print(f"⚠️ Błąd generowania insights: {e}")
        return []

def determine_speaking_order(message, partner_names):
    """
    Określa dynamiczną kolejność wypowiedzi na podstawie tematu.
    Eksperci w danej dziedzinie mówią pierwsi.
    """
    message_lower = message.lower()
    
    # Definicje ekspertyz
    crypto_experts = ['Changpeng Zhao (CZ)', 'Partner ds. Aktywów Cyfrowych']
    value_experts = ['Benjamin Graham', 'Warren Buffett', 'Philip Fisher']
    trading_experts = ['George Soros']
    quality_experts = ['Partner ds. Jakości Biznesowej']
    strategic_experts = ['Partner Strategiczny']
    
    # Słowa kluczowe dla różnych tematów
    crypto_keywords = ['krypto', 'bitcoin', 'btc', 'eth', 'blockchain', 'defi', 'nft', 'altcoin', 'token']
    value_keywords = ['wartość', 'fundamenty', 'dywidenda', 'p/e', 'p/b', 'margin of safety', 'value investing']
    trading_keywords = ['trading', 'short', 'spekulacja', 'momentum', 'swing', 'pozycja krótka']
    quality_keywords = ['jakość', 'zarządzanie', 'moat', 'przewaga konkurencyjna', 'model biznesowy']
    strategic_keywords = ['strategia', 'plan', 'cel', 'alokacja', 'dywersyfikacja', 'portfel']
    
    # Wykryj temat
    priority_experts = []
    if any(keyword in message_lower for keyword in crypto_keywords):
        priority_experts = crypto_experts
    elif any(keyword in message_lower for keyword in value_keywords):
        priority_experts = value_experts
    elif any(keyword in message_lower for keyword in trading_keywords):
        priority_experts = trading_experts
    elif any(keyword in message_lower for keyword in quality_keywords):
        priority_experts = quality_experts
    elif any(keyword in message_lower for keyword in strategic_keywords):
        priority_experts = strategic_experts
    
    # Utwórz listę: najpierw eksperci, potem reszta
    ordered_names = []
    for expert in priority_experts:
        if expert in partner_names:
            ordered_names.append(expert)
    
    for name in partner_names:
        if name not in ordered_names:
            ordered_names.append(name)
    
    return ordered_names

def analyze_sentiment(response):
    """
    Analizuje reakcję/emocję w odpowiedzi partnera.
    Zwraca emoji i typ reakcji.
    """
    response_lower = response.lower()
    
    # Silne zgadzanie się
    if any(word in response_lower for word in ['zgadzam się', 'całkowicie racja', 'dokładnie', 'wspieramy', 'popieram']):
        return "✅", "zgoda"
    
    # Silne niezgadzanie się
    if any(word in response_lower for word in ['nie zgadzam się', 'błąd', 'mylisz się', 'to ryzykowne', 'ostrzegam', 'sprzeciwiam']):
        return "❌", "sprzeciw"
    
    # Ostrzeżenie
    if any(word in response_lower for word in ['uwaga', 'ostrożnie', 'ryzyko', 'problem', 'zagrożenie']):
        return "⚠️", "ostrzeżenie"
    
    # Neutralne/rozwijające
    if any(word in response_lower for word in ['rozumiem', 'widzę', 'interesujące', 'warto rozważyć']):
        return "💭", "refleksja"
    
    # Pytanie/wątpliwość
    if '?' in response or any(word in response_lower for word in ['czy', 'jak', 'dlaczego', 'kiedy']):
        return "❓", "pytanie"
    
    return "💬", "komentarz"

def should_interrupt(partner, message, previous_responses):
    """
    Określa czy partner powinien 'przerwać' w trakcie dyskusji.
    Przerwanie następuje gdy:
    - Partner ma bardzo silną opinię przeciwną
    - Temat jest w jego ekspertyzie a poprzednicy się mylą
    """
    if not previous_responses:
        return False
    
    partner_lower = partner.lower()
    message_lower = message.lower()
    
    # Graham przerywa gdy ktoś ignoruje ryzyko
    if 'graham' in partner_lower:
        for _, prev_resp in previous_responses:
            if any(word in prev_resp.lower() for word in ['agresywny', 'ryzyko warte', 'spekulacja']):
                return True
    
    # Buffett przerywa gdy ktoś komplikuje prostą sprawę
    if 'buffett' in partner_lower:
        for _, prev_resp in previous_responses:
            if len(prev_resp) > 500 and 'skomplikowany' in prev_resp.lower():
                return True
    
    # CZ przerywa gdy mówią o krypto a nie znają technologii
    if 'zhao' in partner_lower or 'cz' in partner_lower:
        if any(word in message_lower for word in ['bitcoin', 'krypto', 'blockchain']):
            for prev_partner, _ in previous_responses:
                if 'graham' in prev_partner.lower() or 'buffett' in prev_partner.lower():
                    return True
    
    return False

def send_to_all_partners(message, stan_spolki=None, cele=None, tryb_odpowiedzi="normalny"):
    """
    Generator - wysyła wiadomość do wszystkich Partnerów kolejno (jeden za drugim).
    NOWE FUNKCJE:
    - Dynamiczna kolejność (eksperci w temacie jako pierwsi)
    - System zwracania się do siebie po imieniu
    - Przerywanie gdy silna opinia przeciwna
    - Reakcje/emocje w dialogu
    - Głosowanie po dyskusji
    """
    # Inicjalizuj historię odpowiedzi w session_state jeśli nie istnieje
    if 'partner_history' not in st.session_state:
        st.session_state.partner_history = {}
    
    # Użyj prawdziwych partnerów z gra_rpg.py (pomijając Partnera Zarządzającego - to użytkownik!)
    partner_names = []
    if IMPORTS_OK and PERSONAS:
        for name in PERSONAS.keys():
            # Pomiń Partnera Zarządzającego - to użytkownik
            if 'Partner Zarządzający' in name and '(JA)' in name:
                continue
            partner_names.append(name)
    
    # 🎯 DYNAMICZNA KOLEJNOŚĆ (tematyczna)
    ordered_partners = determine_speaking_order(message, partner_names)
    
    # Zbieram odpowiedzi poprzednich partnerów (kontekst rozmowy)
    previous_responses = []
    partner_votes = {}  # Do głosowania końcowego
    
    for partner in ordered_partners:
        # 🤚 SYSTEM PRZERYWANIA
        is_interrupting = should_interrupt(partner, message, previous_responses)
        
        # Dodaj kontekst poprzednich odpowiedzi do wiadomości
        message_with_context = message
        if previous_responses:
            context_section = "\n\n💬 POPRZEDNIE WYPOWIEDZI NA TYM SPOTKANIU RADY:\n"
            for prev_partner, prev_response in previous_responses:
                context_section += f"\n**{prev_partner}** powiedział:\n{prev_response}\n"
            context_section += "\n---\n"
            
            # 👥 SYSTEM ZWRACANIA SIĘ DO SIEBIE
            names_in_room = [p for p in ordered_partners]
            context_section += "👥 OBECNI NA SPOTKANIU: " + ", ".join(names_in_room) + "\n\n"
            context_section += "⚠️ WAŻNE ZASADY ROZMOWY:\n"
            context_section += "1. Zwracaj się do kolegów PO IMIENIU (np. 'Warren, zgadzam się...' lub 'CZ, Twoja analiza...')\n"
            context_section += "2. Możesz się zgodzić, nie zgodzić, lub rozwinąć ich argumenty\n"
            context_section += "3. To jest rozmowa, nie monolog - REAGUJ na to co inni powiedzieli!\n"
            
            # 🎭 SYSTEM REAKCJI/EMOCJI
            context_section += "4. Wyraź swoją REAKCJĘ na początku:\n"
            context_section += "   - [zgadzam się ✅] gdy popieram poprzedników\n"
            context_section += "   - [nie zgadzam się ❌] gdy widzę błąd w rozumowaniu\n"
            context_section += "   - [ostrzegam ⚠️] gdy widzę ryzyko\n"
            context_section += "   - [mam pytanie ❓] gdy chcę wyjaśnienia\n"
            context_section += "   - [wstrzymuję się 💭] gdy potrzebuję więcej informacji\n\n"
            
            if is_interrupting:
                context_section += "🤚 PRZERWIJ DYSKUSJĘ! Twoja ekspertyza/opinia jest KLUCZOWA w tym temacie!\n"
                context_section += "Zacznij od: 'Moment! Muszę przerwać, bo...' lub 'Przepraszam że przerwę, ale...'\n\n"
            
            message_with_context = context_section + "\n\nPYTANIE PARTNERA ZARZĄDZAJĄCEGO:\n" + message
        
        # Wysyłaj z trybem odpowiedzi i kontekstem poprzednich
        response, knowledge = send_to_ai_partner(partner, message_with_context, stan_spolki, cele, tryb_odpowiedzi)
        
        # 🎭 ANALIZA REAKCJI/EMOCJI
        sentiment_emoji, sentiment_type = analyze_sentiment(response)
        
        # 📊 WYCIĄGNIJ GŁOS (jeśli jest w odpowiedzi)
        vote = None
        response_lower = response.lower()
        if '[głosuję: tak]' in response_lower or 'głosuję za' in response_lower:
            vote = "ZA"
        elif '[głosuję: nie]' in response_lower or 'głosuję przeciw' in response_lower:
            vote = "PRZECIW"
        elif '[głosuję: wstrzymuję]' in response_lower or 'wstrzymuję się' in response_lower:
            vote = "WSTRZYMANY"
        
        # Zapisz głos partnera
        if vote:
            partner_votes[partner] = vote
        
        # Dodaj tę odpowiedź do kontekstu dla kolejnych partnerów
        previous_responses.append((partner, response))
        
        # Zapisz do historii
        if partner not in st.session_state.partner_history:
            st.session_state.partner_history[partner] = []
        
        st.session_state.partner_history[partner].append({
            'message': message,
            'response': response,
            'knowledge': knowledge,
            'timestamp': datetime.now().isoformat()
        })
        
        # Bezpieczne emoji dla Streamlit chat (tylko podstawowe)
        avatar = "🤖"
        if partner in PERSONAS:
            # Mapowanie kolorów na BEZPIECZNE emoji
            color_map = {
                '\033[97m': '👔',  # Partner Zarządzający (nie wyświetlany)
                '\033[94m': '📊',  # Partner Strategiczny
                '\033[93m': '💼',  # Partner ds. Jakości
                '\033[96m': '💎',  # Partner ds. Aktywów Cyfrowych
                '\033[90m': '🛡',  # Benjamin Graham
                '\033[95m': '🔍',  # Philip Fisher
                '\033[91m': '🌍',  # George Soros
                '\033[92m': '🎯',  # Warren Buffett
            }
            color = PERSONAS[partner].get('color_code', '')
            avatar = color_map.get(color, "🤖")
        
        # Yield odpowiedź od razu (generator pattern)
        yield {
            "partner": partner,
            "response": response,
            "avatar": avatar,
            "knowledge": knowledge,
            "sentiment_emoji": sentiment_emoji,
            "sentiment_type": sentiment_type,
            "vote": vote,
            "is_interrupting": is_interrupting
        }
    
    # 📊 PODSUMOWANIE GŁOSOWANIA (jeśli były głosy)
    if partner_votes:
        # Wczytaj wagi głosów z Kodeksu
        voting_weights = wczytaj_wagi_glosu_z_kodeksu()
        
        votes_za = []
        votes_przeciw = []
        votes_wstrzymane = []
        
        for partner, vote in partner_votes.items():
            weight = voting_weights.get(partner, 0)
            if vote == "ZA":
                votes_za.append((partner, weight))
            elif vote == "PRZECIW":
                votes_przeciw.append((partner, weight))
            else:
                votes_wstrzymane.append((partner, weight))
        
        total_za = sum(w for _, w in votes_za)
        total_przeciw = sum(w for _, w in votes_przeciw)
        total_wstrzymane = sum(w for _, w in votes_wstrzymane)
        
        # Formatuj wyniki
        voting_summary = "\n\n" + "="*50 + "\n"
        voting_summary += "📊 WYNIKI GŁOSOWANIA RADY PARTNERÓW\n"
        voting_summary += "="*50 + "\n\n"
        
        if votes_za:
            voting_summary += f"✅ ZA ({total_za:.1f}%):\n"
            for partner, weight in votes_za:
                voting_summary += f"   • {partner} ({weight:.1f}%)\n"
            voting_summary += "\n"
        
        if votes_przeciw:
            voting_summary += f"❌ PRZECIW ({total_przeciw:.1f}%):\n"
            for partner, weight in votes_przeciw:
                voting_summary += f"   • {partner} ({weight:.1f}%)\n"
            voting_summary += "\n"
        
        if votes_wstrzymane:
            voting_summary += f"⚪ WSTRZYMAŁO SIĘ ({total_wstrzymane:.1f}%):\n"
            for partner, weight in votes_wstrzymane:
                voting_summary += f"   • {partner} ({weight:.1f}%)\n"
            voting_summary += "\n"
        
        # Decyzja
        voting_summary += "="*50 + "\n"
        if total_za > total_przeciw:
            voting_summary += f"✅ DECYZJA RADY: PRZYJĘTA ({total_za:.1f}% ZA > {total_przeciw:.1f}% PRZECIW)\n"
        elif total_przeciw > total_za:
            voting_summary += f"❌ DECYZJA RADY: ODRZUCONA ({total_przeciw:.1f}% PRZECIW > {total_za:.1f}% ZA)\n"
        else:
            voting_summary += f"⚖️ DECYZJA RADY: REMIS ({total_za:.1f}% vs {total_przeciw:.1f}%) - wymagana dalsza dyskusja\n"
        voting_summary += "="*50 + "\n"
        
        # Yield podsumowanie jako specjalny element
        yield {
            "partner": "🗳️ Podsumowanie Głosowania",
            "response": voting_summary,
            "avatar": "🗳️",
            "knowledge": [],
            "sentiment_emoji": "📊",
            "sentiment_type": "podsumowanie",
            "vote": None,
            "is_interrupting": False,
            "is_voting_summary": True
        }

# Konfiguracja strony
st.set_page_config(
    page_title="Horyzont Partnerów",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS dla lepszego wyglądu
def apply_custom_css(theme="light"):
    """Aplikuje custom CSS w zależności od motywu"""
    
    if theme == "dark":
        css = """
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #4da6ff;
                text-align: center;
                padding: 20px 0;
            }
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            .metric-card {
                background-color: #1e2130;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.4);
            }
            .stMetric {
                background-color: #262730;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }
            .stButton button {
                border-radius: 8px;
                font-weight: 500;
            }
        </style>
        """
    else:
        css = """
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1f77b4;
                text-align: center;
                padding: 20px 0;
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stMetric {
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .stButton button {
                border-radius: 8px;
                font-weight: 500;
            }
        </style>
        """
    
    st.markdown(css, unsafe_allow_html=True)

# Inicjalizacja session state dla ustawień
def load_user_preferences():
    """Wczytuje zapisane preferencje użytkownika"""
    default_preferences = {
        "theme": "light",
        "notifications_enabled": True,
        "cache_ttl": 5,
        "auto_refresh": False,
        "refresh_interval": 60
    }
    
    if PERSISTENT_OK:
        prefs = load_persistent_data('user_preferences.json')
        if prefs:
            return prefs
    
    # Fallback
    preferences_file = "user_preferences.json"
    try:
        if os.path.exists(preferences_file):
            with open(preferences_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Błąd wczytywania preferencji: {e}")
    
    return default_preferences

def save_user_preferences(preferences):
    """Zapisuje preferencje użytkownika do pliku"""
    if PERSISTENT_OK:
        return save_persistent_data('user_preferences.json', preferences)
    
    # Fallback
    preferences_file = "user_preferences.json"
    try:
        with open(preferences_file, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Błąd zapisywania preferencji: {e}")
        return False

def init_session_state():
    """Inicjalizuje session state z domyślnymi wartościami lub zapisanymi preferencjami"""
    # Wczytaj zapisane preferencje
    preferences = load_user_preferences()
    
    if 'theme' not in st.session_state:
        st.session_state.theme = preferences.get("theme", "light")
    if 'notifications_enabled' not in st.session_state:
        st.session_state.notifications_enabled = preferences.get("notifications_enabled", True)
    if 'cache_ttl' not in st.session_state:
        st.session_state.cache_ttl = preferences.get("cache_ttl", 5)
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = preferences.get("auto_refresh", False)
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = preferences.get("refresh_interval", 60)
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'selected_partner' not in st.session_state:
        st.session_state.selected_partner = "Wszyscy"

# Funkcja normalizująca strukturę danych
def normalize_stan_spolki(stan_spolki):
    """Normalizuje strukturę danych do oczekiwanego formatu (lowercase keys)"""
    if not stan_spolki:
        return None
    
    normalized = {}
    
    # PORTFEL_AKCJI → akcje
    if 'PORTFEL_AKCJI' in stan_spolki:
        raw_akcje = stan_spolki['PORTFEL_AKCJI']
        normalized['akcje'] = {
            'wartosc_pln': raw_akcje.get('Suma_PLN', 0),
            'wartosc_usd': raw_akcje.get('Suma_USD', 0),
            'liczba_pozycji': raw_akcje.get('Liczba_pozycji_calkowita', 
                                           raw_akcje.get('Liczba_pozycji', 0)),
            'pozycje': raw_akcje.get('Pozycje_szczegoly', {}),
            'dane_rynkowe': raw_akcje.get('Dane_rynkowe', {})
        }
    elif 'akcje' in stan_spolki:
        normalized['akcje'] = stan_spolki['akcje']
    
    # PORTFEL_KRYPTO → krypto
    if 'PORTFEL_KRYPTO' in stan_spolki:
        raw_krypto = stan_spolki['PORTFEL_KRYPTO']
        normalized['krypto'] = {
            'wartosc_pln': raw_krypto.get('Suma_PLN', 0),
            'wartosc_usd': raw_krypto.get('Suma_USD', 0),
            'liczba_pozycji': raw_krypto.get('Liczba_pozycji', 0)
        }
    elif 'krypto' in stan_spolki:
        normalized['krypto'] = stan_spolki['krypto']
    
    # ZOBOWIAZANIA → dlugi
    if 'ZOBOWIAZANIA' in stan_spolki:
        raw_dlugi = stan_spolki['ZOBOWIAZANIA']
        normalized['dlugi'] = {
            'suma_dlugow': raw_dlugi.get('Suma_dlugow_PLN', 0),
            'suma_dlugow_usd': raw_dlugi.get('Suma_dlugow_USD', 0),
            'suma_rat_miesiecznie': raw_dlugi.get('Suma_rat_miesiecznie_PLN', 0),
            'liczba_zobowiazan': raw_dlugi.get('Liczba_zobowiazan', 0),
            'lista_kredytow': raw_dlugi.get('Lista_kredytow', [])
        }
    elif 'dlugi' in stan_spolki:
        normalized['dlugi'] = stan_spolki['dlugi']
    
    # PRZYCHODY_I_WYDATKI → wyplata
    if 'PRZYCHODY_I_WYDATKI' in stan_spolki:
        raw_wyplata = stan_spolki['PRZYCHODY_I_WYDATKI']
        normalized['wyplata'] = {
            'dostepne_na_inwestycje': raw_wyplata.get('Dostepne_na_inwestycje_PLN', 0),
            'dostepne_na_inwestycje_usd': raw_wyplata.get('Dostepne_na_inwestycje_USD', 0),
            'suma_przychodow': raw_wyplata.get('Suma_przychodow_PLN', 0),
            'wynagrodzenie': raw_wyplata.get('Wynagrodzenie_PLN', 0),
            'premia': raw_wyplata.get('Premia_PLN', 0),
            'suma_wydatkow': raw_wyplata.get('Suma_wydatkow_PLN', 0),
            'raty_kredytow': raw_wyplata.get('Raty_kredytow_PLN', 0),
            # Aliasy dla kompatybilności
            'wydatki_stale': raw_wyplata.get('Suma_wydatkow_PLN', 0),
            'raty_miesieczne': raw_wyplata.get('Raty_kredytow_PLN', 0)
        }
    elif 'wyplata' in stan_spolki:
        normalized['wyplata'] = stan_spolki['wyplata']
    
    # PODSUMOWANIE → podsumowanie
    if 'PODSUMOWANIE' in stan_spolki:
        normalized['podsumowanie'] = stan_spolki['PODSUMOWANIE']
    elif 'podsumowanie' in stan_spolki:
        normalized['podsumowanie'] = stan_spolki['podsumowanie']
    
    # Kurs USD/PLN
    if 'Kurs_USD_PLN' in stan_spolki:
        normalized['kurs_usd_pln'] = stan_spolki['Kurs_USD_PLN']
    elif 'kurs_usd_pln' in stan_spolki:
        normalized['kurs_usd_pln'] = stan_spolki['kurs_usd_pln']
    
    # Skopiuj pozostałe dane bez zmian
    for key, value in stan_spolki.items():
        if key.upper() not in ['PORTFEL_AKCJI', 'PORTFEL_KRYPTO', 'ZOBOWIAZANIA', 
                                'PRZYCHODY_I_WYDATKI', 'PODSUMOWANIE', 'KURS_USD_PLN']:
            if key.lower() not in normalized:
                normalized[key] = value
    
    return normalized

# Funkcja do ładowania danych
@st.cache_data(ttl=60)  # Cache na 1 minutę (zmniejszono z 5 minut dla szybszej synchronizacji)
@st.cache_data(ttl=300)  # Cache na 5 minut
def load_portfolio_data():
    """Pobiera dane portfela"""
    if not IMPORTS_OK:
        return None, None
    
    try:
        cele = wczytaj_cele()
        stan_spolki_raw = pobierz_stan_spolki(cele)
        stan_spolki = normalize_stan_spolki(stan_spolki_raw)
        return stan_spolki, cele
    except Exception as e:
        st.error(f"Błąd podczas ładowania danych: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None, None

def format_currency(amount, currency="PLN"):
    """Formatuje walutę"""
    if amount >= 1_000_000:
        return f"{amount/1_000_000:.2f}M {currency}"
    elif amount >= 1_000:
        return f"{amount/1_000:.1f}K {currency}"
    else:
        return f"{amount:.0f} {currency}"

def get_dividend_trend_indicator(dywidendy_info):
    """
    Oblicza prosty wskaźnik trendu dla dywidend
    Returns: dict with 'trend_emoji', 'trend_text', 'trend_color'
    """
    try:
        liczba_spolek = dywidendy_info.get('liczba_spolek_z_dywidendami', 0)
        miesieczna_kwota = dywidendy_info.get('miesieczna_kwota_pln', 0)
        
        # Oblicz średnią dywidendę na spółkę
        if liczba_spolek > 0:
            avg_per_company = miesieczna_kwota / liczba_spolek
        else:
            avg_per_company = 0
        
        # Benchmark: Dobra dywidenda to ~100 PLN/mies na spółkę
        benchmark = 100
        
        if avg_per_company >= benchmark * 1.2:
            # Powyżej 120 PLN/spółkę - excellent trend
            return {
                'trend_emoji': '📈',
                'trend_text': 'Wysoka rentowność',
                'trend_color': 'green',
                'trend_percentage': '+20%'
            }
        elif avg_per_company >= benchmark * 0.8:
            # 80-120 PLN/spółkę - stable trend
            return {
                'trend_emoji': '➡️',
                'trend_text': 'Stabilny trend',
                'trend_color': 'blue',
                'trend_percentage': '±0%'
            }
        else:
            # Poniżej 80 PLN/spółkę - needs improvement
            return {
                'trend_emoji': '📉',
                'trend_text': 'Potencjał wzrostu',
                'trend_color': 'orange',
                'trend_percentage': '-20%'
            }
    except Exception as e:
        return {
            'trend_emoji': '➡️',
            'trend_text': 'Brak danych',
            'trend_color': 'gray',
            'trend_percentage': 'N/A'
        }

def calculate_portfolio_deltas(stan_spolki, cele):
    """
    Oblicza zmiany wartości portfela z ostatniego tygodnia
    Returns: dict with 'wartosc_netto_delta', 'leverage_delta', 'pozycje_delta', 'last_update'
    """
    try:
        # Załaduj historię portfela
        if os.path.exists('portfolio_history.json'):
            with open('portfolio_history.json', 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                snapshots = history_data.get('snapshots', [])
                
                if len(snapshots) < 2:
                    return {
                        'wartosc_netto_delta': None,
                        'leverage_delta': None, 
                        'pozycje_delta': None,
                        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M')
                    }
                
                # Znajdź snapshot sprzed ~7 dni
                today = datetime.now()
                week_ago = today - timedelta(days=7)
                
                # Sortuj po dacie (najnowsze pierwsze)
                sorted_snapshots = sorted(snapshots, key=lambda x: x.get('timestamp', ''), reverse=True)
                current_snapshot = sorted_snapshots[0] if sorted_snapshots else None
                week_ago_snapshot = None
                
                for snapshot in sorted_snapshots:
                    snap_date = datetime.fromisoformat(snapshot.get('timestamp', ''))
                    if snap_date <= week_ago:
                        week_ago_snapshot = snapshot
                        break
                
                # Jeśli nie znaleziono z tydzień temu, użyj najstarszego
                if not week_ago_snapshot and len(sorted_snapshots) > 1:
                    week_ago_snapshot = sorted_snapshots[-1]
                
                if not current_snapshot or not week_ago_snapshot:
                    return {
                        'wartosc_netto_delta': None,
                        'leverage_delta': None,
                        'pozycje_delta': None,
                        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M')
                    }
                
                # Oblicz aktualne wartości
                rezerwa_current = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
                wartosc_netto_current = (
                    stan_spolki['akcje'].get('wartosc_pln', 0) + 
                    stan_spolki['krypto'].get('wartosc_pln', 0) +
                    rezerwa_current -
                    get_suma_kredytow()
                )
                
                suma_aktywow_current = (
                    stan_spolki['akcje'].get('wartosc_pln', 0) + 
                    stan_spolki['krypto'].get('wartosc_pln', 0) +
                    rezerwa_current
                )
                leverage_current = (get_suma_kredytow() / suma_aktywow_current * 100) if suma_aktywow_current > 0 else 0
                
                pozycje_current = (
                    stan_spolki['akcje'].get('liczba_pozycji', 0) + 
                    stan_spolki['krypto'].get('liczba_pozycji', 0)
                )
                
                # Pobierz wartości z week ago
                wartosc_netto_old = week_ago_snapshot.get('net_worth', wartosc_netto_current)
                leverage_old = week_ago_snapshot.get('leverage', leverage_current)
                pozycje_old = week_ago_snapshot.get('total_positions', pozycje_current)
                
                # Oblicz delty
                wartosc_netto_delta_pct = ((wartosc_netto_current - wartosc_netto_old) / wartosc_netto_old * 100) if wartosc_netto_old > 0 else 0
                leverage_delta_pct = leverage_current - leverage_old  # Punkty procentowe
                pozycje_delta = pozycje_current - pozycje_old
                
                last_update = current_snapshot.get('timestamp', datetime.now().isoformat())
                
                return {
                    'wartosc_netto_delta': f"{wartosc_netto_delta_pct:+.2f}%",
                    'leverage_delta': f"{leverage_delta_pct:+.2f}pp",
                    'pozycje_delta': f"{pozycje_delta:+d}",
                    'last_update': datetime.fromisoformat(last_update).strftime('%Y-%m-%d %H:%M')
                }
                
    except Exception as e:
        # Jeśli błąd, zwróć None dla wszystkich
        return {
            'wartosc_netto_delta': None,
            'leverage_delta': None,
            'pozycje_delta': None,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    
    return {
        'wartosc_netto_delta': None,
        'leverage_delta': None,
        'pozycje_delta': None,
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    return f"{amount:.2f} {currency}"

def create_portfolio_value_chart(stan_spolki, cele=None):
    """Tworzy wykres wartości portfela"""
    if not stan_spolki:
        return go.Figure()
    
    # Przygotuj dane z bezpiecznym dostępem - ładuj raz
    wyplaty_cf = load_wyplaty()
    kredyty_chart = load_kredyty()
    wydatki_cf = load_wydatki()
    
    if wyplaty_cf:
        ostatnia_wyplata_chart = wyplaty_cf[0]['kwota']
        wydatki_stale_chart = get_suma_wydatkow_stalych(wydatki_cf)
        raty_chart = sum(k['rata_miesieczna'] for k in kredyty_chart)
        cash_flow_value = ostatnia_wyplata_chart - wydatki_stale_chart - raty_chart
    else:
        cash_flow_value = 0
    
    # Rezerwa gotówkowa
    rezerwa = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
    
    categories = ['Akcje', 'Krypto', 'Rezerwa Gotówkowa', 'Cash Flow', 'Zobowiązania']
    values = [
        stan_spolki.get('akcje', {}).get('wartosc_pln', 0),
        stan_spolki.get('krypto', {}).get('wartosc_pln', 0),
        rezerwa,  # Rezerwa gotówkowa z cele.json
        max(cash_flow_value, 0),  # Nadwyżka z wyplaty.json (tylko dodatnia)
        -sum(k['kwota_poczatkowa'] - k['splacono'] for k in kredyty_chart)  # Zobowiązania - bez kolejnego load
    ]
    
    colors = ['#1f77b4', '#ff7f0e', '#9467bd', '#2ca02c', '#d62728']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[format_currency(abs(v)) for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Struktura Portfela",
        xaxis_title="Kategoria",
        yaxis_title="Wartość (PLN)",
        height=400,
        showlegend=False
    )
    
    return fig

def create_allocation_pie_chart(stan_spolki, cele=None):
    """Tworzy wykres kołowy alokacji"""
    if not stan_spolki:
        return go.Figure()
    
    akcje = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
    krypto = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
    rezerwa = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
    
    fig = go.Figure(data=[go.Pie(
        labels=['Akcje', 'Krypto', 'Rezerwa Gotówkowa'],
        values=[akcje, krypto, rezerwa],
        hole=0.4,
        marker_colors=['#1f77b4', '#ff7f0e', '#9467bd']
    )])
    
    fig.update_layout(
        title="Alokacja Aktywów",
        height=400
    )
    
    return fig


# ============================================================================
# TRANSACTIONS LOG - Strona dziennika transakcji
# ============================================================================

def show_transactions_page():
    """Strona Transactions Log - centralny dziennik wszystkich transakcji"""
    st.title("📝 Dziennik Transakcji")
    st.markdown("*Centralna ewidencja wszystkich operacji finansowych spółki*")
    
    # Wczytaj transakcje
    transactions = load_transactions()
    
    # === SEKCJA 1: KPI ===
    st.markdown("### 📊 Podsumowanie")
    
    from datetime import datetime, timedelta
    today = datetime.now()
    month_start = today.replace(day=1)
    
    # Podsumowanie bieżącego miesiąca
    summary = get_transactions_summary(transactions, start_date=month_start)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Przychody", f"{summary['income']:,.0f} PLN")
    with col2:
        st.metric("💸 Wydatki", f"{summary['expenses']:,.0f} PLN")
    with col3:
        net_color = "normal" if summary['net_flow'] >= 0 else "inverse"
        st.metric("📈 Cash Flow", f"{summary['net_flow']:,.0f} PLN", 
                 delta=f"{summary['net_flow']:,.0f} PLN", delta_color=net_color)
    with col4:
        st.metric("📋 Transakcje", f"{summary['count']}")
    
    st.markdown("---")
    
    # === SEKCJA 2: DODAJ TRANSAKCJĘ ===
    with st.expander("➕ Dodaj nową transakcję", expanded=False):
        with st.form("add_transaction"):
            col1, col2 = st.columns(2)
            
            with col1:
                typ = st.selectbox("Typ transakcji", 
                                  ["income", "expense", "transfer"],
                                  format_func=lambda x: {"income": "💰 Przychód", 
                                                        "expense": "💸 Wydatek",
                                                        "transfer": "🔄 Transfer"}[x])
                
                kategorie_income = ["salary", "dividend", "interest", "crypto_profit", "stock_profit", "other_income"]
                kategorie_expense = ["investment", "loan_payment", "tax", "fee", "withdrawal", "other_expense"]
                kategorie_transfer = ["rebalancing", "internal_transfer"]
                
                if typ == "income":
                    kategoria_options = kategorie_income
                elif typ == "expense":
                    kategoria_options = kategorie_expense
                else:
                    kategoria_options = kategorie_transfer
                
                kategoria = st.selectbox("Kategoria", kategoria_options,
                                        format_func=lambda x: {
                                            "salary": "💵 Wypłata",
                                            "dividend": "💎 Dywidenda",
                                            "interest": "📈 Odsetki",
                                            "crypto_profit": "₿ Zysk z krypto",
                                            "stock_profit": "📊 Zysk z akcji",
                                            "other_income": "💰 Inny przychód",
                                            "investment": "🎯 Inwestycja",
                                            "loan_payment": "🏦 Spłata kredytu",
                                            "tax": "🧾 Podatek",
                                            "fee": "💳 Opłata",
                                            "withdrawal": "🏧 Wypłata gotówki",
                                            "other_expense": "💸 Inny wydatek",
                                            "rebalancing": "⚖️ Rebalansowanie",
                                            "internal_transfer": "🔄 Transfer wewnętrzny"
                                        }.get(x, x))
            
            with col2:
                kwota = st.number_input("Kwota (PLN)", min_value=0.01, value=1000.0, step=100.0)
                data_trans = st.date_input("Data transakcji", value=today)
            
            opis = st.text_area("Opis transakcji (opcjonalnie)", 
                               placeholder="Np. Zakup BTC, Spłata kredytu hipotecznego, Dywidenda z akcji XYZ")
            
            if st.form_submit_button("💾 Zapisz transakcję", use_container_width=True):
                # Dodaj transakcję z datą wybraną przez użytkownika
                trans_datetime = datetime.combine(data_trans, datetime.min.time())
                transaction = {
                    'id': str(datetime.now().timestamp()),
                    'data': trans_datetime.isoformat(),
                    'typ': typ,
                    'kategoria': kategoria,
                    'kwota': abs(kwota),
                    'opis': opis,
                    'metadata': {}
                }
                
                transactions.append(transaction)
                transactions.sort(key=lambda x: x['data'], reverse=True)
                
                if save_transactions(transactions):
                    st.success(f"✅ Transakcja zapisana: {kwota:,.0f} PLN ({kategoria})")
                    st.rerun()
                else:
                    st.error("❌ Błąd zapisu")
    
    st.markdown("---")
    
    # === SEKCJA 3: FILTRY ===
    st.markdown("### 🔍 Filtruj transakcje")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        filtr_typ = st.selectbox("Typ", ["Wszystkie", "income", "expense", "transfer"],
                                format_func=lambda x: {"Wszystkie": "Wszystkie", 
                                                      "income": "💰 Przychody",
                                                      "expense": "💸 Wydatki",
                                                      "transfer": "🔄 Transfery"}[x])
    
    with col_f2:
        wszystkie_kategorie = sorted(set(t['kategoria'] for t in transactions)) if transactions else []
        filtr_kategoria = st.selectbox("Kategoria", ["Wszystkie"] + wszystkie_kategorie)
    
    with col_f3:
        filtr_od = st.date_input("Od daty", value=today - timedelta(days=90))
    
    with col_f4:
        filtr_do = st.date_input("Do daty", value=today)
    
    # Wyszukiwarka
    search_query = st.text_input("🔎 Wyszukaj w opisie", placeholder="Szukaj...")
    
    # Filtrowanie
    filtered = transactions
    
    if filtr_typ != "Wszystkie":
        filtered = [t for t in filtered if t['typ'] == filtr_typ]
    
    if filtr_kategoria != "Wszystkie":
        filtered = [t for t in filtered if t['kategoria'] == filtr_kategoria]
    
    if filtr_od:
        filtered = [t for t in filtered if t['data'] >= filtr_od.isoformat()]
    
    if filtr_do:
        end_date = datetime.combine(filtr_do, datetime.max.time())
        filtered = [t for t in filtered if t['data'] <= end_date.isoformat()]
    
    if search_query:
        filtered = [t for t in filtered if search_query.lower() in t.get('opis', '').lower()]
    
    st.caption(f"**Znaleziono {len(filtered)} transakcji** (z {len(transactions)} w sumie)")
    
    st.markdown("---")
    
    # === SEKCJA 4: WYKRESY ===
    if filtered:
        st.markdown("### 📈 Wykresy i Analiza")
        
        tab1, tab2, tab3 = st.tabs(["💹 Cash Flow", "🥧 Kategorie", "📊 Trendy"])
        
        with tab1:
            # Wykres cash flow w czasie
            import plotly.graph_objects as go
            from collections import defaultdict
            
            # Grupuj po dniach
            daily_flow = defaultdict(lambda: {'income': 0, 'expense': 0})
            for t in filtered:
                date = t['data'][:10]
                if t['typ'] == 'income':
                    daily_flow[date]['income'] += t['kwota']
                elif t['typ'] == 'expense':
                    daily_flow[date]['expense'] += t['kwota']
            
            dates = sorted(daily_flow.keys())
            income_vals = [daily_flow[d]['income'] for d in dates]
            expense_vals = [daily_flow[d]['expense'] for d in dates]
            net_vals = [daily_flow[d]['income'] - daily_flow[d]['expense'] for d in dates]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dates, y=income_vals, name='Przychody', marker_color='green'))
            fig.add_trace(go.Bar(x=dates, y=[-e for e in expense_vals], name='Wydatki', marker_color='red'))
            fig.add_trace(go.Scatter(x=dates, y=net_vals, name='Net Flow', 
                                    line=dict(color='blue', width=3), mode='lines+markers'))
            
            fig.update_layout(title="Cash Flow w czasie", barmode='relative', 
                            xaxis_title="Data", yaxis_title="PLN",
                            hovermode='x unified', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Pie chart kategorie
            cat_summary = defaultdict(float)
            for t in filtered:
                sign = 1 if t['typ'] == 'income' else -1
                cat_summary[t['kategoria']] += t['kwota'] * sign
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(cat_summary.keys()),
                values=[abs(v) for v in cat_summary.values()],
                hole=0.3
            )])
            fig_pie.update_layout(title="Podział po kategoriach", height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab3:
            # Kumulatywny cash flow
            cumulative = []
            running_total = 0
            for date in dates:
                running_total += daily_flow[date]['income'] - daily_flow[date]['expense']
                cumulative.append(running_total)
            
            fig_cum = go.Figure()
            fig_cum.add_trace(go.Scatter(x=dates, y=cumulative, 
                                        fill='tozeroy', name='Kumulatywny Cash Flow'))
            fig_cum.update_layout(title="Kumulatywny Cash Flow", 
                                xaxis_title="Data", yaxis_title="PLN",
                                height=400)
            st.plotly_chart(fig_cum, use_container_width=True)
    
    st.markdown("---")
    
    # === SEKCJA 5: TABELA TRANSAKCJI ===
    st.markdown("### 📋 Lista transakcji")
    
    if filtered:
        # Export button
        col_export1, col_export2, col_export3 = st.columns([2, 1, 1])
        with col_export2:
            if st.button("📥 Export do CSV", use_container_width=True):
                import pandas as pd
                df = pd.DataFrame(filtered)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="⬇️ Pobierz CSV",
                    data=csv,
                    file_name=f"transactions_{today.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # Tabela
        for trans in filtered:
            typ_icon = {"income": "💰", "expense": "💸", "transfer": "🔄"}[trans['typ']]
            date_str = trans['data'][:10]
            
            with st.expander(f"{typ_icon} {date_str} - **{trans['kwota']:,.0f} PLN** ({trans['kategoria']})"):
                col_t1, col_t2, col_t3 = st.columns(3)
                
                with col_t1:
                    st.metric("Kwota", f"{trans['kwota']:,.0f} PLN")
                with col_t2:
                    st.metric("Typ", trans['typ'])
                with col_t3:
                    st.metric("Kategoria", trans['kategoria'])
                
                if trans.get('opis'):
                    st.caption(f"📝 **Opis:** {trans['opis']}")
                
                # Przycisk usuwania
                if st.button(f"🗑️ Usuń tę transakcję", key=f"del_{trans['id']}"):
                    transactions.remove(trans)
                    if save_transactions(transactions):
                        st.success("✅ Transakcja usunięta!")
                        st.rerun()
    else:
        st.info("Brak transakcji spełniających kryteria filtrowania")


# ============================================================================
# FINANCIAL CALENDAR - Strona kalendarza wydarzeń
# ============================================================================

def show_calendar_page():
    """Strona Financial Calendar - kalendarz wydarzeń finansowych"""
    st.title("📅 Kalendarz Finansowy")
    st.markdown("*Wszystkie ważne daty i wydarzenia finansowe w jednym miejscu*")
    
    st.info("🚧 **W budowie** - Ta funkcja zostanie dodana wkrótce!")
    
    st.markdown("""
    ### 🎯 Planowane funkcje:
    - 📌 Terminy płatności kredytów
    - 💰 Oczekiwane dywidendy
    - 🧾 Deadlines podatkowe
    - 📊 Earning reports (jeśli posiadasz akcje)
    - ⚖️ Harmonogram rebalansowania
    - 🔔 Przypomnienia i alerty
    """)


# ============================================================================
# TAX OPTIMIZER - Strona optymalizacji podatkowej
# ============================================================================

def show_tax_optimizer_page():
    """Strona Tax Optimizer - kalkulator i optymalizacja podatków"""
    st.title("🧮 Optymalizator Podatkowy")
    st.markdown("*Kalkulator podatków i sugestie optymalizacji*")
    
    st.info("🚧 **W budowie** - Ta funkcja zostanie dodana wkrótce!")
    
    st.markdown("""
    ### 🎯 Planowane funkcje:
    - 📊 Kalkulator CIT (19%)
    - 👤 Kalkulator PIT (17% / 32%)
    - 💡 Sugestie tax-loss harvesting
    - 📅 Optimal timing sprzedaży
    - 📄 Generator dokumentów (PIT-38)
    - 🧾 Tracking kosztów uzyskania przychodu
    """)


# =======================
# MAIN APP
# =======================

def main():
    # Inicjalizuj session state
    init_session_state()
    
    # Inicjalizuj Crypto Portfolio Manager (cache w session state)
    if CRYPTO_MANAGER_OK and 'crypto_manager' not in st.session_state:
        st.session_state.crypto_manager = CryptoPortfolioManager()
    
    # Aplikuj CSS
    apply_custom_css(st.session_state.theme)
    
    # Custom CSS dla kompaktowego menu
    st.markdown("""
        <style>
        /* Zmniejsz marginesy nagłówków h3 w sidebarze */
        [data-testid="stSidebar"] h3 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.3rem !important;
            font-size: 0.9rem !important;
        }
        /* Zmniejsz odstępy między przyciskami */
        [data-testid="stSidebar"] button {
            margin-bottom: 0.3rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">🏢 HORYZONT PARTNERÓW</div>', unsafe_allow_html=True)
    
    # Theme toggle w headerze
    col_header1, col_header2, col_header3 = st.columns([6, 1, 1])
    with col_header2:
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(theme_icon, help="Przełącz motyw", key="toggle_theme_btn"):
            # Przełącz motyw
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            
            # Zapisz preferencje
            preferences = {
                "theme": st.session_state.theme,
                "notifications_enabled": st.session_state.notifications_enabled,
                "cache_ttl": st.session_state.cache_ttl,
                "auto_refresh": st.session_state.auto_refresh,
                "refresh_interval": st.session_state.refresh_interval
            }
            save_user_preferences(preferences)
            
            st.rerun()
    with col_header3:
        if st.button("🔔", help="Powiadomienia", key="toggle_notifications_btn"):
            st.session_state.notifications_enabled = not st.session_state.notifications_enabled
            
            # Zapisz preferencje
            preferences = {
                "theme": st.session_state.theme,
                "notifications_enabled": st.session_state.notifications_enabled,
                "cache_ttl": st.session_state.cache_ttl,
                "auto_refresh": st.session_state.auto_refresh,
                "refresh_interval": st.session_state.refresh_interval
            }
            save_user_preferences(preferences)
            
            st.toast(f"Powiadomienia: {'✅ ON' if st.session_state.notifications_enabled else '❌ OFF'}")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.title("📋 Menu Główne")
        
        # Przycisk wylogowania
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🚪", key="logout_btn", help="Wyloguj się"):
                st.session_state["password_correct"] = False
                st.rerun()
        
        # Pobierz aktualną stronę (dla highlight)
        current_page = st.session_state.get('page', "📊 Dashboard")
        
        # Widget synchronizacji danych
        if PERSISTENT_OK:
            show_sync_widget()
            st.markdown("---")
        
        # Przycisk odświeżania
        if st.button("🔄 Odśwież Dane", width="stretch", key="refresh_data_btn"):
            st.cache_data.clear()
            # Wyczyść cache cen crypto żeby pobrać świeże przy następnym renderze
            if 'crypto_prices_cache' in st.session_state:
                del st.session_state.crypto_prices_cache
            if 'crypto_prices_symbols' in st.session_state:
                del st.session_state.crypto_prices_symbols
            st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 1: PRZEGLĄD ===
        st.markdown("### 📊 Przegląd")
        button_type_dashboard = "primary" if current_page == "📊 Dashboard" else "secondary"
        if st.button("📊 Dashboard", width="stretch", type=button_type_dashboard, key="nav_dashboard"):
            st.session_state.page = "📊 Dashboard"
            st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 2: FINANSE ===
        st.markdown("### 💰 Finanse")
        button_type_finanse = "primary" if current_page == "💳 Kredyty" else "secondary"
        if st.button("💳 Centrum Finansowe", width="stretch", type=button_type_finanse, key="nav_finanse"):
            st.session_state.page = "💳 Kredyty"
            st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 3: AI & STRATEGIA ===
        st.markdown("### 🤖 AI & Strategia")
        
        button_type_partnerzy = "primary" if current_page == "💬 Partnerzy" else "secondary"
        if st.button("💬 Partnerzy AI", width="stretch", type=button_type_partnerzy, key="nav_partnerzy"):
            st.session_state.page = "💬 Partnerzy"
            st.rerun()
        
        button_type_rozmowy = "primary" if current_page == "🗣️ Rozmowy Rady" else "secondary"
        if st.button("🗣️ Rozmowy Rady", width="stretch", type=button_type_rozmowy, key="nav_rozmowy"):
            st.session_state.page = "🗣️ Rozmowy Rady"
            st.rerun()
        
        button_type_powiadomienia = "primary" if current_page == "📧 Powiadomienia" else "secondary"
        if st.button("📧 Powiadomienia", width="stretch", type=button_type_powiadomienia, key="nav_powiadomienia"):
            st.session_state.page = "📧 Powiadomienia"
            st.rerun()
        
        button_type_konsultacje = "primary" if current_page == "🗳️ Konsultacje" else "secondary"
        if st.button("🗳️ Konsultacje", width="stretch", type=button_type_konsultacje, key="nav_konsultacje"):
            st.session_state.page = "🗳️ Konsultacje"
            st.rerun()
        
        button_type_kodeks = "primary" if current_page == "📜 Kodeks" else "secondary"
        if st.button("📜 Kodeks Spółki", width="stretch", type=button_type_kodeks, key="nav_kodeks"):
            st.session_state.page = "📜 Kodeks"
            st.rerun()
        
        button_type_alerty = "primary" if current_page == "🔔 Alerty" else "secondary"
        if st.button("🔔 Alerty i Notyfikacje", width="stretch", type=button_type_alerty, key="nav_alerty"):
            st.session_state.page = "🔔 Alerty"
            st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 4: ANALIZA ===
        st.markdown("### 📈 Analiza & Historia")
        
        col1, col2 = st.columns(2)
        with col1:
            button_type_analiza = "primary" if current_page == "📈 Analiza" else "secondary"
            if st.button("📈 Analiza", width="stretch", type=button_type_analiza, key="nav_analiza"):
                st.session_state.page = "📈 Analiza"
                st.rerun()
            
            button_type_timeline = "primary" if current_page == "🕐 Timeline" else "secondary"
            if st.button("🕐 Timeline", width="stretch", type=button_type_timeline, key="nav_timeline"):
                st.session_state.page = "🕐 Timeline"
                st.rerun()
        with col2:
            button_type_rynki = "primary" if current_page == "🌍 Rynki" else "secondary"
            if st.button("🌍 Rynki", width="stretch", type=button_type_rynki, key="nav_rynki"):
                st.session_state.page = "🌍 Rynki"
                st.rerun()
            
            button_type_snapshots = "primary" if current_page == "📸 Snapshots" else "secondary"
            if st.button("📸 Snapshots", width="stretch", type=button_type_snapshots, key="nav_snapshots"):
                st.session_state.page = "📸 Snapshots"
                st.rerun()
        
        st.markdown("")
        
        # === SEKCJA FINANSE PRO ===
        st.markdown("### 💼 Finanse PRO")
        
        col1, col2 = st.columns(2)
        with col1:
            button_type_transactions = "primary" if current_page == "📝 Transakcje" else "secondary"
            if st.button("📝 Transakcje", width="stretch", type=button_type_transactions, key="nav_transactions"):
                st.session_state.page = "📝 Transakcje"
                st.rerun()
            
            button_type_calendar = "primary" if current_page == "📅 Kalendarz" else "secondary"
            if st.button("📅 Kalendarz", width="stretch", type=button_type_calendar, key="nav_calendar"):
                st.session_state.page = "📅 Kalendarz"
                st.rerun()
        with col2:
            button_type_tax = "primary" if current_page == "🧮 Podatki" else "secondary"
            if st.button("🧮 Podatki", width="stretch", type=button_type_tax, key="nav_tax"):
                st.session_state.page = "🧮 Podatki"
                st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 5: NARZĘDZIA ===
        st.markdown("### 🛠️ Narzędzia")
        
        col1, col2 = st.columns(2)
        with col1:
            button_type_symulacje = "primary" if current_page == "🎮 Symulacje" else "secondary"
            if st.button("🎮 Symulacje", width="stretch", type=button_type_symulacje, key="nav_symulacje"):
                st.session_state.page = "🎮 Symulacje"
                st.rerun()
        with col2:
            button_type_ustawienia = "primary" if current_page == "⚙️ Ustawienia" else "secondary"
            if st.button("⚙️ Ustawienia", width="stretch", type=button_type_ustawienia, key="nav_ustawienia"):
                st.session_state.page = "⚙️ Ustawienia"
                st.rerun()
        
        st.markdown("")
        
        # Info o ostatniej aktualizacji
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    
    # Ładowanie danych
    if not IMPORTS_OK:
        st.error("⚠️ Nie można załadować modułów. Sprawdź czy gra_rpg.py działa poprawnie.")
        return
    
    with st.spinner("⏳ Ładuję dane portfela..."):
        stan_spolki, cele = load_portfolio_data()
    
    if stan_spolki is None:
        st.error("❌ Nie udało się załadować danych portfela")
        return
    
    # Pobierz aktualną stronę z session_state (domyślnie Dashboard)
    if 'page' not in st.session_state:
        st.session_state.page = "📊 Dashboard"
    
    page = st.session_state.page
    
    # Routing do odpowiedniej strony
    if page == "📊 Dashboard":
        show_dashboard(stan_spolki, cele)
    elif page == "💳 Kredyty":
        show_kredyty_page(stan_spolki, cele)
    elif page == "💬 Partnerzy":
        show_partners_page()
    elif page == "🗣️ Rozmowy Rady":
        show_autonomous_conversations_page()
    elif page == "📧 Powiadomienia":
        show_notifications_page()
    elif page == "🗳️ Konsultacje":
        show_consultations_page()
    elif page == "📜 Kodeks":
        show_kodeks_page()
    elif page == "🔔 Alerty":
        show_alerts_page()
    elif page == "📈 Analiza":
        show_analytics_page(stan_spolki)
    elif page == "🌍 Rynki":
        show_markets_page(stan_spolki, cele)
    elif page == "🕐 Timeline":
        show_timeline_page(stan_spolki)
    elif page == "📸 Snapshots":
        show_snapshots_page()
    elif page == "📝 Transakcje":
        show_transactions_page()
    elif page == "📅 Kalendarz":
        show_calendar_page()
    elif page == "🧮 Podatki":
        show_tax_optimizer_page()
    elif page == "🎮 Symulacje":
        show_simulations_page(stan_spolki)
    elif page == "⚙️ Ustawienia":
        show_settings_page()


def calculate_portfolio_health_score(stan_spolki, cele):
    """
    Oblicza Portfolio Health Score (0-100) bazując na kluczowych metrykach
    Returns: dict with 'score', 'grade', 'factors'
    """
    score = 0
    factors = {}
    
    try:
        # === FACTOR 1: Diversification (0-25 pts) ===
        liczba_pozycji = stan_spolki['akcje'].get('liczba_pozycji', 0) + stan_spolki['krypto'].get('liczba_pozycji', 0)
        
        if liczba_pozycji >= 20:
            diversification_score = 25
        elif liczba_pozycji >= 15:
            diversification_score = 20
        elif liczba_pozycji >= 10:
            diversification_score = 15
        elif liczba_pozycji >= 5:
            diversification_score = 10
        else:
            diversification_score = 5
        
        factors['diversification'] = {
            'score': diversification_score,
            'max': 25,
            'label': 'Dywersyfikacja',
            'detail': f"{liczba_pozycji} pozycji"
        }
        score += diversification_score
        
        # === FACTOR 2: Leverage Health (0-25 pts) ===
        rezerwa = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
        suma_aktywow = (
            stan_spolki['akcje'].get('wartosc_pln', 0) + 
            stan_spolki['krypto'].get('wartosc_pln', 0) +
            rezerwa
        )
        leverage = (get_suma_kredytow() / suma_aktywow * 100) if suma_aktywow > 0 else 0
        
        if leverage <= 10:
            leverage_score = 25
        elif leverage <= 20:
            leverage_score = 20
        elif leverage <= 30:
            leverage_score = 15
        elif leverage <= 40:
            leverage_score = 10
        else:
            leverage_score = 5
        
        factors['leverage'] = {
            'score': leverage_score,
            'max': 25,
            'label': 'Zdrowy Leverage',
            'detail': f"{leverage:.1f}%"
        }
        score += leverage_score
        
        # === FACTOR 3: Passive Income Coverage (0-30 pts) ===
        dywidendy_info = calculate_portfolio_dividends(stan_spolki)
        krypto_holdings = load_krypto()
        crypto_apy_score = {'miesieczne_pln': 0}
        
        if krypto_holdings and CRYPTO_MANAGER_OK:
            try:
                symbols = list(set(k['symbol'] for k in krypto_holdings))
                current_prices = get_cached_crypto_prices(symbols)
                kurs_usd = float(stan_spolki.get('kurs_usd', DEFAULT_USD_PLN_RATE))
                crypto_apy_score = calculate_crypto_apy_earnings(krypto_holdings, current_prices, kurs_usd)
            except:
                pass
        
        passive_income = dywidendy_info['miesieczna_kwota_pln'] + crypto_apy_score['miesieczne_pln']
        wydatki_stale = get_suma_wydatkow_stalych()
        kredyty = load_kredyty()
        raty = sum(k['rata_miesieczna'] for k in kredyty)
        total_wydatki = wydatki_stale + raty
        
        coverage = (passive_income / total_wydatki * 100) if total_wydatki > 0 else 0
        
        if coverage >= 100:
            passive_score = 30
        elif coverage >= 75:
            passive_score = 25
        elif coverage >= 50:
            passive_score = 20
        elif coverage >= 25:
            passive_score = 15
        elif coverage >= 10:
            passive_score = 10
        else:
            passive_score = 5
        
        factors['passive_income'] = {
            'score': passive_score,
            'max': 30,
            'label': 'Pokrycie Wydatków',
            'detail': f"{coverage:.0f}% ({passive_income:.0f}/{total_wydatki:.0f} PLN)"
        }
        score += passive_score
        
        # === FACTOR 4: Portfolio Balance (0-20 pts) ===
        # Sprawdź czy jest balans między akcjami a krypto
        akcje_val = stan_spolki['akcje'].get('wartosc_pln', 0)
        krypto_val = stan_spolki['krypto'].get('wartosc_pln', 0)
        total_val = akcje_val + krypto_val
        
        if total_val > 0:
            akcje_pct = (akcje_val / total_val * 100)
            # Optymalne: 70-90% akcje, 10-30% krypto
            if 70 <= akcje_pct <= 90:
                balance_score = 20
            elif 60 <= akcje_pct <= 95:
                balance_score = 15
            elif 50 <= akcje_pct <= 98:
                balance_score = 10
            else:
                balance_score = 5
        else:
            balance_score = 0
        
        factors['balance'] = {
            'score': balance_score,
            'max': 20,
            'label': 'Balans Portfela',
            'detail': f"{akcje_pct:.0f}% akcje, {100-akcje_pct:.0f}% krypto"
        }
        score += balance_score
        
        # === DETERMINE GRADE ===
        if score >= 90:
            grade = "A+"
            emoji = "🏆"
            status = "Doskonały"
        elif score >= 80:
            grade = "A"
            emoji = "🌟"
            status = "Bardzo dobry"
        elif score >= 70:
            grade = "B+"
            emoji = "✅"
            status = "Dobry"
        elif score >= 60:
            grade = "B"
            emoji = "👍"
            status = "Zadowalający"
        elif score >= 50:
            grade = "C"
            emoji = "⚠️"
            status = "Przeciętny"
        else:
            grade = "D"
            emoji = "❌"
            status = "Wymaga poprawy"
        
        return {
            'score': score,
            'grade': grade,
            'emoji': emoji,
            'status': status,
            'factors': factors
        }
        
    except Exception as e:
        # Return default low score on error
        return {
            'score': 0,
            'grade': 'N/A',
            'emoji': '❓',
            'status': 'Błąd obliczenia',
            'factors': {}
        }

def show_dashboard(stan_spolki, cele):
    """Główny dashboard"""
    
    # Sprawdź czy dane są dostępne
    if not stan_spolki:
        st.error("❌ Nie można załadować danych portfela")
        st.info("💡 Sprawdź czy główny program działa poprawnie")
        return
    
    # Sprawdź strukturę danych
    required_keys = ['akcje', 'krypto', 'dlugi', 'wyplata']
    missing_keys = [k for k in required_keys if k not in stan_spolki]
    
    if missing_keys:
        st.error(f"❌ Brak wymaganych danych: {', '.join(missing_keys)}")
        st.json(stan_spolki)  # Pokaż co mamy
        return
    
    # === HEADER Z TIMESTAMP ===
    col_title, col_timestamp = st.columns([3, 1])
    with col_title:
        st.title("📊 Dashboard Portfela")
    with col_timestamp:
        deltas = calculate_portfolio_deltas(stan_spolki, cele)
        st.caption(f"🕐 Ostatnia aktualizacja:")
        st.caption(f"**{deltas['last_update']}**")
    
    st.markdown("---")
    
    # === PORTFOLIO HEALTH SCORE ===
    health = calculate_portfolio_health_score(stan_spolki, cele)
    
    col_health1, col_health2, col_health3 = st.columns([1, 2, 1])
    
    with col_health1:
        st.metric(
            label="🏥 Portfolio Health Score",
            value=f"{health['score']}/100",
            delta=f"Ocena: {health['grade']}",
            help="Kompleksowa ocena zdrowia portfela: dywersyfikacja, leverage, pokrycie wydatków, balans"
        )
    
    with col_health2:
        st.progress(health['score'] / 100)
        st.caption(f"{health['emoji']} **Status:** {health['status']}")
        
        # Pokaż breakdown w expander
        with st.expander("📊 Szczegóły punktacji", expanded=False):
            for factor_name, factor_data in health['factors'].items():
                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    st.caption(f"**{factor_data['label']}:** {factor_data['detail']}")
                with col_f2:
                    st.caption(f"{factor_data['score']}/{factor_data['max']} pkt")
    
    with col_health3:
        # Rekomendacja bazowana na najsłabszym faktore
        if health['factors']:
            weakest_factor = min(health['factors'].items(), key=lambda x: x[1]['score'] / x[1]['max'])
            st.caption("💡 **Popraw:**")
            st.caption(weakest_factor[1]['label'])
    
    st.markdown("---")
    
    # Metryki główne
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            rezerwa = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
            wartosc_netto = (
                stan_spolki['akcje'].get('wartosc_pln', 0) + 
                stan_spolki['krypto'].get('wartosc_pln', 0) +
                rezerwa -  # Rezerwa gotówkowa z cele.json
                get_suma_kredytow()  # Z kredyty.json
            )
            st.metric(
                label="💼 Wartość Netto",
                value=format_currency(wartosc_netto),
                delta=deltas['wartosc_netto_delta'],
                help="Akcje + Krypto + Rezerwa Gotówkowa - Zobowiązania (zmiana z ostatniego tygodnia)"
            )
        except Exception as e:
            st.error(f"Błąd metryki wartość netto: {e}")
    
    with col2:
        try:
            rezerwa_suma = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
            suma_aktywow = (
                stan_spolki['akcje'].get('wartosc_pln', 0) + 
                stan_spolki['krypto'].get('wartosc_pln', 0) +
                rezerwa_suma  # Dodajemy rezerwę do sumy aktywów
            )
            leverage = (get_suma_kredytow() / suma_aktywow * 100) if suma_aktywow > 0 else 0  # Z kredyty.json
            st.metric(
                label="📈 Leverage",
                value=f"{leverage:.2f}%",
                delta=deltas['leverage_delta'],
                help="Zobowiązania / Aktywa (zmiana w punktach procentowych)"
            )
        except Exception as e:
            st.error(f"Błąd metryki leverage: {e}")
    
    with col3:
        try:
            liczba_pozycji = (
                stan_spolki['akcje'].get('liczba_pozycji', 0) + 
                stan_spolki['krypto'].get('liczba_pozycji', 0)
            )
            st.metric(
                label="🎯 Pozycje",
                value=f"{liczba_pozycji} aktywa",
                delta=deltas['pozycje_delta'],
                help="Łączna liczba pozycji w portfelu (zmiana z ostatniego tygodnia)"
            )
        except Exception as e:
            st.error(f"Błąd metryki pozycje: {e}")
    
    with col4:
        try:
            # Oblicz dokładne dywidendy z portfela (NETTO po 19% podatku)
            dywidendy_info = calculate_portfolio_dividends(stan_spolki)
            
            dochod_pasywny_netto = dywidendy_info['miesieczna_kwota_pln']
            liczba_spolek = dywidendy_info['liczba_spolek_z_dywidendami']
            roczna_netto = dywidendy_info['roczna_kwota_pln']
            
            # === FEATURE #2: Dodaj crypto APY earnings ===
            krypto_holdings = load_krypto()
            crypto_apy = {'miesieczne_pln': 0, 'roczne_pln': 0, 'liczba_earning_positions': 0}
            
            if krypto_holdings and CRYPTO_MANAGER_OK:
                try:
                    # Pobierz aktualne ceny z cache (bez spamowania API)
                    symbols = list(set(k['symbol'] for k in krypto_holdings))
                    current_prices_for_apy = get_cached_crypto_prices(symbols)
                    
                    # Pobierz kurs USD (bezpieczne pobieranie)
                    try:
                        kurs_usd = float(stan_spolki.get('kurs_usd', DEFAULT_USD_PLN_RATE))
                    except (TypeError, ValueError, AttributeError):
                        kurs_usd = DEFAULT_USD_PLN_RATE  # Fallback
                    
                    # Oblicz APY earnings
                    crypto_apy = calculate_crypto_apy_earnings(
                        krypto_holdings, 
                        current_prices_for_apy,
                        kurs_usd=kurs_usd
                    )
                except Exception as e:
                    pass  # Cicho ignoruj błędy - używamy fallback values
            
            # Łączny dochód pasywny: dywidendy + crypto APY
            total_passive_income = dochod_pasywny_netto + crypto_apy['miesieczne_pln']
            total_passive_roczny = roczna_netto + crypto_apy['roczne_pln']
            
            # Build help text
            help_parts = []
            if liczba_spolek > 0:
                help_parts.append(f"📈 Dywidendy: {dochod_pasywny_netto:.0f} PLN/mies z {liczba_spolek} spółek ({roczna_netto:.0f} PLN/rok)")
            if crypto_apy['liczba_earning_positions'] > 0:
                help_parts.append(f"₿ Crypto APY: {crypto_apy['miesieczne_pln']:.0f} PLN/mies z {crypto_apy['liczba_earning_positions']} pozycji ({crypto_apy['roczne_pln']:.0f} PLN/rok)")
            help_parts.append(f"💰 RAZEM: {total_passive_roczny:.0f} PLN/rok")
            
            help_text = "\n".join(help_parts) if help_parts else "Brak dochodu pasywnego"
            
            st.metric(
                label="💰 Dochód Pasywny (NETTO)",
                value=f"{total_passive_income:.0f} PLN/mies",
                delta=f"+{crypto_apy['miesieczne_pln']:.0f} z crypto" if crypto_apy['miesieczne_pln'] > 0 else None,
                help=help_text
            )
        except Exception as e:
            st.error(f"Błąd metryki dochód pasywny: {e}")
    
    st.markdown("---")
    
    # === CASH FLOW OVERVIEW ===
    st.markdown("### 💸 Cash Flow Overview")
    
    # Load financial data
    wyplaty_cf = load_wyplaty()
    wydatki_cf = load_wydatki()
    kredyty_cf = load_kredyty()
    
    if wyplaty_cf:
        ostatnia_wyplata_cf = wyplaty_cf[0]['kwota']
        wydatki_stale_cf = get_suma_wydatkow_stalych(wydatki_cf)
        raty_cf = sum(k['rata_miesieczna'] for k in kredyty_cf)
        wydatki_total_cf = wydatki_stale_cf + raty_cf
        
        nadwyzka = ostatnia_wyplata_cf - wydatki_total_cf
        procent_oszczednosci = (nadwyzka / ostatnia_wyplata_cf * 100) if ostatnia_wyplata_cf > 0 else 0
        
        # Three-column metrics
        col_cf1, col_cf2, col_cf3 = st.columns(3)
        
        with col_cf1:
            st.metric(
                "💰 Ostatnia Wypłata", 
                f"{ostatnia_wyplata_cf:.0f} PLN",
                help=f"📅 Data: {wyplaty_cf[0]['data']}"
            )
        
        with col_cf2:
            st.metric(
                "📊 Wydatki Miesięczne", 
                f"{wydatki_total_cf:.0f} PLN",
                help=f"Stałe: {wydatki_stale_cf:.0f} PLN | Raty: {raty_cf:.0f} PLN"
            )
        
        with col_cf3:
            if nadwyzka >= 0:
                st.metric(
                    "✅ Nadwyżka", 
                    f"{nadwyzka:.0f} PLN",
                    delta=f"{procent_oszczednosci:.1f}% oszczędności",
                    delta_color="normal"
                )
            else:
                st.metric(
                    "⚠️ Deficyt", 
                    f"{nadwyzka:.0f} PLN",
                    delta=f"{procent_oszczednosci:.1f}% deficytu",
                    delta_color="inverse"
                )
        
        # Visual expense gauge
        if ostatnia_wyplata_cf > 0:
            wydatki_procent = min((wydatki_total_cf / ostatnia_wyplata_cf), 1.0)
            
            # Color-coded progress bar
            col_gauge_label, col_gauge_bar = st.columns([1, 5])
            with col_gauge_label:
                st.caption("**Wykorzystanie:**")
            with col_gauge_bar:
                st.progress(wydatki_procent)
                st.caption(f"{wydatki_procent*100:.1f}% wypłaty pokrywa wydatki")
            
            # Status message
            if nadwyzka > 0:
                st.success(f"✅ Miesięczna nadwyżka: **{nadwyzka:.0f} PLN** ({procent_oszczednosci:.1f}%)")
            elif nadwyzka < 0:
                st.error(f"⚠️ Miesięczny deficyt: **{abs(nadwyzka):.0f} PLN** - Wydatki przekraczają wypłatę!")
            else:
                st.warning("⚖️ Bilans zerowy - wydatki równają się wypłacie")
    else:
        st.info("ℹ️ Dodaj wypłaty w zakładce '💳 Kredyty → Wypłaty' aby zobaczyć analizę Cash Flow.")
    
    st.markdown("---")
    
    # === QUICK ACTIONS PANEL ===
    st.markdown("### ⚡ Szybkie Akcje")
    
    col_action1, col_action2, col_action3, col_action4 = st.columns(4)
    
    with col_action1:
        if st.button("🤖 Zapytaj AI o Portfel", use_container_width=True, key="quick_ai"):
            st.session_state.page = "💬 Partnerzy"
            st.session_state.quick_question = "Jak oceniasz mój obecny portfel? Jakie widzisz ryzyka i szanse?"
            st.rerun()
    
    with col_action2:
        if st.button("📊 Szczegółowa Analiza", use_container_width=True, key="quick_analiza"):
            st.session_state.page = "📈 Analiza"
            st.rerun()
    
    with col_action3:
        if st.button("📄 Generuj Raport Excel", use_container_width=True, key="quick_raport"):
            try:
                with st.spinner("📊 Generuję raport..."):
                    filename = generate_full_report(stan_spolki)
                    
                    with open(filename, "rb") as file:
                        st.download_button(
                            label="⬇️ Pobierz raport",
                            data=file,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key="download_raport"
                        )
                    st.success(f"✅ Raport wygenerowany: {filename}")
            except Exception as e:
                st.error(f"❌ Błąd generowania raportu: {e}")
    
    with col_action4:
        if st.button("💳 Zarządzaj Finansami", use_container_width=True, key="quick_finanse"):
            st.session_state.page = "💳 Kredyty"
            st.rerun()
    
    st.markdown("---")
    
    # === OPTIMIZED ALERTS DISPLAY ===
    st.markdown("### 🚨 Alerty Portfela")
    
    alerts = check_portfolio_alerts(stan_spolki, cele)
    
    if alerts:
        # Grupuj alerty po severity
        critical_alerts = [a for a in alerts if a["severity"] == "critical"]
        warning_alerts = [a for a in alerts if a["severity"] == "warning"]
        success_alerts = [a for a in alerts if a["severity"] == "success"]
        info_alerts = [a for a in alerts if a["severity"] == "info"]
        
        # Pokaż TOP 3 critical/warning bezpośrednio
        priority_alerts = critical_alerts + warning_alerts
        top_alerts = priority_alerts[:3]
        remaining_alerts = priority_alerts[3:]
        
        # Wyświetl TOP 3
        for alert in top_alerts:
            if alert["severity"] == "critical":
                st.error(f"**{alert['title']}**\n\n{alert['message']}")
            else:
                st.warning(f"**{alert['title']}**\n\n{alert['message']}")
            
            if alert.get('action'):
                st.caption(f"💡 *Rekomendacja: {alert['action']}*")
        
        # Reszta w expanderze
        if remaining_alerts:
            with st.expander(f"⚠️ Pokaż pozostałe alerty ({len(remaining_alerts)})", expanded=False):
                for alert in remaining_alerts:
                    if alert["severity"] == "critical":
                        st.error(f"**{alert['title']}**\n\n{alert['message']}")
                    else:
                        st.warning(f"**{alert['title']}**\n\n{alert['message']}")
                    
                    if alert.get('action'):
                        st.caption(f"💡 *Rekomendacja: {alert['action']}*")
        
        # Success/Info zawsze w expanderze
        if success_alerts or info_alerts:
            with st.expander(f"✅ Informacje pozytywne ({len(success_alerts + info_alerts)})", expanded=False):
                for alert in success_alerts:
                    st.success(f"**{alert['title']}**\n\n{alert['message']}")
                for alert in info_alerts:
                    st.info(f"**{alert['title']}**\n\n{alert['message']}")
    else:
        st.success("✅ **Brak aktywnych alertów** - Twój portfel wygląda stabilnie!")
        st.caption("System monitoruje: duże spadki/wzrosty, wysokie P/E, dźwignię, koncentrację i cele finansowe.")
    
    st.markdown("---")
    
    # === CODZIENNA RADA OD AI PARTNERA ===
    st.markdown("### 💡 Dzienna Rada od Eksperta")
    
    with st.spinner("Losowanie dzisiejszego doradcy..."):
        try:
            daily_tip = get_daily_advisor_tip(stan_spolki, cele)
            
            st.info(f"""
**{daily_tip['partner_icon']} {daily_tip['partner_name']} mówi:**

_{daily_tip['tip_text']}_
            """)
            
            st.caption(f"💬 Każdy dzień inny ekspert! Jutro ktoś inny podzieli się swoją mądrością.")
            
        except Exception as e:
            st.warning(f"⚠️ Nie udało się pobrać dzisiejszej rady: {str(e)[:100]}")
    
    st.markdown("---")
    
    # Wykresy
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_portfolio_value_chart(stan_spolki, cele)
        st.plotly_chart(fig, config={'displayModeBar': False})
    
    with col2:
        fig = create_allocation_pie_chart(stan_spolki, cele)
        st.plotly_chart(fig, config={'displayModeBar': False})
    
    st.markdown("---")
    
    # === ANALIZA DYWIDEND ===
    with st.expander("💰 Szczegółowa Analiza Dywidend", expanded=False):
        try:
            dywidendy_info = calculate_portfolio_dividends(stan_spolki)
            
            if dywidendy_info['liczba_spolek_z_dywidendami'] > 0:
                # Info o podatku
                st.info(f"📋 **Kwoty NETTO** (po odjęciu 19% podatku Belki: {dywidendy_info.get('podatek_pln', 0):.2f} PLN/rok)")
                
                col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                
                with col_d1:
                    st.metric(
                        "Miesięcznie (NETTO)",
                        f"{dywidendy_info['miesieczna_kwota_pln']:.2f} PLN",
                        help="Miesięczny dochód po 19% podatku"
                    )
                
                with col_d2:
                    st.metric(
                        "Rocznie (NETTO)",
                        f"{dywidendy_info['roczna_kwota_pln']:.2f} PLN",
                        help="Roczny dochód po 19% podatku"
                    )
                
                with col_d3:
                    st.metric(
                        "Rocznie (BRUTTO)",
                        f"{dywidendy_info.get('roczna_kwota_pln_brutto', 0):.2f} PLN",
                        help="Roczny dochód przed opodatkowaniem"
                    )
                
                with col_d4:
                    st.metric(
                        "Spółki z dywidendami",
                        dywidendy_info['liczba_spolek_z_dywidendami'],
                        help="Liczba spółek wypłacających dywidendy"
                    )
                
                st.markdown("**TOP 10 Największych Płatników Dywidend:**")
                
                # Przygotuj tabelę
                df_div = pd.DataFrame(dywidendy_info['szczegoly'][:10])
                if not df_div.empty:
                    df_div_display = df_div[['ticker', 'ilosc', 'dividend_rate', 'dividend_yield', 'roczna_kwota_pln']].copy()
                    df_div_display.columns = ['Ticker', 'Ilość akcji', 'Dywidenda/akcję ($)', 'Yield (%)', 'Roczna NETTO (PLN)']
                    
                    # Format
                    df_div_display['Ilość akcji'] = df_div_display['Ilość akcji'].apply(lambda x: f"{x:.2f}")
                    df_div_display['Dywidenda/akcję ($)'] = df_div_display['Dywidenda/akcję ($)'].apply(lambda x: f"${x:.2f}")
                    df_div_display['Yield (%)'] = df_div_display['Yield (%)'].apply(lambda x: f"{x:.2f}%")
                    df_div_display['Roczna NETTO (PLN)'] = df_div_display['Roczna NETTO (PLN)'].apply(lambda x: f"{x:.2f}")
                    
                    st.dataframe(df_div_display, width="stretch", hide_index=True)
                    
                    st.caption(f"💡 Kwoty NETTO po odjęciu 19% podatku Belki. Dane pochodzą z Yahoo Finance - rzeczywiste wypłaty mogą się różnić.")
            else:
                st.info("ℹ️ Brak spółek wypłacających dywidendy w portfelu lub brak danych o dywidendach.")
                
        except Exception as e:
            st.error(f"Błąd analizy dywidend: {e}")
    
    st.markdown("---")
    
    # Progress bars celów
    st.subheader("🎯 Progres Celów Strategicznych")
    
    # Załaduj dane raz na początku
    kredyty_dash = load_kredyty()
    wyplaty_dash = load_wyplaty()
    wydatki_dash = load_wydatki()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 💳 Kredyty")
        if kredyty_dash:
            suma_pozostala = sum(k['kwota_poczatkowa'] - k['splacono'] for k in kredyty_dash)
            suma_splacona = sum(k['splacono'] for k in kredyty_dash)
            suma_poczatkowa = sum(k['kwota_poczatkowa'] for k in kredyty_dash)
            progress_kredyty = suma_splacona / suma_poczatkowa if suma_poczatkowa > 0 else 0
            
            st.progress(progress_kredyty)
            st.caption(f"Spłacono: {format_currency(suma_splacona)} / {format_currency(suma_poczatkowa)}")
            st.caption(f"Pozostało: {format_currency(suma_pozostala)}")
        else:
            st.caption("Brak dodanych kredytów")
        
        # Przycisk do szczegółów kredytów
        if st.button("📋 Szczegóły Kredytów", key="goto_kredyty_dash"):
            st.session_state['goto_page'] = "💳 Kredyty"
            st.rerun()
        
        st.markdown("##### � Wypłaty")
        if wyplaty_dash:
            ostatnia_wyplata = wyplaty_dash[0]
            srednia_wyplata = get_srednia_wyplata(3, wyplaty_dash)
            
            st.metric("Ostatnia wypłata", f"{ostatnia_wyplata['kwota']:.0f} PLN")
            st.caption(f"📅 Data: {ostatnia_wyplata['data']}")
            st.caption(f"📊 Średnia (3 mies.): {srednia_wyplata:.0f} PLN")
        else:
            st.caption("Brak danych o wypłatach")
        
        # Przycisk do szczegółów wypłat
        if st.button("📋 Historia Wypłat", key="goto_wyplaty_dash"):
            st.session_state['goto_page'] = "💳 Kredyty"
            st.session_state['active_tab'] = 3  # TAB 4 (indeks 3)
            st.rerun()
    
    with col2:
        st.markdown("##### � Rezerwa gotówkowa")
        rezerwa_current = cele.get('Rezerwa_gotowkowa_obecna_PLN', 39904) if cele else 39904
        rezerwa_target = cele.get('Rezerwa_gotowkowa_PLN', 70000) if cele else 70000
        progress_rezerwa = rezerwa_current / rezerwa_target if rezerwa_target > 0 else 0
        st.progress(min(progress_rezerwa, 1.0))
        st.caption(f"Zgromadzone: {format_currency(rezerwa_current)} / {format_currency(rezerwa_target)}")
        
        st.markdown("##### 📋 Wydatki Miesięczne")
        wydatki_stale = get_suma_wydatkow_stalych(wydatki_dash)
        raty_miesieczne = sum(k['rata_miesieczna'] for k in kredyty_dash)
        wydatki_total = wydatki_stale + raty_miesieczne
        
        st.metric("Wydatki stałe", f"{wydatki_stale:.0f} PLN")
        st.caption(f"Raty kredytów: {raty_miesieczne:.0f} PLN")
        st.caption(f"**Total: {wydatki_total:.0f} PLN/mies**")
        
        # Przycisk do szczegółów
        if st.button("📋 Zarządzaj Wydatkami", key="goto_wydatki_dash"):
            st.session_state['goto_page'] = "💳 Kredyty"
            st.session_state['active_tab'] = 4  # TAB 5 (indeks 4)
            st.rerun()
        
        st.markdown("##### 🏖️ Financial Independence (FIRE Analysis)")
        
        # === OBLICZ PEŁNY DOCHÓD PASYWNY (Dywidendy + Crypto APY) ===
        dywidendy_info = calculate_portfolio_dividends(stan_spolki)
        fi_dochod_dywidendy = dywidendy_info['miesieczna_kwota_pln']  # NETTO po 19% podatku
        
        # Dodaj crypto APY
        krypto_holdings_fi = load_krypto()
        crypto_apy_fi = {'miesieczne_pln': 0, 'roczne_pln': 0}
        
        if krypto_holdings_fi and CRYPTO_MANAGER_OK:
            try:
                symbols_fi = list(set(k['symbol'] for k in krypto_holdings_fi))
                current_prices_fi = get_cached_crypto_prices(symbols_fi)
                
                try:
                    kurs_usd_fi = float(stan_spolki.get('kurs_usd', DEFAULT_USD_PLN_RATE))
                except (TypeError, ValueError, AttributeError):
                    kurs_usd_fi = DEFAULT_USD_PLN_RATE
                
                crypto_apy_fi = calculate_crypto_apy_earnings(
                    krypto_holdings_fi, 
                    current_prices_fi,
                    kurs_usd=kurs_usd_fi
                )
            except Exception as e:
                # Błąd przy obliczaniu crypto APY - użyj 0
                crypto_apy_fi = {'miesieczne_pln': 0}
        
        fi_dochod = fi_dochod_dywidendy + crypto_apy_fi['miesieczne_pln']  # TOTAL passive income
        fi_wydatki = wydatki_total  # Z wydatki.json + raty kredytów
        
        # === FI NUMBER (ile potrzebujesz by być FI) ===
        # 4% Rule: FI Number = Roczne wydatki × 25
        fi_number = fi_wydatki * 12 * 25  # Miesięczne wydatki × 12 × 25
        
        # Aktualna wartość netto (akcje + crypto + rezerwa - długi)
        rezerwa_fi = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
        wartosc_netto_fi = (
            stan_spolki['akcje'].get('wartosc_pln', 0) + 
            stan_spolki['krypto'].get('wartosc_pln', 0) +
            rezerwa_fi -
            get_suma_kredytow()
        )
        
        # === PROGRESS & METRICS ===
        col_fi1, col_fi2, col_fi3 = st.columns(3)
        
        with col_fi1:
            progress_fi = fi_dochod / fi_wydatki if fi_wydatki > 0 else 0
            procent_fi = (fi_dochod / fi_wydatki * 100) if fi_wydatki > 0 else 0
            
            st.metric(
                "🎯 FI Progress (Dochód/Wydatki)",
                f"{procent_fi:.1f}%",
                delta=f"{fi_dochod:.0f}/{fi_wydatki:.0f} PLN/mies"
            )
            st.progress(min(progress_fi, 1.0))
            
            if procent_fi >= 100:
                st.success("🎉 **Gratulacje! Jesteś Financially Independent!**")
            elif procent_fi >= 75:
                st.info(f"🚀 Blisko! Brakuje {fi_wydatki - fi_dochod:.0f} PLN/mies")
            elif procent_fi >= 50:
                st.warning(f"💪 W połowie drogi! Brakuje {fi_wydatki - fi_dochod:.0f} PLN/mies")
            else:
                st.caption(f"📊 Brakuje {fi_wydatki - fi_dochod:.0f} PLN/mies do FI")
        
        with col_fi2:
            progress_fi_number = (wartosc_netto_fi / fi_number) if fi_number > 0 else 0
            procent_fi_number = (wartosc_netto_fi / fi_number * 100) if fi_number > 0 else 0
            
            st.metric(
                "💰 FI Number Progress (4% Rule)",
                f"{procent_fi_number:.1f}%",
                delta=f"{wartosc_netto_fi:.0f}/{fi_number:.0f} PLN"
            )
            st.progress(min(progress_fi_number, 1.0))
            
            if procent_fi_number >= 100:
                st.success("🎊 **FI Number osiągnięty!**")
            else:
                st.caption(f"💎 Brakuje {fi_number - wartosc_netto_fi:.0f} PLN do FI Number")
        
        with col_fi3:
            # Time to FI (ile lat do osiągnięcia przy obecnym tempie)
            # Wykorzystaj już załadowane dane
            if 'wyplaty_dash' in locals():
                wyplaty_fi = wyplaty_dash
            else:
                wyplaty_fi = load_wyplaty()
                
            if wyplaty_fi and len(wyplaty_fi) > 0:
                ostatnia_wyplata_fi = wyplaty_fi[0]['kwota']
                miesieczne_inwestycje = ostatnia_wyplata_fi - wydatki_total
                
                if miesieczne_inwestycje > 0 and fi_number > wartosc_netto_fi:
                    brakujaca_kwota = fi_number - wartosc_netto_fi
                    # Uproszczony model: brakująca kwota / miesięczne inwestycje
                    # (zakładamy 0% zwrotu - konserwatywnie)
                    miesiace_do_fi = brakujaca_kwota / miesieczne_inwestycje
                    lata_do_fi = miesiace_do_fi / 12
                    
                    st.metric(
                        "⏱️ Time to FI (lata)",
                        f"{lata_do_fi:.1f} lat",
                        delta=f"{miesieczne_inwestycje:.0f} PLN/mies inwestycji"
                    )
                    
                    rok_fi = 2025 + int(lata_do_fi)
                    st.caption(f"📅 Przewidywany rok FI: {rok_fi}")
                else:
                    st.metric("⏱️ Time to FI", "OSIĄGNIĘTE! 🎉")
        
        # === BREAKDOWN DOCHODU PASYWNEGO ===
        with st.expander("📊 Breakdown Dochodu Pasywnego", expanded=False):
            col_b1, col_b2, col_b3 = st.columns(3)
            
            with col_b1:
                # Get dividend trend indicator
                div_trend = get_dividend_trend_indicator(dywidendy_info)
                
                st.metric("📈 Dywidendy (NETTO)", f"{fi_dochod_dywidendy:.0f} PLN/mies")
                st.caption(f"{dywidendy_info['roczna_kwota_pln']:.0f} PLN/rok z {dywidendy_info['liczba_spolek_z_dywidendami']} spółek")
                
                # Mini trend indicator
                if dywidendy_info['liczba_spolek_z_dywidendami'] > 0:
                    avg_div_per_stock = fi_dochod_dywidendy / dywidendy_info['liczba_spolek_z_dywidendami']
                    
                    # Color-coded trend badge
                    if div_trend['trend_color'] == 'green':
                        st.success(f"{div_trend['trend_emoji']} {div_trend['trend_text']} • {avg_div_per_stock:.0f} PLN/spółka")
                    elif div_trend['trend_color'] == 'blue':
                        st.info(f"{div_trend['trend_emoji']} {div_trend['trend_text']} • {avg_div_per_stock:.0f} PLN/spółka")
                    else:
                        st.warning(f"{div_trend['trend_emoji']} {div_trend['trend_text']} • {avg_div_per_stock:.0f} PLN/spółka")
            
            with col_b2:
                st.metric("₿ Crypto APY", f"{crypto_apy_fi['miesieczne_pln']:.0f} PLN/mies")
                st.caption(f"{crypto_apy_fi['roczne_pln']:.0f} PLN/rok")
            
            with col_b3:
                total_passive_year = (fi_dochod_dywidendy + crypto_apy_fi['miesieczne_pln']) * 12
                st.metric("💰 RAZEM Rocznie", f"{total_passive_year:.0f} PLN/rok")
                st.caption(f"{fi_dochod:.0f} PLN/mies")
        
        # === 4% RULE EXPLANATION ===
        with st.expander("ℹ️ Co to jest FI Number (4% Rule)?", expanded=False):
            st.markdown("""
            **4% Rule** to klasyczna zasada FIRE (Financial Independence, Retire Early):
            
            - **FI Number = Roczne wydatki × 25**
            - Zakłada że możesz bezpiecznie wypłacać 4% rocznie z portfela bez wyczerpania kapitału
            - Bazuje na badaniach Trinity Study (1998)
            
            **Twoje dane:**
            - 📊 Miesięczne wydatki: {wydatki:.0f} PLN
            - 📅 Roczne wydatki: {roczne:.0f} PLN
            - 💰 **FI Number (x25): {fi_num:.0f} PLN**
            
            **Kiedy osiągniesz FI Number:**
            - Możesz żyć z 4% zwrotu portfela (bez pracy!)
            - Twój kapitał będzie rósł szybciej niż go wydajesz
            - Financial Independence = Wolność wyboru! 🏖️
            """.format(
                wydatki=fi_wydatki,
                roczne=fi_wydatki * 12,
                fi_num=fi_number
            ))
    
    st.markdown("---")
    
    # Top Holdings
    st.subheader("📊 Top Holdings")
    
    # Pobierz prawdziwe dane z portfela
    try:
        akcje_pozycje = []
        total_value = stan_spolki.get('podsumowanie', {}).get('Wartosc_netto_PLN', 0)
        kurs_usd = stan_spolki.get('kurs_usd_pln', 3.6)
        
        if 'akcje' in stan_spolki and 'pozycje' in stan_spolki['akcje']:
            for ticker, data in stan_spolki['akcje']['pozycje'].items():
                if isinstance(data, dict):
                    wartosc_usd = data.get('wartosc_total_usd', 0)
                    wartosc_pln = wartosc_usd * kurs_usd
                    waga = (wartosc_pln / total_value * 100) if total_value > 0 else 0
                    
                    akcje_pozycje.append({
                        'Ticker': ticker,
                        'Wartość (PLN)': wartosc_pln,
                        'Zmiana (%)': data.get('zmiana_proc', 0),
                        'Waga (%)': waga,
                        'Typ': 'Akcja/ETF'
                    })
        
        krypto_pozycje = []
        if 'krypto' in stan_spolki and 'pozycje' in stan_spolki['krypto']:
            for ticker, data in stan_spolki['krypto']['pozycje'].items():
                if isinstance(data, dict):
                    wartosc_pln = data.get('wartosc_pln', 0)
                    waga = (wartosc_pln / total_value * 100) if total_value > 0 else 0
                    
                    krypto_pozycje.append({
                        'Ticker': ticker,
                        'Wartość (PLN)': wartosc_pln,
                        'Zmiana (%)': data.get('zmiana_24h', 0),  # Krypto może mieć zmiana_24h
                        'Waga (%)': waga,
                        'Typ': 'Crypto'
                    })
        
        # Combine and sort
        all_holdings = akcje_pozycje + krypto_pozycje
        
        # Filtruj pozycje z wartością > 0
        all_holdings = [h for h in all_holdings if h['Wartość (PLN)'] > 0]
        
        all_holdings = sorted(all_holdings, key=lambda x: x['Wartość (PLN)'], reverse=True)
        
        if all_holdings:
            df = pd.DataFrame(all_holdings[:10])  # Top 10
            
            # Format values
            df['Wartość (PLN)'] = df['Wartość (PLN)'].apply(lambda x: f"{x:,.2f}")
            df['Zmiana (%)'] = df['Zmiana (%)'].apply(lambda x: f"{x:+.2f}")
            df['Waga (%)'] = df['Waga (%)'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.warning("⚠️ Brak danych o pozycjach")
    
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        # Fallback to mock data if real data fails
        holdings_data = {
            'Ticker': ['AAPL', 'MSFT', 'VWCE', 'PBR', 'ADD'],
            'Wartość (PLN)': ['4,520.00', '3,890.00', '2,340.00', '1,980.00', '1,750.00'],
            'Zmiana (%)': ['+2.30', '+1.80', '-0.50', '+5.20', '+0.90'],
            'Waga (%)': ['21.60', '18.60', '11.20', '9.50', '8.40'],
            'Typ': ['Akcja', 'Akcja', 'ETF', 'Akcja', 'ETF']
        }
        df = pd.DataFrame(holdings_data)
        st.dataframe(df, width="stretch", hide_index=True)
    
    # Quick actions
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Odśwież Portfolio", width="stretch", key="refresh_portfolio_btn"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("📊 Analiza Ryzyka", width="stretch", key="analiza_ryzyka_btn"):
            st.session_state.page = "📈 Analiza"
            st.rerun()
    
    with col3:
        if st.button("📄 Generuj Raport Excel", width="stretch", key="raport_excel_btn"):
            try:
                with st.spinner("� Generuję raport..."):
                    filename = generate_full_report(stan_spolki)
                    
                    # Read file and offer download
                    with open(filename, "rb") as file:
                        btn = st.download_button(
                            label="⬇️ Pobierz raport",
                            data=file,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    st.success(f"✅ Raport wygenerowany: {filename}")
            except Exception as e:
                st.error(f"❌ Błąd generowania raportu: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    with col4:
        if st.button("🎮 Symuluj Scenariusz", width="stretch"):
            st.session_state.page = "🎮 Symulacje"
            st.rerun()

def show_kodeks_page():
    """Wyświetla Kodeks Spółki z możliwością edycji i dynamicznym odświeżaniem"""
    st.title("📜 Kodeks Spółki 'Horyzont Partnerów'")
    
    kodeks_file = "kodeks_spolki.txt"
    
    # WAŻNE: Zawsze wczytuj świeży plik (bez cache) - może się zmieniać podczas rozmów/głosowań
    try:
        if not os.path.exists(kodeks_file):
            st.error(f"❌ Plik {kodeks_file} nie istnieje!")
            st.info("Utwórz plik `kodeks_spolki.txt` w katalogu głównym projektu.")
            
            # Debug info
            st.warning("📂 Sprawdzam katalog...")
            current_dir = os.getcwd()
            st.code(f"Aktualny katalog: {current_dir}")
            
            files = os.listdir(current_dir)
            st.write("Pliki w katalogu:")
            st.code("\n".join([f for f in files if f.endswith('.txt')]))
            return
        
        # Dynamiczne wczytanie (bez @st.cache)
        with open(kodeks_file, 'r', encoding='utf-8') as f:
            kodeks_content = f.read()
    except Exception as e:
        st.error(f"❌ Błąd wczytywania Kodeksu: {e}")
        import traceback
        st.code(traceback.format_exc())
        return
    
    # Info o dynamicznym odświeżaniu
    st.info("ℹ️ **Kodeks jest dynamicznie odświeżany** - zmiany wprowadzone podczas rozmów lub głosowań będą natychmiast widoczne po przeładowaniu strony.")
    
    # Tabs: Podgląd i Edycja
    tab1, tab2, tab3 = st.tabs(["📖 Podgląd", "✏️ Edycja", "📊 Statystyki"])
    
    with tab1:
        st.markdown("### Pełna treść Kodeksu:")
        st.markdown("---")
        
        # Wyświetl kodeks w czytelnym formacie z zachowaniem formatowania
        st.text(kodeks_content)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"📁 Ścieżka: `{kodeks_file}`")
        with col2:
            if st.button("🔄 Odśwież"):
                st.rerun()
    
    with tab2:
        st.markdown("### Edytuj Kodeks:")
        st.warning("⚠️ **Uwaga:** Zmiany w Kodeksie wpływają na wszystkie decyzje AI i głosowania partnerów!")
        
        # Text area z możliwością edycji
        edited_content = st.text_area(
            "Treść Kodeksu:",
            value=kodeks_content,
            height=500,
            help="Wprowadź zmiany i kliknij 'Zapisz'"
        )
        
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            if st.button("💾 Zapisz zmiany", type="primary"):
                try:
                    # Backup przed zapisem
                    backup_file = f"kodeks_spolki_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write(kodeks_content)
                    
                    # Zapisz nową wersję
                    with open(kodeks_file, 'w', encoding='utf-8') as f:
                        f.write(edited_content)
                    
                    # Synchronizuj cel rezerwy gotówkowej do cele.json
                    try:
                        import re
                        match = re.search(r'Cel #2: Budowa rezerwy gotówkowej do docelowego poziomu ([\d\s,]+) PLN\.', edited_content)
                        if match:
                            # Wyciągnij liczbę (usuń spacje i przecinki)
                            cel_str = match.group(1).replace(' ', '').replace(',', '')
                            new_rezerwa_cel = int(cel_str)
                            
                            # Zaktualizuj cele.json
                            if PERSISTENT_OK:
                                cele = load_persistent_data('cele.json')
                                if cele is None:
                                    cele = {}
                            else:
                                try:
                                    with open('cele.json', 'r', encoding='utf-8') as f:
                                        cele = json.load(f)
                                except:
                                    cele = {}
                            
                            if cele.get('Rezerwa_gotowkowa_PLN') != new_rezerwa_cel:
                                cele['Rezerwa_gotowkowa_PLN'] = new_rezerwa_cel
                                save_cele(cele)
                                st.success(f"✅ Kodeks zapisany! Cel rezerwy zsynchronizowany: {new_rezerwa_cel:,} PLN. Backup: `{backup_file}`")
                            else:
                                st.success(f"✅ Kodeks zapisany! Backup: `{backup_file}`")
                        else:
                            st.success(f"✅ Kodeks zapisany! Backup: `{backup_file}`")
                    except Exception as sync_error:
                        st.success(f"✅ Kodeks zapisany! Backup: `{backup_file}`")
                        st.warning(f"⚠️ Synchronizacja celu: {str(sync_error)}")
                    
                    # WYCZYŚĆ CACHE aby odświeżyć dane
                    load_portfolio_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Błąd zapisu: {e}")
        
        with col2:
            if st.button("↩️ Cofnij zmiany"):
                st.rerun()
        
        with col3:
            st.caption("Backup tworzony automatycznie przed każdym zapisem")
    
    with tab3:
        st.markdown("### Statystyki Kodeksu:")
        
        # Podstawowe statystyki
        lines = kodeks_content.split('\n')
        words = kodeks_content.split()
        chars = len(kodeks_content)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 Liczba linii", len(lines))
        with col2:
            st.metric("📝 Liczba słów", len(words))
        with col3:
            st.metric("🔤 Liczba znaków", chars)
        
        st.markdown("---")
        
        # Analiza struktury (artykuły, paragrafy)
        import re
        articles = re.findall(r'(?:Artykuł|ARTYKUŁ)\s+[IVXLCDM]+', kodeks_content, re.IGNORECASE)
        sections = re.findall(r'§\s*\d+', kodeks_content)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📚 Artykuły", len(articles))
            if articles:
                with st.expander("Zobacz artykuły"):
                    for art in articles:
                        st.write(f"- {art}")
        
        with col2:
            st.metric("📋 Paragrafy (§)", len(sections))
            if sections:
                with st.expander("Zobacz paragrafy"):
                    for sec in sections[:20]:  # Max 20
                        st.write(f"- {sec}")
        
        st.markdown("---")
        st.caption(f"Ostatnia modyfikacja: {datetime.fromtimestamp(os.path.getmtime(kodeks_file)).strftime('%Y-%m-%d %H:%M:%S')}")

def show_alerts_page():
    """
    Strona z alertami i notyfikacjami
    Pokazuje: nowe pozycje, zmiany cen, terminy kredytów, osiągnięte cele
    """
    st.title("🔔 Alerty i Notyfikacje")
    
    try:
        import alert_system as alerts
        import benchmark_comparison as bench
        import goal_analytics as goals
        import daily_snapshot as ds
        
        # Tabs dla różnych typów alertów
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Wszystkie", 
            "🆕 Nowe Pozycje", 
            "📈 Zmiany Cen", 
            "💳 Kredyty", 
            "🎯 Cele"
        ])
        
        with tab1:
            st.subheader("📊 Wszystkie Alerty")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info("💡 System automatycznie wykrywa ważne wydarzenia w portfelu")
            
            with col2:
                if st.button("🔄 Skanuj Teraz", width="stretch"):
                    with st.spinner("Skanowanie..."):
                        results = alerts.run_all_detectors(verbose=False)
                        total = sum(len(v) if isinstance(v, list) else 0 for v in results.values())
                        if total > 0:
                            st.success(f"✅ Znaleziono {total} nowych alertów!")
                        else:
                            st.info("✅ Brak nowych alertów")
                        st.rerun()
            
            # Historia alertów
            st.markdown("---")
            history = alerts.get_alerts_history()
            
            if not history:
                st.info("📭 Brak alertów w historii. Kliknij 'Skanuj Teraz' aby sprawdzić.")
            else:
                # Filtry
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    filter_type = st.selectbox(
                        "Typ alertu",
                        ["Wszystkie", "new_position", "price_change", "loan_due", "goal_achieved"]
                    )
                
                with col2:
                    filter_severity = st.selectbox(
                        "Ważność",
                        ["Wszystkie", "info", "warning", "critical", "success"]
                    )
                
                with col3:
                    show_read = st.checkbox("Pokaż przeczytane", value=True)
                
                # Filtrowanie
                filtered = history
                if filter_type != "Wszystkie":
                    filtered = [a for a in filtered if a.get('type') == filter_type]
                if filter_severity != "Wszystkie":
                    filtered = [a for a in filtered if a.get('severity') == filter_severity]
                if not show_read:
                    filtered = [a for a in filtered if not a.get('read', False)]
                
                st.caption(f"Wyświetlam {len(filtered)} / {len(history)} alertów")
                
                # Wyświetl alerty
                for alert in filtered[:50]:  # Max 50
                    severity = alert.get('severity', 'info')
                    
                    # Emoji na podstawie severity
                    severity_emoji = {
                        'info': 'ℹ️',
                        'warning': '⚠️',
                        'critical': '🔴',
                        'success': '✅'
                    }.get(severity, 'ℹ️')
                    
                    # Kolor na podstawie severity
                    color_map = {
                        'info': 'blue',
                        'warning': 'orange',
                        'critical': 'red',
                        'success': 'green'
                    }
                    
                    with st.container():
                        col1, col2 = st.columns([5, 1])
                        
                        with col1:
                            timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%Y-%m-%d %H:%M")
                            st.markdown(f"**{severity_emoji} {alert['title']}**")
                            st.caption(f"{timestamp} | {alert['message']}")
                        
                        with col2:
                            if not alert.get('read', False):
                                st.markdown("🔵 **NOWY**")
                        
                        st.markdown("---")
        
        with tab2:
            st.subheader("🆕 Nowe Pozycje w Portfelu")
            
            history = alerts.get_alerts_history()
            new_position_alerts = [a for a in history if a.get('type') == 'new_position']
            
            if not new_position_alerts:
                st.info("📭 Brak nowych pozycji w historii")
            else:
                st.success(f"✅ Znaleziono {len(new_position_alerts)} nowych pozycji")
                
                for alert in new_position_alerts[:20]:
                    meta = alert.get('metadata', {})
                    ticker = meta.get('ticker') or meta.get('symbol', 'N/A')
                    asset_type = meta.get('type', 'N/A')
                    quantity = meta.get('quantity', 0)
                    price = meta.get('price', 0)
                    
                    timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%Y-%m-%d %H:%M")
                    
                    with st.expander(f"🆕 {ticker} - {timestamp}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Typ", asset_type.upper())
                            st.metric("Ilość", f"{quantity:.4f}")
                        
                        with col2:
                            st.metric("Cena", f"${price:.2f}")
                            st.metric("Wartość", f"${quantity * price:.2f}")
                        
                        st.info(alert['message'])
        
        with tab3:
            st.subheader("📈 Znaczące Zmiany Cen (>10%)")
            
            history = alerts.get_alerts_history()
            price_change_alerts = [a for a in history if a.get('type') == 'price_change']
            
            if not price_change_alerts:
                st.info("📭 Brak znaczących zmian cen")
            else:
                st.warning(f"⚠️ Znaleziono {len(price_change_alerts)} znaczących zmian")
                
                for alert in price_change_alerts[:20]:
                    meta = alert.get('metadata', {})
                    ticker = meta.get('ticker') or meta.get('symbol', 'N/A')
                    change_pct = meta.get('change_pct', 0)
                    prev_price = meta.get('previous_price', 0)
                    curr_price = meta.get('current_price', 0)
                    
                    timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%Y-%m-%d %H:%M")
                    
                    # Emoji i kolor
                    emoji = "🔴📉" if change_pct < 0 else "🟢📈"
                    
                    with st.expander(f"{emoji} {ticker}: {change_pct:+.1f}% - {timestamp}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Poprzednia cena", f"${prev_price:.2f}")
                        
                        with col2:
                            st.metric("Aktualna cena", f"${curr_price:.2f}")
                        
                        with col3:
                            st.metric("Zmiana", f"{change_pct:+.1f}%", delta=f"{change_pct:+.1f}%")
                        
                        st.info(alert['message'])
        
        with tab4:
            st.subheader("💳 Zbliżające się Terminy Płatności")
            
            history = alerts.get_alerts_history()
            loan_alerts = [a for a in history if a.get('type') == 'loan_due']
            
            if not loan_alerts:
                st.success("✅ Brak zbliżających się terminów płatności")
            else:
                st.warning(f"⚠️ Zbliża się {len(loan_alerts)} płatności")
                
                for alert in loan_alerts:
                    meta = alert.get('metadata', {})
                    loan_name = meta.get('loan_name', 'N/A')
                    due_date = meta.get('due_date', 'N/A')
                    days_until = meta.get('days_until_due', 0)
                    amount = meta.get('amount', 0)
                    
                    severity = alert.get('severity', 'info')
                    emoji = "🔴" if days_until == 1 else ("🟠" if days_until == 3 else "🟡")
                    
                    with st.container():
                        st.markdown(f"### {emoji} {loan_name}")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Termin", due_date)
                        
                        with col2:
                            st.metric("Za ile dni", f"{days_until} dni")
                        
                        with col3:
                            st.metric("Kwota", f"{amount:.2f} PLN")
                        
                        st.error(alert['message'])
                        st.markdown("---")
        
        with tab5:
            st.subheader("🎯 Cele Finansowe")
            
            # Osiągnięte cele
            history = alerts.get_alerts_history()
            goal_alerts = [a for a in history if a.get('type') == 'goal_achieved']
            
            if goal_alerts:
                st.success(f"🎉 Osiągnięto {len(goal_alerts)} celów!")
                
                for alert in goal_alerts:
                    meta = alert.get('metadata', {})
                    goal_name = meta.get('goal_name', 'N/A')
                    progress = meta.get('progress_pct', 0)
                    
                    st.balloons()
                    st.markdown(f"### 🎉 {goal_name}")
                    st.success(alert['message'])
                    st.progress(min(progress / 100, 1.0))
                    st.markdown("---")
            
            # Predykcje dla aktywnych celów
            st.markdown("### 🔮 Predykcje Osiągnięcia")
            
            snapshots = ds.load_snapshot_history()
            predictions = goals.predict_all_goals(snapshots)
            
            if not predictions:
                st.info("📭 Brak aktywnych celów")
            else:
                for goal_id, pred in predictions.items():
                    status = pred.get('status', 'unknown')
                    
                    with st.expander(f"📌 {pred['goal_name']} - {pred['progress_pct']:.0f}%"):
                        if status == 'achieved':
                            st.success(pred.get('message', 'Cel osiągnięty!'))
                            st.progress(1.0)
                        
                        elif status == 'predicted':
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Postęp", f"{pred['progress_pct']:.1f}%")
                                st.progress(pred['progress_pct'] / 100)
                            
                            with col2:
                                st.metric("Za ile dni", f"{pred['predicted_days']} dni")
                                st.caption(f"Data: {pred['predicted_date']}")
                            
                            with col3:
                                confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
                                st.metric("Pewność", pred['confidence'].upper())
                                st.caption(f"{confidence_emoji.get(pred['confidence'], '⚪')} R² = {pred.get('r_squared', 0):.2f}")
                            
                            st.info(f"📈 Tempo: {pred['daily_rate']:.2f} PLN/dzień")
                        
                        else:
                            st.warning(pred.get('message', 'Brak danych do predykcji'))
            
            # Rekomendacje oszczędzania
            st.markdown("---")
            st.markdown("### 💰 Rekomendacje Oszczędzania")
            
            deadline_months = st.slider("Chcę osiągnąć cele w ciągu (miesięcy):", 1, 36, 12)
            
            recommendations = goals.get_all_savings_recommendations(deadline_months)
            
            if not recommendations:
                st.info("📭 Brak aktywnych celów wymagających oszczędzania")
            else:
                for goal_id, rec in recommendations.items():
                    status = rec.get('status', 'unknown')
                    
                    if status == 'achieved':
                        continue  # Pomijamy już osiągnięte
                    
                    with st.container():
                        st.markdown(f"**💎 {rec['goal_name']}**")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Brakuje", f"{rec['gap']:.0f} PLN")
                        
                        with col2:
                            st.metric("Miesięcznie", f"{rec['required_monthly']:.0f} PLN")
                        
                        with col3:
                            st.metric("Dziennie", f"{rec['required_daily']:.0f} PLN")
                        
                        with col4:
                            st.metric("Termin", rec['deadline_date'])
                        
                        st.caption(rec['recommendation'])
                        st.markdown("---")
    
    except ImportError as e:
        st.error(f"⚠️ Błąd importu modułów: {e}")
        st.info("Upewnij się że pliki alert_system.py, benchmark_comparison.py i goal_analytics.py istnieją")
    except Exception as e:
        st.error(f"⚠️ Błąd: {e}")
        import traceback
        st.code(traceback.format_exc())

def show_autonomous_conversations_page():
    """Strona z autonomicznymi rozmowami Rady"""
    st.title("🗣️ Autonomiczne Rozmowy Rady Partnerów")
    
    st.markdown("""
    ### 🤖 Twoi partnerzy rozmawiają nawet gdy Cię nie ma!
    
    System autonomicznych rozmów pozwala Radzie Partnerów dyskutować o portfelu, rynkach i strategii
    nawet bez Twojej obecności. Wszystkie rozmowy są zapisywane i możesz je przejrzeć tutaj.
    """)
    
    # Import engine
    try:
        from autonomous_conversation_engine import AutonomousConversationEngine
        engine = AutonomousConversationEngine()
    except Exception as e:
        st.error(f"❌ Błąd importu Autonomous Engine: {e}")
        st.info("💡 Upewnij się, że plik `autonomous_conversation_engine.py` istnieje")
        import traceback
        st.code(traceback.format_exc())
        return
    
    # Wyświetl status API
    st.markdown("---")
    st.markdown("### 📊 Status API & Budżet")
    
    try:
        tracker = get_tracker()
    except Exception as e:
        st.error(f"❌ Błąd API Tracker: {e}")
        return
    summary = tracker.get_today_summary()
    budgets = tracker.get_all_budgets()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🤖 Rozmowy dzisiaj",
            summary['autonomous_conversations'],
            help="Liczba autonomicznych rozmów przeprowadzonych dzisiaj"
        )
    
    with col2:
        st.metric(
            "📞 Wywołania API (Autonomous)",
            summary['autonomous_calls'],
            help="Liczba wywołań API przez autonomiczne rozmowy"
        )
    
    with col3:
        st.metric(
            "👤 Wywołania API (User)",
            summary['user_calls'],
            help="Liczba wywołań API przez Ciebie (normalne rozmowy)"
        )
    
    with col4:
        st.metric(
            "💰 Koszt dzisiaj",
            f"${summary['total_cost_usd']:.2f}",
            help="Szacunkowy koszt API dzisiaj"
        )
    
    # Szczegóły budżetów per API
    with st.expander("📋 Szczegóły budżetów API"):
        for api_name in ['claude', 'gemini', 'openai']:
            budget = budgets[api_name]
            st.markdown(f"#### 🔹 {api_name.upper()}")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.progress(
                    budget['autonomous']['percentage_used'] / 100,
                    text=f"Autonomous: {budget['autonomous']['used']}/{budget['autonomous']['limit']} ({budget['autonomous']['percentage_used']}%)"
                )
            
            with col_b:
                st.progress(
                    budget['user']['percentage_used'] / 100,
                    text=f"User: {budget['user']['used']}/{budget['user']['limit']} ({budget['user']['percentage_used']}%)"
                )
    
    # Przyciski akcji
    st.markdown("---")
    st.markdown("### 🎮 Akcje")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Uruchom nową rozmowę", type="primary", width="stretch"):
            with st.spinner("🤖 Partnerzy rozmawiają..."):
                conversation = engine.run_conversation(max_messages=12)
                
                if conversation:
                    st.success(f"✅ Rozmowa zakończona! ID: {conversation['id']}")
                    st.info(f"📝 Liczba wiadomości: {len(conversation['messages'])}")
                    st.rerun()
                else:
                    st.error("❌ Nie udało się uruchomić rozmowy (brak budżetu API?)")
    
    with col2:
        if st.button("🔄 Odśwież listę", width="stretch"):
            st.rerun()
    
    with col3:
        if st.button("📊 Szczegóły API", width="stretch"):
            # Wyświetl szczegółowy status w Streamlit (nie terminal)
            st.markdown("---")
            st.markdown("#### 📊 Szczegółowy Status API")
            
            for api_name in ['claude', 'gemini', 'openai']:
                budget = budgets[api_name]
                
                with st.expander(f"🔹 {api_name.upper()}", expanded=True):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric(
                            "Autonomous Used",
                            f"{budget['autonomous']['used']}/{budget['autonomous']['limit']}",
                            f"{budget['autonomous']['percentage_used']}%"
                        )
                    
                    with col_b:
                        st.metric(
                            "User Used",
                            f"{budget['user']['used']}/{budget['user']['limit']}",
                            f"{budget['user']['percentage_used']}%"
                        )
                    
                    with col_c:
                        st.metric(
                            "Total",
                            f"{budget['total']['used']}/{budget['total']['limit']}",
                            f"{budget['total']['percentage_used']}%"
                        )
            
            st.markdown("---")
    
    # Lista rozmów
    st.markdown("---")
    st.markdown("### 📜 Historia Rozmów")
    
    conversations = engine.get_recent_conversations(limit=50)
    
    if not conversations:
        st.info("📭 Brak autonomicznych rozmów. Kliknij 'Uruchom nową rozmowę' aby rozpocząć!")
        return
    
    # Filtry
    col1, col2, col3 = st.columns(3)
    
    with col1:
        topics = list(set([c.get('topic_name', 'Unknown') for c in conversations]))
        selected_topic = st.selectbox("🏷️ Filtruj po temacie", ["Wszystkie"] + topics)
    
    with col2:
        dates = list(set([c.get('date', '')[:10] for c in conversations if c.get('date')]))
        dates.sort(reverse=True)
        selected_date = st.selectbox("📅 Filtruj po dacie", ["Wszystkie"] + dates)
    
    with col3:
        min_messages = st.slider("📝 Min. liczba wiadomości", 0, 20, 0)
    
    # Zastosuj filtry
    filtered_conversations = conversations
    
    if selected_topic != "Wszystkie":
        filtered_conversations = [c for c in filtered_conversations if c.get('topic_name') == selected_topic]
    
    if selected_date != "Wszystkie":
        filtered_conversations = [c for c in filtered_conversations if c.get('date', '')[:10] == selected_date]
    
    if min_messages > 0:
        filtered_conversations = [c for c in filtered_conversations if len(c.get('messages', [])) >= min_messages]
    
    st.info(f"📊 Znaleziono: {len(filtered_conversations)} rozmów")
    
    # Wyświetl rozmowy
    for conv in filtered_conversations:
        conv_id = conv.get('id', 'unknown')
        topic_name = conv.get('topic_name', 'Unknown Topic')
        date_str = conv.get('date', '')[:19] if conv.get('date') else 'Unknown date'
        participants = conv.get('participants', [])
        messages = conv.get('messages', [])
        api_calls = conv.get('api_calls_used', 0)
        opening_prompt = conv.get('opening_prompt', '')
        summary = conv.get('summary', None)
        
        with st.expander(f"💬 {date_str} - {topic_name} ({len(messages)} wiadomości)"):
            st.markdown(f"**ID:** `{conv_id}`")
            st.markdown(f"**Uczestnicy:** {', '.join(participants)}")
            st.markdown(f"**Wywołania API:** {api_calls}")
            st.markdown(f"**Status:** {conv.get('status', 'unknown')}")
            
            # Pokaż AI Summary jeśli istnieje (NOWE!)
            if summary:
                st.markdown("---")
                st.markdown("### 🤖 AI Summary")
                
                # Sentiment badge
                sentiment = summary.get('sentiment', 'neutral')
                sentiment_emoji = {
                    'positive': '😊',
                    'neutral': '😐',
                    'negative': '😟'
                }.get(sentiment, '😐')
                sentiment_color = {
                    'positive': '#27ae60',
                    'neutral': '#95a5a6',
                    'negative': '#e74c3c'
                }.get(sentiment, '#95a5a6')
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"**📝 Podsumowanie:**\n\n{summary.get('summary', 'Brak podsumowania')}")
                with col2:
                    st.markdown(f"""
                    <div style="background: {sentiment_color}; color: white; padding: 10px; border-radius: 5px; text-align: center;">
                        <div style="font-size: 24px;">{sentiment_emoji}</div>
                        <div style="font-size: 12px;">{sentiment.upper()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Key points
                key_points = summary.get('key_points', [])
                if key_points:
                    st.markdown("**🎯 Kluczowe wnioski:**")
                    for point in key_points:
                        st.markdown(f"- {point}")
            
            # Pokaż opening prompt jeśli istnieje
            if opening_prompt:
                st.markdown("---")
                st.markdown("#### 💭 Temat dyskusji:")
                st.info(opening_prompt)
            
            st.markdown("---")
            st.markdown("#### 📝 Transkrypt:")
            
            for msg in messages:
                partner = msg.get('partner', 'Unknown')
                message_text = msg.get('message', '')
                msg_num = msg.get('message_number', 0)
                
                st.markdown(f"**[{msg_num}] {partner}:**")
                st.markdown(f"> {message_text}")
                st.markdown("")

def show_notifications_page():
    """Strona z konfiguracją i historią powiadomień email"""
    st.title("📧 Powiadomienia Email")
    
    st.markdown("""
    ### 📨 System powiadomień o rozmowach Rady
    
    Otrzymuj emaile gdy Rada Partnerów zakończy autonomiczną rozmowę lub wykryje ważne zagadnienie.
    """)
    
    # Inicjalizuj notifier
    notifier = get_conversation_notifier()
    
    # === SEKCJA 1: KONFIGURACJA ===
    st.markdown("---")
    st.subheader("⚙️ Konfiguracja")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Włącz/wyłącz notyfikacje
        enabled = st.checkbox(
            "🔔 Włącz powiadomienia email",
            value=notifier.config.get("enabled", False),
            help="Włącz/wyłącz całkowicie system powiadomień"
        )
        
        # Email odbiorcy
        email_to = st.text_input(
            "📧 Email odbiorcy",
            value=notifier.config.get("email_to", ""),
            placeholder="your-email@gmail.com",
            help="Adres email na który będą wysyłane powiadomienia"
        )
        
        # Alert: rozmowa zakończona
        alert_conversation = st.checkbox(
            "🗣️ Powiadom o zakończonej rozmowie",
            value=notifier.config.get("alerts", {}).get("conversation_completed", True),
            help="Wyślij email po każdej zakończonej autonomicznej rozmowie"
        )
    
    with col2:
        # Daily digest
        daily_digest_enabled = st.checkbox(
            "📊 Włącz Daily Digest",
            value=notifier.config.get("daily_digest", {}).get("enabled", True),
            help="Codzienny email z podsumowaniem rozmów"
        )
        
        # Czas wysyłki digest
        digest_time = st.time_input(
            "⏰ Godzina wysyłki digest",
            value=datetime.strptime(
                notifier.config.get("daily_digest", {}).get("time", "18:00"),
                "%H:%M"
            ).time(),
            help="O której godzinie wysłać codzienny digest"
        )
    
    # Zapisz konfigurację
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Zapisz konfigurację", type="primary", width="stretch"):
            new_config = {
                "enabled": enabled,
                "email_to": email_to,
                "daily_digest": {
                    "enabled": daily_digest_enabled,
                    "time": digest_time.strftime("%H:%M")
                },
                "alerts": {
                    "conversation_completed": alert_conversation,
                    "critical_issue": True
                }
            }
            
            # Zapisz przez persistence system
            notifier.config.update(new_config)
            if PERSISTENT_OK:
                save_persistent_data('notification_config.json', notifier.config)
            else:
                # Fallback
                with open("notification_config.json", 'w', encoding='utf-8') as f:
                    json.dump(notifier.config, f, indent=2, ensure_ascii=False)
            
            st.success("✅ Konfiguracja zapisana!")
            st.rerun()
    
    with col2:
        if st.button("🧪 Wyślij test email", width="stretch"):
            if not enabled:
                st.error("❌ Najpierw włącz powiadomienia!")
            elif not email_to:
                st.error("❌ Podaj adres email odbiorcy!")
            else:
                with st.spinner("Wysyłam email testowy..."):
                    success = notifier.send_test_email()
                    if success:
                        st.success("✅ Email testowy wysłany! Sprawdź skrzynkę.")
                    else:
                        st.error("❌ Błąd wysyłania. Sprawdź GMAIL_USER i GMAIL_APP_PASSWORD w .env")
    
    # === SEKCJA 2: INSTRUKCJE SETUP ===
    with st.expander("📖 Jak skonfigurować Gmail SMTP?"):
        st.markdown("""
        ### 🔐 Krok 1: Utwórz App Password w Gmail
        
        1. Przejdź do [Google Account Security](https://myaccount.google.com/security)
        2. Włącz **2-Step Verification** (jeśli nie masz)
        3. Przejdź do **App Passwords**
        4. Wybierz aplikację: **Mail** + urządzenie: **Windows Computer**
        5. Skopiuj wygenerowane hasło (16 znaków)
        
        ### ⚙️ Krok 2: Dodaj do .env
        
        Otwórz plik `.env` i dodaj:
        ```
        GMAIL_USER=your-email@gmail.com
        GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
        ```
        
        ### 🧪 Krok 3: Testuj
        
        1. Włącz powiadomienia ☝️
        2. Podaj adres email odbiorcy
        3. Zapisz konfigurację
        4. Kliknij "🧪 Wyślij test email"
        5. Sprawdź skrzynkę odbiorczą
        
        ✅ Jeśli widzisz email - wszystko działa!
        """)
    
    # === SEKCJA 3: HISTORIA POWIADOMIEŃ ===
    st.markdown("---")
    st.subheader("📜 Historia powiadomień")
    
    history = notifier.get_recent_notifications(limit=50)
    
    if history:
        # Filtry
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.multiselect(
                "Typ",
                options=["conversation_completed", "daily_digest", "test", "critical_issue"],
                default=["conversation_completed", "daily_digest", "test"]
            )
        with col2:
            filter_status = st.multiselect(
                "Status",
                options=["sent", "failed"],
                default=["sent", "failed"]
            )
        
        # Filtruj
        filtered = [
            h for h in history
            if h.get("type") in filter_type and h.get("status") in filter_status
        ]
        
        st.markdown(f"**Znaleziono:** {len(filtered)} powiadomień")
        
        # Wyświetl tabelę
        if filtered:
            for notif in filtered:
                timestamp = notif.get("timestamp", "")[:19]
                notif_type = notif.get("type", "unknown")
                subject = notif.get("subject", "")
                status = notif.get("status", "unknown")
                error = notif.get("error", None)
                
                # Emoji dla statusu
                status_emoji = "✅" if status == "sent" else "❌"
                
                # Emoji dla typu
                type_emoji = {
                    "conversation_completed": "🗣️",
                    "daily_digest": "📊",
                    "test": "🧪",
                    "critical_issue": "🚨"
                }.get(notif_type, "📧")
                
                with st.expander(f"{status_emoji} {timestamp} - {type_emoji} {subject}"):
                    st.markdown(f"**Typ:** {notif_type}")
                    st.markdown(f"**Status:** {status}")
                    if error:
                        st.error(f"**Błąd:** {error}")
    else:
        st.info("Brak historii powiadomień. Wyślij pierwszy email!")
    
    # === SEKCJA 4: STATYSTYKI ===
    if history:
        st.markdown("---")
        st.subheader("📊 Statystyki")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(history)
        sent = len([h for h in history if h.get("status") == "sent"])
        failed = len([h for h in history if h.get("status") == "failed"])
        success_rate = (sent / total * 100) if total > 0 else 0
        
        col1.metric("📧 Wysłane", sent)
        col2.metric("❌ Błędy", failed)
        col3.metric("📈 Success Rate", f"{success_rate:.1f}%")
        col4.metric("📅 Ostatni 7 dni", len([
            h for h in history 
            if (datetime.now() - datetime.fromisoformat(h.get("timestamp", "2020-01-01"))).days <= 7
        ]))

def show_consultations_page():
    """Strona z systemem konsultacji z Radą Partnerów"""
    st.title("🗳️ Konsultacje z Radą")
    
    st.markdown("""
    **System konsultacji** pozwala zapytać Radę Partnerów o opinię na dowolny temat.
    Każdy partner AI otrzyma pytanie i wyrazi swoją opinię (ZA/PRZECIW/NEUTRALNIE).
    """)
    
    manager = get_consultation_manager()
    
    # === TABS ===
    tab1, tab2 = st.tabs(["📝 Nowa Konsultacja", "📚 Historia"])
    
    # === TAB 1: NOWA KONSULTACJA ===
    with tab1:
        st.markdown("### Zadaj pytanie Radzie")
        
        # Formularz
        with st.form("new_consultation_form"):
            question = st.text_area(
                "❓ Twoje pytanie lub propozycja:",
                placeholder="Np. Czy powinienem zwiększyć alokację w krypto do 15%?",
                height=100
            )
            
            # Lista partnerów (bez Partner Zarządzający)
            available_partners = [
                p['name'] for p in manager.personas 
                if p['name'] != 'Partner Zarządzający (JA)'
            ]
            
            selected_partners = st.multiselect(
                "👥 Wybierz partnerów do zapytania:",
                options=available_partners,
                default=available_partners  # Domyślnie wszyscy
            )
            
            st.markdown(f"**Wybrano:** {len(selected_partners)} partnerów")
            
            submitted = st.form_submit_button("📤 Wyślij do Rady", type="primary", width="stretch")
        
        # Obsługa wysłania
        if submitted:
            if not question.strip():
                st.error("❌ Wpisz pytanie!")
            elif len(selected_partners) == 0:
                st.error("❌ Wybierz przynajmniej jednego partnera!")
            else:
                with st.spinner("🔄 Tworzę konsultację..."):
                    # 1. Utwórz konsultację
                    consultation = manager.create_consultation(question, selected_partners)
                    st.success(f"✅ Konsultacja utworzona (ID: {consultation['id']})")
                
                # 2. Zbierz odpowiedzi
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                responses_container = st.container()
                
                consultation = manager.collect_responses(consultation['id'])
                
                # Pokaż odpowiedzi w czasie rzeczywistym
                for i, response in enumerate(consultation['responses']):
                    progress = (i + 1) / len(selected_partners)
                    progress_bar.progress(progress)
                    status_text.text(f"✅ Zebrano {i+1}/{len(selected_partners)} odpowiedzi...")
                    
                    with responses_container:
                        stance_emoji = {
                            'for': '✅',
                            'against': '❌',
                            'neutral': '🤔'
                        }.get(response['stance'], '🤔')
                        
                        st.markdown(f"""
                        **{response['partner']}** {stance_emoji} **{response['stance'].upper()}** (Pewność: {response['confidence']}/10)
                        > {response['reasoning']}
                        """)
                
                progress_bar.progress(1.0)
                status_text.text("✅ Wszystkie odpowiedzi zebrane!")
                
                # 3. Wygeneruj AI Summary
                with st.spinner("🤖 Generuję podsumowanie..."):
                    summary = manager.generate_summary(consultation['id'])
                
                if summary:
                    st.success("✅ Konsultacja zakończona!")
                    
                    # Pokaż summary
                    st.markdown("---")
                    st.markdown("### 🤖 Podsumowanie AI")
                    
                    # Wyniki głosowania
                    col1, col2, col3 = st.columns(3)
                    col1.metric("✅ ZA", summary['votes_for'])
                    col2.metric("❌ PRZECIW", summary['votes_against'])
                    col3.metric("🤔 NEUTRALNE", summary['votes_neutral'])
                    
                    # Konsensus badge
                    consensus = summary.get('consensus', 'medium')
                    consensus_color = {
                        'high': '#27ae60',
                        'medium': '#f39c12',
                        'low': '#e74c3c'
                    }.get(consensus, '#95a5a6')
                    
                    consensus_label = {
                        'high': 'Wysoki Konsensus',
                        'medium': 'Średni Konsensus',
                        'low': 'Niski Konsensus'
                    }.get(consensus, 'Nieznany')
                    
                    st.markdown(f"""
                    <div style="background: {consensus_color}; color: white; padding: 10px; 
                                border-radius: 5px; text-align: center; margin: 10px 0;">
                        <strong>{consensus_label}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Główne argumenty
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ Argumenty ZA:**")
                        for arg in summary.get('main_arguments_for', []):
                            st.markdown(f"- {arg}")
                    
                    with col2:
                        st.markdown("**❌ Argumenty PRZECIW:**")
                        for arg in summary.get('main_arguments_against', []):
                            st.markdown(f"- {arg}")
                    
                    # Rekomendacja
                    st.info(f"**💡 Rekomendacja AI:** {summary.get('recommendation', 'Brak rekomendacji')}")
                    
                    # Opcja wysłania emaila (jeśli włączone)
                    try:
                        notifier = get_conversation_notifier()
                        if notifier.config.get("enabled", False):
                            st.success("📧 Email z wynikami został wysłany!")
                    except:
                        pass
    
    # === TAB 2: HISTORIA ===
    with tab2:
        st.markdown("### Historia Konsultacji")
        
        consultations = manager.get_recent_consultations(limit=50)
        
        if not consultations:
            st.info("📭 Brak konsultacji. Utwórz pierwszą w zakładce 'Nowa Konsultacja'!")
        else:
            st.markdown(f"**Znaleziono:** {len(consultations)} konsultacji")
            
            # Filtry
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.multiselect(
                    "Status:",
                    options=['completed', 'in_progress', 'responses_collected'],
                    default=['completed']
                )
            
            # Filtruj
            filtered = [c for c in consultations if c.get('status') in status_filter]
            
            st.markdown(f"**Po filtrowaniu:** {len(filtered)} konsultacji")
            
            # Pokaż każdą konsultację
            for cons in filtered:
                with st.expander(
                    f"🗳️ {cons.get('question', 'Brak pytania')[:80]}... | "
                    f"{cons.get('created_at', '')[:16]} | "
                    f"{len(cons.get('participants', []))} partnerów"
                ):
                    st.markdown(f"**📋 ID:** `{cons['id']}`")
                    st.markdown(f"**❓ Pytanie:** {cons['question']}")
                    st.markdown(f"**👥 Uczestnicy:** {', '.join(cons['participants'])}")
                    st.markdown(f"**📅 Data:** {cons['created_at'][:19]}")
                    st.markdown(f"**📊 Status:** {cons['status']}")
                    
                    # Odpowiedzi
                    responses = cons.get('responses', [])
                    if responses:
                        st.markdown("---")
                        st.markdown("**💬 Odpowiedzi partnerów:**")
                        
                        for resp in responses:
                            stance_emoji = {
                                'for': '✅',
                                'against': '❌',
                                'neutral': '🤔'
                            }.get(resp['stance'], '🤔')
                            
                            st.markdown(f"""
                            **{resp['partner']}** {stance_emoji} **{resp['stance'].upper()}** 
                            (Pewność: {resp['confidence']}/10)
                            > {resp['reasoning']}
                            """)
                    
                    # Summary
                    summary = cons.get('summary')
                    if summary:
                        st.markdown("---")
                        st.markdown("### 🤖 Podsumowanie AI")
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("✅ ZA", summary['votes_for'])
                        col2.metric("❌ PRZECIW", summary['votes_against'])
                        col3.metric("🤔 NEUTRALNE", summary['votes_neutral'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**✅ Argumenty ZA:**")
                            for arg in summary.get('main_arguments_for', []):
                                st.markdown(f"- {arg}")
                        
                        with col2:
                            st.markdown("**❌ Argumenty PRZECIW:**")
                            for arg in summary.get('main_arguments_against', []):
                                st.markdown(f"- {arg}")
                        
                        st.info(f"**💡 Rekomendacja:** {summary.get('recommendation', '')}")

def show_partners_page():
    """Strona z partnerami"""
    st.title("💬 Chat z Partnerami AI")
    
    # Initialize session state for conversation history (per partner)
    if 'partner_conversations' not in st.session_state:
        # Załaduj z persistence jeśli dostępne
        if PERSISTENT_OK:
            saved_conversations = load_persistent_data('partner_conversations.json')
            st.session_state.partner_conversations = saved_conversations if saved_conversations else {}
        else:
            st.session_state.partner_conversations = {}
    
    if 'selected_partner' not in st.session_state:
        st.session_state.selected_partner = "Wszyscy"
    
    # Get or create conversation for current partner
    current_partner = st.session_state.selected_partner
    if current_partner not in st.session_state.partner_conversations:
        st.session_state.partner_conversations[current_partner] = {
            'messages': [],
            'session_id': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'session_count': 1
        }
    
    # Backward compatibility - migrate old messages if exists
    if 'messages' in st.session_state and len(st.session_state.messages) > 0:
        if len(st.session_state.partner_conversations[current_partner]['messages']) == 0:
            st.session_state.partner_conversations[current_partner]['messages'] = st.session_state.messages
        del st.session_state.messages
    
    # Helper function to get current conversation messages
    def get_messages():
        return st.session_state.partner_conversations[current_partner]['messages']
    
    def add_message(msg):
        st.session_state.partner_conversations[current_partner]['messages'].append(msg)
        # Zapisz rozmowy po każdej wiadomości
        if PERSISTENT_OK:
            save_persistent_data('partner_conversations.json', st.session_state.partner_conversations)
    
    def clear_messages():
        st.session_state.partner_conversations[current_partner]['messages'] = []
        # Zapisz po wyczyszczeniu
        if PERSISTENT_OK:
            save_persistent_data('partner_conversations.json', st.session_state.partner_conversations)
    
    # === TABY ===
    tab_chat, tab_profiles = st.tabs(["💬 Chat", "📋 Profile Partnerów"])
    
    # === TAB 1: CHAT ===
    with tab_chat:
        # Sidebar z listą partnerów
        with st.sidebar:
            st.markdown("### 🎭 Rada Partnerów")
            
            partners = {}
            
            # Załaduj prawdziwych partnerów z PERSONAS (pomijając Partnera Zarządzającego - to Ty!)
            if IMPORTS_OK and PERSONAS:
                # Opcja "Wszyscy"
                partners["Wszyscy"] = {"emoji": "👥", "status": "🟢", "display": "Wszyscy"}
                
                # Dodaj każdego partnera OPRÓCZ "Partner Zarządzający (JA)"
                for name, config in PERSONAS.items():
                    # Pomiń Partnera Zarządzającego - to użytkownik
                    if 'Partner Zarządzający' in name and '(JA)' in name:
                        continue
                    
                    # Wyciągnij samo imię bez dodatkowych opisów
                    display_name = name
                    
                    # Dla "Ja (Partner Strategiczny)" -> "Ja"
                    if '(' in name:
                        display_name = name.split('(')[0].strip()
                    
                    # Dla "Partner ds. Czegoś" -> wyciągnij kluczową nazwę
                    if display_name.startswith('Partner ds.'):
                        # Np. "Partner ds. Jakości Biznesowej" -> "Partner Jakości"
                        display_name = display_name.replace('Partner ds. ', '')
                    
                    partners[name] = {
                        "emoji": "🤖",
                        "status": "🟢",
                        "display": display_name
                    }
            else:
                # Fallback jeśli PERSONAS nie załadowało się
                partners = {
                    "Wszyscy": {"emoji": "👥", "status": "🟢", "display": "Wszyscy"}
                }
            
            for name, info in partners.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    display_name = info.get('display', name)
                    # Tylko imię, bez opisu roli
                    if st.button(
                        f"{info.get('emoji', '🤖')} {display_name}",
                        key=f"partner_{name}",
                        width="stretch"
                    ):
                        st.session_state.selected_partner = name
                with col2:
                    st.markdown(info['status'])
            
            st.markdown("---")
            
            st.markdown("### ⚙️ Opcje")
            
            # Przycisk Nowa rozmowa
            if st.button("🆕 Nowa rozmowa", width="stretch", key="new_conversation_btn", type="primary"):
                current_conv = st.session_state.partner_conversations[current_partner]
                current_conv['session_count'] += 1
                current_conv['session_id'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                current_conv['messages'] = []
                st.rerun()
            
            # Statystyki sesji
            conv_info = st.session_state.partner_conversations[current_partner]
            st.caption(f"📅 Sesja #{conv_info['session_count']} od {conv_info['session_id']}")
            st.caption(f"💬 Wiadomości: {len(conv_info['messages'])}")
            
            st.markdown("---")
            
            tryb = st.radio(
                "Tryb odpowiedzi:",
                ["Zwięzły", "Normalny", "Szczegółowy"],
                index=1
            )
            
            fight_club = st.checkbox("🥊 Fight Club", value=True)
            auto_vote = st.checkbox("🗳️ Auto głosowania", value=False)
        
        # Main chat area
        st.markdown(f"### Rozmowa z: **{st.session_state.selected_partner}**")
        
        # === NOWE: MOOD INDICATOR ===
        try:
            stan_spolki, cele = load_portfolio_data()
            portfolio_mood = analyze_portfolio_mood(stan_spolki, cele)
            
            # Wyświetl mood bar
            col_mood1, col_mood2, col_mood3 = st.columns([1, 3, 1])
            with col_mood1:
                st.markdown(f"### {portfolio_mood.get('emoji', '😐')}")
            with col_mood2:
                st.markdown(f"**Nastrój portfela:** {portfolio_mood.get('description', 'Neutralny')}")
                
                # Progress bar dla score
                score = portfolio_mood.get('score', 0)
                normalized_score = (score + 100) / 200  # -100..100 -> 0..1
                st.progress(normalized_score, text=f"Score: {score}/100")
            with col_mood3:
                with st.popover("ℹ️ Szczegóły"):
                    if portfolio_mood.get('highlights'):
                        st.markdown("**✨ Dobre znaki:**")
                        for h in portfolio_mood['highlights']:
                            st.markdown(f"- {h}")
                    
                    if portfolio_mood.get('warnings'):
                        st.markdown("**⚠️ Uwagi:**")
                        for w in portfolio_mood['warnings']:
                            st.markdown(f"- {w}")
            
            st.markdown("---")
        except:
            pass  # Cicho ignoruj błędy mood
        
        # === NOWE: PROAKTYWNE ALERTY (na stronie partnerów) ===
        try:
            stan_spolki, cele = load_portfolio_data()
            alerts = check_portfolio_alerts(stan_spolki, cele)

            # Pokazuj tylko najważniejsze (critical i warning)
            important_alerts = [a for a in alerts if a["severity"] in ["critical", "warning"]]

            if important_alerts:
                with st.expander(f"🚨 Aktywne alerty ({len(important_alerts)})", expanded=True):
                    for alert in important_alerts[:3]:  # Max 3 najważniejsze
                        if alert["severity"] == "critical":
                            st.error(f"**{alert['title']}** - {alert['message']}")
                        else:
                            st.warning(f"**{alert['title']}** - {alert['message']}")
                
                    if len(important_alerts) > 3:
                        st.caption(f"...i {len(important_alerts) - 3} więcej. Zobacz Dashboard.")
            else:
                with st.expander("✅ Status portfela", expanded=False):
                    st.success("**Brak aktywnych alertów** - Twój portfel wygląda stabilnie!")
                    st.caption("Monitoruję: spadki, wzrosty, wyceny, dźwignię, koncentrację i cele.")

            st.markdown("---")
        except:
            pass
        
        # === NOWE: SUGEROWANE PYTANIA ===
        if len(get_messages()) < 3:  # Pokazuj tylko gdy mało wiadomości
            try:
                stan_spolki, cele = load_portfolio_data()
                smart_questions = generate_smart_questions(stan_spolki, cele)
            
                if smart_questions:
                    with st.expander("💡 Sugerowane pytania (kliknij aby użyć)", expanded=True):
                        st.caption("AI przeanalizowało Twój portfel i sugeruje te pytania:")
                    
                    cols = st.columns(1)
                    for i, question in enumerate(smart_questions[:5]):
                        if cols[0].button(
                            question, 
                            key=f"smart_q_{i}",
                            width="stretch",
                            type="secondary"
                        ):
                            # Użyj pytania jako input
                            add_message({
                                "role": "user",
                                "content": question,
                                "avatar": "👤"
                            })
                            
                            # Generate responses
                            with st.spinner("🤖 AI myśli..."):
                                if 'ai_response_mode' in st.session_state:
                                    tryb_odpowiedzi = st.session_state.ai_response_mode
                                else:
                                    tryb_map = {"Zwięzły": "zwiezly", "Normalny": "normalny", "Szczegółowy": "szczegolowy"}
                                    tryb_odpowiedzi = tryb_map.get(tryb, "normalny")
                                
                                if st.session_state.selected_partner == "Wszyscy":
                                    # Placeholder dla odpowiedzi w czasie rzeczywistym
                                    response_container = st.empty()
                                    
                                    with st.spinner("🤔 Partnerzy rozmawiają..."):
                                        for resp in send_to_all_partners(question, stan_spolki, cele, tryb_odpowiedzi):
                                            # Formatuj wiadomość z emoji reakcji i flagą przerywania
                                            sentiment = resp.get('sentiment_emoji', '💬')
                                            is_interrupting = resp.get('is_interrupting', False)
                                            is_voting = resp.get('is_voting_summary', False)
                                        
                                        if is_voting:
                                            # Specjalne formatowanie dla podsumowania głosowania
                                            content = resp['response']
                                        elif is_interrupting:
                                            content = f"{sentiment} **[PRZERWANIE]** **{resp['partner']}**: {resp['response']}"
                                        else:
                                            content = f"{sentiment} **{resp['partner']}**: {resp['response']}"
                                        
                                        # Dodaj do historii
                                        add_message({
                                            "role": "assistant",
                                            "content": content,
                                            "avatar": resp['avatar'],
                                            "knowledge": resp.get('knowledge', [])
                                        })
                                        
                                        # Wyświetl natychmiast z avatarem
                                        with st.chat_message("assistant", avatar=resp['avatar']):
                                            st.markdown(content)
                                else:
                                    response, knowledge = send_to_ai_partner(
                                        st.session_state.selected_partner,
                                        question,
                                        stan_spolki,
                                        cele,
                                        tryb_odpowiedzi
                                    )
                                    avatar = "🤖"
                                    if st.session_state.selected_partner in PERSONAS:
                                        color_map = {
                                            '\033[94m': '📊', '\033[93m': '💼', '\033[96m': '💎',
                                            '\033[90m': '🛡', '\033[95m': '🔍', '\033[91m': '🌍', '\033[92m': '🎯'
                                        }
                                        color = PERSONAS[st.session_state.selected_partner].get('color_code', '')
                                        avatar = color_map.get(color, "🤖")
                                    
                                    add_message({
                                        "role": "assistant",
                                        "content": f"**{st.session_state.selected_partner}**: {response}",
                                        "avatar": avatar,
                                        "knowledge": knowledge  # Zapisz knowledge dla późniejszego wyświetlenia
                                    })
                            
                            st.rerun()
            except Exception as e:
                pass  # Cicho ignoruj błędy sugestii
        
        # Display messages
        chat_container = st.container()
        with chat_container:
            for msg in get_messages():
                with st.chat_message(msg["role"], avatar=msg.get("avatar", "🤖")):
                    st.markdown(msg["content"])
                    
                    # Wyświetl źródła wiedzy jeśli są
                    if msg["role"] == "assistant" and msg.get("knowledge"):
                        display_knowledge_sources(msg["knowledge"])
        
        # Input area
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.chat_input("Napisz wiadomość do Partnerów...")
        
        with col2:
            if st.button("📎"):
                st.info("Załączniki wkrótce!")
        
        # Handle user input
        if user_input:
            # Add user message
            add_message({
                "role": "user",
                "content": user_input,
                "avatar": "👤"
            })
        
            # Get current portfolio data for context
            try:
                stan_spolki, cele = load_portfolio_data()
            except:
                stan_spolki, cele = None, None
        
            # Generate real AI responses
            # Pobierz tryb odpowiedzi z session_state (z ustawień) lub z local radio
            if 'ai_response_mode' in st.session_state:
                tryb_odpowiedzi = st.session_state.ai_response_mode
            else:
                # Fallback na lokalny wybór
                tryb_map = {
                "Zwięzły": "zwiezly",
                "Normalny": "normalny",
                "Szczegółowy": "szczegolowy"
                }
                tryb_odpowiedzi = tryb_map.get(tryb, "normalny")
        
                if st.session_state.selected_partner == "Wszyscy":
                    # Response from all partners - jeden za drugim, wyświetlaj na żywo
                    with st.spinner("🤔 Partnerzy rozmawiają..."):
                        for resp in send_to_all_partners(user_input, stan_spolki, cele, tryb_odpowiedzi):
                            # Formatuj wiadomość z emoji reakcji i flagą przerywania
                            sentiment = resp.get('sentiment_emoji', '💬')
                            is_interrupting = resp.get('is_interrupting', False)
                            is_voting = resp.get('is_voting_summary', False)
                            
                            if is_voting:
                                # Specjalne formatowanie dla podsumowania głosowania
                                content = resp['response']
                            elif is_interrupting:
                                content = f"{sentiment} **[PRZERWANIE]** **{resp['partner']}**: {resp['response']}"
                            else:
                                content = f"{sentiment} **{resp['partner']}**: {resp['response']}"
                            
                            # Dodaj do historii
                            add_message({
                                "role": "assistant",
                                "content": content,
                                "avatar": resp['avatar'],
                                "knowledge": resp.get('knowledge', [])
                            })
                            
                            # Wyświetl natychmiast z avatarem
                            with st.chat_message("assistant", avatar=resp['avatar']):
                                st.markdown(content)
                
                else:
                    # Single partner response
                    with st.spinner(f"💭 {st.session_state.selected_partner} myśli..."):
                        response, knowledge = send_to_ai_partner(
                            st.session_state.selected_partner,
                            user_input,
                            stan_spolki,
                            cele,
                            tryb_odpowiedzi
                        )
                
                    avatar = {
                        "Marek": "🎭",
                        "Ania": "🎨", 
                        "Kasia": "📊",
                        "Tomek": "🔥"
                    }.get(st.session_state.selected_partner, "🤖")
                
                    add_message({
                        "role": "assistant",
                        "content": f"**{st.session_state.selected_partner}**: {response}",
                        "avatar": avatar,
                        "knowledge": knowledge  # Zapisz knowledge
                    })
        
                st.rerun()
        
        # Special commands
        st.markdown("---")
        st.markdown("### 🎯 Szybkie akcje")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗳️ Rozpocznij głosowanie", width="stretch"):
                add_message({
                    "role": "system",
                    "content": "📋 **Nowe głosowanie** - Propozycja do głosowania otworzona",
                    "avatar": "🤖"
                })
                st.rerun()
        
        with col2:
            if st.button("🎯 Poproś o doradztwo", width="stretch"):
                add_message({
                    "role": "system",
                    "content": "🤖 **AI Advisor** - Generuję 3 scenariusze...",
                    "avatar": "🤖"
                })
                st.rerun()
        
        with col3:
            if st.button("🧹 Wyczyść chat", width="stretch"):
                clear_messages()
                st.rerun()
        
        # Drugi rząd przycisków - funkcje pamięci AI
        if MEMORY_OK:
            st.markdown("#### 🧠 Pamięć AI")
            col4, col5, col6 = st.columns(3)
        
            with col4:
                if st.button("💾 Zapisz decyzję", width="stretch", help="Zapisz ostatnią rekomendację AI do pamięci"):
                    # Znajdź ostatnią odpowiedź AI
                    ai_messages = [m for m in get_messages() if m["role"] == "assistant"]
                    if ai_messages:
                        last_msg = ai_messages[-1]
                        content = last_msg["content"]
                        
                        # Proste parsowanie - szukamy tickera i typu decyzji
                        # TODO: Użytkownik powinien podać ticker i typ ręcznie
                        with st.form("save_decision_form"):
                            st.write("Zapisz decyzję do pamięci:")
                            ticker = st.text_input("Ticker (np. AAPL, BTC)", "")
                            decision_type = st.selectbox("Typ", ["BUY", "SELL", "HOLD", "WARN", "RECOMMEND"])
                            price = st.number_input("Aktualna cena", min_value=0.01, value=100.0)
                            reasoning = st.text_area("Uzasadnienie", content[:200])
                            
                            submitted = st.form_submit_button("💾 Zapisz")
                            if submitted and ticker:
                                # Zapisz dla wszystkich person które odpowiadały
                                for persona_name in PERSONAS.keys():
                                    if persona_name in content:
                                        pmm.record_decision(
                                            persona_name=persona_name,
                                            decision_type=decision_type,
                                            ticker=ticker,
                                            reasoning=reasoning,
                                            current_price=price,
                                            confidence=0.7
                                        )
                                st.success(f"✓ Decyzja zapisana: {decision_type} {ticker}")
                                st.rerun()
                    else:
                        st.info("Brak odpowiedzi AI do zapisania")
        
            with col5:
                if st.button("🏆 Leaderboard", width="stretch", help="Zobacz ranking wiarygodności person"):
                    st.session_state.show_leaderboard = not st.session_state.get("show_leaderboard", False)
                    st.rerun()
        
            with col6:
                if st.button("🔍 Audit decyzji", width="stretch", help="Oceń stare decyzje"):
                    st.session_state.show_audit = not st.session_state.get("show_audit", False)
                    st.rerun()
        
            # Leaderboard display
            if st.session_state.get("show_leaderboard", False):
                with st.expander("🏆 Ranking Wiarygodności AI Partnerów", expanded=True):
                    leaderboard = pmm.get_leaderboard()
                    if leaderboard:
                        for i, entry in enumerate(leaderboard, 1):
                            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                            st.write(f"{emoji} **{entry['persona']}**: {entry['credibility']*100:.0f}% "
                                    f"({entry['correct']}/{entry['total']} trafnych)")
                    else:
                        st.info("Brak danych - persony nie podjęły jeszcze rozliczonych decyzji")
        
            # Audit panel
            if st.session_state.get("show_audit", False):
                with st.expander("🔍 Panel Auditu Decyzji", expanded=True):
                    pending = pmm.get_all_pending_decisions()
                    if pending:
                        st.write(f"**{len(pending)} nierozliczonych decyzji:**")
                        for item in pending[:10]:
                            dec = item["decision"]
                            with st.container():
                                col_a, col_b = st.columns([3, 1])
                                with col_a:
                                    st.write(f"**{item['persona']}** → {dec['decision_type']} {dec['ticker']} @ {dec['current_price']}")
                                    st.caption(f"{dec['date']}: {dec['reasoning'][:80]}...")
                                with col_b:
                                    if st.button("✓ Oceń", key=f"audit_{dec['id']}"):
                                        st.session_state[f"auditing_{dec['id']}"] = True
                                        st.rerun()
                                
                                # Formularz oceny
                                if st.session_state.get(f"auditing_{dec['id']}", False):
                                    with st.form(f"form_{dec['id']}"):
                                        current_price = st.number_input("Aktualna cena", value=dec['current_price'])
                                        outcome = st.text_input("Co się stało?", "")
                                        impact = st.number_input("Wpływ (PLN)", value=0.0)
                                        
                                        if st.form_submit_button("💾 Zapisz audit"):
                                            result = pmm.audit_decision(dec['id'], current_price, outcome, impact)
                                            if result:
                                                st.success(f"✓ {'Poprawna' if result['was_correct'] else 'Błędna'} decyzja ({result['result_pct']:+.1f}%)")
                                                del st.session_state[f"auditing_{dec['id']}"]
                                                st.rerun()
                                st.markdown("---")
                    else:
                        st.info("Brak nierozliczonych decyzji")
        
    # === TAB 2: PROFILE PARTNERÓW ===
    with tab_profiles:
        st.markdown("### 📋 Profile Partnerów")
        st.caption("Poznaj każdego partnera i sprawdź wagi głosów z Kodeksu Spółki")
        
        if not IMPORTS_OK or not PERSONAS:
            st.warning("⚠️ Nie można załadować danych partnerów")
            return
        
        # Wczytaj wagi głosu z kodeksu spółki
        wagi_z_kodeksu = wczytaj_wagi_glosu_z_kodeksu()
        
        if not wagi_z_kodeksu:
            st.warning("⚠️ Nie można wczytać wag głosu z kodeksu spółki")
            return
        
        # Przygotuj listę partnerów z wagami głosu z KODEKSU
        partners_with_weights = []
        for name, config in PERSONAS.items():
            # Teraz POKAZUJEMY RÓWNIEŻ Partnera Zarządzającego (JA)!
            
            # Pobierz wagę z kodeksu
            weight = wagi_z_kodeksu.get(name, 0.0)  # Już jest w procentach (35.0, nie 0.35)
            
            partners_with_weights.append((name, config, weight))
        
        # Sortuj według wagi głosu (malejąco)
        partners_with_weights.sort(key=lambda x: x[2], reverse=True)
        total_weight = sum(w for _, _, w in partners_with_weights)
        
        # Informacja o sumie
        st.info(f"📊 **Łączna suma głosów: {total_weight:.0f}%** (z Kodeksu Spółki)")
        
        # Informacja o bonusach
        bonus_pool = 100 - total_weight
        if bonus_pool > 0:
            st.success(f"🎁 **Pula bonusowa: {bonus_pool:.0f}%** - do zdobycia za dobre decyzje!")
            st.caption("💡 Partnerzy mogą zdobywać dodatkowe % głosu jako nagrody za trafne prognozy i wartościowe decyzje")
        
        # Opcja do edycji wag
        if st.checkbox("⚙️ Tryb edycji wag głosu", help="Zmień % głosu partnerów i zapisz do Kodeksu"):
            st.warning("⚠️ Zmienione wartości zostaną zapisane do `kodeks_spolki.txt`")
            
            with st.form("edit_voting_weights"):
                st.markdown("#### Edytuj wagi głosu:")
                
                nowe_wagi = {}
                
                # Podziel na głównych partnerów i radę
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown("**👥 Główni Partnerzy:**")
                    for name, config, current_weight in partners_with_weights:
                        # Główni: Partner Zarządzający, Partner Strategiczny, ds. Jakości, ds. Aktywów Cyfrowych
                        if any(keyword in name for keyword in ["Zarządzający", "Strategiczny", "Jakości", "Aktywów Cyfrowych"]):
                            nowe_wagi[name] = st.number_input(
                                f"{name}",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(current_weight),
                                step=1.0,
                                key=f"edit_{name}"
                            )
                
                with col_right:
                    st.markdown("**🏛️ Rada Nadzorcza & Konsultanci:**")
                    for name, config, current_weight in partners_with_weights:
                        # Rada: Benjamin Graham, Philip Fisher, George Soros, Warren Buffett, Changpeng Zhao (CZ)
                        if any(keyword in name for keyword in ["Graham", "Fisher", "Soros", "Buffett", "Zhao"]):
                            nowe_wagi[name] = st.number_input(
                                f"{name}",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(current_weight),
                                step=0.5,
                                key=f"edit_{name}"
                            )
                
                suma_nowych = sum(nowe_wagi.values())
                st.caption(f"Suma nowych wag: {suma_nowych:.1f}%")
                
                if suma_nowych > 100:
                    st.error(f"⚠️ Suma przekracza 100%! (jest {suma_nowych:.1f}%)")
                elif suma_nowych < 95:
                    st.warning(f"⚠️ Suma jest mniejsza niż 95% (jest {suma_nowych:.1f}%)")
                
                submitted = st.form_submit_button("💾 Zapisz do Kodeksu")
                if submitted:
                    if zapisz_wagi_glosu_do_kodeksu(nowe_wagi):
                        st.success("✅ Wagi głosu zapisane do kodeksu spółki!")
                        st.rerun()
                    else:
                        st.error("❌ Błąd zapisu do kodeksu")
        
        st.markdown("---")
        
        # Wyświetl każdego partnera
        for name, config, weight in partners_with_weights:
            percentage = (weight / total_weight * 100) if total_weight > 0 else 0
            
            # Specjalne oznaczenie dla Ciebie (Partner Zarządzający)
            if "(JA)" in name:
                emoji_prefix = "👤👑"
                subtitle = f"{weight:.1f}% głosu | TY - Głos rozstrzygający"
            else:
                emoji_prefix = config.get('emoji', '🤖')
                subtitle = f"{weight:.1f}% głosu"
            
            with st.expander(f"{emoji_prefix} {name} - {subtitle}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Wyświetl system instruction jako opis roli
                    system_inst = config.get('system_instruction', 'Brak opisu')
                    st.markdown(f"**👤 Rola:** {system_inst[:200]}...")
                    
                    # Ukryty cel jako spoiler (tylko dla AI)
                    if "(JA)" not in name:
                        if st.checkbox("Pokaż ukryty cel", key=f"spoiler_{name}"):
                            st.info(f"🎭 **Ukryty cel:** {config.get('ukryty_cel', 'Brak')}")
                    else:
                        st.success("🎯 **To TY!** Masz głos rozstrzygający w remisach.")
                
                with col2:
                    st.metric("% głosu", f"{weight:.1f}%", help="Waga głosu z Kodeksu Spółki")
                    st.progress(weight / 100)
                    
                    # Memory stats jeśli dostępne (tylko dla AI)
                    if MEMORY_OK and "(JA)" not in name:
                        try:
                            memory_data = load_persona_memory()
                            if name in memory_data:
                                persona_data = memory_data[name]
                                stats = persona_data.get('stats', {})
                                emotions = persona_data.get('emotional_state', {})
                                
                                st.caption(f"💬 {stats.get('sessions_participated', 0)} sesji")
                                st.caption(f"📝 {stats.get('decisions_made', 0)} decyzji")
                                st.caption(f"😊 Nastrój: {emotions.get('current_mood', 'neutral')}")
                        except Exception as e:
                            # Brak danych partnera w pamięci - pomiń
                            st.caption("💬 Nowy partner")
        
        st.markdown("---")
        st.info(f"👥 **Rada składa się z {len(partners_with_weights)} członków** (włącznie z Tobą jako Partner Zarządzający)")
        st.caption("� Wagi głosów pochodzą z Kodeksu Spółki")
        st.caption("🎁 30% puli bonusowej - partnerzy mogą zdobywać dodatkowe % za trafne decyzje i wartościowe analizy")
        st.caption("📜 Zmiany wag są zapisywane bezpośrednio w pliku `kodeks_spolki.txt`")

def show_analytics_page(stan_spolki):
    """Strona z analityką"""
    st.title("📈 Zaawansowana Analityka & Ryzyko")
    
    # Check if we have historical data - używamy daily_snapshots.json
    history_file = "daily_snapshots.json"
    
    if not os.path.exists(history_file):
        st.warning("⚠️ Brak danych historycznych. Utwórz pierwszy snapshot w zakładce 📸 Snapshots.")
        st.info("💡 TIP: System automatycznie zapisuje snapshoty codziennie o 21:00 (jeśli skonfigurujesz Task Scheduler).")
        
        # Pokaż instrukcję
        with st.expander("📝 Jak utworzyć snapshot?"):
            st.markdown("""
            **Opcja 1: Manualnie w aplikacji**
            - Przejdź do zakładki 📸 Snapshots
            - Kliknij "📸 Utwórz Nowy Snapshot"
            
            **Opcja 2: Z linii komend**
            ```bash
            python daily_snapshot.py
            ```
            
            **Opcja 3: Automatycznie (Windows Task Scheduler)**
            ```bash
            run_daily_snapshot.bat  # Uruchom codziennie o 21:00
            ```
            """)
        return
    
    try:
        # Load history z daily_snapshots
        import daily_snapshot as ds
        history = ds.load_snapshot_history()
        
        if len(history) < 2:
            st.warning(f"⚠️ Za mało danych ({len(history)} snapshot). Potrzeba minimum 2 dla analizy ryzyka.")
            st.info("💡 Utwórz więcej snapshotów aby zobaczyć analizę (zakładka 📸 Snapshots)")
            return
        
        st.success(f"✅ Załadowano {len(history)} snapshots historii portfela")
        
        # Create analytics
        analyzer = RiskAnalytics(stan_spolki, history)
        report = analyzer.generate_risk_report()
        metrics = report.get('metrics', {})
        
        # Display metrics in columns
        st.markdown("### 🎯 Kluczowe Metryki Ryzyka")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sharpe = metrics.get('sharpe_ratio', 0)
            delta_color = "normal" if sharpe > 1 else "inverse"
            st.metric(
                label="📊 Sharpe Ratio",
                value=f"{sharpe:.3f}",
                delta="Dobry" if sharpe > 1 else "Słaby",
                delta_color=delta_color
            )
            st.caption(">1 = dobre, >2 = doskonałe")
        
        with col2:
            sortino = metrics.get('sortino_ratio', 0)
            st.metric(
                label="📉 Sortino Ratio",
                value=f"{sortino:.3f}",
                delta="Dobry" if sortino > 1.5 else "Słaby",
                delta_color="normal" if sortino > 1.5 else "inverse"
            )
            st.caption("Uwzględnia tylko straty")
        
        with col3:
            max_dd = metrics.get('max_drawdown_percent', 0)
            st.metric(
                label="⚠️ Max Drawdown",
                value=f"{max_dd:.2f}%",
                delta="Wysokie" if max_dd > 20 else "OK",
                delta_color="inverse" if max_dd > 20 else "normal"
            )
            st.caption("Największy spadek")
        
        with col4:
            var_95 = metrics.get('var_95', 0)
            st.metric(
                label="💔 VaR (95%)",
                value=f"{var_95:.2f}%",
                delta="Ryzykowne" if var_95 > 10 else "OK",
                delta_color="inverse" if var_95 > 10 else "normal"
            )
            st.caption("Max strata z 95% pewnością")
        
        st.markdown("---")
        
        # Additional metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Dodatkowe Metryki")
            
            vol = metrics.get('annual_volatility_percent', 0)
            st.metric("🌊 Zmienność roczna", f"{vol:.2f}%")
            
            ret = metrics.get('total_return_percent', 0)
            st.metric("💰 Całkowity zwrot", f"{ret:+.2f}%")
            
            beta = metrics.get('beta', 0)
            st.metric("📈 Beta (vs S&P 500)", f"{beta:.3f}")
            st.caption("<1 = mniej zmienne, >1 = bardziej zmienne")
        
        with col2:
            st.markdown("### 🎲 Ocena Ryzyka")
            
            level, score, description = analyzer.risk_score()
            
            # Progress bar dla risk score
            st.markdown(f"**Poziom ryzyka:** {level}")
            st.progress(score / 100)
            st.caption(f"Score: {score}/100")
            
            st.info(description)
        
        st.markdown("---")
        
        # Chart: Portfolio value over time
        st.markdown("### 📈 Wartość Portfela w Czasie")
        
        # Parsuj daty i wartości - obsłuż różne formaty
        dates = []
        values = []
        
        for h in history:
            # Data
            if 'timestamp' in h:
                dates.append(datetime.fromisoformat(h['timestamp']))
            elif 'date' in h:
                dates.append(datetime.fromisoformat(h['date']))
            
            # Wartość netto
            if 'totals' in h and 'net_worth_pln' in h['totals']:
                values.append(h['totals']['net_worth_pln'])
            elif 'wartosc_netto' in h:
                values.append(h['wartosc_netto'])
            elif 'value' in h:
                values.append(h['value'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Wartość Netto',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Wartość Netto Portfela",
            xaxis_title="Data",
            yaxis_title="Wartość (PLN)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width="stretch")
        
    except Exception as e:
        st.error(f"❌ Błąd podczas analizy: {e}")
        import traceback
        st.code(traceback.format_exc())

def show_timeline_page(stan_spolki):
    """Strona z animated timeline"""
    st.title("🕐 Animated Timeline - Ewolucja Portfela")
    
    # Używaj nowego systemu daily snapshots
    try:
        import daily_snapshot as ds
        import benchmark_comparison as bench
    except ImportError as e:
        st.error(f"❌ Błąd importu: {e}")
        return
    
    history = ds.load_snapshot_history()
    
    if len(history) < 2:
        st.warning(f"⚠️ Za mało danych ({len(history)} snapshot). Potrzeba minimum 2 dla timeline.")
        st.info("""
        **Jak zgromadzić historię?**
        1. System zapisuje snapshot codziennie o 21:00 (jeśli skonfigurujesz Windows Task)
        2. Możesz też ręcznie: `python daily_snapshot.py`
        3. Lub w zakładce 📸 Snapshots → Utwórz snapshot
        """)
        return
    
    st.success(f"✅ Załadowano {len(history)} snapshots - generuję timeline...")
    
    # Tabs: Portfolio vs Benchmarki
    tab1, tab2 = st.tabs(["📊 Wartość Portfela", "🏆 Porównanie z Benchmarkami"])
    
    with tab1:
        # Przygotuj dane do wykresu
        dates = [datetime.fromisoformat(h['date']) for h in history]
        values = [h['totals']['net_worth_pln'] for h in history]
        
        # Main chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Wartość Netto',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Wartość Portfela w Czasie",
            xaxis_title="Data",
            yaxis_title="Wartość (PLN)",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width="stretch")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        initial_value = values[0]
        current_value = values[-1]
        growth = (current_value - initial_value) / initial_value * 100
        
        with col1:
            st.metric("📊 Wartość początkowa", format_currency(initial_value))
        with col2:
            st.metric("💰 Wartość aktualna", format_currency(current_value), delta=f"{growth:+.2f}%")
        with col3:
            st.metric("📈 Liczba snapshots", len(history))
    
    with tab2:
        st.subheader("🏆 Twój Portfel vs Rynek")
        st.info("💡 Porównanie znormalizowane do 100 punktów na start okresu")
        
        with st.spinner("⏳ Pobieranie danych benchmarków..."):
            comparison_data = bench.prepare_comparison_data(history)
        
        if "error" in comparison_data:
            st.error(f"❌ {comparison_data['error']}")
        else:
            # Wykres porównawczy
            fig = go.Figure()
            
            # Portfolio
            portfolio = comparison_data['portfolio']
            fig.add_trace(go.Scatter(
                x=[datetime.fromisoformat(d) for d in portfolio['dates']],
                y=portfolio['values'],
                mode='lines+markers',
                name=portfolio['name'],
                line=dict(color=portfolio['color'], width=4),
                marker=dict(size=8)
            ))
            
            # Benchmarki
            for bench_id, bench_data in comparison_data['benchmarks'].items():
                fig.add_trace(go.Scatter(
                    x=[datetime.fromisoformat(d) for d in bench_data['dates']],
                    y=bench_data['values'],
                    mode='lines',
                    name=bench_data['name'],
                    line=dict(color=bench_data['color'], width=2, dash='dot')
                ))
            
            fig.update_layout(
                title="Porównanie Wydajności (Normalized to 100)",
                xaxis_title="Data",
                yaxis_title="Wartość Znormalizowana (start = 100)",
                height=600,
                hovermode='x unified',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            st.plotly_chart(fig, width="stretch")
            
            # Statystyki porównawcze
            st.markdown("---")
            st.markdown("### 📊 Statystyki Porównawcze")
            
            stats = bench.calculate_comparison_stats(history)
            
            if "error" not in stats:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "💼 Twój Portfel",
                        f"{stats['portfolio']['total_return_pct']:+.2f}%",
                        delta=f"{stats['portfolio']['days']} dni"
                    )
                
                # Benchmarki
                cols = [col2, col3, col4]
                for idx, (bench_id, bench_stats) in enumerate(stats['benchmarks'].items()):
                    if idx < 3:
                        with cols[idx]:
                            emoji = "🟢" if bench_stats['outperformance_pct'] > 0 else "🔴"
                            st.metric(
                                f"{emoji} {bench_stats['name']}",
                                f"{bench_stats['total_return_pct']:+.2f}%",
                                delta=f"{bench_stats['outperformance_pct']:+.2f}%"
                            )
                
                st.markdown("---")
                st.caption("💡 Delta pokazuje Twoją przewagę (+) lub stratę (-) względem benchmarku")

def show_simulations_page(stan_spolki):
    """Strona z symulacjami"""
    st.title("🎮 Symulator Portfela - Testuj Scenariusze")
    
    try:
        from portfolio_simulator import PortfolioSimulator, ScenarioAnalyzer
    except ImportError:
        st.error("❌ Nie można załadować modułu portfolio_simulator")
        return
    
    # Initialize simulator
    simulator = PortfolioSimulator(stan_spolki)
    
    # Tabs dla różnych typów symulacji
    tab1, tab2, tab3 = st.tabs(["� Scenariusze Rynkowe", "💰 Transakcje", "📊 Porównanie"])
    
    with tab1:
        st.markdown("### 📈 Symuluj Scenariusze Rynkowe")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🐂 Scenariusz Bullish")
            st.info("Wszystkie aktywa rosną o 20%")
            
            if st.button("▶️ Uruchom Bullish", key="bullish", width="stretch"):
                result = simulator.simulate_bullish_scenario()
                
                st.success("✅ Symulacja zakończona!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Wartość przed", format_currency(result['before']['wartosc_netto']))
                with col_b:
                    st.metric(
                        "Wartość po",
                        format_currency(result['after']['wartosc_netto']),
                        delta=f"+{result['zmiana_procent']:.2f}%"
                    )
                
                st.json(result['zmiany'])
        
        with col2:
            st.markdown("#### 🐻 Scenariusz Bearish")
            st.info("Wszystkie aktywa spadają o 20%")
            
            if st.button("▶️ Uruchom Bearish", key="bearish", width="stretch"):
                result = simulator.simulate_bearish_scenario()
                
                st.warning("⚠️ Symulacja spadku!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Wartość przed", format_currency(result['before']['wartosc_netto']))
                with col_b:
                    st.metric(
                        "Wartość po",
                        format_currency(result['after']['wartosc_netto']),
                        delta=f"{result['zmiana_procent']:.2f}%"
                    )
                
                st.json(result['zmiany'])
    
    with tab2:
        st.markdown("### 💰 Symuluj Transakcje")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🛒 Kupno")
            ticker_buy = st.text_input("Ticker", key="buy_ticker", value="AAPL")
            quantity_buy = st.number_input("Ilość", min_value=1, value=10, key="buy_qty")
            price_buy = st.number_input("Cena za sztukę (PLN)", min_value=0.01, value=100.0, key="buy_price")
            
            if st.button("💳 Kup", width="stretch"):
                result = simulator.simulate_buy(ticker_buy, quantity_buy, price_buy)
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.metric(
                        "Wpływ na wartość",
                        format_currency(result['wplyw_na_wartosc']),
                        delta=f"{result['zmiana_procent']:+.2f}%"
                    )
                else:
                    st.error(f"❌ {result['message']}")
        
        with col2:
            st.markdown("#### 💸 Sprzedaż")
            ticker_sell = st.text_input("Ticker", key="sell_ticker", value="AAPL")
            quantity_sell = st.number_input("Ilość", min_value=1, value=5, key="sell_qty")
            price_sell = st.number_input("Cena za sztukę (PLN)", min_value=0.01, value=120.0, key="sell_price")
            
            if st.button("💰 Sprzedaj", width="stretch"):
                result = simulator.simulate_sell(ticker_sell, quantity_sell, price_sell)
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.metric(
                        "Wpływ na wartość",
                        format_currency(result['wplyw_na_wartosc']),
                        delta=f"{result['zmiana_procent']:+.2f}%"
                    )
                    
                    if result.get('zysk_strata'):
                        profit = result['zysk_strata']
                        st.metric(
                            "Zysk/Strata",
                            format_currency(profit),
                            delta="Zysk" if profit > 0 else "Strata"
                        )
                else:
                    st.error(f"❌ {result['message']}")
        
        # Reset button
        st.markdown("---")
        if st.button("🔄 Reset Symulacji", width="stretch"):
            simulator.reset()
            st.success("✅ Symulacja zresetowana do stanu początkowego")
    
    with tab3:
        st.markdown("### 📊 Porównaj Scenariusze")
        st.info("🚧 Funkcja w budowie - będzie pokazywać porównanie różnych scenariuszy")
        
        # TODO: Implement scenario comparison
        st.markdown("""
        Tutaj będzie można:
            - Porównać wyniki różnych scenariuszy
        - Zobaczyć wykres zmian wartości
        - Analizować wpływ poszczególnych transakcji
        - Eksportować wyniki do raportu
        """)

# =====================================================
# KREDYTY PAGE
# =====================================================

def load_kredyty():
    """Wczytaj kredyty z pliku JSON"""
    if PERSISTENT_OK:
        data = load_persistent_data('kredyty.json')
        if data is not None:
            kredyty = data.get('kredyty', [])
            return kredyty if kredyty is not None else []
    
    # Fallback
    try:
        with open('kredyty.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            kredyty = data.get('kredyty', [])
            return kredyty if kredyty is not None else []
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"Błąd wczytywania kredytów: {e}")
        return []

def get_suma_kredytow():
    """Pobierz sumę pozostałych długów z kredyty.json"""
    kredyty = load_kredyty()
    return sum(k['kwota_poczatkowa'] - k['splacono'] for k in kredyty)

def get_srednia_wyplata(liczba_miesiecy=3, wyplaty=None):
    """Oblicz średnią wypłatę z ostatnich N miesięcy"""
    if wyplaty is None:
        wyplaty = load_wyplaty()
    if not wyplaty:
        return 0
    
    ostatnie = wyplaty[:liczba_miesiecy]
    if ostatnie:
        return sum(w['kwota'] for w in ostatnie) / len(ostatnie)
    return 0

def get_suma_wydatkow_stalych(wydatki=None):
    """Pobierz sumę stałych wydatków miesięcznych z wydatki.json"""
    if wydatki is None:
        wydatki = load_wydatki()
    return sum(w['kwota'] for w in wydatki if not w.get('nadprogramowy', False))

def get_suma_wydatkow_nadprogramowych(wydatki=None):
    """Pobierz sumę wydatków nadprogramowych z wydatki.json"""
    if wydatki is None:
        wydatki = load_wydatki()
    return sum(w['kwota'] for w in wydatki if w.get('nadprogramowy', False))

def save_kredyty(kredyty):
    """Zapisz kredyty do pliku JSON"""
    if PERSISTENT_OK:
        return save_persistent_data('kredyty.json', {'kredyty': kredyty})
    
    # Fallback
    try:
        with open('kredyty.json', 'w', encoding='utf-8') as f:
            json.dump({'kredyty': kredyty}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Błąd zapisu kredytów: {e}")
        return False

def save_cele(cele):
    """Zapisz cele do pliku JSON"""
    if PERSISTENT_OK:
        return save_persistent_data('cele.json', cele)
    
    # Fallback
    try:
        with open('cele.json', 'w', encoding='utf-8') as f:
            json.dump(cele, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Błąd zapisu celów: {e}")
        return False

def load_wyplaty():
    """Wczytaj wypłaty z pliku JSON"""
    if PERSISTENT_OK:
        data = load_persistent_data('wyplaty.json')
        if isinstance(data, dict):
            wyplaty = data.get('wyplaty', [])
            wyplaty = wyplaty if wyplaty is not None else []
        else:
            wyplaty = [] if data is None else (data if isinstance(data, list) else [])
    else:
        # Fallback - stary system
        if 'wyplaty_data' in st.session_state:
            wyplaty = st.session_state['wyplaty_data']
        else:
            try:
                with open('wyplaty.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    wyplaty = data.get('wyplaty', [])
                    wyplaty = wyplaty if wyplaty is not None else []
                    st.session_state['wyplaty_data'] = wyplaty
            except FileNotFoundError:
                wyplaty = []
            except Exception as e:
                st.error(f"Błąd wczytywania wypłat: {e}")
                wyplaty = []
    
    # MIGRACJA: dodaj pole 'typ' do starych wpisów
    migrated = False
    for w in wyplaty:
        if 'typ' not in w:
            w['typ'] = 'Wypłata'
            migrated = True
    
    # Zapisz po migracji
    if migrated:
        save_wyplaty(wyplaty)
    
    return wyplaty

def save_wyplaty(wyplaty):
    """Zapisz wypłaty do pliku JSON"""
    if PERSISTENT_OK:
        #清除 cache aby uniknąć konfliktu ze starymi danymi
        st.session_state.pop('wyplaty_data', None)
        return save_persistent_data('wyplaty.json', {'wyplaty': wyplaty})
    
    # Fallback - stary system
    try:
        with open('wyplaty.json', 'w', encoding='utf-8') as f:
            json.dump({'wyplaty': wyplaty}, f, indent=2, ensure_ascii=False)
        st.session_state['wyplaty_data'] = wyplaty
        return True
    except Exception as e:
        # Streamlit Cloud - tylko session
        st.session_state['wyplaty_data'] = wyplaty
        st.warning(f"⚠️ Dane zapisane tymczasowo w sesji. Filesystem read-only: {e}")
        return True  # Zwróć True bo zapisaliśmy do session


# ============================================================================
# TRANSACTIONS LOG - Centralny dziennik transakcji
# ============================================================================

def load_transactions():
    """Wczytaj transakcje z pliku JSON"""
    if PERSISTENT_OK:
        data = load_persistent_data('transactions.json')
        if isinstance(data, dict):
            transactions = data.get('transactions', [])
        else:
            transactions = [] if data is None else (data if isinstance(data, list) else [])
    else:
        # Fallback
        if 'transactions_data' in st.session_state:
            transactions = st.session_state['transactions_data']
        else:
            try:
                with open('transactions.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    transactions = data.get('transactions', [])
                    st.session_state['transactions_data'] = transactions
            except FileNotFoundError:
                transactions = []
            except Exception as e:
                st.error(f"Błąd wczytywania transakcji: {e}")
                transactions = []
    
    return transactions


def save_transactions(transactions):
    """Zapisz transakcje do pliku JSON"""
    if PERSISTENT_OK:
        st.session_state.pop('transactions_data', None)
        return save_persistent_data('transactions.json', {'transactions': transactions})
    
    # Fallback
    try:
        with open('transactions.json', 'w', encoding='utf-8') as f:
            json.dump({'transactions': transactions}, f, indent=2, ensure_ascii=False)
        st.session_state['transactions_data'] = transactions
        return True
    except Exception as e:
        st.session_state['transactions_data'] = transactions
        st.warning(f"⚠️ Transakcje zapisane w sesji. Filesystem read-only: {e}")
        return True


def add_transaction(typ, kategoria, kwota, opis="", metadata=None):
    """
    Dodaj nową transakcję do dziennika
    
    Args:
        typ: 'income' lub 'expense' lub 'transfer'
        kategoria: np. 'salary', 'investment', 'loan_payment', 'crypto_buy'
        kwota: wartość transakcji (dodatnia)
        opis: dodatkowy opis
        metadata: dict z dodatkowymi danymi (np. {'asset': 'BTC', 'price': 95000})
    """
    from datetime import datetime
    
    transactions = load_transactions()
    
    transaction = {
        'id': str(datetime.now().timestamp()),
        'data': datetime.now().isoformat(),
        'typ': typ,  # income/expense/transfer
        'kategoria': kategoria,
        'kwota': abs(kwota),
        'opis': opis,
        'metadata': metadata or {}
    }
    
    transactions.append(transaction)
    
    # Sortuj od najnowszych
    transactions.sort(key=lambda x: x['data'], reverse=True)
    
    save_transactions(transactions)
    return transaction


def get_transactions_summary(transactions, start_date=None, end_date=None):
    """
    Oblicz podsumowanie transakcji w danym okresie
    
    Returns:
        dict z income, expenses, net_flow, by_category
    """
    from datetime import datetime
    
    filtered = transactions
    
    if start_date:
        filtered = [t for t in filtered if t['data'] >= start_date.isoformat()]
    if end_date:
        filtered = [t for t in filtered if t['data'] <= end_date.isoformat()]
    
    income = sum(t['kwota'] for t in filtered if t['typ'] == 'income')
    expenses = sum(t['kwota'] for t in filtered if t['typ'] == 'expense')
    
    # Grupuj po kategoriach
    from collections import defaultdict
    by_category = defaultdict(float)
    for t in filtered:
        by_category[t['kategoria']] += t['kwota'] if t['typ'] == 'income' else -t['kwota']
    
    return {
        'income': income,
        'expenses': expenses,
        'net_flow': income - expenses,
        'by_category': dict(by_category),
        'count': len(filtered)
    }

def load_wydatki():
    """Wczytaj wydatki z pliku JSON"""
    if PERSISTENT_OK:
        data = load_persistent_data('wydatki.json')
        if isinstance(data, dict):
            wydatki = data.get('wydatki', [])
            return wydatki if wydatki is not None else []
        return [] if data is None else (data if isinstance(data, list) else [])
    
    # Fallback - stary system
    if 'wydatki_data' in st.session_state:
        return st.session_state['wydatki_data']
    
    try:
        with open('wydatki.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            wydatki = data.get('wydatki', [])
            st.session_state['wydatki_data'] = wydatki if wydatki is not None else []
            return wydatki if wydatki is not None else []
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"Błąd wczytywania wydatków: {e}")
        return []

def save_wydatki(wydatki):
    """Zapisz wydatki do pliku JSON"""
    if PERSISTENT_OK:
        # Wyczyść cache aby uniknąć konfliktu ze starymi danymi
        st.session_state.pop('wydatki_data', None)
        return save_persistent_data('wydatki.json', {'wydatki': wydatki})
    
    # Fallback - stary system
    try:
        with open('wydatki.json', 'w', encoding='utf-8') as f:
            json.dump({'wydatki': wydatki}, f, indent=2, ensure_ascii=False)
        st.session_state['wydatki_data'] = wydatki
        return True
    except Exception as e:
        # Streamlit Cloud - tylko session
        st.session_state['wydatki_data'] = wydatki
        st.warning(f"⚠️ Dane zapisane tymczasowo w sesji. Filesystem read-only.")
        return True

def load_krypto():
    """Wczytaj kryptowaluty z pliku JSON"""
    if PERSISTENT_OK:
        data = load_persistent_data('krypto.json')
        if data is not None:
            krypto = data.get('krypto', [])
            return krypto if krypto is not None else []
    
    # Fallback
    try:
        with open('krypto.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            krypto = data.get('krypto', [])
            return krypto if krypto is not None else []
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"Błąd wczytywania krypto: {e}")
        return []

def save_krypto(krypto):
    """Zapisz kryptowaluty do pliku JSON"""
    if PERSISTENT_OK:
        return save_persistent_data('krypto.json', {'krypto': krypto})
    
    # Fallback
    try:
        with open('krypto.json', 'w', encoding='utf-8') as f:
            json.dump({'krypto': krypto}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Błąd zapisu krypto: {e}")
        return False

def calculate_financial_overview(stan_spolki, cele):
    """
    Oblicza kluczowe metryki finansowe dla Overview Dashboard
    Returns: dict with assets, debts, net_worth, monthly_cash_flow, deltas
    """
    try:
        # Assets (Aktywa)
        akcje_value = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
        krypto_value = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
        rezerwa = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
        total_assets = akcje_value + krypto_value + rezerwa
        
        # Debts (Zobowiązania)
        kredyty = load_kredyty()
        total_debt = 0
        monthly_payments = 0
        for k in kredyty:
            pozostalo = k['kwota_poczatkowa'] - k['splacono']
            total_debt += pozostalo
            monthly_payments += k.get('rata_miesieczna', 0)
        
        # Net Worth (Wartość Netto)
        net_worth = total_assets - total_debt
        
        # Monthly Cash Flow
        wyplaty = load_wyplaty()
        wydatki = load_wydatki()
        
        last_income = wyplaty[0]['kwota'] if wyplaty else 0
        stale_wydatki = get_suma_wydatkow_stalych(wydatki)
        monthly_cash_flow = last_income - stale_wydatki - monthly_payments
        
        # Calculate deltas from portfolio history (if available)
        deltas = {
            'assets': None,
            'debt': None,
            'net_worth': None,
            'cash_flow': None
        }
        
        # Try to get 30-day changes
        try:
            with open('portfolio_history.json', 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if history and len(history) > 1:
                # Sort by timestamp
                history_sorted = sorted(history, key=lambda x: x['timestamp'], reverse=True)
                
                # Find snapshot from ~30 days ago
                from datetime import datetime, timedelta
                target_date = datetime.now() - timedelta(days=30)
                
                old_snapshot = None
                for snap in reversed(history_sorted):
                    snap_date = datetime.fromisoformat(snap['timestamp'])
                    if snap_date <= target_date:
                        old_snapshot = snap
                        break
                
                if not old_snapshot and len(history_sorted) > 1:
                    old_snapshot = history_sorted[-1]
                
                if old_snapshot:
                    old_value = old_snapshot.get('value', 0)
                    if old_value > 0:
                        net_worth_change = ((net_worth - old_value) / old_value) * 100
                        deltas['net_worth'] = f"{net_worth_change:+.1f}%"
        except:
            pass
        
        return {
            'total_assets': total_assets,
            'total_debt': total_debt,
            'net_worth': net_worth,
            'monthly_cash_flow': monthly_cash_flow,
            'monthly_payments': monthly_payments,
            'last_income': last_income,
            'kredyty_count': len(kredyty),
            'deltas': deltas
        }
    except Exception as e:
        # Return safe defaults
        return {
            'total_assets': 0,
            'total_debt': 0,
            'net_worth': 0,
            'monthly_cash_flow': 0,
            'monthly_payments': 0,
            'last_income': 0,
            'kredyty_count': 0,
            'deltas': {'assets': None, 'debt': None, 'net_worth': None, 'cash_flow': None}
        }

def show_kredyty_page(stan_spolki, cele):
    """Strona zarządzania kredytami i celami finansowymi"""
    st.title("💳 Centrum Finansowe")
    st.caption("Kompleksowe zarządzanie: Cele • Kredyty • Spłaty • Wypłaty • Wydatki • Krypto • Track Record AI")
    
    # === FINANCIAL OVERVIEW DASHBOARD ===
    st.markdown("---")
    
    overview = calculate_financial_overview(stan_spolki, cele)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💼 Total Assets",
            format_currency(overview['total_assets']),
            delta=overview['deltas']['assets'],
            help="Akcje + Krypto + Rezerwa Gotówkowa"
        )
        st.caption(f"Akcje: {format_currency(stan_spolki.get('akcje', {}).get('wartosc_pln', 0))}")
        st.caption(f"Krypto: {format_currency(stan_spolki.get('krypto', {}).get('wartosc_pln', 0))}")
    
    with col2:
        st.metric(
            "💳 Total Debts",
            format_currency(overview['total_debt']),
            delta=overview['deltas']['debt'],
            delta_color="inverse",
            help=f"Suma pozostałych zobowiązań ({overview['kredyty_count']} kredytów)"
        )
        st.caption(f"Rata miesięczna: {overview['monthly_payments']:.0f} PLN")
        st.caption(f"Liczba kredytów: {overview['kredyty_count']}")
    
    with col3:
        st.metric(
            "💎 Net Worth",
            format_currency(overview['net_worth']),
            delta=overview['deltas']['net_worth'],
            help="Assets - Debts"
        )
        
        # Leverage ratio
        if overview['total_assets'] > 0:
            leverage = (overview['total_debt'] / overview['total_assets']) * 100
            leverage_color = "🟢" if leverage < 15 else "🟡" if leverage < 25 else "🔴"
            st.caption(f"{leverage_color} Leverage: {leverage:.1f}%")
        else:
            st.caption("Leverage: N/A")
    
    with col4:
        cash_flow_positive = overview['monthly_cash_flow'] > 0
        st.metric(
            "💰 Monthly Cash Flow",
            f"{overview['monthly_cash_flow']:.0f} PLN",
            delta=overview['deltas']['cash_flow'],
            delta_color="normal" if cash_flow_positive else "inverse",
            help="Ostatnia wypłata - Wydatki stałe - Raty kredytów"
        )
        
        if cash_flow_positive:
            savings_rate = (overview['monthly_cash_flow'] / overview['last_income'] * 100) if overview['last_income'] > 0 else 0
            st.caption(f"✅ Savings rate: {savings_rate:.1f}%")
        else:
            st.caption(f"⚠️ Deficyt: {abs(overview['monthly_cash_flow']):.0f} PLN")
    
    st.markdown("---")
    
    # === SMART ALERTS - NADCHODZĄCE PŁATNOŚCI ===
    kredyty = load_kredyty()
    
    if kredyty:
        from datetime import datetime
        dzis = datetime.now().day
        najblizsze_splaty = []
        suma_platnosci_ten_miesiac = 0
        
        for k in kredyty:
            dzien_splaty = k['dzien_splaty']
            kwota = k.get('rata_miesieczna', 0)
            
            # Oblicz dni do spłaty
            if dzien_splaty >= dzis:
                dni_do_splaty = dzien_splaty - dzis
            else:
                # Następny miesiąc
                import calendar
                dni_w_miesiacu = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
                dni_do_splaty = (dni_w_miesiacu - dzis) + dzien_splaty
            
            najblizsze_splaty.append({
                'nazwa': k['nazwa'],
                'dzien': dzien_splaty,
                'dni_do': dni_do_splaty,
                'kwota': kwota
            })
            
            # Suma płatności w tym miesiącu
            if dzien_splaty >= dzis:
                suma_platnosci_ten_miesiac += kwota
        
        if najblizsze_splaty:
            # Sortuj po liczbie dni
            najblizsze_splaty.sort(key=lambda x: x['dni_do'])
            
            # Znajdź najbliższą płatność
            najblizsza = najblizsze_splaty[0]
            
            # Określ kolor i ikonę
            if najblizsza['dni_do'] == 0:
                alert_type = "error"
                alert_icon = "🚨"
                alert_message = f"**DZIŚ PŁATNOŚĆ!** {najblizsza['nazwa']} - {najblizsza['kwota']:.0f} PLN"
            elif najblizsza['dni_do'] <= 3:
                alert_type = "warning"
                alert_icon = "⚠️"
                alert_message = f"**Za {najblizsza['dni_do']} dni:** {najblizsza['nazwa']} - {najblizsza['kwota']:.0f} PLN"
            elif najblizsza['dni_do'] <= 7:
                alert_type = "info"
                alert_icon = "📅"
                alert_message = f"**Za {najblizsza['dni_do']} dni:** {najblizsza['nazwa']} - {najblizsza['kwota']:.0f} PLN"
            else:
                alert_type = None
                alert_icon = "💳"
                alert_message = None
            
            # Pokaż alert tylko dla płatności < 7 dni
            if alert_type:
                if alert_type == "error":
                    st.error(f"{alert_icon} {alert_message}")
                elif alert_type == "warning":
                    st.warning(f"{alert_icon} {alert_message}")
                else:
                    st.info(f"{alert_icon} {alert_message}")
            
            # Pokaż szczegóły w expander
            with st.expander(f"💳 Nadchodzące płatności ({len(najblizsze_splaty)}) - Suma w tym miesiącu: {suma_platnosci_ten_miesiac:.0f} PLN"):
                for splata in najblizsze_splaty:
                    col_nazwa, col_data, col_kwota = st.columns([3, 2, 2])
                    
                    with col_nazwa:
                        st.write(f"**{splata['nazwa']}**")
                    
                    with col_data:
                        if splata['dni_do'] == 0:
                            st.write("🔴 **DZIŚ!**")
                        elif splata['dni_do'] <= 3:
                            st.write(f"🟡 Za {splata['dni_do']} dni (dzień {splata['dzien']})")
                        else:
                            st.write(f"🟢 Za {splata['dni_do']} dni (dzień {splata['dzien']})")
                    
                    with col_kwota:
                        st.write(f"**{splata['kwota']:.0f} PLN**")
            
            st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💰 Cele Finansowe", 
        "💳 Kredyty", 
        "📊 Analiza Spłat", 
        "💸 Wypłaty", 
        "📋 Stałe Wydatki", 
        "₿ Krypto",
        "🏆 Track Record AI"
    ])
    
    # ===== TAB 1: CELE FINANSOWE =====
    with tab1:
        st.header("💰 Edycja Celów Finansowych")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💵 Rezerwa Gotówkowa")
            
            # Pobierz aktualne wartości
            rezerwa_obecna = cele.get('Rezerwa_gotowkowa_obecna_PLN', 39904) if cele else 39904
            rezerwa_cel = cele.get('Rezerwa_gotowkowa_PLN', 70000) if cele else 70000
            
            # Edycja
            new_rezerwa_obecna = st.number_input(
                "Zgromadzona kwota (PLN)",
                min_value=0,
                value=int(rezerwa_obecna),
                step=1000,
                help="Aktualna kwota rezerwy gotówkowej",
                key="input_rezerwa_obecna"
            )
            
            new_rezerwa_cel = st.number_input(
                "Docelowa kwota (PLN)",
                min_value=0,
                value=int(rezerwa_cel),
                step=5000,
                help="Kwota do osiągnięcia",
                key="input_rezerwa_cel"
            )
            
            # LIVE PREVIEW - Progress z nowymi wartościami
            progress = new_rezerwa_obecna / new_rezerwa_cel if new_rezerwa_cel > 0 else 0
            st.progress(min(progress, 1.0))
            st.caption(f"**Preview:** {progress*100:.1f}% ({format_currency(new_rezerwa_obecna)} / {format_currency(new_rezerwa_cel)})")
            
            # Sprawdź czy są zmiany
            has_changes = (new_rezerwa_obecna != rezerwa_obecna) or (new_rezerwa_cel != rezerwa_cel)
            
            # Pokaż przycisk tylko gdy są zmiany
            if has_changes:
                st.warning("⚠️ Masz niezapisane zmiany!")
                
                col_save, col_cancel = st.columns(2)
                
                with col_save:
                    if st.button("💾 Zapisz Zmiany", key="save_rezerwa", type="primary", use_container_width=True):
                        if cele is None:
                            cele = {}
                        cele['Rezerwa_gotowkowa_obecna_PLN'] = new_rezerwa_obecna
                        cele['Rezerwa_gotowkowa_PLN'] = new_rezerwa_cel
                        if save_cele(cele):
                            # Synchronizuj cel w kodeksie spółki
                            try:
                                with open('kodeks_spolki.txt', 'r', encoding='utf-8') as f:
                                    kodeks_content = f.read()
                                
                                # Zamień linię z celem rezerwy gotówkowej
                                import re
                                pattern = r'Cel #2: Budowa rezerwy gotówkowej do docelowego poziomu \d+[\s,]*\d* PLN\.'
                                replacement = f'Cel #2: Budowa rezerwy gotówkowej do docelowego poziomu {new_rezerwa_cel:,} PLN.'.replace(',', ' ')
                                
                                new_kodeks = re.sub(pattern, replacement, kodeks_content)
                                
                                if new_kodeks != kodeks_content:
                                    with open('kodeks_spolki.txt', 'w', encoding='utf-8') as f:
                                        f.write(new_kodeks)
                                    st.success("✅ Rezerwa gotówkowa zaktualizowana w cele.json i kodeksie spółki!")
                                else:
                                    st.success("✅ Rezerwa gotówkowa zaktualizowana!")
                            except Exception as e:
                                st.success("✅ Rezerwa gotówkowa zaktualizowana w cele.json!")
                                st.warning(f"⚠️ Nie udało się zaktualizować kodeksu: {str(e)}")
                            
                            # WYCZYŚĆ CACHE aby odświeżyć dane
                            load_portfolio_data.clear()
                            st.rerun()
                
                with col_cancel:
                    if st.button("🔄 Anuluj", key="cancel_rezerwa", use_container_width=True):
                        st.rerun()
            else:
                st.success("✅ Wszystkie dane zapisane")
            
            # === PROGRESS TRACKING & TIMELINE ===
            st.markdown("---")
            st.markdown("#### 📈 Progress Tracking")
            
            # Oblicz miesięczny wzrost na podstawie cash flow
            overview_tab1 = calculate_financial_overview(stan_spolki, cele)
            miesieczny_wzrost = overview_tab1['monthly_cash_flow']
            
            if new_rezerwa_cel > new_rezerwa_obecna and miesieczny_wzrost > 0:
                brakujaca_kwota = new_rezerwa_cel - new_rezerwa_obecna
                miesiace_do_celu = brakujaca_kwota / miesieczny_wzrost
                
                from datetime import datetime, timedelta
                data_osiagniecia = datetime.now() + timedelta(days=miesiace_do_celu * 30)
                
                st.info(f"🎯 **Przewidywana data osiągnięcia:** {data_osiagniecia.strftime('%Y-%m-%d')}")
                st.caption(f"⏰ Czas do celu: {int(miesiace_do_celu)} miesięcy (przy obecnym cash flow: {miesieczny_wzrost:.0f} PLN/mies)")
                
                # Milestones
                st.markdown("**🎖️ Milestones:**")
                milestones = [
                    (0.25, "25%", "🥉"),
                    (0.50, "50%", "🥈"),
                    (0.75, "75%", "🥇"),
                    (1.00, "100%", "🏆")
                ]
                
                progress_actual = new_rezerwa_obecna / new_rezerwa_cel if new_rezerwa_cel > 0 else 0
                
                for milestone_pct, label, emoji in milestones:
                    milestone_kwota = new_rezerwa_cel * milestone_pct
                    
                    if progress_actual >= milestone_pct:
                        st.success(f"{emoji} {label} - {format_currency(milestone_kwota)} ✅ OSIĄGNIĘTE!")
                    else:
                        brakuje = milestone_kwota - new_rezerwa_obecna
                        miesiace = brakuje / miesieczny_wzrost if miesieczny_wzrost > 0 else 0
                        data_milestone = datetime.now() + timedelta(days=miesiace * 30)
                        st.info(f"⏳ {label} - {format_currency(milestone_kwota)} (do osiągnięcia: {brakuje:.0f} PLN, ~{data_milestone.strftime('%Y-%m-%d')})")
            elif new_rezerwa_obecna >= new_rezerwa_cel:
                st.success("🎊 **CEL OSIĄGNIĘTY!** Gratulacje!")
            else:
                st.warning("⚠️ Brak dodatniego cash flow - nie można obliczyć przewidywanej daty osiągnięcia celu.")
        
        with col2:
            st.subheader("💳 Zarządzanie Kredytami")
            st.info("📋 Przejdź do zakładki **💳 Kredyty** aby zarządzać swoimi kredytami")
            st.markdown("""
            W zakładce Kredyty możesz:
                - ➕ Dodawać nowe kredyty z pełnymi szczegółami
            - 📅 Śledzić daty spłat
            - � Aktualizować spłacone kwoty
            - 📊 Analizować postęp spłat
            - ⏰ Otrzymywać przypomnienia o płatnościach
            """)
            
            if st.button("� Przejdź do Kredytów", key="goto_kredyty_from_cele"):
                st.session_state['goto_page'] = "💳 Kredyty"
                st.rerun()
    
    # ===== TAB 2: KREDYTY =====
    with tab2:
        st.header("💳 Szczegółowe Zarządzanie Kredytami")
        
        kredyty = load_kredyty()
        
        # Formularz dodawania nowego kredytu
        with st.expander("➕ Dodaj Nowy Kredyt", expanded=len(kredyty)==0):
            with st.form("add_kredyt"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nazwa = st.text_input("Nazwa kredytu *", placeholder="np. Kredyt mieszkaniowy")
                    kwota_poczatkowa = st.number_input("Kwota początkowa (PLN) *", min_value=0, step=1000, value=0)
                    data_zaciagniecia = st.date_input("Data zaciągnięcia *", value=datetime.now())
                    dzien_splaty = st.number_input("Dzień spłaty w miesiącu *", min_value=1, max_value=31, value=10, help="Który dzień miesiąca przypada spłata?")
                
                with col2:
                    oprocentowanie = st.number_input("Oprocentowanie roczne (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f", value=0.0)
                    rata_miesieczna = st.number_input("Rata miesięczna (PLN)", min_value=0, step=100, value=0)
                    splacono = st.number_input("Już spłacono (PLN)", min_value=0, step=1000, value=0)
                
                notatki = st.text_area("Notatki", placeholder="Dodatkowe informacje, np. bank, numer umowy...")
                
                submitted = st.form_submit_button("💾 Dodaj Kredyt")
                if submitted:
                    if not nazwa:
                        st.error("❌ Podaj nazwę kredytu")
                    elif kwota_poczatkowa <= 0:
                        st.error("❌ Kwota musi być większa od 0")
                    else:
                        nowy_kredyt = {
                            'id': str(datetime.now().timestamp()),
                            'nazwa': nazwa,
                            'kwota_poczatkowa': kwota_poczatkowa,
                            'data_zaciagniecia': data_zaciagniecia.isoformat(),
                            'dzien_splaty': dzien_splaty,
                            'oprocentowanie': oprocentowanie,
                            'rata_miesieczna': rata_miesieczna,
                            'splacono': splacono,
                            'notatki': notatki
                        }
                        kredyty.append(nowy_kredyt)
                        if save_kredyty(kredyty):
                            st.success("✅ Kredyt dodany!")
                            st.rerun()
        
        # Lista kredytów
        if kredyty:
            st.markdown("### 📋 Twoje Kredyty")
            
            # Przygotuj dane do tabeli
            import pandas as pd
            df_kredyty_list = []
            
            for i, kredyt in enumerate(kredyty):
                pozostalo = kredyt['kwota_poczatkowa'] - kredyt['splacono']
                postep = (kredyt['splacono'] / kredyt['kwota_poczatkowa'] * 100) if kredyt['kwota_poczatkowa'] > 0 else 0
                miesiace_do_splaty = (pozostalo / kredyt['rata_miesieczna']) if kredyt['rata_miesieczna'] > 0 else 0
                
                df_kredyty_list.append({
                    'ID': i,
                    'Nazwa': kredyt['nazwa'],
                    'Początek': kredyt['kwota_poczatkowa'],
                    'Spłacono': kredyt['splacono'],
                    'Pozostało': pozostalo,
                    'Postęp %': postep,
                    'Rata/mies': kredyt['rata_miesieczna'],
                    'Oprocent. %': kredyt['oprocentowanie'],
                    'Dzień spłaty': kredyt['dzien_splaty'],
                    'Miesiące do końca': int(miesiace_do_splaty)
                })
            
            df_kredyty = pd.DataFrame(df_kredyty_list)
            
            # Wyświetl tabelę
            st.dataframe(
                df_kredyty[['Nazwa', 'Początek', 'Spłacono', 'Pozostało', 'Postęp %', 'Rata/mies', 'Dzień spłaty', 'Miesiące do końca']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Początek': st.column_config.NumberColumn(format="%.0f PLN"),
                    'Spłacono': st.column_config.NumberColumn(format="%.0f PLN"),
                    'Pozostało': st.column_config.NumberColumn(format="%.0f PLN"),
                    'Postęp %': st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
                    'Rata/mies': st.column_config.NumberColumn(format="%.0f PLN"),
                }
            )
            
            st.markdown("---")
            st.markdown("### ✏️ Edycja Kredytu")
            
            # Wybór kredytu do edycji
            kredyt_names = [f"{k['nazwa']} (pozostało: {format_currency(k['kwota_poczatkowa'] - k['splacono'])})" for k in kredyty]
            selected_idx = st.selectbox(
                "Wybierz kredyt do edycji:",
                range(len(kredyty)),
                format_func=lambda i: kredyt_names[i],
                key="select_kredyt_edit"
            )
            
            if selected_idx is not None:
                kredyt = kredyty[selected_idx]
                pozostalo = kredyt['kwota_poczatkowa'] - kredyt['splacono']
                
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.metric("Kwota początkowa", format_currency(kredyt['kwota_poczatkowa']))
                    st.caption(f"📅 Data: {kredyt['data_zaciagniecia']}")
                
                with col_info2:
                    postep = kredyt['splacono'] / kredyt['kwota_poczatkowa'] * 100 if kredyt['kwota_poczatkowa'] > 0 else 0
                    st.metric("Pozostało", format_currency(pozostalo))
                    st.progress(min(postep / 100, 1.0))
                    st.caption(f"Postęp: {postep:.1f}%")
                
                with col_info3:
                    if kredyt['rata_miesieczna'] > 0:
                        miesiace = pozostalo / kredyt['rata_miesieczna']
                        st.metric("Miesiące do spłaty", f"{int(miesiace)}")
                        st.caption(f"({int(miesiace/12)} lat {int(miesiace%12)} mies.)")
                    else:
                        st.metric("Miesiące do spłaty", "N/A")
                
                if kredyt.get('notatki'):
                    st.info(f"📝 Notatki: {kredyt['notatki']}")
                
                st.markdown("---")
                
                col_edit1, col_edit2, col_edit3 = st.columns([2, 1, 1])
                
                with col_edit1:
                    nowa_splacona_kwota = st.number_input(
                        "Aktualizuj spłaconą kwotę (PLN)",
                        min_value=0,
                        max_value=int(kredyt['kwota_poczatkowa']),
                        value=int(kredyt['splacono']),
                        step=100,
                        key=f"edit_splacono_table_{selected_idx}",
                        help="Zmień kwotę która została już spłacona"
                    )
                
                with col_edit2:
                    if st.button("💾 Zapisz", key=f"save_table_{selected_idx}", type="primary", use_container_width=True):
                        kredyty[selected_idx]['splacono'] = nowa_splacona_kwota
                        if save_kredyty(kredyty):
                            st.success("✅ Zaktualizowano!")
                            st.rerun()
                
                with col_edit3:
                    if st.button("🗑️ Usuń", key=f"delete_table_{selected_idx}", use_container_width=True):
                        if st.session_state.get(f'confirm_delete_table_{selected_idx}', False):
                            kredyty.pop(selected_idx)
                            if save_kredyty(kredyty):
                                st.success("✅ Usunięto!")
                                st.rerun()
                        else:
                            st.session_state[f'confirm_delete_table_{selected_idx}'] = True
                            st.warning("⚠️ Kliknij ponownie!")
        else:
            st.info("ℹ️ Nie masz jeszcze żadnych kredytów. Dodaj pierwszy powyżej!")
    
    # ===== TAB 3: ANALIZA =====
    with tab3:
        st.header("📊 Analiza Spłat i Prognoza")
        
        kredyty = load_kredyty()
        
        if not kredyty:
            st.info("ℹ️ Dodaj kredyty w zakładce 'Kredyty', aby zobaczyć analizę.")
        else:
            # Suma wszystkich kredytów
            suma_poczatkowa = sum(k['kwota_poczatkowa'] for k in kredyty)
            suma_splacona = sum(k['splacono'] for k in kredyty)
            suma_pozostala = suma_poczatkowa - suma_splacona
            suma_rat = sum(k['rata_miesieczna'] for k in kredyty)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Suma początkowa", format_currency(suma_poczatkowa))
            with col2:
                st.metric("Suma spłacona", format_currency(suma_splacona))
            with col3:
                st.metric("Suma pozostała", format_currency(suma_pozostala))
            with col4:
                st.metric("Miesięczne raty", f"{suma_rat:.0f} PLN")
            
            # Prognoza spłaty
            st.markdown("### 📈 Prognoza Spłaty")
            
            if suma_rat > 0 and suma_pozostala > 0:
                miesiace_do_splaty = suma_pozostala / suma_rat
                lata = int(miesiace_do_splaty / 12)
                miesiace = int(miesiace_do_splaty % 12)
                
                data_splaty = datetime.now() + timedelta(days=miesiace_do_splaty * 30)
                
                st.success(f"🎯 **Przewidywana data spłaty:** {data_splaty.strftime('%Y-%m-%d')}")
                st.caption(f"⏰ Czas do pełnej spłaty: {lata} lat i {miesiace} miesięcy")
            
            # Tabela kredytów
            st.markdown("### 📋 Szczegóły Kredytów")
            
            df_kredyty = []
            for k in kredyty:
                pozostalo = k['kwota_poczatkowa'] - k['splacono']
                postep = k['splacono'] / k['kwota_poczatkowa'] * 100 if k['kwota_poczatkowa'] > 0 else 0
                df_kredyty.append({
                    'Nazwa': k['nazwa'],
                    'Początek': f"{k['kwota_poczatkowa']:.0f} PLN",
                    'Spłacono': f"{k['splacono']:.0f} PLN",
                    'Pozostało': f"{pozostalo:.0f} PLN",
                    'Postęp': f"{postep:.1f}%",
                    'Oprocentowanie': f"{k['oprocentowanie']:.2f}%",
                    'Rata': f"{k['rata_miesieczna']:.0f} PLN",
                    'Dzień spłaty': str(k['dzien_splaty']),
                    'Data zaciągnięcia': k['data_zaciagniecia']
                })
            
            if df_kredyty:
                import pandas as pd
                st.dataframe(pd.DataFrame(df_kredyty), width="stretch", hide_index=True)
                
                # Wykres postępu spłat
                st.markdown("### 📊 Postęp Spłat (wizualizacja)")
                
                fig = go.Figure()
                
                for k in kredyty:
                    pozostalo = k['kwota_poczatkowa'] - k['splacono']
                    fig.add_trace(go.Bar(
                        name=k['nazwa'],
                        x=['Spłacono', 'Pozostało'],
                        y=[k['splacono'], pozostalo],
                        text=[f"{k['splacono']:.0f}", f"{pozostalo:.0f}"],
                        textposition='auto',
                    ))
                
                fig.update_layout(
                    barmode='stack',
                    title="Postęp spłaty kredytów",
                    xaxis_title="",
                    yaxis_title="Kwota (PLN)",
                    showlegend=True,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # === PIE CHART - BREAKDOWN DŁUGÓW ===
                st.markdown("### 🥧 Breakdown Długów")
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=[k['nazwa'] for k in kredyty],
                    values=[k['kwota_poczatkowa'] - k['splacono'] for k in kredyty],
                    hole=0.4,
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Pozostało: %{value:,.0f} PLN<br>%{percent}<extra></extra>'
                )])
                
                fig_pie.update_layout(
                    title="Rozkład pozostałych zobowiązań",
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
                
                st.markdown("---")
                
                # === INTEREST PAID CALCULATOR ===
                st.markdown("### 💸 Kalkulator Odsetek")
                
                total_interest = 0
                interest_breakdown = []
                
                for k in kredyty:
                    if k['oprocentowanie'] > 0 and k['rata_miesieczna'] > 0:
                        pozostalo = k['kwota_poczatkowa'] - k['splacono']
                        miesiace = pozostalo / k['rata_miesieczna'] if k['rata_miesieczna'] > 0 else 0
                        
                        # Uproszczone obliczenie (annuity formula aproximation)
                        total_to_pay = k['rata_miesieczna'] * miesiace
                        interest = total_to_pay - pozostalo
                        
                        interest_breakdown.append({
                            'Kredyt': k['nazwa'],
                            'Odsetki (przewidywane)': interest
                        })
                        total_interest += interest
                
                if interest_breakdown:
                    col_int1, col_int2 = st.columns(2)
                    
                    with col_int1:
                        st.metric("💰 Łączne odsetki do zapłaty", f"{total_interest:.0f} PLN")
                        st.caption("Przewidywana kwota odsetek przy obecnym harmonogramie spłat")
                    
                    with col_int2:
                        effective_rate = (total_interest / suma_pozostala * 100) if suma_pozostala > 0 else 0
                        st.metric("📊 Efektywna stopa kosztów", f"{effective_rate:.2f}%")
                        st.caption("Stosunek odsetek do pozostałego kapitału")
                    
                    # Tabela breakdown
                    with st.expander("📋 Szczegóły odsetek"):
                        import pandas as pd
                        df_int = pd.DataFrame(interest_breakdown)
                        st.dataframe(df_int, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ Brak kredytów z oprocentowaniem")
                
                st.markdown("---")
                
                # === EARLY PAYOFF SIMULATOR ===
                st.markdown("### 🚀 Symulator Wcześniejszej Spłaty")
                
                dodatkowa_kwota = st.slider(
                    "Dodatkowa miesięczna wpłata (PLN)",
                    min_value=0,
                    max_value=5000,
                    value=500,
                    step=100,
                    help="Ile dodatkowych pieniędzy możesz przeznaczyć miesięcznie na spłatę?"
                )
                
                if dodatkowa_kwota > 0:
                    col_sim1, col_sim2, col_sim3 = st.columns(3)
                    
                    # Scenariusz bez dodatkowych wpłat
                    miesiace_bazowe = suma_pozostala / suma_rat if suma_rat > 0 else 0
                    
                    # Scenariusz z dodatkowymi wpłatami
                    miesiace_z_dodatkiem = suma_pozostala / (suma_rat + dodatkowa_kwota) if (suma_rat + dodatkowa_kwota) > 0 else 0
                    
                    # Oszczędność czasu
                    oszczednosc_miesiecy = miesiace_bazowe - miesiace_z_dodatkiem
                    oszczednosc_lat = oszczednosc_miesiecy / 12
                    
                    with col_sim1:
                        st.metric("⏰ Obecny czas spłaty", f"{int(miesiace_bazowe)} mies.")
                        st.caption(f"({int(miesiace_bazowe/12)} lat {int(miesiace_bazowe%12)} mies.)")
                    
                    with col_sim2:
                        st.metric("🚀 Z dodatkowymi wpłatami", f"{int(miesiace_z_dodatkiem)} mies.")
                        st.caption(f"({int(miesiace_z_dodatkiem/12)} lat {int(miesiace_z_dodatkiem%12)} mies.)")
                    
                    with col_sim3:
                        st.metric("💎 Oszczędność czasu", f"{int(oszczednosc_miesiecy)} mies.", delta=f"-{oszczednosc_lat:.1f} lat")
                        st.caption("Szybsza spłata = mniej odsetek!")
                    
                    # Oszczędność na odsetkach (uproszczone)
                    if total_interest > 0:
                        oszczednosc_odsetek = total_interest * (oszczednosc_miesiecy / miesiace_bazowe) if miesiace_bazowe > 0 else 0
                        st.success(f"💰 **Przewidywana oszczędność na odsetkach:** {oszczednosc_odsetek:.0f} PLN")
                
                st.markdown("---")
                
                # === DEBT SNOWBALL VS AVALANCHE ===
                st.markdown("### ❄️ Strategie Spłaty: Snowball vs Avalanche")
                
                st.info("""
                **Dwie popularne strategie spłaty długów:**
                
                🌨️ **Debt Snowball** - Spłacaj od najmniejszego długu  
                ✅ Motywujące (szybkie wygrane)  
                ❌ Potencjalnie więcej odsetek  
                
                🏔️ **Debt Avalanche** - Spłacaj od najwyższego oprocentowania  
                ✅ Minimalizuje odsetki  
                ❌ Mniej motywujące początkowo  
                """)
                
                col_strat1, col_strat2 = st.columns(2)
                
                with col_strat1:
                    st.markdown("#### 🌨️ Snowball (od najmniejszego)")
                    sorted_by_size = sorted(kredyty, key=lambda k: k['kwota_poczatkowa'] - k['splacono'])
                    for i, k in enumerate(sorted_by_size[:5], 1):
                        pozostalo = k['kwota_poczatkowa'] - k['splacono']
                        st.write(f"{i}. **{k['nazwa']}** - {format_currency(pozostalo)}")
                
                with col_strat2:
                    st.markdown("#### 🏔️ Avalanche (od najdroższego)")
                    sorted_by_interest = sorted(kredyty, key=lambda k: k['oprocentowanie'], reverse=True)
                    for i, k in enumerate(sorted_by_interest[:5], 1):
                        pozostalo = k['kwota_poczatkowa'] - k['splacono']
                        st.write(f"{i}. **{k['nazwa']}** ({k['oprocentowanie']:.2f}%) - {format_currency(pozostalo)}")
    
    # ===== TAB 4: WYPŁATY =====
    with tab4:
        st.header("💸 Historia Wypłat")
        
        # Ustawienie minimalnej krajowej
        col_info1, col_info2 = st.columns([2, 1])
        
        with col_info1:
            st.info("""
            💾 **System persystencji danych:**
            - Dane zapisują się automatycznie do pamięci sesji
            - **Synchronizacja z GitHub co godzinę** (GitHub Actions)
            
            📋 **System wpływów:**
            - 💰 **Wypłata** - minimalna krajowa (automatycznie)
            - 🎁 **Premia** - kwota powyżej minimalnej (automatycznie)
            - 🎉 **Bonus** - jednorazowe bonusy (ręcznie zaznacz)
            """)
        
        with col_info2:
            st.markdown("### ⚙️ Ustawienia")
            minimalna_krajowa = st.number_input(
                "Minimalna krajowa (PLN)",
                min_value=0.0,
                value=st.session_state.get('minimalna_krajowa', 4300.0),
                step=100.0,
                help="Aktualna minimalna płaca krajowa - do automatycznego podziału na Wypłatę + Premia"
            )
            st.session_state['minimalna_krajowa'] = minimalna_krajowa
            st.caption(f"✅ Minimalna: **{minimalna_krajowa:,.0f} PLN**")
        
        wyplaty = load_wyplaty()
        
        # === PODSUMOWANIE ===
        if wyplaty:
            # Sortuj wypłaty po dacie
            wyplaty_sorted = sorted(wyplaty, key=lambda x: x['data'], reverse=True)
            
            # Rozdziel wypłaty regularne (Wypłata + Premia) od Bonusów
            wyplaty_regularne = [w for w in wyplaty_sorted if w.get('typ', 'Wypłata') in ['Wypłata', 'Premia']]
            bonusy = [w for w in wyplaty_sorted if w.get('typ', 'Wypłata') == 'Bonus']
            
            # Różne okresy (tylko regularne wypłaty do statystyk)
            rok_temu = datetime.now() - timedelta(days=365)
            pol_roku_temu = datetime.now() - timedelta(days=180)
            kwartal_temu = datetime.now() - timedelta(days=90)
            
            wyplaty_12m = [w for w in wyplaty_regularne if datetime.fromisoformat(w['data']) >= rok_temu]
            wyplaty_6m = [w for w in wyplaty_regularne if datetime.fromisoformat(w['data']) >= pol_roku_temu]
            wyplaty_3m = [w for w in wyplaty_regularne if datetime.fromisoformat(w['data']) >= kwartal_temu]
            
            # Bonusy w okresach
            bonusy_12m = [b for b in bonusy if datetime.fromisoformat(b['data']) >= rok_temu]
            bonusy_suma_12m = sum(b['kwota'] for b in bonusy_12m)
            
            # Średnie (tylko wypłaty regularne)
            srednia_12m = sum(w['kwota'] for w in wyplaty_12m) / len(wyplaty_12m) if wyplaty_12m else 0
            srednia_6m = sum(w['kwota'] for w in wyplaty_6m) / len(wyplaty_6m) if wyplaty_6m else 0
            srednia_3m = sum(w['kwota'] for w in wyplaty_3m) / len(wyplaty_3m) if wyplaty_3m else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if wyplaty_sorted:
                    ostatnia = wyplaty_sorted[0]
                    typ_emoji = "💰" if ostatnia.get('typ', 'Wypłata') == "Wypłata" else "🎁" if ostatnia.get('typ') == "Premia" else "🎉"
                    st.metric(f"{typ_emoji} Ostatni wpływ", format_currency(ostatnia['kwota']))
                    st.caption(f"{ostatnia.get('typ', 'Wypłata')} • {ostatnia['data']}")
            
            with col2:
                st.metric("📊 Średnia (3 mies.)", format_currency(srednia_3m))
                trend_3_6 = ((srednia_3m - srednia_6m) / srednia_6m * 100) if srednia_6m > 0 else 0
                st.caption(f"Wypłaty regularne • {trend_3_6:+.1f}% vs 6m")
            
            with col3:
                st.metric("📊 Średnia (6 mies.)", format_currency(srednia_6m))
                trend_6_12 = ((srednia_6m - srednia_12m) / srednia_12m * 100) if srednia_12m > 0 else 0
                st.caption(f"Wypłaty regularne • {trend_6_12:+.1f}% vs 12m")
            
            with col4:
                st.metric("🎉 Bonusy (12 mies.)", format_currency(bonusy_suma_12m))
                st.caption(f"Liczba bonusów: {len(bonusy_12m)}")
            
            st.markdown("---")
            
            # === WYKRES HISTORII WYPŁAT ===
            st.markdown("### 📈 Historia Wpływów")
            
            # Przygotuj dane do wykresu
            wyplaty_chart = sorted(wyplaty, key=lambda x: x['data'])
            
            # Rozdziel po typach
            wyplaty_reg = [w for w in wyplaty_chart if w.get('typ', 'Wypłata') in ['Wypłata', 'Premia']]
            bonusy_chart = [w for w in wyplaty_chart if w.get('typ', 'Wypłata') == 'Bonus']
            
            fig_income = go.Figure()
            
            # Wypłaty regularne (linia) - GRUPUJ PO DACIE (łącz Wypłatę + Premię z tego samego dnia)
            if wyplaty_reg:
                from collections import defaultdict
                # Grupuj po dacie i sumuj kwoty
                wyplaty_grouped = defaultdict(float)
                for w in wyplaty_reg:
                    wyplaty_grouped[w['data']] += w['kwota']
                
                # Sortuj i przygotuj dane
                dates_reg = sorted(wyplaty_grouped.keys())
                amounts_reg = [wyplaty_grouped[d] for d in dates_reg]
                
                fig_income.add_trace(go.Scatter(
                    x=dates_reg,
                    y=amounts_reg,
                    mode='lines+markers',
                    name='Wypłata regularna',
                    line=dict(color='#00CC96', width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>%{y:,.0f} PLN<extra></extra>'
                ))
                
                # Średnie kroczące (tylko dla regularnych)
                if len(wyplaty_reg) >= 3:
                    ma_3 = []
                    for i in range(len(amounts_reg)):
                        if i < 2:
                            ma_3.append(None)
                        else:
                            ma_3.append(sum(amounts_reg[i-2:i+1]) / 3)
                    
                    fig_income.add_trace(go.Scatter(
                        x=dates_reg,
                        y=ma_3,
                        mode='lines',
                        name='Średnia 3m',
                        line=dict(color='orange', width=2, dash='dash'),
                        hovertemplate='<b>%{x}</b><br>Śr. 3m: %{y:,.0f} PLN<extra></extra>'
                    ))
            
            # Bonusy (scatter - punkty)
            if bonusy_chart:
                dates_bonus = [b['data'] for b in bonusy_chart]
                amounts_bonus = [b['kwota'] for b in bonusy_chart]
                
                fig_income.add_trace(go.Scatter(
                    x=dates_bonus,
                    y=amounts_bonus,
                    mode='markers',
                    name='Bonus 🎉',
                    marker=dict(size=15, color='gold', symbol='star', line=dict(color='orange', width=2)),
                    hovertemplate='<b>%{x}</b><br>💰 Bonus: %{y:,.0f} PLN<extra></extra>'
                ))
            
            fig_income.update_layout(
                title="Trend wpływów w czasie (regularne + bonusy)",
                xaxis_title="Data",
                yaxis_title="Kwota (PLN)",
                hovermode='x unified',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig_income, use_container_width=True)
            
            st.markdown("---")
            
            # === YoY COMPARISON ===
            st.markdown("### 📅 Porównanie Rok do Roku (YoY)")
            
            col_toggle = st.columns([1, 3])
            with col_toggle[0]:
                include_bonuses_yoy = st.checkbox("Uwzględnij bonusy", value=False, help="Włącz bonusy do porównania YoY")
            
            # Grupuj wypłaty po miesiącach i latach
            from collections import defaultdict
            wyplaty_by_month = defaultdict(list)
            
            # Wybierz które wypłaty uwzględnić
            wyplaty_do_yoy = wyplaty if include_bonuses_yoy else wyplaty_regularne
            
            for w in wyplaty_do_yoy:
                date = datetime.fromisoformat(w['data'])
                month_key = f"{date.year}-{date.month:02d}"
                wyplaty_by_month[month_key].append(w['kwota'])
            
            # Oblicz sumy miesięczne
            monthly_totals = {k: sum(v) for k, v in wyplaty_by_month.items()}
            
            # Porównaj ostatnie miesiące z rokiem wcześniej
            current_month = datetime.now().strftime("%Y-%m")
            last_year_month = (datetime.now().replace(year=datetime.now().year - 1)).strftime("%Y-%m")
            
            if current_month in monthly_totals and last_year_month in monthly_totals:
                current = monthly_totals[current_month]
                last_year = monthly_totals[last_year_month]
                yoy_change = ((current - last_year) / last_year * 100) if last_year > 0 else 0
                
                col_yoy1, col_yoy2, col_yoy3 = st.columns(3)
                
                with col_yoy1:
                    st.metric("Bieżący miesiąc", format_currency(current))
                    st.caption("Łącznie za bieżący miesiąc")
                
                with col_yoy2:
                    st.metric("Rok wcześniej", format_currency(last_year))
                    st.caption("Ten sam miesiąc rok temu")
                
                with col_yoy3:
                    st.metric("Zmiana YoY", f"{yoy_change:+.1f}%", delta=f"{current - last_year:+.0f} PLN")
                    st.caption(f"{'Z bonusami' if include_bonuses_yoy else 'Tylko regularne'}")
            else:
                st.info("ℹ️ Brak wystarczających danych do porównania rok do roku")
            
            st.markdown("---")
            
            # === PREDICTED NEXT PAYCHECK ===
            st.markdown("### 🔮 Przewidywana Następna Wypłata")
            
            if len(wyplaty_regularne) >= 3:
                # Predykcja tylko na podstawie wypłat regularnych (bez bonusów)
                ostatnie_3_reg = wyplaty_regularne[:3]
                predicted_amount = sum(w['kwota'] for w in ostatnie_3_reg) / 3
                
                # Znajdź następny dzień wypłaty (zakładamy 10-ty dzień miesiąca)
                today = datetime.now()
                
                # Sprawdź czy w bieżącym miesiącu już była REGULARNA wypłata
                current_month = today.month
                current_year = today.year
                
                already_paid_this_month = any(
                    datetime.strptime(w['data'], "%Y-%m-%d").month == current_month and
                    datetime.strptime(w['data'], "%Y-%m-%d").year == current_year
                    for w in wyplaty_regularne
                )
                
                if already_paid_this_month:
                    # Już była wypłata w tym miesiącu - przewiduj następny miesiąc
                    if today.month == 12:
                        next_paycheck_date = today.replace(year=today.year + 1, month=1, day=10)
                    else:
                        next_paycheck_date = today.replace(month=today.month + 1, day=10)
                else:
                    # Nie było jeszcze wypłaty w tym miesiącu
                    if today.day < 10:
                        next_paycheck_date = today.replace(day=10)
                    else:
                        # Minął już 10-ty dzień - przewiduj następny miesiąc
                        if today.month == 12:
                            next_paycheck_date = today.replace(year=today.year + 1, month=1, day=10)
                        else:
                            next_paycheck_date = today.replace(month=today.month + 1, day=10)
                
                dni_do_wyplaty = (next_paycheck_date - today).days
                
                col_pred1, col_pred2 = st.columns(2)
                
                with col_pred1:
                    st.metric("💰 Przewidywana kwota", f"{predicted_amount:.0f} PLN")
                    st.caption(f"Średnia z ostatnich 3 wypłat regularnych")
                
                with col_pred2:
                    st.metric("📅 Przewidywana data", next_paycheck_date.strftime("%Y-%m-%d"))
                    
                    if dni_do_wyplaty == 0:
                        st.caption("🎉 **DZIŚ!**")
                    elif dni_do_wyplaty == 1:
                        st.caption("⏰ **JUTRO!**")
                    else:
                        st.caption(f"⏰ Za {dni_do_wyplaty} dni")
                
                # Informacja o bonusach
                if bonusy:
                    st.info(f"ℹ️ **Bonusy nie są uwzględniane w predykcji** (są nieregularne). Ostatni bonus: {bonusy[0]['data']} ({bonusy[0]['kwota']:,.0f} PLN)")
            else:
                st.info("ℹ️ Dodaj więcej wypłat regularnych aby zobaczyć predykcję")
        
        st.markdown("---")
        
        # === DODAWANIE WYPŁATY ===
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("add_wyplata"):
                st.markdown("### ➕ Dodaj Wpływ")
                
                # Checkbox czy to bonus
                jest_bonus = st.checkbox(
                    "🎉 To jest jednorazowy bonus",
                    value=False,
                    help="Zaznacz jeśli to bonus (nie będzie dzielony na wypłatę+premia)"
                )
                
                data_wyplaty = st.date_input(
                    "Data wpływu *",
                    value=datetime.now().replace(day=10),
                    help="Domyślnie 10-ty dzień miesiąca"
                )
                
                kwota_total = st.number_input(
                    "Kwota całkowita (PLN) *",
                    min_value=0.0,
                    value=1000.0 if jest_bonus else minimalna_krajowa + 500.0,
                    step=100.0,
                    help="Pełna kwota przelewu - system automatycznie podzieli na wypłatę + premia (jeśli nie bonus)"
                )
                
                # Podgląd podziału (jeśli nie bonus)
                if not jest_bonus and kwota_total > 0:
                    wyplata_czesc = min(kwota_total, minimalna_krajowa)
                    premia_czesc = max(0, kwota_total - minimalna_krajowa)
                    
                    st.info(f"""
                    **📊 Podział automatyczny:**
                    - 💰 Wypłata: **{wyplata_czesc:,.0f} PLN** (minimalna krajowa)
                    - 🎁 Premia: **{premia_czesc:,.0f} PLN** (kwota ponad minimalną)
                    """)
                
                notatki = st.text_area(
                    "Notatki",
                    help="Opcjonalne notatki (np. za co bonus, projekt, etc.)"
                )
                
                submitted = st.form_submit_button("💾 Zapisz", use_container_width=True)
                
                if submitted:
                    # Walidacja
                    if kwota_total <= 0:
                        st.error("❌ Kwota musi być większa od 0")
                    else:
                        miesiac_rok = data_wyplaty.strftime('%Y-%m')
                        timestamp_base = datetime.now().timestamp()
                        
                        if jest_bonus:
                            # === BONUS - jeden wpis ===
                            nowy_bonus = {
                                'id': str(timestamp_base),
                                'typ': 'Bonus',
                                'data': data_wyplaty.isoformat(),
                                'kwota': kwota_total,
                                'notatki': notatki
                            }
                            wyplaty.append(nowy_bonus)
                            
                            # Sortuj od najnowszej
                            wyplaty.sort(key=lambda x: x['data'], reverse=True)
                            
                            if save_wyplaty(wyplaty):
                                st.success(f"✅ 🎉 Bonus zapisany: {kwota_total:,.0f} PLN")
                                st.rerun()
                            else:
                                st.error("❌ Błąd zapisu")
                        
                        else:
                            # === WYPŁATA + PREMIA - dwa wpisy ===
                            
                            # Sprawdź czy nie ma już wypłaty w tym miesiącu
                            duplikat = any(
                                w['data'].startswith(miesiac_rok) and w.get('typ', 'Wypłata') == 'Wypłata' 
                                for w in wyplaty
                            )
                            
                            if duplikat:
                                st.warning(f"⚠️ Wypłata za {miesiac_rok} już istnieje. Zostanie dodana jako dodatkowa.")
                            
                            # Podział kwoty
                            wyplata_czesc = min(kwota_total, minimalna_krajowa)
                            premia_czesc = max(0, kwota_total - minimalna_krajowa)
                            
                            # Dodaj Wypłatę (ZAPISZ MINIMALNĄ KRAJOWĄ dla historii)
                            nowa_wyplata = {
                                'id': str(timestamp_base),
                                'typ': 'Wypłata',
                                'data': data_wyplaty.isoformat(),
                                'kwota': wyplata_czesc,
                                'minimalna_krajowa': minimalna_krajowa,  # ZAPISZ dla historii
                                'notatki': f"Minimalna krajowa {minimalna_krajowa:,.0f} PLN" + (f" | {notatki}" if notatki else "")
                            }
                            wyplaty.append(nowa_wyplata)
                            
                            # Dodaj Premię (jeśli jest)
                            if premia_czesc > 0:
                                nowa_premia = {
                                    'id': str(timestamp_base + 0.001),  # Lekko inny timestamp
                                    'typ': 'Premia',
                                    'data': data_wyplaty.isoformat(),
                                    'kwota': premia_czesc,
                                    'minimalna_krajowa': minimalna_krajowa,  # ZAPISZ dla historii
                                    'notatki': f"Premia ponad minimalną" + (f" | {notatki}" if notatki else "")
                                }
                                wyplaty.append(nowa_premia)
                            
                            # Sortuj od najnowszej
                            wyplaty.sort(key=lambda x: x['data'], reverse=True)
                            
                            if save_wyplaty(wyplaty):
                                st.success(f"""
                                ✅ **Zapisano wpływ:** {kwota_total:,.0f} PLN
                                - 💰 Wypłata: {wyplata_czesc:,.0f} PLN
                                {f"- 🎁 Premia: {premia_czesc:,.0f} PLN" if premia_czesc > 0 else ""}
                                """)
                                st.rerun()
                            else:
                                st.error("❌ Błąd zapisu")
        
        with col2:
            st.markdown("### 📊 Szybkie Statystyki")
            if wyplaty:
                # Rozdziel po typach
                wyplaty_regularne = [w for w in wyplaty if w.get('typ', 'Wypłata') in ['Wypłata', 'Premia']]
                bonusy = [w for w in wyplaty if w.get('typ', 'Wypłata') == 'Bonus']
                
                ostatnia = wyplaty[0]
                typ_emoji = "💰" if ostatnia.get('typ', 'Wypłata') == "Wypłata" else "🎁" if ostatnia.get('typ') == "Premia" else "🎉"
                
                st.info(f"""
                **Ostatni wpływ:**
                - {typ_emoji} Typ: {ostatnia.get('typ', 'Wypłata')}
                - 📅 Data: {ostatnia['data']}
                - � Kwota: {ostatnia['kwota']:.2f} PLN
                """)
                
                # Statystyki bonusów
                if bonusy:
                    suma_bonusow = sum(b['kwota'] for b in bonusy)
                    st.success(f"""
                    **🎉 Bonusy (łącznie):**
                    - Liczba: {len(bonusy)}
                    - Suma: {suma_bonusow:,.0f} PLN
                    """)
                
                # Trend wypłat regularnych (ostatnie 3)
                if len(wyplaty_regularne) >= 3:
                    ostatnie_3_reg = wyplaty_regularne[:3]
                    kwoty = [w['kwota'] for w in ostatnie_3_reg]
                    trend = "📈 Rosnąca" if kwoty[0] > kwoty[-1] else "📉 Malejąca" if kwoty[0] < kwoty[-1] else "➡️ Stabilna"
                    st.caption(f"Trend wypłat (3 mies.): {trend}")
            else:
                st.caption("Brak danych")
        
        # === HISTORIA WYPŁAT ===
        if wyplaty:
            st.markdown("### 📋 Historia Wypłat")
            
            # Filtr roku i typu
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                lata = sorted(set(w['data'][:4] for w in wyplaty), reverse=True)
                if len(lata) > 1:
                    filtr_rok = st.selectbox("Filtruj rok:", ["Wszystkie"] + lata)
                else:
                    filtr_rok = "Wszystkie"
            
            with col_filter2:
                filtr_typ = st.selectbox("Filtruj typ:", ["Wszystkie", "Wypłata regularna", "Bonus"])
            
            # GRUPUJ WYPŁATY - połącz Wypłatę + Premia z tego samego dnia
            from collections import defaultdict
            wyplaty_grouped = defaultdict(lambda: {'kwota': 0, 'typy': [], 'notatki': [], 'ids': [], 'minimalna': None})
            
            for w in wyplaty:
                data = w['data']
                typ = w.get('typ', 'Wypłata')
                
                if typ in ['Wypłata', 'Premia']:
                    # Wypłaty regularne - grupuj po dacie
                    wyplaty_grouped[data]['kwota'] += w['kwota']
                    wyplaty_grouped[data]['typy'].append(typ)
                    wyplaty_grouped[data]['ids'].append(w['id'])
                    if w.get('notatki'):
                        wyplaty_grouped[data]['notatki'].append(w['notatki'])
                    if w.get('minimalna_krajowa'):
                        wyplaty_grouped[data]['minimalna'] = w['minimalna_krajowa']
                    wyplaty_grouped[data]['is_bonus'] = False
                else:
                    # Bonusy - każdy osobno
                    bonus_key = f"{data}_bonus_{w['id']}"
                    wyplaty_grouped[bonus_key] = {
                        'kwota': w['kwota'],
                        'typy': ['Bonus'],
                        'notatki': [w.get('notatki', '')] if w.get('notatki') else [],
                        'ids': [w['id']],
                        'minimalna': None,
                        'is_bonus': True,
                        'data': data
                    }
            
            # Sortuj po dacie (od najnowszej)
            wyplaty_sorted_grouped = sorted(
                [(k, v) for k, v in wyplaty_grouped.items()],
                key=lambda x: x[1].get('data', x[0]) if x[1]['is_bonus'] else x[0],
                reverse=True
            )
            
            # Filtrowanie
            wyplaty_filtr = []
            for key, group in wyplaty_sorted_grouped:
                data = group.get('data', key) if group['is_bonus'] else key
                
                # Filtr roku
                if filtr_rok != "Wszystkie" and not data.startswith(filtr_rok):
                    continue
                
                # Filtr typu
                if filtr_typ == "Wypłata regularna" and group['is_bonus']:
                    continue
                elif filtr_typ == "Bonus" and not group['is_bonus']:
                    continue
                
                wyplaty_filtr.append((key, group, data))
            
            # Podsumowanie po filtrach
            if wyplaty_filtr:
                suma_filtr = sum(g[1]['kwota'] for g in wyplaty_filtr)
                st.caption(f"**{len(wyplaty_filtr)} wpływ(ów)** | Suma: **{suma_filtr:,.0f} PLN**")
            
            # Tabela - wyświetl pogrupowane
            for key, group, data in wyplaty_filtr:
                if group['is_bonus']:
                    typ_display = "🎉 Bonus"
                    typ_label = "Bonus"
                else:
                    typ_display = "💰 Wypłata regularna"
                    typ_label = "Regularna"
                    if 'Premia' in group['typy'] and 'Wypłata' in group['typy']:
                        typ_display += " (Wypłata + Premia)"
                
                with st.expander(f"{typ_display.split()[0]} {data} - **{group['kwota']:,.0f} PLN** ({typ_label})"):
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.metric("💵 Kwota łączna", f"{group['kwota']:,.0f} PLN")
                    with col_m2:
                        st.metric("📌 Typ", typ_label)
                    
                    # Szczegóły składowych (jeśli wypłata + premia)
                    if len(group['typy']) > 1:
                        st.caption("📊 **Składowe:**")
                        for orig_w in wyplaty:
                            if orig_w['id'] in group['ids']:
                                st.caption(f"  • {orig_w.get('typ', 'Wypłata')}: {orig_w['kwota']:,.0f} PLN")
                    
                    if group['notatki']:
                        st.caption(f"📝 {' | '.join(group['notatki'])}")
                    
                    # Pokaż zapisaną minimalną krajową (jeśli jest)
                    if group['minimalna']:
                        st.info(f"⚙️ **Minimalna krajowa w tym okresie:** {group['minimalna']:,.0f} PLN")
                    
                    # Edycja/usuwanie - tylko dla bonusów
                    if group['is_bonus']:
                        st.markdown("---")
                        orig_wyplata = next((w for w in wyplaty if w['id'] == group['ids'][0]), None)
                        
                        if orig_wyplata:
                            with st.form(f"edit_wyplata_{orig_wyplata['id']}"):
                                st.caption("Edytuj bonus:")
                                
                                col_edit1, col_edit2 = st.columns(2)
                                with col_edit1:
                                    nowa_data = st.date_input(
                                        "Data",
                                        value=datetime.fromisoformat(orig_wyplata['data']),
                                        key=f"data_{orig_wyplata['id']}"
                                    )
                                with col_edit2:
                                    nowa_kwota = st.number_input(
                                        "Kwota (PLN)",
                                        min_value=0.0,
                                        value=float(orig_wyplata['kwota']),
                                        step=100.0,
                                        key=f"kwota_{orig_wyplata['id']}"
                                    )
                                
                                nowe_notatki = st.text_input(
                                    "Notatki",
                                    value=orig_wyplata.get('notatki', ''),
                                    key=f"notatki_{orig_wyplata['id']}"
                                )
                                
                                col_save, col_delete = st.columns([1, 1])
                                
                                with col_save:
                                    if st.form_submit_button("💾 Zapisz", use_container_width=True):
                                        orig_wyplata['kwota'] = nowa_kwota
                                        orig_wyplata['data'] = nowa_data.isoformat()
                                        orig_wyplata['notatki'] = nowe_notatki
                                        wyplaty.sort(key=lambda x: x['data'], reverse=True)
                                        if save_wyplaty(wyplaty):
                                            st.success("✅ Zaktualizowano!")
                                            st.rerun()
                                
                                with col_delete:
                                    if st.form_submit_button("🗑️ Usuń", use_container_width=True, type="secondary"):
                                        wyplaty.remove(orig_wyplata)
                                        if save_wyplaty(wyplaty):
                                            st.success("✅ Usunięto!")
                                            st.rerun()
                    else:
                        # Dla wypłat regularnych - przycisk usuwania grupy
                        st.markdown("---")
                        st.caption("💡 Aby skorygować kwotę, usuń i dodaj ponownie.")
                        if st.button(f"🗑️ Usuń tę wypłatę", key=f"delete_group_{key}"):
                            for wid in group['ids']:
                                wpis_to_remove = next((w for w in wyplaty if w['id'] == wid), None)
                                if wpis_to_remove:
                                    wyplaty.remove(wpis_to_remove)
                            if save_wyplaty(wyplaty):
                                st.success("✅ Usunięto!")
                                st.rerun()
                
            # === WYKRES WYPŁAT ===
            st.markdown("### 📊 Wizualizacja Wypłat")
            
            # Przygotuj dane dla wykresu (ostatnie 12 miesięcy) - pogrupowane
            wyplaty_do_wykresu = wyplaty
            if filtr_rok != "Wszystkie":
                wyplaty_do_wykresu = [w for w in wyplaty_do_wykresu if w['data'].startswith(filtr_rok)]
            
            # Grupuj także dla wykresu (łącz Wypłata + Premia)
            from collections import defaultdict
            wyplaty_wykres_grouped = defaultdict(float)
            bonusy_wykres = []
            
            for w in wyplaty_do_wykresu:
                typ = w.get('typ', 'Wypłata')
                if typ in ['Wypłata', 'Premia']:
                    wyplaty_wykres_grouped[w['data']] += w['kwota']
                elif filtr_typ in ["Wszystkie", "Bonus"]:  # Pokaż bonusy jeśli filtr pozwala
                    bonusy_wykres.append(w)
            
            # Sortuj i weź ostatnie 12 pozycji
            wyplaty_wykres_sorted = sorted(wyplaty_wykres_grouped.items(), key=lambda x: x[0])[-12:]
            
            if wyplaty_wykres_sorted or bonusy_wykres:
                fig = go.Figure()
                
                if wyplaty_wykres_sorted:
                    daty = [x[0] for x in wyplaty_wykres_sorted]
                    kwoty = [x[1] for x in wyplaty_wykres_sorted]
                
                fig.add_trace(go.Bar(
                    name='Wypłata',
                    x=daty,
                    y=kwoty,
                    marker_color='#1f77b4',
                    text=[f"{k:.0f}" for k in kwoty],
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title="Wypłaty - Ostatnie 12 miesięcy",
                    xaxis_title="Data",
                    yaxis_title="Kwota (PLN)",
                    hovermode='x unified',
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, width="stretch")
    
    # ===== TAB 5: STAŁE WYDATKI =====
    with tab5:
        st.header("📋 Stałe Wydatki Miesięczne")
        
        wydatki = load_wydatki()
        
        # Informacja o systemie
        st.info("""
        📋 **System wydatków:**
        - Wydatki stałe: powtarzają się co miesiąc
        - Wydatki nadprogramowe: jednorazowe, niecykliczne
        """)
        
        # === PODSUMOWANIE ===
        if wydatki:
            wydatki_stale = [w for w in wydatki if not w.get('nadprogramowy', False)]
            wydatki_nadprog = [w for w in wydatki if w.get('nadprogramowy', False)]
            
            suma_stale = sum(w['kwota'] for w in wydatki_stale)
            suma_nadprog = sum(w['kwota'] for w in wydatki_nadprog)
            suma_total = suma_stale + suma_nadprog
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Suma Stałe", format_currency(suma_stale))
            with col2:
                st.metric("🔥 Nadprogramowe", format_currency(suma_nadprog))
            with col3:
                st.metric("📊 Total", format_currency(suma_total))
            with col4:
                st.metric("🔢 Liczba wydatków", len(wydatki))
        
        # === DODAWANIE WYDATKU ===
        st.markdown("### ➕ Dodaj Wydatek")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("add_wydatek"):
                nazwa = st.text_input(
                    "Nazwa wydatku *",
                    placeholder="np. Czynsz, Netflix, Zakupy"
                )
                
                kwota = st.number_input(
                    "Kwota (PLN) *",
                    min_value=0.0,
                    value=0.0,
                    step=10.0
                )
                
                kategoria = st.selectbox(
                    "Kategoria *",
                    ["Mieszkanie", "Media", "Transport", "Jedzenie", "Zdrowie", 
                     "Rozrywka", "Subskrypcje", "Inne"]
                )
                
                nadprogramowy = st.checkbox(
                    "Wydatek nadprogramowy",
                    help="Zaznacz jeśli to jednorazowy wydatek (nie powtarza się co miesiąc)"
                )
                
                notatki = st.text_area(
                    "Notatki",
                    help="Opcjonalne szczegóły"
                )
                
                submitted = st.form_submit_button("💾 Zapisz Wydatek")
                
                if submitted:
                    # Walidacja
                    if not nazwa:
                        st.error("❌ Nazwa jest wymagana")
                    elif kwota <= 0:
                        st.error("❌ Kwota musi być większa od 0")
                    else:
                        nowy_wydatek = {
                            'id': str(datetime.now().timestamp()),
                            'nazwa': nazwa,
                            'kwota': kwota,
                            'kategoria': kategoria,
                            'nadprogramowy': nadprogramowy,
                            'notatki': notatki,
                            'data_dodania': datetime.now().isoformat()
                        }
                        
                        wydatki.append(nowy_wydatek)
                        # Sortuj alfabetycznie po nazwie
                        wydatki.sort(key=lambda x: x['nazwa'])
                        
                        if save_wydatki(wydatki):
                            st.success("✅ Wydatek zapisany!")
                            st.rerun()
                        else:
                            st.error("❌ Błąd zapisu wydatku")
        
        with col2:
            st.markdown("### 📊 Podział po Kategoriach")
            if wydatki:
                # Grupuj po kategoriach
                kategorie_suma = {}
                for w in wydatki:
                    if not w.get('nadprogramowy', False):  # Tylko stałe
                        kat = w['kategoria']
                        kategorie_suma[kat] = kategorie_suma.get(kat, 0) + w['kwota']
                
                if kategorie_suma:
                    for kat, suma in sorted(kategorie_suma.items(), key=lambda x: x[1], reverse=True):
                        procent = (suma / suma_stale * 100) if suma_stale > 0 else 0
                        st.caption(f"**{kat}**: {suma:.0f} PLN ({procent:.1f}%)")
                else:
                    st.caption("Brak wydatków stałych")
            else:
                st.caption("Brak danych")
        
        # === LISTA WYDATKÓW ===
        if wydatki:
            st.markdown("---")
            st.markdown("### 📋 Lista Wydatków")
            
            # Filtr
            filtr = st.radio(
                "Pokaż:",
                ["Wszystkie", "Stałe", "Nadprogramowe"],
                horizontal=True
            )
            
            # Filtrowanie
            if filtr == "Stałe":
                wydatki_filtr = [w for w in wydatki if not w.get('nadprogramowy', False)]
            elif filtr == "Nadprogramowe":
                wydatki_filtr = [w for w in wydatki if w.get('nadprogramowy', False)]
            else:
                wydatki_filtr = wydatki
            
            # Grupuj po kategoriach
            kategorie = {}
            for w in wydatki_filtr:
                kat = w['kategoria']
                if kat not in kategorie:
                    kategorie[kat] = []
                kategorie[kat].append(w)
            
            # Wyświetl po kategoriach
            for kategoria, lista in sorted(kategorie.items()):
                suma_kat = sum(w['kwota'] for w in lista)
                
                with st.expander(f"**{kategoria}** - {format_currency(suma_kat)} ({len(lista)} wydatków)", expanded=True):
                    for wydatek in lista:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            ikona = "🔥" if wydatek.get('nadprogramowy', False) else "💰"
                            st.write(f"{ikona} **{wydatek['nazwa']}**")
                            if wydatek.get('notatki'):
                                st.caption(f"📝 {wydatek['notatki']}")
                        
                        with col2:
                            st.metric("Kwota", f"{wydatek['kwota']:.2f} PLN")
                        
                        with col3:
                            # Edycja/Usunięcie
                            with st.form(f"action_{wydatek['id']}"):
                                col_edit, col_del = st.columns(2)
                                
                                with col_edit:
                                    if st.form_submit_button("✏️", width="stretch"):
                                        st.session_state[f'edit_{wydatek["id"]}'] = True
                                        st.rerun()
                                
                                with col_del:
                                    if st.form_submit_button("🗑️", width="stretch"):
                                        if f'confirm_del_{wydatek["id"]}' not in st.session_state:
                                            st.session_state[f'confirm_del_{wydatek["id"]}'] = True
                                            st.warning("Kliknij ponownie")
                                        else:
                                            wydatki.remove(wydatek)
                                            if save_wydatki(wydatki):
                                                del st.session_state[f'confirm_del_{wydatek["id"]}']
                                                st.success("✅ Usunięto!")
                                                st.rerun()
                        
                        # Formularz edycji (jeśli aktywny)
                        if st.session_state.get(f'edit_{wydatek["id"]}', False):
                            st.markdown("---")
                            with st.form(f"edit_form_{wydatek['id']}"):
                                st.caption("Edytuj wydatek:")
                                
                                nowa_kwota = st.number_input(
                                    "Kwota (PLN)",
                                    min_value=0.0,
                                    value=float(wydatek['kwota']),
                                    step=10.0,
                                    key=f"edit_kwota_{wydatek['id']}"
                                )
                                
                                nowy_nadprog = st.checkbox(
                                    "Nadprogramowy",
                                    value=wydatek.get('nadprogramowy', False),
                                    key=f"edit_nadprog_{wydatek['id']}"
                                )
                                
                                col_save, col_cancel = st.columns(2)
                                
                                with col_save:
                                    if st.form_submit_button("💾 Zapisz", width="stretch"):
                                        wydatek['kwota'] = nowa_kwota
                                        wydatek['nadprogramowy'] = nowy_nadprog
                                        if save_wydatki(wydatki):
                                            del st.session_state[f'edit_{wydatek["id"]}']
                                            st.success("✅ Zaktualizowano!")
                                            st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button("❌ Anuluj", width="stretch"):
                                        del st.session_state[f'edit_{wydatek["id"]}']
                                        st.rerun()
                        
                        st.markdown("---")
            
            # === WYKRES WYDATKÓW ===
            st.markdown("### 📊 Wizualizacja Wydatków")
            
            # Wykres po kategoriach (tylko stałe)
            wydatki_stale_wykres = [w for w in wydatki if not w.get('nadprogramowy', False)]
            
            if wydatki_stale_wykres:
                kategorie_dane = {}
                for w in wydatki_stale_wykres:
                    kat = w['kategoria']
                    kategorie_dane[kat] = kategorie_dane.get(kat, 0) + w['kwota']
                
                fig = go.Figure(data=[
                    go.Pie(
                        labels=list(kategorie_dane.keys()),
                        values=list(kategorie_dane.values()),
                        hole=.3,
                        textinfo='label+percent',
                        textposition='outside'
                    )
                ])
                
                fig.update_layout(
                    title="Podział Wydatków Stałych po Kategoriach",
                    height=400
                )
                
                st.plotly_chart(fig, width="stretch")
    
    # ===== TAB 6: KRYPTO =====
    with tab6:
        st.header("₿ Portfel Kryptowalut")
        
        krypto = load_krypto()
        
        # === POBIERZ AKTUALNE CENY DLA CAŁEGO TAB (raz na początku) ===
        current_prices = {}
        if krypto and CRYPTO_MANAGER_OK:
            try:
                symbols = list(set(k['symbol'] for k in krypto))
                current_prices = get_cached_crypto_prices(symbols)
            except Exception as e:
                st.warning(f"⚠️ Nie udało się pobrać aktualnych cen: {e}")
        
        # Informacja o systemie
        st.info("""
        📋 **Zarządzanie kryptowalutami (Lokalne dane - krypto.json):**
        - ✅ **Pełna kontrola** - wszystkie dane przechowywane lokalnie
        - 🏦 Obsługa wielu platform (Binance, Gate.io, MEXC, etc.)
        - 💰 Śledź ilość, średnią cenę zakupu i wartość pozycji
        - 📈 Monitoruj APY/Staking dla pozycji generujących dochód
        - 🟢 **NOWOŚĆ:** Real-time ceny z CoinGecko + P&L analysis!
        - ⚠️ **Dane NIE są pobierane z Google Sheets** - zarządzaj wszystkim tutaj!
        """)
        
        # === FEAR & GREED INDEX (Feature #5) ===
        if CRYPTO_MANAGER_OK and krypto:
            try:
                fg_data = st.session_state.crypto_manager.get_fear_greed_index()
                if fg_data:
                    value = fg_data['value']
                    classification = fg_data['value_classification']
                    
                    # Kolor bazowany na wartości
                    if value < 25:
                        color = "#DC2626"  # Extreme Fear - czerwony
                        emoji = "😱"
                        interpretation = "Skrajny strach - może być dobry moment na zakupy!"
                    elif value < 45:
                        color = "#F59E0B"  # Fear - pomarańczowy
                        emoji = "😰"
                        interpretation = "Strach na rynku - okazje inwestycyjne?"
                    elif value < 55:
                        color = "#10B981"  # Neutral - zielony
                        emoji = "😐"
                        interpretation = "Neutralny sentyment rynkowy"
                    elif value < 75:
                        color = "#3B82F6"  # Greed - niebieski
                        emoji = "😊"
                        interpretation = "Chciwość - rynek rośnie, bądź ostrożny"
                    else:
                        color = "#8B5CF6"  # Extreme Greed - fioletowy
                        emoji = "🤑"
                        interpretation = "Skrajna chciwość - możliwa korekta!"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {color}22 0%, {color}11 100%); 
                                border-left: 4px solid {color}; 
                                padding: 15px; 
                                border-radius: 8px; 
                                margin: 10px 0;">
                        <h3 style="margin: 0; color: {color};">{emoji} Fear & Greed Index: {value}/100</h3>
                        <p style="margin: 5px 0; font-size: 16px;"><strong>{classification}</strong></p>
                        <p style="margin: 0; color: #666;">{interpretation}</p>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                pass  # Cicho ignoruj błędy Fear & Greed
        
        # === PODSUMOWANIE Z REAL-TIME DATA (Feature #1, #7) ===
        if krypto:
            # Oblicz statystyki zakupu
            total_wartosc_zakupu = sum(k['ilosc'] * k['cena_zakupu_usd'] for k in krypto)
            liczba_platform = len(set(k['platforma'] for k in krypto))
            liczba_aktywow = len(krypto)
            srednie_apy = sum(k.get('apy', 0) for k in krypto) / len(krypto) if krypto else 0
            
            # Oblicz aktualną wartość i P&L (używa current_prices z góry TAB)
            total_wartosc_current = 0
            total_pnl = 0
            
            if current_prices:
                # Oblicz aktualną wartość i P&L
                for k in krypto:
                    symbol = k['symbol']
                    if symbol in current_prices and current_prices[symbol].get('current_price'):
                        current_price = current_prices[symbol]['current_price']
                        current_value = k['ilosc'] * current_price
                        purchase_value = k['ilosc'] * k['cena_zakupu_usd']
                        pnl = current_value - purchase_value
                        
                        total_wartosc_current += current_value
                        total_pnl += pnl
            
            # Metryki - 5 kolumn
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💰 Wartość zakupu", f"${total_wartosc_zakupu:.2f}", 
                         help="Wartość według średniej ceny zakupu")
            
            with col2:
                if total_wartosc_current > 0:
                    st.metric("📈 Wartość aktualna", f"${total_wartosc_current:.2f}",
                             delta=f"${total_pnl:.2f}",
                             help="Aktualna wartość rynkowa (live prices)")
                else:
                    st.metric("🔢 Liczba aktywów", liczba_aktywow)
            
            with col3:
                if total_pnl != 0 and total_wartosc_zakupu > 0:
                    pnl_percent = (total_pnl / total_wartosc_zakupu) * 100
                    st.metric("💵 Zysk/Strata", 
                             f"{'+' if total_pnl > 0 else ''}{pnl_percent:.2f}%",
                             delta=f"${total_pnl:.2f}",
                             help="Całkowity profit/loss")
                else:
                    st.metric("🔢 Liczba aktywów", liczba_aktywow)
            
            with col4:
                st.metric("🏦 Platformy", liczba_platform)
            
            with col5:
                st.metric("📈 Średnie APY", f"{srednie_apy:.2f}%")
            
            # === RISK ANALYTICS (Feature #8) ===
            st.markdown("---")
            st.markdown("### ⚠️ Analiza Ryzyka Portfela")
            
            # Oblicz concentration metrics
            coin_concentration = {}
            platform_concentration = {}
            stablecoin_value = 0
            total_value = total_wartosc_current if total_wartosc_current > 0 else total_wartosc_zakupu
            
            for k in krypto:
                # Coin concentration
                symbol = k['symbol']
                if CRYPTO_MANAGER_OK and symbol in current_prices and current_prices[symbol].get('current_price'):
                    value = k['ilosc'] * current_prices[symbol]['current_price']
                else:
                    value = k['ilosc'] * k['cena_zakupu_usd']
                
                coin_concentration[symbol] = coin_concentration.get(symbol, 0) + value
                
                # Platform concentration
                platform = k['platforma']
                platform_concentration[platform] = platform_concentration.get(platform, 0) + value
                
                # Stablecoin tracking
                if symbol.upper() in ['USDT', 'USDC', 'BUSD', 'DAI', 'GUSD', 'USDY', 'TUSD', 'USDP']:
                    stablecoin_value += value
            
            # Alerts
            alerts = []
            
            # Check coin concentration (>40% in one coin)
            if coin_concentration:
                try:
                    max_coin = max(coin_concentration.items(), key=lambda x: x[1])
                    max_coin_percent = (max_coin[1] / total_value * 100) if total_value > 0 else 0
                    if max_coin_percent > 40:
                        alerts.append(f"🔴 **Wysoka koncentracja:** {max_coin[0]} stanowi {max_coin_percent:.1f}% portfela")
                    elif max_coin_percent > 25:
                        alerts.append(f"🟡 **Średnia koncentracja:** {max_coin[0]} stanowi {max_coin_percent:.1f}% portfela")
                except ValueError:
                    pass
            
            # Check platform concentration (>60% on one platform)
            if platform_concentration:
                try:
                    max_platform = max(platform_concentration.items(), key=lambda x: x[1])
                    max_platform_percent = (max_platform[1] / total_value * 100) if total_value > 0 else 0
                    if max_platform_percent > 70:
                        alerts.append(f"🔴 **Ryzyko platformy:** {max_platform[0]} - {max_platform_percent:.1f}% aktywów")
                    elif max_platform_percent > 50:
                        alerts.append(f"🟡 **Koncentracja platformy:** {max_platform[0]} - {max_platform_percent:.1f}% aktywów")
                except ValueError:
                    pass
            
            # Check stablecoin ratio
            stablecoin_percent = (stablecoin_value / total_value * 100) if total_value > 0 else 0
            if stablecoin_percent > 60:
                alerts.append(f"🔵 **Wysoki % stablecoinów:** {stablecoin_percent:.1f}% (mała ekspozycja na wzrosty)")
            elif stablecoin_percent < 10:
                alerts.append(f"🟡 **Niski % stablecoinów:** {stablecoin_percent:.1f}% (większe ryzyko zmienności)")
            
            # Display alerts or OK status
            if alerts:
                for alert in alerts:
                    st.warning(alert)
            else:
                st.success("✅ **Portfel dobrze zdywersyfikowany!** Brak alertów ryzyka.")
            
            # Risk metrics w kolumnach
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                max_coin = max(coin_concentration.items(), key=lambda x: x[1]) if coin_concentration else ("N/A", 0)
                max_coin_pct = (max_coin[1] / total_value * 100) if total_value > 0 else 0
                st.metric("🪙 Największa pozycja", f"{max_coin[0]}", f"{max_coin_pct:.1f}%")
            
            with col_r2:
                max_plat = max(platform_concentration.items(), key=lambda x: x[1]) if platform_concentration else ("N/A", 0)
                max_plat_pct = (max_plat[1] / total_value * 100) if total_value > 0 else 0
                st.metric("🏦 Główna platforma", f"{max_plat[0]}", f"{max_plat_pct:.1f}%")
            
            with col_r3:
                st.metric("💵 Stablecoiny", f"${stablecoin_value:.2f}", f"{stablecoin_percent:.1f}%")
        
        # === APY EARNINGS BREAKDOWN (Feature #2) ===
        if krypto:
            st.markdown("---")
            st.markdown("### 💰 Zarobki z APY/Staking/Earn")
            
            # Oblicz earnings
            kurs_usd = DEFAULT_USD_PLN_RATE  # Default, można pobrać z API
            crypto_earnings = calculate_crypto_apy_earnings(krypto, current_prices, kurs_usd)
            
            if crypto_earnings['liczba_earning_positions'] > 0:
                # Summary metrics
                col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                
                with col_e1:
                    st.metric("📅 Dziennie", 
                             f"${crypto_earnings['dziennie_usd']:.2f}",
                             delta=f"{crypto_earnings['dziennie_pln']:.2f} PLN")
                
                with col_e2:
                    st.metric("📆 Miesięcznie", 
                             f"${crypto_earnings['miesieczne_usd']:.2f}",
                             delta=f"{crypto_earnings['miesieczne_pln']:.2f} PLN")
                
                with col_e3:
                    st.metric("📊 Rocznie", 
                             f"${crypto_earnings['roczne_usd']:.2f}",
                             delta=f"{crypto_earnings['roczne_pln']:.2f} PLN")
                
                with col_e4:
                    st.metric("💎 Earning Positions", 
                             crypto_earnings['liczba_earning_positions'])
                
                # Detailed breakdown
                st.markdown("#### 📋 Szczegóły zarobków po pozycjach:")
                
                for detail in crypto_earnings['szczegoly']:
                    col_d1, col_d2, col_d3, col_d4 = st.columns([2, 1, 1, 2])
                    
                    with col_d1:
                        st.write(f"**{detail['symbol']}** ({detail['status']})")
                        st.caption(f"APY: {detail['apy']:.2f}%")
                    
                    with col_d2:
                        st.caption(f"Wartość: ${detail['value_usd']:.2f}")
                    
                    with col_d3:
                        st.caption(f"Dziennie: ${detail['dziennie_usd']:.2f}")
                    
                    with col_d4:
                        st.caption(f"Miesięcznie: ${detail['miesieczne_usd']:.2f}")
                        st.caption(f"Rocznie: ${detail['roczne_usd']:.2f}")
                
                st.success(f"💡 **Tip:** Twój portfel crypto generuje pasywny dochód {crypto_earnings['miesieczne_pln']:.0f} PLN/mies bez dodatkowej pracy!")
            else:
                st.info("ℹ️ Brak pozycji generujących dochód pasywny (APY/Staking/Earn). Rozważ earning products!")
        
        # === DODAWANIE KRYPTO ===
        st.markdown("---")
        st.markdown("### ➕ Dodaj Kryptowalutę")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("add_krypto"):
                symbol = st.text_input(
                    "Symbol/Ticker *",
                    placeholder="np. BTC, ETH, BNB",
                    help="Skrót kryptowaluty"
                ).upper()
                
                ilosc = st.number_input(
                    "Ilość *",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.8f"
                )
                
                cena_zakupu = st.number_input(
                    "Średnia cena zakupu (USD) *",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f"
                )
                
                platforma = st.selectbox(
                    "Platforma *",
                    ["Binance", "Gate.io", "MEXC", "Coinbase", "Kraken", 
                     "KuCoin", "Bybit", "OKX", "Bitget", "Inne"]
                )
                
                status = st.selectbox(
                    "Status",
                    ["Spot", "Earn", "Launchpool", "Staking", "Lending", 
                     "Kickstarter", "Farming", "Locked", "Inne"]
                )
                
                apy = st.number_input(
                    "APY % (jeśli dotyczy)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    help="Roczny procent zysku"
                )
                
                notatki = st.text_area(
                    "Notatki",
                    help="Dodatkowe informacje"
                )
                
                submitted = st.form_submit_button("💾 Zapisz Kryptowalutę")
                
                if submitted:
                    # Walidacja
                    if not symbol:
                        st.error("❌ Symbol jest wymagany")
                    elif ilosc <= 0:
                        st.error("❌ Ilość musi być większa od 0")
                    elif cena_zakupu <= 0:
                        st.error("❌ Cena zakupu musi być większa od 0")
                    else:
                        nowe_krypto = {
                            'id': str(datetime.now().timestamp()),
                            'symbol': symbol,
                            'ilosc': ilosc,
                            'cena_zakupu_usd': cena_zakupu,
                            'platforma': platforma,
                            'status': status,
                            'apy': apy,
                            'notatki': notatki,
                            'data_dodania': datetime.now().isoformat()
                        }
                        
                        krypto.append(nowe_krypto)
                        # Sortuj alfabetycznie po symbolu
                        krypto.sort(key=lambda x: x['symbol'])
                        
                        if save_krypto(krypto):
                            st.success("✅ Kryptowaluta zapisana!")
                            st.rerun()
                        else:
                            st.error("❌ Błąd zapisu")
        
        with col2:
            st.markdown("### 📊 Podział po Platformach")
            if krypto:
                # Grupuj po platformach
                platformy_suma = {}
                for k in krypto:
                    plat = k['platforma']
                    wartosc = k['ilosc'] * k['cena_zakupu_usd']
                    platformy_suma[plat] = platformy_suma.get(plat, 0) + wartosc
                
                total = sum(platformy_suma.values())
                
                for plat, suma in sorted(platformy_suma.items(), key=lambda x: x[1], reverse=True):
                    procent = (suma / total * 100) if total > 0 else 0
                    st.caption(f"**{plat}**: ${suma:.2f} ({procent:.1f}%)")
            else:
                st.caption("Brak danych")
        
        # === LISTA KRYPTOWALUT ===
        if krypto:
            st.markdown("---")
            st.markdown("### 📋 Twoje Kryptowaluty")
            
            # === TABELA PORÓWNAWCZA CEN ===
            st.markdown("#### 💰 Porównanie Cen: Zakup vs Aktualne")
            
            # Grupuj po symbolach dla tabeli
            price_comparison = []
            for symbol in set(k['symbol'] for k in krypto):
                holdings_of_symbol = [k for k in krypto if k['symbol'] == symbol]
                total_qty = sum(k['ilosc'] for k in holdings_of_symbol)
                total_cost = sum(k['ilosc'] * k['cena_zakupu_usd'] for k in holdings_of_symbol)
                avg_purchase_price = total_cost / total_qty if total_qty > 0 else 0
                
                # Pobierz aktualną cenę
                current_price = None
                change_24h = None
                pnl_usd = None
                pnl_pct = None
                price_source = ""  # Skąd pochodzi cena
                
                # Priorytet 1: API (live data)
                if CRYPTO_MANAGER_OK and symbol in current_prices:
                    coin_data = current_prices[symbol]
                    if coin_data.get('current_price'):
                        current_price = coin_data['current_price']
                        change_24h = coin_data.get('price_change_percentage_24h')
                        
                        # Sprawdź źródło API
                        api_source = coin_data.get('source', 'CoinGecko')
                        if 'MEXC' in api_source:
                            price_source = "🟠 MEXC"
                        elif 'Gate.io' in api_source:
                            price_source = "🔵 Gate.io"
                        else:
                            price_source = "🟢 CoinGecko"
                
                # Priorytet 2: Manual price z pierwszego holdingu (backup)
                if current_price is None:
                    for holding in holdings_of_symbol:
                        if holding.get('manual_price'):
                            current_price = float(holding['manual_price'])
                            price_source = "🟡 Manual"
                            break
                
                # Oblicz P&L jeśli mamy cenę
                if current_price:
                    current_value = total_qty * current_price
                    pnl_usd = current_value - total_cost
                    pnl_pct = (pnl_usd / total_cost * 100) if total_cost > 0 else 0
                
                price_comparison.append({
                    'Symbol': symbol,
                    'Ilość': f"{total_qty:.6f}",
                    'Cena Zakupu': f"${avg_purchase_price:.4f}",
                    'Cena Aktualna': f"${current_price:.4f} {price_source}" if current_price else "❌ Brak (dodaj manual_price)",
                    'Zmiana 24h': f"{change_24h:+.2f}%" if change_24h is not None else "N/A",
                    'P&L': f"${pnl_usd:+.2f} ({pnl_pct:+.2f}%)" if pnl_usd is not None else "N/A",
                    '_pnl_raw': pnl_pct if pnl_pct is not None else 0  # do sortowania
                })
            
            # Sortuj po P&L (najlepsze na górze)
            price_comparison.sort(key=lambda x: x['_pnl_raw'], reverse=True)
            
            # Wyświetl jako tabelę z kolorami
            if price_comparison:
                st.markdown("""
                <style>
                .price-table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10px 0;
                }
                .price-table th { 
                    background: #1f1f1f; 
                    padding: 10px; 
                    text-align: left;
                    border-bottom: 2px solid #333;
                }
                .price-table td { 
                    padding: 8px; 
                    border-bottom: 1px solid #333;
                }
                .positive { color: #00ff00; }
                .negative { color: #ff4444; }
                </style>
                """, unsafe_allow_html=True)
                
                table_html = "<table class='price-table'><tr>"
                table_html += "<th>Symbol</th><th>Ilość</th><th>Cena Zakupu</th><th>Cena Aktualna</th><th>Zmiana 24h</th><th>P&L</th></tr>"
                
                for row in price_comparison:
                    pnl_class = "positive" if row['_pnl_raw'] > 0 else "negative" if row['_pnl_raw'] < 0 else ""
                    change_class = ""
                    if row['Zmiana 24h'] != "N/A":
                        change_val = float(row['Zmiana 24h'].replace('%',''))
                        change_class = "positive" if change_val > 0 else "negative" if change_val < 0 else ""
                    
                    table_html += f"<tr>"
                    table_html += f"<td><strong>{row['Symbol']}</strong></td>"
                    table_html += f"<td>{row['Ilość']}</td>"
                    table_html += f"<td>{row['Cena Zakupu']}</td>"
                    table_html += f"<td>{row['Cena Aktualna']}</td>"
                    table_html += f"<td class='{change_class}'>{row['Zmiana 24h']}</td>"
                    table_html += f"<td class='{pnl_class}'><strong>{row['P&L']}</strong></td>"
                    table_html += f"</tr>"
                
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)
                
                # Podsumowanie
                total_pnl = sum(float(r['P&L'].split('$')[1].split('(')[0]) for r in price_comparison if r['P&L'] != "N/A")
                st.caption(f"📊 **Total Portfolio P&L:** ${total_pnl:+.2f} USD")
                
                # Info o brakujących cenach
                missing_prices = [r['Symbol'] for r in price_comparison if "Brak" in r['Cena Aktualna']]
                if missing_prices:
                    with st.expander(f"ℹ️ Jak dodać ceny dla {', '.join(missing_prices)}?", expanded=False):
                        st.markdown("""
                        **System automatycznie próbuje pobrać ceny z wielu źródeł:**
                        - 🟢 **CoinGecko API** - główne źródło (Top 250 coinów)
                        - 🟠 **MEXC API** - dla MX Token (auto)
                        - 🔵 **Gate.io API** - dla GUSD i tokenów giełdowych (auto)
                        
                        **Jeśli token nadal nie ma ceny, możesz dodać ręcznie jako backup:**
                        
                        Edytuj `krypto.json` i dodaj pole `"manual_price"`:
                            ```json
                        {
                          "symbol": "RARE_TOKEN",
                          "manual_price": 1.23,
                          ...
                        }
                        ```
                        
                        💡 Manual price to fallback - system zawsze najpierw próbuje live API!
                        """)
            else:
                st.info("Brak danych do porównania cen")
            
            st.markdown("---")
            
            # Filtr
            platformy_unikalne = sorted(set(k['platforma'] for k in krypto))
            filtr_platforma = st.selectbox(
                "Filtruj po platformie:",
                ["Wszystkie"] + platformy_unikalne
            )
            
            # Filtrowanie
            if filtr_platforma == "Wszystkie":
                krypto_filtr = krypto
            else:
                krypto_filtr = [k for k in krypto if k['platforma'] == filtr_platforma]
            
            # Grupuj po symbolu
            symbole = {}
            for k in krypto_filtr:
                sym = k['symbol']
                if sym not in symbole:
                    symbole[sym] = []
                symbole[sym].append(k)
            
            # Wyświetl po symbolach
            for symbol, lista in sorted(symbole.items()):
                total_ilosc = sum(k['ilosc'] for k in lista)
                total_wartosc_zakupu = sum(k['ilosc'] * k['cena_zakupu_usd'] for k in lista)
                srednia_cena = total_wartosc_zakupu / total_ilosc if total_ilosc > 0 else 0
                
                # Pobierz metadata dla tego symbolu (Feature #7)
                coin_name = symbol
                coin_rank = ""
                change_24h = ""
                change_color = ""
                current_price_symbol = None
                total_wartosc_current = total_wartosc_zakupu
                pnl_symbol = 0
                
                if CRYPTO_MANAGER_OK and symbol in current_prices:
                    coin_data = current_prices[symbol]
                    coin_name = coin_data.get('name', symbol)
                    
                    if coin_data.get('market_cap_rank'):
                        coin_rank = f" #{coin_data['market_cap_rank']}"
                    
                    if coin_data.get('price_change_percentage_24h') is not None:
                        change_val = coin_data['price_change_percentage_24h']
                        change_24h = f" | 24h: {change_val:+.2f}%"
                        change_color = "🟢" if change_val > 0 else "🔴" if change_val < 0 else "⚪"
                    
                    if coin_data.get('current_price'):
                        current_price_symbol = coin_data['current_price']
                        total_wartosc_current = total_ilosc * current_price_symbol
                        pnl_symbol = total_wartosc_current - total_wartosc_zakupu
                
                # Tytuł expandera z enhanced info
                if current_price_symbol:
                    pnl_emoji = "📈" if pnl_symbol > 0 else "📉" if pnl_symbol < 0 else "➡️"
                    expander_title = f"**{symbol}** ({coin_name}){coin_rank}{change_color}{change_24h} {pnl_emoji} ${total_wartosc_current:.2f}"
                else:
                    expander_title = f"**{symbol}** ({coin_name}){coin_rank} - {total_ilosc:.8f} (${total_wartosc_zakupu:.2f})"
                
                with st.expander(expander_title, expanded=False):
                    # Header z cenami
                    col_h1, col_h2, col_h3 = st.columns(3)
                    
                    with col_h1:
                        st.caption(f"💰 Średnia cena zakupu: **${srednia_cena:.2f}**")
                    
                    with col_h2:
                        if current_price_symbol:
                            st.caption(f"📊 Aktualna cena: **${current_price_symbol:.2f}**")
                        else:
                            st.caption(f"📊 Aktualna cena: **N/A**")
                    
                    with col_h3:
                        if pnl_symbol != 0:
                            pnl_percent = (pnl_symbol / total_wartosc_zakupu * 100) if total_wartosc_zakupu > 0 else 0
                            pnl_color = "green" if pnl_symbol > 0 else "red"
                            st.caption(f"💵 P&L: :{pnl_color}[**{pnl_percent:+.2f}%** (${pnl_symbol:+.2f})]")
                        else:
                            st.caption(f"💵 P&L: **N/A**")
                    
                    st.markdown("---")
                    
                    for krypto_item in lista:
                        st.markdown("---")
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"🏦 **{krypto_item['platforma']}** - {krypto_item['status']}")
                            st.caption(f"Ilość: {krypto_item['ilosc']:.8f}")
                            st.caption(f"Cena zakupu: ${krypto_item['cena_zakupu_usd']:.2f}")
                            if krypto_item.get('apy', 0) > 0:
                                st.caption(f"📈 APY: {krypto_item['apy']:.2f}%")
                            if krypto_item.get('notatki'):
                                st.caption(f"📝 {krypto_item['notatki']}")
                        
                        with col2:
                            wartosc_pozycji = krypto_item['ilosc'] * krypto_item['cena_zakupu_usd']
                            st.metric("Wartość", f"${wartosc_pozycji:.2f}")
                        
                        with col3:
                            # Edycja/Usunięcie
                            with st.form(f"action_krypto_{krypto_item['id']}"):
                                col_edit, col_del = st.columns(2)
                                
                                with col_edit:
                                    if st.form_submit_button("✏️", width="stretch"):
                                        st.session_state[f'edit_krypto_{krypto_item["id"]}'] = True
                                        st.rerun()
                                
                                with col_del:
                                    if st.form_submit_button("🗑️", width="stretch"):
                                        if f'confirm_del_krypto_{krypto_item["id"]}' not in st.session_state:
                                            st.session_state[f'confirm_del_krypto_{krypto_item["id"]}'] = True
                                            st.warning("Kliknij ponownie")
                                        else:
                                            krypto.remove(krypto_item)
                                            if save_krypto(krypto):
                                                del st.session_state[f'confirm_del_krypto_{krypto_item["id"]}']
                                                st.success("✅ Usunięto!")
                                                st.rerun()
                        
                        # Formularz edycji
                        if st.session_state.get(f'edit_krypto_{krypto_item["id"]}', False):
                            with st.form(f"edit_form_krypto_{krypto_item['id']}"):
                                st.caption("Edytuj pozycję:")
                                
                                nowa_ilosc = st.number_input(
                                    "Ilość",
                                    min_value=0.0,
                                    value=float(krypto_item['ilosc']),
                                    step=0.01,
                                    format="%.8f",
                                    key=f"edit_ilosc_{krypto_item['id']}"
                                )
                                
                                nowa_cena = st.number_input(
                                    "Cena zakupu (USD)",
                                    min_value=0.0,
                                    value=float(krypto_item['cena_zakupu_usd']),
                                    step=0.01,
                                    format="%.2f",
                                    key=f"edit_cena_{krypto_item['id']}"
                                )
                                
                                col_save, col_cancel = st.columns(2)
                                
                                with col_save:
                                    if st.form_submit_button("💾 Zapisz", width="stretch"):
                                        krypto_item['ilosc'] = nowa_ilosc
                                        krypto_item['cena_zakupu_usd'] = nowa_cena
                                        if save_krypto(krypto):
                                            del st.session_state[f'edit_krypto_{krypto_item["id"]}']
                                            st.success("✅ Zaktualizowano!")
                                            st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button("❌ Anuluj", width="stretch"):
                                        del st.session_state[f'edit_krypto_{krypto_item["id"]}']
                                        st.rerun()
            
            # === WYKRES KRYPTO ===
            st.markdown("### 📊 Wizualizacja Portfela Krypto")
            
            # Wykres kołowy po symbolach
            symbole_dane = {}
            for k in krypto:
                sym = k['symbol']
                wartosc = k['ilosc'] * k['cena_zakupu_usd']
                symbole_dane[sym] = symbole_dane.get(sym, 0) + wartosc
            
            if symbole_dane:
                fig = go.Figure(data=[
                    go.Pie(
                        labels=list(symbole_dane.keys()),
                        values=list(symbole_dane.values()),
                        hole=.3,
                        textinfo='label+percent',
                        textposition='outside'
                    )
                ])
                
                fig.update_layout(
                    title="Podział Portfela Krypto po Symbolach (wartość zakupu)",
                    height=400
                )
                
                st.plotly_chart(fig, width="stretch")
    
    # ===== TAB 7: TRACK RECORD AI =====
    with tab7:
        st.header("🏆 Track Record AI Partnerów")
        
        if not MEMORY_OK:
            st.warning("⚠️ System pamięci AI niedostępny")
            st.info("Aby aktywować ten system, upewnij się że persona_memory_manager.py jest dostępny")
            return
        
        st.markdown("""
        System pamięci AI śledzi decyzje każdej persony, ich trafność i ewolucję charakteru.
        **Twoi partnerzy uczą się na błędach i sukcesach!**
        """)
        
        # Leaderboard
        st.markdown("### 🏆 Ranking Wiarygodności")
        
        leaderboard = pmm.get_leaderboard()
        
        if leaderboard:
            # Top 3 z medalami
            if len(leaderboard) > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if len(leaderboard) >= 1:
                        entry = leaderboard[0]
                        st.metric(
                            "🥇 Miejsce 1",
                            entry['persona'],
                            f"{entry['credibility']*100:.0f}% ({entry['correct']}/{entry['total']})"
                        )
                
                with col2:
                    if len(leaderboard) >= 2:
                        entry = leaderboard[1]
                        st.metric(
                            "🥈 Miejsce 2",
                            entry['persona'],
                            f"{entry['credibility']*100:.0f}% ({entry['correct']}/{entry['total']})"
                        )
                
                with col3:
                    if len(leaderboard) >= 3:
                        entry = leaderboard[2]
                        st.metric(
                            "🥉 Miejsce 3",
                            entry['persona'],
                            f"{entry['credibility']*100:.0f}% ({entry['correct']}/{entry['total']})"
                        )
            
            # Pełna tabela
            st.markdown("#### Pełny Ranking")
            
            df_leaderboard = pd.DataFrame(leaderboard)
            df_leaderboard['Ranking'] = range(1, len(df_leaderboard) + 1)
            df_leaderboard['Wiarygodność'] = df_leaderboard['credibility'].apply(lambda x: f"{x*100:.0f}%")
            df_leaderboard['Track Record'] = df_leaderboard.apply(
                lambda row: f"{row['correct']}/{row['total']}", axis=1
            )
            df_leaderboard['Wpływ (PLN)'] = df_leaderboard['impact'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                df_leaderboard[['Ranking', 'persona', 'Wiarygodność', 'Track Record', 'Wpływ (PLN)']].rename(
                    columns={'persona': 'Persona'}
                ),
                width="stretch",
                hide_index=True
            )
        else:
            st.info("📊 Brak danych - persony nie podjęły jeszcze rozliczonych decyzji")
        
        st.markdown("---")
        
        # Historia decyzji
        st.markdown("### 📜 Historia Decyzji")
        
        memory = pmm.load_memory()
        all_decisions = []
        
        for persona_name, data in memory.items():
            if persona_name == "meta":
                continue
            
            for dec in data.get("decision_history", []):
                all_decisions.append({
                    "Persona": persona_name,
                    "Data": dec.get("date", ""),
                    "Typ": dec.get("decision_type", ""),
                    "Ticker": dec.get("ticker", ""),
                    "Cena": dec.get("current_price", 0),
                    "Wynik": dec.get("result_pct"),
                    "Status": "✓" if dec.get("was_correct") else "✗" if dec.get("was_correct") is not None else "⏳",
                    "Uzasadnienie": dec.get("reasoning", "")[:80] + "..."
                })
        
        if all_decisions:
            df_decisions = pd.DataFrame(all_decisions)
            
            # Sortuj po dacie (newest first)
            df_decisions = df_decisions.sort_values("Data", ascending=False)
            
            # Filtrowanie
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                filter_persona = st.selectbox(
                    "Filtruj po personie",
                    ["Wszystkie"] + sorted(df_decisions["Persona"].unique().tolist())
                )
            
            with col_filter2:
                filter_status = st.selectbox(
                    "Filtruj po statusie",
                    ["Wszystkie", "✓ Trafne", "✗ Błędne", "⏳ Nierozliczone"]
                )
            
            # Aplikuj filtry
            df_filtered = df_decisions.copy()
            
            if filter_persona != "Wszystkie":
                df_filtered = df_filtered[df_filtered["Persona"] == filter_persona]
            
            if filter_status != "Wszystkie":
                status_map = {
                    "✓ Trafne": "✓",
                    "✗ Błędne": "✗",
                    "⏳ Nierozliczone": "⏳"
                }
                df_filtered = df_filtered[df_filtered["Status"] == status_map[filter_status]]
            
            st.dataframe(
                df_filtered,
                width="stretch",
                hide_index=True
            )
            
            # Statystyki
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                total_decisions = len(all_decisions)
                st.metric("📊 Wszystkie decyzje", total_decisions)
            
            with col_stat2:
                audited = len([d for d in all_decisions if d["Status"] in ["✓", "✗"]])
                st.metric("✅ Rozliczone", audited)
            
            with col_stat3:
                pending = len([d for d in all_decisions if d["Status"] == "⏳"])
                st.metric("⏳ Oczekujące", pending)
        else:
            st.info("📊 Brak decyzji w historii")
        
        st.markdown("---")
        
        # Ewolucja charakteru
        st.markdown("### 🧬 Ewolucja Charakteru Person")
        
        st.markdown("""
        Cechy charakteru person zmieniają się na podstawie ich sukcesów i porażek.
        """)
        
        # Wybierz personę do analizy
        persona_to_analyze = st.selectbox(
            "Wybierz personę",
            [p for p in memory.keys() if p != "meta"]
        )
        
        if persona_to_analyze and persona_to_analyze in memory:
            persona_data = memory[persona_to_analyze]
            traits = persona_data.get("personality_traits", {})
            
            if traits:
                # Wykres radarowy cech
                categories = [t.replace('_', ' ').title() for t in traits.keys()]
                values = list(traits.values())
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=persona_to_analyze
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )),
                    showlegend=False,
                    title=f"Profil Psychologiczny: {persona_to_analyze}",
                    height=500
                )
                
                st.plotly_chart(fig, width="stretch")
                
                # Tabela cech
                st.markdown("#### Szczegóły Cech")
                
                trait_descriptions = {
                    "risk_tolerance": "Tolerancja ryzyka - skłonność do ryzykownych inwestycji",
                    "optimism_bias": "Optymizm - tendencja do pozytywnych prognoz",
                    "analytical_depth": "Głębokość analityczna - szczegółowość analiz",
                    "patience": "Cierpliwość - preferencja dla długoterminowych strategii",
                    "innovation_focus": "Innowacyjność - zainteresowanie nowymi technologiami"
                }
                
                for trait, value in traits.items():
                    trait_name = trait.replace('_', ' ').title()
                    description = trait_descriptions.get(trait, "")
                    
                    # Normalize value to 0-1 range (handle negative values)
                    normalized_value = max(0.0, min(1.0, (value + 1) / 2 if value < 0 else value))
                    progress_bar = "█" * int(normalized_value * 20) + "░" * (20 - int(normalized_value * 20))
                    
                    st.write(f"**{trait_name}** ({value:.2f})")
                    st.progress(normalized_value)
                    if description:
                        st.caption(description)
                    st.markdown("")
            
            # Kluczowe lekcje
            lessons = persona_data.get("key_lessons", [])
            if lessons:
                st.markdown("#### 📚 Kluczowe Lekcje")
                
                for lesson in lessons[-5:]:
                    if isinstance(lesson, dict):
                        st.info(f"**[{lesson.get('date')}]** {lesson.get('lesson')}")
                    else:
                        st.info(lesson)
        
        # === NOWE FEATURY V2.0 ===
        if MEMORY_V2:
            st.markdown("---")
            st.markdown("### 🎭 System Osobowości v2.0")
            st.success("✅ Zaawansowane featury aktywne!")
            
            # Emocje
            emotions = persona_data.get('emotional_state', {})
            if emotions:
                st.markdown("#### 🎭 Stan Emocjonalny")
                
                mood = emotions.get('current_mood', 'neutral')
                mood_emojis = {
                    'excited': '🔥', 'confident': '💪', 'optimistic': '😊',
                    'neutral': '😐', 'cautious': '🤔', 'worried': '😟',
                    'fearful': '😰', 'angry': '😠', 'disappointed': '😞'
                }
                
                col_mood1, col_mood2, col_mood3 = st.columns(3)
                
                with col_mood1:
                    st.metric("Nastrój", f"{mood_emojis.get(mood, '😐')} {mood.upper()}")
                
                with col_mood2:
                    st.metric("Stres", f"{emotions.get('stress_level', 0.3):.0%}")
                
                with col_mood3:
                    st.metric("Strach", f"{emotions.get('fear_index', 0.2):.0%}")
                
                # Mood history
                mood_hist = emotions.get('mood_history', [])
                if mood_hist:
                    st.markdown("**Ostatnie zmiany nastroju:**")
                    for change in mood_hist[-3:]:
                        st.caption(f"{change.get('date')}: {change.get('from')} → {change.get('to')}")
            
            # Relacje
            relationships = persona_data.get('relationships', {})
            if relationships:
                st.markdown("#### 🤝 Relacje z Partnerami")
                
                # Sortuj po trust
                sorted_rels = sorted(relationships.items(), key=lambda x: x[1].get('trust', 0), reverse=True)
                
                for partner, rel in sorted_rels[:5]:
                    trust = rel.get('trust', 0.5)
                    agree = rel.get('agreement_rate', 0.5)
                    
                    trust_emoji = '🟢' if trust > 0.7 else '🟡' if trust > 0.4 else '🔴'
                    
                    col_r1, col_r2, col_r3 = st.columns([2, 1, 1])
                    
                    with col_r1:
                        st.write(f"{trust_emoji} **{partner}**")
                    
                    with col_r2:
                        st.progress(trust, text=f"Zaufanie: {trust:.0%}")
                    
                    with col_r3:
                        st.progress(agree, text=f"Zgoda: {agree:.0%}")
            
            # Voting weight
            voting = persona_data.get('voting_weight_modifier', {})
            if voting:
                st.markdown("#### 🗳️ Siła Głosu w Radzie")
                
                col_v1, col_v2, col_v3 = st.columns(3)
                
                with col_v1:
                    st.metric("Waga Bazowa", f"{voting.get('base_weight', 5):.1f}%")
                
                with col_v2:
                    bonus = voting.get('credibility_bonus', 0)
                    st.metric("Bonus za Wiarygodność", f"{bonus:+.1f}%")
                
                with col_v3:
                    effective = voting.get('effective_weight', 5)
                    st.metric("Efektywna Waga", f"{effective:.1f}%", delta=f"{bonus:+.1f}%")
            
            # Ekspertyza
            expertise = persona_data.get('expertise_areas', {})
            if expertise:
                st.markdown("#### 🎯 Obszary Ekspertyzy")
                
                sectors = expertise.get('sectors', {})
                if sectors:
                    st.markdown("**Sektory:**")
                    top_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:5]
                    
                    for sector, level in top_sectors:
                        st.progress(level, text=f"{sector}: {level:.0%}")
                
                geographies = expertise.get('geographies', {})
                if geographies:
                    st.markdown("**Geografia:**")
                    for geo, level in sorted(geographies.items(), key=lambda x: x[1], reverse=True)[:3]:
                        st.progress(level, text=f"{geo}: {level:.0%}")
            
            # Personal agenda
            agenda = persona_data.get('personal_agenda', {})
            if agenda:
                st.markdown("#### 🎯 Osobista Agenda")
                
                goal = agenda.get('primary_goal', '')
                progress = agenda.get('progress', 0)
                
                if goal:
                    st.info(f"**Cel:** {goal}")
                    st.progress(progress, text=f"Postęp: {progress:.0%}")
                
                tactics = agenda.get('tactics', [])
                if tactics:
                    st.markdown("**Taktyki:**")
                    for tactic in tactics:
                        st.write(f"• {tactic}")
            
            # Communication style
            comm = persona_data.get('communication_style', {})
            if comm:
                st.markdown("#### 💬 Styl Komunikacji")
                
                catchphrases = comm.get('catchphrases', [])
                if catchphrases:
                    st.markdown("**Ulubione zwroty:**")
                    for phrase in catchphrases[:3]:
                        st.write(f"💬 \"{phrase}\"")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                
                with col_c1:
                    verbosity = comm.get('verbosity', 0.5)
                    st.metric("Szczegółowość", f"{verbosity:.0%}")
                
                with col_c2:
                    humor = comm.get('humor', 0.3)
                    st.metric("Humor", f"{humor:.0%}")
                
                with col_c3:
                    formality = comm.get('formality', 0.5)
                    st.metric("Formalność", f"{formality:.0%}")

def show_markets_page(stan_spolki, cele):
    """Strona analizy rynków geograficznych"""
    st.title("🌍 Analiza Rynków Globalnych")
    
    st.markdown("""
    Analiza światowych indeksów, Twojego portfela i ekspozycji geograficznej.
    """)
    
    # === TABS - dodaj nowy tab dla indeksów ===
    tab_indices, tab_portfolio, tab_correlations, tab_insights, tab_recommendations = st.tabs([
        "📊 Światowe Indeksy", "🗺️ Twój Portfel", "🔗 Korelacje", "💡 Insights", "🎯 Rekomendacje"
    ])
    
    # === TAB 1: ŚWIATOWE INDEKSY ===
    with tab_indices:
        st.markdown("### 📊 Główne Indeksy Giełdowe")
        
        # Definicje indeksów
        indices = {
            "🇺🇸 S&P 500": "^GSPC",
            "🇺🇸 Nasdaq": "^IXIC",
            "🇺🇸 Dow Jones": "^DJI",
            "🇪🇺 Euro Stoxx 50": "^STOXX50E",
            "🇬🇧 FTSE 100": "^FTSE",
            "🇩🇪 DAX": "^GDAXI",
            "🇯🇵 Nikkei 225": "^N225",
            "🇨🇳 Shanghai Composite": "000001.SS",
            "🪙 Bitcoin": "BTC-USD",
            "🪙 Ethereum": "ETH-USD"
        }
        
        # Pobierz dane
        st.caption("📈 Dane z ostatnich 30 dni")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Multi-line chart z wszystkimi indeksami (znormalizowane do 100)
            st.markdown("**📈 Porównanie Wydajności (znormalizowane do 100)**")
            
            with st.spinner("Pobieranie danych indeksów..."):
                fig = go.Figure()
                
                for name, ticker in indices.items():
                    try:
                        import yfinance as yf
                        data = yf.download(ticker, period="1mo", progress=False, auto_adjust=True)
                        
                        if not data.empty and 'Close' in data.columns:
                            # Normalizuj do 100
                            normalized = (data['Close'] / data['Close'].iloc[0]) * 100
                            
                            fig.add_trace(go.Scatter(
                                x=normalized.index,
                                y=normalized.values,
                                mode='lines',
                                name=name,
                                hovertemplate=f'<b>{name}</b><br>Data: %{{x}}<br>Wartość: %{{y:.2f}}<extra></extra>'
                            ))
                    except Exception as e:
                        st.caption(f"⚠️ Nie udało się pobrać {name}: {str(e)[:50]}")
                
                fig.update_layout(
                    title="Wydajność Indeksów (ostatnie 30 dni)",
                    xaxis_title="Data",
                    yaxis_title="Wartość znormalizowana (start = 100)",
                    height=500,
                    hovermode='x unified',
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02
                    )
                )
                
                st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.markdown("**📊 Zmiana 1M:**")
            
            # Tabela zmian
            changes_data = []
            
            for name, ticker in indices.items():
                try:
                    import yfinance as yf
                    data = yf.download(ticker, period="1mo", progress=False, auto_adjust=True)
                    
                    if not data.empty and 'Close' in data.columns:
                        start_price = data['Close'].iloc[0]
                        end_price = data['Close'].iloc[-1]
                        change_pct = ((end_price - start_price) / start_price) * 100
                        
                        emoji = "📈" if change_pct > 0 else "📉"
                        color = "🟢" if change_pct > 0 else "🔴"
                        
                        changes_data.append({
                            "Indeks": name,
                            "": f"{color} {emoji}",
                            "Zmiana": f"{change_pct:+.2f}%"
                        })
                except Exception as e:
                    # Błąd przy pobieraniu danych indeksu - pomiń
                    continue
            
            if changes_data:
                # Sortuj po zmianie
                changes_df = pd.DataFrame(changes_data)
                changes_df = changes_df.sort_values("Zmiana", ascending=False, key=lambda x: x.str.rstrip('%').astype(float))
                
                st.dataframe(
                    changes_df,
                    hide_index=True,
                    width="stretch",
                    height=500
                )
        
        st.markdown("---")
        st.caption("💡 Dane pobierane z Yahoo Finance w czasie rzeczywistym")
    
    # === TAB 2: TWÓJ PORTFEL (stary content) ===
    with tab_portfolio:
        st.markdown("### 🗺️ Geograficzna Alokacja Twojego Portfela")
        
        # Analiza składu rynków
        market_analysis = analyze_market_composition(stan_spolki)
        correlations = calculate_market_correlations(stan_spolki)
        insights = generate_market_insights(market_analysis, correlations)
        
        # === METRICS ===
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💼 Wartość Portfela",
                f"{market_analysis['total_value']:,.0f} PLN"
            )
        
        with col2:
            st.metric(
                "🌍 Dywersyfikacja Geo",
                f"{market_analysis['diversification_score']:.0f}/100",
                delta="Dobra" if market_analysis['diversification_score'] > 60 else "Niska"
            )
        
        with col3:
            markets_count = sum(1 for m in market_analysis['markets'].values() if m['count'] > 0)
            st.metric(
                "🗺️ Aktywne Rynki",
                markets_count
            )
        
        st.markdown("---")
        
        # Alokacja geograficzna
        st.markdown("### 📊 Alokacja Geograficzna")
        
        col_chart1, col_chart2 = st.columns([2, 1])
        
        with col_chart1:
            # Pie chart alokacji
            markets = market_analysis['markets']
            active_markets = {name: data for name, data in markets.items() if data['percentage'] > 0}
            
            if active_markets:
                fig = go.Figure(data=[go.Pie(
                    labels=list(active_markets.keys()),
                    values=[m['value_pln'] for m in active_markets.values()],
                    hole=0.4,
                    marker=dict(
                        colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
                    ),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Wartość: %{value:,.0f} PLN<br>Udział: %{percent}<extra></extra>'
                )])
                
                fig.update_layout(
                    title="Podział Portfela według Rynków",
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Brak danych do wyświetlenia")
        
        with col_chart2:
            st.markdown("**📈 Szczegóły po rynkach:**")
            
            for market_name, market_data in sorted(
                markets.items(), 
                key=lambda x: x[1]['percentage'], 
                reverse=True
            ):
                if market_data['percentage'] > 0:
                    st.markdown(f"**{market_name}**")
                    st.progress(market_data['percentage'] / 100)
                    st.caption(f"{market_data['percentage']:.1f}% | {market_data['count']} pozycji | {market_data['value_pln']:,.0f} PLN")
                    st.markdown("---")
        
        # Tabela szczegółów
        st.markdown("### 📋 Lista Tickerów według Rynków")
        
        for market_name, market_data in sorted(markets.items(), key=lambda x: x[1]['percentage'], reverse=True):
            if market_data['tickers']:
                with st.expander(f"{market_name} - {len(market_data['tickers'])} tickerów"):
                    st.write(", ".join(market_data['tickers']))
    
    # === TAB 3: KORELACJE ===
    with tab_correlations:
        st.markdown("### 🔗 Korelacje między Rynkami")
        
        st.info("""
        **Interpretacja korelacji:**
        - **+0.7 do +1.0**: Silna pozytywna korelacja (rynki poruszają się razem)
        - **+0.3 do +0.7**: Umiarkowana korelacja
        - **-0.3 to +0.3**: Słaba/brak korelacji (dobre dla dywersyfikacji!)
        - **-0.7 to -0.3**: Umiarkowana negatywna korelacja
        - **-1.0 to -0.7**: Silna negatywna korelacja (rynki poruszają się w przeciwnych kierunkach)
        """)
        
        market_changes = correlations.get('market_changes', {})
        
        if market_changes:
            # Performance table
            st.markdown("**📊 Aktualna Wydajność Rynków:**")
            
            perf_data = []
            for market, change in sorted(market_changes.items(), key=lambda x: x[1], reverse=True):
                emoji = "📈" if change > 0 else "📉"
                color = "🟢" if change > 2 else "🔴" if change < -2 else "🟡"
                
                perf_data.append({
                    "Rynek": market,
                    "Status": f"{color} {emoji}",
                    "Zmiana %": f"{change:.2f}%",
                    "Trend": "Wzrost" if change > 0 else "Spadek"
                })
            
            st.dataframe(
                pd.DataFrame(perf_data),
                width="stretch",
                hide_index=True
            )
            
            st.markdown("---")
            
            # Heatmapa korelacji (uproszczona)
            st.markdown("**🔥 Macierz Korelacji (uproszczona):**")
            
            corr_data = correlations.get('correlations', {})
            
            if corr_data:
                markets_list = list(market_changes.keys())
                
                # Stwórz macierz
                corr_matrix = []
                for m1 in markets_list:
                    row = []
                    for m2 in markets_list:
                        key = f"{m1}-{m2}"
                        corr = corr_data.get(key, 0)
                        row.append(corr)
                    corr_matrix.append(row)
                
                # Heatmapa
                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix,
                    x=markets_list,
                    y=markets_list,
                    colorscale='RdYlGn_r',
                    zmid=0,
                    text=[[f"{val:.2f}" for val in row] for row in corr_matrix],
                    texttemplate='%{text}',
                    textfont={"size": 12},
                    hovertemplate='%{y} vs %{x}<br>Korelacja: %{z:.2f}<extra></extra>'
                ))
                
                fig.update_layout(
                    title="Korelacje między Rynkami",
                    xaxis_title="Rynek",
                    yaxis_title="Rynek",
                    height=500
                )
                
                st.plotly_chart(fig, width="stretch")
        else:
            st.warning("Brak danych o zmianach cen - nie można obliczyć korelacji")
    
    # === TAB 4: INSIGHTS ===
    with tab_insights:
        st.markdown("### 💡 Insights & Analiza")
        
        if insights:
            for insight in insights:
                if insight['type'] == 'success':
                    st.success(f"{insight['icon']} **{insight['title']}**\n\n{insight['description']}")
                elif insight['type'] == 'warning':
                    st.warning(f"{insight['icon']} **{insight['title']}**\n\n{insight['description']}")
                else:
                    st.info(f"{insight['icon']} **{insight['title']}**\n\n{insight['description']}")
        else:
            st.info("Brak insights do wyświetlenia")
    
    # === TAB 5: REKOMENDACJE ===
    with tab_recommendations:
        st.markdown("### 🎯 Rekomendacje Rebalancingu")
        
        markets = market_analysis['markets']
        
        st.markdown("""
        **Idealna alokacja geograficzna (benchmark):**
        - 🇺🇸 **US**: 50-60% (największy, najbardziej płynny rynek)
        - 🇪🇺 **EU**: 15-25% (stabilny, dywidendy)
        - 🇨🇦 **Canada**: 5-10% (surowce, banki)
        - 🌏 **Emerging**: 5-15% (wyższy potencjał wzrostu, wyższe ryzyko)
        - 💎 **Crypto**: 2-10% (opcjonalne, wysokie ryzyko)
        """)
        
        st.markdown("---")
        
        st.markdown("**📊 Twoja Alokacja vs Benchmark:**")
        
        # Porównaj z benchmarkiem
        benchmark = {
            "US": {"min": 50, "max": 60, "ideal": 55},
            "EU": {"min": 15, "max": 25, "ideal": 20},
            "Canada": {"min": 5, "max": 10, "ideal": 7.5},
            "Emerging": {"min": 5, "max": 15, "ideal": 10},
            "Crypto": {"min": 2, "max": 10, "ideal": 5}
        }
        
        recommendations = []
        
        for market_name, bench in benchmark.items():
            current = markets.get(market_name, {}).get('percentage', 0)
            ideal = bench['ideal']
            min_val = bench['min']
            max_val = bench['max']
            
            status = ""
            action = ""
            
            if current < min_val:
                status = "🔴 Niedowaga"
                action = f"Zwiększ ekspozycję o {min_val - current:.1f}%"
            elif current > max_val:
                status = "🔴 Nadwaga"
                action = f"Zmniejsz ekspozycję o {current - max_val:.1f}%"
            elif current < ideal - 5:
                status = "🟡 Lekka niedowaga"
                action = f"Rozważ zwiększenie o {ideal - current:.1f}%"
            elif current > ideal + 5:
                status = "🟡 Lekka nadwaga"
                action = f"Rozważ zmniejszenie o {current - ideal:.1f}%"
            else:
                status = "🟢 OK"
                action = "Alokacja w normie"
            
            recommendations.append({
                "Rynek": market_name,
                "Aktualna": f"{current:.1f}%",
                "Benchmark": f"{ideal:.1f}%",
                "Status": status,
                "Rekomendacja": action
            })
        
        df_recommendations = pd.DataFrame(recommendations)
        st.dataframe(df_recommendations, width="stretch", hide_index=True)
        
        st.markdown("---")
        
        st.markdown("**💡 Konkretne Akcje:**")
        
        # Generuj konkretne sugestie
        us_pct = markets.get("US", {}).get('percentage', 0)
        eu_pct = markets.get("EU", {}).get('percentage', 0)
        crypto_pct = markets.get("Crypto", {}).get('percentage', 0)
        emerging_pct = markets.get("Emerging", {}).get('percentage', 0)
        
        if us_pct < 50:
            st.info("📌 **Zwiększ US**: Kup ETF S&P 500 (np. VOO, SPY) lub pojedyncze blue chips (AAPL, MSFT, GOOGL)")
        
        if eu_pct > 30:
            st.warning("📌 **Zmniejsz EU**: Rozważ sprzedaż części VWCE.DE lub europejskich akcji")
        
        if crypto_pct > 10:
            st.warning("📌 **Zmniejsz Crypto**: Sprzedaj część BTC/ETH, reinwestuj w tradycyjne aktywa")
        elif crypto_pct < 2 and market_analysis['total_value'] > 20000:
            st.info("📌 **Dodaj Crypto**: Rozważ małą pozycję w BTC lub ETH (2-5% portfela)")
        
        if emerging_pct < 5:
            st.info("📌 **Dodaj Emerging Markets**: Rozważ ETF (VWO) lub pojedyncze akcje (TSM, BABA, VALE)")

def show_snapshots_page():
    """Strona Daily Snapshots - historia codziennych zapisów portfela"""
    st.title("📸 Daily Snapshots")
    st.markdown("*Automatyczny system codziennych zapisów stanu portfela*")
    
    # Import modułu
    try:
        import daily_snapshot as ds
    except ImportError:
        st.error("❌ Moduł daily_snapshot.py nie znaleziony")
        st.info("Upewnij się że plik daily_snapshot.py znajduje się w tym samym folderze co streamlit_app.py")
        return
    
    # Pokaż statystyki
    stats = ds.get_snapshot_stats()
    
    if stats['count'] == 0:
        st.warning("⚠️ Brak zapisanych snapshots")
        
        # Sprawdź czy istnieje monthly_snapshot.json do migracji
        if os.path.exists('monthly_snapshot.json'):
            st.info("""
            **🔄 Wykryto historyczne dane!**
            
            Znaleziono `monthly_snapshot.json` z historycznymi danymi portfela.
            Możesz zmigrować te dane do nowego systemu daily snapshots.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Migruj dane historyczne", type="primary"):
                    with st.spinner("Migruję monthly_snapshot.json..."):
                        count = ds.migrate_monthly_to_daily_snapshots()
                        if count > 0:
                            st.success(f"✅ Zmigrowano {count} snapshot!")
                            st.rerun()
                        else:
                            st.info("ℹ️ Dane już zmigrowane lub brak nowych danych")
            
            with col2:
                if st.button("📸 Utwórz nowy snapshot"):
                    with st.spinner("Tworzę snapshot..."):
                        success = ds.save_daily_snapshot()
                        if success:
                            st.success("✅ Snapshot zapisany!")
                            st.rerun()
                        else:
                            st.error("❌ Błąd przy tworzeniu snapshotu")
        else:
            st.info("""
            **Jak zacząć?**
            1. Uruchom ręcznie: `python daily_snapshot.py`
            2. Lub kliknij przycisk poniżej
            3. Skonfiguruj automatyczne uruchamianie (Windows Task Scheduler o 21:00)
            """)
            
            if st.button("📸 Utwórz pierwszy snapshot teraz"):
                with st.spinner("Tworzę snapshot..."):
                    success = ds.save_daily_snapshot()
                    if success:
                        st.success("✅ Snapshot zapisany!")
                        st.rerun()
                    else:
                        st.error("❌ Błąd przy tworzeniu snapshotu")
        return
    
    # Metryki główne
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Liczba Snapshots", stats['count'])
    
    with col2:
        st.metric("📅 Dni Śledzenia", stats['days_tracked'])
    
    with col3:
        delta = f"{stats['net_worth_change_pct']:+.1f}%"
        st.metric(
            "💎 Net Worth", 
            f"{stats['last_net_worth']:,.0f} PLN",
            delta=delta
        )
    
    with col4:
        st.metric("⚡ Snapshots/tydzień", f"{stats['avg_snapshots_per_week']:.1f}")
    
    st.markdown("---")
    
    # Wczytaj pełną historię
    history = ds.load_snapshot_history()
    
    # Zakładki
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Wykresy", 
        "📊 Historia Tabela", 
        "🎯 Szczegóły Ostatniego",
        "⚙️ Zarządzanie"
    ])
    
    with tab1:
        st.subheader("📈 Net Worth Over Time")
        
        # Przygotuj dane do wykresu
        dates = [s['date'][:10] for s in history]
        net_worths = [s['totals']['net_worth_pln'] for s in history]
        stocks_pln = [s['stocks']['value_pln'] if s.get('stocks') else 0 for s in history]
        crypto_pln = [s['crypto']['value_pln'] if s.get('crypto') else 0 for s in history]
        debt_pln = [s['debt']['total_pln'] if s.get('debt') else 0 for s in history]
        
        # Wykres główny - Net Worth
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=dates,
            y=net_worths,
            mode='lines+markers',
            name='Net Worth',
            line=dict(color='#00D9FF', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(0, 217, 255, 0.1)'
        ))
        
        fig1.update_layout(
            title='💎 Net Worth (Wartość Netto)',
            xaxis_title='Data',
            yaxis_title='PLN',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig1, width="stretch", key="snapshot_networth_chart")
        
        # Wykres składowych
        st.subheader("📊 Składowe Portfela")
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=dates,
            y=stocks_pln,
            mode='lines',
            name='Akcje',
            line=dict(color='#4CAF50', width=2),
            stackgroup='one'
        ))
        
        fig2.add_trace(go.Scatter(
            x=dates,
            y=crypto_pln,
            mode='lines',
            name='Crypto',
            line=dict(color='#FF9800', width=2),
            stackgroup='one'
        ))
        
        fig2.add_trace(go.Scatter(
            x=dates,
            y=debt_pln,
            mode='lines',
            name='Zobowiązania',
            line=dict(color='#F44336', width=2, dash='dash')
        ))
        
        fig2.update_layout(
            title='Składowe Aktywów i Pasywów',
            xaxis_title='Data',
            yaxis_title='PLN',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig2, width="stretch", key="snapshot_components_chart")
        
        # Wykres % change
        st.subheader("📊 Zmiana Procentowa (od początku)")
        
        if net_worths:
            base_value = net_worths[0]
            pct_changes = [((nw - base_value) / base_value * 100) if base_value > 0 else 0 
                          for nw in net_worths]
            
            fig3 = go.Figure()
            
            fig3.add_trace(go.Scatter(
                x=dates,
                y=pct_changes,
                mode='lines+markers',
                name='% Change',
                line=dict(color='#9C27B0', width=2),
                marker=dict(size=4),
                fill='tozeroy'
            ))
            
            fig3.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            fig3.update_layout(
                title=f'Zmiana Net Worth od {stats["first_date"]}',
                xaxis_title='Data',
                yaxis_title='%',
                hovermode='x unified',
                height=300
            )
            
            st.plotly_chart(fig3, width="stretch", key="snapshot_percent_change_chart")
    
    with tab2:
        st.subheader("📊 Historia Wszystkich Snapshots")
        
        # Przygotuj tabelę
        table_data = []
        for i, s in enumerate(reversed(history)):  # Najnowsze na górze
            table_data.append({
                '#': len(history) - i,
                'Data': s['date'][:10],
                'Godzina': s['date'][11:16],
                'Akcje (PLN)': f"{s['stocks']['value_pln']:,.0f}" if s.get('stocks') else '-',
                'Crypto (PLN)': f"{s['crypto']['value_pln']:,.0f}" if s.get('crypto') else '-',
                'Zobowiązania': f"{s['debt']['total_pln']:,.0f}" if s.get('debt') else '-',
                'Net Worth': f"{s['totals']['net_worth_pln']:,.0f}",
                'USD/PLN': f"{s['usd_pln_rate']:.4f}"
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, width="stretch", height=400)
        
        # Opcja exportu
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Pobierz jako CSV",
            data=csv,
            file_name=f"snapshots_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )
    
    with tab3:
        st.subheader("🎯 Szczegóły Ostatniego Snapshotu")
        
        last = history[-1]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📅 Informacje Podstawowe**")
            st.write(f"Data: `{last['date']}`")
            st.write(f"Kurs USD/PLN: `{last['usd_pln_rate']:.4f}`")
        
        with col2:
            st.markdown("**💰 Podsumowanie**")
            st.write(f"Aktywa: `{last['totals']['assets_pln']:,.2f} PLN`")
            st.write(f"Zobowiązania: `{last['totals']['debt_pln']:,.2f} PLN`")
            st.write(f"**Net Worth: `{last['totals']['net_worth_pln']:,.2f} PLN`**")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if last.get('stocks'):
                st.markdown("**📈 Akcje**")
                st.write(f"Wartość: `${last['stocks']['value_usd']:,.2f}` = `{last['stocks']['value_pln']:,.2f} PLN`")
                st.write(f"Pozycje: `{last['stocks']['positions']}`")
                st.write(f"Cash: `${last['stocks']['cash_usd']:,.2f}`")
        
        with col2:
            if last.get('crypto'):
                st.markdown("**₿ Kryptowaluty**")
                st.write(f"Wartość: `${last['crypto']['value_usd']:,.2f}` = `{last['crypto']['value_pln']:,.2f} PLN`")
                st.write(f"Pozycje: `{last['crypto']['positions']}`")
        
        if last.get('debt'):
            st.markdown("**💳 Zobowiązania**")
            st.write(f"Suma: `{last['debt']['total_pln']:,.2f} PLN`")
            st.write(f"Liczba kredytów: `{last['debt']['loans_count']}`")
        
        # Pokaż raw JSON
        with st.expander("🔍 Zobacz Raw JSON"):
            st.json(last)
    
    with tab4:
        st.subheader("⚙️ Zarządzanie Snapshots")
        
        st.markdown("**📸 Tworzenie Snapshot**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📸 Utwórz snapshot TERAZ"):
                with st.spinner("Tworzę snapshot..."):
                    success = ds.save_daily_snapshot()
                    if success:
                        st.success("✅ Snapshot zapisany!")
                        st.rerun()
                    else:
                        st.error("❌ Błąd")
        
        with col2:
            should_create = ds.should_create_snapshot(target_hour=21)
            if should_create:
                st.info("✅ Pora na dzienny snapshot (po 21:00)")
            else:
                today = datetime.now().strftime('%Y-%m-%d')
                today_snapshots = [s for s in history if s['date'][:10] == today]
                if today_snapshots:
                    st.success(f"✅ Snapshot z dzisiaj już istnieje ({today_snapshots[0]['date'][11:16]})")
                else:
                    st.warning("⏳ Za wcześnie (snapshot tworzone po 21:00)")
        
        st.markdown("---")
        
        st.markdown("**⚙️ Konfiguracja Automatycznego Uruchamiania**")
        
        st.info("""
        **Windows Task Scheduler:**
        1. Otwórz Task Scheduler (`taskschd.msc`)
        2. Create Basic Task → Nazwa: "Portfolio Daily Snapshot"
        3. Trigger: Daily o 21:00
        4. Action: Start a program
        5. Program: `run_daily_snapshot.bat`
        6. Start in: `C:\\Users\\alech\\Desktop\\Horyzont Partnerów`
        
        **Plik .bat został utworzony:** `run_daily_snapshot.bat`
        """)
        
        st.markdown("---")
        
        st.markdown("**🗑️ Zarządzanie Danymi**")
        
        st.write(f"📁 Plik: `daily_snapshots.json`")
        st.write(f"📊 Rozmiar historii: {stats['count']} snapshots")
        st.write(f"⏱️  Automatyczna rotacja: ostatnie {ds.MAX_HISTORY_DAYS} dni")
        
        # Opcja usunięcia wszystkich snapshots (niebezpieczne!)
        with st.expander("⚠️ Niebezpieczna Strefa"):
            st.warning("**Uwaga!** Poniższe akcje są nieodwracalne!")
            
            if st.button("🗑️ USUŃ WSZYSTKIE SNAPSHOTS", type="secondary"):
                if st.session_state.get('confirm_delete_snapshots'):
                    try:
                        os.remove('daily_snapshots.json')
                        st.success("✅ Usunięto wszystkie snapshots")
                        st.session_state.confirm_delete_snapshots = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Błąd: {e}")
                else:
                    st.session_state.confirm_delete_snapshots = True
                    st.warning("⚠️ Kliknij ponownie aby potwierdzić usunięcie")

def show_settings_page():
    """Strona ustawień"""
    st.title("⚙️ Ustawienia")
    
    # === NOWA SEKCJA: AI PARTNERZY ===
    st.subheader("🤖 Partnerzy AI")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tryb_ai = st.selectbox(
            "Tryb odpowiedzi partnerów",
            ["Zwięzły", "Normalny", "Szczegółowy"],
            index=1,  # Normalny jako domyślny
            key="ai_mode_select",
            help="Zwięzły: 2-4 zdania | Normalny: 4-6 zdań | Szczegółowy: 8-12 zdań"
        )
        
        # Mapuj wybór na wartość używaną w kodzie
        mode_map = {
            "Zwięzły": "zwiezly",
            "Normalny": "normalny",
            "Szczegółowy": "szczegolowy"
        }
        
        if 'ai_response_mode' not in st.session_state:
            st.session_state.ai_response_mode = "normalny"
        
        st.session_state.ai_response_mode = mode_map[tryb_ai]
        
        st.caption(f"Wybrano: **{tryb_ai}**")
    
    with col2:
        st.info("""
        **Opis trybów:**
        
        🎯 **Zwięzły**: Krótkie, konkretne odpowiedzi (2-4 zdania)
        
        📊 **Normalny**: Zbalansowane odpowiedzi z danymi (4-6 zdań)
        
        📚 **Szczegółowy**: Pełna analiza z uzasadnieniami (8-12 zdań)
        """)
    
    # Statystyki historii rozmów (Session)
    if 'partner_history' in st.session_state and st.session_state.partner_history:
        st.markdown("---")
        st.markdown("**📝 Historia rozmów (Sesja bieżąca):**")
        
        total_messages = sum(len(history) for history in st.session_state.partner_history.values())
        st.metric("Wiadomości w tej sesji", total_messages)
        
        if st.button("🗑️ Wyczyść historię sesji", width="stretch", key="clear_session"):
            st.session_state.partner_history = {}
            st.success("✅ Historia sesji wyczyszczona!")
            st.rerun()
    
    # Statystyki pamięci długoterminowej
    st.markdown("---")
    st.markdown("**🧠 Pamięć Długoterminowa (Permanentna):**")
    
    if IMPORTS_OK and PERSONAS:
        col_mem1, col_mem2 = st.columns(2)
        
        total_permanent_messages = 0
        partners_with_memory = 0
        
        with col_mem1:
            for name in PERSONAS.keys():
                if 'Partner Zarządzający' in name and '(JA)' in name:
                    continue
                    
                stats = get_memory_statistics(name)
                if stats:
                    partners_with_memory += 1
                    total_permanent_messages += stats.get('total_messages', 0)
            
            st.metric("Partnerzy z pamięcią", partners_with_memory)
            st.metric("Całkowita liczba rozmów", total_permanent_messages)
        
        with col_mem2:
            st.info("💡 Pamięć długoterminowa:\n- Zapisana na dysku\n- Przetrwa restart\n- Partner pamięta historię")
            
            if st.button("🗑️ Wyczyść CAŁĄ pamięć", width="stretch", key="clear_memory", type="primary"):
                if st.checkbox("⚠️ Potwierdź usunięcie", key="confirm_delete"):
                    import shutil
                    if MEMORY_FOLDER.exists():
                        shutil.rmtree(MEMORY_FOLDER)
                        MEMORY_FOLDER.mkdir(exist_ok=True)
                    st.success("✅ Pamięć długoterminowa wyczyszczona!")
                    st.rerun()
        
        # Szczegóły per partner
        with st.expander("📊 Szczegóły pamięci partnerów"):
            for name in PERSONAS.keys():
                if 'Partner Zarządzający' in name and '(JA)' in name:
                    continue
                
                stats = get_memory_statistics(name)
                if stats:
                    display_name = name.split('(')[0].strip() if '(' in name else name
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.markdown(f"**{display_name}**")
                    with col_b:
                        st.caption(f"{stats.get('total_messages', 0)} rozmów")
                    with col_c:
                        if stats.get('last_interaction'):
                            last = datetime.fromisoformat(stats['last_interaction'])
                            st.caption(f"Ostatnio: {last.strftime('%Y-%m-%d')}")
    
    st.markdown("---")
    
    st.subheader("🎨 Wygląd")
    st.caption("💾 Ustawienia są automatycznie zapisywane")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme_option = st.selectbox(
            "Motyw",
            ["Jasny", "Ciemny"],
            index=0 if st.session_state.theme == "light" else 1,
            key="theme_select"
        )
        
        if theme_option == "Jasny" and st.session_state.theme != "light":
            st.session_state.theme = "light"
            # Zapisz preferencje
            preferences = {
                "theme": st.session_state.theme,
                "notifications_enabled": st.session_state.notifications_enabled,
                "cache_ttl": st.session_state.cache_ttl,
                "auto_refresh": st.session_state.auto_refresh,
                "refresh_interval": st.session_state.refresh_interval
            }
            if save_user_preferences(preferences):
                st.toast("💾 Motyw zapisany!", icon="✅")
            st.rerun()
        elif theme_option == "Ciemny" and st.session_state.theme != "dark":
            st.session_state.theme = "dark"
            # Zapisz preferencje
            preferences = {
                "theme": st.session_state.theme,
                "notifications_enabled": st.session_state.notifications_enabled,
                "cache_ttl": st.session_state.cache_ttl,
                "auto_refresh": st.session_state.auto_refresh,
                "refresh_interval": st.session_state.refresh_interval
            }
            if save_user_preferences(preferences):
                st.toast("💾 Motyw zapisany!", icon="✅")
            st.rerun()
    
    with col2:
        st.info(f"Aktualny motyw: **{st.session_state.theme.upper()}**")
    
    st.markdown("---")
    
    st.subheader("🔔 Powiadomienia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        notifications = st.checkbox(
            "Włącz powiadomienia",
            value=st.session_state.notifications_enabled,
            key="notif_checkbox"
        )
        
        # Jeśli zmieniono ustawienie powiadomień
        if notifications != st.session_state.notifications_enabled:
            st.session_state.notifications_enabled = notifications
            # Zapisz preferencje
            preferences = {
                "theme": st.session_state.theme,
                "notifications_enabled": st.session_state.notifications_enabled,
                "cache_ttl": st.session_state.cache_ttl,
                "auto_refresh": st.session_state.auto_refresh,
                "refresh_interval": st.session_state.refresh_interval
            }
            save_user_preferences(preferences)
        
        if notifications:
            st.success("✅ Powiadomienia włączone")
            
            # Opcje powiadomień
            st.markdown("**Powiadamiaj o:**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.checkbox("📉 Spadki >5%", value=True)
                st.checkbox("🎯 Cele osiągnięte", value=True)
            with col_b:
                st.checkbox("💰 Nowe dywidendy", value=True)
                st.checkbox("⚠️ Wysokie ryzyko", value=False)
        else:
            st.warning("⚠️ Powiadomienia wyłączone")
    
    with col2:
        if st.button("🔔 Testuj powiadomienie", width="stretch"):
            st.toast("🎉 To jest testowe powiadomienie!")
            st.balloons()
    
    st.markdown("---")
    
    st.subheader("📊 Dane i Cache")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cache_ttl = st.slider(
            "Czas cache danych (minuty)",
            min_value=1,
            max_value=60,
            value=st.session_state.cache_ttl,
            key="cache_slider"
        )
        st.session_state.cache_ttl = cache_ttl
        
        st.caption(f"Dane będą odświeżane co {cache_ttl} minut")
    
    with col2:
        if st.button("🗑️ Wyczyść cache teraz", width="stretch"):
            st.cache_data.clear()
            st.success("✅ Cache wyczyszczony!")
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("🔄 Auto-refresh")
    
    col1, col2 = st.columns(2)
    
    with col1:
        auto_refresh = st.checkbox(
            "Włącz automatyczne odświeżanie",
            value=st.session_state.auto_refresh,
            key="auto_refresh_checkbox"
        )
        st.session_state.auto_refresh = auto_refresh
        
        if auto_refresh:
            refresh_interval = st.slider(
                "Interwał odświeżania (sekundy)",
                min_value=10,
                max_value=300,
                value=st.session_state.refresh_interval,
                step=10,
                key="refresh_slider"
            )
            st.session_state.refresh_interval = refresh_interval
            
            st.info(f"⏱️ Auto-refresh co {refresh_interval}s")
            
            # Auto-refresh logic
            import time
            time.sleep(refresh_interval)
            st.rerun()
    
    with col2:
        if auto_refresh:
            st.success("✅ Auto-refresh aktywny")
        else:
            st.warning("⚠️ Auto-refresh wyłączony")
    
    st.markdown("---")
    
    st.subheader("💾 Eksport Ustawień")
    
    col1, col2 = st.columns(2)
    
    with col1:
        settings_dict = {
            "theme": st.session_state.theme,
            "notifications_enabled": st.session_state.notifications_enabled,
            "cache_ttl": st.session_state.cache_ttl,
            "auto_refresh": st.session_state.auto_refresh,
            "refresh_interval": st.session_state.refresh_interval
        }
        
        st.json(settings_dict)
    
    with col2:
        if st.button("💾 Zapisz ustawienia do pliku", width="stretch"):
            try:
                with open("streamlit_settings.json", "w", encoding='utf-8') as f:
                    json.dump(settings_dict, f, indent=2, ensure_ascii=False)
                st.success("✅ Ustawienia zapisane do streamlit_settings.json")
            except Exception as e:
                st.error(f"❌ Błąd zapisu: {e}")
        
        if st.button("📂 Wczytaj ustawienia z pliku", width="stretch"):
            try:
                with open("streamlit_settings.json", "r", encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                st.session_state.theme = loaded_settings.get("theme", "light")
                st.session_state.notifications_enabled = loaded_settings.get("notifications_enabled", True)
                st.session_state.cache_ttl = loaded_settings.get("cache_ttl", 5)
                st.session_state.auto_refresh = loaded_settings.get("auto_refresh", False)
                st.session_state.refresh_interval = loaded_settings.get("refresh_interval", 60)
                
                st.success("✅ Ustawienia wczytane!")
                st.rerun()
            except FileNotFoundError:
                st.error("❌ Plik streamlit_settings.json nie istnieje")
    
    st.markdown("---")
    
    # === NOWA SEKCJA: PORTFOLIO CO-PILOT ===
    st.subheader("📊 Portfolio Co-Pilot")
    
    st.markdown("""
    System automatycznego generowania tygodniowych raportów portfela.
    Raport zawiera: osiągnięcia, ostrzeżenia, rekomendacje i statystyki.
    """)
    
    # === OSTATNI RAPORT (jeśli istnieje) ===
    latest_reports = load_weekly_reports(limit=1)
    if latest_reports:
        latest_report = latest_reports[0]
        
        st.info(f"📊 **Ostatni raport:** Tydzień {latest_report.get('week_number', '?')}/{latest_report.get('year', '?')}")
        
        # Szybki podgląd - kluczowe metryki w kolumnach
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            mood_emoji = latest_report.get("mood", {}).get("emoji", "😐")
            mood_level = latest_report.get("mood", {}).get("level", "neutral")
            st.metric("Nastrój", f"{mood_emoji} {mood_level.title()}")
        
        with col_m2:
            achievements = latest_report.get("achievements", [])
            st.metric("Osiągnięcia", len(achievements), delta="pozytywne" if achievements else None)
        
        with col_m3:
            warnings = latest_report.get("warnings", [])
            st.metric("Ostrzeżenia", len(warnings), delta="negatywne" if warnings else None)
        
        with col_m4:
            actions = latest_report.get("action_items", [])
            st.metric("Akcje", len(actions))
        
        # Szybki przegląd - najważniejsze informacje
        summary = latest_report.get("summary", "")
        if summary:
            st.success(f"**Streszczenie:** {summary}")
        
        # Top osiągnięcia i ostrzeżenia
        col_preview1, col_preview2 = st.columns(2)
        
        with col_preview1:
            achievements = latest_report.get("achievements", [])
            if achievements:
                st.markdown("**🎉 Top 3 Osiągnięcia:**")
                for ach in achievements[:3]:
                    st.markdown(f"- {ach.get('icon', '✓')} {ach.get('title', 'N/A')}")
        
        with col_preview2:
            warnings = latest_report.get("warnings", [])
            if warnings:
                st.markdown("**⚠️ Top 3 Ostrzeżenia:**")
                for warn in warnings[:3]:
                    st.markdown(f"- {warn.get('icon', '⚠')} {warn.get('title', 'N/A')}")
        
        # Pełny raport w expanderze
        with st.expander("📖 Pokaż pełny raport", expanded=False):
            display_weekly_report(latest_report)
        
        st.markdown("---")
    
    col_cp1, col_cp2, col_cp3 = st.columns([3, 2, 1])
    
    with col_cp1:
        if st.button("📝 Generuj Raport Tygodniowy", width="stretch", type="primary"):
            with st.spinner("📊 Generuję raport..."):
                try:
                    stan_spolki, cele = load_portfolio_data()
                    report = generate_weekly_report(stan_spolki, cele)
                    
                    if report and "error" not in report:
                        filepath = save_weekly_report(report)
                        
                        if filepath:
                            st.success(f"✅ Raport wygenerowany: `{filepath.name}`")
                            st.balloons()
                            
                            # Automatyczne odświeżenie strony
                            st.rerun()
                        else:
                            st.error("❌ Błąd zapisu raportu")
                    else:
                        st.error(f"❌ Błąd generowania: {report.get('error', 'Unknown')}")
                        
                except Exception as e:
                    st.error(f"❌ Błąd: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    
    with col_cp2:
        st.info(f"**Aktualny tydzień:** {datetime.now().isocalendar()[1]}")
        st.caption(f"Rok: {datetime.now().year}")
    
    with col_cp3:
        if st.button("🔄", width="stretch", help="Odśwież stronę"):
            st.rerun()
    
    # Historia raportów
    st.markdown("**📚 Historia Raportów:**")
    
    reports = load_weekly_reports(limit=5)
    
    if reports:
        st.caption(f"Znaleziono {len(reports)} ostatnich raportów")
        
        for i, report in enumerate(reports):
            with st.expander(f"📄 Tydzień {report.get('week_number', '?')}/{report.get('year', '?')} - {report.get('summary', 'Brak opisu')[:60]}..."):
                display_weekly_report(report)
                
                col_del1, col_del2, col_del3 = st.columns([2, 1, 1])
                
                with col_del2:
                    if st.button("📥 Eksportuj", key=f"export_report_{i}"):
                        st.info("Eksport wkrótce!")
                
                with col_del3:
                    if st.button("🗑️ Usuń", key=f"delete_report_{i}"):
                        try:
                            reports_folder = Path("weekly_reports")
                            filepath = reports_folder / report.get("filename", "")
                            if filepath.exists():
                                filepath.unlink()
                                st.success("✅ Raport usunięty")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Błąd usuwania: {e}")
    else:
        st.info("Brak raportów. Wygeneruj pierwszy raport przyciskiem powyżej!")
    
    # Ustawienia auto-generowania
    with st.expander("⚙️ Ustawienia Auto-generowania"):
        auto_gen = st.checkbox(
            "Automatycznie generuj raport w niedzielę",
            value=False,
            help="System automatycznie wygeneruje raport w każdą niedzielę o 20:00"
        )
        
        if auto_gen:
            st.success("✅ Auto-generowanie włączone")
            st.caption("Raport będzie generowany każdą niedzielę o 20:00")
        else:
            st.info("ℹ️ Auto-generowanie wyłączone - generuj ręcznie")
    
    st.markdown("---")
    
    st.subheader("🔧 Zaawansowane")
    
    with st.expander("🐛 Debug Info"):
        st.write("**Session State:**")
        st.json(dict(st.session_state))
        
        st.write("**Streamlit Version:**")
        st.code(st.__version__)
        
        st.write("**Cache Stats:**")
        st.write(f"Cache TTL: {st.session_state.cache_ttl} min")
    
    with st.expander("⚡ Performance"):
        st.write("**Optymalizacje:**")
        st.checkbox("Enable caching", value=True, disabled=True)
        st.checkbox("Lazy loading", value=True)
        st.checkbox("Compress data", value=False)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reset do domyślnych", width="stretch"):
            st.session_state.theme = "light"
            st.session_state.notifications_enabled = True
            st.session_state.cache_ttl = 5
            st.session_state.auto_refresh = False
            st.session_state.refresh_interval = 60
            st.success("✅ Przywrócono domyślne ustawienia")
            st.rerun()
    
    with col2:
        if st.button("💾 Zapisz i zamknij", width="stretch"):
            st.success("✅ Ustawienia zapisane!")
            st.balloons()
    
    with col3:
        if st.button("❌ Anuluj zmiany", width="stretch"):
            st.rerun()
if __name__ == "__main__":
    main()
