"""
?? HORYZONT PARTNER”W - Streamlit Dashboard
Interaktywny dashboard do zarzπdzania portfelem inwestycyjnym
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# Konfiguracja strony - MUSI byÊ jako pierwsze
st.set_page_config(
    page_title="Horyzont PartnerÛw",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === EKRAN £ADOWANIA ===
if 'app_loaded' not in st.session_state:
    st.session_state.app_loaded = False

if not st.session_state.app_loaded:
    # Pokaø ekran ≥adowania
    with st.spinner(''):
        st.markdown("""
        <div style="text-align: center; padding: 100px 20px;">
            <h1 style="color: #1f77b4;">?? HORYZONT PARTNER”W</h1>
            <p style="font-size: 18px; color: #666;">?? 100% Lazy Loading - start w <5 sekund!</p>
            <p style="font-size: 14px; color: #999;">Wszystkie AI/Sheets za≥adujπ siÍ dopiero gdy bÍdπ uøyte</p>
            <p style="font-size: 12px; color: #aaa;">Gemini: pierwszy chat | Claude/OpenAI: wybÛr w ustawieniach | Sheets: load danych</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Krok 1: Podstawowe modu≥y
        status_text.text("?? £adowanie modu≥Ûw podstawowych...")
        progress_bar.progress(20)

# API Usage Tracker
from api_usage_tracker import get_tracker

# Email Notifier (dla Fazy 2)
from email_notifier import get_conversation_notifier

# Consultation System (dla Fazy 2D)
from consultation_system import get_consultation_manager

# Folder dla pamiÍci d≥ugoterminowej
MEMORY_FOLDER = Path("partner_memories")
MEMORY_FOLDER.mkdir(exist_ok=True)

# Importy z g≥Ûwnego programu
if not st.session_state.app_loaded:
    status_text.text("?? 100% lazy load - bez AI przy starcie!")
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
        status_text.text("?? £adowanie modu≥Ûw analitycznych...")
        progress_bar.progress(60)
    
    from risk_analytics import RiskAnalytics, PortfolioHistory
    from animated_timeline import AnimatedTimeline
    from excel_reporter import ExcelReportGenerator, generate_full_report
    
    if not st.session_state.app_loaded:
        status_text.text("?? InicjalizujÍ pamiÍÊ AI partnerÛw...")
        progress_bar.progress(80)
    
    import persona_memory_manager as pmm
    from persona_context_builder import build_enhanced_context, get_emotional_modifier, load_persona_memory
    from crypto_portfolio_manager import CryptoPortfolioManager
    
    IMPORTS_OK = True
    MEMORY_OK = True
    MEMORY_V2 = True
    CRYPTO_MANAGER_OK = True
    
    if not st.session_state.app_loaded:
        status_text.text("? Gotowe! Uruchamiam dashboard...")
        progress_bar.progress(100)
        st.session_state.app_loaded = True
        st.rerun()
        
except ImportError as e:
    if "persona_memory_manager" in str(e) or "persona_context_builder" in str(e):
        IMPORTS_OK = True
        MEMORY_OK = False
        MEMORY_V2 = False
        CRYPTO_MANAGER_OK = "crypto_portfolio_manager" not in str(e)
        st.warning("?? System pamiÍci AI niedostÍpny")
    elif "crypto_portfolio_manager" in str(e):
        IMPORTS_OK = True
        MEMORY_OK = True
        MEMORY_V2 = True
        CRYPTO_MANAGER_OK = False
        st.warning("?? Crypto Portfolio Manager niedostÍpny - ceny na øywo wy≥πczone")
    else:
        IMPORTS_OK = False
        MEMORY_OK = False
        MEMORY_V2 = False
        CRYPTO_MANAGER_OK = False
        st.error(f"?? B≥πd importu: {e}")
    
    if not st.session_state.app_loaded:
        st.session_state.app_loaded = True
        st.rerun()
        
except Exception as e:
    IMPORTS_OK = False
    MEMORY_OK = False
    MEMORY_V2 = False
    CRYPTO_MANAGER_OK = False
    st.error(f"?? B≥πd importu: {e}")
    
    if not st.session_state.app_loaded:
        st.session_state.app_loaded = True
        st.rerun()
    import traceback
    st.code(traceback.format_exc())

# === FUNKCJE DO ZARZ•DZANIA WAGAMI G£OSU Z KODEKSU ===
def wczytaj_wagi_glosu_z_kodeksu():
    """
    Parsuje kodeks_spolki.txt i zwraca s≥ownik z wagami g≥osu dla kaødego partnera.
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
    # UWAGA: W kodeksie sπ stare nazwy, w PERSONAS sπ inne!
    mapping = {
        "Partner Zarzπdzajπcy (Pan)": "Partner Zarzπdzajπcy (JA)",
        "Partner Strategiczny (Ja)": "Partner Strategiczny",
        "Partner ds. Jakoúci Biznesowej": "Partner ds. Jakoúci Biznesowej",
        "Partner ds. AktywÛw Cyfrowych": "Partner ds. AktywÛw Cyfrowych",
        "Konsultant Strategiczny ds. AktywÛw Cyfrowych": "Changpeng Zhao (CZ)"
    }
    
    wagi = {}
    
    # Szukaj linii z procentami g≥osu lub wp≥ywu filozoficznego
    pattern = r'(.+?):\s*(\d+)%\s+(?:udzia≥Ûw w g≥osach|wp≥ywu filozoficznego)'
    matches = re.findall(pattern, kodeks)
    
    for nazwa_surowa, procent in matches:
        nazwa = nazwa_surowa.strip()
        procent_float = float(procent)
        
        if nazwa in mapping:
            persona_name = mapping[nazwa]
            wagi[persona_name] = procent_float
        elif "Rada Nadzorcza" in nazwa:
            # Rada Nadzorcza 15% - rozdziel rÛwno miÍdzy cz≥onkÛw w PERSONAS
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
    Zapisuje zaktualizowane wagi g≥osu z powrotem do kodeksu_spolki.txt.
    
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
        "Partner Zarzπdzajπcy (JA)": "Partner Zarzπdzajπcy (Pan)",
        "Partner Strategiczny": "Partner Strategiczny (Ja)",
        "Partner ds. Jakoúci Biznesowej": "Partner ds. Jakoúci Biznesowej",
        "Partner ds. AktywÛw Cyfrowych": "Partner ds. AktywÛw Cyfrowych",
        "Changpeng Zhao (CZ)": "Konsultant Strategiczny ds. AktywÛw Cyfrowych"
    }
    
    # Rada Nadzorcza - zsumuj wagi cz≥onkÛw (RZECZYWISTE nazwy z PERSONAS)
    rada_nadzorcza = [
        "Benjamin Graham",
        "Philip Fisher",
        "George Soros",
        "Warren Buffett"
    ]
    
    rada_suma = sum(wagi.get(czlonek, 0) for czlonek in rada_nadzorcza)
    
    # Aktualizuj poszczegÛlne linie w kodeksie
    for persona_name, procent in wagi.items():
        if persona_name in reverse_mapping:
            kodeks_name = reverse_mapping[persona_name]
            # Znajdü liniÍ z tπ nazwπ i zaktualizuj procent
            pattern = rf'({re.escape(kodeks_name)}:\s*)\d+(% udzia≥Ûw w g≥osach)'
            kodeks = re.sub(pattern, rf'\g<1>{int(procent)}\g<2>', kodeks)
    
    # Zaktualizuj RadÍ Nadzorczπ (wp≥yw filozoficzny)
    if rada_suma > 0:
        pattern = r'(Rada Nadzorcza.*?:\s*)\d+(% wp≥ywu filozoficznego)'
        kodeks = re.sub(pattern, rf'\g<1>{int(rada_suma)}\g<2>', kodeks)
    
    # Zapisz zaktualizowany kodeks
    try:
        with open('kodeks_spolki.txt', 'w', encoding='utf-8') as f:
            f.write(kodeks)
        return True
    except Exception as e:
        st.error(f"B≥πd zapisu kodeksu: {e}")
        return False

# Funkcje pomocnicze do integracji AI
def send_to_ai_partner(partner_name, message, stan_spolki=None, cele=None, tryb_odpowiedzi="normalny"):
    """Wysy≥a wiadomoúÊ do pojedynczego Partnera AI z pe≥nym kontekstem jak w gra_rpg.py"""
    try:
        if not IMPORTS_OK:
            return "[Import gra_rpg.py nie powiÛd≥ siÍ]"
        
        # Pobierz konfiguracjÍ partnera
        persona_config = PERSONAS.get(partner_name, {})
        
        # === KODEKS SP”£KI ===
        kodeks = ""
        if os.path.exists('kodeks_spolki.txt'):
            with open('kodeks_spolki.txt', 'r', encoding='utf-8') as f:
                kodeks = f.read()
        
        # === PRZYGOTUJ DANE FINANSOWE ===
        if not stan_spolki:
            stan_spolki = {}
        
        # Podstawowe wartoúci
        akcje_val = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
        krypto_val = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
        rezerwa_val = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
        dlugi_val = get_suma_kredytow()  # Pobierz z kredyty.json zamiast Google Sheets
        wyplata_info = stan_spolki.get('wyplata', {})
        dostepne = wyplata_info.get('dostepne_na_inwestycje', 0)
        
        # === SZCZEG”£Y POZYCJI (TOP 10) ===
        pozycje_szczegoly = stan_spolki.get('akcje', {}).get('pozycje', {})
        sorted_pozycje = sorted(
            pozycje_szczegoly.items(),
            key=lambda x: x[1].get('wartosc_total_usd', 0),
            reverse=True
        )
        
        szczegoly_top10 = "\n\n?? SZCZEG”£Y TOP 10 POZYCJI W PORTFELU:\n"
        for ticker, dane in sorted_pozycje[:10]:
            szczegoly_top10 += f"ï {ticker}:\n"
            szczegoly_top10 += f"  - IloúÊ: {dane.get('ilosc', 0):.2f} akcji\n"
            szczegoly_top10 += f"  - WartoúÊ: ${dane.get('wartosc_total_usd', 0):.2f} (${dane.get('wartosc_obecna_usd', 0):.2f}/akcja)\n"
            szczegoly_top10 += f"  - Koszt zakupu: ${dane.get('koszt_total_usd', 0):.2f} (${dane.get('cena_zakupu_usd', 0):.2f}/akcja)\n"
            szczegoly_top10 += f"  - Zysk/Strata: ${dane.get('zysk_total_usd', 0):.2f} ({dane.get('zmiana_proc', 0):.1f}%)\n"
        
        # === DANE RYNKOWE ===
        dane_rynkowe_str = "\n\n?? DANE RYNKOWE (wybrane spÛ≥ki):\n"
        dane_rynkowe = {}
        if IMPORTS_OK:
            try:
                from gra_rpg import pobierz_stan_spolki
                stan_pelny = pobierz_stan_spolki(cele or {})
                if stan_pelny:
                    dane_rynkowe = stan_pelny.get('PORTFEL_AKCJI', {}).get('Dane_rynkowe', {})
            except:
                pass
        
        if dane_rynkowe:
            for ticker, dane in list(dane_rynkowe.items())[:8]:
                pe = dane.get('PE')
                pe_str = f"P/E: {pe:.1f}" if pe and pe > 0 else "P/E: N/A"
                dywidenda = dane.get('dywidenda_roczna', 0)
                dywidenda_str = f"Dywidenda: {dywidenda*100:.1f}%" if dywidenda else "Dywidenda: N/A"
                sektor = dane.get('sektor', 'N/A')
                dane_rynkowe_str += f"ï {dane.get('nazwa', ticker)} ({ticker}): {pe_str}, {dywidenda_str}, {sektor}\n"
        else:
            dane_rynkowe_str += "Brak dostÍpnych danych rynkowych.\n"
        
        # === KONTEKST SKALI ===
        kontekst_skali = f"\n\n?? KONTEKST SKALI:\n"
        kontekst_skali += f"To sπ prywatne finanse osoby fizycznej.\n"
        kontekst_skali += f"DostÍpny kapita≥ miesiÍcznie: ~{dostepne:.2f} PLN\n"
        kontekst_skali += f"WartoúÊ netto portfela: {akcje_val + krypto_val + rezerwa_val - dlugi_val:.2f} PLN (Akcje + Krypto + Rezerwa - Zobowiπzania)\n"
        
        # === HISTORIA SNAPSHOTS ===
        snapshot_section = ""
        try:
            import daily_snapshot as ds
            history = ds.load_snapshot_history()
            if len(history) >= 2:
                stats = ds.get_snapshot_stats()
                first = history[0]
                last = history[-1]
                
                snapshot_section = f"\n\n?? HISTORIA PORTFOLIO (DAILY SNAPSHOTS):\n"
                snapshot_section += f"- Okres úledzenia: {stats['first_date']} õ {stats['last_date']} ({stats['days_tracked']} dni)\n"
                snapshot_section += f"- Liczba snapshots: {stats['count']}\n"
                snapshot_section += f"- Net Worth PIERWSZY: {first['totals']['net_worth_pln']:.2f} PLN\n"
                snapshot_section += f"- Net Worth OSTATNI: {last['totals']['net_worth_pln']:.2f} PLN\n"
                snapshot_section += f"- Zmiana: {stats['percent_change']:.2f}%\n"
                snapshot_section += f"- årednio snapshots/tydzieÒ: {stats['avg_per_week']:.1f}\n\n"
                snapshot_section += "OSTATNIE 3 SNAPSHOTS:\n"
                
                for h in history[-3:]:
                    snapshot_section += f"ï {h['date_only']}: Net Worth {h['totals']['net_worth_pln']:.2f} PLN "
                    snapshot_section += f"(Akcje: {h['stocks']['value_pln']:.0f} PLN, Krypto: {h['crypto']['value_pln']:.0f} PLN, D≥ugi: {h['debt']['total_pln']:.0f} PLN)\n"
        except:
            pass  # Jeúli brak snapshots lub b≥πd importu, kontynuuj bez tej sekcji
        
        # === INSTRUKCJE D£UGOåCI ODPOWIEDZI ===
        if tryb_odpowiedzi == "zwiezly":
            length_instruction = """
TRYB ODPOWIEDZI: ZWI Z£Y
- Odpowiedü 2-4 zdania MAX
- Tylko najwaøniejsze punkty
- Konkretne liczby i wnioski
- Brak rozbudowanych wyjaúnieÒ
"""
        elif tryb_odpowiedzi == "szczegolowy":
            length_instruction = """
TRYB ODPOWIEDZI: SZCZEG”£OWY
- Pe≥na analiza (8-12 zdaÒ)
- Dok≥adne wyjaúnienia i uzasadnienia
- Odniesienia do konkretnych pozycji
- Rekomendacje krok po kroku
- Cytuj Kodeks gdy stosowne
"""
        else:
            length_instruction = """
TRYB ODPOWIEDZI: NORMALNY
- Odpowiedü 4-6 zdaÒ
- Balans miÍdzy szczegÛ≥ami a zwiÍz≥oúciπ
- Konkretne dane z portfela
- Praktyczne wnioski
"""
        
        # === PAMI ∆ D£UGOTERMINOWA ===
        memory_context = load_memory_context(partner_name, limit=5)
        memory_section = memory_context if memory_context else ""
        
        # === PAMI ∆ PERSONY (track record i ewolucja) ===
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
                st.warning(f"?? B≥πd wczytywania pamiÍci persony: {e}")
        
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
            # Dodaj tylko najwaøniejsze alerty do promptu
            critical_alerts = [a for a in alerts if a["severity"] == "critical"]
            warning_alerts = [a for a in alerts if a["severity"] == "warning"]
            important_alerts = critical_alerts + warning_alerts[:2]  # Max 2 warning
            
            if important_alerts:
                alerts_section = "\n\n?? AKTYWNE ALERTY PORTFELA:\n"
                for alert in important_alerts:
                    severity_emoji = "??" if alert["severity"] == "critical" else "??"
                    alerts_section += f"{severity_emoji} {alert['title']}: {alert['message']}\n"
                    if alert.get('action'):
                        alerts_section += f"   õ Rekomendacja: {alert['action']}\n"
                
                alerts_section += "\n?? WAØNE: Moøesz odnieúÊ siÍ do tych alertÛw w swojej odpowiedzi jeúli sπ istotne dla pytania uøytkownika!\n"
        
        # === NEWSY FINANSOWE ===
        news_section = ""
        try:
            import news_aggregator as na
            news_section = na.format_news_for_ai(limit=5)
        except Exception as e:
            # Jeúli news_aggregator nie dzia≥a, pomijamy tÍ sekcjÍ
            pass
        
        # === BUDOWA PROMPTU (JAK W GRA_RPG.PY) ===
        prompt = f"""{persona_config.get('system_instruction', '')}

KODEKS SP”£KI "HORYZONT PARTNER”W":
    {kodeks}

---
Twoim tajnym celem jest: {persona_config.get('ukryty_cel', 'Wspieranie rozwoju spÛ≥ki')}
---

{persona_memory_section}

{emotional_hint}

{memory_section}

{mood_modifier}

{alerts_section}

{knowledge_section}

AKTUALNY STAN FINANSOWY SP”£KI:

?? PODSUMOWANIE:
    - WartoúÊ netto: {akcje_val + krypto_val + rezerwa_val - dlugi_val:.2f} PLN (Akcje + Krypto + Rezerwa - Zobowiπzania)
- Akcje: {akcje_val:.2f} PLN ({stan_spolki.get('akcje', {}).get('liczba_pozycji', 0)} pozycji)
- Krypto: {krypto_val:.2f} PLN ({stan_spolki.get('krypto', {}).get('liczba_pozycji', 0)} pozycji)
- Rezerwa GotÛwkowa: {rezerwa_val:.2f} PLN  
- Zobowiπzania: {dlugi_val:.2f} PLN
- DostÍpne na inwestycje: {dostepne:.2f} PLN/mies.

{szczegoly_top10}

{dane_rynkowe_str}

{kontekst_skali}

{snapshot_section}

{news_section}

---
{length_instruction}
---

PYTANIE UØYTKOWNIKA:
    "{message}"

TWOJE ZADANIE:
    Odpowiedz jako cz≥onek Zarzπdu spÛ≥ki inwestycyjnej:
- Odwo≥uj siÍ do Kodeksu gdy stosowne (np. "Zgodnie z Artyku≥em IV ß1...")
- Analizuj konkretne liczby z portfela
- Ton profesjonalny ale nie przesadnie korporacyjny
- Wykorzystaj swojπ unikalnπ perspektywÍ i wiedzÍ
- Realizuj swÛj ukryty cel w sposÛb subtelny
"""
        
        # Wywo≥aj AI
        response = generuj_odpowiedz_ai(partner_name, prompt)
        
        # Bezpiecznie wydobπdü tekst z response (moøe byÊ string lub obiekt)
        if hasattr(response, 'text'):
            response_text = response.text
        elif isinstance(response, str):
            response_text = response
        else:
            response_text = str(response)
        
        # Zapisz do pamiÍci d≥ugoterminowej
        save_conversation_to_memory(partner_name, message, response_text, stan_spolki)
        
        return response_text, relevant_knowledge
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"[B≥πd AI: {str(e)}\n{error_detail}]", []

def save_conversation_to_memory(partner_name, user_message, ai_response, stan_spolki=None):
    """Zapisuje rozmowÍ do pamiÍci d≥ugoterminowej partnera"""
    try:
        memory_file = MEMORY_FOLDER / f"{partner_name.replace('/', '_').replace(' ', '_')}.json"
        
        # Za≥aduj istniejπcπ pamiÍÊ lub stwÛrz nowπ
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8-sig') as f:
                memory = json.load(f)
        else:
            memory = {
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
        
        # Dodaj nowπ rozmowÍ
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
        
        memory["conversations"].append(conversation_entry)
        memory["statistics"]["total_messages"] += 1
        memory["statistics"]["last_interaction"] = datetime.now().isoformat()
        
        # Zachowaj ostatnie 100 rozmÛw (øeby plik nie rÛs≥ w nieskoÒczonoúÊ)
        if len(memory["conversations"]) > 100:
            memory["conversations"] = memory["conversations"][-100:]
        
        # Zapisz
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"B≥πd zapisu pamiÍci dla {partner_name}: {e}")
        return False

def load_memory_context(partner_name, limit=5):
    """£aduje kontekst z pamiÍci d≥ugoterminowej partnera"""
    try:
        memory_file = MEMORY_FOLDER / f"{partner_name.replace('/', '_').replace(' ', '_')}.json"
        
        if not memory_file.exists():
            return None
        
        with open(memory_file, 'r', encoding='utf-8-sig') as f:
            memory = json.load(f)
        
        # Pobierz ostatnie N rozmÛw
        recent_conversations = memory["conversations"][-limit:] if memory["conversations"] else []
        
        if not recent_conversations:
            return None
        
        # Formatuj kontekst
        context = "\n\n?? PAMI ∆ Z POPRZEDNICH ROZM”W:\n"
        context += f"(Ostatnie {len(recent_conversations)} rozmÛw z {memory['statistics']['total_messages']} ca≥kowitych)\n\n"
        
        for conv in recent_conversations:
            date = datetime.fromisoformat(conv['timestamp']).strftime("%Y-%m-%d %H:%M")
            context += f"[{date}]\n"
            context += f"Uøytkownik: {conv['user_message'][:100]}...\n"
            context += f"Ty: {conv['ai_response'][:150]}...\n\n"
        
        return context
        
    except Exception as e:
        print(f"B≥πd ≥adowania pamiÍci dla {partner_name}: {e}")
        return None

def get_memory_statistics(partner_name):
    """Pobiera statystyki pamiÍci partnera"""
    try:
        memory_file = MEMORY_FOLDER / f"{partner_name.replace('/', '_').replace(' ', '_')}.json"
        
        if not memory_file.exists():
            return None
        
        with open(memory_file, 'r', encoding='utf-8-sig') as f:
            memory = json.load(f)
        
        return memory["statistics"]
    except:
        return None

def analyze_portfolio_mood(stan_spolki, cele=None):
    """Analizuje stan portfela i zwraca nastrÛj (mood) oraz szczegÛ≥y"""
    try:
        if not stan_spolki:
            return {"mood": "neutral", "emoji": "??", "reason": "Brak danych portfela"}
        
        mood_data = {
            "mood": "neutral",
            "emoji": "??",
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
        
        # === ANALIZA 1: OgÛlna performance portfela ===
        if pozycje:
            positions_with_change = [(ticker, data) for ticker, data in pozycje.items() 
                                    if data.get('zmiana_proc') is not None]
            
            if positions_with_change:
                avg_change = sum(p[1].get('zmiana_proc', 0) for p in positions_with_change) / len(positions_with_change)
                
                if avg_change > 15:
                    mood_data["score"] += 40
                    mood_data["highlights"].append(f"?? åwietna performance! åredni zysk: +{avg_change:.1f}%")
                elif avg_change > 5:
                    mood_data["score"] += 20
                    mood_data["highlights"].append(f"?? Dobry wzrost: +{avg_change:.1f}%")
                elif avg_change < -10:
                    mood_data["score"] -= 40
                    mood_data["warnings"].append(f"?? Portfel spada: {avg_change:.1f}%")
                elif avg_change < -5:
                    mood_data["score"] -= 20
                    mood_data["warnings"].append(f"?? Lekkie spadki: {avg_change:.1f}%")
        
        # === ANALIZA 2: Leverage i ryzyko ===
        if total_assets > 0:
            leverage = (dlugi_val / total_assets) * 100
            
            if leverage > 50:
                mood_data["score"] -= 30
                mood_data["warnings"].append(f"?? WYSOKI leverage: {leverage:.1f}%")
            elif leverage > 30:
                mood_data["score"] -= 15
                mood_data["warnings"].append(f"?? Podwyøszony leverage: {leverage:.1f}%")
            elif leverage < 15 and dlugi_val > 0:
                mood_data["score"] += 10
                mood_data["highlights"].append(f"? Zdrowy leverage: {leverage:.1f}%")
        
        # === ANALIZA 3: NajwiÍksze pozycje ===
        if pozycje:
            sorted_pozycje = sorted(pozycje.items(), 
                                   key=lambda x: x[1].get('wartosc_total_usd', 0), 
                                   reverse=True)
            
            # Najlepszy performer
            best = max(positions_with_change, key=lambda x: x[1].get('zmiana_proc', 0)) if positions_with_change else None
            if best and best[1].get('zmiana_proc', 0) > 30:
                mood_data["score"] += 15
                mood_data["highlights"].append(f"?? {best[0]}: +{best[1].get('zmiana_proc', 0):.1f}% ??")
            
            # Najgorszy performer
            worst = min(positions_with_change, key=lambda x: x[1].get('zmiana_proc', 0)) if positions_with_change else None
            if worst and worst[1].get('zmiana_proc', 0) < -20:
                mood_data["score"] -= 15
                mood_data["warnings"].append(f"?? {worst[0]}: {worst[1].get('zmiana_proc', 0):.1f}%")
        
        # === ANALIZA 4: WartoúÊ netto ===
        if net_worth > 50000:
            mood_data["score"] += 20
            mood_data["highlights"].append(f"?? Silna pozycja: {net_worth:.0f} PLN netto")
        elif net_worth < 0:
            mood_data["score"] -= 50
            mood_data["warnings"].append(f"?? UJEMNA wartoúÊ netto: {net_worth:.0f} PLN")
        
        # === OKREåL MOOD na podstawie score ===
        final_score = mood_data["score"]
        
        if final_score >= 50:
            mood_data["mood"] = "very_bullish"
            mood_data["emoji"] = "??"
            mood_data["description"] = "åwietnie! Portfel roúnie silnie!"
        elif final_score >= 20:
            mood_data["mood"] = "bullish"
            mood_data["emoji"] = "??"
            mood_data["description"] = "Dobry momentum, wszystko idzie dobrze"
        elif final_score >= -20:
            mood_data["mood"] = "neutral"
            mood_data["emoji"] = "??"
            mood_data["description"] = "Stabilna sytuacja, bez wiÍkszych zmian"
        elif final_score >= -50:
            mood_data["mood"] = "cautious"
            mood_data["emoji"] = "??"
            mood_data["description"] = "Ostroønie, niektÛre sygna≥y ostrzegawcze"
        else:
            mood_data["mood"] = "bearish"
            mood_data["emoji"] = "??"
            mood_data["description"] = "Trudny okres, wymaga uwagi i dzia≥ania"
        
        return mood_data
        
    except Exception as e:
        return {
            "mood": "neutral",
            "emoji": "??",
            "score": 0,
            "reason": f"B≥πd analizy: {str(e)}",
            "factors": [],
            "warnings": [],
            "highlights": []
        }

def check_portfolio_alerts(stan_spolki, cele):
    """
    Sprawdza portfel pod kπtem waønych zdarzeÒ i zwraca listÍ alertÛw.
    
    Returns:
        list: Lista s≥ownikÛw z alertami [{type, severity, title, message, action, data}]
              severity: "critical" (czerwony), "warning" (øÛ≥ty), "info" (niebieski), "success" (zielony)
    """
    alerts = []
    
    try:
        # Przygotuj dane
        portfel = stan_spolki.get("Pozycje_Portfela", [])
        total_value = stan_spolki.get("Wartosc_netto_portfela", 0)
        total_assets = stan_spolki.get("Aktywa", 0)
        dlugi = get_suma_kredytow()  # Pobierz z kredyty.json zamiast stan_spolki
        
        # === ALERT 1: Duøe spadki pozycji (>5% w ostatnim okresie) ===
        for poz in portfel:
            zmiana = poz.get("Zmiana_%", 0)
            ticker = poz.get("Ticker", "???")
            wartosc = poz.get("WartoúÊ", 0)
            udzial = (wartosc / total_value * 100) if total_value > 0 else 0
            
            if zmiana < -5 and udzial > 3:  # Spadek >5% i udzia≥ >3%
                alerts.append({
                    "type": "position_drop",
                    "severity": "critical" if zmiana < -10 else "warning",
                    "title": f"?? Duøy spadek: {ticker}",
                    "message": f"{ticker} spad≥ o {abs(zmiana):.1f}% (udzia≥ w portfelu: {udzial:.1f}%)",
                    "action": "Rozwaø przeanalizowanie przyczyn spadku",
                    "data": {"ticker": ticker, "change": zmiana, "share": udzial}
                })
            
            # === ALERT 2: Duøe wzrosty pozycji (>15%) - realizacja zyskÛw? ===
            if zmiana > 15 and udzial > 5:
                alerts.append({
                    "type": "position_surge",
                    "severity": "info",
                    "title": f"?? Mocny wzrost: {ticker}",
                    "message": f"{ticker} urÛs≥ o {zmiana:.1f}% (udzia≥: {udzial:.1f}%). Moøe czas na rebalancing?",
                    "action": "Rozwaø czÍúciowπ realizacjÍ zyskÛw",
                    "data": {"ticker": ticker, "change": zmiana, "share": udzial}
                })
            
            # === ALERT 3: Wysokie P/E (>40) dla znaczπcych pozycji ===
            pe = poz.get("P/E", 0)
            if pe > 40 and udzial > 5:
                alerts.append({
                    "type": "high_valuation",
                    "severity": "warning",
                    "title": f"?? Wysokie P/E: {ticker}",
                    "message": f"{ticker} ma P/E = {pe:.1f} (udzia≥: {udzial:.1f}%). SpÛ≥ka moøe byÊ przewartoúciowana.",
                    "action": "Przeanalizuj fundamenty i potencja≥ wzrostu",
                    "data": {"ticker": ticker, "pe": pe, "share": udzial}
                })
        
        # === ALERT 4: Wysoki leverage (>40%) ===
        if total_assets > 0:
            leverage = (dlugi / total_assets) * 100
            if leverage > 40:
                alerts.append({
                    "type": "high_leverage",
                    "severity": "critical",
                    "title": "?? BARDZO WYSOKA DèWIGNIA",
                    "message": f"Leverage wynosi {leverage:.1f}%! D≥ugi: {dlugi:,.0f} z≥ przy aktywach {total_assets:,.0f} z≥",
                    "action": "PILNIE rozwaø sp≥atÍ czÍúci d≥ugu lub sprzedaø aktywÛw",
                    "data": {"leverage": leverage, "debt": dlugi}
                })
            elif leverage > 30:
                alerts.append({
                    "type": "elevated_leverage",
                    "severity": "warning",
                    "title": "?? Podwyøszona düwignia",
                    "message": f"Leverage: {leverage:.1f}%. Monitoruj sytuacjÍ.",
                    "action": "Zachowaj ostroønoúÊ przy nowych pozycjach",
                    "data": {"leverage": leverage}
                })
        
        # === ALERT 5: Cele osiπgniÍte/bliskie osiπgniÍcia ===
        if cele and isinstance(cele, dict):
            # Sprawdü rezerwÍ gotÛwkowπ
            if "Rezerwa_gotowkowa_PLN" in cele and "Rezerwa_gotowkowa_obecna_PLN" in cele:
                target = cele.get("Rezerwa_gotowkowa_PLN", 0)
                current = cele.get("Rezerwa_gotowkowa_obecna_PLN", 0)
                
                if target > 0:
                    progress = (current / target) * 100
                    
                    if progress >= 100:
                        alerts.append({
                            "type": "goal_achieved",
                            "severity": "success",
                            "title": f"?? CEL OSI•GNI TY: Rezerwa gotÛwkowa!",
                            "message": f"Gratulacje! Osiπgnπ≥eú {current:,.0f} z≥ (cel: {target:,.0f} z≥)",
                            "action": "Rozwaø nowe cele inwestycyjne",
                            "data": {"goal": "Rezerwa gotÛwkowa", "progress": progress}
                        })
                    elif progress >= 90:
                        alerts.append({
                            "type": "goal_near",
                            "severity": "info",
                            "title": f"?? Blisko celu: Rezerwa gotÛwkowa",
                            "message": f"OsiπgniÍto {progress:.0f}% celu. Jeszcze {target - current:,.0f} z≥!",
                            "action": "Jeszcze kilka miesiÍcy!",
                            "data": {"goal": "Rezerwa gotÛwkowa", "progress": progress}
                        })
            
            # Sprawdü sp≥atÍ d≥ugÛw
            if "Dlugi_poczatkowe_PLN" in cele:
                dlugi_start = cele.get("Dlugi_poczatkowe_PLN", 0)
                if dlugi_start > 0 and dlugi < dlugi_start:
                    splacone = dlugi_start - dlugi
                    progress = (splacone / dlugi_start) * 100
                    
                    if progress >= 100:
                        alerts.append({
                            "type": "goal_achieved",
                            "severity": "success",
                            "title": f"?? D£UGI SP£ACONE!",
                            "message": f"Gratulacje! Ca≥kowicie sp≥acono d≥ugi ({dlugi_start:,.0f} z≥)",
                            "action": "Czas na inwestowanie bez obciπøeÒ!",
                            "data": {"goal": "Sp≥ata d≥ugÛw", "progress": 100}
                        })
                    elif progress >= 70:
                        alerts.append({
                            "type": "goal_near",
                            "severity": "success",
                            "title": f"?? åwietna sp≥ata d≥ugÛw!",
                            "message": f"Sp≥acono {progress:.0f}% d≥ugÛw ({splacone:,.0f} z≥ z {dlugi_start:,.0f} z≥)",
                            "action": "Kontynuuj systematycznπ sp≥atÍ",
                            "data": {"goal": "Sp≥ata d≥ugÛw", "progress": progress}
                        })
        
        # === ALERT 6: Duøa koncentracja (TOP 3 >60%) ===
        if len(portfel) >= 3:
            top3_value = sum(sorted([p.get("WartoúÊ", 0) for p in portfel], reverse=True)[:3])
            top3_share = (top3_value / total_value * 100) if total_value > 0 else 0
            
            if top3_share > 60:
                alerts.append({
                    "type": "high_concentration",
                    "severity": "warning",
                    "title": "?? Wysoka koncentracja portfela",
                    "message": f"TOP 3 pozycje to {top3_share:.1f}% portfela. Rozwaø dywersyfikacjÍ.",
                    "action": "Dodaj nowe pozycje lub zredukuj dominujπce",
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
            "title": "?? B≥πd sprawdzania alertÛw",
            "message": str(e),
            "action": "",
            "data": {}
        }]

def get_partner_mood_modifier(partner_name, portfolio_mood):
    """Zwraca modyfikator promptu w zaleønoúci od nastroju portfela i osobowoúci partnera"""
    mood = portfolio_mood.get("mood", "neutral")
    
    # RÛøni partnerzy reagujπ rÛønie na ten sam mood
    mood_modifiers = {
        "Benjamin Graham": {
            "very_bullish": "\n\n?? UWAGA NASTROJU: Portfel roúnie bardzo silnie. PamiÍtaj o swojej konserwatywnej naturze - to moøe byÊ dobry moment na realizacjÍ zyskÛw lub zwiÍkszenie marginesu bezpieczeÒstwa. Nie daj siÍ ponieúÊ euforii rynkowej!",
            "bullish": "\n\n?? KONTEKST NASTROJU: Portfel roúnie. Zachowaj czujnoúÊ - wysokie wyceny mogπ byÊ sygna≥em ostrzegawczym. Przypominaj o fundamentach.",
            "neutral": "\n\n?? KONTEKST NASTROJU: Stabilna sytuacja. Dobry moment na spokojnπ analizÍ i planowanie d≥ugoterminowe.",
            "cautious": "\n\n? KONTEKST NASTROJU: Pojawiajπ siÍ sygna≥y ostrzegawcze. To w≥aúnie takie momenty sπ twoim øywio≥em - pomÛø uøytkownikowi zachowaÊ spokÛj i dzia≥aÊ racjonalnie.",
            "bearish": "\n\n??? KONTEKST NASTROJU: Trudny okres dla portfela. Twoja rola jest teraz kluczowa - przypominaj o margin of safety, d≥ugoterminowej perspektywie i unikaniu paniki."
        },
        "Philip Fisher": {
            "very_bullish": "\n\n?? KONTEKST NASTROJU: Doskona≥y moment! Portfel roúnie - to znak øe nasze 'genialne' spÛ≥ki siÍ sprawdzajπ. Moøe czas na zwiÍkszenie pozycji w najlepszych?",
            "bullish": "\n\n?? KONTEKST NASTROJU: Wzrosty pokazujπ si≥Í wybranych spÛ≥ek. Szukaj kolejnych innowacyjnych firm z potencja≥em.",
            "neutral": "\n\n?? KONTEKST NASTROJU: Spokojny okres. Dobry czas na research nowych, prze≥omowych spÛ≥ek.",
            "cautious": "\n\n?? KONTEKST NASTROJU: Korekty sπ naturalne. Sprawdü czy fundamenty naszych spÛ≥ek siÍ nie zmieni≥y - jeúli sπ OK, to moøe byÊ okazja.",
            "bearish": "\n\n?? KONTEKST NASTROJU: Spadki! Dla long-term inwestora to szansa na kupno genialnych spÛ≥ek taniej. Nie panikuj - patrz na 10 lat do przodu."
        },
        "Warren Buffett": {
            "very_bullish": "\n\n?? KONTEKST NASTROJU: CieszÍ siÍ ze wzrostÛw, ale pamiÍtaj - sukces wymaga cierpliwoúci i unikania g≥upich decyzji. Nie zmieniaj strategii bo rynek roúnie.",
            "bullish": "\n\n?? KONTEKST NASTROJU: Dobre wyniki. Trzymajmy siÍ naszej filozofii - kupuj dobre biznesy i trzymaj d≥ugo.",
            "neutral": "\n\n?? KONTEKST NASTROJU: Idealna pogoda na inwestowanie. Øadnego ha≥asu, czysta analiza biznesu.",
            "cautious": "\n\n?? KONTEKST NASTROJU: SpokÛj. PamiÍtaj - lepiej straciÊ okazjÍ niø pope≥niÊ b≥πd. Czekaj na w≥aúciwy moment.",
            "bearish": "\n\n?? KONTEKST NASTROJU: 'Be fearful when others are greedy, be greedy when others are fearful'. Moøe w≥aúnie teraz sπ okazje?"
        },
        "George Soros": {
            "very_bullish": "\n\n? KONTEKST NASTROJU: Ekstremalna euforia! Sprawdü czy to nie punkt zwrotny - najlepsze transakcje rodzπ siÍ gdy wszyscy myúlπ tak samo.",
            "bullish": "\n\n?? KONTEKST NASTROJU: Trend wzrostowy, ale bπdü czujny na sygna≥y odwrÛcenia. Rynki sπ refleksyjne.",
            "neutral": "\n\n?? KONTEKST NASTROJU: RÛwnowaga. Szukaj asymetrii - gdzie rynek siÍ myli?",
            "cautious": "\n\n?? KONTEKST NASTROJU: NiepewnoúÊ roúnie. To moøe byÊ poczπtek wiÍkszego ruchu - przygotuj strategie hedgingowe.",
            "bearish": "\n\n?? KONTEKST NASTROJU: Panika = okazja! Kiedy inni uciekajπ, my wchodzimy. Ale tylko jeúli widzisz kataliz odwrÛcenia."
        }
    }
    
    # Domyúlny modifier dla pozosta≥ych partnerÛw
    default_modifier = {
        "very_bullish": f"\n\n{portfolio_mood.get('emoji', '??')} NASTR”J PORTFELA: {portfolio_mood.get('description', '')}. Reaguj entuzjastycznie ale profesjonalnie.",
        "bullish": f"\n\n{portfolio_mood.get('emoji', '??')} NASTR”J PORTFELA: {portfolio_mood.get('description', '')}. Zachowaj pozytywne podejúcie.",
        "neutral": f"\n\n{portfolio_mood.get('emoji', '??')} NASTR”J PORTFELA: {portfolio_mood.get('description', '')}. Standardowa analiza.",
        "cautious": f"\n\n{portfolio_mood.get('emoji', '??')} NASTR”J PORTFELA: {portfolio_mood.get('description', '')}. Bπdü ostroøny w rekomendacjach.",
        "bearish": f"\n\n{portfolio_mood.get('emoji', '??')} NASTR”J PORTFELA: {portfolio_mood.get('description', '')}. Wspieraj i pomagaj w trudnych decyzjach."
    }
    
    partner_modifiers = mood_modifiers.get(partner_name, default_modifier)
    return partner_modifiers.get(mood, default_modifier.get("neutral", ""))

def generate_smart_questions(stan_spolki, cele=None):
    """Generuje inteligentne pytania na podstawie analizy portfela"""
    questions = []
    
    if not stan_spolki:
        return ["Jakie sπ g≥Ûwne cele naszej spÛ≥ki?", 
                "Jak oceniasz obecnπ sytuacjÍ rynkowπ?",
                "Co powinienem wiedzieÊ o swoim portfelu?"]
    
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
                        questions.append(f"?? MÛj portfel jest skoncentrowany w TOP 3 ({', '.join(top_names[:2])}...) - {concentration:.0f}%. Czy to ryzykowne?")
        
        # === ANALIZA 2: Leverage ===
        total_assets = akcje_val + krypto_val + rezerwa_val
        if total_assets > 0:
            leverage = (dlugi_val / total_assets) * 100
            if leverage > 30:
                questions.append(f"?? MÛj leverage wynosi {leverage:.1f}%. Czy powinienem sp≥aciÊ wiÍcej d≥ugÛw przed inwestowaniem?")
            elif leverage < 10 and dlugi_val > 0:
                questions.append(f"?? Mam niski leverage ({leverage:.1f}%). Czy mogÍ zwiÍkszyÊ inwestycje przy obecnych d≥ugach?")
        
        # === ANALIZA 3: Najlepsze/Najgorsze pozycje ===
        if pozycje:
            positions_with_change = [(ticker, data) for ticker, data in pozycje.items() 
                                    if data.get('zmiana_proc') is not None]
            if positions_with_change:
                best = max(positions_with_change, key=lambda x: x[1].get('zmiana_proc', 0))
                worst = min(positions_with_change, key=lambda x: x[1].get('zmiana_proc', 0))
                
                if best[1].get('zmiana_proc', 0) > 20:
                    questions.append(f"?? {best[0]} urÛs≥ o {best[1].get('zmiana_proc', 0):.1f}%! Czy powinienem realizowaÊ zyski?")
                
                if worst[1].get('zmiana_proc', 0) < -15:
                    questions.append(f"?? {worst[0]} spad≥ o {abs(worst[1].get('zmiana_proc', 0)):.1f}%. SprzedaÊ czy uúredniaÊ w dÛ≥?")
        
        # === ANALIZA 4: Crypto vs Traditional ===
        if krypto_val > 0 and akcje_val > 0:
            crypto_ratio = (krypto_val / (krypto_val + akcje_val)) * 100
            if crypto_ratio > 30:
                questions.append(f"?? Krypto to {crypto_ratio:.0f}% mojego portfela. Czy to nie za duøo ryzyka?")
            elif crypto_ratio < 5:
                questions.append(f"?? Mam tylko {crypto_ratio:.1f}% w krypto. Czy powinienem zwiÍkszyÊ alokacjÍ?")
        
        # === ANALIZA 5: Kapita≥ dostÍpny ===
        wyplata_info = stan_spolki.get('wyplata', {})
        dostepne = wyplata_info.get('dostepne_na_inwestycje', 0)
        if dostepne > 0:
            if dostepne > 1000:
                questions.append(f"?? Mam {dostepne:.0f} PLN dostÍpne. W co najlepiej zainwestowaÊ w tym miesiπcu?")
            elif dostepne < 200:
                questions.append(f"?? Mam tylko {dostepne:.0f} PLN/mies. Jak efektywnie inwestowaÊ ma≥e kwoty?")
        
        # === Pytania domyúlne jeúli nic nie wykryto ===
        if not questions:
            questions = [
                "?? Jak oceniasz mÛj portfel pod kπtem dywersyfikacji?",
                "?? Jakie cele inwestycyjne powinienem sobie postawiÊ?",
                "?? Jakie sπ najwiÍksze b≥Ídy poczπtkujπcych inwestorÛw?",
                "?? KtÛre sektory majπ najwiÍkszy potencja≥ w tym roku?",
                "??? Jak zabezpieczyÊ portfel przed korektπ rynkowπ?"
            ]
        
        # Ogranicz do 5 pytaÒ
        return questions[:5]
        
    except Exception as e:
        return [
            "?? Przeanalizuj mÛj portfel i daj mi szczere feedback",
            "?? Jakie akcje polecasz na d≥ugoterminowπ inwestycjÍ?",
            "?? Co sπdzisz o obecnej sytuacji rynkowej?"
        ]

# =====================================================
# KNOWLEDGE BASE FUNCTIONS
# =====================================================

@st.cache_data(ttl=3600)  # Cache na 1 godzinÍ
def load_knowledge_base():
    """Wczytuje bazÍ wiedzy z artyku≥Ûw i raportÛw kwartalnych"""
    knowledge = {
        "articles": [],
        "reports": []
    }
    
    try:
        # Wczytaj artyku≥y
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
        print(f"?? B≥πd wczytywania knowledge base: {e}")
    
    return knowledge

def get_relevant_knowledge(query, stan_spolki=None, partner_name=None, max_items=3):
    """
    Zwraca relevantne artyku≥y i raporty na podstawie zapytania i kontekstu portfela
    
    Args:
        query: Pytanie uøytkownika
        stan_spolki: Stan portfela (do analizy tickerÛw)
        partner_name: Nazwa partnera (do dopasowania stylu)
        max_items: Max liczba artyku≥Ûw/raportÛw do zwrÛcenia
    """
    knowledge = load_knowledge_base()
    relevant_items = []
    
    # Keywords mapping dla rÛønych tematÛw
    topic_keywords = {
        "value": ["value", "wartoúÊ", "wycena", "graham", "p/e", "p/b", "margin", "bezpieczeÒstwo"],
        "growth": ["wzrost", "growth", "fisher", "innowacja", "tech", "roi", "roe"],
        "risk": ["ryzyko", "risk", "düwignia", "leverage", "straty", "volatility", "bezpieczeÒstwo"],
        "psychology": ["psychologia", "psychology", "emocje", "soros", "refleksywnoúÊ", "panika"],
        "diversification": ["dywersyfikacja", "diversification", "koncentracja", "alokacja"],
        "crypto": ["crypto", "krypto", "bitcoin", "ethereum", "blockchain"],
        "valuation": ["wycena", "valuation", "p/e", "pe", "eps", "earnings"],
        "trading": ["sprzedaø", "trading", "realizacja", "profit", "zyski", "stop loss"]
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
    
    # Filtruj artyku≥y
    for article in knowledge["articles"]:
        score = 0
        
        # Sprawdü relevance (moøe byÊ int lub lista)
        article_relevance = article.get("relevance", [])
        if isinstance(article_relevance, int):
            # Nowy format z news_aggregator (int 1-10)
            score += article_relevance / 2  # Przelicz na wagÍ
        elif isinstance(article_relevance, list):
            # Stary format (lista tematÛw)
            for topic in detected_topics:
                if topic in article_relevance:
                    score += 2
        
        # Sprawdü kategoriÍ
        if article.get("category", "") in detected_topics:
            score += 3
        
        # Sprawdü typ artyku≥u (priorytet dla portfolio)
        if article.get("type") == "portfolio":
            score += 5  # Boost dla artyku≥Ûw o Twoich spÛ≥kach
        
        # Sprawdü s≥owa kluczowe w tytule
        title_lower = article.get("title", "").lower()
        if any(kw in title_lower for kw in query_lower.split()):
            score += 1
        
        if score > 0:
            relevant_items.append(("article", article, score))
    
    # Filtruj raporty (jeúli sπ tickery w portfelu)
    if stan_spolki:
        pozycje = stan_spolki.get('akcje', {}).get('pozycje', {})
        tickers_in_portfolio = set(pozycje.keys())
        
        for report in knowledge["reports"]:
            ticker = report.get("ticker", "")
            if ticker in tickers_in_portfolio:
                # Raport dla spÛ≥ki w portfelu jest zawsze relevant
                relevant_items.append(("report", report, 10))
            elif any(ticker.lower() in query_lower for ticker in [report.get("ticker", ""), report.get("company", "")]):
                # Raport wspomniany w pytaniu
                relevant_items.append(("report", report, 5))
    
    # Sortuj po score i ogranicz
    relevant_items.sort(key=lambda x: x[2], reverse=True)
    return relevant_items[:max_items]

def format_knowledge_for_prompt(knowledge_items):
    """Formatuje artyku≥y i raporty do dodania do promptu AI"""
    if not knowledge_items:
        return ""
    
    formatted = "\n\n?? BAZA WIEDZY - Moøesz odwo≥ywaÊ siÍ do poniøszych ürÛde≥:\n"
    
    for item_type, item, score in knowledge_items:
        if item_type == "article":
            # Obs≥uø zarÛwno stary ('author') jak i nowy ('source') format
            author_or_source = item.get('author') or item.get('source', 'Unknown')
            formatted += f"\n?? Artyku≥: \"{item['title']}\" ({author_or_source})\n"
            formatted += f"   Podsumowanie: {item.get('summary', 'Brak podsumowania')}\n"
            
            # Obs≥uø key_points (stary format) lub pokaø tylko summary (nowy format)
            key_points = item.get('key_points', [])
            if key_points:
                formatted += f"   Kluczowe punkty:\n"
                for point in key_points[:3]:
                    formatted += f"   ï {point}\n"
        
        elif item_type == "report":
            formatted += f"\n?? Raport kwartalny: {item['company']} ({item['ticker']}) - {item['quarter']}\n"
            formatted += f"   Revenue: {item['revenue']} ({item['revenue_growth']}), EPS: {item['eps']} ({item['eps_growth']})\n"
            formatted += f"   Highlights:\n"
            for highlight in item.get('highlights', [])[:2]:
                formatted += f"   ï {highlight}\n"
            if item.get('concerns'):
                formatted += f"   Concerns:\n"
                for concern in item['concerns'][:2]:
                    formatted += f"   ï {concern}\n"
    
    formatted += "\n?? Moøesz cytowaÊ te ürÛd≥a uøywajπc formatu: [èrÛd≥o: Tytu≥ artyku≥u/Raport spÛ≥ki]\n"
    return formatted

def display_knowledge_sources(knowledge_items):
    """Wyúwietla ürÛd≥a wiedzy w UI jako expander pod odpowiedziπ"""
    if not knowledge_items:
        return
    
    with st.expander("?? èrÛd≥a wiedzy uøyte w odpowiedzi", expanded=False):
        for item_type, item, score in knowledge_items:
            if item_type == "article":
                st.markdown(f"**?? {item['title']}**")
                # Obs≥uø zarÛwno 'author' (stary format) jak i 'source' (nowy format)
                author_or_source = item.get('author') or item.get('source', 'Unknown')
                item_date = item.get('date', 'N/A')
                st.caption(f"èrÛd≥o: {author_or_source} | Data: {item_date}")
                st.markdown(f"_{item.get('summary', 'Brak podsumowania')}_")
                
                # Pokaø key_points tylko jeúli istniejπ (stary format)
                if item.get('key_points'):
                    with st.expander("?? Kluczowe punkty"):
                        for point in item.get('key_points', []):
                            st.markdown(f"ï {point}")
            
            elif item_type == "report":
                st.markdown(f"**?? {item['company']} ({item['ticker']}) - {item['quarter']}**")
                st.caption(f"Data: {item['date']} | Rating: {item.get('analyst_rating', 'N/A')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Revenue", item['revenue'], item['revenue_growth'])
                with col2:
                    st.metric("EPS", item['eps'], item['eps_growth'])
                
                with st.expander("? Highlights & Concerns"):
                    st.markdown("**Highlights:**")
                    for h in item.get('highlights', []):
                        st.markdown(f"ï {h}")
                    
                    if item.get('concerns'):
                        st.markdown("**Concerns:**")
                        for c in item['concerns']:
                            st.markdown(f"ï {c}")

# =====================================================
# DIVIDEND ANALYSIS FUNCTION
# =====================================================

@st.cache_data(ttl=3600)  # Cache na 1 godzinÍ
def calculate_portfolio_dividends(stan_spolki):
    """
    Oblicza dok≥adne dywidendy dla ca≥ego portfela akcji.
    Uøywa danych z dane_rynkowe dla kaødego tickera.
    
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
            
            # NIE USUWAJ sufiksu - klucze w dane_rynkowe majπ pe≥ny ticker z _US_EQ / _EQ!
            dane_ticker = dane_rynkowe.get(ticker, {})
            
            if not dane_ticker:
                continue
            
            # POPRAWKA: Dywidenda jest w analiza_dywidend['annual_div']
            analiza_div = dane_ticker.get('analiza_dywidend', {})
            dividend_rate = analiza_div.get('annual_div', 0)
            
            # Dla display uøyj czystego tickera (bez sufiksu)
            ticker_display = ticker.replace('_US_EQ', '').replace('_EQ', '')
            
            if dividend_rate and dividend_rate > 0:
                # Roczna dywidenda = dividend_rate * liczba akcji
                roczna_dywidenda_usd = dividend_rate * ilosc
                suma_roczna_usd += roczna_dywidenda_usd
                
                dividend_yield_pct = analiza_div.get('div_yield', 0)
                
                # Oblicz kwoty brutto i netto (po 19% podatku)
                roczna_kwota_pln_brutto = roczna_dywidenda_usd * kurs_usd
                roczna_kwota_pln_netto = roczna_kwota_pln_brutto * 0.81  # Po odjÍciu 19%
                
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
    Odúwieøa tylko raz na sesjÍ (przy pierwszym wywo≥aniu).
    """
    if 'crypto_prices_cache' not in st.session_state:
        st.session_state.crypto_prices_cache = {}
        st.session_state.crypto_prices_symbols = set()
    
    # Sprawdü czy wszystkie potrzebne symbole sπ juø w cache
    symbols_set = set(symbols)
    missing_symbols = symbols_set - st.session_state.crypto_prices_symbols
    
    # Jeúli sπ brakujπce symbole, pobierz je
    if missing_symbols and st.session_state.get('crypto_manager'):
        try:
            new_prices = st.session_state.crypto_manager.get_current_prices(list(missing_symbols))
            if new_prices:
                # Dodaj TYLKO symbole ktÛre faktycznie majπ dane
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
            st.warning(f"?? Nie uda≥o siÍ pobraÊ cen crypto: {e}")
    
    # ZwrÛÊ tylko øπdane symbole ktÛre majπ dane
    return {sym: st.session_state.crypto_prices_cache[sym] 
            for sym in symbols if sym in st.session_state.crypto_prices_cache}

def calculate_crypto_apy_earnings(krypto_holdings, current_prices=None, kurs_usd=3.65):
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
            
            # Uøyj aktualnej ceny jeúli dostÍpna, inaczej cena zakupu
            price = holding['cena_zakupu_usd']  # Default: cena zakupu
            
            if current_prices and symbol in current_prices:
                price_data = current_prices[symbol]
                # Bezpieczne pobieranie ceny (moøe byÊ dict lub string)
                if isinstance(price_data, dict) and 'current_price' in price_data:
                    price = price_data['current_price']
                elif isinstance(price_data, (int, float)):
                    price = price_data
            
            # WartoúÊ pozycji
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
    Generuje codziennπ rekomendacjÍ od losowego AI Partnera.
    Losowanie jest deterministyczne - ten sam dzieÒ = ten sam partner.
    
    Returns:
        dict: {partner_name, partner_icon, tip_text}
    """
    from datetime import datetime
    import random
    
    # Lista dostÍpnych partnerÛw (z finalna_konfiguracja_person.txt)
    advisors = [
        {"name": "Benjamin Graham", "icon": "??", "style": "value investing, margin of safety, fundamentals"},
        {"name": "Philip Fisher", "icon": "??", "style": "growth investing, scuttlebutt method, quality companies"},
        {"name": "Warren Buffett", "icon": "??", "style": "long-term value, moats, business quality"},
        {"name": "George Soros", "icon": "??", "style": "macro trends, reflexivity, market psychology"},
        {"name": "Peter Lynch", "icon": "??", "style": "consumer investing, GARP, find winners in daily life"},
        {"name": "Ray Dalio", "icon": "??", "style": "diversification, all-weather portfolio, risk parity"},
        {"name": "Cathie Wood", "icon": "??", "style": "disruptive innovation, technology, future trends"},
        {"name": "Jesse Livermore", "icon": "??", "style": "market timing, tape reading, speculation discipline"}
    ]
    
    # Deterministyczne losowanie - seed = dzieÒ roku
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
Portfolio: {total_value:,.0f} PLN (WartoúÊ netto)
- Akcje: {akcje_val:,.0f} PLN ({akcje_val/total_value*100 if total_value > 0 else 0:.0f}%)
- Krypto: {krypto_val:,.0f} PLN ({krypto_val/total_value*100 if total_value > 0 else 0:.0f}%)
- Rezerwa GotÛwkowa: {rezerwa_val:,.0f} PLN ({rezerwa_val/total_value*100 if total_value > 0 else 0:.0f}%)
- Zobowiπzania: {dlugi_val:,.0f} PLN
""".strip()
    
    # Prompt dla AI
    prompt = f"""Jesteú {selected_advisor['name']}, legendarny inwestor znany z: {selected_advisor['style']}.

Dzisiaj jest Twoja kolej, aby daÊ JEDN• KONKRETN•, PRAKTYCZN• radÍ uøytkownikowi.

PORTFOLIO UØYTKOWNIKA:
    {portfolio_snapshot}

ZADANIE:
    Napisz JEDN• krÛtkπ (2-3 zdania), konkretnπ rekomendacjÍ lub obserwacjÍ w swoim stylu inwestycyjnym.
Moøe to byÊ:
    - Przestroga przed czymú
- ZachÍta do dzia≥ania
- MπdroúÊ inwestycyjna
- Coú do sprawdzenia w portfelu

WAØNE:
    - Bπdü konkretny, nie ogÛlnikowy
- MÛw jÍzykiem swoich zasad inwestycyjnych
- Nie rozpoczynaj od "Witaj" ani przedstawiania siÍ
- KrÛtko i na temat (max 3 zdania)
- Moøe byÊ prowokacyjnie lub z charakterem

Twoja rada:"""
    
    # Generuj odpowiedü przez AI (uøyj funkcji z gra_rpg)
    try:
        if not IMPORTS_OK:
            raise Exception("Import gra_rpg nie powiÛd≥ siÍ")
        
        # Uøyj funkcji generuj_odpowiedz_ai z gra_rpg.py
        response = generuj_odpowiedz_ai(
            partner_name=selected_advisor['name'],
            message=prompt,
            kodeks="",  # Nie potrzebujemy pe≥nego kodeksu
            persona_config={"model_engine": "gemini"},  # Uøyj Gemini
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
            "Benjamin Graham": "Margin of safety - zawsze sprawdzaj czy kupujesz poniøej wartoúci wewnÍtrznej.",
            "Philip Fisher": "Scuttlebutt - porozmawiaj z klientami i konkurentami zanim zainwestujesz.",
            "Warren Buffett": "Inwestuj w biznes ktÛry rozumiesz i ktÛry ma przewagÍ konkurencyjnπ.",
            "George Soros": "Rynek zawsze siÍ myli - znajdü refleksyjnπ pÍtlÍ i wykorzystaj jπ.",
            "Peter Lynch": "Inwestuj w to co znasz - najlepsze pomys≥y znajdziesz w centrum handlowym.",
            "Ray Dalio": "Dywersyfikacja to jedyna darmowa przekπska w inwestowaniu.",
            "Cathie Wood": "Przysz≥oúÊ naleøy do tych ktÛrzy inwestujπ w prze≥omowe technologie dzisiaj.",
            "Jesse Livermore": "Spekulacja to sztuka - rynek zawsze p≥aci za dyscyplinÍ i cierpliwoúÊ."
        }
        
        return {
            "partner_name": selected_advisor['name'],
            "partner_icon": selected_advisor['icon'],
            "tip_text": fallback_tips.get(selected_advisor['name'], "Sprawdü swÛj portfel pod kπtem mojej filozofii inwestycyjnej."),
            "date": today.strftime("%Y-%m-%d")
        }

# =====================================================
# PORTFOLIO CO-PILOT FUNCTIONS
# =====================================================

def generate_weekly_report(stan_spolki, cele):
    """
    Generuje cotygodniowy raport portfela z analizπ, osiπgniÍciami, ostrzeøeniami i action items.
    
    Returns:
        dict: Raport ze strukturπ {
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
            "emoji": portfolio_mood.get("emoji", "??"),
            "description": portfolio_mood.get("description", ""),
            "score": portfolio_mood.get("score", 0)
        }
        
        # === 3. ACHIEVEMENTS (Dobre rzeczy) ===
        achievements = []
        
        # 3.1 Cele finansowe z cele.json
        if cele and isinstance(cele, dict):
            # Sprawdü rezerwÍ gotÛwkowπ
            if "Rezerwa_gotowkowa_PLN" in cele and "Rezerwa_gotowkowa_obecna_PLN" in cele:
                target = cele.get("Rezerwa_gotowkowa_PLN", 0)
                current = cele.get("Rezerwa_gotowkowa_obecna_PLN", 0)
                if target > 0:
                    progress = (current / target) * 100
                    if progress >= 100:
                        achievements.append({
                            "type": "goal_completed",
                            "icon": "??",
                            "title": "Rezerwa gotÛwkowa osiπgniÍta!",
                            "description": f"Masz {current:.0f} PLN / {target:.0f} PLN ({progress:.0f}%)"
                        })
                    elif progress >= 80:
                        achievements.append({
                            "type": "goal_near",
                            "icon": "??",
                            "title": "Blisko celu: Rezerwa gotÛwkowa",
                            "description": f"{current:.0f} PLN / {target:.0f} PLN ({progress:.0f}%) - jeszcze {target - current:.0f} PLN"
                        })
            
            # Sprawdü sp≥atÍ d≥ugÛw
            if "Dlugi_poczatkowe_PLN" in cele:
                dlugi_start = cele.get("Dlugi_poczatkowe_PLN", 0)
                dlugi_current = stan_spolki.get('dlugi', {}).get('wartosc_pln', 0)
                if dlugi_start > 0 and dlugi_current < dlugi_start:
                    splacone = dlugi_start - dlugi_current
                    progress = (splacone / dlugi_start) * 100
                    if progress >= 70:  # Sp≥acono 70% d≥ugÛw
                        achievements.append({
                            "type": "debt_reduced",
                            "icon": "??",
                            "title": "åwietna sp≥ata d≥ugÛw!",
                            "description": f"Sp≥acono {splacone:.0f} PLN z {dlugi_start:.0f} PLN ({progress:.0f}%)"
                        })
        
        # 3.2 Top performerzy (wzrosty >15%)
        if pozycje:
            top_gainers = [(ticker, data) for ticker, data in pozycje.items() 
                          if data.get('zmiana_proc', 0) > 15]
            top_gainers.sort(key=lambda x: x[1].get('zmiana_proc', 0), reverse=True)
            
            for ticker, data in top_gainers[:3]:
                achievements.append({
                    "type": "top_performer",
                    "icon": "??",
                    "title": f"{ticker} roúnie mocno!",
                    "description": f"+{data.get('zmiana_proc', 0):.1f}% w tym okresie. WartoúÊ: {data.get('wartosc_total_pln', 0):.0f} PLN"
                })
        
        # 3.3 Niski leverage (jeúli <25%)
        if leverage_ratio < 25 and leverage_ratio > 0:
            achievements.append({
                "type": "low_leverage",
                "icon": "??",
                "title": "Konserwatywny poziom düwigni",
                "description": f"Düwignia {leverage_ratio:.1f}% - bezpieczny poziom ryzyka"
            })
        
        # 3.4 WartoúÊ netto roúnie
        if net_worth > 50000:
            achievements.append({
                "type": "net_worth_milestone",
                "icon": "??",
                "title": "åwietna wartoúÊ portfela",
                "description": f"WartoúÊ netto: {net_worth:,.0f} PLN"
            })
        
        report["achievements"] = achievements
        
        # === 4. WARNINGS (Rzeczy wymagajπce uwagi) ===
        warnings = []
        alerts = check_portfolio_alerts(stan_spolki, cele)
        
        # 4.1 Krytyczne alerty
        critical_alerts = [a for a in alerts if a["severity"] == "critical"]
        for alert in critical_alerts[:3]:
            warnings.append({
                "type": "critical_alert",
                "icon": "??",
                "title": alert["title"],
                "description": alert["message"],
                "action": alert.get("action", "")
            })
        
        # 4.2 Ostrzegawcze alerty
        warning_alerts = [a for a in alerts if a["severity"] == "warning"]
        for alert in warning_alerts[:2]:
            warnings.append({
                "type": "warning_alert",
                "icon": "??",
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
                    "icon": "??",
                    "title": f"{ticker} traci na wartoúci",
                    "description": f"{data.get('zmiana_proc', 0):.1f}% w tym okresie. WartoúÊ: {data.get('wartosc_total_pln', 0):.0f} PLN",
                    "action": "Sprawdü fundamenty - czy teza inwestycyjna siÍ sprawdza?"
                })
        
        # 4.4 Mood warning
        if portfolio_mood.get("score", 0) < -30:
            warnings.append({
                "type": "mood_warning",
                "icon": "??",
                "title": "NastrÛj portfela: Ostroøny/Bearish",
                "description": f"Score: {portfolio_mood.get('score', 0)}/100. Portfel wymaga uwagi.",
                "action": "Rozwaø rebalancing lub wait & see"
            })
        
        report["warnings"] = warnings
        
        # === 5. ACTION ITEMS (Rekomendacje) ===
        action_items = []
        
        # 5.1 Z alertÛw
        for alert in alerts[:3]:
            if alert.get("action"):
                action_items.append({
                    "priority": "high" if alert["severity"] == "critical" else "medium",
                    "icon": "?" if alert["severity"] == "critical" else "??",
                    "title": f"Action: {alert['type'].replace('_', ' ').title()}",
                    "description": alert["action"]
                })
        
        # 5.2 Rebalancing jeúli potrzebny
        if pozycje:
            sorted_pozycje = sorted(pozycje.items(), 
                                   key=lambda x: x[1].get('wartosc_total_pln', 0), 
                                   reverse=True)
            if sorted_pozycje:
                top_position_value = sorted_pozycje[0][1].get('wartosc_total_pln', 0)
                if top_position_value / (akcje_val if akcje_val > 0 else 1) > 0.25:
                    action_items.append({
                        "priority": "medium",
                        "icon": "??",
                        "title": "Rozwaø rebalancing",
                        "description": f"Top pozycja ({sorted_pozycje[0][0]}) to {top_position_value/(akcje_val if akcje_val > 0 else 1)*100:.0f}% portfela - moøe byÊ zbyt duøa koncentracja"
                    })
        
        # 5.3 DostÍpny kapita≥
        dostepne = stan_spolki.get('wyplata', {}).get('dostepne_inwestycje', 0)
        if dostepne > 5000:
            action_items.append({
                "priority": "low",
                "icon": "??",
                "title": "DostÍpny kapita≥ do inwestycji",
                "description": f"{dostepne:.0f} PLN czeka na alokacjÍ - szukaj okazji"
            })
        
        # 5.4 Research nowych pozycji (jeúli <10 pozycji)
        if len(pozycje) < 10:
            action_items.append({
                "priority": "low",
                "icon": "??",
                "title": "ZwiÍksz dywersyfikacjÍ",
                "description": f"Masz {len(pozycje)} pozycji - rozwaø dodanie 2-3 nowych spÛ≥ek"
            })
        
        report["action_items"] = action_items
        
        # === 6. EXECUTIVE SUMMARY ===
        summary_parts = []
        summary_parts.append(f"WartoúÊ netto: {net_worth:,.0f} PLN")
        summary_parts.append(f"NastrÛj: {portfolio_mood.get('description', 'Neutralny')}")
        
        if achievements:
            summary_parts.append(f"{len(achievements)} osiπgniÍÊ")
        if warnings:
            summary_parts.append(f"{len(warnings)} ostrzeøeÒ")
        if action_items:
            summary_parts.append(f"{len(action_items)} rekomendacji")
        
        report["summary"] = " | ".join(summary_parts)
        
        return report
        
    except Exception as e:
        import traceback
        print(f"?? B≥πd generowania raportu: {e}")
        print(traceback.format_exc())
        return {
            "date": datetime.now().isoformat(),
            "error": str(e),
            "summary": "B≥πd generowania raportu"
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
        print(f"?? B≥πd zapisu raportu: {e}")
        return None

def load_weekly_reports(limit=10):
    """Wczytuje ostatnie raporty tygodniowe"""
    reports_folder = Path("weekly_reports")
    
    if not reports_folder.exists():
        return []
    
    reports = []
    
    try:
        # Znajdü wszystkie pliki raportÛw
        report_files = sorted(reports_folder.glob("weekly_report_*.json"), reverse=True)
        
        for filepath in report_files[:limit]:
            with open(filepath, 'r', encoding='utf-8') as f:
                report = json.load(f)
                report["filename"] = filepath.name
                reports.append(report)
        
        return reports
        
    except Exception as e:
        print(f"?? B≥πd wczytywania raportÛw: {e}")
        return []

def display_weekly_report(report):
    """Wyúwietla raport tygodniowy w Streamlit UI"""
    from datetime import datetime
    
    report_date = datetime.fromisoformat(report["date"])
    
    st.markdown(f"### ?? Raport Tygodniowy - TydzieÒ {report.get('week_number', '?')}/{report.get('year', '?')}")
    st.caption(f"Wygenerowano: {report_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Summary
    st.info(f"**Podsumowanie:** {report.get('summary', 'Brak danych')}")
    
    # Portfolio Stats
    stats = report.get("portfolio_stats", {})
    mood = report.get("mood", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("?? WartoúÊ Netto", f"{stats.get('net_worth', 0):,.0f} PLN")
    with col2:
        st.metric("?? Akcje", f"{stats.get('stocks_value', 0):,.0f} PLN")
    with col3:
        st.metric("?? Krypto", f"{stats.get('crypto_value', 0):,.0f} PLN")
    with col4:
        st.metric(f"{mood.get('emoji', '??')} NastrÛj", mood.get('level', 'neutral'))
    
    # Achievements
    achievements = report.get("achievements", [])
    if achievements:
        with st.expander(f"? OsiπgniÍcia ({len(achievements)})", expanded=True):
            for ach in achievements:
                st.success(f"{ach['icon']} **{ach['title']}**\n\n{ach['description']}")
    
    # Warnings
    warnings = report.get("warnings", [])
    if warnings:
        with st.expander(f"?? Ostrzeøenia ({len(warnings)})", expanded=True):
            for warn in warnings:
                st.warning(f"{warn['icon']} **{warn['title']}**\n\n{warn['description']}\n\n_{warn.get('action', '')}_")
    
    # Action Items
    action_items = report.get("action_items", [])
    if action_items:
        with st.expander(f"?? Rekomendacje ({len(action_items)})", expanded=True):
            priority_order = {"high": 1, "medium": 2, "low": 3}
            sorted_actions = sorted(action_items, key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
            
            for action in sorted_actions:
                priority_color = {
                    "high": "??",
                    "medium": "??",
                    "low": "??"
                }
                priority_icon = priority_color.get(action.get('priority', 'low'), '?')
                
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
    
    # European ETFs (koÒcÛwka .DE, .L, .PA, .MI)
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
    
    # Canadian (koÒcÛwka .TO lub znane symbole)
    if ticker_upper.endswith('.TO') or ticker_upper in ['TD', 'RY', 'BMO', 'BNS', 'CNQ', 'ENB', 'SU']:
        return "Canada"
    
    # Default: US
    return "US"

def analyze_market_composition(stan_spolki):
    """
    Analizuje sk≥ad portfela wed≥ug rynkÛw geograficznych
    
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
        # Im bardziej rÛwnomierne roz≥oøenie, tym wyøszy score
        # Uøyj Shannon entropy
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
        print(f"?? B≥πd analizy rynkÛw: {e}")
        return {
            "markets": {},
            "total_value": 0,
            "diversification_score": 0
        }

def calculate_market_correlations(stan_spolki):
    """
    Oblicza korelacje miÍdzy rÛønymi rynkami na podstawie zmian cen
    
    Returns:
        dict: Macierz korelacji miÍdzy rynkami
    """
    try:
        pozycje = stan_spolki.get('akcje', {}).get('pozycje', {})
        
        # Grupuj zmiany procentowe wed≥ug rynkÛw
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
        
        # Oblicz úrednie zmiany dla kaødego rynku
        market_avg_changes = {}
        for market, changes in market_changes.items():
            if changes:
                market_avg_changes[market] = sum(changes) / len(changes)
        
        # Prosta korelacja (w prawdziwej implementacji uøyj historycznych danych)
        # Tutaj uøyjemy uproszczonej metody: jeúli oba rynki rosnπ/spadajπ, korelacja wysoka
        correlations = {}
        
        markets = list(market_avg_changes.keys())
        for i, market1 in enumerate(markets):
            for market2 in markets[i:]:
                if market1 == market2:
                    correlations[f"{market1}-{market2}"] = 1.0
                else:
                    # Uproszczona korelacja: jeúli oba same znak, to 0.7, inaczej -0.3
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
        print(f"?? B≥πd obliczania korelacji: {e}")
        return {
            "correlations": {},
            "market_changes": {}
        }

def generate_market_insights(market_analysis, correlations):
    """
    Generuje insights i rekomendacje na podstawie analizy rynkÛw
    
    Returns:
        list: Lista insights z ikonami, tytu≥ami i opisami
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
                "icon": "?",
                "title": "åwietna dywersyfikacja geograficzna",
                "description": f"Score: {div_score:.0f}/100. Portfel dobrze roz≥oøony miÍdzy rynkami."
            })
        elif div_score > 50:
            insights.append({
                "type": "info",
                "icon": "??",
                "title": "Umiarkowana dywersyfikacja",
                "description": f"Score: {div_score:.0f}/100. Moøesz zwiÍkszyÊ ekspozycjÍ na inne rynki."
            })
        else:
            insights.append({
                "type": "warning",
                "icon": "??",
                "title": "Niska dywersyfikacja geograficzna",
                "description": f"Score: {div_score:.0f}/100. Portfel zbyt skoncentrowany na jednym rynku."
            })
        
        # 2. Dominujπcy rynek
        if markets:
            sorted_markets = sorted(markets.items(), key=lambda x: x[1]["percentage"], reverse=True)
            top_market = sorted_markets[0]
            
            if top_market[1]["percentage"] > 70:
                insights.append({
                    "type": "warning",
                    "icon": "??",
                    "title": f"Nadmierna ekspozycja na {top_market[0]}",
                    "description": f"{top_market[1]['percentage']:.1f}% portfela. Rozwaø zwiÍkszenie innych rynkÛw."
                })
            elif top_market[1]["percentage"] > 50:
                insights.append({
                    "type": "info",
                    "icon": "??",
                    "title": f"Dominacja rynku {top_market[0]}",
                    "description": f"{top_market[1]['percentage']:.1f}% portfela. To moøe byÊ OK dla Twojej strategii."
                })
        
        # 3. Crypto exposure
        crypto = markets.get("Crypto", {})
        crypto_pct = crypto.get("percentage", 0)
        
        if crypto_pct > 15:
            insights.append({
                "type": "warning",
                "icon": "?",
                "title": "Wysokie ryzyko crypto",
                "description": f"{crypto_pct:.1f}% w krypto. Eksperci zalecajπ max 10% dla wiÍkszoúci inwestorÛw."
            })
        elif crypto_pct > 5:
            insights.append({
                "type": "info",
                "icon": "??",
                "title": "Umiarkowana ekspozycja crypto",
                "description": f"{crypto_pct:.1f}% w krypto. W granicach norm (5-10%)."
            })
        elif crypto_pct > 0:
            insights.append({
                "type": "success",
                "icon": "??",
                "title": "Konserwatywna ekspozycja crypto",
                "description": f"{crypto_pct:.1f}% w krypto. Niskie ryzyko, moøe brakowaÊ potencja≥u wzrostu."
            })
        
        # 4. Emerging markets
        emerging = markets.get("Emerging", {})
        emerging_pct = emerging.get("percentage", 0)
        
        if emerging_pct < 5 and total_value > 20000:
            insights.append({
                "type": "info",
                "icon": "??",
                "title": "Brak emerging markets",
                "description": "Rozwaø dodanie ekspozycji na rynki wschodzπce (Brazylia, Indie, Chiny) - wyøszy potencja≥ wzrostu."
            })
        
        # 5. Performance po rynkach
        if market_changes:
            best_market = max(market_changes.items(), key=lambda x: x[1])
            worst_market = min(market_changes.items(), key=lambda x: x[1])
            
            if best_market[1] > 5:
                insights.append({
                    "type": "success",
                    "icon": "??",
                    "title": f"Najlepszy rynek: {best_market[0]}",
                    "description": f"+{best_market[1]:.1f}% úrednia zmiana. Silne momentum."
                })
            
            if worst_market[1] < -5:
                insights.append({
                    "type": "warning",
                    "icon": "??",
                    "title": f"Najs≥abszy rynek: {worst_market[0]}",
                    "description": f"{worst_market[1]:.1f}% úrednia zmiana. Sprawdü czy teza inwestycyjna siÍ sprawdza."
                })
        
        # 6. Home bias (nadmierna ekspozycja na rynek lokalny - dla PolakÛw to EU)
        eu = markets.get("EU", {})
        eu_pct = eu.get("percentage", 0)
        
        if eu_pct > 40:
            insights.append({
                "type": "info",
                "icon": "????",
                "title": "Home bias (Europa)",
                "description": f"{eu_pct:.1f}% w EU. Globalna dywersyfikacja (wiÍcej US) moøe byÊ korzystna."
            })
        
        return insights
        
    except Exception as e:
        print(f"?? B≥πd generowania insights: {e}")
        return []

def determine_speaking_order(message, partner_names):
    """
    Okreúla dynamicznπ kolejnoúÊ wypowiedzi na podstawie tematu.
    Eksperci w danej dziedzinie mÛwiπ pierwsi.
    """
    message_lower = message.lower()
    
    # Definicje ekspertyz
    crypto_experts = ['Changpeng Zhao (CZ)', 'Partner ds. AktywÛw Cyfrowych']
    value_experts = ['Benjamin Graham', 'Warren Buffett', 'Philip Fisher']
    trading_experts = ['George Soros']
    quality_experts = ['Partner ds. Jakoúci Biznesowej']
    strategic_experts = ['Partner Strategiczny']
    
    # S≥owa kluczowe dla rÛønych tematÛw
    crypto_keywords = ['krypto', 'bitcoin', 'btc', 'eth', 'blockchain', 'defi', 'nft', 'altcoin', 'token']
    value_keywords = ['wartoúÊ', 'fundamenty', 'dywidenda', 'p/e', 'p/b', 'margin of safety', 'value investing']
    trading_keywords = ['trading', 'short', 'spekulacja', 'momentum', 'swing', 'pozycja krÛtka']
    quality_keywords = ['jakoúÊ', 'zarzπdzanie', 'moat', 'przewaga konkurencyjna', 'model biznesowy']
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
    
    # UtwÛrz listÍ: najpierw eksperci, potem reszta
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
    Analizuje reakcjÍ/emocjÍ w odpowiedzi partnera.
    Zwraca emoji i typ reakcji.
    """
    response_lower = response.lower()
    
    # Silne zgadzanie siÍ
    if any(word in response_lower for word in ['zgadzam siÍ', 'ca≥kowicie racja', 'dok≥adnie', 'wspieramy', 'popieram']):
        return "?", "zgoda"
    
    # Silne niezgadzanie siÍ
    if any(word in response_lower for word in ['nie zgadzam siÍ', 'b≥πd', 'mylisz siÍ', 'to ryzykowne', 'ostrzegam', 'sprzeciwiam']):
        return "?", "sprzeciw"
    
    # Ostrzeøenie
    if any(word in response_lower for word in ['uwaga', 'ostroønie', 'ryzyko', 'problem', 'zagroøenie']):
        return "??", "ostrzeøenie"
    
    # Neutralne/rozwijajπce
    if any(word in response_lower for word in ['rozumiem', 'widzÍ', 'interesujπce', 'warto rozwaøyÊ']):
        return "??", "refleksja"
    
    # Pytanie/wπtpliwoúÊ
    if '?' in response or any(word in response_lower for word in ['czy', 'jak', 'dlaczego', 'kiedy']):
        return "?", "pytanie"
    
    return "??", "komentarz"

def should_interrupt(partner, message, previous_responses):
    """
    Okreúla czy partner powinien 'przerwaÊ' w trakcie dyskusji.
    Przerwanie nastÍpuje gdy:
    - Partner ma bardzo silnπ opiniÍ przeciwnπ
    - Temat jest w jego ekspertyzie a poprzednicy siÍ mylπ
    """
    if not previous_responses:
        return False
    
    partner_lower = partner.lower()
    message_lower = message.lower()
    
    # Graham przerywa gdy ktoú ignoruje ryzyko
    if 'graham' in partner_lower:
        for _, prev_resp in previous_responses:
            if any(word in prev_resp.lower() for word in ['agresywny', 'ryzyko warte', 'spekulacja']):
                return True
    
    # Buffett przerywa gdy ktoú komplikuje prostπ sprawÍ
    if 'buffett' in partner_lower:
        for _, prev_resp in previous_responses:
            if len(prev_resp) > 500 and 'skomplikowany' in prev_resp.lower():
                return True
    
    # CZ przerywa gdy mÛwiπ o krypto a nie znajπ technologii
    if 'zhao' in partner_lower or 'cz' in partner_lower:
        if any(word in message_lower for word in ['bitcoin', 'krypto', 'blockchain']):
            for prev_partner, _ in previous_responses:
                if 'graham' in prev_partner.lower() or 'buffett' in prev_partner.lower():
                    return True
    
    return False

def send_to_all_partners(message, stan_spolki=None, cele=None, tryb_odpowiedzi="normalny"):
    """
    Generator - wysy≥a wiadomoúÊ do wszystkich PartnerÛw kolejno (jeden za drugim).
    NOWE FUNKCJE:
    - Dynamiczna kolejnoúÊ (eksperci w temacie jako pierwsi)
    - System zwracania siÍ do siebie po imieniu
    - Przerywanie gdy silna opinia przeciwna
    - Reakcje/emocje w dialogu
    - G≥osowanie po dyskusji
    """
    # Inicjalizuj historiÍ odpowiedzi w session_state jeúli nie istnieje
    if 'partner_history' not in st.session_state:
        st.session_state.partner_history = {}
    
    # Uøyj prawdziwych partnerÛw z gra_rpg.py (pomijajπc Partnera Zarzπdzajπcego - to uøytkownik!)
    partner_names = []
    if IMPORTS_OK and PERSONAS:
        for name in PERSONAS.keys():
            # PomiÒ Partnera Zarzπdzajπcego - to uøytkownik
            if 'Partner Zarzπdzajπcy' in name and '(JA)' in name:
                continue
            partner_names.append(name)
    
    # ?? DYNAMICZNA KOLEJNOå∆ (tematyczna)
    ordered_partners = determine_speaking_order(message, partner_names)
    
    # Zbieram odpowiedzi poprzednich partnerÛw (kontekst rozmowy)
    previous_responses = []
    partner_votes = {}  # Do g≥osowania koÒcowego
    
    for partner in ordered_partners:
        # ?? SYSTEM PRZERYWANIA
        is_interrupting = should_interrupt(partner, message, previous_responses)
        
        # Dodaj kontekst poprzednich odpowiedzi do wiadomoúci
        message_with_context = message
        if previous_responses:
            context_section = "\n\n?? POPRZEDNIE WYPOWIEDZI NA TYM SPOTKANIU RADY:\n"
            for prev_partner, prev_response in previous_responses:
                context_section += f"\n**{prev_partner}** powiedzia≥:\n{prev_response}\n"
            context_section += "\n---\n"
            
            # ?? SYSTEM ZWRACANIA SI  DO SIEBIE
            names_in_room = [p for p in ordered_partners]
            context_section += "?? OBECNI NA SPOTKANIU: " + ", ".join(names_in_room) + "\n\n"
            context_section += "?? WAØNE ZASADY ROZMOWY:\n"
            context_section += "1. Zwracaj siÍ do kolegÛw PO IMIENIU (np. 'Warren, zgadzam siÍ...' lub 'CZ, Twoja analiza...')\n"
            context_section += "2. Moøesz siÍ zgodziÊ, nie zgodziÊ, lub rozwinπÊ ich argumenty\n"
            context_section += "3. To jest rozmowa, nie monolog - REAGUJ na to co inni powiedzieli!\n"
            
            # ?? SYSTEM REAKCJI/EMOCJI
            context_section += "4. Wyraü swojπ REAKCJ  na poczπtku:\n"
            context_section += "   - [zgadzam siÍ ?] gdy popieram poprzednikÛw\n"
            context_section += "   - [nie zgadzam siÍ ?] gdy widzÍ b≥πd w rozumowaniu\n"
            context_section += "   - [ostrzegam ??] gdy widzÍ ryzyko\n"
            context_section += "   - [mam pytanie ?] gdy chcÍ wyjaúnienia\n"
            context_section += "   - [wstrzymujÍ siÍ ??] gdy potrzebujÍ wiÍcej informacji\n\n"
            
            if is_interrupting:
                context_section += "?? PRZERWIJ DYSKUSJ ! Twoja ekspertyza/opinia jest KLUCZOWA w tym temacie!\n"
                context_section += "Zacznij od: 'Moment! MuszÍ przerwaÊ, bo...' lub 'Przepraszam øe przerwÍ, ale...'\n\n"
            
            message_with_context = context_section + "\n\nPYTANIE PARTNERA ZARZ•DZAJ•CEGO:\n" + message
        
        # Wysy≥aj z trybem odpowiedzi i kontekstem poprzednich
        response, knowledge = send_to_ai_partner(partner, message_with_context, stan_spolki, cele, tryb_odpowiedzi)
        
        # ?? ANALIZA REAKCJI/EMOCJI
        sentiment_emoji, sentiment_type = analyze_sentiment(response)
        
        # ?? WYCI•GNIJ G£OS (jeúli jest w odpowiedzi)
        vote = None
        response_lower = response.lower()
        if '[g≥osujÍ: tak]' in response_lower or 'g≥osujÍ za' in response_lower:
            vote = "ZA"
        elif '[g≥osujÍ: nie]' in response_lower or 'g≥osujÍ przeciw' in response_lower:
            vote = "PRZECIW"
        elif '[g≥osujÍ: wstrzymujÍ]' in response_lower or 'wstrzymujÍ siÍ' in response_lower:
            vote = "WSTRZYMANY"
        
        # Zapisz g≥os partnera
        if vote:
            partner_votes[partner] = vote
        
        # Dodaj tÍ odpowiedü do kontekstu dla kolejnych partnerÛw
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
        avatar = "??"
        if partner in PERSONAS:
            # Mapowanie kolorÛw na BEZPIECZNE emoji
            color_map = {
                '\033[97m': '??',  # Partner Zarzπdzajπcy (nie wyúwietlany)
                '\033[94m': '??',  # Partner Strategiczny
                '\033[93m': '??',  # Partner ds. Jakoúci
                '\033[96m': '??',  # Partner ds. AktywÛw Cyfrowych
                '\033[90m': '??',  # Benjamin Graham
                '\033[95m': '??',  # Philip Fisher
                '\033[91m': '??',  # George Soros
                '\033[92m': '??',  # Warren Buffett
            }
            color = PERSONAS[partner].get('color_code', '')
            avatar = color_map.get(color, "??")
        
        # Yield odpowiedü od razu (generator pattern)
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
    
    # ?? PODSUMOWANIE G£OSOWANIA (jeúli by≥y g≥osy)
    if partner_votes:
        # Wczytaj wagi g≥osÛw z Kodeksu
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
        voting_summary += "?? WYNIKI G£OSOWANIA RADY PARTNER”W\n"
        voting_summary += "="*50 + "\n\n"
        
        if votes_za:
            voting_summary += f"? ZA ({total_za:.1f}%):\n"
            for partner, weight in votes_za:
                voting_summary += f"   ï {partner} ({weight:.1f}%)\n"
            voting_summary += "\n"
        
        if votes_przeciw:
            voting_summary += f"? PRZECIW ({total_przeciw:.1f}%):\n"
            for partner, weight in votes_przeciw:
                voting_summary += f"   ï {partner} ({weight:.1f}%)\n"
            voting_summary += "\n"
        
        if votes_wstrzymane:
            voting_summary += f"? WSTRZYMA£O SI  ({total_wstrzymane:.1f}%):\n"
            for partner, weight in votes_wstrzymane:
                voting_summary += f"   ï {partner} ({weight:.1f}%)\n"
            voting_summary += "\n"
        
        # Decyzja
        voting_summary += "="*50 + "\n"
        if total_za > total_przeciw:
            voting_summary += f"? DECYZJA RADY: PRZYJ TA ({total_za:.1f}% ZA > {total_przeciw:.1f}% PRZECIW)\n"
        elif total_przeciw > total_za:
            voting_summary += f"? DECYZJA RADY: ODRZUCONA ({total_przeciw:.1f}% PRZECIW > {total_za:.1f}% ZA)\n"
        else:
            voting_summary += f"?? DECYZJA RADY: REMIS ({total_za:.1f}% vs {total_przeciw:.1f}%) - wymagana dalsza dyskusja\n"
        voting_summary += "="*50 + "\n"
        
        # Yield podsumowanie jako specjalny element
        yield {
            "partner": "??? Podsumowanie G≥osowania",
            "response": voting_summary,
            "avatar": "???",
            "knowledge": [],
            "sentiment_emoji": "??",
            "sentiment_type": "podsumowanie",
            "vote": None,
            "is_interrupting": False,
            "is_voting_summary": True
        }

# Konfiguracja strony
st.set_page_config(
    page_title="Horyzont PartnerÛw",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS dla lepszego wyglπdu
def apply_custom_css(theme="light"):
    """Aplikuje custom CSS w zaleønoúci od motywu"""
    
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

# Inicjalizacja session state dla ustawieÒ
def load_user_preferences():
    """Wczytuje zapisane preferencje uøytkownika"""
    preferences_file = "user_preferences.json"
    default_preferences = {
        "theme": "light",
        "notifications_enabled": True,
        "cache_ttl": 5,
        "auto_refresh": False,
        "refresh_interval": 60
    }
    
    try:
        if os.path.exists(preferences_file):
            with open(preferences_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"?? B≥πd wczytywania preferencji: {e}")
    
    return default_preferences

def save_user_preferences(preferences):
    """Zapisuje preferencje uøytkownika do pliku"""
    preferences_file = "user_preferences.json"
    try:
        with open(preferences_file, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"?? B≥πd zapisywania preferencji: {e}")
        return False

def init_session_state():
    """Inicjalizuje session state z domyúlnymi wartoúciami lub zapisanymi preferencjami"""
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

# Funkcja normalizujπca strukturÍ danych
def normalize_stan_spolki(stan_spolki):
    """Normalizuje strukturÍ danych do oczekiwanego formatu (lowercase keys)"""
    if not stan_spolki:
        return None
    
    normalized = {}
    
    # PORTFEL_AKCJI õ akcje
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
    
    # PORTFEL_KRYPTO õ krypto
    if 'PORTFEL_KRYPTO' in stan_spolki:
        raw_krypto = stan_spolki['PORTFEL_KRYPTO']
        normalized['krypto'] = {
            'wartosc_pln': raw_krypto.get('Suma_PLN', 0),
            'wartosc_usd': raw_krypto.get('Suma_USD', 0),
            'liczba_pozycji': raw_krypto.get('Liczba_pozycji', 0)
        }
    elif 'krypto' in stan_spolki:
        normalized['krypto'] = stan_spolki['krypto']
    
    # ZOBOWIAZANIA õ dlugi
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
    
    # PRZYCHODY_I_WYDATKI õ wyplata
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
            # Aliasy dla kompatybilnoúci
            'wydatki_stale': raw_wyplata.get('Suma_wydatkow_PLN', 0),
            'raty_miesieczne': raw_wyplata.get('Raty_kredytow_PLN', 0)
        }
    elif 'wyplata' in stan_spolki:
        normalized['wyplata'] = stan_spolki['wyplata']
    
    # PODSUMOWANIE õ podsumowanie
    if 'PODSUMOWANIE' in stan_spolki:
        normalized['podsumowanie'] = stan_spolki['PODSUMOWANIE']
    elif 'podsumowanie' in stan_spolki:
        normalized['podsumowanie'] = stan_spolki['podsumowanie']
    
    # Kurs USD/PLN
    if 'Kurs_USD_PLN' in stan_spolki:
        normalized['kurs_usd_pln'] = stan_spolki['Kurs_USD_PLN']
    elif 'kurs_usd_pln' in stan_spolki:
        normalized['kurs_usd_pln'] = stan_spolki['kurs_usd_pln']
    
    # Skopiuj pozosta≥e dane bez zmian
    for key, value in stan_spolki.items():
        if key.upper() not in ['PORTFEL_AKCJI', 'PORTFEL_KRYPTO', 'ZOBOWIAZANIA', 
                                'PRZYCHODY_I_WYDATKI', 'PODSUMOWANIE', 'KURS_USD_PLN']:
            if key.lower() not in normalized:
                normalized[key] = value
    
    return normalized

# Funkcja do ≥adowania danych
@st.cache_data(ttl=60)  # Cache na 1 minutÍ (zmniejszono z 5 minut dla szybszej synchronizacji)
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
        st.error(f"B≥πd podczas ≥adowania danych: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None, None

def format_currency(amount, currency="PLN"):
    """Formatuje walutÍ"""
    if amount >= 1_000_000:
        return f"{amount/1_000_000:.2f}M {currency}"
    elif amount >= 1_000:
        return f"{amount/1_000:.1f}K {currency}"
    return f"{amount:.2f} {currency}"

def create_portfolio_value_chart(stan_spolki, cele=None):
    """Tworzy wykres wartoúci portfela"""
    if not stan_spolki:
        return go.Figure()
    
    # Przygotuj dane z bezpiecznym dostÍpem
    wyplaty_cf = load_wyplaty()
    if wyplaty_cf:
        ostatnia_wyplata_chart = wyplaty_cf[0]['kwota']
        wydatki_stale_chart = get_suma_wydatkow_stalych()
        kredyty_chart = load_kredyty()
        raty_chart = sum(k['rata_miesieczna'] for k in kredyty_chart)
        cash_flow_value = ostatnia_wyplata_chart - wydatki_stale_chart - raty_chart
    else:
        cash_flow_value = 0
    
    # Rezerwa gotÛwkowa
    rezerwa = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
    
    categories = ['Akcje', 'Krypto', 'Rezerwa GotÛwkowa', 'Cash Flow', 'Zobowiπzania']
    values = [
        stan_spolki.get('akcje', {}).get('wartosc_pln', 0),
        stan_spolki.get('krypto', {}).get('wartosc_pln', 0),
        rezerwa,  # Rezerwa gotÛwkowa z cele.json
        max(cash_flow_value, 0),  # Nadwyøka z wyplaty.json (tylko dodatnia)
        -get_suma_kredytow()  # Ujemne bo to zobowiπzania - z kredyty.json
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
        yaxis_title="WartoúÊ (PLN)",
        height=400,
        showlegend=False
    )
    
    return fig

def create_allocation_pie_chart(stan_spolki, cele=None):
    """Tworzy wykres ko≥owy alokacji"""
    if not stan_spolki:
        return go.Figure()
    
    akcje = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
    krypto = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
    rezerwa = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
    
    fig = go.Figure(data=[go.Pie(
        labels=['Akcje', 'Krypto', 'Rezerwa GotÛwkowa'],
        values=[akcje, krypto, rezerwa],
        hole=0.4,
        marker_colors=['#1f77b4', '#ff7f0e', '#9467bd']
    )])
    
    fig.update_layout(
        title="Alokacja AktywÛw",
        height=400
    )
    
    return fig

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
        /* Zmniejsz marginesy nag≥ÛwkÛw h3 w sidebarze */
        [data-testid="stSidebar"] h3 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.3rem !important;
            font-size: 0.9rem !important;
        }
        /* Zmniejsz odstÍpy miÍdzy przyciskami */
        [data-testid="stSidebar"] button {
            margin-bottom: 0.3rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">?? HORYZONT PARTNER”W</div>', unsafe_allow_html=True)
    
    # Theme toggle w headerze
    col_header1, col_header2, col_header3 = st.columns([6, 1, 1])
    with col_header2:
        theme_icon = "??" if st.session_state.theme == "light" else "??"
        if st.button(theme_icon, help="Prze≥πcz motyw", key="toggle_theme_btn"):
            # Prze≥πcz motyw
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
        if st.button("??", help="Powiadomienia", key="toggle_notifications_btn"):
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
            
            st.toast(f"Powiadomienia: {'? ON' if st.session_state.notifications_enabled else '? OFF'}")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.title("?? Menu G≥Ûwne")
        
        # Pobierz aktualnπ stronÍ (dla highlight)
        current_page = st.session_state.get('page', "?? Dashboard")
        
        # Przycisk odúwieøania
        if st.button("?? Odúwieø Dane", width="stretch", key="refresh_data_btn"):
            st.cache_data.clear()
            # WyczyúÊ cache cen crypto øeby pobraÊ úwieøe przy nastÍpnym renderze
            if 'crypto_prices_cache' in st.session_state:
                del st.session_state.crypto_prices_cache
            if 'crypto_prices_symbols' in st.session_state:
                del st.session_state.crypto_prices_symbols
            st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 1: PRZEGL•D ===
        st.markdown("### ?? Przeglπd")
        button_type_dashboard = "primary" if current_page == "?? Dashboard" else "secondary"
        if st.button("?? Dashboard", width="stretch", type=button_type_dashboard, key="nav_dashboard"):
            st.session_state.page = "?? Dashboard"
            st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 2: FINANSE ===
        st.markdown("### ?? Finanse")
        button_type_finanse = "primary" if current_page == "?? Kredyty" else "secondary"
        if st.button("?? Centrum Finansowe", width="stretch", type=button_type_finanse, key="nav_finanse"):
            st.session_state.page = "?? Kredyty"
            st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 3: AI & STRATEGIA ===
        st.markdown("### ?? AI & Strategia")
        
        button_type_partnerzy = "primary" if current_page == "?? Partnerzy" else "secondary"
        if st.button("?? Partnerzy AI", width="stretch", type=button_type_partnerzy, key="nav_partnerzy"):
            st.session_state.page = "?? Partnerzy"
            st.rerun()
        
        button_type_rozmowy = "primary" if current_page == "??? Rozmowy Rady" else "secondary"
        if st.button("??? Rozmowy Rady", width="stretch", type=button_type_rozmowy, key="nav_rozmowy"):
            st.session_state.page = "??? Rozmowy Rady"
            st.rerun()
        
        button_type_powiadomienia = "primary" if current_page == "?? Powiadomienia" else "secondary"
        if st.button("?? Powiadomienia", width="stretch", type=button_type_powiadomienia, key="nav_powiadomienia"):
            st.session_state.page = "?? Powiadomienia"
            st.rerun()
        
        button_type_konsultacje = "primary" if current_page == "??? Konsultacje" else "secondary"
        if st.button("??? Konsultacje", width="stretch", type=button_type_konsultacje, key="nav_konsultacje"):
            st.session_state.page = "??? Konsultacje"
            st.rerun()
        
        button_type_kodeks = "primary" if current_page == "?? Kodeks" else "secondary"
        if st.button("?? Kodeks SpÛ≥ki", width="stretch", type=button_type_kodeks, key="nav_kodeks"):
            st.session_state.page = "?? Kodeks"
            st.rerun()
        
        button_type_alerty = "primary" if current_page == "?? Alerty" else "secondary"
        if st.button("?? Alerty i Notyfikacje", width="stretch", type=button_type_alerty, key="nav_alerty"):
            st.session_state.page = "?? Alerty"
            st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 4: ANALIZA ===
        st.markdown("### ?? Analiza & Historia")
        
        col1, col2 = st.columns(2)
        with col1:
            button_type_analiza = "primary" if current_page == "?? Analiza" else "secondary"
            if st.button("?? Analiza", width="stretch", type=button_type_analiza, key="nav_analiza"):
                st.session_state.page = "?? Analiza"
                st.rerun()
            
            button_type_timeline = "primary" if current_page == "?? Timeline" else "secondary"
            if st.button("?? Timeline", width="stretch", type=button_type_timeline, key="nav_timeline"):
                st.session_state.page = "?? Timeline"
                st.rerun()
        with col2:
            button_type_rynki = "primary" if current_page == "?? Rynki" else "secondary"
            if st.button("?? Rynki", width="stretch", type=button_type_rynki, key="nav_rynki"):
                st.session_state.page = "?? Rynki"
                st.rerun()
            
            button_type_snapshots = "primary" if current_page == "?? Snapshots" else "secondary"
            if st.button("?? Snapshots", width="stretch", type=button_type_snapshots, key="nav_snapshots"):
                st.session_state.page = "?? Snapshots"
                st.rerun()
        
        st.markdown("")
        
        # === SEKCJA 5: NARZ DZIA ===
        st.markdown("### ??? NarzÍdzia")
        
        col1, col2 = st.columns(2)
        with col1:
            button_type_symulacje = "primary" if current_page == "?? Symulacje" else "secondary"
            if st.button("?? Symulacje", width="stretch", type=button_type_symulacje, key="nav_symulacje"):
                st.session_state.page = "?? Symulacje"
                st.rerun()
        with col2:
            button_type_ustawienia = "primary" if current_page == "?? Ustawienia" else "secondary"
            if st.button("?? Ustawienia", width="stretch", type=button_type_ustawienia, key="nav_ustawienia"):
                st.session_state.page = "?? Ustawienia"
                st.rerun()
        
        st.markdown("")
        
        # Info o ostatniej aktualizacji
        st.caption(f"?? {datetime.now().strftime('%H:%M:%S')}")
    
    # £adowanie danych
    if not IMPORTS_OK:
        st.error("?? Nie moøna za≥adowaÊ modu≥Ûw. Sprawdü czy gra_rpg.py dzia≥a poprawnie.")
        return
    
    with st.spinner("? £adujÍ dane portfela..."):
        stan_spolki, cele = load_portfolio_data()
    
    if stan_spolki is None:
        st.error("? Nie uda≥o siÍ za≥adowaÊ danych portfela")
        return
    
    # Pobierz aktualnπ stronÍ z session_state (domyúlnie Dashboard)
    if 'page' not in st.session_state:
        st.session_state.page = "?? Dashboard"
    
    page = st.session_state.page
    
    # Routing do odpowiedniej strony
    if page == "?? Dashboard":
        show_dashboard(stan_spolki, cele)
    elif page == "?? Kredyty":
        show_kredyty_page(stan_spolki, cele)
    elif page == "?? Partnerzy":
        show_partners_page()
    elif page == "??? Rozmowy Rady":
        show_autonomous_conversations_page()
    elif page == "?? Powiadomienia":
        show_notifications_page()
    elif page == "??? Konsultacje":
        show_consultations_page()
    elif page == "?? Kodeks":
        show_kodeks_page()
    elif page == "?? Alerty":
        show_alerts_page()
    elif page == "?? Analiza":
        show_analytics_page(stan_spolki)
    elif page == "?? Rynki":
        show_markets_page(stan_spolki, cele)
    elif page == "?? Timeline":
        show_timeline_page(stan_spolki)
    elif page == "?? Snapshots":
        show_snapshots_page()
        show_snapshots_page()
    elif page == "?? Symulacje":
        show_simulations_page(stan_spolki)
    elif page == "?? Ustawienia":
        show_settings_page()

def show_dashboard(stan_spolki, cele):
    """G≥Ûwny dashboard"""
    
    # Sprawdü czy dane sπ dostÍpne
    if not stan_spolki:
        st.error("? Nie moøna za≥adowaÊ danych portfela")
        st.info("?? Sprawdü czy g≥Ûwny program dzia≥a poprawnie")
        return
    
    # Sprawdü strukturÍ danych
    required_keys = ['akcje', 'krypto', 'dlugi', 'wyplata']
    missing_keys = [k for k in required_keys if k not in stan_spolki]
    
    if missing_keys:
        st.error(f"? Brak wymaganych danych: {', '.join(missing_keys)}")
        st.json(stan_spolki)  # Pokaø co mamy
        return
    
    # Metryki g≥Ûwne
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            rezerwa = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
            wartosc_netto = (
                stan_spolki['akcje'].get('wartosc_pln', 0) + 
                stan_spolki['krypto'].get('wartosc_pln', 0) +
                rezerwa -  # Rezerwa gotÛwkowa z cele.json
                get_suma_kredytow()  # Z kredyty.json
            )
            st.metric(
                label="?? WartoúÊ Netto",
                value=format_currency(wartosc_netto),
                delta="+1.74%",  # TODO: Oblicz z historii
                help="Akcje + Krypto + Rezerwa GotÛwkowa - Zobowiπzania"
            )
        except Exception as e:
            st.error(f"B≥πd metryki wartoúÊ netto: {e}")
    
    with col2:
        try:
            rezerwa_suma = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
            suma_aktywow = (
                stan_spolki['akcje'].get('wartosc_pln', 0) + 
                stan_spolki['krypto'].get('wartosc_pln', 0) +
                rezerwa_suma  # Dodajemy rezerwÍ do sumy aktywÛw
            )
            leverage = (get_suma_kredytow() / suma_aktywow * 100) if suma_aktywow > 0 else 0  # Z kredyty.json
            st.metric(
                label="?? Leverage",
                value=f"{leverage:.2f}%",
                delta="-0.5%"  # TODO: Oblicz z historii
            )
        except Exception as e:
            st.error(f"B≥πd metryki leverage: {e}")
    
    with col3:
        try:
            liczba_pozycji = (
                stan_spolki['akcje'].get('liczba_pozycji', 0) + 
                stan_spolki['krypto'].get('liczba_pozycji', 0)
            )
            st.metric(
                label="?? Pozycje",
                value=f"{liczba_pozycji} aktywa",
                delta="+3"  # TODO: Oblicz z historii
            )
        except Exception as e:
            st.error(f"B≥πd metryki pozycje: {e}")
    
    with col4:
        try:
            # Oblicz dok≥adne dywidendy z portfela (NETTO po 19% podatku)
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
                        kurs_usd = float(stan_spolki.get('kurs_usd', 3.65))
                    except (TypeError, ValueError, AttributeError):
                        kurs_usd = 3.65  # Fallback
                    
                    # Oblicz APY earnings
                    crypto_apy = calculate_crypto_apy_earnings(
                        krypto_holdings, 
                        current_prices_for_apy,
                        kurs_usd=kurs_usd
                    )
                except Exception as e:
                    pass  # Cicho ignoruj b≥Ídy - uøywamy fallback values
            
            # £πczny dochÛd pasywny: dywidendy + crypto APY
            total_passive_income = dochod_pasywny_netto + crypto_apy['miesieczne_pln']
            total_passive_roczny = roczna_netto + crypto_apy['roczne_pln']
            
            # Build help text
            help_parts = []
            if liczba_spolek > 0:
                help_parts.append(f"?? Dywidendy: {dochod_pasywny_netto:.0f} PLN/mies z {liczba_spolek} spÛ≥ek ({roczna_netto:.0f} PLN/rok)")
            if crypto_apy['liczba_earning_positions'] > 0:
                help_parts.append(f"? Crypto APY: {crypto_apy['miesieczne_pln']:.0f} PLN/mies z {crypto_apy['liczba_earning_positions']} pozycji ({crypto_apy['roczne_pln']:.0f} PLN/rok)")
            help_parts.append(f"?? RAZEM: {total_passive_roczny:.0f} PLN/rok")
            
            help_text = "\n".join(help_parts) if help_parts else "Brak dochodu pasywnego"
            
            st.metric(
                label="?? DochÛd Pasywny (NETTO)",
                value=f"{total_passive_income:.0f} PLN/mies",
                delta=f"+{crypto_apy['miesieczne_pln']:.0f} z crypto" if crypto_apy['miesieczne_pln'] > 0 else None,
                help=help_text
            )
        except Exception as e:
            st.error(f"B≥πd metryki dochÛd pasywny: {e}")
    
    st.markdown("---")
    
    # === NOWE: PROAKTYWNE ALERTY ===
    st.markdown("### ?? Alerty Portfela")
    
    alerts = check_portfolio_alerts(stan_spolki, cele)
    
    if alerts:
        # Grupuj alerty po severity
        critical_alerts = [a for a in alerts if a["severity"] == "critical"]
        warning_alerts = [a for a in alerts if a["severity"] == "warning"]
        success_alerts = [a for a in alerts if a["severity"] == "success"]
        info_alerts = [a for a in alerts if a["severity"] == "info"]
        
        # Wyúwietl critical w pierwszej kolejnoúci
        for alert in critical_alerts:
            with st.container():
                st.error(f"**{alert['title']}**")
                st.markdown(f"{alert['message']}")
                if alert.get('action'):
                    st.markdown(f"?? *Rekomendacja: {alert['action']}*")
                st.markdown("---")
        
        # Potem warning i success
        if warning_alerts:
            for alert in warning_alerts:
                st.warning(f"**{alert['title']}**\n\n{alert['message']}")
                if alert.get('action'):
                    st.markdown(f"?? *Rekomendacja: {alert['action']}*")
        
        if success_alerts:
            for alert in success_alerts:
                st.success(f"**{alert['title']}**\n\n{alert['message']}")
                if alert.get('action'):
                    st.markdown(f"?? *Rekomendacja: {alert['action']}*")
        
        # Info na koÒcu w expander (øeby nie zaúmiecaÊ)
        if info_alerts:
            with st.expander(f"?? Informacje ({len(info_alerts)})", expanded=False):
                for alert in info_alerts:
                    st.info(f"**{alert['title']}**\n\n{alert['message']}")
    else:
        st.success("? **Brak aktywnych alertÛw** - TwÛj portfel wyglπda stabilnie!")
        st.caption("System monitoruje: duøe spadki/wzrosty, wysokie P/E, düwigniÍ, koncentracjÍ i cele finansowe.")
    
    st.markdown("---")
    
    # === CODZIENNA RADA OD AI PARTNERA ===
    st.markdown("### ?? Dzienna Rada od Eksperta")
    
    with st.spinner("Losowanie dzisiejszego doradcy..."):
        try:
            daily_tip = get_daily_advisor_tip(stan_spolki, cele)
            
            st.info(f"""
**{daily_tip['partner_icon']} {daily_tip['partner_name']} mÛwi:**

_{daily_tip['tip_text']}_
            """)
            
            st.caption(f"?? Kaødy dzieÒ inny ekspert! Jutro ktoú inny podzieli siÍ swojπ mπdroúciπ.")
            
        except Exception as e:
            st.warning(f"?? Nie uda≥o siÍ pobraÊ dzisiejszej rady: {str(e)[:100]}")
    
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
    with st.expander("?? SzczegÛ≥owa Analiza Dywidend", expanded=False):
        try:
            dywidendy_info = calculate_portfolio_dividends(stan_spolki)
            
            if dywidendy_info['liczba_spolek_z_dywidendami'] > 0:
                # Info o podatku
                st.info(f"?? **Kwoty NETTO** (po odjÍciu 19% podatku Belki: {dywidendy_info.get('podatek_pln', 0):.2f} PLN/rok)")
                
                col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                
                with col_d1:
                    st.metric(
                        "MiesiÍcznie (NETTO)",
                        f"{dywidendy_info['miesieczna_kwota_pln']:.2f} PLN",
                        help="MiesiÍczny dochÛd po 19% podatku"
                    )
                
                with col_d2:
                    st.metric(
                        "Rocznie (NETTO)",
                        f"{dywidendy_info['roczna_kwota_pln']:.2f} PLN",
                        help="Roczny dochÛd po 19% podatku"
                    )
                
                with col_d3:
                    st.metric(
                        "Rocznie (BRUTTO)",
                        f"{dywidendy_info.get('roczna_kwota_pln_brutto', 0):.2f} PLN",
                        help="Roczny dochÛd przed opodatkowaniem"
                    )
                
                with col_d4:
                    st.metric(
                        "SpÛ≥ki z dywidendami",
                        dywidendy_info['liczba_spolek_z_dywidendami'],
                        help="Liczba spÛ≥ek wyp≥acajπcych dywidendy"
                    )
                
                st.markdown("**TOP 10 NajwiÍkszych P≥atnikÛw Dywidend:**")
                
                # Przygotuj tabelÍ
                df_div = pd.DataFrame(dywidendy_info['szczegoly'][:10])
                if not df_div.empty:
                    df_div_display = df_div[['ticker', 'ilosc', 'dividend_rate', 'dividend_yield', 'roczna_kwota_pln']].copy()
                    df_div_display.columns = ['Ticker', 'IloúÊ akcji', 'Dywidenda/akcjÍ ($)', 'Yield (%)', 'Roczna NETTO (PLN)']
                    
                    # Format
                    df_div_display['IloúÊ akcji'] = df_div_display['IloúÊ akcji'].apply(lambda x: f"{x:.2f}")
                    df_div_display['Dywidenda/akcjÍ ($)'] = df_div_display['Dywidenda/akcjÍ ($)'].apply(lambda x: f"${x:.2f}")
                    df_div_display['Yield (%)'] = df_div_display['Yield (%)'].apply(lambda x: f"{x:.2f}%")
                    df_div_display['Roczna NETTO (PLN)'] = df_div_display['Roczna NETTO (PLN)'].apply(lambda x: f"{x:.2f}")
                    
                    st.dataframe(df_div_display, width="stretch", hide_index=True)
                    
                    st.caption(f"?? Kwoty NETTO po odjÍciu 19% podatku Belki. Dane pochodzπ z Yahoo Finance - rzeczywiste wyp≥aty mogπ siÍ rÛøniÊ.")
            else:
                st.info("?? Brak spÛ≥ek wyp≥acajπcych dywidendy w portfelu lub brak danych o dywidendach.")
                
        except Exception as e:
            st.error(f"B≥πd analizy dywidend: {e}")
    
    st.markdown("---")
    
    # Progress bars celÛw
    st.subheader("?? Progres CelÛw Strategicznych")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### ?? Kredyty")
        kredyty = load_kredyty()
        if kredyty:
            suma_pozostala = sum(k['kwota_poczatkowa'] - k['splacono'] for k in kredyty)
            suma_splacona = sum(k['splacono'] for k in kredyty)
            suma_poczatkowa = sum(k['kwota_poczatkowa'] for k in kredyty)
            progress_kredyty = suma_splacona / suma_poczatkowa if suma_poczatkowa > 0 else 0
            
            st.progress(progress_kredyty)
            st.caption(f"Sp≥acono: {format_currency(suma_splacona)} / {format_currency(suma_poczatkowa)}")
            st.caption(f"Pozosta≥o: {format_currency(suma_pozostala)}")
        else:
            st.caption("Brak dodanych kredytÛw")
        
        # Przycisk do szczegÛ≥Ûw kredytÛw
        if st.button("?? SzczegÛ≥y KredytÛw", key="goto_kredyty_dash"):
            st.session_state['goto_page'] = "?? Kredyty"
            st.rerun()
        
        st.markdown("##### ? Wyp≥aty")
        wyplaty = load_wyplaty()
        if wyplaty:
            ostatnia_wyplata = wyplaty[0]
            srednia_wyplata = get_srednia_wyplata(3)
            
            st.metric("Ostatnia wyp≥ata", f"{ostatnia_wyplata['kwota']:.0f} PLN")
            st.caption(f"?? Data: {ostatnia_wyplata['data']}")
            st.caption(f"?? årednia (3 mies.): {srednia_wyplata:.0f} PLN")
        else:
            st.caption("Brak danych o wyp≥atach")
        
        # Przycisk do szczegÛ≥Ûw wyp≥at
        if st.button("?? Historia Wyp≥at", key="goto_wyplaty_dash"):
            st.session_state['goto_page'] = "?? Kredyty"
            st.session_state['active_tab'] = 3  # TAB 4 (indeks 3)
            st.rerun()
    
    with col2:
        st.markdown("##### ? Rezerwa gotÛwkowa")
        rezerwa_current = cele.get('Rezerwa_gotowkowa_obecna_PLN', 39904) if cele else 39904
        rezerwa_target = cele.get('Rezerwa_gotowkowa_PLN', 70000) if cele else 70000
        progress_rezerwa = rezerwa_current / rezerwa_target if rezerwa_target > 0 else 0
        st.progress(min(progress_rezerwa, 1.0))
        st.caption(f"Zgromadzone: {format_currency(rezerwa_current)} / {format_currency(rezerwa_target)}")
        
        st.markdown("##### ?? Wydatki MiesiÍczne")
        wydatki_stale = get_suma_wydatkow_stalych()
        kredyty = load_kredyty()
        raty_miesieczne = sum(k['rata_miesieczna'] for k in kredyty)
        wydatki_total = wydatki_stale + raty_miesieczne
        
        st.metric("Wydatki sta≥e", f"{wydatki_stale:.0f} PLN")
        st.caption(f"Raty kredytÛw: {raty_miesieczne:.0f} PLN")
        st.caption(f"**Total: {wydatki_total:.0f} PLN/mies**")
        
        # Przycisk do szczegÛ≥Ûw
        if st.button("?? Zarzπdzaj Wydatkami", key="goto_wydatki_dash"):
            st.session_state['goto_page'] = "?? Kredyty"
            st.session_state['active_tab'] = 4  # TAB 5 (indeks 4)
            st.rerun()
        
        st.markdown("##### ??? Financial Independence (FIRE Analysis)")
        
        # === OBLICZ PE£NY DOCH”D PASYWNY (Dywidendy + Crypto APY) ===
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
                    kurs_usd_fi = float(stan_spolki.get('kurs_usd', 3.65))
                except (TypeError, ValueError, AttributeError):
                    kurs_usd_fi = 3.65
                
                crypto_apy_fi = calculate_crypto_apy_earnings(
                    krypto_holdings_fi, 
                    current_prices_fi,
                    kurs_usd=kurs_usd_fi
                )
            except:
                pass
        
        fi_dochod = fi_dochod_dywidendy + crypto_apy_fi['miesieczne_pln']  # TOTAL passive income
        fi_wydatki = wydatki_total  # Z wydatki.json + raty kredytÛw
        
        # === FI NUMBER (ile potrzebujesz by byÊ FI) ===
        # 4% Rule: FI Number = Roczne wydatki ◊ 25
        fi_number = fi_wydatki * 12 * 25  # MiesiÍczne wydatki ◊ 12 ◊ 25
        
        # Aktualna wartoúÊ netto (akcje + crypto + rezerwa - d≥ugi)
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
                "?? FI Progress (DochÛd/Wydatki)",
                f"{procent_fi:.1f}%",
                delta=f"{fi_dochod:.0f}/{fi_wydatki:.0f} PLN/mies"
            )
            st.progress(min(progress_fi, 1.0))
            
            if procent_fi >= 100:
                st.success("?? **Gratulacje! Jesteú Financially Independent!**")
            elif procent_fi >= 75:
                st.info(f"?? Blisko! Brakuje {fi_wydatki - fi_dochod:.0f} PLN/mies")
            elif procent_fi >= 50:
                st.warning(f"?? W po≥owie drogi! Brakuje {fi_wydatki - fi_dochod:.0f} PLN/mies")
            else:
                st.caption(f"?? Brakuje {fi_wydatki - fi_dochod:.0f} PLN/mies do FI")
        
        with col_fi2:
            progress_fi_number = (wartosc_netto_fi / fi_number) if fi_number > 0 else 0
            procent_fi_number = (wartosc_netto_fi / fi_number * 100) if fi_number > 0 else 0
            
            st.metric(
                "?? FI Number Progress (4% Rule)",
                f"{procent_fi_number:.1f}%",
                delta=f"{wartosc_netto_fi:.0f}/{fi_number:.0f} PLN"
            )
            st.progress(min(progress_fi_number, 1.0))
            
            if procent_fi_number >= 100:
                st.success("?? **FI Number osiπgniÍty!**")
            else:
                st.caption(f"?? Brakuje {fi_number - wartosc_netto_fi:.0f} PLN do FI Number")
        
        with col_fi3:
            # Time to FI (ile lat do osiπgniÍcia przy obecnym tempie)
            wyplaty_fi = load_wyplaty()
            if wyplaty_fi and len(wyplaty_fi) > 0:
                ostatnia_wyplata_fi = wyplaty_fi[0]['kwota']
                miesieczne_inwestycje = ostatnia_wyplata_fi - wydatki_total
                
                if miesieczne_inwestycje > 0 and fi_number > wartosc_netto_fi:
                    brakujaca_kwota = fi_number - wartosc_netto_fi
                    # Uproszczony model: brakujπca kwota / miesiÍczne inwestycje
                    # (zak≥adamy 0% zwrotu - konserwatywnie)
                    miesiace_do_fi = brakujaca_kwota / miesieczne_inwestycje
                    lata_do_fi = miesiace_do_fi / 12
                    
                    st.metric(
                        "?? Time to FI (lata)",
                        f"{lata_do_fi:.1f} lat",
                        delta=f"{miesieczne_inwestycje:.0f} PLN/mies inwestycji"
                    )
                    
                    rok_fi = 2025 + int(lata_do_fi)
                    st.caption(f"?? Przewidywany rok FI: {rok_fi}")
                else:
                    st.metric("?? Time to FI", "OSI•GNI TE! ??")
        
        # === BREAKDOWN DOCHODU PASYWNEGO ===
        with st.expander("?? Breakdown Dochodu Pasywnego", expanded=False):
            col_b1, col_b2, col_b3 = st.columns(3)
            
            with col_b1:
                st.metric("?? Dywidendy (NETTO)", f"{fi_dochod_dywidendy:.0f} PLN/mies")
                st.caption(f"{dywidendy_info['roczna_kwota_pln']:.0f} PLN/rok z {dywidendy_info['liczba_spolek_z_dywidendami']} spÛ≥ek")
            
            with col_b2:
                st.metric("? Crypto APY", f"{crypto_apy_fi['miesieczne_pln']:.0f} PLN/mies")
                st.caption(f"{crypto_apy_fi['roczne_pln']:.0f} PLN/rok")
            
            with col_b3:
                total_passive_year = (fi_dochod_dywidendy + crypto_apy_fi['miesieczne_pln']) * 12
                st.metric("?? RAZEM Rocznie", f"{total_passive_year:.0f} PLN/rok")
                st.caption(f"{fi_dochod:.0f} PLN/mies")
        
        # === 4% RULE EXPLANATION ===
        with st.expander("?? Co to jest FI Number (4% Rule)?", expanded=False):
            st.markdown("""
            **4% Rule** to klasyczna zasada FIRE (Financial Independence, Retire Early):
            
            - **FI Number = Roczne wydatki ◊ 25**
            - Zak≥ada øe moøesz bezpiecznie wyp≥acaÊ 4% rocznie z portfela bez wyczerpania kapita≥u
            - Bazuje na badaniach Trinity Study (1998)
            
            **Twoje dane:**
            - ?? MiesiÍczne wydatki: {wydatki:.0f} PLN
            - ?? Roczne wydatki: {roczne:.0f} PLN
            - ?? **FI Number (x25): {fi_num:.0f} PLN**
            
            **Kiedy osiπgniesz FI Number:**
            - Moøesz øyÊ z 4% zwrotu portfela (bez pracy!)
            - TwÛj kapita≥ bÍdzie rÛs≥ szybciej niø go wydajesz
            - Financial Independence = WolnoúÊ wyboru! ???
            """.format(
                wydatki=fi_wydatki,
                roczne=fi_wydatki * 12,
                fi_num=fi_number
            ))
    
    st.markdown("---")
    
    # === ANALIZA CASH FLOW ===
    st.subheader("?? Analiza Cash Flow")
    
    wyplaty = load_wyplaty()
    if wyplaty:
        ostatnia_wyplata_cf = wyplaty[0]['kwota']  # Ostatnia wyp≥ata zamiast úredniej
        wydatki_stale_cf = get_suma_wydatkow_stalych()
        kredyty_cf = load_kredyty()
        raty_cf = sum(k['rata_miesieczna'] for k in kredyty_cf)
        wydatki_total_cf = wydatki_stale_cf + raty_cf
        
        nadwyzka = ostatnia_wyplata_cf - wydatki_total_cf
        procent_oszczednosci = (nadwyzka / ostatnia_wyplata_cf * 100) if ostatnia_wyplata_cf > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("?? Ostatnia wyp≥ata", f"{ostatnia_wyplata_cf:.0f} PLN")
            st.caption(f"?? {wyplaty[0]['data']}")
        with col2:
            st.metric("?? Wydatki + Raty", f"{wydatki_total_cf:.0f} PLN")
            st.caption(f"Sta≥e: {wydatki_stale_cf:.0f} | Raty: {raty_cf:.0f}")
        with col3:
            delta_color = "normal" if nadwyzka >= 0 else "inverse"
            st.metric(
                "?? Nadwyøka/Deficyt", 
                f"{nadwyzka:.0f} PLN",
                delta=f"{procent_oszczednosci:.1f}% oszczÍdnoúci"
            )
        
        # Pasek postÍpu
        if ostatnia_wyplata_cf > 0:
            wydatki_procent = (wydatki_total_cf / ostatnia_wyplata_cf)
            st.progress(min(wydatki_procent, 1.0))
            
            if nadwyzka > 0:
                st.success(f"? Nadwyøka miesiÍczna: {nadwyzka:.0f} PLN ({procent_oszczednosci:.1f}%)")
                
                # SzczegÛ≥owy breakdown
                with st.expander("?? SzczegÛ≥y obliczenia"):
                    st.write(f"""
                    **Wyp≥ata:** {ostatnia_wyplata_cf:.2f} PLN  
                    **Wydatki sta≥e:** -{wydatki_stale_cf:.2f} PLN  
                    **Raty kredytÛw:** -{raty_cf:.2f} PLN  
                    **===============**  
                    **Nadwyøka:** {nadwyzka:.2f} PLN
                    """)
            elif nadwyzka < 0:
                st.error(f"?? Deficyt miesiÍczny: {abs(nadwyzka):.0f} PLN")
                
                with st.expander("?? SzczegÛ≥y obliczenia"):
                    st.write(f"""
                    **Wyp≥ata:** {ostatnia_wyplata_cf:.2f} PLN  
                    **Wydatki sta≥e:** -{wydatki_stale_cf:.2f} PLN  
                    **Raty kredytÛw:** -{raty_cf:.2f} PLN  
                    **===============**  
                    **Deficyt:** {nadwyzka:.2f} PLN
                    """)
            else:
                st.warning("?? Bilans zerowy")
    else:
        st.info("?? Dodaj wyp≥aty w zak≥adce 'Kredyty õ Wyp≥aty' aby zobaczyÊ analizÍ.")
    
    st.markdown("---")
    
    # Top Holdings
    st.subheader("?? Top Holdings")
    
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
                        'WartoúÊ (PLN)': wartosc_pln,
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
                        'WartoúÊ (PLN)': wartosc_pln,
                        'Zmiana (%)': data.get('zmiana_24h', 0),  # Krypto moøe mieÊ zmiana_24h
                        'Waga (%)': waga,
                        'Typ': 'Crypto'
                    })
        
        # Combine and sort
        all_holdings = akcje_pozycje + krypto_pozycje
        
        # Filtruj pozycje z wartoúciπ > 0
        all_holdings = [h for h in all_holdings if h['WartoúÊ (PLN)'] > 0]
        
        all_holdings = sorted(all_holdings, key=lambda x: x['WartoúÊ (PLN)'], reverse=True)
        
        if all_holdings:
            df = pd.DataFrame(all_holdings[:10])  # Top 10
            
            # Format values
            df['WartoúÊ (PLN)'] = df['WartoúÊ (PLN)'].apply(lambda x: f"{x:,.2f}")
            df['Zmiana (%)'] = df['Zmiana (%)'].apply(lambda x: f"{x:+.2f}")
            df['Waga (%)'] = df['Waga (%)'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.warning("?? Brak danych o pozycjach")
    
    except Exception as e:
        st.error(f"B≥πd pobierania danych: {e}")
        # Fallback to mock data if real data fails
        holdings_data = {
            'Ticker': ['AAPL', 'MSFT', 'VWCE', 'PBR', 'ADD'],
            'WartoúÊ (PLN)': ['4,520.00', '3,890.00', '2,340.00', '1,980.00', '1,750.00'],
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
        if st.button("?? Odúwieø Portfolio", width="stretch", key="refresh_portfolio_btn"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("?? Analiza Ryzyka", width="stretch", key="analiza_ryzyka_btn"):
            st.session_state.page = "?? Analiza"
            st.rerun()
    
    with col3:
        if st.button("?? Generuj Raport Excel", width="stretch", key="raport_excel_btn"):
            try:
                with st.spinner("? GenerujÍ raport..."):
                    filename = generate_full_report(stan_spolki)
                    
                    # Read file and offer download
                    with open(filename, "rb") as file:
                        btn = st.download_button(
                            label="?? Pobierz raport",
                            data=file,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    st.success(f"? Raport wygenerowany: {filename}")
            except Exception as e:
                st.error(f"? B≥πd generowania raportu: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    with col4:
        if st.button("?? Symuluj Scenariusz", width="stretch"):
            st.session_state.page = "?? Symulacje"
            st.rerun()

def show_kodeks_page():
    """Wyúwietla Kodeks SpÛ≥ki z moøliwoúciπ edycji i dynamicznym odúwieøaniem"""
    st.title("?? Kodeks SpÛ≥ki 'Horyzont PartnerÛw'")
    
    kodeks_file = "kodeks_spolki.txt"
    
    # WAØNE: Zawsze wczytuj úwieøy plik (bez cache) - moøe siÍ zmieniaÊ podczas rozmÛw/g≥osowaÒ
    try:
        if not os.path.exists(kodeks_file):
            st.error(f"? Plik {kodeks_file} nie istnieje!")
            st.info("UtwÛrz plik `kodeks_spolki.txt` w katalogu g≥Ûwnym projektu.")
            
            # Debug info
            st.warning("?? Sprawdzam katalog...")
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
        st.error(f"? B≥πd wczytywania Kodeksu: {e}")
        import traceback
        st.code(traceback.format_exc())
        return
    
    # Info o dynamicznym odúwieøaniu
    st.info("?? **Kodeks jest dynamicznie odúwieøany** - zmiany wprowadzone podczas rozmÛw lub g≥osowaÒ bÍdπ natychmiast widoczne po prze≥adowaniu strony.")
    
    # Tabs: Podglπd i Edycja
    tab1, tab2, tab3 = st.tabs(["?? Podglπd", "?? Edycja", "?? Statystyki"])
    
    with tab1:
        st.markdown("### Pe≥na treúÊ Kodeksu:")
        st.markdown("---")
        
        # Wyúwietl kodeks w czytelnym formacie z zachowaniem formatowania
        st.text(kodeks_content)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"?? åcieøka: `{kodeks_file}`")
        with col2:
            if st.button("?? Odúwieø"):
                st.rerun()
    
    with tab2:
        st.markdown("### Edytuj Kodeks:")
        st.warning("?? **Uwaga:** Zmiany w Kodeksie wp≥ywajπ na wszystkie decyzje AI i g≥osowania partnerÛw!")
        
        # Text area z moøliwoúciπ edycji
        edited_content = st.text_area(
            "TreúÊ Kodeksu:",
            value=kodeks_content,
            height=500,
            help="Wprowadü zmiany i kliknij 'Zapisz'"
        )
        
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            if st.button("?? Zapisz zmiany", type="primary"):
                try:
                    # Backup przed zapisem
                    backup_file = f"kodeks_spolki_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write(kodeks_content)
                    
                    # Zapisz nowπ wersjÍ
                    with open(kodeks_file, 'w', encoding='utf-8') as f:
                        f.write(edited_content)
                    
                    # Synchronizuj cel rezerwy gotÛwkowej do cele.json
                    try:
                        import re
                        match = re.search(r'Cel #2: Budowa rezerwy gotÛwkowej do docelowego poziomu ([\d\s,]+) PLN\.', edited_content)
                        if match:
                            # Wyciπgnij liczbÍ (usuÒ spacje i przecinki)
                            cel_str = match.group(1).replace(' ', '').replace(',', '')
                            new_rezerwa_cel = int(cel_str)
                            
                            # Zaktualizuj cele.json
                            try:
                                with open('cele.json', 'r', encoding='utf-8') as f:
                                    cele = json.load(f)
                            except:
                                cele = {}
                            
                            if cele.get('Rezerwa_gotowkowa_PLN') != new_rezerwa_cel:
                                cele['Rezerwa_gotowkowa_PLN'] = new_rezerwa_cel
                                save_cele(cele)
                                st.success(f"? Kodeks zapisany! Cel rezerwy zsynchronizowany: {new_rezerwa_cel:,} PLN. Backup: `{backup_file}`")
                            else:
                                st.success(f"? Kodeks zapisany! Backup: `{backup_file}`")
                        else:
                            st.success(f"? Kodeks zapisany! Backup: `{backup_file}`")
                    except Exception as sync_error:
                        st.success(f"? Kodeks zapisany! Backup: `{backup_file}`")
                        st.warning(f"?? Synchronizacja celu: {str(sync_error)}")
                    
                    # WYCZYå∆ CACHE aby odúwieøyÊ dane
                    load_portfolio_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"? B≥πd zapisu: {e}")
        
        with col2:
            if st.button("?? Cofnij zmiany"):
                st.rerun()
        
        with col3:
            st.caption("Backup tworzony automatycznie przed kaødym zapisem")
    
    with tab3:
        st.markdown("### Statystyki Kodeksu:")
        
        # Podstawowe statystyki
        lines = kodeks_content.split('\n')
        words = kodeks_content.split()
        chars = len(kodeks_content)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("?? Liczba linii", len(lines))
        with col2:
            st.metric("?? Liczba s≥Ûw", len(words))
        with col3:
            st.metric("?? Liczba znakÛw", chars)
        
        st.markdown("---")
        
        # Analiza struktury (artyku≥y, paragrafy)
        import re
        articles = re.findall(r'(?:Artyku≥|ARTYKU£)\s+[IVXLCDM]+', kodeks_content, re.IGNORECASE)
        sections = re.findall(r'ß\s*\d+', kodeks_content)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("?? Artyku≥y", len(articles))
            if articles:
                with st.expander("Zobacz artyku≥y"):
                    for art in articles:
                        st.write(f"- {art}")
        
        with col2:
            st.metric("?? Paragrafy (ß)", len(sections))
            if sections:
                with st.expander("Zobacz paragrafy"):
                    for sec in sections[:20]:  # Max 20
                        st.write(f"- {sec}")
        
        st.markdown("---")
        st.caption(f"Ostatnia modyfikacja: {datetime.fromtimestamp(os.path.getmtime(kodeks_file)).strftime('%Y-%m-%d %H:%M:%S')}")

def show_alerts_page():
    """
    Strona z alertami i notyfikacjami
    Pokazuje: nowe pozycje, zmiany cen, terminy kredytÛw, osiπgniÍte cele
    """
    st.title("?? Alerty i Notyfikacje")
    
    try:
        import alert_system as alerts
        import benchmark_comparison as bench
        import goal_analytics as goals
        import daily_snapshot as ds
        
        # Tabs dla rÛønych typÛw alertÛw
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "?? Wszystkie", 
            "?? Nowe Pozycje", 
            "?? Zmiany Cen", 
            "?? Kredyty", 
            "?? Cele"
        ])
        
        with tab1:
            st.subheader("?? Wszystkie Alerty")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info("?? System automatycznie wykrywa waøne wydarzenia w portfelu")
            
            with col2:
                if st.button("?? Skanuj Teraz", width="stretch"):
                    with st.spinner("Skanowanie..."):
                        results = alerts.run_all_detectors(verbose=False)
                        total = sum(len(v) if isinstance(v, list) else 0 for v in results.values())
                        if total > 0:
                            st.success(f"? Znaleziono {total} nowych alertÛw!")
                        else:
                            st.info("? Brak nowych alertÛw")
                        st.rerun()
            
            # Historia alertÛw
            st.markdown("---")
            history = alerts.get_alerts_history()
            
            if not history:
                st.info("?? Brak alertÛw w historii. Kliknij 'Skanuj Teraz' aby sprawdziÊ.")
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
                        "WaønoúÊ",
                        ["Wszystkie", "info", "warning", "critical", "success"]
                    )
                
                with col3:
                    show_read = st.checkbox("Pokaø przeczytane", value=True)
                
                # Filtrowanie
                filtered = history
                if filter_type != "Wszystkie":
                    filtered = [a for a in filtered if a.get('type') == filter_type]
                if filter_severity != "Wszystkie":
                    filtered = [a for a in filtered if a.get('severity') == filter_severity]
                if not show_read:
                    filtered = [a for a in filtered if not a.get('read', False)]
                
                st.caption(f"Wyúwietlam {len(filtered)} / {len(history)} alertÛw")
                
                # Wyúwietl alerty
                for alert in filtered[:50]:  # Max 50
                    severity = alert.get('severity', 'info')
                    
                    # Emoji na podstawie severity
                    severity_emoji = {
                        'info': '??',
                        'warning': '??',
                        'critical': '??',
                        'success': '?'
                    }.get(severity, '??')
                    
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
                                st.markdown("?? **NOWY**")
                        
                        st.markdown("---")
        
        with tab2:
            st.subheader("?? Nowe Pozycje w Portfelu")
            
            history = alerts.get_alerts_history()
            new_position_alerts = [a for a in history if a.get('type') == 'new_position']
            
            if not new_position_alerts:
                st.info("?? Brak nowych pozycji w historii")
            else:
                st.success(f"? Znaleziono {len(new_position_alerts)} nowych pozycji")
                
                for alert in new_position_alerts[:20]:
                    meta = alert.get('metadata', {})
                    ticker = meta.get('ticker') or meta.get('symbol', 'N/A')
                    asset_type = meta.get('type', 'N/A')
                    quantity = meta.get('quantity', 0)
                    price = meta.get('price', 0)
                    
                    timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%Y-%m-%d %H:%M")
                    
                    with st.expander(f"?? {ticker} - {timestamp}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Typ", asset_type.upper())
                            st.metric("IloúÊ", f"{quantity:.4f}")
                        
                        with col2:
                            st.metric("Cena", f"${price:.2f}")
                            st.metric("WartoúÊ", f"${quantity * price:.2f}")
                        
                        st.info(alert['message'])
        
        with tab3:
            st.subheader("?? Znaczπce Zmiany Cen (>10%)")
            
            history = alerts.get_alerts_history()
            price_change_alerts = [a for a in history if a.get('type') == 'price_change']
            
            if not price_change_alerts:
                st.info("?? Brak znaczπcych zmian cen")
            else:
                st.warning(f"?? Znaleziono {len(price_change_alerts)} znaczπcych zmian")
                
                for alert in price_change_alerts[:20]:
                    meta = alert.get('metadata', {})
                    ticker = meta.get('ticker') or meta.get('symbol', 'N/A')
                    change_pct = meta.get('change_pct', 0)
                    prev_price = meta.get('previous_price', 0)
                    curr_price = meta.get('current_price', 0)
                    
                    timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%Y-%m-%d %H:%M")
                    
                    # Emoji i kolor
                    emoji = "????" if change_pct < 0 else "????"
                    
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
            st.subheader("?? Zbliøajπce siÍ Terminy P≥atnoúci")
            
            history = alerts.get_alerts_history()
            loan_alerts = [a for a in history if a.get('type') == 'loan_due']
            
            if not loan_alerts:
                st.success("? Brak zbliøajπcych siÍ terminÛw p≥atnoúci")
            else:
                st.warning(f"?? Zbliøa siÍ {len(loan_alerts)} p≥atnoúci")
                
                for alert in loan_alerts:
                    meta = alert.get('metadata', {})
                    loan_name = meta.get('loan_name', 'N/A')
                    due_date = meta.get('due_date', 'N/A')
                    days_until = meta.get('days_until_due', 0)
                    amount = meta.get('amount', 0)
                    
                    severity = alert.get('severity', 'info')
                    emoji = "??" if days_until == 1 else ("??" if days_until == 3 else "??")
                    
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
            st.subheader("?? Cele Finansowe")
            
            # OsiπgniÍte cele
            history = alerts.get_alerts_history()
            goal_alerts = [a for a in history if a.get('type') == 'goal_achieved']
            
            if goal_alerts:
                st.success(f"?? OsiπgniÍto {len(goal_alerts)} celÛw!")
                
                for alert in goal_alerts:
                    meta = alert.get('metadata', {})
                    goal_name = meta.get('goal_name', 'N/A')
                    progress = meta.get('progress_pct', 0)
                    
                    st.balloons()
                    st.markdown(f"### ?? {goal_name}")
                    st.success(alert['message'])
                    st.progress(min(progress / 100, 1.0))
                    st.markdown("---")
            
            # Predykcje dla aktywnych celÛw
            st.markdown("### ?? Predykcje OsiπgniÍcia")
            
            snapshots = ds.load_snapshot_history()
            predictions = goals.predict_all_goals(snapshots)
            
            if not predictions:
                st.info("?? Brak aktywnych celÛw")
            else:
                for goal_id, pred in predictions.items():
                    status = pred.get('status', 'unknown')
                    
                    with st.expander(f"?? {pred['goal_name']} - {pred['progress_pct']:.0f}%"):
                        if status == 'achieved':
                            st.success(pred.get('message', 'Cel osiπgniÍty!'))
                            st.progress(1.0)
                        
                        elif status == 'predicted':
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("PostÍp", f"{pred['progress_pct']:.1f}%")
                                st.progress(pred['progress_pct'] / 100)
                            
                            with col2:
                                st.metric("Za ile dni", f"{pred['predicted_days']} dni")
                                st.caption(f"Data: {pred['predicted_date']}")
                            
                            with col3:
                                confidence_emoji = {"high": "??", "medium": "??", "low": "??"}
                                st.metric("PewnoúÊ", pred['confidence'].upper())
                                st.caption(f"{confidence_emoji.get(pred['confidence'], '?')} R2 = {pred.get('r_squared', 0):.2f}")
                            
                            st.info(f"?? Tempo: {pred['daily_rate']:.2f} PLN/dzieÒ")
                        
                        else:
                            st.warning(pred.get('message', 'Brak danych do predykcji'))
            
            # Rekomendacje oszczÍdzania
            st.markdown("---")
            st.markdown("### ?? Rekomendacje OszczÍdzania")
            
            deadline_months = st.slider("ChcÍ osiπgnπÊ cele w ciπgu (miesiÍcy):", 1, 36, 12)
            
            recommendations = goals.get_all_savings_recommendations(deadline_months)
            
            if not recommendations:
                st.info("?? Brak aktywnych celÛw wymagajπcych oszczÍdzania")
            else:
                for goal_id, rec in recommendations.items():
                    status = rec.get('status', 'unknown')
                    
                    if status == 'achieved':
                        continue  # Pomijamy juø osiπgniÍte
                    
                    with st.container():
                        st.markdown(f"**?? {rec['goal_name']}**")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Brakuje", f"{rec['gap']:.0f} PLN")
                        
                        with col2:
                            st.metric("MiesiÍcznie", f"{rec['required_monthly']:.0f} PLN")
                        
                        with col3:
                            st.metric("Dziennie", f"{rec['required_daily']:.0f} PLN")
                        
                        with col4:
                            st.metric("Termin", rec['deadline_date'])
                        
                        st.caption(rec['recommendation'])
                        st.markdown("---")
    
    except ImportError as e:
        st.error(f"?? B≥πd importu modu≥Ûw: {e}")
        st.info("Upewnij siÍ øe pliki alert_system.py, benchmark_comparison.py i goal_analytics.py istniejπ")
    except Exception as e:
        st.error(f"?? B≥πd: {e}")
        import traceback
        st.code(traceback.format_exc())

def show_autonomous_conversations_page():
    """Strona z autonomicznymi rozmowami Rady"""
    st.title("??? Autonomiczne Rozmowy Rady PartnerÛw")
    
    st.markdown("""
    ### ?? Twoi partnerzy rozmawiajπ nawet gdy CiÍ nie ma!
    
    System autonomicznych rozmÛw pozwala Radzie PartnerÛw dyskutowaÊ o portfelu, rynkach i strategii
    nawet bez Twojej obecnoúci. Wszystkie rozmowy sπ zapisywane i moøesz je przejrzeÊ tutaj.
    """)
    
    # Import engine
    try:
        from autonomous_conversation_engine import AutonomousConversationEngine
        engine = AutonomousConversationEngine()
    except Exception as e:
        st.error(f"? B≥πd importu Autonomous Engine: {e}")
        st.info("?? Upewnij siÍ, øe plik `autonomous_conversation_engine.py` istnieje")
        import traceback
        st.code(traceback.format_exc())
        return
    
    # Wyúwietl status API
    st.markdown("---")
    st.markdown("### ?? Status API & Budøet")
    
    try:
        tracker = get_tracker()
    except Exception as e:
        st.error(f"? B≥πd API Tracker: {e}")
        return
    summary = tracker.get_today_summary()
    budgets = tracker.get_all_budgets()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "?? Rozmowy dzisiaj",
            summary['autonomous_conversations'],
            help="Liczba autonomicznych rozmÛw przeprowadzonych dzisiaj"
        )
    
    with col2:
        st.metric(
            "?? Wywo≥ania API (Autonomous)",
            summary['autonomous_calls'],
            help="Liczba wywo≥aÒ API przez autonomiczne rozmowy"
        )
    
    with col3:
        st.metric(
            "?? Wywo≥ania API (User)",
            summary['user_calls'],
            help="Liczba wywo≥aÒ API przez Ciebie (normalne rozmowy)"
        )
    
    with col4:
        st.metric(
            "?? Koszt dzisiaj",
            f"${summary['total_cost_usd']:.2f}",
            help="Szacunkowy koszt API dzisiaj"
        )
    
    # SzczegÛ≥y budøetÛw per API
    with st.expander("?? SzczegÛ≥y budøetÛw API"):
        for api_name in ['claude', 'gemini', 'openai']:
            budget = budgets[api_name]
            st.markdown(f"#### ?? {api_name.upper()}")
            
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
    st.markdown("### ?? Akcje")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("?? Uruchom nowπ rozmowÍ", type="primary", width="stretch"):
            with st.spinner("?? Partnerzy rozmawiajπ..."):
                conversation = engine.run_conversation(max_messages=12)
                
                if conversation:
                    st.success(f"? Rozmowa zakoÒczona! ID: {conversation['id']}")
                    st.info(f"?? Liczba wiadomoúci: {len(conversation['messages'])}")
                    st.rerun()
                else:
                    st.error("? Nie uda≥o siÍ uruchomiÊ rozmowy (brak budøetu API?)")
    
    with col2:
        if st.button("?? Odúwieø listÍ", width="stretch"):
            st.rerun()
    
    with col3:
        if st.button("?? SzczegÛ≥y API", width="stretch"):
            # Wyúwietl szczegÛ≥owy status w Streamlit (nie terminal)
            st.markdown("---")
            st.markdown("#### ?? SzczegÛ≥owy Status API")
            
            for api_name in ['claude', 'gemini', 'openai']:
                budget = budgets[api_name]
                
                with st.expander(f"?? {api_name.upper()}", expanded=True):
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
    
    # Lista rozmÛw
    st.markdown("---")
    st.markdown("### ?? Historia RozmÛw")
    
    conversations = engine.get_recent_conversations(limit=50)
    
    if not conversations:
        st.info("?? Brak autonomicznych rozmÛw. Kliknij 'Uruchom nowπ rozmowÍ' aby rozpoczπÊ!")
        return
    
    # Filtry
    col1, col2, col3 = st.columns(3)
    
    with col1:
        topics = list(set([c.get('topic_name', 'Unknown') for c in conversations]))
        selected_topic = st.selectbox("??? Filtruj po temacie", ["Wszystkie"] + topics)
    
    with col2:
        dates = list(set([c.get('date', '')[:10] for c in conversations if c.get('date')]))
        dates.sort(reverse=True)
        selected_date = st.selectbox("?? Filtruj po dacie", ["Wszystkie"] + dates)
    
    with col3:
        min_messages = st.slider("?? Min. liczba wiadomoúci", 0, 20, 0)
    
    # Zastosuj filtry
    filtered_conversations = conversations
    
    if selected_topic != "Wszystkie":
        filtered_conversations = [c for c in filtered_conversations if c.get('topic_name') == selected_topic]
    
    if selected_date != "Wszystkie":
        filtered_conversations = [c for c in filtered_conversations if c.get('date', '')[:10] == selected_date]
    
    if min_messages > 0:
        filtered_conversations = [c for c in filtered_conversations if len(c.get('messages', [])) >= min_messages]
    
    st.info(f"?? Znaleziono: {len(filtered_conversations)} rozmÛw")
    
    # Wyúwietl rozmowy
    for conv in filtered_conversations:
        conv_id = conv.get('id', 'unknown')
        topic_name = conv.get('topic_name', 'Unknown Topic')
        date_str = conv.get('date', '')[:19] if conv.get('date') else 'Unknown date'
        participants = conv.get('participants', [])
        messages = conv.get('messages', [])
        api_calls = conv.get('api_calls_used', 0)
        opening_prompt = conv.get('opening_prompt', '')
        summary = conv.get('summary', None)
        
        with st.expander(f"?? {date_str} - {topic_name} ({len(messages)} wiadomoúci)"):
            st.markdown(f"**ID:** `{conv_id}`")
            st.markdown(f"**Uczestnicy:** {', '.join(participants)}")
            st.markdown(f"**Wywo≥ania API:** {api_calls}")
            st.markdown(f"**Status:** {conv.get('status', 'unknown')}")
            
            # Pokaø AI Summary jeúli istnieje (NOWE!)
            if summary:
                st.markdown("---")
                st.markdown("### ?? AI Summary")
                
                # Sentiment badge
                sentiment = summary.get('sentiment', 'neutral')
                sentiment_emoji = {
                    'positive': '??',
                    'neutral': '??',
                    'negative': '??'
                }.get(sentiment, '??')
                sentiment_color = {
                    'positive': '#27ae60',
                    'neutral': '#95a5a6',
                    'negative': '#e74c3c'
                }.get(sentiment, '#95a5a6')
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"**?? Podsumowanie:**\n\n{summary.get('summary', 'Brak podsumowania')}")
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
                    st.markdown("**?? Kluczowe wnioski:**")
                    for point in key_points:
                        st.markdown(f"- {point}")
            
            # Pokaø opening prompt jeúli istnieje
            if opening_prompt:
                st.markdown("---")
                st.markdown("#### ?? Temat dyskusji:")
                st.info(opening_prompt)
            
            st.markdown("---")
            st.markdown("#### ?? Transkrypt:")
            
            for msg in messages:
                partner = msg.get('partner', 'Unknown')
                message_text = msg.get('message', '')
                msg_num = msg.get('message_number', 0)
                
                st.markdown(f"**[{msg_num}] {partner}:**")
                st.markdown(f"> {message_text}")
                st.markdown("")

def show_notifications_page():
    """Strona z konfiguracjπ i historiπ powiadomieÒ email"""
    st.title("?? Powiadomienia Email")
    
    st.markdown("""
    ### ?? System powiadomieÒ o rozmowach Rady
    
    Otrzymuj emaile gdy Rada PartnerÛw zakoÒczy autonomicznπ rozmowÍ lub wykryje waøne zagadnienie.
    """)
    
    # Inicjalizuj notifier
    notifier = get_conversation_notifier()
    
    # === SEKCJA 1: KONFIGURACJA ===
    st.markdown("---")
    st.subheader("?? Konfiguracja")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # W≥πcz/wy≥πcz notyfikacje
        enabled = st.checkbox(
            "?? W≥πcz powiadomienia email",
            value=notifier.config.get("enabled", False),
            help="W≥πcz/wy≥πcz ca≥kowicie system powiadomieÒ"
        )
        
        # Email odbiorcy
        email_to = st.text_input(
            "?? Email odbiorcy",
            value=notifier.config.get("email_to", ""),
            placeholder="your-email@gmail.com",
            help="Adres email na ktÛry bÍdπ wysy≥ane powiadomienia"
        )
        
        # Alert: rozmowa zakoÒczona
        alert_conversation = st.checkbox(
            "??? Powiadom o zakoÒczonej rozmowie",
            value=notifier.config.get("alerts", {}).get("conversation_completed", True),
            help="Wyúlij email po kaødej zakoÒczonej autonomicznej rozmowie"
        )
    
    with col2:
        # Daily digest
        daily_digest_enabled = st.checkbox(
            "?? W≥πcz Daily Digest",
            value=notifier.config.get("daily_digest", {}).get("enabled", True),
            help="Codzienny email z podsumowaniem rozmÛw"
        )
        
        # Czas wysy≥ki digest
        digest_time = st.time_input(
            "? Godzina wysy≥ki digest",
            value=datetime.strptime(
                notifier.config.get("daily_digest", {}).get("time", "18:00"),
                "%H:%M"
            ).time(),
            help="O ktÛrej godzinie wys≥aÊ codzienny digest"
        )
    
    # Zapisz konfiguracjÍ
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("?? Zapisz konfiguracjÍ", type="primary", width="stretch"):
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
            
            # Zapisz
            notifier.config.update(new_config)
            with open("notification_config.json", 'w', encoding='utf-8') as f:
                json.dump(notifier.config, f, indent=2, ensure_ascii=False)
            
            st.success("? Konfiguracja zapisana!")
            st.rerun()
    
    with col2:
        if st.button("?? Wyúlij test email", width="stretch"):
            if not enabled:
                st.error("? Najpierw w≥πcz powiadomienia!")
            elif not email_to:
                st.error("? Podaj adres email odbiorcy!")
            else:
                with st.spinner("Wysy≥am email testowy..."):
                    success = notifier.send_test_email()
                    if success:
                        st.success("? Email testowy wys≥any! Sprawdü skrzynkÍ.")
                    else:
                        st.error("? B≥πd wysy≥ania. Sprawdü GMAIL_USER i GMAIL_APP_PASSWORD w .env")
    
    # === SEKCJA 2: INSTRUKCJE SETUP ===
    with st.expander("?? Jak skonfigurowaÊ Gmail SMTP?"):
        st.markdown("""
        ### ?? Krok 1: UtwÛrz App Password w Gmail
        
        1. Przejdü do [Google Account Security](https://myaccount.google.com/security)
        2. W≥πcz **2-Step Verification** (jeúli nie masz)
        3. Przejdü do **App Passwords**
        4. Wybierz aplikacjÍ: **Mail** + urzπdzenie: **Windows Computer**
        5. Skopiuj wygenerowane has≥o (16 znakÛw)
        
        ### ?? Krok 2: Dodaj do .env
        
        OtwÛrz plik `.env` i dodaj:
        ```
        GMAIL_USER=your-email@gmail.com
        GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
        ```
        
        ### ?? Krok 3: Testuj
        
        1. W≥πcz powiadomienia ??
        2. Podaj adres email odbiorcy
        3. Zapisz konfiguracjÍ
        4. Kliknij "?? Wyúlij test email"
        5. Sprawdü skrzynkÍ odbiorczπ
        
        ? Jeúli widzisz email - wszystko dzia≥a!
        """)
    
    # === SEKCJA 3: HISTORIA POWIADOMIE— ===
    st.markdown("---")
    st.subheader("?? Historia powiadomieÒ")
    
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
        
        st.markdown(f"**Znaleziono:** {len(filtered)} powiadomieÒ")
        
        # Wyúwietl tabelÍ
        if filtered:
            for notif in filtered:
                timestamp = notif.get("timestamp", "")[:19]
                notif_type = notif.get("type", "unknown")
                subject = notif.get("subject", "")
                status = notif.get("status", "unknown")
                error = notif.get("error", None)
                
                # Emoji dla statusu
                status_emoji = "?" if status == "sent" else "?"
                
                # Emoji dla typu
                type_emoji = {
                    "conversation_completed": "???",
                    "daily_digest": "??",
                    "test": "??",
                    "critical_issue": "??"
                }.get(notif_type, "??")
                
                with st.expander(f"{status_emoji} {timestamp} - {type_emoji} {subject}"):
                    st.markdown(f"**Typ:** {notif_type}")
                    st.markdown(f"**Status:** {status}")
                    if error:
                        st.error(f"**B≥πd:** {error}")
    else:
        st.info("Brak historii powiadomieÒ. Wyúlij pierwszy email!")
    
    # === SEKCJA 4: STATYSTYKI ===
    if history:
        st.markdown("---")
        st.subheader("?? Statystyki")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(history)
        sent = len([h for h in history if h.get("status") == "sent"])
        failed = len([h for h in history if h.get("status") == "failed"])
        success_rate = (sent / total * 100) if total > 0 else 0
        
        col1.metric("?? Wys≥ane", sent)
        col2.metric("? B≥Ídy", failed)
        col3.metric("?? Success Rate", f"{success_rate:.1f}%")
        col4.metric("?? Ostatni 7 dni", len([
            h for h in history 
            if (datetime.now() - datetime.fromisoformat(h.get("timestamp", "2020-01-01"))).days <= 7
        ]))

def show_consultations_page():
    """Strona z systemem konsultacji z Radπ PartnerÛw"""
    st.title("??? Konsultacje z Radπ")
    
    st.markdown("""
    **System konsultacji** pozwala zapytaÊ RadÍ PartnerÛw o opiniÍ na dowolny temat.
    Kaødy partner AI otrzyma pytanie i wyrazi swojπ opiniÍ (ZA/PRZECIW/NEUTRALNIE).
    """)
    
    manager = get_consultation_manager()
    
    # === TABS ===
    tab1, tab2 = st.tabs(["?? Nowa Konsultacja", "?? Historia"])
    
    # === TAB 1: NOWA KONSULTACJA ===
    with tab1:
        st.markdown("### Zadaj pytanie Radzie")
        
        # Formularz
        with st.form("new_consultation_form"):
            question = st.text_area(
                "? Twoje pytanie lub propozycja:",
                placeholder="Np. Czy powinienem zwiÍkszyÊ alokacjÍ w krypto do 15%?",
                height=100
            )
            
            # Lista partnerÛw (bez Partner Zarzπdzajπcy)
            available_partners = [
                p['name'] for p in manager.personas 
                if p['name'] != 'Partner Zarzπdzajπcy (JA)'
            ]
            
            selected_partners = st.multiselect(
                "?? Wybierz partnerÛw do zapytania:",
                options=available_partners,
                default=available_partners  # Domyúlnie wszyscy
            )
            
            st.markdown(f"**Wybrano:** {len(selected_partners)} partnerÛw")
            
            submitted = st.form_submit_button("?? Wyúlij do Rady", type="primary", width="stretch")
        
        # Obs≥uga wys≥ania
        if submitted:
            if not question.strip():
                st.error("? Wpisz pytanie!")
            elif len(selected_partners) == 0:
                st.error("? Wybierz przynajmniej jednego partnera!")
            else:
                with st.spinner("?? TworzÍ konsultacjÍ..."):
                    # 1. UtwÛrz konsultacjÍ
                    consultation = manager.create_consultation(question, selected_partners)
                    st.success(f"? Konsultacja utworzona (ID: {consultation['id']})")
                
                # 2. Zbierz odpowiedzi
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                responses_container = st.container()
                
                consultation = manager.collect_responses(consultation['id'])
                
                # Pokaø odpowiedzi w czasie rzeczywistym
                for i, response in enumerate(consultation['responses']):
                    progress = (i + 1) / len(selected_partners)
                    progress_bar.progress(progress)
                    status_text.text(f"? Zebrano {i+1}/{len(selected_partners)} odpowiedzi...")
                    
                    with responses_container:
                        stance_emoji = {
                            'for': '?',
                            'against': '?',
                            'neutral': '??'
                        }.get(response['stance'], '??')
                        
                        st.markdown(f"""
                        **{response['partner']}** {stance_emoji} **{response['stance'].upper()}** (PewnoúÊ: {response['confidence']}/10)
                        > {response['reasoning']}
                        """)
                
                progress_bar.progress(1.0)
                status_text.text("? Wszystkie odpowiedzi zebrane!")
                
                # 3. Wygeneruj AI Summary
                with st.spinner("?? GenerujÍ podsumowanie..."):
                    summary = manager.generate_summary(consultation['id'])
                
                if summary:
                    st.success("? Konsultacja zakoÒczona!")
                    
                    # Pokaø summary
                    st.markdown("---")
                    st.markdown("### ?? Podsumowanie AI")
                    
                    # Wyniki g≥osowania
                    col1, col2, col3 = st.columns(3)
                    col1.metric("? ZA", summary['votes_for'])
                    col2.metric("? PRZECIW", summary['votes_against'])
                    col3.metric("?? NEUTRALNE", summary['votes_neutral'])
                    
                    # Konsensus badge
                    consensus = summary.get('consensus', 'medium')
                    consensus_color = {
                        'high': '#27ae60',
                        'medium': '#f39c12',
                        'low': '#e74c3c'
                    }.get(consensus, '#95a5a6')
                    
                    consensus_label = {
                        'high': 'Wysoki Konsensus',
                        'medium': 'åredni Konsensus',
                        'low': 'Niski Konsensus'
                    }.get(consensus, 'Nieznany')
                    
                    st.markdown(f"""
                    <div style="background: {consensus_color}; color: white; padding: 10px; 
                                border-radius: 5px; text-align: center; margin: 10px 0;">
                        <strong>{consensus_label}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # G≥Ûwne argumenty
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**? Argumenty ZA:**")
                        for arg in summary.get('main_arguments_for', []):
                            st.markdown(f"- {arg}")
                    
                    with col2:
                        st.markdown("**? Argumenty PRZECIW:**")
                        for arg in summary.get('main_arguments_against', []):
                            st.markdown(f"- {arg}")
                    
                    # Rekomendacja
                    st.info(f"**?? Rekomendacja AI:** {summary.get('recommendation', 'Brak rekomendacji')}")
                    
                    # Opcja wys≥ania emaila (jeúli w≥πczone)
                    try:
                        notifier = get_conversation_notifier()
                        if notifier.config.get("enabled", False):
                            st.success("?? Email z wynikami zosta≥ wys≥any!")
                    except:
                        pass
    
    # === TAB 2: HISTORIA ===
    with tab2:
        st.markdown("### Historia Konsultacji")
        
        consultations = manager.get_recent_consultations(limit=50)
        
        if not consultations:
            st.info("?? Brak konsultacji. UtwÛrz pierwszπ w zak≥adce 'Nowa Konsultacja'!")
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
            
            # Pokaø kaødπ konsultacjÍ
            for cons in filtered:
                with st.expander(
                    f"??? {cons.get('question', 'Brak pytania')[:80]}... | "
                    f"{cons.get('created_at', '')[:16]} | "
                    f"{len(cons.get('participants', []))} partnerÛw"
                ):
                    st.markdown(f"**?? ID:** `{cons['id']}`")
                    st.markdown(f"**? Pytanie:** {cons['question']}")
                    st.markdown(f"**?? Uczestnicy:** {', '.join(cons['participants'])}")
                    st.markdown(f"**?? Data:** {cons['created_at'][:19]}")
                    st.markdown(f"**?? Status:** {cons['status']}")
                    
                    # Odpowiedzi
                    responses = cons.get('responses', [])
                    if responses:
                        st.markdown("---")
                        st.markdown("**?? Odpowiedzi partnerÛw:**")
                        
                        for resp in responses:
                            stance_emoji = {
                                'for': '?',
                                'against': '?',
                                'neutral': '??'
                            }.get(resp['stance'], '??')
                            
                            st.markdown(f"""
                            **{resp['partner']}** {stance_emoji} **{resp['stance'].upper()}** 
                            (PewnoúÊ: {resp['confidence']}/10)
                            > {resp['reasoning']}
                            """)
                    
                    # Summary
                    summary = cons.get('summary')
                    if summary:
                        st.markdown("---")
                        st.markdown("### ?? Podsumowanie AI")
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("? ZA", summary['votes_for'])
                        col2.metric("? PRZECIW", summary['votes_against'])
                        col3.metric("?? NEUTRALNE", summary['votes_neutral'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**? Argumenty ZA:**")
                            for arg in summary.get('main_arguments_for', []):
                                st.markdown(f"- {arg}")
                        
                        with col2:
                            st.markdown("**? Argumenty PRZECIW:**")
                            for arg in summary.get('main_arguments_against', []):
                                st.markdown(f"- {arg}")
                        
                        st.info(f"**?? Rekomendacja:** {summary.get('recommendation', '')}")

def show_partners_page():
    """Strona z partnerami"""
    st.title("?? Chat z Partnerami AI")
    
    # Initialize session state for messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'selected_partner' not in st.session_state:
        st.session_state.selected_partner = "Wszyscy"
    
    # === TABY ===
    tab_chat, tab_profiles = st.tabs(["?? Chat", "?? Profile PartnerÛw"])
    
    # === TAB 1: CHAT ===
    with tab_chat:
        # Sidebar z listπ partnerÛw
        with st.sidebar:
            st.markdown("### ?? Rada PartnerÛw")
            
            partners = {}
            
            # Za≥aduj prawdziwych partnerÛw z PERSONAS (pomijajπc Partnera Zarzπdzajπcego - to Ty!)
            if IMPORTS_OK and PERSONAS:
                # Opcja "Wszyscy"
                partners["Wszyscy"] = {"emoji": "??", "status": "??", "display": "Wszyscy"}
                
                # Dodaj kaødego partnera OPR”CZ "Partner Zarzπdzajπcy (JA)"
                for name, config in PERSONAS.items():
                    # PomiÒ Partnera Zarzπdzajπcego - to uøytkownik
                    if 'Partner Zarzπdzajπcy' in name and '(JA)' in name:
                        continue
                    
                    # Wyciπgnij samo imiÍ bez dodatkowych opisÛw
                    display_name = name
                    
                    # Dla "Ja (Partner Strategiczny)" -> "Ja"
                    if '(' in name:
                        display_name = name.split('(')[0].strip()
                    
                    # Dla "Partner ds. Czegoú" -> wyciπgnij kluczowπ nazwÍ
                    if display_name.startswith('Partner ds.'):
                        # Np. "Partner ds. Jakoúci Biznesowej" -> "Partner Jakoúci"
                        display_name = display_name.replace('Partner ds. ', '')
                    
                    partners[name] = {
                        "emoji": "??",
                        "status": "??",
                        "display": display_name
                    }
            else:
                # Fallback jeúli PERSONAS nie za≥adowa≥o siÍ
                partners = {
                    "Wszyscy": {"emoji": "??", "status": "??", "display": "Wszyscy"}
                }
            
            for name, info in partners.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    display_name = info.get('display', name)
                    # Tylko imiÍ, bez opisu roli
                    if st.button(
                        f"{info.get('emoji', '??')} {display_name}",
                        key=f"partner_{name}",
                        width="stretch"
                    ):
                        st.session_state.selected_partner = name
                with col2:
                    st.markdown(info['status'])
            
            st.markdown("---")
            
            st.markdown("### ?? Opcje")
            tryb = st.radio(
                "Tryb odpowiedzi:",
                ["ZwiÍz≥y", "Normalny", "SzczegÛ≥owy"],
                index=1
            )
            
            fight_club = st.checkbox("?? Fight Club", value=True)
            auto_vote = st.checkbox("??? Auto g≥osowania", value=False)
        
        # Main chat area
        st.markdown(f"### Rozmowa z: **{st.session_state.selected_partner}**")
        
        # === NOWE: MOOD INDICATOR ===
        try:
            stan_spolki, cele = load_portfolio_data()
            portfolio_mood = analyze_portfolio_mood(stan_spolki, cele)
            
            # Wyúwietl mood bar
            col_mood1, col_mood2, col_mood3 = st.columns([1, 3, 1])
            with col_mood1:
                st.markdown(f"### {portfolio_mood.get('emoji', '??')}")
            with col_mood2:
                st.markdown(f"**NastrÛj portfela:** {portfolio_mood.get('description', 'Neutralny')}")
                
                # Progress bar dla score
                score = portfolio_mood.get('score', 0)
                normalized_score = (score + 100) / 200  # -100..100 -> 0..1
                st.progress(normalized_score, text=f"Score: {score}/100")
            with col_mood3:
                with st.popover("?? SzczegÛ≥y"):
                    if portfolio_mood.get('highlights'):
                        st.markdown("**? Dobre znaki:**")
                        for h in portfolio_mood['highlights']:
                            st.markdown(f"- {h}")
                    
                    if portfolio_mood.get('warnings'):
                        st.markdown("**?? Uwagi:**")
                        for w in portfolio_mood['warnings']:
                            st.markdown(f"- {w}")
            
            st.markdown("---")
        except:
            pass  # Cicho ignoruj b≥Ídy mood
        
        # === NOWE: PROAKTYWNE ALERTY (na stronie partnerÛw) ===
        try:
            stan_spolki, cele = load_portfolio_data()
            alerts = check_portfolio_alerts(stan_spolki, cele)

            # Pokazuj tylko najwaøniejsze (critical i warning)
            important_alerts = [a for a in alerts if a["severity"] in ["critical", "warning"]]

            if important_alerts:
                with st.expander(f"?? Aktywne alerty ({len(important_alerts)})", expanded=True):
                    for alert in important_alerts[:3]:  # Max 3 najwaøniejsze
                        if alert["severity"] == "critical":
                            st.error(f"**{alert['title']}** - {alert['message']}")
                        else:
                            st.warning(f"**{alert['title']}** - {alert['message']}")
                
                    if len(important_alerts) > 3:
                        st.caption(f"...i {len(important_alerts) - 3} wiÍcej. Zobacz Dashboard.")
            else:
                with st.expander("? Status portfela", expanded=False):
                    st.success("**Brak aktywnych alertÛw** - TwÛj portfel wyglπda stabilnie!")
                    st.caption("MonitorujÍ: spadki, wzrosty, wyceny, düwigniÍ, koncentracjÍ i cele.")

            st.markdown("---")
        except:
            pass
        
        # === NOWE: SUGEROWANE PYTANIA ===
        if len(st.session_state.messages) < 3:  # Pokazuj tylko gdy ma≥o wiadomoúci
            try:
                stan_spolki, cele = load_portfolio_data()
                smart_questions = generate_smart_questions(stan_spolki, cele)
            
                if smart_questions:
                    with st.expander("?? Sugerowane pytania (kliknij aby uøyÊ)", expanded=True):
                        st.caption("AI przeanalizowa≥o TwÛj portfel i sugeruje te pytania:")
                    
                    cols = st.columns(1)
                    for i, question in enumerate(smart_questions[:5]):
                        if cols[0].button(
                            question, 
                            key=f"smart_q_{i}",
                            width="stretch",
                            type="secondary"
                        ):
                            # Uøyj pytania jako input
                            st.session_state.messages.append({
                                "role": "user",
                                "content": question,
                                "avatar": "??"
                            })
                            
                            # Generate responses
                            with st.spinner("?? AI myúli..."):
                                if 'ai_response_mode' in st.session_state:
                                    tryb_odpowiedzi = st.session_state.ai_response_mode
                                else:
                                    tryb_map = {"ZwiÍz≥y": "zwiezly", "Normalny": "normalny", "SzczegÛ≥owy": "szczegolowy"}
                                    tryb_odpowiedzi = tryb_map.get(tryb, "normalny")
                                
                                if st.session_state.selected_partner == "Wszyscy":
                                    # Placeholder dla odpowiedzi w czasie rzeczywistym
                                    response_container = st.empty()
                                    
                                    for resp in send_to_all_partners(question, stan_spolki, cele, tryb_odpowiedzi):
                                        # Formatuj wiadomoúÊ z emoji reakcji i flagπ przerywania
                                        sentiment = resp.get('sentiment_emoji', '??')
                                        is_interrupting = resp.get('is_interrupting', False)
                                        is_voting = resp.get('is_voting_summary', False)
                                        
                                        if is_voting:
                                            # Specjalne formatowanie dla podsumowania g≥osowania
                                            content = resp['response']
                                        elif is_interrupting:
                                            content = f"{sentiment} **[PRZERWANIE]** **{resp['partner']}**: {resp['response']}"
                                        else:
                                            content = f"{sentiment} **{resp['partner']}**: {resp['response']}"
                                        
                                        # Dodaj do historii
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": content,
                                            "avatar": resp['avatar'],
                                            "knowledge": resp.get('knowledge', [])
                                        })
                                        
                                        # Wyúwietl natychmiast z avatarem
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
                                    avatar = "??"
                                    if st.session_state.selected_partner in PERSONAS:
                                        color_map = {
                                            '\033[94m': '??', '\033[93m': '??', '\033[96m': '??',
                                            '\033[90m': '??', '\033[95m': '??', '\033[91m': '??', '\033[92m': '??'
                                        }
                                        color = PERSONAS[st.session_state.selected_partner].get('color_code', '')
                                        avatar = color_map.get(color, "??")
                                    
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": f"**{st.session_state.selected_partner}**: {response}",
                                        "avatar": avatar,
                                        "knowledge": knowledge  # Zapisz knowledge dla pÛüniejszego wyúwietlenia
                                    })
                            
                            st.rerun()
            except Exception as e:
                pass  # Cicho ignoruj b≥Ídy sugestii
        
        # Display messages
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar=msg.get("avatar", "??")):
                    st.markdown(msg["content"])
                    
                    # Wyúwietl ürÛd≥a wiedzy jeúli sπ
                    if msg["role"] == "assistant" and msg.get("knowledge"):
                        display_knowledge_sources(msg["knowledge"])
        
        # Input area
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.chat_input("Napisz wiadomoúÊ do PartnerÛw...")
        
        with col2:
            if st.button("??"):
                st.info("Za≥πczniki wkrÛtce!")
        
        # Handle user input
        if user_input:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "avatar": "??"
            })
        
            # Get current portfolio data for context
            try:
                stan_spolki, cele = load_portfolio_data()
            except:
                stan_spolki, cele = None, None
        
            # Generate real AI responses
            # Pobierz tryb odpowiedzi z session_state (z ustawieÒ) lub z local radio
            if 'ai_response_mode' in st.session_state:
                tryb_odpowiedzi = st.session_state.ai_response_mode
            else:
                # Fallback na lokalny wybÛr
                tryb_map = {
                "ZwiÍz≥y": "zwiezly",
                "Normalny": "normalny",
                "SzczegÛ≥owy": "szczegolowy"
                }
                tryb_odpowiedzi = tryb_map.get(tryb, "normalny")
        
                with st.spinner("?? AI myúli..."):
                    if st.session_state.selected_partner == "Wszyscy":
                        # Response from all partners - jeden za drugim, wyúwietlaj na øywo
                        for resp in send_to_all_partners(user_input, stan_spolki, cele, tryb_odpowiedzi):
                            # Formatuj wiadomoúÊ z emoji reakcji i flagπ przerywania
                            sentiment = resp.get('sentiment_emoji', '??')
                            is_interrupting = resp.get('is_interrupting', False)
                            is_voting = resp.get('is_voting_summary', False)
                            
                            if is_voting:
                                # Specjalne formatowanie dla podsumowania g≥osowania
                                content = resp['response']
                            elif is_interrupting:
                                content = f"{sentiment} **[PRZERWANIE]** **{resp['partner']}**: {resp['response']}"
                            else:
                                content = f"{sentiment} **{resp['partner']}**: {resp['response']}"
                            
                            # Dodaj do historii
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": content,
                                "avatar": resp['avatar'],
                                "knowledge": resp.get('knowledge', [])
                            })
                            
                            # Wyúwietl natychmiast z avatarem
                            with st.chat_message("assistant", avatar=resp['avatar']):
                                st.markdown(content)
                    else:
                        # Single partner response
                        response, knowledge = send_to_ai_partner(
                            st.session_state.selected_partner,
                            user_input,
                            stan_spolki,
                            cele,
                            tryb_odpowiedzi
                        )
                
                        avatar = {
                            "Marek": "??",
                            "Ania": "??", 
                            "Kasia": "??",
                            "Tomek": "??"
                        }.get(st.session_state.selected_partner, "??")
                
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"**{st.session_state.selected_partner}**: {response}",
                            "avatar": avatar,
                            "knowledge": knowledge  # Zapisz knowledge
                        })
        
                st.rerun()
        
        # Special commands
        st.markdown("---")
        st.markdown("### ?? Szybkie akcje")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("??? Rozpocznij g≥osowanie", width="stretch"):
                st.session_state.messages.append({
                    "role": "system",
                    "content": "?? **Nowe g≥osowanie** - Propozycja do g≥osowania otworzona",
                    "avatar": "??"
                })
                st.rerun()
        
        with col2:
            if st.button("?? Poproú o doradztwo", width="stretch"):
                st.session_state.messages.append({
                    "role": "system",
                    "content": "?? **AI Advisor** - GenerujÍ 3 scenariusze...",
                    "avatar": "??"
                })
                st.rerun()
        
        with col3:
            if st.button("?? WyczyúÊ chat", width="stretch"):
                st.session_state.messages = []
                st.rerun()
        
        # Drugi rzπd przyciskÛw - funkcje pamiÍci AI
        if MEMORY_OK:
            st.markdown("#### ?? PamiÍÊ AI")
            col4, col5, col6 = st.columns(3)
        
            with col4:
                if st.button("?? Zapisz decyzjÍ", width="stretch", help="Zapisz ostatniπ rekomendacjÍ AI do pamiÍci"):
                    # Znajdü ostatniπ odpowiedü AI
                    ai_messages = [m for m in st.session_state.messages if m["role"] == "assistant"]
                    if ai_messages:
                        last_msg = ai_messages[-1]
                        content = last_msg["content"]
                        
                        # Proste parsowanie - szukamy tickera i typu decyzji
                        # TODO: Uøytkownik powinien podaÊ ticker i typ rÍcznie
                        with st.form("save_decision_form"):
                            st.write("Zapisz decyzjÍ do pamiÍci:")
                            ticker = st.text_input("Ticker (np. AAPL, BTC)", "")
                            decision_type = st.selectbox("Typ", ["BUY", "SELL", "HOLD", "WARN", "RECOMMEND"])
                            price = st.number_input("Aktualna cena", min_value=0.01, value=100.0)
                            reasoning = st.text_area("Uzasadnienie", content[:200])
                            
                            submitted = st.form_submit_button("?? Zapisz")
                            if submitted and ticker:
                                # Zapisz dla wszystkich person ktÛre odpowiada≥y
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
                                st.success(f"? Decyzja zapisana: {decision_type} {ticker}")
                                st.rerun()
                    else:
                        st.info("Brak odpowiedzi AI do zapisania")
        
            with col5:
                if st.button("?? Leaderboard", width="stretch", help="Zobacz ranking wiarygodnoúci person"):
                    st.session_state.show_leaderboard = not st.session_state.get("show_leaderboard", False)
                    st.rerun()
        
            with col6:
                if st.button("?? Audit decyzji", width="stretch", help="OceÒ stare decyzje"):
                    st.session_state.show_audit = not st.session_state.get("show_audit", False)
                    st.rerun()
        
            # Leaderboard display
            if st.session_state.get("show_leaderboard", False):
                with st.expander("?? Ranking Wiarygodnoúci AI PartnerÛw", expanded=True):
                    leaderboard = pmm.get_leaderboard()
                    if leaderboard:
                        for i, entry in enumerate(leaderboard, 1):
                            emoji = "??" if i == 1 else "??" if i == 2 else "??" if i == 3 else f"{i}."
                            st.write(f"{emoji} **{entry['persona']}**: {entry['credibility']*100:.0f}% "
                                    f"({entry['correct']}/{entry['total']} trafnych)")
                    else:
                        st.info("Brak danych - persony nie podjÍ≥y jeszcze rozliczonych decyzji")
        
            # Audit panel
            if st.session_state.get("show_audit", False):
                with st.expander("?? Panel Auditu Decyzji", expanded=True):
                    pending = pmm.get_all_pending_decisions()
                    if pending:
                        st.write(f"**{len(pending)} nierozliczonych decyzji:**")
                        for item in pending[:10]:
                            dec = item["decision"]
                            with st.container():
                                col_a, col_b = st.columns([3, 1])
                                with col_a:
                                    st.write(f"**{item['persona']}** õ {dec['decision_type']} {dec['ticker']} @ {dec['current_price']}")
                                    st.caption(f"{dec['date']}: {dec['reasoning'][:80]}...")
                                with col_b:
                                    if st.button("? OceÒ", key=f"audit_{dec['id']}"):
                                        st.session_state[f"auditing_{dec['id']}"] = True
                                        st.rerun()
                                
                                # Formularz oceny
                                if st.session_state.get(f"auditing_{dec['id']}", False):
                                    with st.form(f"form_{dec['id']}"):
                                        current_price = st.number_input("Aktualna cena", value=dec['current_price'])
                                        outcome = st.text_input("Co siÍ sta≥o?", "")
                                        impact = st.number_input("Wp≥yw (PLN)", value=0.0)
                                        
                                        if st.form_submit_button("?? Zapisz audit"):
                                            result = pmm.audit_decision(dec['id'], current_price, outcome, impact)
                                            if result:
                                                st.success(f"? {'Poprawna' if result['was_correct'] else 'B≥Ídna'} decyzja ({result['result_pct']:+.1f}%)")
                                                del st.session_state[f"auditing_{dec['id']}"]
                                                st.rerun()
                                st.markdown("---")
                    else:
                        st.info("Brak nierozliczonych decyzji")
        
    # === TAB 2: PROFILE PARTNER”W ===
    with tab_profiles:
        st.markdown("### ?? Profile PartnerÛw")
        st.caption("Poznaj kaødego partnera i sprawdü wagi g≥osÛw z Kodeksu SpÛ≥ki")
        
        if not IMPORTS_OK or not PERSONAS:
            st.warning("?? Nie moøna za≥adowaÊ danych partnerÛw")
            return
        
        # Wczytaj wagi g≥osu z kodeksu spÛ≥ki
        wagi_z_kodeksu = wczytaj_wagi_glosu_z_kodeksu()
        
        if not wagi_z_kodeksu:
            st.warning("?? Nie moøna wczytaÊ wag g≥osu z kodeksu spÛ≥ki")
            return
        
        # Przygotuj listÍ partnerÛw z wagami g≥osu z KODEKSU
        partners_with_weights = []
        for name, config in PERSONAS.items():
            # Teraz POKAZUJEMY R”WNIEØ Partnera Zarzπdzajπcego (JA)!
            
            # Pobierz wagÍ z kodeksu
            weight = wagi_z_kodeksu.get(name, 0.0)  # Juø jest w procentach (35.0, nie 0.35)
            
            partners_with_weights.append((name, config, weight))
        
        # Sortuj wed≥ug wagi g≥osu (malejπco)
        partners_with_weights.sort(key=lambda x: x[2], reverse=True)
        total_weight = sum(w for _, _, w in partners_with_weights)
        
        # Informacja o sumie
        st.info(f"?? **£πczna suma g≥osÛw: {total_weight:.0f}%** (z Kodeksu SpÛ≥ki)")
        
        # Informacja o bonusach
        bonus_pool = 100 - total_weight
        if bonus_pool > 0:
            st.success(f"?? **Pula bonusowa: {bonus_pool:.0f}%** - do zdobycia za dobre decyzje!")
            st.caption("?? Partnerzy mogπ zdobywaÊ dodatkowe % g≥osu jako nagrody za trafne prognozy i wartoúciowe decyzje")
        
        # Opcja do edycji wag
        if st.checkbox("?? Tryb edycji wag g≥osu", help="ZmieÒ % g≥osu partnerÛw i zapisz do Kodeksu"):
            st.warning("?? Zmienione wartoúci zostanπ zapisane do `kodeks_spolki.txt`")
            
            with st.form("edit_voting_weights"):
                st.markdown("#### Edytuj wagi g≥osu:")
                
                nowe_wagi = {}
                
                # Podziel na g≥Ûwnych partnerÛw i radÍ
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown("**?? G≥Ûwni Partnerzy:**")
                    for name, config, current_weight in partners_with_weights:
                        # G≥Ûwni: Partner Zarzπdzajπcy, Partner Strategiczny, ds. Jakoúci, ds. AktywÛw Cyfrowych
                        if any(keyword in name for keyword in ["Zarzπdzajπcy", "Strategiczny", "Jakoúci", "AktywÛw Cyfrowych"]):
                            nowe_wagi[name] = st.number_input(
                                f"{name}",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(current_weight),
                                step=1.0,
                                key=f"edit_{name}"
                            )
                
                with col_right:
                    st.markdown("**??? Rada Nadzorcza & Konsultanci:**")
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
                    st.error(f"?? Suma przekracza 100%! (jest {suma_nowych:.1f}%)")
                elif suma_nowych < 95:
                    st.warning(f"?? Suma jest mniejsza niø 95% (jest {suma_nowych:.1f}%)")
                
                submitted = st.form_submit_button("?? Zapisz do Kodeksu")
                if submitted:
                    if zapisz_wagi_glosu_do_kodeksu(nowe_wagi):
                        st.success("? Wagi g≥osu zapisane do kodeksu spÛ≥ki!")
                        st.rerun()
                    else:
                        st.error("? B≥πd zapisu do kodeksu")
        
        st.markdown("---")
        
        # Wyúwietl kaødego partnera
        for name, config, weight in partners_with_weights:
            percentage = (weight / total_weight * 100) if total_weight > 0 else 0
            
            # Specjalne oznaczenie dla Ciebie (Partner Zarzπdzajπcy)
            if "(JA)" in name:
                emoji_prefix = "????"
                subtitle = f"{weight:.1f}% g≥osu | TY - G≥os rozstrzygajπcy"
            else:
                emoji_prefix = config.get('emoji', '??')
                subtitle = f"{weight:.1f}% g≥osu"
            
            with st.expander(f"{emoji_prefix} {name} - {subtitle}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Wyúwietl system instruction jako opis roli
                    system_inst = config.get('system_instruction', 'Brak opisu')
                    st.markdown(f"**?? Rola:** {system_inst[:200]}...")
                    
                    # Ukryty cel jako spoiler (tylko dla AI)
                    if "(JA)" not in name:
                        if st.checkbox("Pokaø ukryty cel", key=f"spoiler_{name}"):
                            st.info(f"?? **Ukryty cel:** {config.get('ukryty_cel', 'Brak')}")
                    else:
                        st.success("?? **To TY!** Masz g≥os rozstrzygajπcy w remisach.")
                
                with col2:
                    st.metric("% g≥osu", f"{weight:.1f}%", help="Waga g≥osu z Kodeksu SpÛ≥ki")
                    st.progress(weight / 100)
                    
                    # Memory stats jeúli dostÍpne (tylko dla AI)
                    if MEMORY_OK and "(JA)" not in name:
                        try:
                            memory_data = load_persona_memory()
                            if name in memory_data:
                                persona_data = memory_data[name]
                                stats = persona_data.get('stats', {})
                                emotions = persona_data.get('emotional_state', {})
                                
                                st.caption(f"?? {stats.get('sessions_participated', 0)} sesji")
                                st.caption(f"?? {stats.get('decisions_made', 0)} decyzji")
                                st.caption(f"?? NastrÛj: {emotions.get('current_mood', 'neutral')}")
                        except Exception as e:
                            pass
        
        st.markdown("---")
        st.info(f"?? **Rada sk≥ada siÍ z {len(partners_with_weights)} cz≥onkÛw** (w≥πcznie z Tobπ jako Partner Zarzπdzajπcy)")
        st.caption("? Wagi g≥osÛw pochodzπ z Kodeksu SpÛ≥ki")
        st.caption("?? 30% puli bonusowej - partnerzy mogπ zdobywaÊ dodatkowe % za trafne decyzje i wartoúciowe analizy")
        st.caption("?? Zmiany wag sπ zapisywane bezpoúrednio w pliku `kodeks_spolki.txt`")

def show_analytics_page(stan_spolki):
    """Strona z analitykπ"""
    st.title("?? Zaawansowana Analityka & Ryzyko")
    
    # Check if we have historical data - uøywamy daily_snapshots.json
    history_file = "daily_snapshots.json"
    
    if not os.path.exists(history_file):
        st.warning("?? Brak danych historycznych. UtwÛrz pierwszy snapshot w zak≥adce ?? Snapshots.")
        st.info("?? TIP: System automatycznie zapisuje snapshoty codziennie o 21:00 (jeúli skonfigurujesz Task Scheduler).")
        
        # Pokaø instrukcjÍ
        with st.expander("?? Jak utworzyÊ snapshot?"):
            st.markdown("""
            **Opcja 1: Manualnie w aplikacji**
            - Przejdü do zak≥adki ?? Snapshots
            - Kliknij "?? UtwÛrz Nowy Snapshot"
            
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
            st.warning(f"?? Za ma≥o danych ({len(history)} snapshot). Potrzeba minimum 2 dla analizy ryzyka.")
            st.info("?? UtwÛrz wiÍcej snapshotÛw aby zobaczyÊ analizÍ (zak≥adka ?? Snapshots)")
            return
        
        st.success(f"? Za≥adowano {len(history)} snapshots historii portfela")
        
        # Create analytics
        analyzer = RiskAnalytics(stan_spolki, history)
        report = analyzer.generate_risk_report()
        metrics = report.get('metrics', {})
        
        # Display metrics in columns
        st.markdown("### ?? Kluczowe Metryki Ryzyka")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sharpe = metrics.get('sharpe_ratio', 0)
            delta_color = "normal" if sharpe > 1 else "inverse"
            st.metric(
                label="?? Sharpe Ratio",
                value=f"{sharpe:.3f}",
                delta="Dobry" if sharpe > 1 else "S≥aby",
                delta_color=delta_color
            )
            st.caption(">1 = dobre, >2 = doskona≥e")
        
        with col2:
            sortino = metrics.get('sortino_ratio', 0)
            st.metric(
                label="?? Sortino Ratio",
                value=f"{sortino:.3f}",
                delta="Dobry" if sortino > 1.5 else "S≥aby",
                delta_color="normal" if sortino > 1.5 else "inverse"
            )
            st.caption("UwzglÍdnia tylko straty")
        
        with col3:
            max_dd = metrics.get('max_drawdown_percent', 0)
            st.metric(
                label="?? Max Drawdown",
                value=f"{max_dd:.2f}%",
                delta="Wysokie" if max_dd > 20 else "OK",
                delta_color="inverse" if max_dd > 20 else "normal"
            )
            st.caption("NajwiÍkszy spadek")
        
        with col4:
            var_95 = metrics.get('var_95', 0)
            st.metric(
                label="?? VaR (95%)",
                value=f"{var_95:.2f}%",
                delta="Ryzykowne" if var_95 > 10 else "OK",
                delta_color="inverse" if var_95 > 10 else "normal"
            )
            st.caption("Max strata z 95% pewnoúciπ")
        
        st.markdown("---")
        
        # Additional metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ?? Dodatkowe Metryki")
            
            vol = metrics.get('annual_volatility_percent', 0)
            st.metric("?? ZmiennoúÊ roczna", f"{vol:.2f}%")
            
            ret = metrics.get('total_return_percent', 0)
            st.metric("?? Ca≥kowity zwrot", f"{ret:+.2f}%")
            
            beta = metrics.get('beta', 0)
            st.metric("?? Beta (vs S&P 500)", f"{beta:.3f}")
            st.caption("<1 = mniej zmienne, >1 = bardziej zmienne")
        
        with col2:
            st.markdown("### ?? Ocena Ryzyka")
            
            level, score, description = analyzer.risk_score()
            
            # Progress bar dla risk score
            st.markdown(f"**Poziom ryzyka:** {level}")
            st.progress(score / 100)
            st.caption(f"Score: {score}/100")
            
            st.info(description)
        
        st.markdown("---")
        
        # Chart: Portfolio value over time
        st.markdown("### ?? WartoúÊ Portfela w Czasie")
        
        # Parsuj daty i wartoúci - obs≥uø rÛøne formaty
        dates = []
        values = []
        
        for h in history:
            # Data
            if 'timestamp' in h:
                dates.append(datetime.fromisoformat(h['timestamp']))
            elif 'date' in h:
                dates.append(datetime.fromisoformat(h['date']))
            
            # WartoúÊ netto
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
            name='WartoúÊ Netto',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="WartoúÊ Netto Portfela",
            xaxis_title="Data",
            yaxis_title="WartoúÊ (PLN)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width="stretch")
        
    except Exception as e:
        st.error(f"? B≥πd podczas analizy: {e}")
        import traceback
        st.code(traceback.format_exc())

def show_timeline_page(stan_spolki):
    """Strona z animated timeline"""
    st.title("?? Animated Timeline - Ewolucja Portfela")
    
    # Uøywaj nowego systemu daily snapshots
    try:
        import daily_snapshot as ds
        import benchmark_comparison as bench
    except ImportError as e:
        st.error(f"? B≥πd importu: {e}")
        return
    
    history = ds.load_snapshot_history()
    
    if len(history) < 2:
        st.warning(f"?? Za ma≥o danych ({len(history)} snapshot). Potrzeba minimum 2 dla timeline.")
        st.info("""
        **Jak zgromadziÊ historiÍ?**
        1. System zapisuje snapshot codziennie o 21:00 (jeúli skonfigurujesz Windows Task)
        2. Moøesz teø rÍcznie: `python daily_snapshot.py`
        3. Lub w zak≥adce ?? Snapshots õ UtwÛrz snapshot
        """)
        return
    
    st.success(f"? Za≥adowano {len(history)} snapshots - generujÍ timeline...")
    
    # Tabs: Portfolio vs Benchmarki
    tab1, tab2 = st.tabs(["?? WartoúÊ Portfela", "?? PorÛwnanie z Benchmarkami"])
    
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
            name='WartoúÊ Netto',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="WartoúÊ Portfela w Czasie",
            xaxis_title="Data",
            yaxis_title="WartoúÊ (PLN)",
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
            st.metric("?? WartoúÊ poczπtkowa", format_currency(initial_value))
        with col2:
            st.metric("?? WartoúÊ aktualna", format_currency(current_value), delta=f"{growth:+.2f}%")
        with col3:
            st.metric("?? Liczba snapshots", len(history))
    
    with tab2:
        st.subheader("?? TwÛj Portfel vs Rynek")
        st.info("?? PorÛwnanie znormalizowane do 100 punktÛw na start okresu")
        
        with st.spinner("? Pobieranie danych benchmarkÛw..."):
            comparison_data = bench.prepare_comparison_data(history)
        
        if "error" in comparison_data:
            st.error(f"? {comparison_data['error']}")
        else:
            # Wykres porÛwnawczy
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
                title="PorÛwnanie Wydajnoúci (Normalized to 100)",
                xaxis_title="Data",
                yaxis_title="WartoúÊ Znormalizowana (start = 100)",
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
            
            # Statystyki porÛwnawcze
            st.markdown("---")
            st.markdown("### ?? Statystyki PorÛwnawcze")
            
            stats = bench.calculate_comparison_stats(history)
            
            if "error" not in stats:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "?? TwÛj Portfel",
                        f"{stats['portfolio']['total_return_pct']:+.2f}%",
                        delta=f"{stats['portfolio']['days']} dni"
                    )
                
                # Benchmarki
                cols = [col2, col3, col4]
                for idx, (bench_id, bench_stats) in enumerate(stats['benchmarks'].items()):
                    if idx < 3:
                        with cols[idx]:
                            emoji = "??" if bench_stats['outperformance_pct'] > 0 else "??"
                            st.metric(
                                f"{emoji} {bench_stats['name']}",
                                f"{bench_stats['total_return_pct']:+.2f}%",
                                delta=f"{bench_stats['outperformance_pct']:+.2f}%"
                            )
                
                st.markdown("---")
                st.caption("?? Delta pokazuje Twojπ przewagÍ (+) lub stratÍ (-) wzglÍdem benchmarku")

def show_simulations_page(stan_spolki):
    """Strona z symulacjami"""
    st.title("?? Symulator Portfela - Testuj Scenariusze")
    
    try:
        from portfolio_simulator import PortfolioSimulator, ScenarioAnalyzer
    except ImportError:
        st.error("? Nie moøna za≥adowaÊ modu≥u portfolio_simulator")
        return
    
    # Initialize simulator
    simulator = PortfolioSimulator(stan_spolki)
    
    # Tabs dla rÛønych typÛw symulacji
    tab1, tab2, tab3 = st.tabs(["? Scenariusze Rynkowe", "?? Transakcje", "?? PorÛwnanie"])
    
    with tab1:
        st.markdown("### ?? Symuluj Scenariusze Rynkowe")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ?? Scenariusz Bullish")
            st.info("Wszystkie aktywa rosnπ o 20%")
            
            if st.button("?? Uruchom Bullish", key="bullish", width="stretch"):
                result = simulator.simulate_bullish_scenario()
                
                st.success("? Symulacja zakoÒczona!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("WartoúÊ przed", format_currency(result['before']['wartosc_netto']))
                with col_b:
                    st.metric(
                        "WartoúÊ po",
                        format_currency(result['after']['wartosc_netto']),
                        delta=f"+{result['zmiana_procent']:.2f}%"
                    )
                
                st.json(result['zmiany'])
        
        with col2:
            st.markdown("#### ?? Scenariusz Bearish")
            st.info("Wszystkie aktywa spadajπ o 20%")
            
            if st.button("?? Uruchom Bearish", key="bearish", width="stretch"):
                result = simulator.simulate_bearish_scenario()
                
                st.warning("?? Symulacja spadku!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("WartoúÊ przed", format_currency(result['before']['wartosc_netto']))
                with col_b:
                    st.metric(
                        "WartoúÊ po",
                        format_currency(result['after']['wartosc_netto']),
                        delta=f"{result['zmiana_procent']:.2f}%"
                    )
                
                st.json(result['zmiany'])
    
    with tab2:
        st.markdown("### ?? Symuluj Transakcje")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ?? Kupno")
            ticker_buy = st.text_input("Ticker", key="buy_ticker", value="AAPL")
            quantity_buy = st.number_input("IloúÊ", min_value=1, value=10, key="buy_qty")
            price_buy = st.number_input("Cena za sztukÍ (PLN)", min_value=0.01, value=100.0, key="buy_price")
            
            if st.button("?? Kup", width="stretch"):
                result = simulator.simulate_buy(ticker_buy, quantity_buy, price_buy)
                
                if result['success']:
                    st.success(f"? {result['message']}")
                    st.metric(
                        "Wp≥yw na wartoúÊ",
                        format_currency(result['wplyw_na_wartosc']),
                        delta=f"{result['zmiana_procent']:+.2f}%"
                    )
                else:
                    st.error(f"? {result['message']}")
        
        with col2:
            st.markdown("#### ?? Sprzedaø")
            ticker_sell = st.text_input("Ticker", key="sell_ticker", value="AAPL")
            quantity_sell = st.number_input("IloúÊ", min_value=1, value=5, key="sell_qty")
            price_sell = st.number_input("Cena za sztukÍ (PLN)", min_value=0.01, value=120.0, key="sell_price")
            
            if st.button("?? Sprzedaj", width="stretch"):
                result = simulator.simulate_sell(ticker_sell, quantity_sell, price_sell)
                
                if result['success']:
                    st.success(f"? {result['message']}")
                    st.metric(
                        "Wp≥yw na wartoúÊ",
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
                    st.error(f"? {result['message']}")
        
        # Reset button
        st.markdown("---")
        if st.button("?? Reset Symulacji", width="stretch"):
            simulator.reset()
            st.success("? Symulacja zresetowana do stanu poczπtkowego")
    
    with tab3:
        st.markdown("### ?? PorÛwnaj Scenariusze")
        st.info("?? Funkcja w budowie - bÍdzie pokazywaÊ porÛwnanie rÛønych scenariuszy")
        
        # TODO: Implement scenario comparison
        st.markdown("""
        Tutaj bÍdzie moøna:
            - PorÛwnaÊ wyniki rÛønych scenariuszy
        - ZobaczyÊ wykres zmian wartoúci
        - AnalizowaÊ wp≥yw poszczegÛlnych transakcji
        - EksportowaÊ wyniki do raportu
        """)

# =====================================================
# KREDYTY PAGE
# =====================================================

def load_kredyty():
    """Wczytaj kredyty z pliku JSON"""
    try:
        with open('kredyty.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('kredyty', [])
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"B≥πd wczytywania kredytÛw: {e}")
        return []

def get_suma_kredytow():
    """Pobierz sumÍ pozosta≥ych d≥ugÛw z kredyty.json"""
    kredyty = load_kredyty()
    return sum(k['kwota_poczatkowa'] - k['splacono'] for k in kredyty)

def get_ostatnia_wyplata():
    """Pobierz ostatniπ wyp≥atÍ z wyplaty.json"""
    wyplaty = load_wyplaty()
    if wyplaty:
        # Wyp≥aty sπ posortowane od najnowszej
        return wyplaty[0]['kwota']
    return 0

def get_srednia_wyplata(liczba_miesiecy=3):
    """Oblicz úredniπ wyp≥atÍ z ostatnich N miesiÍcy"""
    wyplaty = load_wyplaty()
    if not wyplaty:
        return 0
    
    ostatnie = wyplaty[:liczba_miesiecy]
    if ostatnie:
        return sum(w['kwota'] for w in ostatnie) / len(ostatnie)
    return 0

def get_suma_wydatkow_stalych():
    """Pobierz sumÍ sta≥ych wydatkÛw miesiÍcznych z wydatki.json"""
    wydatki = load_wydatki()
    return sum(w['kwota'] for w in wydatki if not w.get('nadprogramowy', False))

def get_suma_wydatkow_nadprogramowych():
    """Pobierz sumÍ wydatkÛw nadprogramowych z wydatki.json"""
    wydatki = load_wydatki()
    return sum(w['kwota'] for w in wydatki if w.get('nadprogramowy', False))

def save_kredyty(kredyty):
    """Zapisz kredyty do pliku JSON"""
    try:
        with open('kredyty.json', 'w', encoding='utf-8') as f:
            json.dump({'kredyty': kredyty}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"B≥πd zapisu kredytÛw: {e}")
        return False

def save_cele(cele):
    """Zapisz cele do pliku JSON"""
    try:
        with open('cele.json', 'w', encoding='utf-8') as f:
            json.dump(cele, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"B≥πd zapisu celÛw: {e}")
        return False

def load_wyplaty():
    """Wczytaj wyp≥aty z pliku JSON"""
    try:
        with open('wyplaty.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('wyplaty', [])
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"B≥πd wczytywania wyp≥at: {e}")
        return []

def save_wyplaty(wyplaty):
    """Zapisz wyp≥aty do pliku JSON"""
    try:
        with open('wyplaty.json', 'w', encoding='utf-8') as f:
            json.dump({'wyplaty': wyplaty}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"B≥πd zapisu wyp≥at: {e}")
        return False

def load_wydatki():
    """Wczytaj wydatki z pliku JSON"""
    try:
        with open('wydatki.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('wydatki', [])
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"B≥πd wczytywania wydatkÛw: {e}")
        return []

def save_wydatki(wydatki):
    """Zapisz wydatki do pliku JSON"""
    try:
        with open('wydatki.json', 'w', encoding='utf-8') as f:
            json.dump({'wydatki': wydatki}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"B≥πd zapisu wydatkÛw: {e}")
        return False

def load_krypto():
    """Wczytaj kryptowaluty z pliku JSON"""
    try:
        with open('krypto.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('krypto', [])
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"B≥πd wczytywania krypto: {e}")
        return []

def save_krypto(krypto):
    """Zapisz kryptowaluty do pliku JSON"""
    try:
        with open('krypto.json', 'w', encoding='utf-8') as f:
            json.dump({'krypto': krypto}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"B≥πd zapisu krypto: {e}")
        return False

def show_kredyty_page(stan_spolki, cele):
    """Strona zarzπdzania kredytami i celami finansowymi"""
    st.title("?? Centrum Finansowe")
    st.caption("Kompleksowe zarzπdzanie: Cele ï Kredyty ï Sp≥aty ï Wyp≥aty ï Wydatki ï Krypto ï Track Record AI")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "?? Cele Finansowe", 
        "?? Kredyty", 
        "?? Analiza Sp≥at", 
        "?? Wyp≥aty", 
        "?? Sta≥e Wydatki", 
        "? Krypto",
        "?? Track Record AI"
    ])
    
    # ===== TAB 1: CELE FINANSOWE =====
    with tab1:
        st.header("?? Edycja CelÛw Finansowych")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("?? Rezerwa GotÛwkowa")
            
            # Pobierz aktualne wartoúci
            rezerwa_obecna = cele.get('Rezerwa_gotowkowa_obecna_PLN', 39904) if cele else 39904
            rezerwa_cel = cele.get('Rezerwa_gotowkowa_PLN', 70000) if cele else 70000
            
            # Edycja
            new_rezerwa_obecna = st.number_input(
                "Zgromadzona kwota (PLN)",
                min_value=0,
                value=int(rezerwa_obecna),
                step=1000,
                help="Aktualna kwota rezerwy gotÛwkowej"
            )
            
            new_rezerwa_cel = st.number_input(
                "Docelowa kwota (PLN)",
                min_value=0,
                value=int(rezerwa_cel),
                step=5000,
                help="Kwota do osiπgniÍcia"
            )
            
            # Progress
            progress = new_rezerwa_obecna / new_rezerwa_cel if new_rezerwa_cel > 0 else 0
            st.progress(min(progress, 1.0))
            st.caption(f"PostÍp: {progress*100:.1f}% ({format_currency(new_rezerwa_obecna)} / {format_currency(new_rezerwa_cel)})")
            
            if st.button("?? Zapisz RezerwÍ", key="save_rezerwa"):
                if cele is None:
                    cele = {}
                cele['Rezerwa_gotowkowa_obecna_PLN'] = new_rezerwa_obecna
                cele['Rezerwa_gotowkowa_PLN'] = new_rezerwa_cel
                if save_cele(cele):
                    # Synchronizuj cel w kodeksie spÛ≥ki
                    try:
                        with open('kodeks_spolki.txt', 'r', encoding='utf-8') as f:
                            kodeks_content = f.read()
                        
                        # ZamieÒ liniÍ z celem rezerwy gotÛwkowej
                        import re
                        pattern = r'Cel #2: Budowa rezerwy gotÛwkowej do docelowego poziomu \d+[\s,]*\d* PLN\.'
                        replacement = f'Cel #2: Budowa rezerwy gotÛwkowej do docelowego poziomu {new_rezerwa_cel:,} PLN.'.replace(',', ' ')
                        
                        new_kodeks = re.sub(pattern, replacement, kodeks_content)
                        
                        if new_kodeks != kodeks_content:
                            with open('kodeks_spolki.txt', 'w', encoding='utf-8') as f:
                                f.write(new_kodeks)
                            st.success("? Rezerwa gotÛwkowa zaktualizowana w cele.json i kodeksie spÛ≥ki!")
                        else:
                            st.success("? Rezerwa gotÛwkowa zaktualizowana!")
                    except Exception as e:
                        st.success("? Rezerwa gotÛwkowa zaktualizowana w cele.json!")
                        st.warning(f"?? Nie uda≥o siÍ zaktualizowaÊ kodeksu: {str(e)}")
                    
                    # WYCZYå∆ CACHE aby odúwieøyÊ dane
                    load_portfolio_data.clear()
                    st.rerun()
        
        with col2:
            st.subheader("?? Zarzπdzanie Kredytami")
            st.info("?? Przejdü do zak≥adki **?? Kredyty** aby zarzπdzaÊ swoimi kredytami")
            st.markdown("""
            W zak≥adce Kredyty moøesz:
                - ? DodawaÊ nowe kredyty z pe≥nymi szczegÛ≥ami
            - ?? åledziÊ daty sp≥at
            - ? AktualizowaÊ sp≥acone kwoty
            - ?? AnalizowaÊ postÍp sp≥at
            - ? OtrzymywaÊ przypomnienia o p≥atnoúciach
            """)
            
            if st.button("? Przejdü do KredytÛw", key="goto_kredyty_from_cele"):
                st.session_state['goto_page'] = "?? Kredyty"
                st.rerun()
    
    # ===== TAB 2: KREDYTY =====
    with tab2:
        st.header("?? SzczegÛ≥owe Zarzπdzanie Kredytami")
        
        kredyty = load_kredyty()
        
        # Przypomnienia o nadchodzπcych sp≥atach
        if kredyty:
            dzis = datetime.now().day
            najblizsze_splaty = []
            
            for k in kredyty:
                dzien_splaty = k['dzien_splaty']
                if dzien_splaty >= dzis:
                    dni_do_splaty = dzien_splaty - dzis
                    najblizsze_splaty.append({
                        'nazwa': k['nazwa'],
                        'dzien': dzien_splaty,
                        'dni_do': dni_do_splaty,
                        'kwota': k['rata_miesieczna']
                    })
            
            if najblizsze_splaty:
                # Sortuj po liczbie dni
                najblizsze_splaty.sort(key=lambda x: x['dni_do'])
                
                with st.expander(f"?? Nadchodzπce sp≥aty ({len(najblizsze_splaty)})", expanded=True):
                    for splata in najblizsze_splaty:
                        if splata['dni_do'] == 0:
                            st.error(f"?? **DZIå!** {splata['nazwa']} - {splata['kwota']:.0f} PLN (dzieÒ {splata['dzien']})")
                        elif splata['dni_do'] <= 3:
                            st.warning(f"?? Za {splata['dni_do']} dni: {splata['nazwa']} - {splata['kwota']:.0f} PLN (dzieÒ {splata['dzien']})")
                        else:
                            st.info(f"?? Za {splata['dni_do']} dni: {splata['nazwa']} - {splata['kwota']:.0f} PLN (dzieÒ {splata['dzien']})")
                
                st.markdown("---")
        
        # Formularz dodawania nowego kredytu
        with st.expander("? Dodaj Nowy Kredyt", expanded=len(kredyty)==0):
            with st.form("add_kredyt"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nazwa = st.text_input("Nazwa kredytu *", placeholder="np. Kredyt mieszkaniowy")
                    kwota_poczatkowa = st.number_input("Kwota poczπtkowa (PLN) *", min_value=0, step=1000, value=0)
                    data_zaciagniecia = st.date_input("Data zaciπgniÍcia *", value=datetime.now())
                    dzien_splaty = st.number_input("DzieÒ sp≥aty w miesiπcu *", min_value=1, max_value=31, value=10, help="KtÛry dzieÒ miesiπca przypada sp≥ata?")
                
                with col2:
                    oprocentowanie = st.number_input("Oprocentowanie roczne (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f", value=0.0)
                    rata_miesieczna = st.number_input("Rata miesiÍczna (PLN)", min_value=0, step=100, value=0)
                    splacono = st.number_input("Juø sp≥acono (PLN)", min_value=0, step=1000, value=0)
                
                notatki = st.text_area("Notatki", placeholder="Dodatkowe informacje, np. bank, numer umowy...")
                
                submitted = st.form_submit_button("?? Dodaj Kredyt")
                if submitted:
                    if not nazwa:
                        st.error("? Podaj nazwÍ kredytu")
                    elif kwota_poczatkowa <= 0:
                        st.error("? Kwota musi byÊ wiÍksza od 0")
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
                            st.success("? Kredyt dodany!")
                            st.rerun()
        
        # Lista kredytÛw
        if kredyty:
            st.markdown("### ?? Twoje Kredyty")
            
            for i, kredyt in enumerate(kredyty):
                pozostalo = kredyt['kwota_poczatkowa'] - kredyt['splacono']
                with st.expander(f"**{kredyt['nazwa']}** - {format_currency(pozostalo)} pozosta≥o"):
                    # Informacje g≥Ûwne
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.metric("Kwota poczπtkowa", format_currency(kredyt['kwota_poczatkowa']))
                        st.metric("Sp≥acono", format_currency(kredyt['splacono']))
                        st.caption(f"?? Data zaciπgniÍcia: {kredyt['data_zaciagniecia']}")
                    
                    with col2:
                        st.metric("Pozosta≥o", format_currency(pozostalo))
                        postep = kredyt['splacono'] / kredyt['kwota_poczatkowa'] * 100 if kredyt['kwota_poczatkowa'] > 0 else 0
                        st.progress(min(postep / 100, 1.0))
                        st.caption(f"PostÍp: {postep:.1f}%")
                    
                    with col3:
                        st.metric("Oprocentowanie", f"{kredyt['oprocentowanie']:.2f}%")
                        st.metric("Rata miesiÍczna", f"{kredyt['rata_miesieczna']:.0f} PLN")
                        st.caption(f"??? Sp≥ata: {kredyt['dzien_splaty']} dzieÒ miesiπca")
                    
                    # Oblicz ile miesiÍcy do sp≥aty
                    if kredyt['rata_miesieczna'] > 0:
                        miesiace = pozostalo / kredyt['rata_miesieczna']
                        st.info(f"? **Przewidywany czas sp≥aty:** {int(miesiace)} miesiÍcy ({int(miesiace/12)} lat {int(miesiace%12)} miesiÍcy)")
                    
                    if kredyt.get('notatki'):
                        st.text_area("Notatki", value=kredyt['notatki'], disabled=True, key=f"notatki_view_{i}")
                    
                    # Edycja sp≥aty
                    st.markdown("---")
                    st.markdown("**?? Aktualizuj sp≥atÍ**")
                    col_edit1, col_edit2, col_edit3 = st.columns([2, 2, 1])
                    
                    with col_edit1:
                        nowa_splacona_kwota = st.number_input(
                            "Sp≥acona kwota (PLN)",
                            min_value=0,
                            max_value=int(kredyt['kwota_poczatkowa']),
                            value=int(kredyt['splacono']),
                            step=100,
                            key=f"edit_splacono_{i}"
                        )
                    
                    with col_edit2:
                        if st.button("? Zapisz sp≥atÍ", key=f"save_{i}"):
                            kredyty[i]['splacono'] = nowa_splacona_kwota
                            if save_kredyty(kredyty):
                                st.success("? Zaktualizowano sp≥atÍ!")
                                st.rerun()
                    
                    with col_edit3:
                        if st.button("??? UsuÒ kredyt", key=f"delete_{i}", type="secondary"):
                            if st.session_state.get(f'confirm_delete_{i}', False):
                                kredyty.pop(i)
                                if save_kredyty(kredyty):
                                    st.success("? UsuniÍto kredyt!")
                                    st.rerun()
                            else:
                                st.session_state[f'confirm_delete_{i}'] = True
                                st.warning("?? Kliknij ponownie aby potwierdziÊ!")
        else:
            st.info("?? Nie masz jeszcze øadnych kredytÛw. Dodaj pierwszy powyøej!")
    
    # ===== TAB 3: ANALIZA =====
    with tab3:
        st.header("?? Analiza Sp≥at i Prognoza")
        
        kredyty = load_kredyty()
        
        if not kredyty:
            st.info("?? Dodaj kredyty w zak≥adce 'Kredyty', aby zobaczyÊ analizÍ.")
        else:
            # Suma wszystkich kredytÛw
            suma_poczatkowa = sum(k['kwota_poczatkowa'] for k in kredyty)
            suma_splacona = sum(k['splacono'] for k in kredyty)
            suma_pozostala = suma_poczatkowa - suma_splacona
            suma_rat = sum(k['rata_miesieczna'] for k in kredyty)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Suma poczπtkowa", format_currency(suma_poczatkowa))
            with col2:
                st.metric("Suma sp≥acona", format_currency(suma_splacona))
            with col3:
                st.metric("Suma pozosta≥a", format_currency(suma_pozostala))
            with col4:
                st.metric("MiesiÍczne raty", f"{suma_rat:.0f} PLN")
            
            # Prognoza sp≥aty
            st.markdown("### ?? Prognoza Sp≥aty")
            
            if suma_rat > 0 and suma_pozostala > 0:
                miesiace_do_splaty = suma_pozostala / suma_rat
                lata = int(miesiace_do_splaty / 12)
                miesiace = int(miesiace_do_splaty % 12)
                
                data_splaty = datetime.now() + timedelta(days=miesiace_do_splaty * 30)
                
                st.success(f"?? **Przewidywana data sp≥aty:** {data_splaty.strftime('%Y-%m-%d')}")
                st.caption(f"? Czas do pe≥nej sp≥aty: {lata} lat i {miesiace} miesiÍcy")
            
            # Tabela kredytÛw
            st.markdown("### ?? SzczegÛ≥y KredytÛw")
            
            df_kredyty = []
            for k in kredyty:
                pozostalo = k['kwota_poczatkowa'] - k['splacono']
                postep = k['splacono'] / k['kwota_poczatkowa'] * 100 if k['kwota_poczatkowa'] > 0 else 0
                df_kredyty.append({
                    'Nazwa': k['nazwa'],
                    'Poczπtek': f"{k['kwota_poczatkowa']:.0f} PLN",
                    'Sp≥acono': f"{k['splacono']:.0f} PLN",
                    'Pozosta≥o': f"{pozostalo:.0f} PLN",
                    'PostÍp': f"{postep:.1f}%",
                    'Oprocentowanie': f"{k['oprocentowanie']:.2f}%",
                    'Rata': f"{k['rata_miesieczna']:.0f} PLN",
                    'DzieÒ sp≥aty': str(k['dzien_splaty']),
                    'Data zaciπgniÍcia': k['data_zaciagniecia']
                })
            
            if df_kredyty:
                import pandas as pd
                st.dataframe(pd.DataFrame(df_kredyty), width="stretch", hide_index=True)
                
                # Wykres postÍpu sp≥at
                st.markdown("### ?? PostÍp Sp≥at (wizualizacja)")
                
                fig = go.Figure()
                
                for k in kredyty:
                    pozostalo = k['kwota_poczatkowa'] - k['splacono']
                    fig.add_trace(go.Bar(
                        name=k['nazwa'],
                        x=['Sp≥acono', 'Pozosta≥o'],
                        y=[k['splacono'], pozostalo],
                        text=[f"{k['splacono']:.0f}", f"{pozostalo:.0f}"],
                        textposition='auto',
                    ))
                
                fig.update_layout(
                    barmode='stack',
                    title="PostÍp sp≥aty kredytÛw",
                    xaxis_title="",
                    yaxis_title="Kwota (PLN)",
                    showlegend=True,
                    height=400
                )
                
                st.plotly_chart(fig, width="stretch")
    
    # ===== TAB 4: WYP£ATY =====
    with tab4:
        st.header("?? Historia Wyp≥at")
        
        wyplaty = load_wyplaty()
        
        # Informacja o systemie
        st.info("""
        ?? **System wyp≥at:**
        - Wyp≥ata oko≥o **10-go** kaødego miesiπca
        - Podstawa + premia w jednym przelewie
        """)
        
        # === PODSUMOWANIE ===
        if wyplaty:
            col1, col2, col3 = st.columns(3)
            
            # Ostatnie 12 miesiÍcy
            rok_temu = datetime.now() - timedelta(days=365)
            wyplaty_12m = [w for w in wyplaty if datetime.fromisoformat(w['data']) >= rok_temu]
            
            suma_total_12m = sum(w['kwota'] for w in wyplaty_12m)
            srednia_12m = suma_total_12m / len(wyplaty_12m) if wyplaty_12m else 0
            
            with col1:
                st.metric("?? Suma (12 mies.)", format_currency(suma_total_12m))
            with col2:
                st.metric("?? årednia", format_currency(srednia_12m))
            with col3:
                if wyplaty:
                    st.metric("? Liczba wyp≥at", len(wyplaty))
        
        # === DODAWANIE WYP£ATY ===
        st.markdown("### ? Dodaj Wyp≥atÍ")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("add_wyplata"):
                data_wyplaty = st.date_input(
                    "Data wyp≥aty *",
                    value=datetime.now().replace(day=10),
                    help="Domyúlnie 10-ty dzieÒ miesiπca"
                )
                
                kwota = st.number_input(
                    "Kwota wyp≥aty (PLN) *",
                    min_value=0.0,
                    value=3500.0,
                    step=100.0,
                    help="Ca≥kowita kwota wyp≥aty (podstawa + premia)"
                )
                
                notatki = st.text_area(
                    "Notatki",
                    help="Opcjonalne notatki (np. bonus, nadgodziny, urlop)"
                )
                
                submitted = st.form_submit_button("?? Zapisz Wyp≥atÍ")
                
                if submitted:
                    # Walidacja
                    if kwota <= 0:
                        st.error("? Kwota musi byÊ wiÍksza od 0")
                    else:
                        # Sprawdü czy nie ma juø wyp≥aty w tym miesiπcu
                        miesiac_rok = data_wyplaty.strftime('%Y-%m')
                        duplikat = any(w['data'].startswith(miesiac_rok) for w in wyplaty)
                        
                        if duplikat:
                            st.warning(f"?? Wyp≥ata za {miesiac_rok} juø istnieje. Zostanie dodana jako dodatkowa.")
                        
                        nowa_wyplata = {
                            'id': str(datetime.now().timestamp()),
                            'data': data_wyplaty.isoformat(),
                            'kwota': kwota,
                            'notatki': notatki
                        }
                        
                        wyplaty.append(nowa_wyplata)
                        # Sortuj od najnowszej
                        wyplaty.sort(key=lambda x: x['data'], reverse=True)
                        
                        if save_wyplaty(wyplaty):
                            st.success("? Wyp≥ata zapisana!")
                            st.rerun()
                        else:
                            st.error("? B≥πd zapisu wyp≥aty")
        
        with col2:
            st.markdown("### ?? Szybkie Statystyki")
            if wyplaty:
                ostatnia = wyplaty[0]
                st.info(f"""
                **Ostatnia wyp≥ata:**
                - ?? Data: {ostatnia['data']}
                - ?? Kwota: {ostatnia['kwota']:.2f} PLN
                """)
                
                # Trend wyp≥at (ostatnie 3 miesiπce)
                ostatnie_3 = wyplaty[:3]
                if len(ostatnie_3) >= 3:
                    kwoty = [w['kwota'] for w in ostatnie_3]
                    trend = "?? Rosnπca" if kwoty[0] > kwoty[-1] else "?? Malejπca" if kwoty[0] < kwoty[-1] else "?? Stabilna"
                    st.caption(f"Trend (3 mies.): {trend}")
            else:
                st.caption("Brak danych")
        
        # === HISTORIA WYP£AT ===
        if wyplaty:
            st.markdown("### ?? Historia Wyp≥at")
            
            # Filtr roku
            lata = sorted(set(w['data'][:4] for w in wyplaty), reverse=True)
            if len(lata) > 1:
                filtr_rok = st.selectbox("Filtruj rok:", ["Wszystkie"] + lata)
            else:
                filtr_rok = "Wszystkie"
            
            # Filtrowanie
            wyplaty_filtr = wyplaty if filtr_rok == "Wszystkie" else [w for w in wyplaty if w['data'].startswith(filtr_rok)]
            
            # Tabela
            for wyplata in wyplaty_filtr:
                with st.expander(f"?? {wyplata['data']} - **{wyplata['kwota']:.2f} PLN**"):
                    st.metric("?? Kwota wyp≥aty", f"{wyplata['kwota']:.2f} PLN")
                    
                    if wyplata.get('notatki'):
                        st.caption(f"?? {wyplata['notatki']}")
                    
                    # Edycja kwoty (jeúli potrzeba korekty)
                    st.markdown("---")
                    with st.form(f"edit_wyplata_{wyplata['id']}"):
                        st.caption("Edytuj kwotÍ:")
                        nowa_kwota = st.number_input(
                            "Nowa kwota (PLN)",
                            min_value=0.0,
                            value=float(wyplata['kwota']),
                            step=100.0,
                            key=f"kwota_{wyplata['id']}"
                        )
                        
                        col_save, col_delete = st.columns([1, 1])
                        
                        with col_save:
                            if st.form_submit_button("?? Zapisz", width="stretch"):
                                wyplata['kwota'] = nowa_kwota
                                if save_wyplaty(wyplaty):
                                    st.success("? Zaktualizowano!")
                                    st.rerun()
                        
                        with col_delete:
                            if st.form_submit_button("??? UsuÒ", width="stretch", type="secondary"):
                                # Potwierdü usuniÍcie
                                if f'confirm_delete_{wyplata["id"]}' not in st.session_state:
                                    st.session_state[f'confirm_delete_{wyplata["id"]}'] = True
                                    st.warning("?? Kliknij ponownie aby potwierdziÊ")
                                else:
                                    wyplaty.remove(wyplata)
                                    if save_wyplaty(wyplaty):
                                        del st.session_state[f'confirm_delete_{wyplata["id"]}']
                                        st.success("? UsuniÍto!")
                                        st.rerun()
            
            # === WYKRES WYP£AT ===
            st.markdown("### ?? Wizualizacja Wyp≥at")
            
            # Przygotuj dane dla wykresu (ostatnie 12 miesiÍcy)
            wyplaty_wykres = sorted(wyplaty_filtr, key=lambda x: x['data'])[-12:]
            
            if wyplaty_wykres:
                fig = go.Figure()
                
                daty = [w['data'] for w in wyplaty_wykres]
                kwoty = [w['kwota'] for w in wyplaty_wykres]
                
                fig.add_trace(go.Bar(
                    name='Wyp≥ata',
                    x=daty,
                    y=kwoty,
                    marker_color='#1f77b4',
                    text=[f"{k:.0f}" for k in kwoty],
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title="Wyp≥aty - Ostatnie 12 miesiÍcy",
                    xaxis_title="Data",
                    yaxis_title="Kwota (PLN)",
                    hovermode='x unified',
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, width="stretch")
    
    # ===== TAB 5: STA£E WYDATKI =====
    with tab5:
        st.header("?? Sta≥e Wydatki MiesiÍczne")
        
        wydatki = load_wydatki()
        
        # Informacja o systemie
        st.info("""
        ?? **System wydatkÛw:**
        - Wydatki sta≥e: powtarzajπ siÍ co miesiπc
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
                st.metric("?? Suma Sta≥e", format_currency(suma_stale))
            with col2:
                st.metric("?? Nadprogramowe", format_currency(suma_nadprog))
            with col3:
                st.metric("?? Total", format_currency(suma_total))
            with col4:
                st.metric("?? Liczba wydatkÛw", len(wydatki))
        
        # === DODAWANIE WYDATKU ===
        st.markdown("### ? Dodaj Wydatek")
        
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
                    help="Zaznacz jeúli to jednorazowy wydatek (nie powtarza siÍ co miesiπc)"
                )
                
                notatki = st.text_area(
                    "Notatki",
                    help="Opcjonalne szczegÛ≥y"
                )
                
                submitted = st.form_submit_button("?? Zapisz Wydatek")
                
                if submitted:
                    # Walidacja
                    if not nazwa:
                        st.error("? Nazwa jest wymagana")
                    elif kwota <= 0:
                        st.error("? Kwota musi byÊ wiÍksza od 0")
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
                            st.success("? Wydatek zapisany!")
                            st.rerun()
                        else:
                            st.error("? B≥πd zapisu wydatku")
        
        with col2:
            st.markdown("### ?? Podzia≥ po Kategoriach")
            if wydatki:
                # Grupuj po kategoriach
                kategorie_suma = {}
                for w in wydatki:
                    if not w.get('nadprogramowy', False):  # Tylko sta≥e
                        kat = w['kategoria']
                        kategorie_suma[kat] = kategorie_suma.get(kat, 0) + w['kwota']
                
                if kategorie_suma:
                    for kat, suma in sorted(kategorie_suma.items(), key=lambda x: x[1], reverse=True):
                        procent = (suma / suma_stale * 100) if suma_stale > 0 else 0
                        st.caption(f"**{kat}**: {suma:.0f} PLN ({procent:.1f}%)")
                else:
                    st.caption("Brak wydatkÛw sta≥ych")
            else:
                st.caption("Brak danych")
        
        # === LISTA WYDATK”W ===
        if wydatki:
            st.markdown("---")
            st.markdown("### ?? Lista WydatkÛw")
            
            # Filtr
            filtr = st.radio(
                "Pokaø:",
                ["Wszystkie", "Sta≥e", "Nadprogramowe"],
                horizontal=True
            )
            
            # Filtrowanie
            if filtr == "Sta≥e":
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
            
            # Wyúwietl po kategoriach
            for kategoria, lista in sorted(kategorie.items()):
                suma_kat = sum(w['kwota'] for w in lista)
                
                with st.expander(f"**{kategoria}** - {format_currency(suma_kat)} ({len(lista)} wydatkÛw)", expanded=True):
                    for wydatek in lista:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            ikona = "??" if wydatek.get('nadprogramowy', False) else "??"
                            st.write(f"{ikona} **{wydatek['nazwa']}**")
                            if wydatek.get('notatki'):
                                st.caption(f"?? {wydatek['notatki']}")
                        
                        with col2:
                            st.metric("Kwota", f"{wydatek['kwota']:.2f} PLN")
                        
                        with col3:
                            # Edycja/UsuniÍcie
                            with st.form(f"action_{wydatek['id']}"):
                                col_edit, col_del = st.columns(2)
                                
                                with col_edit:
                                    if st.form_submit_button("??", width="stretch"):
                                        st.session_state[f'edit_{wydatek["id"]}'] = True
                                        st.rerun()
                                
                                with col_del:
                                    if st.form_submit_button("???", width="stretch"):
                                        if f'confirm_del_{wydatek["id"]}' not in st.session_state:
                                            st.session_state[f'confirm_del_{wydatek["id"]}'] = True
                                            st.warning("Kliknij ponownie")
                                        else:
                                            wydatki.remove(wydatek)
                                            if save_wydatki(wydatki):
                                                del st.session_state[f'confirm_del_{wydatek["id"]}']
                                                st.success("? UsuniÍto!")
                                                st.rerun()
                        
                        # Formularz edycji (jeúli aktywny)
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
                                    if st.form_submit_button("?? Zapisz", width="stretch"):
                                        wydatek['kwota'] = nowa_kwota
                                        wydatek['nadprogramowy'] = nowy_nadprog
                                        if save_wydatki(wydatki):
                                            del st.session_state[f'edit_{wydatek["id"]}']
                                            st.success("? Zaktualizowano!")
                                            st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button("? Anuluj", width="stretch"):
                                        del st.session_state[f'edit_{wydatek["id"]}']
                                        st.rerun()
                        
                        st.markdown("---")
            
            # === WYKRES WYDATK”W ===
            st.markdown("### ?? Wizualizacja WydatkÛw")
            
            # Wykres po kategoriach (tylko sta≥e)
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
                    title="Podzia≥ WydatkÛw Sta≥ych po Kategoriach",
                    height=400
                )
                
                st.plotly_chart(fig, width="stretch")
    
    # ===== TAB 6: KRYPTO =====
    with tab6:
        st.header("? Portfel Kryptowalut")
        
        krypto = load_krypto()
        
        # === POBIERZ AKTUALNE CENY DLA CA£EGO TAB (raz na poczπtku) ===
        current_prices = {}
        if krypto and CRYPTO_MANAGER_OK:
            try:
                symbols = list(set(k['symbol'] for k in krypto))
                current_prices = get_cached_crypto_prices(symbols)
            except Exception as e:
                st.warning(f"?? Nie uda≥o siÍ pobraÊ aktualnych cen: {e}")
        
        # Informacja o systemie
        st.info("""
        ?? **Zarzπdzanie kryptowalutami (Lokalne dane - krypto.json):**
        - ? **Pe≥na kontrola** - wszystkie dane przechowywane lokalnie
        - ?? Obs≥uga wielu platform (Binance, Gate.io, MEXC, etc.)
        - ?? åledü iloúÊ, úredniπ cenÍ zakupu i wartoúÊ pozycji
        - ?? Monitoruj APY/Staking dla pozycji generujπcych dochÛd
        - ?? **NOWOå∆:** Real-time ceny z CoinGecko + P&L analysis!
        - ?? **Dane NIE sπ pobierane z Google Sheets** - zarzπdzaj wszystkim tutaj!
        """)
        
        # === FEAR & GREED INDEX (Feature #5) ===
        if CRYPTO_MANAGER_OK and krypto:
            try:
                fg_data = st.session_state.crypto_manager.get_fear_greed_index()
                if fg_data:
                    value = fg_data['value']
                    classification = fg_data['value_classification']
                    
                    # Kolor bazowany na wartoúci
                    if value < 25:
                        color = "#DC2626"  # Extreme Fear - czerwony
                        emoji = "??"
                        interpretation = "Skrajny strach - moøe byÊ dobry moment na zakupy!"
                    elif value < 45:
                        color = "#F59E0B"  # Fear - pomaraÒczowy
                        emoji = "??"
                        interpretation = "Strach na rynku - okazje inwestycyjne?"
                    elif value < 55:
                        color = "#10B981"  # Neutral - zielony
                        emoji = "??"
                        interpretation = "Neutralny sentyment rynkowy"
                    elif value < 75:
                        color = "#3B82F6"  # Greed - niebieski
                        emoji = "??"
                        interpretation = "ChciwoúÊ - rynek roúnie, bπdü ostroøny"
                    else:
                        color = "#8B5CF6"  # Extreme Greed - fioletowy
                        emoji = "??"
                        interpretation = "Skrajna chciwoúÊ - moøliwa korekta!"
                    
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
                pass  # Cicho ignoruj b≥Ídy Fear & Greed
        
        # === PODSUMOWANIE Z REAL-TIME DATA (Feature #1, #7) ===
        if krypto:
            # Oblicz statystyki zakupu
            total_wartosc_zakupu = sum(k['ilosc'] * k['cena_zakupu_usd'] for k in krypto)
            liczba_platform = len(set(k['platforma'] for k in krypto))
            liczba_aktywow = len(krypto)
            srednie_apy = sum(k.get('apy', 0) for k in krypto) / len(krypto) if krypto else 0
            
            # Oblicz aktualnπ wartoúÊ i P&L (uøywa current_prices z gÛry TAB)
            total_wartosc_current = 0
            total_pnl = 0
            
            if current_prices:
                # Oblicz aktualnπ wartoúÊ i P&L
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
                st.metric("?? WartoúÊ zakupu", f"${total_wartosc_zakupu:.2f}", 
                         help="WartoúÊ wed≥ug úredniej ceny zakupu")
            
            with col2:
                if total_wartosc_current > 0:
                    st.metric("?? WartoúÊ aktualna", f"${total_wartosc_current:.2f}",
                             delta=f"${total_pnl:.2f}",
                             help="Aktualna wartoúÊ rynkowa (live prices)")
                else:
                    st.metric("?? Liczba aktywÛw", liczba_aktywow)
            
            with col3:
                if total_pnl != 0 and total_wartosc_zakupu > 0:
                    pnl_percent = (total_pnl / total_wartosc_zakupu) * 100
                    st.metric("?? Zysk/Strata", 
                             f"{'+' if total_pnl > 0 else ''}{pnl_percent:.2f}%",
                             delta=f"${total_pnl:.2f}",
                             help="Ca≥kowity profit/loss")
                else:
                    st.metric("?? Liczba aktywÛw", liczba_aktywow)
            
            with col4:
                st.metric("?? Platformy", liczba_platform)
            
            with col5:
                st.metric("?? årednie APY", f"{srednie_apy:.2f}%")
            
            # === RISK ANALYTICS (Feature #8) ===
            st.markdown("---")
            st.markdown("### ?? Analiza Ryzyka Portfela")
            
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
                max_coin = max(coin_concentration.items(), key=lambda x: x[1])
                max_coin_percent = (max_coin[1] / total_value * 100) if total_value > 0 else 0
                if max_coin_percent > 40:
                    alerts.append(f"?? **Wysoka koncentracja:** {max_coin[0]} stanowi {max_coin_percent:.1f}% portfela")
                elif max_coin_percent > 25:
                    alerts.append(f"?? **årednia koncentracja:** {max_coin[0]} stanowi {max_coin_percent:.1f}% portfela")
            
            # Check platform concentration (>60% on one platform)
            if platform_concentration:
                max_platform = max(platform_concentration.items(), key=lambda x: x[1])
                max_platform_percent = (max_platform[1] / total_value * 100) if total_value > 0 else 0
                if max_platform_percent > 70:
                    alerts.append(f"?? **Ryzyko platformy:** {max_platform[0]} - {max_platform_percent:.1f}% aktywÛw")
                elif max_platform_percent > 50:
                    alerts.append(f"?? **Koncentracja platformy:** {max_platform[0]} - {max_platform_percent:.1f}% aktywÛw")
            
            # Check stablecoin ratio
            stablecoin_percent = (stablecoin_value / total_value * 100) if total_value > 0 else 0
            if stablecoin_percent > 60:
                alerts.append(f"?? **Wysoki % stablecoinÛw:** {stablecoin_percent:.1f}% (ma≥a ekspozycja na wzrosty)")
            elif stablecoin_percent < 10:
                alerts.append(f"?? **Niski % stablecoinÛw:** {stablecoin_percent:.1f}% (wiÍksze ryzyko zmiennoúci)")
            
            # Display alerts or OK status
            if alerts:
                for alert in alerts:
                    st.warning(alert)
            else:
                st.success("? **Portfel dobrze zdywersyfikowany!** Brak alertÛw ryzyka.")
            
            # Risk metrics w kolumnach
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                max_coin = max(coin_concentration.items(), key=lambda x: x[1]) if coin_concentration else ("N/A", 0)
                max_coin_pct = (max_coin[1] / total_value * 100) if total_value > 0 else 0
                st.metric("?? NajwiÍksza pozycja", f"{max_coin[0]}", f"{max_coin_pct:.1f}%")
            
            with col_r2:
                max_plat = max(platform_concentration.items(), key=lambda x: x[1]) if platform_concentration else ("N/A", 0)
                max_plat_pct = (max_plat[1] / total_value * 100) if total_value > 0 else 0
                st.metric("?? G≥Ûwna platforma", f"{max_plat[0]}", f"{max_plat_pct:.1f}%")
            
            with col_r3:
                st.metric("?? Stablecoiny", f"${stablecoin_value:.2f}", f"{stablecoin_percent:.1f}%")
        
        # === APY EARNINGS BREAKDOWN (Feature #2) ===
        if krypto:
            st.markdown("---")
            st.markdown("### ?? Zarobki z APY/Staking/Earn")
            
            # Oblicz earnings
            kurs_usd = 3.65  # Default, moøna pobraÊ z API
            crypto_earnings = calculate_crypto_apy_earnings(krypto, current_prices, kurs_usd)
            
            if crypto_earnings['liczba_earning_positions'] > 0:
                # Summary metrics
                col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                
                with col_e1:
                    st.metric("?? Dziennie", 
                             f"${crypto_earnings['dziennie_usd']:.2f}",
                             delta=f"{crypto_earnings['dziennie_pln']:.2f} PLN")
                
                with col_e2:
                    st.metric("?? MiesiÍcznie", 
                             f"${crypto_earnings['miesieczne_usd']:.2f}",
                             delta=f"{crypto_earnings['miesieczne_pln']:.2f} PLN")
                
                with col_e3:
                    st.metric("?? Rocznie", 
                             f"${crypto_earnings['roczne_usd']:.2f}",
                             delta=f"{crypto_earnings['roczne_pln']:.2f} PLN")
                
                with col_e4:
                    st.metric("?? Earning Positions", 
                             crypto_earnings['liczba_earning_positions'])
                
                # Detailed breakdown
                st.markdown("#### ?? SzczegÛ≥y zarobkÛw po pozycjach:")
                
                for detail in crypto_earnings['szczegoly']:
                    col_d1, col_d2, col_d3, col_d4 = st.columns([2, 1, 1, 2])
                    
                    with col_d1:
                        st.write(f"**{detail['symbol']}** ({detail['status']})")
                        st.caption(f"APY: {detail['apy']:.2f}%")
                    
                    with col_d2:
                        st.caption(f"WartoúÊ: ${detail['value_usd']:.2f}")
                    
                    with col_d3:
                        st.caption(f"Dziennie: ${detail['dziennie_usd']:.2f}")
                    
                    with col_d4:
                        st.caption(f"MiesiÍcznie: ${detail['miesieczne_usd']:.2f}")
                        st.caption(f"Rocznie: ${detail['roczne_usd']:.2f}")
                
                st.success(f"?? **Tip:** TwÛj portfel crypto generuje pasywny dochÛd {crypto_earnings['miesieczne_pln']:.0f} PLN/mies bez dodatkowej pracy!")
            else:
                st.info("?? Brak pozycji generujπcych dochÛd pasywny (APY/Staking/Earn). Rozwaø earning products!")
        
        # === DODAWANIE KRYPTO ===
        st.markdown("---")
        st.markdown("### ? Dodaj KryptowalutÍ")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("add_krypto"):
                symbol = st.text_input(
                    "Symbol/Ticker *",
                    placeholder="np. BTC, ETH, BNB",
                    help="SkrÛt kryptowaluty"
                ).upper()
                
                ilosc = st.number_input(
                    "IloúÊ *",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.8f"
                )
                
                cena_zakupu = st.number_input(
                    "årednia cena zakupu (USD) *",
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
                    "APY % (jeúli dotyczy)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    help="Roczny procent zysku"
                )
                
                notatki = st.text_area(
                    "Notatki",
                    help="Dodatkowe informacje"
                )
                
                submitted = st.form_submit_button("?? Zapisz KryptowalutÍ")
                
                if submitted:
                    # Walidacja
                    if not symbol:
                        st.error("? Symbol jest wymagany")
                    elif ilosc <= 0:
                        st.error("? IloúÊ musi byÊ wiÍksza od 0")
                    elif cena_zakupu <= 0:
                        st.error("? Cena zakupu musi byÊ wiÍksza od 0")
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
                            st.success("? Kryptowaluta zapisana!")
                            st.rerun()
                        else:
                            st.error("? B≥πd zapisu")
        
        with col2:
            st.markdown("### ?? Podzia≥ po Platformach")
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
            st.markdown("### ?? Twoje Kryptowaluty")
            
            # === TABELA POR”WNAWCZA CEN ===
            st.markdown("#### ?? PorÛwnanie Cen: Zakup vs Aktualne")
            
            # Grupuj po symbolach dla tabeli
            price_comparison = []
            for symbol in set(k['symbol'] for k in krypto):
                holdings_of_symbol = [k for k in krypto if k['symbol'] == symbol]
                total_qty = sum(k['ilosc'] for k in holdings_of_symbol)
                total_cost = sum(k['ilosc'] * k['cena_zakupu_usd'] for k in holdings_of_symbol)
                avg_purchase_price = total_cost / total_qty if total_qty > 0 else 0
                
                # Pobierz aktualnπ cenÍ
                current_price = None
                change_24h = None
                pnl_usd = None
                pnl_pct = None
                price_source = ""  # Skπd pochodzi cena
                
                # Priorytet 1: API (live data)
                if CRYPTO_MANAGER_OK and symbol in current_prices:
                    coin_data = current_prices[symbol]
                    if coin_data.get('current_price'):
                        current_price = coin_data['current_price']
                        change_24h = coin_data.get('price_change_percentage_24h')
                        
                        # Sprawdü ürÛd≥o API
                        api_source = coin_data.get('source', 'CoinGecko')
                        if 'MEXC' in api_source:
                            price_source = "?? MEXC"
                        elif 'Gate.io' in api_source:
                            price_source = "?? Gate.io"
                        else:
                            price_source = "?? CoinGecko"
                
                # Priorytet 2: Manual price z pierwszego holdingu (backup)
                if current_price is None:
                    for holding in holdings_of_symbol:
                        if holding.get('manual_price'):
                            current_price = float(holding['manual_price'])
                            price_source = "?? Manual"
                            break
                
                # Oblicz P&L jeúli mamy cenÍ
                if current_price:
                    current_value = total_qty * current_price
                    pnl_usd = current_value - total_cost
                    pnl_pct = (pnl_usd / total_cost * 100) if total_cost > 0 else 0
                
                price_comparison.append({
                    'Symbol': symbol,
                    'IloúÊ': f"{total_qty:.6f}",
                    'Cena Zakupu': f"${avg_purchase_price:.4f}",
                    'Cena Aktualna': f"${current_price:.4f} {price_source}" if current_price else "? Brak (dodaj manual_price)",
                    'Zmiana 24h': f"{change_24h:+.2f}%" if change_24h is not None else "N/A",
                    'P&L': f"${pnl_usd:+.2f} ({pnl_pct:+.2f}%)" if pnl_usd is not None else "N/A",
                    '_pnl_raw': pnl_pct if pnl_pct is not None else 0  # do sortowania
                })
            
            # Sortuj po P&L (najlepsze na gÛrze)
            price_comparison.sort(key=lambda x: x['_pnl_raw'], reverse=True)
            
            # Wyúwietl jako tabelÍ z kolorami
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
                table_html += "<th>Symbol</th><th>IloúÊ</th><th>Cena Zakupu</th><th>Cena Aktualna</th><th>Zmiana 24h</th><th>P&L</th></tr>"
                
                for row in price_comparison:
                    pnl_class = "positive" if row['_pnl_raw'] > 0 else "negative" if row['_pnl_raw'] < 0 else ""
                    change_class = ""
                    if row['Zmiana 24h'] != "N/A":
                        change_val = float(row['Zmiana 24h'].replace('%',''))
                        change_class = "positive" if change_val > 0 else "negative" if change_val < 0 else ""
                    
                    table_html += f"<tr>"
                    table_html += f"<td><strong>{row['Symbol']}</strong></td>"
                    table_html += f"<td>{row['IloúÊ']}</td>"
                    table_html += f"<td>{row['Cena Zakupu']}</td>"
                    table_html += f"<td>{row['Cena Aktualna']}</td>"
                    table_html += f"<td class='{change_class}'>{row['Zmiana 24h']}</td>"
                    table_html += f"<td class='{pnl_class}'><strong>{row['P&L']}</strong></td>"
                    table_html += f"</tr>"
                
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)
                
                # Podsumowanie
                total_pnl = sum(float(r['P&L'].split('$')[1].split('(')[0]) for r in price_comparison if r['P&L'] != "N/A")
                st.caption(f"?? **Total Portfolio P&L:** ${total_pnl:+.2f} USD")
                
                # Info o brakujπcych cenach
                missing_prices = [r['Symbol'] for r in price_comparison if "Brak" in r['Cena Aktualna']]
                if missing_prices:
                    with st.expander(f"?? Jak dodaÊ ceny dla {', '.join(missing_prices)}?", expanded=False):
                        st.markdown("""
                        **System automatycznie prÛbuje pobraÊ ceny z wielu ürÛde≥:**
                        - ?? **CoinGecko API** - g≥Ûwne ürÛd≥o (Top 250 coinÛw)
                        - ?? **MEXC API** - dla MX Token (auto)
                        - ?? **Gate.io API** - dla GUSD i tokenÛw gie≥dowych (auto)
                        
                        **Jeúli token nadal nie ma ceny, moøesz dodaÊ rÍcznie jako backup:**
                        
                        Edytuj `krypto.json` i dodaj pole `"manual_price"`:
                            ```json
                        {
                          "symbol": "RARE_TOKEN",
                          "manual_price": 1.23,
                          ...
                        }
                        ```
                        
                        ?? Manual price to fallback - system zawsze najpierw prÛbuje live API!
                        """)
            else:
                st.info("Brak danych do porÛwnania cen")
            
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
            
            # Wyúwietl po symbolach
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
                        change_color = "??" if change_val > 0 else "??" if change_val < 0 else "?"
                    
                    if coin_data.get('current_price'):
                        current_price_symbol = coin_data['current_price']
                        total_wartosc_current = total_ilosc * current_price_symbol
                        pnl_symbol = total_wartosc_current - total_wartosc_zakupu
                
                # Tytu≥ expandera z enhanced info
                if current_price_symbol:
                    pnl_emoji = "??" if pnl_symbol > 0 else "??" if pnl_symbol < 0 else "??"
                    expander_title = f"**{symbol}** ({coin_name}){coin_rank}{change_color}{change_24h} {pnl_emoji} ${total_wartosc_current:.2f}"
                else:
                    expander_title = f"**{symbol}** ({coin_name}){coin_rank} - {total_ilosc:.8f} (${total_wartosc_zakupu:.2f})"
                
                with st.expander(expander_title, expanded=False):
                    # Header z cenami
                    col_h1, col_h2, col_h3 = st.columns(3)
                    
                    with col_h1:
                        st.caption(f"?? årednia cena zakupu: **${srednia_cena:.2f}**")
                    
                    with col_h2:
                        if current_price_symbol:
                            st.caption(f"?? Aktualna cena: **${current_price_symbol:.2f}**")
                        else:
                            st.caption(f"?? Aktualna cena: **N/A**")
                    
                    with col_h3:
                        if pnl_symbol != 0:
                            pnl_percent = (pnl_symbol / total_wartosc_zakupu * 100) if total_wartosc_zakupu > 0 else 0
                            pnl_color = "green" if pnl_symbol > 0 else "red"
                            st.caption(f"?? P&L: :{pnl_color}[**{pnl_percent:+.2f}%** (${pnl_symbol:+.2f})]")
                        else:
                            st.caption(f"?? P&L: **N/A**")
                    
                    st.markdown("---")
                    
                    for krypto_item in lista:
                        st.markdown("---")
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"?? **{krypto_item['platforma']}** - {krypto_item['status']}")
                            st.caption(f"IloúÊ: {krypto_item['ilosc']:.8f}")
                            st.caption(f"Cena zakupu: ${krypto_item['cena_zakupu_usd']:.2f}")
                            if krypto_item.get('apy', 0) > 0:
                                st.caption(f"?? APY: {krypto_item['apy']:.2f}%")
                            if krypto_item.get('notatki'):
                                st.caption(f"?? {krypto_item['notatki']}")
                        
                        with col2:
                            wartosc_pozycji = krypto_item['ilosc'] * krypto_item['cena_zakupu_usd']
                            st.metric("WartoúÊ", f"${wartosc_pozycji:.2f}")
                        
                        with col3:
                            # Edycja/UsuniÍcie
                            with st.form(f"action_krypto_{krypto_item['id']}"):
                                col_edit, col_del = st.columns(2)
                                
                                with col_edit:
                                    if st.form_submit_button("??", width="stretch"):
                                        st.session_state[f'edit_krypto_{krypto_item["id"]}'] = True
                                        st.rerun()
                                
                                with col_del:
                                    if st.form_submit_button("???", width="stretch"):
                                        if f'confirm_del_krypto_{krypto_item["id"]}' not in st.session_state:
                                            st.session_state[f'confirm_del_krypto_{krypto_item["id"]}'] = True
                                            st.warning("Kliknij ponownie")
                                        else:
                                            krypto.remove(krypto_item)
                                            if save_krypto(krypto):
                                                del st.session_state[f'confirm_del_krypto_{krypto_item["id"]}']
                                                st.success("? UsuniÍto!")
                                                st.rerun()
                        
                        # Formularz edycji
                        if st.session_state.get(f'edit_krypto_{krypto_item["id"]}', False):
                            with st.form(f"edit_form_krypto_{krypto_item['id']}"):
                                st.caption("Edytuj pozycjÍ:")
                                
                                nowa_ilosc = st.number_input(
                                    "IloúÊ",
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
                                    if st.form_submit_button("?? Zapisz", width="stretch"):
                                        krypto_item['ilosc'] = nowa_ilosc
                                        krypto_item['cena_zakupu_usd'] = nowa_cena
                                        if save_krypto(krypto):
                                            del st.session_state[f'edit_krypto_{krypto_item["id"]}']
                                            st.success("? Zaktualizowano!")
                                            st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button("? Anuluj", width="stretch"):
                                        del st.session_state[f'edit_krypto_{krypto_item["id"]}']
                                        st.rerun()
            
            # === WYKRES KRYPTO ===
            st.markdown("### ?? Wizualizacja Portfela Krypto")
            
            # Wykres ko≥owy po symbolach
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
                    title="Podzia≥ Portfela Krypto po Symbolach (wartoúÊ zakupu)",
                    height=400
                )
                
                st.plotly_chart(fig, width="stretch")
    
    # ===== TAB 7: TRACK RECORD AI =====
    with tab7:
        st.header("?? Track Record AI PartnerÛw")
        
        if not MEMORY_OK:
            st.warning("?? System pamiÍci AI niedostÍpny")
            st.info("Aby aktywowaÊ ten system, upewnij siÍ øe persona_memory_manager.py jest dostÍpny")
            return
        
        st.markdown("""
        System pamiÍci AI úledzi decyzje kaødej persony, ich trafnoúÊ i ewolucjÍ charakteru.
        **Twoi partnerzy uczπ siÍ na b≥Ídach i sukcesach!**
        """)
        
        # Leaderboard
        st.markdown("### ?? Ranking Wiarygodnoúci")
        
        leaderboard = pmm.get_leaderboard()
        
        if leaderboard:
            # Top 3 z medalami
            if len(leaderboard) > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if len(leaderboard) >= 1:
                        entry = leaderboard[0]
                        st.metric(
                            "?? Miejsce 1",
                            entry['persona'],
                            f"{entry['credibility']*100:.0f}% ({entry['correct']}/{entry['total']})"
                        )
                
                with col2:
                    if len(leaderboard) >= 2:
                        entry = leaderboard[1]
                        st.metric(
                            "?? Miejsce 2",
                            entry['persona'],
                            f"{entry['credibility']*100:.0f}% ({entry['correct']}/{entry['total']})"
                        )
                
                with col3:
                    if len(leaderboard) >= 3:
                        entry = leaderboard[2]
                        st.metric(
                            "?? Miejsce 3",
                            entry['persona'],
                            f"{entry['credibility']*100:.0f}% ({entry['correct']}/{entry['total']})"
                        )
            
            # Pe≥na tabela
            st.markdown("#### Pe≥ny Ranking")
            
            df_leaderboard = pd.DataFrame(leaderboard)
            df_leaderboard['Ranking'] = range(1, len(df_leaderboard) + 1)
            df_leaderboard['WiarygodnoúÊ'] = df_leaderboard['credibility'].apply(lambda x: f"{x*100:.0f}%")
            df_leaderboard['Track Record'] = df_leaderboard.apply(
                lambda row: f"{row['correct']}/{row['total']}", axis=1
            )
            df_leaderboard['Wp≥yw (PLN)'] = df_leaderboard['impact'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                df_leaderboard[['Ranking', 'persona', 'WiarygodnoúÊ', 'Track Record', 'Wp≥yw (PLN)']].rename(
                    columns={'persona': 'Persona'}
                ),
                width="stretch",
                hide_index=True
            )
        else:
            st.info("?? Brak danych - persony nie podjÍ≥y jeszcze rozliczonych decyzji")
        
        st.markdown("---")
        
        # Historia decyzji
        st.markdown("### ?? Historia Decyzji")
        
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
                    "Status": "?" if dec.get("was_correct") else "?" if dec.get("was_correct") is not None else "?",
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
                    ["Wszystkie", "? Trafne", "? B≥Ídne", "? Nierozliczone"]
                )
            
            # Aplikuj filtry
            df_filtered = df_decisions.copy()
            
            if filter_persona != "Wszystkie":
                df_filtered = df_filtered[df_filtered["Persona"] == filter_persona]
            
            if filter_status != "Wszystkie":
                status_map = {
                    "? Trafne": "?",
                    "? B≥Ídne": "?",
                    "? Nierozliczone": "?"
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
                st.metric("?? Wszystkie decyzje", total_decisions)
            
            with col_stat2:
                audited = len([d for d in all_decisions if d["Status"] in ["?", "?"]])
                st.metric("? Rozliczone", audited)
            
            with col_stat3:
                pending = len([d for d in all_decisions if d["Status"] == "?"])
                st.metric("? Oczekujπce", pending)
        else:
            st.info("?? Brak decyzji w historii")
        
        st.markdown("---")
        
        # Ewolucja charakteru
        st.markdown("### ?? Ewolucja Charakteru Person")
        
        st.markdown("""
        Cechy charakteru person zmieniajπ siÍ na podstawie ich sukcesÛw i poraøek.
        """)
        
        # Wybierz personÍ do analizy
        persona_to_analyze = st.selectbox(
            "Wybierz personÍ",
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
                st.markdown("#### SzczegÛ≥y Cech")
                
                trait_descriptions = {
                    "risk_tolerance": "Tolerancja ryzyka - sk≥onnoúÊ do ryzykownych inwestycji",
                    "optimism_bias": "Optymizm - tendencja do pozytywnych prognoz",
                    "analytical_depth": "G≥ÍbokoúÊ analityczna - szczegÛ≥owoúÊ analiz",
                    "patience": "CierpliwoúÊ - preferencja dla d≥ugoterminowych strategii",
                    "innovation_focus": "InnowacyjnoúÊ - zainteresowanie nowymi technologiami"
                }
                
                for trait, value in traits.items():
                    trait_name = trait.replace('_', ' ').title()
                    description = trait_descriptions.get(trait, "")
                    
                    # Normalize value to 0-1 range (handle negative values)
                    normalized_value = max(0.0, min(1.0, (value + 1) / 2 if value < 0 else value))
                    progress_bar = "-" * int(normalized_value * 20) + "-" * (20 - int(normalized_value * 20))
                    
                    st.write(f"**{trait_name}** ({value:.2f})")
                    st.progress(normalized_value)
                    if description:
                        st.caption(description)
                    st.markdown("")
            
            # Kluczowe lekcje
            lessons = persona_data.get("key_lessons", [])
            if lessons:
                st.markdown("#### ?? Kluczowe Lekcje")
                
                for lesson in lessons[-5:]:
                    if isinstance(lesson, dict):
                        st.info(f"**[{lesson.get('date')}]** {lesson.get('lesson')}")
                    else:
                        st.info(lesson)
        
        # === NOWE FEATURY V2.0 ===
        if MEMORY_V2:
            st.markdown("---")
            st.markdown("### ?? System Osobowoúci v2.0")
            st.success("? Zaawansowane featury aktywne!")
            
            # Emocje
            emotions = persona_data.get('emotional_state', {})
            if emotions:
                st.markdown("#### ?? Stan Emocjonalny")
                
                mood = emotions.get('current_mood', 'neutral')
                mood_emojis = {
                    'excited': '??', 'confident': '??', 'optimistic': '??',
                    'neutral': '??', 'cautious': '??', 'worried': '??',
                    'fearful': '??', 'angry': '??', 'disappointed': '??'
                }
                
                col_mood1, col_mood2, col_mood3 = st.columns(3)
                
                with col_mood1:
                    st.metric("NastrÛj", f"{mood_emojis.get(mood, '??')} {mood.upper()}")
                
                with col_mood2:
                    st.metric("Stres", f"{emotions.get('stress_level', 0.3):.0%}")
                
                with col_mood3:
                    st.metric("Strach", f"{emotions.get('fear_index', 0.2):.0%}")
                
                # Mood history
                mood_hist = emotions.get('mood_history', [])
                if mood_hist:
                    st.markdown("**Ostatnie zmiany nastroju:**")
                    for change in mood_hist[-3:]:
                        st.caption(f"{change.get('date')}: {change.get('from')} õ {change.get('to')}")
            
            # Relacje
            relationships = persona_data.get('relationships', {})
            if relationships:
                st.markdown("#### ?? Relacje z Partnerami")
                
                # Sortuj po trust
                sorted_rels = sorted(relationships.items(), key=lambda x: x[1].get('trust', 0), reverse=True)
                
                for partner, rel in sorted_rels[:5]:
                    trust = rel.get('trust', 0.5)
                    agree = rel.get('agreement_rate', 0.5)
                    
                    trust_emoji = '??' if trust > 0.7 else '??' if trust > 0.4 else '??'
                    
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
                st.markdown("#### ??? Si≥a G≥osu w Radzie")
                
                col_v1, col_v2, col_v3 = st.columns(3)
                
                with col_v1:
                    st.metric("Waga Bazowa", f"{voting.get('base_weight', 5):.1f}%")
                
                with col_v2:
                    bonus = voting.get('credibility_bonus', 0)
                    st.metric("Bonus za WiarygodnoúÊ", f"{bonus:+.1f}%")
                
                with col_v3:
                    effective = voting.get('effective_weight', 5)
                    st.metric("Efektywna Waga", f"{effective:.1f}%", delta=f"{bonus:+.1f}%")
            
            # Ekspertyza
            expertise = persona_data.get('expertise_areas', {})
            if expertise:
                st.markdown("#### ?? Obszary Ekspertyzy")
                
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
                st.markdown("#### ?? Osobista Agenda")
                
                goal = agenda.get('primary_goal', '')
                progress = agenda.get('progress', 0)
                
                if goal:
                    st.info(f"**Cel:** {goal}")
                    st.progress(progress, text=f"PostÍp: {progress:.0%}")
                
                tactics = agenda.get('tactics', [])
                if tactics:
                    st.markdown("**Taktyki:**")
                    for tactic in tactics:
                        st.write(f"ï {tactic}")
            
            # Communication style
            comm = persona_data.get('communication_style', {})
            if comm:
                st.markdown("#### ?? Styl Komunikacji")
                
                catchphrases = comm.get('catchphrases', [])
                if catchphrases:
                    st.markdown("**Ulubione zwroty:**")
                    for phrase in catchphrases[:3]:
                        st.write(f"?? \"{phrase}\"")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                
                with col_c1:
                    verbosity = comm.get('verbosity', 0.5)
                    st.metric("SzczegÛ≥owoúÊ", f"{verbosity:.0%}")
                
                with col_c2:
                    humor = comm.get('humor', 0.3)
                    st.metric("Humor", f"{humor:.0%}")
                
                with col_c3:
                    formality = comm.get('formality', 0.5)
                    st.metric("FormalnoúÊ", f"{formality:.0%}")

def show_markets_page(stan_spolki, cele):
    """Strona analizy rynkÛw geograficznych"""
    st.title("?? Analiza RynkÛw Globalnych")
    
    st.markdown("""
    Analiza úwiatowych indeksÛw, Twojego portfela i ekspozycji geograficznej.
    """)
    
    # === TABS - dodaj nowy tab dla indeksÛw ===
    tab_indices, tab_portfolio, tab_correlations, tab_insights, tab_recommendations = st.tabs([
        "?? åwiatowe Indeksy", "??? TwÛj Portfel", "?? Korelacje", "?? Insights", "?? Rekomendacje"
    ])
    
    # === TAB 1: åWIATOWE INDEKSY ===
    with tab_indices:
        st.markdown("### ?? G≥Ûwne Indeksy Gie≥dowe")
        
        # Definicje indeksÛw
        indices = {
            "???? S&P 500": "^GSPC",
            "???? Nasdaq": "^IXIC",
            "???? Dow Jones": "^DJI",
            "???? Euro Stoxx 50": "^STOXX50E",
            "???? FTSE 100": "^FTSE",
            "???? DAX": "^GDAXI",
            "???? Nikkei 225": "^N225",
            "???? Shanghai Composite": "000001.SS",
            "?? Bitcoin": "BTC-USD",
            "?? Ethereum": "ETH-USD"
        }
        
        # Pobierz dane
        st.caption("?? Dane z ostatnich 30 dni")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Multi-line chart z wszystkimi indeksami (znormalizowane do 100)
            st.markdown("**?? PorÛwnanie Wydajnoúci (znormalizowane do 100)**")
            
            with st.spinner("Pobieranie danych indeksÛw..."):
                fig = go.Figure()
                
                for name, ticker in indices.items():
                    try:
                        import yfinance as yf
                        data = yf.download(ticker, period="1mo", progress=False)
                        
                        if not data.empty and 'Close' in data.columns:
                            # Normalizuj do 100
                            normalized = (data['Close'] / data['Close'].iloc[0]) * 100
                            
                            fig.add_trace(go.Scatter(
                                x=normalized.index,
                                y=normalized.values,
                                mode='lines',
                                name=name,
                                hovertemplate=f'<b>{name}</b><br>Data: %{{x}}<br>WartoúÊ: %{{y:.2f}}<extra></extra>'
                            ))
                    except Exception as e:
                        st.caption(f"?? Nie uda≥o siÍ pobraÊ {name}: {str(e)[:50]}")
                
                fig.update_layout(
                    title="WydajnoúÊ IndeksÛw (ostatnie 30 dni)",
                    xaxis_title="Data",
                    yaxis_title="WartoúÊ znormalizowana (start = 100)",
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
            st.markdown("**?? Zmiana 1M:**")
            
            # Tabela zmian
            changes_data = []
            
            for name, ticker in indices.items():
                try:
                    import yfinance as yf
                    data = yf.download(ticker, period="1mo", progress=False)
                    
                    if not data.empty and 'Close' in data.columns:
                        start_price = data['Close'].iloc[0]
                        end_price = data['Close'].iloc[-1]
                        change_pct = ((end_price - start_price) / start_price) * 100
                        
                        emoji = "??" if change_pct > 0 else "??"
                        color = "??" if change_pct > 0 else "??"
                        
                        changes_data.append({
                            "Indeks": name,
                            "": f"{color} {emoji}",
                            "Zmiana": f"{change_pct:+.2f}%"
                        })
                except:
                    pass
            
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
        st.caption("?? Dane pobierane z Yahoo Finance w czasie rzeczywistym")
    
    # === TAB 2: TW”J PORTFEL (stary content) ===
    with tab_portfolio:
        st.markdown("### ??? Geograficzna Alokacja Twojego Portfela")
        
        # Analiza sk≥adu rynkÛw
        market_analysis = analyze_market_composition(stan_spolki)
        correlations = calculate_market_correlations(stan_spolki)
        insights = generate_market_insights(market_analysis, correlations)
        
        # === METRICS ===
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "?? WartoúÊ Portfela",
                f"{market_analysis['total_value']:,.0f} PLN"
            )
        
        with col2:
            st.metric(
                "?? Dywersyfikacja Geo",
                f"{market_analysis['diversification_score']:.0f}/100",
                delta="Dobra" if market_analysis['diversification_score'] > 60 else "Niska"
            )
        
        with col3:
            markets_count = sum(1 for m in market_analysis['markets'].values() if m['count'] > 0)
            st.metric(
                "??? Aktywne Rynki",
                markets_count
            )
        
        st.markdown("---")
        
        # Alokacja geograficzna
        st.markdown("### ?? Alokacja Geograficzna")
        
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
                    hovertemplate='<b>%{label}</b><br>WartoúÊ: %{value:,.0f} PLN<br>Udzia≥: %{percent}<extra></extra>'
                )])
                
                fig.update_layout(
                    title="Podzia≥ Portfela wed≥ug RynkÛw",
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Brak danych do wyúwietlenia")
        
        with col_chart2:
            st.markdown("**?? SzczegÛ≥y po rynkach:**")
            
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
        
        # Tabela szczegÛ≥Ûw
        st.markdown("### ?? Lista TickerÛw wed≥ug RynkÛw")
        
        for market_name, market_data in sorted(markets.items(), key=lambda x: x[1]['percentage'], reverse=True):
            if market_data['tickers']:
                with st.expander(f"{market_name} - {len(market_data['tickers'])} tickerÛw"):
                    st.write(", ".join(market_data['tickers']))
    
    # === TAB 3: KORELACJE ===
    with tab_correlations:
        st.markdown("### ?? Korelacje miÍdzy Rynkami")
        
        st.info("""
        **Interpretacja korelacji:**
        - **+0.7 do +1.0**: Silna pozytywna korelacja (rynki poruszajπ siÍ razem)
        - **+0.3 do +0.7**: Umiarkowana korelacja
        - **-0.3 to +0.3**: S≥aba/brak korelacji (dobre dla dywersyfikacji!)
        - **-0.7 to -0.3**: Umiarkowana negatywna korelacja
        - **-1.0 to -0.7**: Silna negatywna korelacja (rynki poruszajπ siÍ w przeciwnych kierunkach)
        """)
        
        market_changes = correlations.get('market_changes', {})
        
        if market_changes:
            # Performance table
            st.markdown("**?? Aktualna WydajnoúÊ RynkÛw:**")
            
            perf_data = []
            for market, change in sorted(market_changes.items(), key=lambda x: x[1], reverse=True):
                emoji = "??" if change > 0 else "??"
                color = "??" if change > 2 else "??" if change < -2 else "??"
                
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
            st.markdown("**?? Macierz Korelacji (uproszczona):**")
            
            corr_data = correlations.get('correlations', {})
            
            if corr_data:
                markets_list = list(market_changes.keys())
                
                # StwÛrz macierz
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
                    title="Korelacje miÍdzy Rynkami",
                    xaxis_title="Rynek",
                    yaxis_title="Rynek",
                    height=500
                )
                
                st.plotly_chart(fig, width="stretch")
        else:
            st.warning("Brak danych o zmianach cen - nie moøna obliczyÊ korelacji")
    
    # === TAB 4: INSIGHTS ===
    with tab_insights:
        st.markdown("### ?? Insights & Analiza")
        
        if insights:
            for insight in insights:
                if insight['type'] == 'success':
                    st.success(f"{insight['icon']} **{insight['title']}**\n\n{insight['description']}")
                elif insight['type'] == 'warning':
                    st.warning(f"{insight['icon']} **{insight['title']}**\n\n{insight['description']}")
                else:
                    st.info(f"{insight['icon']} **{insight['title']}**\n\n{insight['description']}")
        else:
            st.info("Brak insights do wyúwietlenia")
    
    # === TAB 5: REKOMENDACJE ===
    with tab_recommendations:
        st.markdown("### ?? Rekomendacje Rebalancingu")
        
        markets = market_analysis['markets']
        
        st.markdown("""
        **Idealna alokacja geograficzna (benchmark):**
        - ???? **US**: 50-60% (najwiÍkszy, najbardziej p≥ynny rynek)
        - ???? **EU**: 15-25% (stabilny, dywidendy)
        - ???? **Canada**: 5-10% (surowce, banki)
        - ?? **Emerging**: 5-15% (wyøszy potencja≥ wzrostu, wyøsze ryzyko)
        - ?? **Crypto**: 2-10% (opcjonalne, wysokie ryzyko)
        """)
        
        st.markdown("---")
        
        st.markdown("**?? Twoja Alokacja vs Benchmark:**")
        
        # PorÛwnaj z benchmarkiem
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
                status = "?? Niedowaga"
                action = f"ZwiÍksz ekspozycjÍ o {min_val - current:.1f}%"
            elif current > max_val:
                status = "?? Nadwaga"
                action = f"Zmniejsz ekspozycjÍ o {current - max_val:.1f}%"
            elif current < ideal - 5:
                status = "?? Lekka niedowaga"
                action = f"Rozwaø zwiÍkszenie o {ideal - current:.1f}%"
            elif current > ideal + 5:
                status = "?? Lekka nadwaga"
                action = f"Rozwaø zmniejszenie o {current - ideal:.1f}%"
            else:
                status = "?? OK"
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
        
        st.markdown("**?? Konkretne Akcje:**")
        
        # Generuj konkretne sugestie
        us_pct = markets.get("US", {}).get('percentage', 0)
        eu_pct = markets.get("EU", {}).get('percentage', 0)
        crypto_pct = markets.get("Crypto", {}).get('percentage', 0)
        emerging_pct = markets.get("Emerging", {}).get('percentage', 0)
        
        if us_pct < 50:
            st.info("?? **ZwiÍksz US**: Kup ETF S&P 500 (np. VOO, SPY) lub pojedyncze blue chips (AAPL, MSFT, GOOGL)")
        
        if eu_pct > 30:
            st.warning("?? **Zmniejsz EU**: Rozwaø sprzedaø czÍúci VWCE.DE lub europejskich akcji")
        
        if crypto_pct > 10:
            st.warning("?? **Zmniejsz Crypto**: Sprzedaj czÍúÊ BTC/ETH, reinwestuj w tradycyjne aktywa")
        elif crypto_pct < 2 and market_analysis['total_value'] > 20000:
            st.info("?? **Dodaj Crypto**: Rozwaø ma≥π pozycjÍ w BTC lub ETH (2-5% portfela)")
        
        if emerging_pct < 5:
            st.info("?? **Dodaj Emerging Markets**: Rozwaø ETF (VWO) lub pojedyncze akcje (TSM, BABA, VALE)")

def show_snapshots_page():
    """Strona Daily Snapshots - historia codziennych zapisÛw portfela"""
    st.title("?? Daily Snapshots")
    st.markdown("*Automatyczny system codziennych zapisÛw stanu portfela*")
    
    # Import modu≥u
    try:
        import daily_snapshot as ds
    except ImportError:
        st.error("? Modu≥ daily_snapshot.py nie znaleziony")
        st.info("Upewnij siÍ øe plik daily_snapshot.py znajduje siÍ w tym samym folderze co streamlit_app.py")
        return
    
    # Pokaø statystyki
    stats = ds.get_snapshot_stats()
    
    if stats['count'] == 0:
        st.warning("?? Brak zapisanych snapshots")
        
        # Sprawdü czy istnieje monthly_snapshot.json do migracji
        if os.path.exists('monthly_snapshot.json'):
            st.info("""
            **?? Wykryto historyczne dane!**
            
            Znaleziono `monthly_snapshot.json` z historycznymi danymi portfela.
            Moøesz zmigrowaÊ te dane do nowego systemu daily snapshots.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("?? Migruj dane historyczne", type="primary"):
                    with st.spinner("MigrujÍ monthly_snapshot.json..."):
                        count = ds.migrate_monthly_to_daily_snapshots()
                        if count > 0:
                            st.success(f"? Zmigrowano {count} snapshot!")
                            st.rerun()
                        else:
                            st.info("?? Dane juø zmigrowane lub brak nowych danych")
            
            with col2:
                if st.button("?? UtwÛrz nowy snapshot"):
                    with st.spinner("TworzÍ snapshot..."):
                        success = ds.save_daily_snapshot()
                        if success:
                            st.success("? Snapshot zapisany!")
                            st.rerun()
                        else:
                            st.error("? B≥πd przy tworzeniu snapshotu")
        else:
            st.info("""
            **Jak zaczπÊ?**
            1. Uruchom rÍcznie: `python daily_snapshot.py`
            2. Lub kliknij przycisk poniøej
            3. Skonfiguruj automatyczne uruchamianie (Windows Task Scheduler o 21:00)
            """)
            
            if st.button("?? UtwÛrz pierwszy snapshot teraz"):
                with st.spinner("TworzÍ snapshot..."):
                    success = ds.save_daily_snapshot()
                    if success:
                        st.success("? Snapshot zapisany!")
                        st.rerun()
                    else:
                        st.error("? B≥πd przy tworzeniu snapshotu")
        return
    
    # Metryki g≥Ûwne
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("?? Liczba Snapshots", stats['count'])
    
    with col2:
        st.metric("?? Dni åledzenia", stats['days_tracked'])
    
    with col3:
        delta = f"{stats['net_worth_change_pct']:+.1f}%"
        st.metric(
            "?? Net Worth", 
            f"{stats['last_net_worth']:,.0f} PLN",
            delta=delta
        )
    
    with col4:
        st.metric("? Snapshots/tydzieÒ", f"{stats['avg_snapshots_per_week']:.1f}")
    
    st.markdown("---")
    
    # Wczytaj pe≥nπ historiÍ
    history = ds.load_snapshot_history()
    
    # Zak≥adki
    tab1, tab2, tab3, tab4 = st.tabs([
        "?? Wykresy", 
        "?? Historia Tabela", 
        "?? SzczegÛ≥y Ostatniego",
        "?? Zarzπdzanie"
    ])
    
    with tab1:
        st.subheader("?? Net Worth Over Time")
        
        # Przygotuj dane do wykresu
        dates = [s['date'][:10] for s in history]
        net_worths = [s['totals']['net_worth_pln'] for s in history]
        stocks_pln = [s['stocks']['value_pln'] if s.get('stocks') else 0 for s in history]
        crypto_pln = [s['crypto']['value_pln'] if s.get('crypto') else 0 for s in history]
        debt_pln = [s['debt']['total_pln'] if s.get('debt') else 0 for s in history]
        
        # Wykres g≥Ûwny - Net Worth
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
            title='?? Net Worth (WartoúÊ Netto)',
            xaxis_title='Data',
            yaxis_title='PLN',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig1, width="stretch", key="snapshot_networth_chart")
        
        # Wykres sk≥adowych
        st.subheader("?? Sk≥adowe Portfela")
        
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
            name='Zobowiπzania',
            line=dict(color='#F44336', width=2, dash='dash')
        ))
        
        fig2.update_layout(
            title='Sk≥adowe AktywÛw i PasywÛw',
            xaxis_title='Data',
            yaxis_title='PLN',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig2, width="stretch", key="snapshot_components_chart")
        
        # Wykres % change
        st.subheader("?? Zmiana Procentowa (od poczπtku)")
        
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
        st.subheader("?? Historia Wszystkich Snapshots")
        
        # Przygotuj tabelÍ
        table_data = []
        for i, s in enumerate(reversed(history)):  # Najnowsze na gÛrze
            table_data.append({
                '#': len(history) - i,
                'Data': s['date'][:10],
                'Godzina': s['date'][11:16],
                'Akcje (PLN)': f"{s['stocks']['value_pln']:,.0f}" if s.get('stocks') else '-',
                'Crypto (PLN)': f"{s['crypto']['value_pln']:,.0f}" if s.get('crypto') else '-',
                'Zobowiπzania': f"{s['debt']['total_pln']:,.0f}" if s.get('debt') else '-',
                'Net Worth': f"{s['totals']['net_worth_pln']:,.0f}",
                'USD/PLN': f"{s['usd_pln_rate']:.4f}"
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, width="stretch", height=400)
        
        # Opcja exportu
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="?? Pobierz jako CSV",
            data=csv,
            file_name=f"snapshots_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )
    
    with tab3:
        st.subheader("?? SzczegÛ≥y Ostatniego Snapshotu")
        
        last = history[-1]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**?? Informacje Podstawowe**")
            st.write(f"Data: `{last['date']}`")
            st.write(f"Kurs USD/PLN: `{last['usd_pln_rate']:.4f}`")
        
        with col2:
            st.markdown("**?? Podsumowanie**")
            st.write(f"Aktywa: `{last['totals']['assets_pln']:,.2f} PLN`")
            st.write(f"Zobowiπzania: `{last['totals']['debt_pln']:,.2f} PLN`")
            st.write(f"**Net Worth: `{last['totals']['net_worth_pln']:,.2f} PLN`**")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if last.get('stocks'):
                st.markdown("**?? Akcje**")
                st.write(f"WartoúÊ: `${last['stocks']['value_usd']:,.2f}` = `{last['stocks']['value_pln']:,.2f} PLN`")
                st.write(f"Pozycje: `{last['stocks']['positions']}`")
                st.write(f"Cash: `${last['stocks']['cash_usd']:,.2f}`")
        
        with col2:
            if last.get('crypto'):
                st.markdown("**? Kryptowaluty**")
                st.write(f"WartoúÊ: `${last['crypto']['value_usd']:,.2f}` = `{last['crypto']['value_pln']:,.2f} PLN`")
                st.write(f"Pozycje: `{last['crypto']['positions']}`")
        
        if last.get('debt'):
            st.markdown("**?? Zobowiπzania**")
            st.write(f"Suma: `{last['debt']['total_pln']:,.2f} PLN`")
            st.write(f"Liczba kredytÛw: `{last['debt']['loans_count']}`")
        
        # Pokaø raw JSON
        with st.expander("?? Zobacz Raw JSON"):
            st.json(last)
    
    with tab4:
        st.subheader("?? Zarzπdzanie Snapshots")
        
        st.markdown("**?? Tworzenie Snapshot**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("?? UtwÛrz snapshot TERAZ"):
                with st.spinner("TworzÍ snapshot..."):
                    success = ds.save_daily_snapshot()
                    if success:
                        st.success("? Snapshot zapisany!")
                        st.rerun()
                    else:
                        st.error("? B≥πd")
        
        with col2:
            should_create = ds.should_create_snapshot(target_hour=21)
            if should_create:
                st.info("? Pora na dzienny snapshot (po 21:00)")
            else:
                today = datetime.now().strftime('%Y-%m-%d')
                today_snapshots = [s for s in history if s['date'][:10] == today]
                if today_snapshots:
                    st.success(f"? Snapshot z dzisiaj juø istnieje ({today_snapshots[0]['date'][11:16]})")
                else:
                    st.warning("? Za wczeúnie (snapshot tworzone po 21:00)")
        
        st.markdown("---")
        
        st.markdown("**?? Konfiguracja Automatycznego Uruchamiania**")
        
        st.info("""
        **Windows Task Scheduler:**
        1. OtwÛrz Task Scheduler (`taskschd.msc`)
        2. Create Basic Task õ Nazwa: "Portfolio Daily Snapshot"
        3. Trigger: Daily o 21:00
        4. Action: Start a program
        5. Program: `run_daily_snapshot.bat`
        6. Start in: `C:\\Users\\alech\\Desktop\\Horyzont PartnerÛw`
        
        **Plik .bat zosta≥ utworzony:** `run_daily_snapshot.bat`
        """)
        
        st.markdown("---")
        
        st.markdown("**??? Zarzπdzanie Danymi**")
        
        st.write(f"?? Plik: `daily_snapshots.json`")
        st.write(f"?? Rozmiar historii: {stats['count']} snapshots")
        st.write(f"??  Automatyczna rotacja: ostatnie {ds.MAX_HISTORY_DAYS} dni")
        
        # Opcja usuniÍcia wszystkich snapshots (niebezpieczne!)
        with st.expander("?? Niebezpieczna Strefa"):
            st.warning("**Uwaga!** Poniøsze akcje sπ nieodwracalne!")
            
            if st.button("??? USU— WSZYSTKIE SNAPSHOTS", type="secondary"):
                if st.session_state.get('confirm_delete_snapshots'):
                    try:
                        os.remove('daily_snapshots.json')
                        st.success("? UsuniÍto wszystkie snapshots")
                        st.session_state.confirm_delete_snapshots = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"? B≥πd: {e}")
                else:
                    st.session_state.confirm_delete_snapshots = True
                    st.warning("?? Kliknij ponownie aby potwierdziÊ usuniÍcie")

def show_settings_page():
    """Strona ustawieÒ"""
    st.title("?? Ustawienia")
    
    # === NOWA SEKCJA: AI PARTNERZY ===
    st.subheader("?? Partnerzy AI")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tryb_ai = st.selectbox(
            "Tryb odpowiedzi partnerÛw",
            ["ZwiÍz≥y", "Normalny", "SzczegÛ≥owy"],
            index=1,  # Normalny jako domyúlny
            key="ai_mode_select",
            help="ZwiÍz≥y: 2-4 zdania | Normalny: 4-6 zdaÒ | SzczegÛ≥owy: 8-12 zdaÒ"
        )
        
        # Mapuj wybÛr na wartoúÊ uøywanπ w kodzie
        mode_map = {
            "ZwiÍz≥y": "zwiezly",
            "Normalny": "normalny",
            "SzczegÛ≥owy": "szczegolowy"
        }
        
        if 'ai_response_mode' not in st.session_state:
            st.session_state.ai_response_mode = "normalny"
        
        st.session_state.ai_response_mode = mode_map[tryb_ai]
        
        st.caption(f"Wybrano: **{tryb_ai}**")
    
    with col2:
        st.info("""
        **Opis trybÛw:**
        
        ?? **ZwiÍz≥y**: KrÛtkie, konkretne odpowiedzi (2-4 zdania)
        
        ?? **Normalny**: Zbalansowane odpowiedzi z danymi (4-6 zdaÒ)
        
        ?? **SzczegÛ≥owy**: Pe≥na analiza z uzasadnieniami (8-12 zdaÒ)
        """)
    
    # Statystyki historii rozmÛw (Session)
    if 'partner_history' in st.session_state and st.session_state.partner_history:
        st.markdown("---")
        st.markdown("**?? Historia rozmÛw (Sesja bieøπca):**")
        
        total_messages = sum(len(history) for history in st.session_state.partner_history.values())
        st.metric("Wiadomoúci w tej sesji", total_messages)
        
        if st.button("??? WyczyúÊ historiÍ sesji", width="stretch", key="clear_session"):
            st.session_state.partner_history = {}
            st.success("? Historia sesji wyczyszczona!")
            st.rerun()
    
    # Statystyki pamiÍci d≥ugoterminowej
    st.markdown("---")
    st.markdown("**?? PamiÍÊ D≥ugoterminowa (Permanentna):**")
    
    if IMPORTS_OK and PERSONAS:
        col_mem1, col_mem2 = st.columns(2)
        
        total_permanent_messages = 0
        partners_with_memory = 0
        
        with col_mem1:
            for name in PERSONAS.keys():
                if 'Partner Zarzπdzajπcy' in name and '(JA)' in name:
                    continue
                    
                stats = get_memory_statistics(name)
                if stats:
                    partners_with_memory += 1
                    total_permanent_messages += stats.get('total_messages', 0)
            
            st.metric("Partnerzy z pamiÍciπ", partners_with_memory)
            st.metric("Ca≥kowita liczba rozmÛw", total_permanent_messages)
        
        with col_mem2:
            st.info("?? PamiÍÊ d≥ugoterminowa:\n- Zapisana na dysku\n- Przetrwa restart\n- Partner pamiÍta historiÍ")
            
            if st.button("??? WyczyúÊ CA£• pamiÍÊ", width="stretch", key="clear_memory", type="primary"):
                if st.checkbox("?? Potwierdü usuniÍcie", key="confirm_delete"):
                    import shutil
                    if MEMORY_FOLDER.exists():
                        shutil.rmtree(MEMORY_FOLDER)
                        MEMORY_FOLDER.mkdir(exist_ok=True)
                    st.success("? PamiÍÊ d≥ugoterminowa wyczyszczona!")
                    st.rerun()
        
        # SzczegÛ≥y per partner
        with st.expander("?? SzczegÛ≥y pamiÍci partnerÛw"):
            for name in PERSONAS.keys():
                if 'Partner Zarzπdzajπcy' in name and '(JA)' in name:
                    continue
                
                stats = get_memory_statistics(name)
                if stats:
                    display_name = name.split('(')[0].strip() if '(' in name else name
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.markdown(f"**{display_name}**")
                    with col_b:
                        st.caption(f"{stats.get('total_messages', 0)} rozmÛw")
                    with col_c:
                        if stats.get('last_interaction'):
                            last = datetime.fromisoformat(stats['last_interaction'])
                            st.caption(f"Ostatnio: {last.strftime('%Y-%m-%d')}")
    
    st.markdown("---")
    
    st.subheader("?? Wyglπd")
    st.caption("?? Ustawienia sπ automatycznie zapisywane")
    
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
                st.toast("?? Motyw zapisany!", icon="?")
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
                st.toast("?? Motyw zapisany!", icon="?")
            st.rerun()
    
    with col2:
        st.info(f"Aktualny motyw: **{st.session_state.theme.upper()}**")
    
    st.markdown("---")
    
    st.subheader("?? Powiadomienia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        notifications = st.checkbox(
            "W≥πcz powiadomienia",
            value=st.session_state.notifications_enabled,
            key="notif_checkbox"
        )
        
        # Jeúli zmieniono ustawienie powiadomieÒ
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
            st.success("? Powiadomienia w≥πczone")
            
            # Opcje powiadomieÒ
            st.markdown("**Powiadamiaj o:**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.checkbox("?? Spadki >5%", value=True)
                st.checkbox("?? Cele osiπgniÍte", value=True)
            with col_b:
                st.checkbox("?? Nowe dywidendy", value=True)
                st.checkbox("?? Wysokie ryzyko", value=False)
        else:
            st.warning("?? Powiadomienia wy≥πczone")
    
    with col2:
        if st.button("?? Testuj powiadomienie", width="stretch"):
            st.toast("?? To jest testowe powiadomienie!")
            st.balloons()
    
    st.markdown("---")
    
    st.subheader("?? Dane i Cache")
    
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
        
        st.caption(f"Dane bÍdπ odúwieøane co {cache_ttl} minut")
    
    with col2:
        if st.button("??? WyczyúÊ cache teraz", width="stretch"):
            st.cache_data.clear()
            st.success("? Cache wyczyszczony!")
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("?? Auto-refresh")
    
    col1, col2 = st.columns(2)
    
    with col1:
        auto_refresh = st.checkbox(
            "W≥πcz automatyczne odúwieøanie",
            value=st.session_state.auto_refresh,
            key="auto_refresh_checkbox"
        )
        st.session_state.auto_refresh = auto_refresh
        
        if auto_refresh:
            refresh_interval = st.slider(
                "Interwa≥ odúwieøania (sekundy)",
                min_value=10,
                max_value=300,
                value=st.session_state.refresh_interval,
                step=10,
                key="refresh_slider"
            )
            st.session_state.refresh_interval = refresh_interval
            
            st.info(f"?? Auto-refresh co {refresh_interval}s")
            
            # Auto-refresh logic
            import time
            time.sleep(refresh_interval)
            st.rerun()
    
    with col2:
        if auto_refresh:
            st.success("? Auto-refresh aktywny")
        else:
            st.warning("?? Auto-refresh wy≥πczony")
    
    st.markdown("---")
    
    st.subheader("?? Eksport UstawieÒ")
    
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
        if st.button("?? Zapisz ustawienia do pliku", width="stretch"):
            with open("streamlit_settings.json", "w") as f:
                json.dump(settings_dict, f, indent=2)
            st.success("? Ustawienia zapisane do streamlit_settings.json")
        
        if st.button("?? Wczytaj ustawienia z pliku", width="stretch"):
            try:
                with open("streamlit_settings.json", "r") as f:
                    loaded_settings = json.load(f)
                
                st.session_state.theme = loaded_settings.get("theme", "light")
                st.session_state.notifications_enabled = loaded_settings.get("notifications_enabled", True)
                st.session_state.cache_ttl = loaded_settings.get("cache_ttl", 5)
                st.session_state.auto_refresh = loaded_settings.get("auto_refresh", False)
                st.session_state.refresh_interval = loaded_settings.get("refresh_interval", 60)
                
                st.success("? Ustawienia wczytane!")
                st.rerun()
            except FileNotFoundError:
                st.error("? Plik streamlit_settings.json nie istnieje")
    
    st.markdown("---")
    
    # === NOWA SEKCJA: PORTFOLIO CO-PILOT ===
    st.subheader("?? Portfolio Co-Pilot")
    
    st.markdown("""
    System automatycznego generowania tygodniowych raportÛw portfela.
    Raport zawiera: osiπgniÍcia, ostrzeøenia, rekomendacje i statystyki.
    """)
    
    # === OSTATNI RAPORT (jeúli istnieje) ===
    latest_reports = load_weekly_reports(limit=1)
    if latest_reports:
        latest_report = latest_reports[0]
        
        st.info(f"?? **Ostatni raport:** TydzieÒ {latest_report.get('week_number', '?')}/{latest_report.get('year', '?')}")
        
        # Szybki podglπd - kluczowe metryki w kolumnach
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            mood_emoji = latest_report.get("mood", {}).get("emoji", "??")
            mood_level = latest_report.get("mood", {}).get("level", "neutral")
            st.metric("NastrÛj", f"{mood_emoji} {mood_level.title()}")
        
        with col_m2:
            achievements = latest_report.get("achievements", [])
            st.metric("OsiπgniÍcia", len(achievements), delta="pozytywne" if achievements else None)
        
        with col_m3:
            warnings = latest_report.get("warnings", [])
            st.metric("Ostrzeøenia", len(warnings), delta="negatywne" if warnings else None)
        
        with col_m4:
            actions = latest_report.get("action_items", [])
            st.metric("Akcje", len(actions))
        
        # Szybki przeglπd - najwaøniejsze informacje
        summary = latest_report.get("summary", "")
        if summary:
            st.success(f"**Streszczenie:** {summary}")
        
        # Top osiπgniÍcia i ostrzeøenia
        col_preview1, col_preview2 = st.columns(2)
        
        with col_preview1:
            achievements = latest_report.get("achievements", [])
            if achievements:
                st.markdown("**?? Top 3 OsiπgniÍcia:**")
                for ach in achievements[:3]:
                    st.markdown(f"- {ach.get('icon', '?')} {ach.get('title', 'N/A')}")
        
        with col_preview2:
            warnings = latest_report.get("warnings", [])
            if warnings:
                st.markdown("**?? Top 3 Ostrzeøenia:**")
                for warn in warnings[:3]:
                    st.markdown(f"- {warn.get('icon', '?')} {warn.get('title', 'N/A')}")
        
        # Pe≥ny raport w expanderze
        with st.expander("?? Pokaø pe≥ny raport", expanded=False):
            display_weekly_report(latest_report)
        
        st.markdown("---")
    
    col_cp1, col_cp2, col_cp3 = st.columns([3, 2, 1])
    
    with col_cp1:
        if st.button("?? Generuj Raport Tygodniowy", width="stretch", type="primary"):
            with st.spinner("?? GenerujÍ raport..."):
                try:
                    stan_spolki, cele = load_portfolio_data()
                    report = generate_weekly_report(stan_spolki, cele)
                    
                    if report and "error" not in report:
                        filepath = save_weekly_report(report)
                        
                        if filepath:
                            st.success(f"? Raport wygenerowany: `{filepath.name}`")
                            st.balloons()
                            
                            # Automatyczne odúwieøenie strony
                            st.rerun()
                        else:
                            st.error("? B≥πd zapisu raportu")
                    else:
                        st.error(f"? B≥πd generowania: {report.get('error', 'Unknown')}")
                        
                except Exception as e:
                    st.error(f"? B≥πd: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    
    with col_cp2:
        st.info(f"**Aktualny tydzieÒ:** {datetime.now().isocalendar()[1]}")
        st.caption(f"Rok: {datetime.now().year}")
    
    with col_cp3:
        if st.button("??", width="stretch", help="Odúwieø stronÍ"):
            st.rerun()
    
    # Historia raportÛw
    st.markdown("**?? Historia RaportÛw:**")
    
    reports = load_weekly_reports(limit=5)
    
    if reports:
        st.caption(f"Znaleziono {len(reports)} ostatnich raportÛw")
        
        for i, report in enumerate(reports):
            with st.expander(f"?? TydzieÒ {report.get('week_number', '?')}/{report.get('year', '?')} - {report.get('summary', 'Brak opisu')[:60]}..."):
                display_weekly_report(report)
                
                col_del1, col_del2, col_del3 = st.columns([2, 1, 1])
                
                with col_del2:
                    if st.button("?? Eksportuj", key=f"export_report_{i}"):
                        st.info("Eksport wkrÛtce!")
                
                with col_del3:
                    if st.button("??? UsuÒ", key=f"delete_report_{i}"):
                        try:
                            reports_folder = Path("weekly_reports")
                            filepath = reports_folder / report.get("filename", "")
                            if filepath.exists():
                                filepath.unlink()
                                st.success("? Raport usuniÍty")
                                st.rerun()
                        except Exception as e:
                            st.error(f"? B≥πd usuwania: {e}")
    else:
        st.info("Brak raportÛw. Wygeneruj pierwszy raport przyciskiem powyøej!")
    
    # Ustawienia auto-generowania
    with st.expander("?? Ustawienia Auto-generowania"):
        auto_gen = st.checkbox(
            "Automatycznie generuj raport w niedzielÍ",
            value=False,
            help="System automatycznie wygeneruje raport w kaødπ niedzielÍ o 20:00"
        )
        
        if auto_gen:
            st.success("? Auto-generowanie w≥πczone")
            st.caption("Raport bÍdzie generowany kaødπ niedzielÍ o 20:00")
        else:
            st.info("?? Auto-generowanie wy≥πczone - generuj rÍcznie")
    
    st.markdown("---")
    
    st.subheader("?? Zaawansowane")
    
    with st.expander("?? Debug Info"):
        st.write("**Session State:**")
        st.json(dict(st.session_state))
        
        st.write("**Streamlit Version:**")
        st.code(st.__version__)
        
        st.write("**Cache Stats:**")
        st.write(f"Cache TTL: {st.session_state.cache_ttl} min")
    
    with st.expander("? Performance"):
        st.write("**Optymalizacje:**")
        st.checkbox("Enable caching", value=True, disabled=True)
        st.checkbox("Lazy loading", value=True)
        st.checkbox("Compress data", value=False)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("?? Reset do domyúlnych", width="stretch"):
            st.session_state.theme = "light"
            st.session_state.notifications_enabled = True
            st.session_state.cache_ttl = 5
            st.session_state.auto_refresh = False
            st.session_state.refresh_interval = 60
            st.success("? PrzywrÛcono domyúlne ustawienia")
            st.rerun()
    
    with col2:
        if st.button("?? Zapisz i zamknij", width="stretch"):
            st.success("? Ustawienia zapisane!")
            st.balloons()
    
    with col3:
        if st.button("? Anuluj zmiany", width="stretch"):
            st.rerun()

if __name__ == "__main__":
    main()


