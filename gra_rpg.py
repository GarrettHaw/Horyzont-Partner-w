# === LAZY IMPORTS - AI biblioteki ładowane tylko gdy potrzebne ===
# import google.generativeai as genai  # -> lazy load w get_ai_client()
# import openai  # -> lazy load w get_ai_client()
# import anthropic  # -> lazy load w get_ai_client()

import os
import random
import json
# import gspread  # -> lazy load w pobierz_stan_spolki()
import asyncio
import certifi

# Konfiguracja certyfikatów SSL
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()
from google.oauth2.service_account import Credentials
import time
import ast
from dotenv import load_dotenv
from datetime import datetime
from collections import Counter
import re
import requests
import calendar
import yfinance as yf
import pandas as pd
import logging

# API Usage Tracker
from api_usage_tracker import get_tracker

# Import systemu pamięci person
try:
    import persona_memory_manager as pmm
    from persona_context_builder import build_enhanced_context, get_emotional_modifier
    PERSONA_MEMORY_ENABLED = True
    PERSONA_MEMORY_V2 = True
    print("✓ System pamięci AI v2.0 włączony (emocje, relacje, voting weights)")
except ImportError:
    PERSONA_MEMORY_ENABLED = False
    PERSONA_MEMORY_V2 = False
    print("⚠️ System pamięci AI niedostępny")

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import ssl
import socket
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from cache_manager import CacheManager
from analiza_portfela import przeprowadz_analize_portfela, wyswietl_raport_analizy
from dashboard_wizualizacje import wyswietl_dashboard
from portfolio_simulator import PortfolioSimulator, ScenarioAnalyzer
from risk_analytics import RiskAnalytics, PortfolioHistory
from animated_timeline import AnimatedTimeline, display_timeline

try:
    from excel_reporter import generate_full_report
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# Portfolio History Manager
portfolio_history = PortfolioHistory()

# Cache manager dla danych YFinance
yf_cache = CacheManager('yfinance_cache.json')

# Wyczyść cache przy starcie (tylko raz)
if os.path.exists('cache_migrated.flag'):
    print("🔄 Cache już zmigrowany")
else:
    print("🔄 Migracja cache'u do nowego formatu...")
    yf_cache.clear()  # Wyczyść cały cache
    # Utwórz flagę, że cache został zmigrowany
    with open('cache_migrated.flag', 'w') as f:
        f.write('1')

# Konfiguracja SSL
import ssl
import certifi
import requests
from urllib3 import poolmanager
import urllib3

def configure_ssl():
    """Konfiguruje certyfikaty SSL dla wszystkich bibliotek"""
    cert_path = certifi.where()
    
    # Konfiguracja dla requests/urllib3
    poolmanager.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=cert_path
    )
    
    # Konfiguracja dla SSL
    ssl_context = ssl.create_default_context(cafile=cert_path)
    ssl._create_default_https_context = lambda: ssl_context
    
    # Konfiguracja dla requests
    requests.utils.DEFAULT_CA_BUNDLE_PATH = cert_path
    urllib3.util.ssl_.DEFAULT_CERT_FILE = cert_path

# Wykonaj konfigurację SSL
configure_ssl()

# Manager asynchronicznego pobierania danych
from async_data_manager import AsyncDataManager
async_manager = AsyncDataManager(yf_cache)

def clear_market_cache():
    """Czyści cache danych rynkowych"""
    yf_cache.clear('market_data')
    print("🔄 Cache danych rynkowych wyczyszczony")

# ------------------ KONFIGURACJA ------------------

# Wyłączanie denerwujących logów z bibliotek Google
os.environ['GRPC_VERBOSITY'] = 'ERROR'

# === DEFINICJE FUNKCJI POMOCNICZYCH ===
def print_colored(text, color_code):
    """Drukuje tekst w kolorze."""
    print(f"{color_code}{text}\033[0m")

# Funkcja do bezpiecznego pobierania kluczy API
def get_api_key(key_name):
    """Pobiera klucz API z Streamlit Secrets lub zmiennych środowiskowych."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
    except:
        pass
    return os.getenv(key_name)

load_dotenv()
GOOGLE_API_KEY = get_api_key("GOOGLE_API_KEY")
TRADING212_API_KEY = get_api_key("TRADING212_API_KEY")

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "":
    print("\033[91m" + "="*60)
    print("BŁĄD KRYTYCZNY: Brak klucza API!")
    print("="*60)
    print("Nie znaleziono klucza GOOGLE_API_KEY.")
    print("\nAby naprawić:")
    print("1. W Streamlit Cloud: Settings → Secrets → dodaj GOOGLE_API_KEY")
    print("2. Lokalnie: Utwórz plik '.env' i dodaj: GOOGLE_API_KEY=twoj_klucz")
    print("3. Zainstaluj: pip install python-dotenv")
    print("="*60 + "\033[0m")
    exit(1)
def wait_for_gemini_rate_limit():
    """
    Sprawdza czas ostatniego zapytania do Gemini i czeka,
    aby nie przekroczyć limitu 2 zapytań na minutę.
    """
    GEMINI_TIMESTAMP_FILE = "gemini_last_call.txt"
    # Bezpieczny odstęp między zapytaniami (2 na minutę -> 1 co 30s. Dajemy 31s buforu)
    MIN_SECONDS_BETWEEN_CALLS = 31

    try:
        # Spróbuj odczytać czas ostatniego zapytania
        with open(GEMINI_TIMESTAMP_FILE, 'r') as f:
            last_call_time_str = f.read()
        last_call_time = datetime.fromisoformat(last_call_time_str)

        # Oblicz, ile czasu minęło
        elapsed = datetime.now() - last_call_time
        elapsed_seconds = elapsed.total_seconds()

        if elapsed_seconds < MIN_SECONDS_BETWEEN_CALLS:
            # Jeśli minęło za mało czasu, oblicz ile trzeba poczekać
            wait_time = MIN_SECONDS_BETWEEN_CALLS - elapsed_seconds
            print_colored(f"    [SYSTEM] Limit Gemini. Czekam {wait_time:.1f} sekund...", "\033[90m")
            time.sleep(wait_time)

    except FileNotFoundError:
        # Plik nie istnieje, to pierwsze zapytanie. Nic nie robimy.
        pass

    # Po odczekaniu (lub nie), zapisz aktualny czas jako czas ostatniego zapytania
    with open(GEMINI_TIMESTAMP_FILE, 'w') as f:
        f.write(datetime.now().isoformat())

# Walidacja Trading212 API Key (opcjonalne)
if TRADING212_API_KEY:
    print_colored("✓ Wykryto klucz Trading212 API - włączono integrację.", "\033[92m")
    TRADING212_ENABLED = True
else:
    print_colored("⚠️  Brak klucza Trading212 API - używam Google Sheets jako źródło danych.", "\033[93m")
    TRADING212_ENABLED = False

NAZWA_PLIKU_KREDENCJALI = "credentials.json"
NAZWA_PLIKU_KONFIGURACJI_PERSON = "finalna_konfiguracja_person.txt"
NAZWA_PLIKU_KODEKSU = "kodeks_spolki.txt"
NAZWA_PLIKU_CELOW = "cele.json"
NAZWA_PLIKU_COMPLIANCE = "compliance_log.json"
NAZWA_PLIKU_MONTHLY_SNAPSHOT = "monthly_snapshot.json"
NAZWA_PLIKU_T212_CACHE = "trading212_cache.json"  # NOWY: Cache dla Trading212

NAZWY_ARKUSZY = {
    "akcje": "Horyzont Akcje",  # Używane jako FALLBACK gdy Trading212 API nie działa
    # "krypto": "Horyzont Krypto",  # ✅ ZMIGROWANE → krypto.json
    # "dlugi": "Horyzont Długi",    # ✅ ZMIGROWANE → kredyty.json
    # "wyplata": "Horyzont Wypłata" # ✅ ZMIGROWANE → wyplaty.json + wydatki.json
}
NAZWA_KRONIKI = "kronika_spotkan.txt"
FOLDER_SESJI = "sesje"
FOLDER_RAPORTOW = "raporty_miesieczne"

MAX_RETRIES = 3
RETRY_DELAY = 2
SZANSA_SPONTANICZNEGO_KOMENTARZA = 0.25
MAX_SPONTANICZNYCH_REAKCJI = 1
NBP_API_URL = "https://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json"
TRADING212_BASE_URL = "https://live.trading212.com/api/v0"  # NOWY: Trading212 API endpoint
TRADING212_CACHE_HOURS = 24  # Cache na 24 godziny

# === GLOBALNE ZMIENNE ===
historia_wypowiedzi = []
licznik_wypowiedzi = Counter()
aktywne_glosowanie = None
ostatnie_sprawdzenie_compliance = None
tryb_odpowiedzi = "zwiezly"  # zwiezly / normalny / szczegolowy
fight_club_enabled = True  # NOWY: Financial Fight Club włączony
conflict_memory = {}  # NOWY: Pamięć konfliktów między Partnerami

# === CELE DOMYŚLNE (jeśli nie ma pliku) ===
CELE_DOMYSLNE = {
    "Rezerwa_gotowkowa_PLN": 70000,
    "Dlugi_do_splaty_70_procent_PLN": 12082,
    "PBR_akcje_liczba": 100,
    "GAIN_akcje_limit": 200,
    "ADD_wartosc_docelowa_PLN": 50000,
    "wiek_uzytkownika": None,  # NOWY: Wiek użytkownika
    "miesieczne_wydatki_fi": None  # NOWY: Opcjonalne nadpisanie wydatków (domyślnie z arkusza)
}

def clear_screen():
    """Czyści ekran konsoli."""
    os.system('cls' if os.name == 'nt' else 'clear')

def wczytaj_cele():
    """Wczytuje cele z pliku lub tworzy domyślny."""
    if not os.path.exists(NAZWA_PLIKU_CELOW):
        print_colored(f"⚠️  Nie znaleziono pliku '{NAZWA_PLIKU_CELOW}'. Tworzę domyślny...", "\033[93m")
        with open(NAZWA_PLIKU_CELOW, 'w', encoding='utf-8') as f:
            json.dump(CELE_DOMYSLNE, f, indent=2, ensure_ascii=False)
        print_colored(f"✓ Utworzono plik '{NAZWA_PLIKU_CELOW}' z domyślnymi celami.", "\033[92m")
        print_colored("   Możesz edytować ten plik aby dostosować cele do swoich potrzeb.", "\033[93m")
        return CELE_DOMYSLNE
    
    try:
        with open(NAZWA_PLIKU_CELOW, 'r', encoding='utf-8') as f:
            cele = json.load(f)
        print_colored(f"✓ Wczytano cele z pliku '{NAZWA_PLIKU_CELOW}'.", "\033[92m")
        return cele
    except Exception as e:
        print_colored(f"⚠️  Błąd wczytywania celów: {e}. Używam domyślnych.", "\033[93m")
        return CELE_DOMYSLNE

def wczytaj_kodeks():
    """Wczytuje Kodeks Spółki z pliku."""
    if not os.path.exists(NAZWA_PLIKU_KODEKSU):
        print_colored(f"⚠️  Ostrzeżenie: Nie znaleziono pliku '{NAZWA_PLIKU_KODEKSU}'.", "\033[93m")
        print_colored("   Partnerzy nie będą mieli dostępu do Kodeksu Spółki.", "\033[93m")
        return ""
    
    try:
        with open(NAZWA_PLIKU_KODEKSU, 'r', encoding='utf-8') as f:
            kodeks = f.read()
        print_colored(f"✓ Wczytano Kodeks Spółki z pliku '{NAZWA_PLIKU_KODEKSU}'.", "\033[92m")
        return kodeks
    except Exception as e:
        print_colored(f"⚠️  Błąd wczytywania Kodeksu: {e}", "\033[93m")
        return ""

def wczytaj_compliance_log():
    """Wczytuje log compliance z pliku."""
    if not os.path.exists(NAZWA_PLIKU_COMPLIANCE):
        return {"ostatnia_aktualizacja": None, "wpisy": []}
    
    try:
        with open(NAZWA_PLIKU_COMPLIANCE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print_colored(f"⚠️  Błąd wczytywania compliance log: {e}", "\033[93m")
        return {"ostatnia_aktualizacja": None, "wpisy": []}

def zapisz_compliance_log(log):
    """Zapisuje log compliance do pliku."""
    try:
        with open(NAZWA_PLIKU_COMPLIANCE, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print_colored(f"⚠️  Błąd zapisu compliance log: {e}", "\033[93m")

def wczytaj_monthly_snapshot():
    """Wczytuje ostatni snapshot miesięczny."""
    if not os.path.exists(NAZWA_PLIKU_MONTHLY_SNAPSHOT):
        return None
    
    try:
        with open(NAZWA_PLIKU_MONTHLY_SNAPSHOT, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print_colored(f"⚠️  Błąd wczytywania monthly snapshot: {e}", "\033[93m")
        return None

def zapisz_monthly_snapshot(stan_spolki):
    """Zapisuje snapshot stanu spółki na koniec miesiąca."""
    try:
        snapshot = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "miesiac": datetime.now().strftime("%Y-%m"),
            "stan": stan_spolki
        }
        with open(NAZWA_PLIKU_MONTHLY_SNAPSHOT, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        print_colored(f"✓ Zapisano snapshot miesięczny.", "\033[92m")
    except Exception as e:
        print_colored(f"⚠️  Błąd zapisu monthly snapshot: {e}", "\033[93m")

def sprawdz_nowy_miesiac():
    """Sprawdza czy to nowy miesiąc i czy trzeba wygenerować raport."""
    snapshot = wczytaj_monthly_snapshot()
    obecny_miesiac = datetime.now().strftime("%Y-%m")
    
    if snapshot is None:
        # Pierwszy raz - zapisz obecny stan jako baseline
        print_colored("📅 Pierwszy uruchomienie - zapisuję baseline dla przyszłych raportów...", "\033[96m")
        return False, None
    
    ostatni_miesiac = snapshot.get("miesiac")
    
    if ostatni_miesiac != obecny_miesiac:
        print_colored(f"📅 Wykryto nowy miesiąc! ({ostatni_miesiac} → {obecny_miesiac})", "\033[96m")
        return True, snapshot
    
    return False, None

def generuj_raport_miesieczny(stan_obecny, snapshot_poprzedni, cele):
    """Generuje miesięczny raport porównawczy."""
    if not os.path.exists(FOLDER_RAPORTOW):
        os.makedirs(FOLDER_RAPORTOW)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    miesiac_nazwa = datetime.now().strftime("%B_%Y")
    filename = f"raport_{miesiac_nazwa}_{timestamp}.txt"
    filepath = os.path.join(FOLDER_RAPORTOW, filename)
    
    raport_lines = []
    raport_lines.append("="*80)
    raport_lines.append("MIESIĘCZNE POSIEDZENIE ZARZĄDU - RAPORT AUTOMATYCZNY")
    raport_lines.append(f"Spółka: HORYZONT PARTNERÓW")
    raport_lines.append(f"Data wygenerowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    raport_lines.append("="*80)
    raport_lines.append("")
    
    # SEKCJA 1: Porównanie z poprzednim miesiącem
    if snapshot_poprzedni:
        raport_lines.append("📊 PORÓWNANIE Z POPRZEDNIM MIESIĄCEM")
        raport_lines.append("-" * 80)
        
        stan_poprzedni = snapshot_poprzedni.get("stan", {})
        
        # Wartość portfela
        if "PODSUMOWANIE" in stan_obecny and "PODSUMOWANIE" in stan_poprzedni:
            wartosc_teraz = stan_obecny["PODSUMOWANIE"]["Wartosc_netto_PLN"]
            wartosc_wtedy = stan_poprzedni["PODSUMOWANIE"]["Wartosc_netto_PLN"]
            zmiana = wartosc_teraz - wartosc_wtedy
            zmiana_proc = (zmiana / wartosc_wtedy * 100) if wartosc_wtedy > 0 else 0
            
            raport_lines.append(f"\n💰 Wartość netto portfela:")
            raport_lines.append(f"  Poprzedni miesiąc: {wartosc_wtedy:,.2f} PLN")
            raport_lines.append(f"  Obecny stan:       {wartosc_teraz:,.2f} PLN")
            raport_lines.append(f"  Zmiana:            {zmiana:+,.2f} PLN ({zmiana_proc:+.2f}%)")
        
        # Długi
        if "ZOBOWIAZANIA" in stan_obecny and "ZOBOWIAZANIA" in stan_poprzedni:
            dlugi_teraz = stan_obecny["ZOBOWIAZANIA"]["Suma_dlugow_PLN"]
            dlugi_wtedy = stan_poprzedni["ZOBOWIAZANIA"]["Suma_dlugow_PLN"]
            zmiana_dlugi = dlugi_teraz - dlugi_wtedy
            
            raport_lines.append(f"\n💳 Zobowiązania:")
            raport_lines.append(f"  Poprzedni miesiąc: {dlugi_wtedy:,.2f} PLN")
            raport_lines.append(f"  Obecny stan:       {dlugi_teraz:,.2f} PLN")
            raport_lines.append(f"  Zmiana:            {zmiana_dlugi:+,.2f} PLN")
            
            if zmiana_dlugi < 0:
                raport_lines.append(f"  ✅ Spłacono: {abs(zmiana_dlugi):,.2f} PLN")
    
    raport_lines.append("")
    raport_lines.append("")
    
    # SEKCJA 2: Zgodność z Kodeksem (Compliance)
    raport_lines.append("✅ COMPLIANCE - PRZESTRZEGANIE KODEKSU SPÓŁKI")
    raport_lines.append("-" * 80)
    
    compliance_log = wczytaj_compliance_log()
    
    raport_lines.append("\n📋 Status protokołów z Artykułu IV:")
    raport_lines.append("")
    
    # Sprawdź ostatnie wpisy compliance
    ostatnie_wpisy = compliance_log.get("wpisy", [])[-5:] if compliance_log.get("wpisy") else []
    
    if ostatnie_wpisy:
        for wpis in ostatnie_wpisy:
            status_emoji = "🟢" if wpis.get("status") == "zgodne" else "🔴" if wpis.get("status") == "niezgodne" else "🟡"
            raport_lines.append(f"  {status_emoji} {wpis.get('protokol', 'N/A')}: {wpis.get('opis', 'N/A')}")
    else:
        raport_lines.append("  ⚠️  Brak danych compliance. Uruchom tracking protokołów.")
    
    raport_lines.append("")
    raport_lines.append("")
    
    # SEKCJA 3: Progres w realizacji celów
    raport_lines.append("🎯 PROGRES W REALIZACJI CELÓW STRATEGICZNYCH")
    raport_lines.append("-" * 80)
    raport_lines.append("")
    
    # Cel 1: Rezerwa gotówkowa
    if "PRZYCHODY_I_WYDATKI" in stan_obecny:
        # Zakładamy że "Płynny kapitał" będzie w przyszłości, na razie symulujemy
        rezerwa_cel = cele.get("Rezerwa_gotowkowa_PLN", 70000)
        rezerwa_obecna = 0  # TODO: Dodać tracking gotówki
        procent = (rezerwa_obecna / rezerwa_cel * 100) if rezerwa_cel > 0 else 0
        
        raport_lines.append(f"💰 Rezerwa gotówkowa:")
        raport_lines.append(f"  Cel:        {rezerwa_cel:,.2f} PLN")
        raport_lines.append(f"  Obecny:     {rezerwa_obecna:,.2f} PLN")
        raport_lines.append(f"  Progres:    {procent:.1f}%")
        raport_lines.append(f"  Bar:        [{'█' * int(procent/10)}{'░' * (10-int(procent/10))}]")
    
    # Cel 2: Spłata długów do 70%
    if "ZOBOWIAZANIA" in stan_obecny:
        dlugi_obecne = stan_obecny["ZOBOWIAZANIA"]["Suma_dlugow_PLN"]
        dlugi_70proc = cele.get("Dlugi_do_splaty_70_procent_PLN", 12082)
        procent_splaty = ((dlugi_70proc - dlugi_obecne) / dlugi_70proc * 100) if dlugi_70proc > 0 else 0
        procent_splaty = max(0, min(100, procent_splaty))
        
        raport_lines.append(f"\n💳 Spłata 70% długów (Artykuł IV §1 - Protokół Bezpieczeństwa):")
        raport_lines.append(f"  Cel:        {dlugi_70proc:,.2f} PLN (70% spłacone)")
        raport_lines.append(f"  Obecny:     {dlugi_obecne:,.2f} PLN")
        raport_lines.append(f"  Progres:    {procent_splaty:.1f}%")
        raport_lines.append(f"  Bar:        [{'█' * int(procent_splaty/10)}{'░' * (10-int(procent_splaty/10))}]")
    
    raport_lines.append("")
    raport_lines.append("")
    
    # SEKCJA 4: Rekomendacje Partnerów (zostawiamy placeholder)
    raport_lines.append("💡 REKOMENDACJE PARTNERÓW NA KOLEJNY MIESIĄC")
    raport_lines.append("-" * 80)
    raport_lines.append("")
    raport_lines.append("  [Rekomendacje będą generowane przez AI w przyszłej wersji]")
    raport_lines.append("")
    
    raport_lines.append("="*80)
    raport_lines.append("KONIEC RAPORTU")
    raport_lines.append("="*80)
    
    # Zapisz raport
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(raport_lines))
        
        print_colored(f"\n📊 WYGENEROWANO MIESIĘCZNY RAPORT ZARZĄDU", "\033[96m")
        print_colored(f"   Zapisano w: {filepath}", "\033[93m")
        
        # Wyświetl raport
        print_colored("\n" + "="*80, "\033[96m")
        for line in raport_lines:
            print(line)
        print_colored("="*80 + "\n", "\033[96m")
        
        return True
    except Exception as e:
        print_colored(f"❌ Błąd zapisu raportu: {e}", "\033[91m")
        return False

def tracking_protokolow():
    """Interaktywne śledzenie przestrzegania protokołów."""
    print_colored("\n📋 TRACKING PROTOKOŁÓW Z KODEKSU SPÓŁKI", "\033[96m")
    print_colored("="*80, "\033[96m")
    
    compliance_log = wczytaj_compliance_log()
    
    # Protokoły do sprawdzenia
    protokoly = [
        {
            "id": "ADD_325",
            "nazwa": "Artykuł IV §2 - Zasilenie ADD",
            "pytanie": "Czy w tym miesiącu wpłaciłeś 325 PLN na 'Twierdzę' (ADD Pie)?",
            "kwota": 325
        },
        {
            "id": "PBR_50_tydz",
            "nazwa": "Artykuł IV §2 - Zasilenie PBR",
            "pytanie": "Czy regularnie wpłacasz 50 PLN tygodniowo na 'Silnik Surowcowy' (PBR)?",
            "kwota": 50
        },
        {
            "id": "BCAT_VWCE_50_tydz",
            "nazwa": "Artykuł IV §2 - Zasilenie Filaru Taktycznego",
            "pytanie": "Czy regularnie wpłacasz 50 PLN tygodniowo na Filar Taktyczny (BCAT + VWCE)?",
            "kwota": 50
        }
    ]
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for protokol in protokoly:
        print_colored(f"\n{protokol['nazwa']}", "\033[93m")
        print(f"  {protokol['pytanie']}")
        
        odpowiedz = input("  Odpowiedź (tak/nie): ").strip().lower()
        
        if odpowiedz in ['tak', 't', 'yes', 'y']:
            status = "zgodne"
            print_colored("  ✅ Zaznaczono jako zgodne", "\033[92m")
            uwagi = ""
        else:
            status = "niezgodne"
            print_colored("  ❌ Zaznaczono jako niezgodne", "\033[91m")
            uwagi = input("  Opcjonalne uwagi/powód: ").strip()
        
        # Dodaj wpis do logu
        wpis = {
            "data": timestamp,
            "protokol": protokol['nazwa'],
            "id": protokol['id'],
            "status": status,
            "opis": f"Kwota: {protokol['kwota']} PLN" + (f" | Uwagi: {uwagi}" if uwagi else "")
        }
        
        compliance_log["wpisy"].append(wpis)
    
    compliance_log["ostatnia_aktualizacja"] = timestamp
    zapisz_compliance_log(compliance_log)
    
    print_colored("\n✅ Tracking protokołów zakończony i zapisany.", "\033[92m")

def sprawdz_compliance_auto(dane_t212=None):
    """
    Automatyczne sprawdzenie zgodności z Kodeksem.
    Uruchamiane raz dziennie przy pierwszym uruchomieniu.
    """
    global ostatnie_sprawdzenie_compliance
    
    # Sprawdź czy już dzisiaj sprawdzaliśmy
    dzisiaj = datetime.now().strftime("%Y-%m-%d")
    
    if ostatnie_sprawdzenie_compliance == dzisiaj:
        return None  # Już sprawdzane dzisiaj
    
    print_colored("\n🔍 AUTOMATYCZNE SPRAWDZENIE ZGODNOŚCI Z KODEKSEM...", "\033[96m")
    print_colored("="*80, "\033[96m")
    
    compliance_wyniki = {
        "data_sprawdzenia": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "protokoly": [],
        "score": 0,
        "max_score": 0
    }
    
    # Protokół 1: ADD 325 PLN/mies
    if dane_t212 and "transactions" in dane_t212:
        # TODO: Sprawdź transakcje z bieżącego miesiąca
        # Na razie placeholder
        compliance_wyniki["protokoly"].append({
            "nazwa": "ADD 325 PLN/mies",
            "status": "nieznany",
            "komunikat": "⚠️  Brak danych o transakcjach w API (wymaga rozszerzenia)"
        })
        compliance_wyniki["max_score"] += 1
    else:
        compliance_wyniki["protokoly"].append({
            "nazwa": "ADD 325 PLN/mies",
            "status": "nieznany",
            "komunikat": "⚠️  Sprawdź ręcznie komendą 'tracking'"
        })
        compliance_wyniki["max_score"] += 1
    
    # Protokół 2: PBR 50 PLN/tydz
    compliance_wyniki["protokoly"].append({
        "nazwa": "PBR 50 PLN/tydz",
        "status": "nieznany",
        "komunikat": "⚠️  Sprawdź ręcznie komendą 'tracking'"
    })
    compliance_wyniki["max_score"] += 1
    
    # Protokół 3: BCAT+VWCE 50 PLN/tydz
    compliance_wyniki["protokoly"].append({
        "nazwa": "BCAT+VWCE 50 PLN/tydz",
        "status": "nieznany",
        "komunikat": "⚠️  Sprawdź ręcznie komendą 'tracking'"
    })
    compliance_wyniki["max_score"] += 1
    
    # Wyświetl wyniki
    print_colored("\n📊 WYNIKI SPRAWDZENIA:", "\033[93m")
    for protokol in compliance_wyniki["protokoly"]:
        status_emoji = "✅" if protokol["status"] == "zgodne" else "❌" if protokol["status"] == "niezgodne" else "⚠️"
        print(f"  {status_emoji} {protokol['nazwa']}")
        print(f"     {protokol['komunikat']}")
    
    if compliance_wyniki["score"] == 0:
        print_colored("\n💡 TIP: Użyj komendy 'tracking' aby ręcznie potwierdzić przestrzeganie protokołów.", "\033[93m")
    
    print_colored("="*80 + "\n", "\033[96m")
    
    ostatnie_sprawdzenie_compliance = dzisiaj
    return compliance_wyniki

def ai_advisor(pytanie, stan_spolki, cele, z_partnerami=False):
    """
    AI Advisor - inteligentny doradca finansowy.
    Analizuje pytanie i generuje 3 scenariusze z rekomendacjami.
    """
    print_colored("\n🤖 AI ADVISOR - ANALIZA I REKOMENDACJE", "\033[96m")
    print_colored("="*80, "\033[96m")
    print_colored(f"\n📋 Twoje pytanie: {pytanie}\n", "\033[93m")
    print_colored("⏳ Analizuję sytuację i przygotowuję scenariusze...\n", "\033[90m")
    
    # Przygotuj kontekst dla AI
    stan_json = json.dumps(stan_spolki, indent=2, ensure_ascii=False)
    cele_json = json.dumps(cele, indent=2, ensure_ascii=False)
    
    advisor_prompt = f"""
Jesteś ekspertem finansowym i doradcą inwestycyjnym dla osoby prywatnej.

KODEKS SPÓŁKI (MUSISZ GO PRZESTRZEGAĆ):
{KODEKS_SPOLKI}

AKTUALNY STAN FINANSOWY:
{stan_json}

CELE FINANSOWE:
{cele_json}

PYTANIE KLIENTA:
"{pytanie}"

TWOJE ZADANIE:
Przeanalizuj sytuację i przedstaw 3 różne scenariusze działania:

SCENARIUSZ A: Zgodny z Kodeksem (konserwatywny)
SCENARIUSZ B: Zbalansowany (optymalizacja ryzyka/zysku)
SCENARIUSZ C: Agresywny (maksymalizacja wyniku)

Dla każdego scenariusza podaj:
1. Konkretne kroki działania (co zrobić z pieniędzmi)
2. Oczekiwany efekt krótkoterminowy (1-3 miesiące)
3. Oczekiwany efekt długoterminowy (12+ miesięcy)
4. Ryzyka i wady
5. Czy zgodne z Kodeksem (jeśli nie - które artykuły narusza)

Na końcu dodaj REKOMENDACJĘ: Który scenariusz polecasz i dlaczego.

FORMAT ODPOWIEDZI:
═══════════════════════════════════════════════════════════════
📊 SCENARIUSZ A: [Nazwa]
[Opis zgodny z Kodeksem]

Kroki:
• [krok 1]
• [krok 2]

Efekt krótkoterminowy: [opis]
Efekt długoterminowy: [opis]
Ryzyko: [opis]
Zgodność z Kodeksem: ✅ Zgodny / ❌ Narusza Art. X

───────────────────────────────────────────────────────────────
📊 SCENARIUSZ B: [Nazwa]
[analogicznie]

───────────────────────────────────────────────────────────────
📊 SCENARIUSZ C: [Nazwa]
[analogicznie]

═══════════════════════════════════════════════════════════════
💡 REKOMENDACJA:
[Który scenariusz polecasz i szczegółowe uzasadnienie]

═══════════════════════════════════════════════════════════════

WAŻNE:
- Używaj konkretnych liczb z danych
- Bądź praktyczny i realistyczny
- Odwołuj się do konkretnych Artykułów Kodeksu
- Pisz zwięźle ale kompletnie
"""
    
    try:
        response = generuj_odpowiedz_ai("Ja (Partner Strategiczny)", advisor_prompt)
        
        print_colored(response, "\033[97m")
        
        # Zapisz do kroniki
        save_to_chronicle("AI Advisor", f"Pytanie: {pytanie}\n\n{response}")
        
        # Opcjonalnie: zapytaj Partnerów o komentarze
        if z_partnerami:
            print_colored("\n" + "="*80, "\033[95m")
            print_colored("💬 KOMENTARZE PARTNERÓW", "\033[95m")
            print_colored("="*80, "\033[95m")
            
            for persona_name in ["Partner Strategiczny", "Partner ds. Jakości Biznesowej", "Partner ds. Aktywów Cyfrowych"]:
                if persona_name not in PERSONAS:
                    continue
                
                time.sleep(0.5)
                
                # Wstrzyknij pamięć persony (jeśli system włączony)
                memory_context = ""
                emotional_hint = ""
                if PERSONA_MEMORY_ENABLED:
                    if PERSONA_MEMORY_V2:
                        # v2.0: Rozbudowany kontekst z emocjami, relacjami, etc
                        memory_context = build_enhanced_context(persona_name, limit=5)
                        emotional_hint = get_emotional_modifier(persona_name)
                    else:
                        # v1.0: Podstawowy kontekst
                        memory_context = pmm.get_persona_context(persona_name)
                    
                    pmm.increment_session(persona_name)
                
                partner_prompt = f"""
{PERSONAS[persona_name]['system_instruction']}

{memory_context}

{emotional_hint}

KODEKS SPÓŁKI:
{KODEKS_SPOLKI}

Twoim tajnym celem jest: {PERSONAS[persona_name]['ukryty_cel']}

AI Advisor przedstawił 3 scenariusze dotyczące pytania:
"{pytanie}"

Rekomendacja AI Advisor:
{response[-500:]}  

TWOJE ZADANIE:
Skomentuj rekomendację w 2-3 zdaniach:
- Czy się zgadzasz?
- Co byś zmienił/dodał?
- Czy widzisz jakieś ryzyko które pominięto?

Bądź zwięzły ale konkretny.
"""
                
                partner_response = generuj_odpowiedz_ai(persona_name, partner_prompt)
                
                print_colored(f"\n💼 [{persona_name}]:", PERSONAS[persona_name]['color_code'])
                print_colored(partner_response, PERSONAS[persona_name]['color_code'])
                
                save_to_chronicle(persona_name, f"[Komentarz do AI Advisor] {partner_response}")
        
        print_colored("\n" + "="*80, "\033[96m")
        print_colored("✅ Analiza zakończona. Która opcja Cię interesuje?", "\033[92m")
        print_colored("="*80 + "\n", "\033[96m")
        
    except Exception as e:
        print_colored(f"\n❌ Błąd AI Advisor: {e}", "\033[91m")
        import traceback
        traceback.print_exc()

def oblicz_fire_metrics(stan_spolki, cele):
    """
    Oblicza metryki Financial Independence / Retire Early.
    Model: Dividend-based (żyjesz z samych dywidend).
    """
    # Pobierz wydatki miesięczne
    wydatki_miesieczne = cele.get("miesieczne_wydatki_fi")
    if not wydatki_miesieczne and "PRZYCHODY_I_WYDATKI" in stan_spolki:
        wydatki_miesieczne = stan_spolki["PRZYCHODY_I_WYDATKI"]["Suma_wydatkow_PLN"]
    
    if not wydatki_miesieczne or wydatki_miesieczne == 0:
        return None
    
    # Parametry
    wiek = cele.get("wiek_uzytkownika")
    inflacja_roczna = 0.03  # 3% inflacja
    srednia_dywidenda = 0.04  # 4% średnia dywidenda rocznie (konserwatywne)
    wzrost_portfela = 0.08  # 8% średni wzrost rocznie
    
    # Obecny portfel i dochód pasywny
    if "PODSUMOWANIE" not in stan_spolki:
        return None
    
    portfel_obecny = stan_spolki["PODSUMOWANIE"]["Wartosc_netto_PLN"]
    dochod_pasywny_obecny = portfel_obecny * srednia_dywidenda / 12  # miesięcznie
    
    # Potrzebny kapitał dla FI (dividend-based)
    # Wydatki rosną z inflacją, więc potrzebujemy więcej
    wydatki_roczne = wydatki_miesieczne * 12
    potrzebny_kapital = wydatki_roczne / srednia_dywidenda
    
    # Miesięczne wpłaty (z PRZYCHODY_I_WYDATKI)
    miesieczne_wplaty = 0
    if "PRZYCHODY_I_WYDATKI" in stan_spolki:
        miesieczne_wplaty = stan_spolki["PRZYCHODY_I_WYDATKI"]["Dostepne_na_inwestycje_PLN"]
    
    # Oblicz czas do FI (uwzględniając wzrost portfela + wpłaty)
    if miesieczne_wplaty <= 0:
        miesiace_do_fi = None  # Nie da się osiągnąć bez wpłat
    else:
        # Złożona formuła uwzględniająca:
        # - Wzrost obecnego portfela
        # - Regularne wpłaty
        # - Cel rosnący z inflacją
        
        miesiace_do_fi = 0
        kapital_symulacja = portfel_obecny
        cel_symulacja = potrzebny_kapital
        
        while kapital_symulacja < cel_symulacja and miesiace_do_fi < 600:  # Max 50 lat
            miesiace_do_fi += 1
            # Wzrost kapitału
            kapital_symulacja *= (1 + wzrost_portfela / 12)
            # Wpłata miesięczna
            kapital_symulacja += miesieczne_wplaty
            # Cel rośnie z inflacją
            if miesiace_do_fi % 12 == 0:
                cel_symulacja *= (1 + inflacja_roczna)
        
        if miesiace_do_fi >= 600:
            miesiace_do_fi = None
    
    lata_do_fi = miesiace_do_fi / 12 if miesiace_do_fi else None
    rok_fi = datetime.now().year + int(lata_do_fi) if lata_do_fi else None
    
    # Milestones
    coast_fi = potrzebny_kapital * 0.25  # 25% celu - już nie musisz wpłacać, czas zrobi robotę
    barista_fi = potrzebny_kapital * 0.50  # 50% celu - możesz pracować part-time
    
    # Procent do celu
    procent_fi = (portfel_obecny / potrzebny_kapital * 100) if potrzebny_kapital > 0 else 0
    
    return {
        "wydatki_miesieczne": round(wydatki_miesieczne, 2),
        "wydatki_roczne": round(wydatki_roczne, 2),
        "potrzebny_kapital_fi": round(potrzebny_kapital, 2),
        "portfel_obecny": round(portfel_obecny, 2),
        "dochod_pasywny_miesiac": round(dochod_pasywny_obecny, 2),
        "procent_do_fi": round(procent_fi, 2),
        "miesiace_do_fi": miesiace_do_fi,
        "lata_do_fi": round(lata_do_fi, 1) if lata_do_fi else None,
        "rok_fi": rok_fi,
        "wiek_fi": wiek + int(lata_do_fi) if wiek and lata_do_fi else None,
        "coast_fi": round(coast_fi, 2),
        "barista_fi": round(barista_fi, 2),
        "miesieczne_wplaty": round(miesieczne_wplaty, 2)
    }

def wyswietl_analize_dywidend(portfel_akcji):
    """Wyświetla szczegółową analizę dywidend dla całego portfela."""
    print_colored("\n📊 ANALIZA DYWIDEND:", "\033[96m")
    
    # Zbierz wszystkie spółki z danymi o dywidendach
    spolki_z_dywidenda = []
    suma_rocznych_dywidend = 0
    
    for ticker, dane in portfel_akcji.get("Pozycje_szczegoly", {}).items():
        ticker_base = ticker.split('_')[0]  # Usuń suffiks z tickera
        ticker_dane = portfel_akcji.get("Dane_rynkowe", {}).get(ticker, {})
        if ticker_dane:
            ilosc = dane.get("ilosc", 0)
            
            try:
                stock = yf.Ticker(ticker_base)
                div_data = analizuj_dywidendy(ticker_base, ticker_dane)
                
                if div_data:
                    # Walidacja ilości akcji
                    if not isinstance(ilosc, (int, float)) or ilosc <= 0:
                        print(f"⚠️ {ticker}: Nieprawidłowa ilość akcji: {ilosc}")
                        continue
                    
                    # Sprawdzamy czy to nie jest pozycja specjalna (np. ETF)
                    czy_etf = "_ETF" in ticker or "_EQ" in ticker
                    
                    # Obliczanie rocznej dywidendy
                    annual_per_share = div_data["annual_div"]
                    
                    # Zaokrąglamy ilość akcji dla zwykłych akcji (nie ETF)
                    used_shares = ilosc if czy_etf else round(ilosc, 2)
                    roczna_dywidenda = annual_per_share * used_shares
                    
                    # Debugowanie szczegółów
                    share_type = "ETF/EQ" if czy_etf else "akcji"
                    print(f"📈 {ticker}: ${annual_per_share:.4f}/akcję × {used_shares:.2f} {share_type} = ${roczna_dywidenda:.2f}/rok")
                    
                    spolki_z_dywidenda.append({
                        "ticker": ticker,
                        "nazwa": ticker_dane.get("nazwa", ticker),
                        "ilosc": ilosc,
                        "yield": div_data["div_yield"],
                        "roczna_dywidenda": roczna_dywidenda,
                        "wzrost_dywidend": div_data["div_growth_cagr"],
                        "nastepna_data": div_data["next_div_date"],
                        "nastepna_kwota": div_data["next_div_amount"],
                        "czestotliwosc": div_data["div_frequency"],
                        "ostatnia_dywidenda": div_data["last_div_amount"]
                    })
                    suma_rocznych_dywidend += roczna_dywidenda
            except Exception as e:
                print(f"Błąd analizy {ticker}: {str(e)}")

    # Sortuj po najbliższej wypłacie dywidendy
    spolki_z_dywidenda.sort(key=lambda x: (x["nastepna_data"] is None, x["nastepna_data"] if x["nastepna_data"] else "9999-99-99"))

    # Wyświetl podsumowanie
    print(f"  📈 Łączna roczna dywidenda:     ${suma_rocznych_dywidend:,.2f}")
    print(f"  🎯 Liczba spółek dywidendowych:  {len(spolki_z_dywidenda)}")
    
    if spolki_z_dywidenda:
        print("\n  NADCHODZĄCE WYPŁATY DYWIDEND:")
        nadchodzace = [s for s in spolki_z_dywidenda if s["nastepna_data"]]
        nadchodzace.sort(key=lambda x: x["nastepna_data"])
        
        for spolka in nadchodzace[:5]:  # Pokaż top 5 najbliższych wypłat
            wartosc = spolka["nastepna_kwota"] * spolka["ilosc"] if spolka["nastepna_kwota"] else spolka["ostatnia_dywidenda"] * spolka["ilosc"]
            print(f"  • {spolka['ticker']:<8} | {spolka['nastepna_data']} | ${wartosc:,.2f}")
        
        print("\n  TOP 5 SPÓŁEK POD WZGLĘDEM ROCZNEJ DYWIDENDY:")
        for spolka in sorted(spolki_z_dywidenda, key=lambda x: x["roczna_dywidenda"], reverse=True)[:5]:
            print(f"  • {spolka['ticker']:<8} | ${spolka['roczna_dywidenda']:,.2f}/rok | Yield: {spolka['yield']:.1f}% | Wzrost: {spolka['wzrost_dywidend']:+.1f}%")
            
        # Dodaj statystyki
        yields = [s["yield"] for s in spolki_z_dywidenda]
        wzrosty = [s["wzrost_dywidend"] for s in spolki_z_dywidenda]
        
        print("\n  STATYSTYKI PORTFELA DYWIDENDOWEGO:")
        print(f"  • Średni yield:           {sum(yields)/len(yields):.1f}%")
        print(f"  • Średni wzrost dywidend: {sum(wzrosty)/len(wzrosty):+.1f}%")
        print(f"  • Miesięczny przychód:    ${suma_rocznych_dywidend/12:,.2f}")
        
        # Pokaż rozkład częstotliwości wypłat
        czestotliwosci = {}
        for s in spolki_z_dywidenda:
            freq = s["czestotliwosc"]
            czestotliwosci[freq] = czestotliwosci.get(freq, 0) + 1
            
        print("\n  CZĘSTOTLIWOŚĆ WYPŁAT DYWIDEND:")
        for freq, count in sorted(czestotliwosci.items()):
            if freq == 1:
                okres = "rocznie"
            elif freq == 2:
                okres = "półrocznie"
            elif freq in [3, 4]:
                okres = "kwartalnie"
            elif freq == 12:
                okres = "miesięcznie"
            elif freq > 4:
                okres = f"{freq} razy w roku"
            else:
                okres = "nieregularnie"
            print(f"  • {count} spółek wypłaca {okres}")

def wyswietl_fire_calculator(stan_spolki, cele, pelny=False):
    """Wyświetla kalkulator FIRE."""
    fire = oblicz_fire_metrics(stan_spolki, cele)
    
    if not fire:
        print_colored("⚠️  Brak danych do obliczenia FIRE. Ustaw wydatki komendą: ustawwydatki [kwota]", "\033[93m")
        return
    
    if pelny:
        # Pełna wersja z komendą !fire
        print_colored("\n" + "="*80, "\033[96m")
        print_colored("🏖️  KALKULATOR FINANCIAL INDEPENDENCE / RETIRE EARLY", "\033[96m")
        print_colored("="*80, "\033[96m")
        
        print_colored("\n📊 TWOJA SYTUACJA:", "\033[93m")
        print(f"  Obecny portfel (netto):     {fire['portfel_obecny']:>15,.2f} PLN")
        print(f"  Miesięczne wydatki:          {fire['wydatki_miesieczne']:>15,.2f} PLN")
        print(f"  Roczne wydatki:              {fire['wydatki_roczne']:>15,.2f} PLN")
        print(f"  Pasywny dochód (4%):         {fire['dochod_pasywny_miesiac']:>15,.2f} PLN/mies")
        
        print_colored(f"\n🎯 CEL FINANCIAL INDEPENDENCE:", "\033[93m")
        print(f"  Potrzebny kapitał:           {fire['potrzebny_kapital_fi']:>15,.2f} PLN")
        print(f"  Model: Dividend-based (4% dywidendy rocznie)")
        print(f"  = {fire['wydatki_miesieczne']:.2f} PLN/mies z dywidend")
        
        print_colored(f"\n📈 PROGRESS DO CELU:", "\033[93m")
        procent = fire['procent_do_fi']
        bar_length = 40
        filled = int(procent / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  [{bar}] {procent:.1f}%")
        print(f"  Masz: {fire['portfel_obecny']:,.0f} PLN / Cel: {fire['potrzebny_kapital_fi']:,.0f} PLN")
        
        if fire['lata_do_fi']:
            print_colored(f"\n⏰ PROJEKCJA:", "\033[93m")
            print(f"  Czas do FI:                  {fire['lata_do_fi']:.1f} lat ({fire['miesiace_do_fi']} miesięcy)")
            if fire['rok_fi']:
                print(f"  Osiągniesz FI:               {fire['rok_fi']} rok")
            if fire['wiek_fi']:
                print(f"  Twój wiek:                   {fire['wiek_fi']} lat")
            print(f"\n  Założenia:")
            print(f"  • Wzrost portfela: 8% rocznie")
            print(f"  • Miesięczne wpłaty: {fire['miesieczne_wplaty']:,.2f} PLN")
            print(f"  • Inflacja: 3% rocznie")
        else:
            print_colored(f"\n⚠️  Nie można osiągnąć FI przy obecnych wpłatach.", "\033[93m")
            print(f"   Potrzebujesz większych wpłat lub wzrostu dochodów.")
        
        print_colored(f"\n🏁 MILESTONES:", "\033[93m")
        coast_status = "✅" if fire['portfel_obecny'] >= fire['coast_fi'] else "⏳"
        barista_status = "✅" if fire['portfel_obecny'] >= fire['barista_fi'] else "⏳"
        fi_status = "✅" if fire['portfel_obecny'] >= fire['potrzebny_kapital_fi'] else "⏳"
        
        print(f"  {coast_status} CoastFI:  {fire['coast_fi']:>12,.0f} PLN (przestań wpłacać, czas zrobi robotę)")
        print(f"  {barista_status} BaristaFI: {fire['barista_fi']:>12,.0f} PLN (pracuj part-time)")
        print(f"  {fi_status} Full FI:   {fire['potrzebny_kapital_fi']:>12,.0f} PLN (nie musisz pracować)")
        
        print_colored("\n💡 JAK PRZYSPIESZYĆ:", "\033[93m")
        if fire['miesieczne_wplaty'] > 0:
            # Symuluj +500 PLN i +1000 PLN więcej
            for extra in [500, 1000]:
                miesiace_nowe = 0
                kapital = fire['portfel_obecny']
                cel = fire['potrzebny_kapital_fi']
                wplaty_nowe = fire['miesieczne_wplaty'] + extra
                
                while kapital < cel and miesiace_nowe < 600:
                    miesiace_nowe += 1
                    kapital *= 1.0066667  # 8% / 12
                    kapital += wplaty_nowe
                    if miesiace_nowe % 12 == 0:
                        cel *= 1.03
                
                lata_nowe = miesiace_nowe / 12
                przyspieszenie = fire['lata_do_fi'] - lata_nowe if fire['lata_do_fi'] else 0
                rok_nowy = datetime.now().year + int(lata_nowe)
                
                print(f"  • +{extra} PLN/mies → FI w {rok_nowy} ({przyspieszenie:.1f} lat szybciej!)")
        
        print_colored("\n" + "="*80, "\033[96m")
        
    else:
        # Zwięzła wersja dla `status`
        print_colored(f"\n🏖️  FINANCIAL INDEPENDENCE:", "\033[96m")
        procent = fire['procent_do_fi']
        bar_length = 30
        filled = int(procent / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  [{bar}] {procent:.1f}%")
        
        if fire['lata_do_fi']:
            print(f"  Do FI: {fire['lata_do_fi']:.1f} lat | Rok: {fire['rok_fi']}", end="")
            if fire['wiek_fi']:
                print(f" | Wiek: {fire['wiek_fi']}")
            else:
                print()
        else:
            print(f"  ⚠️  FI nieosiągalne przy obecnych wpłatach")
        
        print(f"  Dochód pasywny: {fire['dochod_pasywny_miesiac']:,.0f} PLN/mies (cel: {fire['wydatki_miesieczne']:,.0f} PLN)")
        print(f"  Użyj komendy 'fire' dla pełnej analizy")

def wyswietl_progress_bars(stan_spolki, cele):
    """Wyświetla paski postępu dla kluczowych celów."""
    print_colored("\n🎯 PROGRES W REALIZACJI CELÓW STRATEGICZNYCH", "\033[96m")
    print_colored("="*80, "\033[96m")
    
    # Cel 1: Spłata 70% długów
    if "ZOBOWIAZANIA" in stan_spolki:
        dlugi_obecne = stan_spolki["ZOBOWIAZANIA"]["Suma_dlugow_PLN"]
        # Pobieramy kwotę początkową z pliku cele.json, a nie na sztywno!
        dlugi_poczatkowe = cele.get("Dlugi_poczatkowe_PLN", dlugi_obecne) # Jeśli nie ma, użyj obecnej
        dlugi_cel = cele.get("Dlugi_do_splaty_70_procent_PLN", 12082)
        
        # Ile do spłaty, żeby osiągnąć cel
        do_splaty_lacznie = dlugi_poczatkowe - dlugi_cel
        splacone_w_kierunku_celu = dlugi_poczatkowe - dlugi_obecne
        
        procent = 0
        if do_splaty_lacznie > 0:
            procent = (splacone_w_kierunku_celu / do_splaty_lacznie * 100)
        procent = max(0, min(100, procent)) # Ogranicz do 0-100%
        
        bar_filled = int(procent / 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        
        print(f"\n💳 Spłata długów (cel: {dlugi_cel:,.2f} PLN):")
        print(f"   [{bar}] {procent:.1f}%")
        print(f"   Spłacono w kierunku celu: {splacone_w_kierunku_celu:,.2f} PLN / Wymagane: {do_splaty_lacznie:,.2f} PLN")
        print(f"   Pozostało: {dlugi_obecne:,.2f} PLN")

    # Cel 2: Rezerwa gotówkowa (teraz odczytywana z pliku cele.json)
    rezerwa_cel = cele.get("Rezerwa_gotowkowa_PLN", 70000)
    rezerwa_obecna = cele.get("Rezerwa_gotowkowa_obecna_PLN", 0) # Odczytujemy aktualną rezerwę
    procent = (rezerwa_obecna / rezerwa_cel * 100) if rezerwa_cel > 0 else 0
    procent = max(0, min(100, procent))
    
    bar_filled = int(procent / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    
    print(f"\n💰 Rezerwa gotówkowa:")
    print(f"   [{bar}] {procent:.1f}%")
    print(f"   Obecny: {rezerwa_obecna:,.2f} PLN / Cel: {rezerwa_cel:,.2f} PLN")
    
    # Cel 3: PBR - 100 akcji (teraz odczytywane z danych spółki)
    pbr_cel = cele.get("PBR_akcje_liczba", 100)
    pbr_obecne = stan_spolki.get("PORTFEL_AKCJI", {}).get("Ilosc_PBR", 0)
    procent = (pbr_obecne / pbr_cel * 100) if pbr_cel > 0 else 0
    procent = max(0, min(100, procent))
    
    bar_filled = int(procent / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    
    print(f"\n📊 Filar Surowcowy (PBR):")
    print(f"   [{bar}] {procent:.1f}%")
    print(f"   Posiadane: {pbr_obecne} akcji / Cel: {pbr_cel} akcji")
    
    # Cel 4: GAIN - limit 200 akcji (teraz odczytywane z danych spółki)
    gain_limit = cele.get("GAIN_akcje_limit", 200)
    gain_obecne = stan_spolki.get("PORTFEL_AKCJI", {}).get("Ilosc_GAIN", 0)
    procent = (gain_obecne / gain_limit * 100) if gain_limit > 0 else 0
    procent = max(0, min(100, procent))
    
    bar_filled = int(procent / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    
    print(f"\n💵 Filar Dochód (GAIN - limit):")
    print(f"   [{bar}] {procent:.1f}%")
    print(f"   Posiadane: {gain_obecne} akcji / Limit: {gain_limit} akcji")
    
    print_colored("\n" + "="*80, "\033[96m")
def pobierz_kurs_usd_pln():
    """Pobiera aktualny kurs USD/PLN z API NBP."""
    try:
        response = requests.get(NBP_API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        kurs = data['rates'][0]['mid']
        print_colored(f"  ✓ Pobrano aktualny kurs USD/PLN: {kurs:.4f} PLN", "\033[92m")
        return kurs
    except Exception as e:
        print_colored(f"  ⚠️  Nie udało się pobrać kursu z NBP ({e}). Używam kursu awaryjnego 4.00 PLN", "\033[93m")
        return 4.00

# === TRADING212 API FUNCTIONS ===

def wczytaj_t212_cache():
    """Wczytuje cache Trading212."""
    if not os.path.exists(NAZWA_PLIKU_T212_CACHE):
        return None
    
    try:
        with open(NAZWA_PLIKU_T212_CACHE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        # Sprawdź czy cache jest świeży (< 24h)
        cache_time = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
        now = datetime.now()
        age_hours = (now - cache_time).total_seconds() / 3600
        
        if age_hours < TRADING212_CACHE_HOURS:
            print_colored(f"  ✓ Używam cache Trading212 (wiek: {age_hours:.1f}h)", "\033[92m")
            return cache
        else:
            print_colored(f"  ⚠️  Cache Trading212 wygasł ({age_hours:.1f}h) - pobieram świeże dane...", "\033[93m")
            return None
            
    except Exception as e:
        print_colored(f"  ⚠️  Błąd wczytywania cache T212: {e}", "\033[93m")
        return None

def zapisz_t212_cache(data):
    """Zapisuje dane Trading212 do cache."""
    try:
        cache = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(NAZWA_PLIKU_T212_CACHE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print_colored(f"  ⚠️  Błąd zapisu cache T212: {e}", "\033[93m")

def pobierz_dane_trading212():
    """Pobiera dane z Trading212 API (pozycje, saldo, historia)."""
    if not TRADING212_ENABLED or not TRADING212_API_KEY:
        return None
    
    # Sprawdź cache
    cache = wczytaj_t212_cache()
    if cache:
        return cache["data"]
    
    print_colored("  📡 Pobieram dane z Trading212 API...", "\033[96m")
    
    headers = {
        "Authorization": TRADING212_API_KEY
    }
    
    dane_t212 = {}
    
    try:
        # 1. Pobierz pozycje w portfelu
        print("    → Pobieram pozycje...")
        response = requests.get(f"{TRADING212_BASE_URL}/equity/portfolio", headers=headers, timeout=10)
        response.raise_for_status()
        dane_t212["positions"] = response.json()
        print(f"    ✓ Pobrano {len(dane_t212['positions'])} pozycji")
        
        # 2. Pobierz informacje o koncie (saldo gotówkowe)
        print("    → Pobieram info o koncie...")
        response = requests.get(f"{TRADING212_BASE_URL}/equity/account/cash", headers=headers, timeout=10)
        response.raise_for_status()
        dane_t212["account"] = response.json()
        print(f"    ✓ Saldo: {dane_t212['account'].get('free', 0):.2f} {dane_t212['account'].get('currencyCode', 'USD')}")
        
        # 3. Pobierz historię dywidend (ostatnie 6 miesięcy)
        print("    → Pobieram historię dywidend...")
        try:
            response = requests.get(f"{TRADING212_BASE_URL}/history/dividends", headers=headers, timeout=10)
            response.raise_for_status()
            dane_t212["dividends"] = response.json()
            print(f"    ✓ Pobrano {len(dane_t212['dividends'])} dywidend")
        except Exception as e:
            print(f"    ⚠️  Dywidendy niedostępne: {e}")
            dane_t212["dividends"] = []
        
        # 4. Pobierz historię transakcji (opcjonalne - może być dużo danych)
        # print("    → Pobieram historię transakcji...")
        # Pomijamy na razie - może spowolnić
        dane_t212["transactions"] = []
        
        # Zapisz do cache
        zapisz_t212_cache(dane_t212)
        
        print_colored("  ✓ Dane z Trading212 API pobrane pomyślnie!", "\033[92m")
        return dane_t212
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print_colored(f"  ❌ Błąd autoryzacji Trading212: Nieprawidłowy API Key!", "\033[91m")
        elif e.response.status_code == 429:
            print_colored(f"  ⚠️  Przekroczono limit requestów Trading212. Spróbuję użyć Google Sheets...", "\033[93m")
        else:
            print_colored(f"  ❌ Błąd HTTP Trading212: {e.response.status_code}", "\033[91m")
        return None
    except Exception as e:
        print_colored(f"  ❌ Błąd pobierania z Trading212 API: {e}", "\033[91m")
        return None

def parsuj_dane_t212_do_portfela(dane_t212, kurs_usd_pln, cele):
    """
    Parsuje dane z T212, rozdzielając akcje na 'rdzenne' i te należące do 'Pies'.
    Wzbogaca je również o dane z yfinance.
    """
    if not dane_t212:
        return None
    
    try:
        positions = dane_t212.get("positions", [])
        account = dane_t212.get("account", {})
        
        # --- NOWA LOGIKA: Wczytanie definicji "Pies" ---
        pies_config = cele.get("Pies_Inwestycyjne", {})
        # Tworzymy listę wszystkich tickerów, które należą do jakiegokolwiek Pie
        tickery_w_pies = []
        for pie_name, pie_data in pies_config.items():
            if isinstance(pie_data, dict) and 'symbols' in pie_data:
                tickery_w_pies.extend([symbol['symbol'] for symbol in pie_data['symbols']])
        # ---------------------------------------------

        suma_akcji_usd = 0
        ilosc_pbr = 0
        ilosc_gain = 0
        tickery_w_portfelu = []
        
        liczba_pozycji_rdzennych = 0
        liczba_pozycji_w_pie = 0
        
        for pos in positions:
            ticker_oryginalny = pos.get("ticker", "").upper()
            if not ticker_oryginalny:
                continue
            
            tickery_w_portfelu.append(ticker_oryginalny)
            
            # Sprawdzamy, czy ticker należy do portfela rdzennego czy do Pie
            ticker_base = ticker_oryginalny.split('_')[0]  # Bierzemy podstawowy symbol bez sufiksu
            is_in_pie = False
            for pie_name, pie_data in pies_config.items():
                if isinstance(pie_data, dict) and 'symbols' in pie_data:
                    if any(symbol['symbol'] == ticker_base for symbol in pie_data['symbols']):
                        is_in_pie = True
                        break
            
            if is_in_pie:
                liczba_pozycji_w_pie += 1
            else:
                liczba_pozycji_rdzennych += 1

            quantity = pos.get("quantity", 0)
            if 'PBR' in ticker_oryginalny:
                ilosc_pbr += quantity
            elif 'GAIN' in ticker_oryginalny:
                ilosc_gain += quantity

            suma_akcji_usd += pos.get("currentPrice", 0) * quantity

        dane_rynkowe = pobierz_dane_yfinance(tickery_w_portfelu)
        
        suma_akcji_pln = suma_akcji_usd * kurs_usd_pln
        cash_free = account.get("free", 0)
        
        # Zbieramy szczegółowe dane o wszystkich pozycjach
        pozycje_szczegoly = {}
        for pos in positions:
            ticker = pos.get("ticker", "").upper()
            if ticker:
                quantity = pos.get("quantity", 0)
                avg_price = pos.get("averagePrice", 0)
                current_price = pos.get("currentPrice", 0)
                zmiana_proc = ((current_price / avg_price) - 1) * 100 if avg_price > 0 else 0
                wartosc_total = quantity * current_price
                koszt_total = quantity * avg_price
                zysk_total = wartosc_total - koszt_total

                pozycje_szczegoly[ticker] = {
                    "ilosc": quantity,
                    "cena_zakupu_usd": avg_price,
                    "wartosc_obecna_usd": current_price,
                    "zmiana_proc": zmiana_proc,
                    "wartosc_total_usd": wartosc_total,
                    "koszt_total_usd": koszt_total,
                    "zysk_total_usd": zysk_total,
                    "zysk_total_pln": zysk_total * kurs_usd_pln
                }

        # Obliczamy wartość dla każdego pie
        pie_wartosci = {}
        suma_w_pie = 0
        suma_poza_pie = 0
        
        for pos in positions:
            ticker_oryginalny = pos.get("ticker", "").upper()
            if not ticker_oryginalny:
                continue
                
            ticker_base = ticker_oryginalny.split('_')[0]
            quantity = pos.get("quantity", 0)
            current_value = pos.get("currentPrice", 0) * quantity
            
            found_in_pie = False
            for pie_name, pie_data in pies_config.items():
                if isinstance(pie_data, dict) and 'symbols' in pie_data:
                    if any(symbol['symbol'] == ticker_base for symbol in pie_data['symbols']):
                        pie_wartosci[pie_name] = pie_wartosci.get(pie_name, 0) + current_value
                        suma_w_pie += current_value
                        found_in_pie = True
                        break
                        
            if not found_in_pie:
                suma_poza_pie += current_value

        portfel = {
            "Suma_USD": round(suma_akcji_usd, 2),
            "Suma_PLN": round(suma_akcji_pln, 2),
            "Liczba_pozycji_calkowita": len(positions),
            "Liczba_pozycji_rdzennych": liczba_pozycji_rdzennych,
            "Liczba_pozycji_w_pie": liczba_pozycji_w_pie,
            "Cash_free_USD": round(cash_free / kurs_usd_pln if account.get("currencyCode") != "USD" else cash_free, 2),
            "Zrodlo": "Trading212 API",
            "Ilosc_PBR": round(ilosc_pbr, 2),
            "Ilosc_GAIN": round(ilosc_gain, 2),
            "Pozycje_szczegoly": pozycje_szczegoly,
            "Dane_rynkowe": dane_rynkowe,
            "Pie_wartosci": {
                "Details": pie_wartosci,
                "Suma_w_pie_USD": round(suma_w_pie, 2),
                "Suma_poza_pie_USD": round(suma_poza_pie, 2)
            }
        }
        
        # Wyświetlamy szczegółowe informacje o wartościach pie
        print(f"  ✓ Dane z T212 API przetworzone:")
        print(f"    - Pozycje rdzenne: {liczba_pozycji_rdzennych} (${portfel['Pie_wartosci']['Suma_poza_pie_USD']:.2f})")
        for pie_name, wartosc in portfel['Pie_wartosci']['Details'].items():
            print(f"    - {pie_name}: {sum(1 for pos in positions if any(symbol['symbol'] == pos.get('ticker', '').split('_')[0] for symbol in pies_config[pie_name]['symbols']))} pozycji (${wartosc:.2f})")
        
        return portfel
        
    except Exception as e:
        print_colored(f"  ⚠️  Błąd parsowania danych T212: {e}", "\033[93m")
        import traceback
        traceback.print_exc()
        return None

def format_positions_t212(positions):
    """Formatuje pozycje z Trading212 do czytelnej tabeli."""
    if not positions:
        return "(brak pozycji)"
    
    lines = []
    lines.append("Ticker | Nazwa | Ilość | Cena | Wartość | P/L")
    lines.append("-" * 80)
    
    for pos in positions[:20]:  # Pierwsze 20 pozycji
        ticker = pos.get("ticker", "N/A")
        quantity = pos.get("quantity", 0)
        current_price = pos.get("currentPrice", 0)
        avg_price = pos.get("averagePrice", 0)
        ppl = pos.get("ppl", 0)  # Profit/Loss
        
        value = quantity * current_price
        
        line = f"{ticker:8s} | {quantity:6.2f} | ${current_price:8.2f} | ${value:10.2f} | ${ppl:8.2f}"
        lines.append(line)
    
    if len(positions) > 20:
        lines.append(f"... i {len(positions) - 20} więcej pozycji")
    
    return "\n".join(lines)

def save_to_chronicle(author, message):
    """Zapisuje wpis do pliku kroniki."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(NAZWA_KRONIKI, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{author}]: {message}\n\n")
        historia_wypowiedzi.append((author, message, timestamp))
        licznik_wypowiedzi[author] += 1
    except Exception as e:
        print_colored(f"Błąd zapisu do kroniki: {e}", "\033[91m")

def analyze_sentiment(text):
    """Prosta analiza sentymentu."""
    pozytywne = ['zgadzam', 'świetnie', 'doskonale', 'popieram', 'dobrze', 'tak', 
                 'sukces', 'zysk', 'rozwój', 'możliwość', 'szansa', 'aprobuję']
    negatywne = ['nie', 'błąd', 'problem', 'ryzyko', 'strata', 'obawiam', 
                 'niepokoi', 'niebezpiecz', 'sprzeciwiam', 'przeciw', 'weto']
    
    text_lower = text.lower()
    poz_count = sum(1 for word in pozytywne if word in text_lower)
    neg_count = sum(1 for word in negatywne if word in text_lower)
    
    if poz_count > neg_count:
        return 'pozytywny'
    elif neg_count > poz_count:
        return 'negatywny'
    return 'neutralny'

def extract_topics(text):
    """Wyciąga główne tematy z tekstu."""
    tematy = {
        'akcje': ['akcj', 'portfel', 'giełd', 'inwestycj', 'trading', 'add', 'pie', 'twierdza'],
        'krypto': ['krypto', 'bitcoin', 'eth', 'blockchain', 'binance', 'gate', 'airdrop'],
        'długi': ['dług', 'kredyt', 'rata', 'spłat', 'zobowiązani'],
        'wypłata': ['wypłat', 'wynagrodzeni', 'premia', 'pensja', 'zarobki'],
        'kodeks': ['kodeks', 'artykuł', 'protokół', 'zasad', 'regulamin']
    }
    
    znalezione = []
    text_lower = text.lower()
    for temat, keywords in tematy.items():
        if any(keyword in text_lower for keyword in keywords):
            znalezione.append(temat)
    return znalezione

def inicjuj_glosowanie(propozycja, personas):
    """Inicjuje proces głosowania."""
    global aktywne_glosowanie
    
    udzialy = {
        "Partner Zarządzający (JA)": 35,
        "Partner Strategiczny": 30,
        "Partner ds. Jakości Biznesowej": 5,
        "Partner ds. Aktywów Cyfrowych": 5
    }
    
    aktywne_glosowanie = {
        "propozycja": propozycja,
        "glosy": {},
        "udzialy": udzialy,
        "status": "trwa"
    }
    
    print_colored("\n" + "="*80, "\033[95m")
    print_colored("🗳️  ROZPOCZĘTO GŁOSOWANIE ZGODNIE Z KODEKSEM SPÓŁKI", "\033[95m")
    print_colored("="*80, "\033[95m")
    print_colored(f"\n📋 Propozycja: {propozycja}\n", "\033[96m")
    print_colored("Struktura głosów (zgodnie z Artykułem II §1 Kodeksu):", "\033[93m")
    for partner, procent in udzialy.items():
        print(f"  • {partner}: {procent}%")
    print_colored("\n⏳ Oczekiwanie na głosy Partnerów...", "\033[93m")
    print_colored("="*80 + "\n", "\033[95m")

def oddaj_glos(partner_name, glos, uzasadnienie=""):
    """Rejestruje głos partnera."""
    global aktywne_glosowanie
    
    if not aktywne_glosowanie or aktywne_glosowanie["status"] != "trwa":
        return False
    
    if partner_name not in aktywne_glosowanie["udzialy"]:
        return False
    
    aktywne_glosowanie["glosy"][partner_name] = {
        "glos": glos.upper(),
        "uzasadnienie": uzasadnienie
    }
    
    procent = aktywne_glosowanie["udzialy"][partner_name]
    emoji = "✅" if glos.upper() == "TAK" else "❌"
    print_colored(f"{emoji} {partner_name} głosuje: {glos.upper()} ({procent}%)", "\033[96m")
    if uzasadnienie:
        print_colored(f"   Uzasadnienie: {uzasadnienie}", "\033[90m")
    
    return True

def podsumuj_glosowanie():
    """Podsumowuje wyniki głosowania."""
    global aktywne_glosowanie
    
    if not aktywne_glosowanie or aktywne_glosowanie["status"] != "trwa":
        return None
    
    glosy_za = 0
    glosy_przeciw = 0
    
    for partner, dane in aktywne_glosowanie["glosy"].items():
        procent = aktywne_glosowanie["udzialy"][partner]
        if dane["glos"] == "TAK":
            glosy_za += procent
        else:
            glosy_przeciw += procent
    
    wynik = "PRZYJĘTA" if glosy_za > glosy_przeciw else "ODRZUCONA"
    
    print_colored("\n" + "="*80, "\033[95m")
    print_colored("📊 WYNIKI GŁOSOWANIA", "\033[95m")
    print_colored("="*80, "\033[95m")
    print_colored(f"\n📋 Propozycja: {aktywne_glosowanie['propozycja']}\n", "\033[96m")
    
    print_colored("Szczegóły głosowania:", "\033[93m")
    for partner, dane in aktywne_glosowanie["glosy"].items():
        procent = aktywne_glosowanie["udzialy"][partner]
        emoji = "✅" if dane["glos"] == "TAK" else "❌"
        print(f"  {emoji} {partner} ({procent}%): {dane['glos']}")
    
    print_colored(f"\n🔢 Podsumowanie:", "\033[93m")
    print(f"  ✅ ZA: {glosy_za}%")
    print(f"  ❌ PRZECIW: {glosy_przeciw}%")
    
    if wynik == "PRZYJĘTA":
        print_colored(f"\n🎉 PROPOZYCJA ZOSTAŁA {wynik}!", "\033[92m")
    else:
        print_colored(f"\n⛔ PROPOZYCJA ZOSTAŁA {wynik}!", "\033[91m")
    
    print_colored("\nZgodnie z Kodeksem Spółki, Artykuł II §2:", "\033[90m")
    print_colored("'Wszystkie decyzje w Zarządzie podejmowane są wolą większości głosów.'", "\033[90m")
    print_colored("="*80 + "\n", "\033[95m")
    
    aktywne_glosowanie["status"] = "zakonczone"
    aktywne_glosowanie["wynik"] = wynik
    aktywne_glosowanie["glosy_za"] = glosy_za
    aktywne_glosowanie["glosy_przeciw"] = glosy_przeciw
    
    save_to_chronicle("SYSTEM", f"GŁOSOWANIE: {aktywne_glosowanie['propozycja']} - {wynik} ({glosy_za}% ZA, {glosy_przeciw}% PRZECIW)")
    
    return aktywne_glosowanie

def analyze_potential_conflict(user_message, personas):
    """
    Analizuje czy wiadomość może wywołać konflikt między Partnerami.
    Zwraca listę potencjalnych "stron konfliktu".
    """
    controversial_topics = {
        'krypto': ['krypto', 'bitcoin', 'btc', 'eth', 'crypto', 'spekulacj'],
        'ryzyko': ['ryzyko', 'agresywn', 'spekulacj', 'hazard'],
        'dlugi': ['dług', 'pożycz', 'kredyt', 'spłat'],
        'kodeks': ['kodeks', 'zasad', 'protokół', 'narusza'],
        'duze_kwoty': ['1000', '2000', '3000', '5000', 'premi', 'duż'],
    }
    
    user_lower = user_message.lower()
    controversial_score = 0
    
    for topic, keywords in controversial_topics.items():
        if any(kw in user_lower for kw in keywords):
            controversial_score += 1
    
    # Im więcej kontrowersyjnych tematów, tym większa szansa na konflikt
    return controversial_score >= 2

def detect_disagreement(responses):
    """
    Analizuje odpowiedzi i wykrywa czy są sprzeczne.
    Zwraca True jeśli wykryto konflikt.
    """
    # Słowa kluczowe wskazujące na zgodę vs sprzeciw
    agreement_words = ['zgadzam', 'popieram', 'słuszn', 'racja', 'dokładnie', 'tak']
    disagreement_words = ['nie zgadzam', 'sprzeciw', 'błąd', 'mylisz', 'naiwn', 
                          'nie', 'przeciw', 'wątpliw', 'ryzykowne']
    
    agree_count = 0
    disagree_count = 0
    
    for response in responses.values():
        response_lower = response.lower()
        if any(word in response_lower for word in agreement_words):
            agree_count += 1
        if any(word in response_lower for word in disagreement_words):
            disagree_count += 1
    
    # Konflikt gdy przynajmniej 1 osoba się nie zgadza
    return disagree_count > 0 and agree_count > 0

def save_conflict_memory(persona1, persona2, topic, who_was_right=None):
    """Zapisuje konflikt do pamięci."""
    global conflict_memory
    
    key = f"{persona1}_{persona2}"
    if key not in conflict_memory:
        conflict_memory[key] = []
    
    conflict_memory[key].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": topic,
        "who_was_right": who_was_right
    })
    
    # Zachowaj tylko ostatnie 5 konfliktów
    if len(conflict_memory[key]) > 5:
        conflict_memory[key] = conflict_memory[key][-5:]

def get_conflict_history(persona1, persona2):
    """Pobiera historię konfliktów między dwoma Partnerami."""
    key1 = f"{persona1}_{persona2}"
    key2 = f"{persona2}_{persona1}"
    
    conflicts = conflict_memory.get(key1, []) + conflict_memory.get(key2, [])
    
    if not conflicts:
        return ""
    
    history_text = "\n\nHISTORIA KONFLIKTÓW z tym Partnerem:\n"
    for conflict in conflicts[-3:]:  # Ostatnie 3
        history_text += f"- {conflict['date']}: Spór o {conflict['topic']}"
        if conflict.get('who_was_right'):
            history_text += f" (Rację miał: {conflict['who_was_right']})"
        history_text += "\n"
    
    return history_text

def generate_conflict_prompt(persona_name, user_message, other_responses, stan_spolki):
    """
    Generuje prompt dla Partnera w trybie konfliktu.
    Partner dostaje odpowiedzi innych i może się z nimi nie zgodzić.
    """
    # Zbierz odpowiedzi innych
    other_opinions = "\n\n📣 OPINIE INNYCH PARTNERÓW:\n"
    for other_name, other_response in other_responses.items():
        if other_name != persona_name:
            other_opinions += f"\n[{other_name}]:\n{other_response}\n"
            # Dodaj historię konfliktów z tym Partnerem
            other_opinions += get_conflict_history(persona_name, other_name)
    
    stan_json = json.dumps(stan_spolki, indent=2, ensure_ascii=False)
    length_instruction = get_response_length_instruction(False)
    
    prompt = f"""
{PERSONAS[persona_name]['system_instruction']}

KODEKS SPÓŁKI:
{KODEKS_SPOLKI}

Twoim tajnym celem jest: {PERSONAS[persona_name]['ukryty_cel']}

AKTUALNY STAN FINANSOWY:
{stan_json}

{other_opinions}

🥊 FINANCIAL FIGHT CLUB MODE - ZASADY:
1. NIE MUSISZ się zgadzać z innymi - wręcz przeciwnie!
2. Jeśli widzisz błąd w myśleniu innego Partnera - POWIEDZ TO
3. Używaj argumentów, danych, odwołuj się do Kodeksu
4. Bądź bezpośredni: "To naiwne", "@Partner się myli", "Kompletnie błędne założenia"
5. Możesz wspomnieć poprzednie błędy innych (jeśli są w historii)
6. Możesz tworzyć koalicje: "Zgadzam się z @Partner X przeciwko @Partner Y"
7. PAMIĘTAJ: Chodzi o najlepsze rozwiązanie, nie o bycie miłym

{length_instruction}

PYTANIE/SYTUACJA:
"{user_message}"

TWOJA ODPOWIEDŹ (możesz się zgodzić LUB ostro skrytykować innych):
"""
    
    return prompt

def get_response_length_instruction(is_spontaneous):

    """Zwraca instrukcję dotyczącą długości odpowiedzi w zależności od trybu."""
    global tryb_odpowiedzi
    
    if is_spontaneous:
        # Spontaniczne reakcje ZAWSZE krótkie
        return """
WAŻNE - DŁUGOŚĆ ODPOWIEDZI:
To spontaniczna reakcja - bądź BARDZO ZWIĘZŁY:
- Maksymalnie 2 zdania
- Tylko najważniejszy punkt
- Bez długich rozważań
"""
    
    if tryb_odpowiedzi == "zwiezly":
        return """
WAŻNE - DŁUGOŚĆ ODPOWIEDZI:
Odpowiedz ZWIĘŹLE I KONKRETNIE:
- Maksymalnie 3-4 zdania (około 50-80 słów)
- Jeden główny punkt + uzasadnienie
- Bez długich wprowadzeń i podsumowań
- Idź prosto do sedna
"""
    elif tryb_odpowiedzi == "normalny":
        return """
WAŻNE - DŁUGOŚĆ ODPOWIEDZI:
Odpowiedz w sposób STANDARDOWY:
- Około 5-7 zdań (100-150 słów)
- 2-3 punkty kluczowe
- Krótkie uzasadnienie dla każdego
"""
    else:  # szczegolowy
        return """
WAŻNE - DŁUGOŚĆ ODPOWIEDZI:
Możesz odpowiedzieć SZCZEGÓŁOWO:
- Pełna analiza bez limitów
- Wszystkie istotne punkty
- Szczegółowe uzasadnienia
"""
def generate_dashboard():
    """Generuje dashboard z statystykami spotkania."""
    print_colored("\n" + "="*70, "\033[96m")
    print_colored("📊 DASHBOARD SPOTKANIA - PODSUMOWANIE", "\033[96m")
    print_colored("="*70, "\033[96m")
    
    if not historia_wypowiedzi:
        print_colored("Brak danych do analizy (puste spotkanie).", "\033[93m")
        return
    
    print_colored("\n📈 STATYSTYKI WYPOWIEDZI:", "\033[92m")
    for persona, count in licznik_wypowiedzi.most_common():
        procent = (count / sum(licznik_wypowiedzi.values())) * 100
        bar = "█" * int(procent / 5)
        print(f"  {persona:35s} | {count:2d} wypowiedzi ({procent:5.1f}%) {bar}")
    
    print_colored("\n😊 ANALIZA SENTYMENTU:", "\033[92m")
    sentiment_counts = {'pozytywny': 0, 'negatywny': 0, 'neutralny': 0}
    for author, msg, _ in historia_wypowiedzi:
        if author != "Partner Zarządzający (JA)":
            sentiment = analyze_sentiment(msg)
            sentiment_counts[sentiment] += 1
    
    total_sentiment = sum(sentiment_counts.values())
    if total_sentiment > 0:
        for sentiment, count in sentiment_counts.items():
            procent = (count / total_sentiment) * 100
            emoji = "😊" if sentiment == 'pozytywny' else "😟" if sentiment == 'negatywny' else "😐"
            print(f"  {emoji} {sentiment.capitalize():12s}: {count:2d} ({procent:5.1f}%)")
    
    print_colored("\n💼 GŁÓWNE TEMATY ROZMÓW:", "\033[92m")
    all_topics = []
    for author, msg, _ in historia_wypowiedzi:
        all_topics.extend(extract_topics(msg))
    
    topic_counts = Counter(all_topics)
    if topic_counts:
        for topic, count in topic_counts.most_common(5):
            print(f"  • {topic.capitalize()}: {count} wzmianek")
    else:
        print("  (brak wykrytych tematów)")
    
    print_colored("\n⏰ TIMELINE SPOTKANIA:", "\033[92m")
    if len(historia_wypowiedzi) >= 2:
        pierwsza = historia_wypowiedzi[0][2]
        ostatnia = historia_wypowiedzi[-1][2]
        print(f"  Rozpoczęcie: {pierwsza}")
        print(f"  Zakończenie: {ostatnia}")
        print(f"  Łącznie wypowiedzi: {len(historia_wypowiedzi)}")
    
    print_colored("="*70 + "\n", "\033[96m")

def analizuj_dywidendy(ticker, ticker_info):
    """
    Analizuje historię i przyszłość dywidend dla danej spółki.
    Używa cache'u do przyspieszenia kolejnych wywołań.
    """
    try:
        # Sprawdź cache dla danych o dywidendach
        dividend_cache_key = f"dividend_data_{ticker}"
        cached_dividend_data = yf_cache.get_data(dividend_cache_key)
        if cached_dividend_data:
            return cached_dividend_data
            
        # Sprawdź cache dla danych historycznych
        history_cache_key = f"history_data_{ticker}"
        cached_history = yf_cache.get_data(history_cache_key)
        if cached_history:
            hist_div = pd.DataFrame(cached_history)
            
        # Jeśli nie ma w cache'u, pobierz świeże dane
        stock = yf.Ticker(ticker)
        try:
            info = stock.info
        except Exception as e:
            print(f"⚠️ {ticker}: Błąd pobierania danych - {str(e)}")
            info = {}
            
        if not info or 'regularMarketPrice' not in info:
            print(f"⚠️ {ticker}: Ticker niedostępny lub wycofany z obrotu")
            return None
            
        # Historia dywidend
        try:
            hist_div = stock.dividends
            if hist_div is None or len(hist_div) == 0:
                if 'dividendRate' not in ticker_info:
                    print(f"ℹ️ {ticker}: Brak historii dywidend")
                    return None
                    
                # Jeśli nie ma historii, ale jest dividendRate, tworzymy sztuczną historię
                last_div = ticker_info.get('lastDividendValue', ticker_info['dividendRate'] / 4)
                hist_div = pd.Series([last_div], index=[pd.Timestamp.now()])
                
            # Konwertujemy serię na DataFrame
            hist_div = hist_div.to_frame(name='Dividends')
        except:
            if 'dividendRate' not in ticker_info:
                return None
                
            # Alternatywne podejście używając tylko ticker_info
            last_div = ticker_info.get('lastDividendValue', ticker_info['dividendRate'] / 4)
            hist_div = pd.DataFrame({'Dividends': [last_div]}, 
                                  index=[pd.Timestamp.now()])
        
        # Ostatnie 5 lat dywidend
        last_5y = hist_div.tail(20)  # Bierzemy ostatnie 20 wypłat
        
        # Obliczanie rocznej stopy wzrostu dywidend (CAGR)
        if len(last_5y) >= 2:
            oldest_div = last_5y.iloc[0]['Dividends']
            newest_div = last_5y.iloc[-1]['Dividends']
            years = (last_5y.index[-1] - last_5y.index[0]).days / 365.25
            div_cagr = ((newest_div / oldest_div) ** (1/years) - 1) * 100 if oldest_div > 0 else 0
        else:
            div_cagr = 0
            
        # Następna data dywidendy i kwota
        next_div_date = None
        next_div_amount = None
        calendar = stock.calendar
        if calendar is not None and isinstance(calendar, pd.DataFrame) and not calendar.empty:
            if 'Dividend Date' in calendar.index:
                next_div_date = calendar.loc['Dividend Date'].iloc[0]
            if 'Dividend' in calendar.index:
                next_div_amount = calendar.loc['Dividend'].iloc[0]
        
        # Roczna suma dywidend
        try:
            annual_div = 0
            # Próba 1: Użyj forward annual dividend rate (przewidywana roczna dywidenda na akcję)
            if 'dividendRate' in info and isinstance(info['dividendRate'], (int, float)) and 0 < info['dividendRate'] < 100:
                annual_div = info['dividendRate']
                print(f"ℹ️ {ticker}: Użyto dividendRate: ${annual_div:.4f}/akcję")
            
            # Próba 2: Użyj trailing annual dividend (faktyczna roczna dywidenda na akcję)
            elif 'trailingAnnualDividendRate' in info and isinstance(info['trailingAnnualDividendRate'], (int, float)) and 0 < info['trailingAnnualDividendRate'] < 100:
                annual_div = info['trailingAnnualDividendRate']
                print(f"ℹ️ {ticker}: Użyto trailingAnnualDividendRate: ${annual_div:.4f}/akcję")
            
            # Próba 3: Użyj dividendRate z ticker_info
            elif 'dividendRate' in ticker_info and isinstance(ticker_info['dividendRate'], (int, float)) and 0 < ticker_info['dividendRate'] < 100:
                annual_div = ticker_info['dividendRate']
                print(f"ℹ️ {ticker}: Użyto ticker_info dividendRate: ${annual_div:.4f}/akcję")
            
            # Próba 4: Oblicz z historii
            else:
                # Pobierz wypłaty z ostatniego roku
                recent_divs = last_5y.tail(4)['Dividends']  # Dla kwartalnych
                annual_divs = last_5y.tail(12)['Dividends']  # Dla miesięcznych
                if len(recent_divs) > 0:
                    freq = min(12, len(last_5y) // (max(1, round(years))))  # Częstotliwość wypłat
                    if freq == 4 and len(recent_divs) >= 4:  # Kwartalne wypłaty
                        annual_div = sum(recent_divs.tail(4))
                        print(f"ℹ️ {ticker}: Użyto 4 ostatnie kwartalne wypłaty: ${annual_div:.4f}/akcję")
                    elif freq == 12 and len(annual_divs) >= 12:  # Miesięczne wypłaty
                        annual_div = sum(annual_divs.tail(12))
                        print(f"ℹ️ {ticker}: Użyto 12 ostatnich miesięcznych wypłat: ${annual_div:.4f}/akcję")
                    elif freq > 0:  # Inne częstotliwości
                        avg_payment = sum(recent_divs) / len(recent_divs)  # Średnia wypłata
                        annual_div = avg_payment * freq  # Roczna suma
                        print(f"ℹ️ {ticker}: Użyto średnią z {len(recent_divs)} wypłat × częstotliwość {freq}: ${annual_div:.4f}/akcję")
                    
            # Walidacja końcowa
            if not isinstance(annual_div, (int, float)) or annual_div < 0:
                annual_div = 0
                
        except Exception as e:
            print(f"Błąd obliczania rocznej dywidendy dla {ticker}: {str(e)}")
            annual_div = 0
            
        # Obliczanie yieldu z różnych źródeł
        div_yield = 0
        current_price = None
        
        # Próba 1: Pobierz aktualną cenę
        if 'regularMarketPrice' in info and isinstance(info['regularMarketPrice'], (int, float)):
            current_price = info['regularMarketPrice']
        elif 'currentPrice' in ticker_info and isinstance(ticker_info['currentPrice'], (int, float)):
            current_price = ticker_info['currentPrice']
        elif 'previousClose' in info and isinstance(info['previousClose'], (int, float)):
            current_price = info['previousClose']
            
        # Próba 2: Bezpośrednio z info
        if 'dividendYield' in info and isinstance(info['dividendYield'], (int, float)):
            div_yield = info['dividendYield'] * 100
            if div_yield > 100:  # Sanity check - yield nie powinien przekraczać 100%
                div_yield = 0
            
        # Próba 3: Z ticker_info
        if div_yield == 0 and ticker_info.get('dividendYield') and isinstance(ticker_info['dividendYield'], (int, float)):
            div_yield = ticker_info['dividendYield'] * 100
            if div_yield > 100:  # Sanity check
                div_yield = 0
            
        # Próba 4: Oblicz na podstawie rocznej dywidendy i ceny
        if div_yield == 0 and annual_div > 0 and current_price and current_price > 0:
            div_yield = (annual_div / current_price) * 100
            if div_yield > 100:  # Sanity check
                div_yield = 0
                
        # Dodatkowa walidacja
        if not isinstance(div_yield, (int, float)):
            div_yield = 0

        # Przygotuj dane do zwrotu
        dividend_data = {
            "div_yield": div_yield,  # Już w procentach
            "last_div_date": hist_div.index[-1].strftime("%Y-%m-%d") if len(hist_div) > 0 else None,
            "last_div_amount": float(hist_div.iloc[-1]['Dividends']) if len(hist_div) > 0 else 0,
            "next_div_date": next_div_date.strftime("%Y-%m-%d") if next_div_date else None,
            "next_div_amount": float(next_div_amount) if next_div_amount else None,
            "div_growth_cagr": round(div_cagr, 2),
            "annual_div": round(annual_div, 4),
            "div_history": [{"date": str(date), "amount": float(amount)} for date, amount in hist_div.tail(8)['Dividends'].items()],
            "div_frequency": min(12, len(last_5y) // (max(1, round(years))))  # Ograniczamy do max 12 wypłat rocznie
        }
        
        # Zapisz do cache'u
        dividend_cache_key = f"dividend_data_{ticker}"
        yf_cache.set_data(dividend_cache_key, dividend_data)
        
        return dividend_data

    except Exception as e:
        print(f"Błąd analizy dywidend dla {ticker}: {str(e)}")
        return None

def pobierz_dane_yfinance(tickery):
    """
    Pobiera kluczowe wskaźniki finansowe, używając asynchronicznego pobierania danych
    dla lepszej wydajności. Używa cache'u do przyspieszenia kolejnych wywołań.
    """
    # Konfiguracja certyfikatów SSL
    cert_path = certifi.where()
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    os.environ['CURL_CA_BUNDLE'] = cert_path
    
    # Sprawdź cache dla danych rynkowych
    cached_data = yf_cache.get_data("market_data")
    if cached_data:
        return cached_data
        
    print("🔄 Pobieram świeże dane rynkowe (asynchronicznie)...")
    
    # Przygotuj listę tickerów do pobrania
    tickery_do_pobrania = []
    for ticker_oryginalny in tickery:
        ticker_base = ticker_oryginalny.split('_')[0]  # Usuń suffiks
        if ticker_base not in tickery_do_pobrania:
            tickery_do_pobrania.append(ticker_base)
            
    # Pobierz dane asynchronicznie
    try:
        # Spróbuj użyć cache'u najpierw
        cached_data = yf_cache.get_data('market_data')
        if cached_data:
            age = time.time() - cached_data.get('timestamp', 0)
            if age < 3600:  # 1 godzina
                print(f"📥 Używam cache'u dla market_data (wiek: {age/60:.1f}min)")
                return cached_data.get('data', {})

        print("🔄 Pobieram świeże dane rynkowe...")
        
        # Utwórz i skonfiguruj pętlę zdarzeń
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Inicjalizacja asynchronicznego managera
            loop.run_until_complete(async_manager.initialize())
            
            # Pobieranie danych z obsługą przerwań
            dane_szczegolowe = loop.run_until_complete(async_manager.fetch_multiple_stocks(tickery_do_pobrania))
            
            # Jeśli udało się pobrać jakieś dane, zapisz do cache'u
            if dane_szczegolowe:
                yf_cache.set_data('market_data', {
                    'timestamp': time.time(),
                    'data': dane_szczegolowe
                })
                print("💾 Zapisano do cache'u: market_data (odświeżanie co 1:00:00)")
            
        except KeyboardInterrupt:
            print("\n⚠️ Przerwano pobieranie danych...")
            # Próbuj użyć starych danych z cache'u w przypadku przerwania
            if cached_data:
                print("📥 Używam poprzednich danych z cache'u")
                return cached_data.get('data', {})
        finally:
            # Zamknij sesję i pętlę - bardziej niezawodnie
            try:
                if hasattr(async_manager, 'session') and async_manager.session:
                    loop.run_until_complete(async_manager.session.close())
            except:
                pass
            
            try:
                # Anuluj wszystkie pending tasks
                try:
                    pending = asyncio.all_tasks(loop)
                except AttributeError:
                    # Starsze wersje Pythona
                    pending = asyncio.Task.all_tasks(loop)
                
                for task in pending:
                    task.cancel()
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass
                
            loop.close()
            asyncio.set_event_loop(None)
            
    except Exception as e:
        print(f"⚠️ Błąd podczas pobierania danych: {str(e)}")
        # Próbuj użyć cache'u w przypadku błędu
        if cached_data:
            print("📥 Używam poprzednich danych z cache'u")
            return cached_data.get('data', {})
        dane_szczegolowe = {}
    
    # === SŁOWNIK TŁUMACZEŃ ===
    # Mapuje nazwy z T212 (lub inne niestandardowe) na poprawne symbole yfinance
    mapowanie_tickerow = {
        'SXRVd_EQ': 'SXR8.DE',  # Trading212 zwraca małe "d"
        'VWCEd_EQ': 'VWCE.DE',  # Trading212 zwraca małe "d"
        'BCAT_US_EQ': 'BCAT',
        # Możesz tu w przyszłości dodawać kolejne, jeśli pojawią się problemy
    }
    # ==========================

    unikalne_tickery = list(set(tickery))
    
    for ticker_oryginalny in unikalne_tickery:
        try:
            # KROK 1: Spróbuj użyć "tłumacza"
            if ticker_oryginalny in mapowanie_tickerow:
                ticker_do_wyszukania = mapowanie_tickerow[ticker_oryginalny]
                print_colored(f"    [yfinance] Tłumaczę '{ticker_oryginalny}' na '{ticker_do_wyszukania}'...", "\033[90m")
            else:
                # Jeśli nie ma w słowniku, spróbuj oczyścić automatycznie
                ticker_do_wyszukania = ticker_oryginalny.split('_')[0]

            # KROK 2: Pobierz dane dla przetłumaczonego/oczyszczonego tickera
            ticker_obj = yf.Ticker(ticker_do_wyszukania)
            info = ticker_obj.info

            if not info or info.get('regularMarketPrice') is None:
                 raise ValueError(f"Nie znaleziono danych dla symbolu '{ticker_do_wyszukania}'")

            # KROK 3: Zbieranie danych podstawowych
            dane_podstawowe = {
                "nazwa": info.get('shortName', 'Brak danych'),
                "sektor": info.get('sector', 'N/A'),
                "branza": info.get('industry', 'N/A'),
                "kapitalizacja": info.get('marketCap', 0),
                "PE": info.get('trailingPE'),
                "przyszle_PE": info.get('forwardPE'),
                "dywidenda_roczna": info.get('dividendYield', 0) or 0
            }
            
            # KROK 4: Dodaj analizę dywidend
            dane_dywidend = analizuj_dywidendy(ticker_do_wyszukania, info)
            if dane_dywidend:
                dane_podstawowe["analiza_dywidend"] = dane_dywidend
                
            dane_szczegolowe[ticker_oryginalny] = dane_podstawowe

        except Exception as e:
            print_colored(f"    [yfinance] ⚠️  Pominięto ticker '{ticker_oryginalny}'. Powód: {e}", "\033[90m")
            continue

    print_colored("    [yfinance] ✓ Pobieranie danych rynkowych zakończone.", "\033[92m")
    
    # Zapisz dane do cache'u
    yf_cache.set_data("market_data", dane_szczegolowe)
    print("💾 Dane zapisane do cache'u")
    
    return dane_szczegolowe

def save_session(session_name, stan_spolki, last_responses):
    """Zapisuje stan sesji do pliku JSON."""
    try:
        if not os.path.exists(FOLDER_SESJI):
            os.makedirs(FOLDER_SESJI)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{session_name}_{timestamp}.json"
        filepath = os.path.join(FOLDER_SESJI, filename)
        
        session_data = {
            "session_name": session_name,
            "timestamp": timestamp,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stan_spolki": stan_spolki,
            "last_responses": last_responses,
            "historia_wypowiedzi": historia_wypowiedzi,
            "licznik_wypowiedzi": dict(licznik_wypowiedzi)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        print_colored(f"\n✅ Sesja zapisana: {filepath}", "\033[92m")
        return True
        
    except Exception as e:
        print_colored(f"\n❌ Błąd zapisu sesji: {e}", "\033[91m")
        return False

def load_session(session_name):
    """Wczytuje stan sesji z pliku JSON."""
    try:
        if not os.path.exists(FOLDER_SESJI):
            print_colored(f"❌ Folder '{FOLDER_SESJI}' nie istnieje.", "\033[91m")
            return None
        
        matching_files = [f for f in os.listdir(FOLDER_SESJI) if f.startswith(session_name)]
        
        if not matching_files:
            print_colored(f"❌ Nie znaleziono sesji o nazwie '{session_name}'", "\033[91m")
            print_colored(f"Dostępne sesje w folderze '{FOLDER_SESJI}':", "\033[93m")
            all_files = os.listdir(FOLDER_SESJI)
            if all_files:
                for f in all_files:
                    print(f"  - {f}")
            else:
                print("  (brak zapisanych sesji)")
            return None
        
        latest_file = sorted(matching_files)[-1]
        filepath = os.path.join(FOLDER_SESJI, latest_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        print_colored(f"\n✅ Wczytano sesję: {filepath}", "\033[92m")
        print_colored(f"   Data zapisu: {session_data['datetime']}", "\033[93m")
        
        global historia_wypowiedzi, licznik_wypowiedzi
        historia_wypowiedzi = session_data.get('historia_wypowiedzi', [])
        licznik_wypowiedzi = Counter(session_data.get('licznik_wypowiedzi', {}))
        
        return session_data
        
    except Exception as e:
        print_colored(f"\n❌ Błąd wczytywania sesji: {e}", "\033[91m")
        return None

def check_spontaneous_reaction(user_message, target_personas, all_personas, last_responses):
    """Sprawdza czy któraś z person powinna spontanicznie zareagować."""
    potential_reactors = []
    user_message_lower = user_message.lower()
    
    other_personas = [name for name in all_personas.keys() if name not in target_personas]
    
    for persona_name in other_personas:
        ukryty_cel = all_personas[persona_name]['ukryty_cel'].lower()
        cel_keywords = extract_topics(ukryty_cel)
        msg_keywords = extract_topics(user_message_lower)
        
        if any(keyword in msg_keywords for keyword in cel_keywords):
            if random.random() < SZANSA_SPONTANICZNEGO_KOMENTARZA:
                potential_reactors.append(persona_name)
    
    if len(potential_reactors) > MAX_SPONTANICZNYCH_REAKCJI:
        potential_reactors = random.sample(potential_reactors, MAX_SPONTANICZNYCH_REAKCJI)
    
    return potential_reactors

def generuj_odpowiedz_ai(persona_name, prompt):
    """Kieruje zapytanie do odpowiedniego, darmowego modelu AI przez różne API."""
    persona_config = PERSONAS.get(persona_name, {})
    model_engine = persona_config.get('model_engine', 'gemini')
    
    print(f"    [AI Engine: Używam {model_engine.upper()} dla postaci '{persona_name}']")
    
    # Pobierz tracker API
    tracker = get_tracker()

    try:
        if model_engine.startswith('openrouter'):
            client = openai.OpenAI(
                api_key=get_api_key("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )
            
            model_map = {
                'openrouter_llama': "meta-llama/llama-4-maverick:free",
                'openrouter_mistral': "mistralai/mistral-7b-instruct:free",
                'openrouter_mixtral': "meta-llama/llama-4-scout:free",
                'openrouter_glm': "z-ai/glm-4.5-air:free",
            }
            model_name = model_map.get(model_engine)

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            # Track API call (openrouter używa OpenAI compatible API)
            tracker.track_call("openai", is_autonomous=False)
            
            return response.choices[0].message.content

        else: # Domyślnie Gemini
            wait_for_gemini_rate_limit()
            
            # LAZY LOAD: Załaduj Gemini tylko gdy potrzebne
            global model_gemini
            if model_gemini is None:
                print_colored("   [Lazy load: Ładuję Gemini po raz pierwszy...]", "\033[96m")
                model_gemini = get_ai_client("gemini")
                if model_gemini is None:
                    return "[BŁĄD: Gemini niedostępny]"

            response = model_gemini.generate_content(prompt)
            
            # Track API call
            tracker.track_call("gemini", is_autonomous=False)
            
            if not response.parts:
                return "[ODPOWIEDŹ ZABLOKOWANA PRZEZ FILTRY BEZPIECZEŃSTWA GEMINI]"
            return response.text

    except Exception as e:
        error_type = type(e).__name__
        error_details = str(e)
        print_colored(f"  ❌ Błąd API dla {model_engine.upper()}: {error_type}", "\033[91m")
        
        if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'text'):
             print_colored(f"     Odpowiedź serwera: {e.response.text}", "\033[90m")
        elif hasattr(e, 'message'):
             print_colored(f"     Szczegóły: {e.message}", "\033[90m")
        else:
             print_colored(f"     Szczegóły: {error_details}", "\033[90m")
             
        return f"[BŁĄD API: Nie udało się uzyskać odpowiedzi z {model_engine.upper()}]"
def format_table_for_ai(rows, max_rows=50):
    if not rows:
        return "(brak danych)"
    
    if len(rows) > max_rows:
        rows = rows[:max_rows]
        truncated_note = f"\n... (pokazano pierwszych {max_rows} wierszy)"
    else:
        truncated_note = ""
    
    col_widths = []
    num_cols = max(len(row) for row in rows)
    
    for col_idx in range(num_cols):
        max_width = 0
        for row in rows:
            if col_idx < len(row):
                cell_value = str(row[col_idx]) if row[col_idx] else ""
                max_width = max(max_width, len(cell_value))
        col_widths.append(min(max_width, 30))
    
    table_lines = []
    for row_idx, row in enumerate(rows):
        line_parts = []
        for col_idx in range(num_cols):
            cell_value = str(row[col_idx]) if col_idx < len(row) and row[col_idx] else ""
            if len(cell_value) > 30:
                cell_value = cell_value[:27] + "..."
            line_parts.append(cell_value.ljust(col_widths[col_idx]))
        table_lines.append(" | ".join(line_parts))
        
        if row_idx == 0:
            separator = "-+-".join(["-" * w for w in col_widths])
            table_lines.append(separator)
    
    return "\n".join(table_lines) + truncated_note

def wczytaj_konfiguracje_person(nazwa_pliku):
    """Wczytuje i parsuje konfigurację PERSONAS z pliku."""
    if not os.path.exists(nazwa_pliku):
        print_colored(f"BŁĄD KRYTYCZNY: Nie znaleziono pliku konfiguracyjnego '{nazwa_pliku}'.", "\033[91m")
        print_colored("Uruchom najpierw skrypt 'generator_celow.py', aby go stworzyć.", "\033[93m")
        return None
    
    with open(nazwa_pliku, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        slownik_str = content.split('=', 1)[1].strip()
        persony = ast.literal_eval(slownik_str)
        print_colored(f"✓ Pomyślnie wczytano konfigurację dla {len(persony)} postaci z pliku '{nazwa_pliku}'.", "\033[92m")
        return persony
    except Exception as e:
        print_colored(f"BŁĄD KRYTYCZNY: Nie udało się wczytać konfiguracji postaci z pliku '{nazwa_pliku}'. Sprawdź jego zawartość. Błąd: {e}", "\033[91m")
        return None

# --- GŁÓWNA LOGIKA PROGRAMU ---

PERSONAS = wczytaj_konfiguracje_person(NAZWA_PLIKU_KONFIGURACJI_PERSON)
if not PERSONAS:
    exit()

KODEKS_SPOLKI = wczytaj_kodeks()
CELE = wczytaj_cele()

# === LAZY LOADING AI CLIENTS ===
# Zamiast inicjalizować wszystkie AI na starcie, tworzymy je na żądanie
_ai_clients = {}

def get_ai_client(engine_name):
    """
    Lazy loading AI clients - tworzy tylko gdy potrzebne.
    Oszczędza RAM i przyspiesza start aplikacji.
    Importuje biblioteki AI dopiero gdy są potrzebne.
    """
    global _ai_clients
    
    if engine_name in _ai_clients:
        return _ai_clients[engine_name]
    
    try:
        if engine_name == "gemini":
            import google.generativeai as genai  # LAZY IMPORT
            genai.configure(api_key=get_api_key("GOOGLE_API_KEY"))
            client = genai.GenerativeModel('gemini-2.5-pro')
            print_colored("✓ Gemini AI zainicjalizowany.", "\033[92m")
            
        elif engine_name == "openai":
            import openai  # LAZY IMPORT
            client = openai.OpenAI(api_key=get_api_key("OPENAI_API_KEY"))
            print_colored("✓ OpenAI GPT zainicjalizowany.", "\033[92m")
            
        elif engine_name == "deepseek":
            import openai  # LAZY IMPORT
            client = openai.OpenAI(
                api_key=get_api_key("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1"
            )
            print_colored("✓ DeepSeek AI zainicjalizowany.", "\033[92m")
            
        elif engine_name == "anthropic":
            import anthropic  # LAZY IMPORT
            client = anthropic.Anthropic(api_key=get_api_key("ANTHROPIC_API_KEY"))
            print_colored("✓ Anthropic Claude zainicjalizowany.", "\033[92m")
            
        else:
            raise ValueError(f"Nieznany silnik AI: {engine_name}")
        
        _ai_clients[engine_name] = client
        return client
        
    except Exception as e:
        print_colored(f"⚠️ Nie udało się zainicjalizować {engine_name}: {e}", "\033[93m")
        return None

# Inicjalizacja tylko Gemini (domyślny, darmowy)
print_colored("� ULTRA-SZYBKI START: Lazy loading aktywny!", "\033[96m")
print_colored("   → Gemini: ładuje się teraz", "\033[96m")
print_colored("   → Claude/OpenAI: załadują się gdy potrzebne", "\033[96m")
print_colored("   → Google Sheets: załadują się gdy potrzebne", "\033[96m")
try:
    # NIE inicjalizuj nic przy starcie - WSZYSTKO lazy load
    model_gemini = None  # get_ai_client("gemini")  # Lazy load - bedzie utworzony gdy potrzebny
    # Pozostałe AI będą ładowane na żądanie
    client_openai = None  # Lazy load
    client_deepseek = None  # Lazy load
    client_anthropic = None  # Lazy load
    print_colored("ULTRA-SZYBKI START: System gotowy w <3 sekundy!", "\033[92m")
except Exception as e:
    print_colored(f"⚠️ Gemini niedostępny: {e}", "\033[93m")
    model_gemini = None

# === GOOGLE SHEETS CLIENT - LAZY LOADING ===
_gspread_client = None

def get_gspread_client():
    """Lazy loading Google Sheets client - tworzy tylko gdy potrzebne."""
    global _gspread_client
    
    if _gspread_client is not None:
        return _gspread_client
    
    import gspread  # LAZY IMPORT
    import httplib2
    
    if not os.path.exists(NAZWA_PLIKU_KREDENCJALI):
        print_colored(f"BŁĄD KRYTYCZNY: Nie znaleziono pliku '{NAZWA_PLIKU_KREDENCJALI}'.", "\033[91m")
        print_colored("Upewnij się, że plik znajduje się w tym samym folderze co skrypt.", "\033[93m")
        return None
    
    try:
        # Konfiguracja SSL dla gspread
        httplib2.Http(ca_certs=certifi.where())
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
        
        # Utworzenie klienta z niestandardową konfiguracją SSL
        creds = Credentials.from_service_account_file(NAZWA_PLIKU_KREDENCJALI, scopes=scopes)
        session = requests.Session()
        session.verify = certifi.where()
        
        gc = gspread.Client(auth=creds)
        gc.session = session
        
        _gspread_client = gc
        print_colored("✓ Google Sheets API połączony.", "\033[92m")
        return gc
    except Exception as e:
        print_colored(f"⚠️ Nie udało się połączyć z Google Sheets API: {e}", "\033[93m")
        return None

# NIE inicjalizuj Google Sheets przy starcie - będzie lazy loaded
# if not os.path.exists(NAZWA_PLIKU_KREDENCJALI):
#     print_colored(f"BŁĄD KRYTYCZNY: Nie znaleziono pliku '{NAZWA_PLIKU_KREDENCJALI}'.", "\033[91m")
#     print_colored("Upewnij się, że plik znajduje się w tym samym folderze co skrypt.", "\033[93m")
#     exit(1)

# NIE inicjalizuj Google Sheets przy starcie - będzie lazy loaded
# if not os.path.exists(NAZWA_PLIKU_KREDENCJALI):
#     print_colored(f"BŁĄD KRYTYCZNY: Nie znaleziono pliku '{NAZWA_PLIKU_KREDENCJALI}'.", "\033[91m")
#     print_colored("Upewnij się, że plik znajduje się w tym samym folderze co skrypt.", "\033[93m")
#     exit(1)

# try:
#     # Konfiguracja SSL dla gspread
#     import httplib2
#     httplib2.Http(ca_certs=certifi.where())
#     
#     scopes = [
#         "https://www.googleapis.com/auth/spreadsheets.readonly",
#         "https://www.googleapis.com/auth/drive.readonly"
#     ]
#     
#     # Utworzenie klienta z niestandardową konfiguracją SSL
#     creds = Credentials.from_service_account_file(NAZWA_PLIKU_KREDENCJALI, scopes=scopes)
#     session = requests.Session()
#     session.verify = certifi.where()
#     
#     gc = gspread.Client(auth=creds)
#     gc.session = session
#     
#     print_colored("✓ Pomyślnie połączono z Google Sheets API.", "\033[92m")
# except Exception as e:
#     print_colored(f"KRYTYCZNY BŁĄD: Nie udało się połączyć z Google Sheets API. Sprawdź plik credentials.json i udostępnienie arkuszy. Błąd: {e}", "\033[91m")
#     exit(1)

last_responses = { name: "Jeszcze nic nie powiedział/a." for name in PERSONAS }

def pobierz_stan_spolki(cele):
    """Pobiera najnowsze dane ze WSZYSTKICH źródeł (Trading212 API + Google Sheets)."""
    print("⏳ Pobieram najnowsze dane finansowe...")
    stan_spolki = {}
    
    try:
        kurs_usd = pobierz_kurs_usd_pln()
        stan_spolki["Kurs_USD_PLN"] = kurs_usd
        
        # === ARKUSZ AKCJE - TRADING212 API (z fallback do Google Sheets) ===
        print("  📈 Pobieram dane o akcjach...")
        
        # Próba 1: Trading212 API
        dane_t212 = pobierz_dane_trading212() if TRADING212_ENABLED else None
        
        if dane_t212:
            portfel_akcji = parsuj_dane_t212_do_portfela(dane_t212, kurs_usd, cele)
            if portfel_akcji:
                stan_spolki["PORTFEL_AKCJI"] = portfel_akcji
                print_colored(f"  ✓ Dane akcji z Trading212 API: {portfel_akcji['Suma_PLN']:.2f} PLN", "\033[92m")
            else:
                print_colored("  ⚠️  Błąd parsowania T212 - przechodzę na Google Sheets...", "\033[93m")
                dane_t212 = None
        
# Fallback: Google Sheets
        if not dane_t212:
            print("  📊 Używam Google Sheets jako źródło danych akcji...")
            gc = get_gspread_client()  # LAZY LOAD
            if not gc:
                print_colored("  ⚠️ Google Sheets niedostępny - brak danych akcji!", "\033[93m")
                stan_spolki["PORTFEL_AKCJI"] = {"Suma_PLN": 0, "tickery": []}
                return stan_spolki
            
            arkusz_akcje = gc.open(NAZWY_ARKUSZY["akcje"]).sheet1
            dane_akcje = arkusz_akcje.get_all_values()
            
            suma_akcji_pln = 0
            ilosc_pbr = 0
            ilosc_gain = 0
            tickery_w_portfelu = []
            
            for row in dane_akcje[1:]:
                try:
                    if len(row) > 1 and row[1]:
                        ticker = row[1].upper()
                        tickery_w_portfelu.append(ticker)

                        if len(row) > 7 and row[7]:
                            wartosc = str(row[7]).replace(',', '.').strip()
                            suma_akcji_pln += float(wartosc)
                        
                        ilosc_str = row[3].replace(',', '.').strip()
                        if ticker == 'PBR':
                            ilosc_pbr += float(ilosc_str)
                        elif ticker == 'GAIN':
                            ilosc_gain += float(ilosc_str)
                except (ValueError, IndexError):
                    continue
            
            # --- NOWA LOGIKA YFINANCE ---
            dane_rynkowe = pobierz_dane_yfinance(tickery_w_portfelu)
            # ---------------------------

            stan_spolki["PORTFEL_AKCJI"] = {
                "Suma_PLN": round(suma_akcji_pln, 2),
                "Suma_USD": round(suma_akcji_pln / kurs_usd, 2),
                "Liczba_pozycji": len([r for r in dane_akcje[1:] if len(r) > 1 and r[1]]),
                "Zrodlo": "Google Sheets (Backup)",
                "Szczegoly_tabela": format_table_for_ai(dane_akcje[:20]),
                "Ilosc_PBR": ilosc_pbr,
                "Ilosc_GAIN": ilosc_gain,
                "Dane_rynkowe": dane_rynkowe # <-- DODAJEMY DANE RYNKOWE
            }
            print(f"  ✓ Arkusz 'Akcje' wczytany: {suma_akcji_pln:.2f} PLN (PBR: {ilosc_pbr}, GAIN: {ilosc_gain})")
        
        # KRYPTO - Z LOKALNEGO PLIKU JSON
        print("  💰 Pobieram dane krypto z lokalnego pliku...")
        try:
            with open('krypto.json', 'r', encoding='utf-8') as f:
                krypto_data = json.load(f)
                krypto_lista = krypto_data.get('krypto', [])
            
            suma_krypto_usd = 0
            liczba_pozycji_krypto = len(krypto_lista)
            
            # Oblicz całkowitą wartość portfela krypto
            for k in krypto_lista:
                wartosc = k['ilosc'] * k['cena_zakupu_usd']
                suma_krypto_usd += wartosc
            
            print(f"  ✓ Krypto wczytane z krypto.json: {suma_krypto_usd:.2f} USD ({liczba_pozycji_krypto} pozycji)")
            
        except FileNotFoundError:
            print("  ⚠️ Plik krypto.json nie istnieje - używam wartości domyślnych")
            suma_krypto_usd = 0
            liczba_pozycji_krypto = 0
            krypto_lista = []
        except Exception as e:
            print(f"  ❌ Błąd wczytywania krypto.json: {e}")
            suma_krypto_usd = 0
            liczba_pozycji_krypto = 0
            krypto_lista = []
        
        # Aktualizuj stan spółki
        stan_spolki["PORTFEL_KRYPTO"] = {
            "Suma_USD": round(suma_krypto_usd, 2),
            "Suma_PLN": round(suma_krypto_usd * kurs_usd, 2),
            "Liczba_pozycji": liczba_pozycji_krypto,
            "pozycje": krypto_lista  # Dodajemy pełne dane pozycji dla AI
        }
        
        # ZOBOWIĄZANIA - Z LOKALNEGO PLIKU JSON
        print("  💳 Pobieram dane zobowiązań z lokalnego pliku...")
        try:
            with open('kredyty.json', 'r', encoding='utf-8') as f:
                kredyty_data = json.load(f)
                kredyty_lista = kredyty_data.get('kredyty', [])
            
            suma_dlugu_pln = 0
            suma_rat_pln = 0
            lista_kredytow = []
            
            for kredyt in kredyty_lista:
                # Oblicz pozostałą kwotę do spłaty
                pozostalo = kredyt['kwota_poczatkowa'] - kredyt.get('splacono', 0)
                suma_dlugu_pln += pozostalo
                suma_rat_pln += kredyt.get('rata_miesieczna', 0)
                
                lista_kredytow.append({
                    "Nazwa": kredyt['nazwa'],
                    "Typ": "Kredyt",
                    "Do_splaty_PLN": f"{pozostalo:.2f}",
                    "Rata_PLN": f"{kredyt.get('rata_miesieczna', 0):.2f}",
                    "Oprocentowanie": f"{kredyt.get('oprocentowanie', 0):.2f}%"
                })
            
            print(f"  ✓ Zobowiązania wczytane z kredyty.json: {suma_dlugu_pln:.2f} PLN ({len(kredyty_lista)} kredytów)")
            
        except FileNotFoundError:
            print("  ⚠️ Plik kredyty.json nie istnieje - używam wartości domyślnych")
            suma_dlugu_pln = 0
            suma_rat_pln = 0
            lista_kredytow = []
            kredyty_lista = []
        except Exception as e:
            print(f"  ❌ Błąd wczytywania kredyty.json: {e}")
            suma_dlugu_pln = 0
            suma_rat_pln = 0
            lista_kredytow = []
            kredyty_lista = []
        
        stan_spolki["ZOBOWIAZANIA"] = {
            "Suma_dlugow_PLN": round(suma_dlugu_pln, 2),
            "Suma_dlugow_USD": round(suma_dlugu_pln / kurs_usd, 2),
            "Suma_rat_miesiecznie_PLN": round(suma_rat_pln, 2),
            "Liczba_zobowiazan": len(kredyty_lista),
            "Lista_kredytow": lista_kredytow,
            "Szczegoly": kredyty_lista  # Pełne dane dla AI
        }
        
        # PRZYCHODY I WYDATKI - Z LOKALNYCH PLIKÓW JSON
        # PRZYCHODY I WYDATKI - Z LOKALNYCH PLIKÓW JSON
        print("  💵 Pobieram dane przychodów i wydatków z lokalnych plików...")
        try:
            # Wczytaj wypłaty
            with open('wyplaty.json', 'r', encoding='utf-8') as f:
                wyplaty_data = json.load(f)
                wyplaty_lista = wyplaty_data.get('wyplaty', [])
            
            # Wczytaj wydatki
            with open('wydatki.json', 'r', encoding='utf-8') as f:
                wydatki_data = json.load(f)
                wydatki_lista = wydatki_data.get('wydatki', [])
            
            # Oblicz sumy
            if wyplaty_lista:
                # Ostatnia wypłata (podstawa + premia w jednej kwocie)
                ostatnia_wyplata = wyplaty_lista[0]['kwota']
                
                # Średnia z ostatnich 3 wypłat
                ostatnie_3 = wyplaty_lista[:3]
                srednia_wyplata = sum(w['kwota'] for w in ostatnie_3) / len(ostatnie_3) if ostatnie_3 else 0
            else:
                ostatnia_wyplata = 0
                srednia_wyplata = 0
            
            # Suma wydatków stałych (nadprogramowy = false)
            wydatki_stale = sum(w['kwota'] for w in wydatki_lista if not w.get('nadprogramowy', False))
            
            # Suma wszystkich wydatków
            suma_wydatkow = sum(w['kwota'] for w in wydatki_lista)
            
            # Dostępne na inwestycje = Wypłata - Wydatki stałe - Raty kredytów
            dostepne_na_inwestycje = ostatnia_wyplata - wydatki_stale - suma_rat_pln
            
            print(f"  ✓ Przychody/Wydatki: Wypłata {ostatnia_wyplata:.2f} PLN, Wydatki {wydatki_stale:.2f} PLN, Dostępne {dostepne_na_inwestycje:.2f} PLN")
            
        except FileNotFoundError as e:
            print(f"  ⚠️ Brak pliku {e.filename} - używam wartości domyślnych")
            ostatnia_wyplata = 0
            srednia_wyplata = 0
            wydatki_stale = 0
            suma_wydatkow = 0
            dostepne_na_inwestycje = 0
        except Exception as e:
            print(f"  ❌ Błąd wczytywania danych finansowych: {e}")
            ostatnia_wyplata = 0
            srednia_wyplata = 0
            wydatki_stale = 0
            suma_wydatkow = 0
            dostepne_na_inwestycje = 0
        
        stan_spolki["PRZYCHODY_I_WYDATKI"] = {
            "Wynagrodzenie_PLN": round(ostatnia_wyplata, 2),  # Cała kwota (podstawa + premia)
            "Premia_PLN": 0,  # Nie rozdzielamy już
            "Suma_przychodow_PLN": round(ostatnia_wyplata, 2),
            "Suma_wydatkow_PLN": round(wydatki_stale, 2),  # Tylko stałe wydatki
            "Suma_wydatkow_wszystkich_PLN": round(suma_wydatkow, 2),  # Wszystkie (stałe + nadprogramowe)
            "Raty_kredytow_PLN": round(suma_rat_pln, 2),
            "Dostepne_na_inwestycje_PLN": round(dostepne_na_inwestycje, 2),
            "Dostepne_na_inwestycje_USD": round(dostepne_na_inwestycje / kurs_usd, 2),
            "Srednia_wyplata_3m_PLN": round(srednia_wyplata, 2)
        }
        print(f"  ✓ Cash Flow: {dostepne_na_inwestycje:.2f} PLN/mies. dostępne na inwestycje")
        
        # NOWOŚĆ: Pobieramy rezerwę gotówkową z przekazanych celów
        rezerwa_gotowkowa = cele.get("Rezerwa_gotowkowa_obecna_PLN", 0)
        
        # Obliczamy wartość portfeli (tak jak wcześniej)
        wartosc_portfeli_pln = stan_spolki["PORTFEL_AKCJI"]["Suma_PLN"] + (suma_krypto_usd * kurs_usd)
        
        # NOWOŚĆ: Obliczamy CAŁKOWITĄ wartość aktywów (portfele + gotówka)
        wartosc_calkowita_aktyw_pln = wartosc_portfeli_pln + rezerwa_gotowkowa
        
        # Wartość netto to aktywa minus długi
        wartosc_netto_pln = wartosc_calkowita_aktyw_pln - suma_dlugu_pln
        
        stan_spolki["PODSUMOWANIE"] = {
            "Gotowka_PLN": round(rezerwa_gotowkowa, 2), # Dodajemy dla przejrzystości
            "Wartosc_portfeli_PLN": round(wartosc_portfeli_pln, 2),
            "Wartosc_calkowita_aktyw_PLN": round(wartosc_calkowita_aktyw_pln, 2),
            "Zobowiazania_PLN": round(suma_dlugu_pln, 2),
            "Wartosc_netto_PLN": round(wartosc_netto_pln, 2),
            "Wartosc_netto_USD": round(wartosc_netto_pln / kurs_usd, 2),
            # POPRAWKA: Dzielimy przez sumę WSZYSTKICH aktywów
            "Leverage_ratio": round((suma_dlugu_pln / wartosc_calkowita_aktyw_pln * 100), 2) if wartosc_calkowita_aktyw_pln > 0 else 0
        }
        
        print_colored("\n✓ Wszystkie dane pomyślnie zaktualizowane!", "\033[92m")
        
        return stan_spolki
        
    except Exception as e:
        print_colored(f"KRYTYCZNY BŁĄD podczas pobierania danych: {e}", "\033[91m")
        import traceback
        traceback.print_exc()
        return None

def display_status(stan_spolki, cele):
    """Wyświetla szczegółowy status finansowy spółki."""
    if not stan_spolki:
        print_colored("Nie udało się pobrać stanu spółki.", "\033[91m")
        return
    
    print_colored("\n" + "="*80, "\033[93m")
    print_colored("💼 RAPORT FINANSOWY SPÓŁKI 'HORYZONT PARTNERÓW'", "\033[93m")
    print_colored("="*80, "\033[93m")
    
    if "PODSUMOWANIE" in stan_spolki:
        p = stan_spolki["PODSUMOWANIE"]
        print_colored("\n📊 PODSUMOWANIE GŁÓWNE:", "\033[96m")
        print(f"  Wartość netto:               {p['Wartosc_netto_PLN']:>15,.2f} PLN")
        print(f"  Leverage:                    {p['Leverage_ratio']:>15.2f} %")
    
    if "PORTFEL_AKCJI" in stan_spolki:
        a = stan_spolki["PORTFEL_AKCJI"]
        print_colored("\n📈 PORTFEL AKCJI (Trading212):", "\033[96m")
        print(f"  Wartość:                     {a['Suma_PLN']:>15,.2f} PLN ({a['Suma_USD']:,.2f} USD)")
        print(f"  Liczba pozycji:              {a.get('Liczba_pozycji_calkowita', a.get('Liczba_pozycji', 'N/A')):>15}")
    
    if "PORTFEL_KRYPTO" in stan_spolki:
        k = stan_spolki["PORTFEL_KRYPTO"]
        print_colored("\n💰 PORTFEL KRYPTO:", "\033[96m")
        print(f"  Wartość:                     {k['Suma_PLN']:>15,.2f} PLN ({k['Suma_USD']:,.2f} USD)")
        print(f"  Liczba pozycji:              {k['Liczba_pozycji']:>15}")
    
    if "ZOBOWIAZANIA" in stan_spolki:
        z = stan_spolki["ZOBOWIAZANIA"]
        print_colored("\n💳 ZOBOWIĄZANIA:", "\033[96m")
        print(f"  Suma długów:                 {z['Suma_dlugow_PLN']:>15,.2f} PLN")
        print(f"  Raty miesięczne:             {z['Suma_rat_miesiecznie_PLN']:>15,.2f} PLN")
        print(f"  Liczba kredytów:             {z['Liczba_zobowiazan']:>15}")
    
    if "PRZYCHODY_I_WYDATKI" in stan_spolki:
        w = stan_spolki["PRZYCHODY_I_WYDATKI"]
        print_colored("\n💵 CASH FLOW MIESIĘCZNY:", "\033[96m")
        print(f"  Przychody:                   {w['Suma_przychodow_PLN']:>15,.2f} PLN")
        print(f"  Wydatki stałe:               {w['Suma_wydatkow_PLN']:>15,.2f} PLN")
        print(f"  Raty kredytów:               {w['Raty_kredytow_PLN']:>15,.2f} PLN")
        print_colored(f"  💎 Dostępne na inwestycje:   {w['Dostepne_na_inwestycje_PLN']:>15,.2f} PLN", "\033[92m")
    
    # PROGRESS BARS
    wyswietl_progress_bars(stan_spolki, cele)
    
    # FIRE CALCULATOR (zwięzła wersja)
    wyswietl_fire_calculator(stan_spolki, cele, pelny=False)
    
    if "Kurs_USD_PLN" in stan_spolki:
        print_colored(f"\n💱 Kurs USD/PLN: {stan_spolki['Kurs_USD_PLN']:.4f} PLN (źródło: NBP)", "\033[90m")
    
    print_colored("="*80 + "\n", "\033[93m")

def main():
    global tryb_odpowiedzi, fight_club_enabled
    clear_screen()
    
    global last_responses
    
    # Sprawdź czy nowy miesiąc i czy trzeba raport
    nowy_miesiac, poprzedni_snapshot = sprawdz_nowy_miesiac()
    
    STAN_SPOLKI = pobierz_stan_spolki(CELE)
    if not STAN_SPOLKI:
        return
    
    # Jeśli nowy miesiąc, generuj raport
    if nowy_miesiac and poprzedni_snapshot:
        generuj_raport_miesieczny(STAN_SPOLKI, poprzedni_snapshot, CELE)
    
    # Zapisz snapshot na początek tego miesiąca (dla przyszłego raportu)
    zapisz_monthly_snapshot(STAN_SPOLKI)
    
    # NOWY: Automatyczne sprawdzenie compliance raz dziennie
    sprawdz_compliance_auto(pobierz_dane_trading212() if TRADING212_ENABLED else None)
    
    print_colored("\n🏢 WITAMY NA POSIEDZENIU ZARZĄDU SPÓŁKI 'HORYZONT PARTNERÓW'", "\033[96m")
    print_colored("📜 Działamy zgodnie z Kodeksem Spółki ratyfikowanym 1 października 2025", "\033[93m")
    display_status(STAN_SPOLKI, CELE)
    
    print_colored("📋 Dostępne Komendy:", "\033[92m")
    print("  - `Nazwa: Wiadomość` | `wszyscy: Wiadomość` | `reakcja: Opis`")
    print("  - `wszyscy --krotko: Wiadomość` (wymusza krótkie odpowiedzi)")
    print("  - `wszyscy --szczegolowo: Wiadomość` (wymusza długie analizy)")
    print("  - `tryb: zwiezly/normalny/szczegolowy` (zmień domyślny tryb)")
    print("  - `fightclub: on/off` (włącz/wyłącz konflikty między Partnerami)")
    print("  - `glosowanie: Treść propozycji` (Oficjalne głosowanie Partnerów)")
    print("  - `doradz: Twoje pytanie` (AI Advisor - 3 scenariusze)")
    print("  - `doradz --z-partnerami: Pytanie` (+ komentarze Partnerów)")
    print("  - `tracking` (Ręczne śledzenie protokołów z Kodeksu)")
    print("  - `status` (Odśwież Stan Finansowy + Progress Bars)")
    print("  - `dywidendy` (Szczegółowa analiza portfela dywidendowego)")
    print("  - `analiza` (Pełna analiza portfela i rekomendacje AI)")
    print("  - `dashboard` (Statystyki spotkania)")
    print("  - `symulacja` (Symulator portfela - testuj scenariusze)")
    print("  - `raport` (Generuj raport Excel)")
    print("  - `ryzyko` (📊 Analiza ryzyka: Sharpe, VaR, Max Drawdown)")
    print("  - `timeline` (🕐 Animated timeline portfela)")
    print("  - `zapisz nazwa_sesji` | `wczytaj nazwa_sesji`")
    print("  - `wyjscie` (Zakończ i pokaż podsumowanie)")
    print(f"  📊 Tryb odpowiedzi: {tryb_odpowiedzi.upper()} | 🥊 Fight Club: {'ON' if fight_club_enabled else 'OFF'}")
    print("-" * 80)

    while True:
        try:
            prompt = input("\033[97m💼 Partner Zarządzający (JA): \033[0m")
            save_to_chronicle("Partner Zarządzający (JA)", prompt)

            if prompt.lower() == 'wyjscie':
                print_colored("\n👋 Zakończono posiedzenie Zarządu.", "\033[96m")
                generate_dashboard()
                
                odpowiedz = input("\n💾 Czy chcesz zapisać protokół z tego spotkania? (tak/nie): ").lower()
                if odpowiedz in ['tak', 't', 'yes', 'y']:
                    nazwa = input("Podaj nazwę sesji: ").strip()
                    if nazwa:
                        save_session(nazwa, STAN_SPOLKI, last_responses)
                
                print_colored("Protokół zapisany w: " + NAZWA_KRONIKI, "\033[93m")
                break
            
            elif prompt.lower() == 'status':
                STAN_SPOLKI = pobierz_stan_spolki(CELE)
                display_status(STAN_SPOLKI, CELE)
                # Zapisz snapshot do historii
                portfolio_history.save_snapshot(STAN_SPOLKI)
                continue
            
            elif prompt.lower() == 'ryzyko':
                print_colored("\n📊 ANALIZA RYZYKA PORTFELA", "\033[96m")
                print("-" * 80)
                
                # Pobierz historię
                history = portfolio_history.get_history()
                
                if len(history) < 2:
                    print_colored("⚠️ Za mało danych historycznych (minimum 2 snapshoty)", "\033[93m")
                    print("Uruchom program kilka razy aby zgromadzić dane.")
                else:
                    # Utwórz analyzer
                    analyzer = RiskAnalytics(STAN_SPOLKI, history)
                    
                    # Generuj raport
                    report = analyzer.generate_risk_report()
                    metrics = report.get('metrics', {})
                    
                    # Wyświetl metryki
                    print_colored("\n🎯 KLUCZOWE METRYKI:", "\033[92m")
                    
                    if 'sharpe_ratio' in metrics:
                        sharpe = metrics['sharpe_ratio']
                        color = "\033[92m" if sharpe > 1 else "\033[93m" if sharpe > 0.5 else "\033[91m"
                        print(f"  Sharpe Ratio: {color}{sharpe:.3f}\033[0m (>1 = dobre, >2 = doskonałe)")
                    
                    if 'sortino_ratio' in metrics:
                        sortino = metrics['sortino_ratio']
                        color = "\033[92m" if sortino > 1.5 else "\033[93m"
                        print(f"  Sortino Ratio: {color}{sortino:.3f}\033[0m (uwzględnia tylko straty)")
                    
                    if 'max_drawdown_percent' in metrics:
                        max_dd = metrics['max_drawdown_percent']
                        color = "\033[92m" if max_dd < 10 else "\033[93m" if max_dd < 20 else "\033[91m"
                        print(f"  Max Drawdown: {color}{max_dd:.2f}%\033[0m (największy spadek)")
                    
                    if 'var_95' in metrics:
                        var_95 = metrics['var_95']
                        color = "\033[92m" if var_95 < 5 else "\033[93m" if var_95 < 10 else "\033[91m"
                        print(f"  VaR (95%): {color}{var_95:.2f}%\033[0m (max strata z 95% pewnością)")
                    
                    if 'annual_volatility_percent' in metrics:
                        vol = metrics['annual_volatility_percent']
                        color = "\033[92m" if vol < 20 else "\033[93m" if vol < 30 else "\033[91m"
                        print(f"  Zmienność roczna: {color}{vol:.2f}%\033[0m")
                    
                    if 'total_return_percent' in metrics:
                        ret = metrics['total_return_percent']
                        color = "\033[92m" if ret > 0 else "\033[91m"
                        print(f"  Całkowity zwrot: {color}{ret:+.2f}%\033[0m")
                    
                    # Ogólny risk score
                    print_colored("\n🎲 OCENA RYZYKA:", "\033[96m")
                    level, score, description = analyzer.risk_score()
                    score_color = "\033[92m" if score >= 70 else "\033[93m" if score >= 50 else "\033[91m"
                    print(f"  Poziom: {score_color}{level}\033[0m")
                    print(f"  Score: {score_color}{score}/100\033[0m")
                    print(f"  {description}")
                
                print("-" * 80)
                continue
            
            elif prompt.lower() == 'timeline':
                print_colored("\n🕐 GENEROWANIE ANIMATED TIMELINE...", "\033[96m")
                
                # Pobierz historię
                history = portfolio_history.get_history()
                
                if len(history) < 2:
                    print_colored("⚠️ Za mało danych historycznych", "\033[93m")
                    print("Uruchom program kilka razy aby zgromadzić dane.")
                else:
                    try:
                        display_timeline(history, open_browser=True)
                        print_colored("✅ Timeline wygenerowany i otwarty w przeglądarce!", "\033[92m")
                    except Exception as e:
                        print_colored(f"❌ Błąd: {e}", "\033[91m")
                        import traceback
                        traceback.print_exc()
                
                continue
            
            elif prompt.lower() == 'raport':
                if EXCEL_AVAILABLE:
                    print_colored("📄 Generuję raport Excel...", "\033[96m")
                    filename = generate_full_report(STAN_SPOLKI)
                    if filename:
                        print_colored(f"✅ Raport zapisany: {filename}", "\033[92m")
                    else:
                        print_colored("❌ Błąd przy generowaniu raportu", "\033[91m")
                else:
                    print_colored("⚠️ Pakiet openpyxl nie jest zainstalowany.", "\033[93m")
                    print("Zainstaluj: pip install openpyxl")
                continue
            
            elif prompt.lower() == 'symulacja':
                print_colored("\n🎮 SYMULATOR PORTFELA - Analiza Scenariuszy", "\033[96m")
                print("Dostępne komendy:")
                print("  1. kupuj: ticker, ilość, cena  - Kupowanie papieru wartościowego")
                print("  2. sprzedaj: ticker, ilość, cena  - Sprzedaż papieru wartościowego")
                print("  3. bullish  - Scenariusz wzrostu (wszystkie aktywa +20%)")
                print("  4. bearish  - Scenariusz spadku (wszystkie aktywa -20%)")
                print("  5. dywidendy  - Scenariusz wzrostu z dywidend")
                print("  6. porównaj  - Porównaj scenariusze")
                print("  7. pokaż  - Pokaż wpływ zmian")
                print("  8. reset  - Resetuj symulację")
                print("  9. wróć  - Powrót do głównego menu")
                print("-" * 60)
                
                simulator = PortfolioSimulator(STAN_SPOLKI)
                
                while True:
                    sim_prompt = input("\n🎮 Symulator: ").lower().strip()
                    
                    if sim_prompt == 'wróć':
                        break
                    
                    elif sim_prompt.startswith('kupuj:'):
                        try:
                            parts = sim_prompt[6:].split(',')
                            ticker = parts[0].strip()
                            quantity = float(parts[1].strip())
                            price = float(parts[2].strip())
                            
                            transaction = simulator.add_transaction('stock', ticker, quantity, price, 'buy')
                            print_colored(f"✅ Zakupiono {quantity} x {ticker} po {price} PLN", "\033[92m")
                        except Exception as e:
                            print_colored(f"❌ Błąd: {e}", "\033[91m")
                    
                    elif sim_prompt.startswith('sprzedaj:'):
                        try:
                            parts = sim_prompt[9:].split(',')
                            ticker = parts[0].strip()
                            quantity = float(parts[1].strip())
                            price = float(parts[2].strip())
                            
                            transaction = simulator.add_transaction('stock', ticker, quantity, price, 'sell')
                            print_colored(f"✅ Sprzedano {quantity} x {ticker} po {price} PLN", "\033[92m")
                        except Exception as e:
                            print_colored(f"❌ Błąd: {e}", "\033[91m")
                    
                    elif sim_prompt == 'bullish':
                        simulator = ScenarioAnalyzer.create_bullish_scenario(STAN_SPOLKI, 20)
                        print_colored("🚀 Zastosowano scenariusz BULLISH (+20% dla wszystkich aktywów)", "\033[92m")
                    
                    elif sim_prompt == 'bearish':
                        simulator = ScenarioAnalyzer.create_bearish_scenario(STAN_SPOLKI, 20)
                        print_colored("📉 Zastosowano scenariusz BEARISH (-20% dla wszystkich aktywów)", "\033[91m")
                    
                    elif sim_prompt == 'dywidendy':
                        simulator = ScenarioAnalyzer.create_dividend_scenario(STAN_SPOLKI, 5)
                        print_colored("💰 Zastosowano scenariusz DYWIDENDY (+5% z tytułu dywidend)", "\033[92m")
                    
                    elif sim_prompt == 'pokaż':
                        impact = simulator.calculate_impact()
                        print_colored("\n📊 WPŁYW SCENARIUSZA", "\033[96m")
                        print(f"  Oryginalna wartość: {impact['original_value_pln']:,.2f} PLN")
                        print(f"  Symulowana wartość: {impact['simulated_value_pln']:,.2f} PLN")
                        print(f"  Zmiana bezwzględna: {impact['absolute_change_pln']:+,.2f} PLN")
                        print(f"  Zmiana procentowa: {impact['percentage_change']:+.2f}%")
                        print(f"  Liczba transakcji: {impact['transactions_count']}")
                        
                        recommendations = simulator.get_recommendations()
                        print_colored("\n💡 REKOMENDACJE:", "\033[93m")
                        for rec in recommendations:
                            print(f"  {rec['type']} {rec['message']}")
                    
                    elif sim_prompt == 'reset':
                        simulator.reset_to_original()
                        print_colored("🔄 Scenariusz zresetowany do oryginalnego portfela", "\033[93m")
                    
                    else:
                        print_colored("❌ Nieznana komenda. Wpisz 'wróć' aby wrócić do menu", "\033[91m")
                
                continue
            
            elif prompt.lower() == 'tracking':
                tracking_protokolow()
                continue
            
            elif prompt.lower().startswith('doradz'):
                # Sprawdź czy z Partnerami
                z_partnerami = '--z-partnerami' in prompt.lower()
                
                if z_partnerami:
                    pytanie = prompt.split(':', 1)[1].strip() if ':' in prompt else ""
                else:
                    pytanie = prompt[7:].strip() if len(prompt) > 7 else ""
                
                if not pytanie:
                    print_colored("❌ Podaj pytanie: doradz: treść pytania", "\033[91m")
                    continue
                
                ai_advisor(pytanie, STAN_SPOLKI, CELE, z_partnerami=z_partnerami)
                continue
            
            elif prompt.lower().startswith('tryb:'):
                nowy_tryb = prompt[5:].strip().lower()
                if nowy_tryb in ['zwiezly', 'normalny', 'szczegolowy']:
                    tryb_odpowiedzi = nowy_tryb
                    print_colored(f"✅ Zmieniono tryb odpowiedzi na: {nowy_tryb.upper()}", "\033[92m")
                    if nowy_tryb == "zwiezly":
                        print_colored("   Partnerzy będą odpowiadać zwięźle (3-4 zdania)", "\033[93m")
                    elif nowy_tryb == "normalny":
                        print_colored("   Partnerzy będą odpowiadać standardowo (5-7 zdań)", "\033[93m")
                    else:
                        print_colored("   Partnerzy będą odpowiadać szczegółowo (pełna analiza)", "\033[93m")
                else:
                    print_colored("❌ Dostępne tryby: zwiezly, normalny, szczegolowy", "\033[91m")
                continue
            
            elif prompt.lower().startswith('fightclub:'):
                nowy_stan = prompt[11:].strip().lower()
                if nowy_stan in ['on', 'off']:
                    fight_club_enabled = (nowy_stan == 'on')
                    if fight_club_enabled:
                        print_colored("🥊 Financial Fight Club WŁĄCZONY!", "\033[91m")
                        print_colored("   Partnerzy mogą się teraz kłócić i nie zgadzać!", "\033[93m")
                    else:
                        print_colored("😇 Financial Fight Club wyłączony.", "\033[92m")
                        print_colored("   Partnerzy wrócili do grzecznych odpowiedzi.", "\033[93m")
                else:
                    print_colored("❌ Użyj: fightclub: on lub fightclub: off", "\033[91m")
                continue
            
            elif prompt.lower() == 'dywidendy':
                STAN_SPOLKI = pobierz_stan_spolki(CELE)
                if "PORTFEL_AKCJI" in STAN_SPOLKI:
                    wyswietl_analize_dywidend(STAN_SPOLKI["PORTFEL_AKCJI"])
                else:
                    print_colored("❌ Brak danych o portfelu akcji.", "\033[91m")
                continue
                
            elif prompt.lower() == 'fire':
                wyswietl_fire_calculator(STAN_SPOLKI, CELE, pelny=True)
                continue
            
            elif prompt.lower().startswith('ustawwiek '):
                try:
                    wiek = int(prompt[11:].strip())
                    if 15 <= wiek <= 100:
                        CELE["wiek_uzytkownika"] = wiek
                        # Zapisz do pliku
                        with open(NAZWA_PLIKU_CELOW, 'w', encoding='utf-8') as f:
                            json.dump(CELE, f, indent=2, ensure_ascii=False)
                        print_colored(f"✅ Ustawiono wiek: {wiek} lat", "\033[92m")
                    else:
                        print_colored("❌ Wiek musi być między 15 a 100", "\033[91m")
                except ValueError:
                    print_colored("❌ Użyj: ustawwiek [liczba], np. ustawwiek 28", "\033[91m")
                continue
            
            elif prompt.lower().startswith('ustawwydatki '):
                try:
                    wydatki = float(prompt[14:].strip())
                    if wydatki > 0:
                        CELE["miesieczne_wydatki_fi"] = wydatki
                        # Zapisz do pliku
                        with open(NAZWA_PLIKU_CELOW, 'w', encoding='utf-8') as f:
                            json.dump(CELE, f, indent=2, ensure_ascii=False)
                        print_colored(f"✅ Ustawiono wydatki: {wydatki:,.2f} PLN/mies", "\033[92m")
                        print_colored("   (Domyślnie używane są wydatki z arkusza)", "\033[93m")
                    else:
                        print_colored("❌ Wydatki muszą być > 0", "\033[91m")
                except ValueError:
                    print_colored("❌ Użyj: ustawwydatki [kwota], np. ustawwydatki 2600", "\033[91m")
                continue
            
            elif prompt.lower() == 'dashboard':
                generate_dashboard()
                wyswietl_dashboard(STAN_SPOLKI)  # Dodajemy nowe wykresy
                continue
                
            elif prompt.lower() == 'analiza':
                print_colored("\n🔍 Rozpoczynam pełną analizę portfela...", "\033[96m")
                try:
                    statystyki, rekomendacje = przeprowadz_analize_portfela(STAN_SPOLKI)
                    wyswietl_raport_analizy(statystyki, rekomendacje)
                    
                    # Przekaż analizę do doradców AI
                    ai_pytanie = ("Na podstawie przeprowadzonej analizy portfela, "
                                "jakie są Twoje dodatkowe rekomendacje i sugestie? "
                                "Uwzględnij obecną sytuację rynkową i długoterminowe cele spółki.")
                    
                    # Użyj istniejącego systemu doradztwa AI
                    ai_advisor(ai_pytanie, STAN_SPOLKI, CELE, z_partnerami=True)
                except Exception as e:
                    print_colored(f"\n❌ Błąd podczas analizy: {str(e)}", "\033[91m")
                continue

            elif prompt.lower().startswith('rezerwa '):
                try:
                    kwota_str = prompt[8:].strip()
                    kwota = float(kwota_str)
                    
                    if kwota >= 0:
                        CELE["Rezerwa_gotowkowa_obecna_PLN"] = kwota
                        # Zapisz zmianę do pliku
                        with open(NAZWA_PLIKU_CELOW, 'w', encoding='utf-8') as f:
                            json.dump(CELE, f, indent=2, ensure_ascii=False)
                        print_colored(f"✅ Zaktualizowano rezerwę gotówkową na: {kwota:,.2f} PLN", "\033[92m")
                        # Odśwież widok, żeby zobaczyć zmiany
                        display_status(STAN_SPOLKI, CELE)
                    else:
                        print_colored("❌ Kwota rezerwy nie może być ujemna.", "\033[91m")
                except ValueError:
                    print_colored("❌ Błędny format. Użyj: rezerwa [kwota], np. rezerwa 15000", "\033[91m")
                continue
            
            elif prompt.lower().startswith('glosowanie:'):
                propozycja = prompt[11:].strip()
                if not propozycja:
                    print_colored("❌ Podaj treść propozycji: glosowanie: treść", "\033[91m")
                    continue
                
                inicjuj_glosowanie(propozycja, PERSONAS)
                
                STAN_SPOLKI_ODSWIEZONY = pobierz_stan_spolki(CELE)
                if not STAN_SPOLKI_ODSWIEZONY:
                    print_colored("❌ Błąd pobierania danych. Anulowano głosowanie.", "\033[91m")
                    aktywne_glosowanie = None
                    continue

                stan_spolki_str = json.dumps(STAN_SPOLKI_ODSWIEZONY, indent=2, ensure_ascii=False)
                
                glosujacy_partnerzy = [
                    "Partner Strategiczny",
                    "Partner ds. Jakości Biznesowej", 
                    "Partner ds. Aktywów Cyfrowych"
                ]
                
                for persona_name in glosujacy_partnerzy:
                    if persona_name not in PERSONAS:
                        continue
                    
                    time.sleep(0.5)
                    
                    prompt_glosowanie = f"""

{PERSONAS[persona_name]['system_instruction']}

KODEKS SPÓŁKI "HORYZONT PARTNERÓW":
{KODEKS_SPOLKI}

---
Twoim tajnym celem jest: {PERSONAS[persona_name]['ukryty_cel']}
---
AKTUALNY STAN FINANSOWY SPÓŁKI:
{stan_spolki_str}
---
🗳️ OFICJALNE GŁOSOWANIE ZARZĄDU

Propozycja do głosowania: "{propozycja}"

TWOJE ZADANIE:
1. Przeanalizuj propozycję w kontekście Kodeksu Spółki, stanu finansowego i Twojego celu
2. Oddaj swój głos: TAK lub NIE
3. Krótko uzasadnij swoją decyzję (2-3 zdania)

FORMAT ODPOWIEDZI:
GŁOS: [TAK/NIE]
UZASADNIENIE: [Twoje uzasadnienie]

Pamiętaj: Posiadasz {aktywne_glosowanie['udzialy'].get(persona_name, 0)}% głosów w Zarządzie zgodnie z Artykułem II §1 Kodeksu.
"""
                    
                    response_text = generuj_odpowiedz_ai(persona_name, prompt_glosowanie)
                    
                    glos = "NIE"
                    uzasadnienie = response_text
                    
                    if "GŁOS:" in response_text.upper():
                        lines = response_text.split('\n')
                        for line in lines:
                            if "GŁOS:" in line.upper():
                                if "TAK" in line.upper():
                                    glos = "TAK"
                                else:
                                    glos = "NIE"
                            elif "UZASADNIENIE:" in line.upper():
                                uzasadnienie = line.split(':', 1)[1].strip() if ':' in line else response_text
                    
                    oddaj_glos(persona_name, glos, uzasadnienie)
                    last_responses[persona_name] = response_text
                    save_to_chronicle(persona_name, f"[GŁOSOWANIE] {response_text}")
                
                print_colored(f"\n💼 Partner Zarządzający (JA) - Twój głos (35%):", "\033[96m")
                twoj_glos = input("Twój głos (TAK/NIE): ").strip().upper()
                while twoj_glos not in ['TAK', 'NIE']:
                    twoj_glos = input("Wpisz TAK lub NIE: ").strip().upper()
                
                uzasadnienie_twoje = input("Krótkie uzasadnienie (opcjonalne): ").strip()
                oddaj_glos("Partner Zarządzający (JA)", twoj_glos, uzasadnienie_twoje)
                
                podsumuj_glosowanie()
                continue
            
            elif prompt.lower().startswith('zapisz '):
                nazwa_sesji = prompt[7:].strip()
                if nazwa_sesji:
                    save_session(nazwa_sesji, STAN_SPOLKI, last_responses)
                else:
                    print_colored("❌ Podaj nazwę sesji", "\033[91m")
                continue
            
            elif prompt.lower().startswith('wczytaj '):
                nazwa_sesji = prompt[8:].strip()
                if nazwa_sesji:
                    session_data = load_session(nazwa_sesji)
                    if session_data:
                        STAN_SPOLKI = session_data.get('stan_spolki', STAN_SPOLKI)
                        last_responses = session_data.get('last_responses', last_responses)
                        print_colored("\n✅ Sesja przywrócona!", "\033[92m")
                        display_status(STAN_SPOLKI, CELE)
                else:
                    print_colored("❌ Podaj nazwę sesji", "\033[91m")
                continue

            target_personas, user_message, is_reaction = [], "", False
            
            # Sprawdź flagi --krotko i --szczegolowo
            force_short = '--krotko' in prompt.lower()
            force_detailed = '--szczegolowo' in prompt.lower()
            
            # Tymczasowo zmień tryb jeśli flag
            old_tryb = tryb_odpowiedzi
            if force_short:
                tryb_odpowiedzi = "zwiezly"
                prompt = prompt.replace('--krotko', '').replace('--krótko', '')
            elif force_detailed:
                tryb_odpowiedzi = "szczegolowy"
                prompt = prompt.replace('--szczegolowo', '').replace('--szczegółowo', '')
            
            if prompt.lower().startswith('reakcja:'):
                user_message, target_personas, is_reaction = prompt[len('reakcja:'):].strip(), list(PERSONAS.keys()), True
            elif prompt.lower().startswith('wszyscy:'):
                user_message, target_personas = prompt[len('wszyscy:'):].strip(), list(PERSONAS.keys())
            else:
                for name in PERSONAS:
                    if prompt.lower().startswith(f"{name.lower()}:"):
                        user_message, target_personas = prompt[len(name)+1:].strip(), [name]
                        break
            
            if not target_personas:
                print_colored("❌ Nie rozpoznano komendy. Sprawdź format.", "\033[91m")
                continue

            STAN_SPOLKI_ODSWIEZONY = pobierz_stan_spolki(CELE)
            if not STAN_SPOLKI_ODSWIEZONY:
                print_colored("❌ Przerwano akcję z powodu błędu pobierania danych.", "\033[91m")
                continue

            stan_spolki_kompaktowy = {
                "PODSUMOWANIE": STAN_SPOLKI_ODSWIEZONY.get("PODSUMOWANIE", {}),
                "PORTFEL_AKCJI_summary": {
                    "Suma_PLN": STAN_SPOLKI_ODSWIEZONY.get("PORTFEL_AKCJI", {}).get("Suma_PLN"),
                    "Liczba_pozycji_rdzennych": STAN_SPOLKI_ODSWIEZONY.get("PORTFEL_AKCJI", {}).get("Liczba_pozycji_rdzennych"),
                    "Opis_pozycji_rdzennych": "Pozycje zarządzane indywidualnie, podlegające pełnej analizie.",
                    "Zewnetrzne_Strategie_Pie": {
                        "Almost_Daily_Dividends": {
                            "liczba_akcji": STAN_SPOLKI_ODSWIEZONY.get("PORTFEL_AKCJI", {}).get("Liczba_pozycji_w_pie"),
                            "opis": "Zarządzane zewnętrznie, traktowane jako jedna pozycja strategiczna. Nie analizować pojedynczych spółek."
                        }
                    }
                },
                "PORTFEL_KRYPTO_summary": STAN_SPOLKI_ODSWIEZONY.get("PORTFEL_KRYPTO", {}),
                "ZOBOWIAZANIA_summary": STAN_SPOLKI_ODSWIEZONY.get("ZOBOWIAZANIA", {}),
                "PRZYCHODY_I_WYDATKI": STAN_SPOLKI_ODSWIEZONY.get("PRZYCHODY_I_WYDATKI", {})
            }
            stan_spolki_str = json.dumps(stan_spolki_kompaktowy, indent=2, ensure_ascii=False)

            # NOWY: Stworzenie analizy rynkowej jako string
            analiza_rynkowa_str = "\n\nDANE RYNKOWE (wybrane pozycje):\n"
            dane_rynkowe = STAN_SPOLKI_ODSWIEZONY.get("PORTFEL_AKCJI", {}).get("Dane_rynkowe", {})
            if dane_rynkowe:
                for ticker, dane in list(dane_rynkowe.items())[:10]: # Pokaż do 10 pierwszych
                    pe_str = f"P/E: {dane.get('PE', 'N/A'):.1f}" if dane.get('PE') else "P/E: N/A"
                    dywidenda_str = f"Dywidenda: {dane.get('dywidenda_roczna', 0) * 100:.1f}%" if dane.get('dywidenda_roczna') else "Dywidenda: N/A"
                    analiza_rynkowa_str += f"- {dane.get('nazwa', ticker)} ({ticker}): {pe_str}, {dywidenda_str}\n"
            else:
                analiza_rynkowa_str += "Brak dostępnych danych rynkowych.\n"

            stan_spolki_str += analiza_rynkowa_str
            
            # Pobierz szczegóły pozycji
            pozycje_szczegoly = STAN_SPOLKI_ODSWIEZONY['PORTFEL_AKCJI'].get('Pozycje_szczegoly', {})
            
            # Przygotuj sekcję szczegółów pozycji posortowaną według wartości
            sorted_pozycje = sorted(
                pozycje_szczegoly.items(), 
                key=lambda x: x[1]['wartosc_total_usd'], 
                reverse=True
            )

            dodatek_szczegoly = "\n\nDOSTĘPNE SZCZEGÓŁOWE DANE:\n"
            dodatek_szczegoly += f"- Szczegółowa tabela akcji: {STAN_SPOLKI_ODSWIEZONY['PORTFEL_AKCJI'].get('Liczba_pozycji_calkowita', STAN_SPOLKI_ODSWIEZONY['PORTFEL_AKCJI'].get('Liczba_pozycji', 'N/A'))} pozycji\n"
            dodatek_szczegoly += f"- Szczegółowa tabela krypto: {STAN_SPOLKI_ODSWIEZONY['PORTFEL_KRYPTO']['Liczba_pozycji']} pozycji\n"
            dodatek_szczegoly += f"- Lista kredytów: {len(STAN_SPOLKI_ODSWIEZONY['ZOBOWIAZANIA']['Lista_kredytow'])} zobowiązań\n\n"
            
            dodatek_szczegoly += "SZCZEGÓŁY WSZYSTKICH POZYCJI W PORTFELU (TOP 10 wg wartości):\n"
            for ticker, dane in sorted_pozycje[:10]:
                dodatek_szczegoly += f"- {ticker}:\n"
                dodatek_szczegoly += f"  * Ilość: {dane['ilosc']:.2f} akcji\n"
                dodatek_szczegoly += f"  * Wartość całkowita: ${dane['wartosc_total_usd']:.2f} (${dane['wartosc_obecna_usd']:.2f}/akcję)\n"
                dodatek_szczegoly += f"  * Koszt zakupu: ${dane['koszt_total_usd']:.2f} (${dane['cena_zakupu_usd']:.2f}/akcję)\n"
                dodatek_szczegoly += f"  * Zysk/Strata: ${dane['zysk_total_usd']:.2f} ({dane['zmiana_proc']:.1f}%)\n"

            dodatek_szczegoly += f"\nKONTEKST SKALI: To są prywatne finanse osoby fizycznej. Dostępny kapitał: ~{STAN_SPOLKI_ODSWIEZONY['PRZYCHODY_I_WYDATKI']['Dostepne_na_inwestycje_PLN']:.2f} PLN/mies.\n"""

            spontaneous_reactors = check_spontaneous_reaction(
                user_message, target_personas, PERSONAS, last_responses
            )
            
            all_responders = target_personas + spontaneous_reactors
            
            # NOWY: Fight Club Mode - odpowiedzi w 2 rundach jeśli kontrowersyjne
            is_controversial = analyze_potential_conflict(user_message, PERSONAS) if fight_club_enabled else False
            
            first_round_responses = {}

            gemini_request_count = 0
            for i, persona_name in enumerate(all_responders):
                if i > 0:
                    time.sleep(1) # Zwiększamy standardowe opóźnienie

                reaction_context = ""
                if is_reaction:
                    reaction_context = f"\n(Kontekst: Ostatnie wypowiedzi innych Partnerów:\n"
                    for other_name, last_msg in last_responses.items():
                        if other_name != persona_name:
                            reaction_context += f"- {other_name}: {last_msg}\n"
                    reaction_context += ")"
                
                is_spontaneous = persona_name in spontaneous_reactors
                spontaneous_note = "\n\n[UWAGA: To spontaniczna reakcja. Bądź naturalny/a ale zwięzły/a]" if is_spontaneous else ""
                
                # Instrukcja długości odpowiedzi
                length_instruction = get_response_length_instruction(is_spontaneous)

                final_prompt = (
                    f"{PERSONAS[persona_name]['system_instruction']}\n\n"
                    f'KODEKS SPÓŁKI "HORYZONT PARTNERÓW":\n'
                    f"{KODEKS_SPOLKI}\n\n"
                    "---\n"
                    f"Twoim tajnym celem jest: {PERSONAS[persona_name]['ukryty_cel']}\n"
                    "---\n"
                    "AKTUALNY PEŁNY STAN FINANSOWY SPÓŁKI:\n"
                    f"{stan_spolki_str}\n"
                    f"{dodatek_szczegoly}\n"
                    "---\n"
                    f"{reaction_context}\n"
                    "---\n"
                    f"{length_instruction}\n"
                    "---\n"
                    'TWOJE ZADANIE: Odpowiedz jako członek Zarządu spółki inwestycyjnej:\n'
                    f'"{user_message}"{spontaneous_note}\n\n'
                    "WSKAZÓWKI:\n"
                    '- Odwołuj się do Kodeksu gdy stosowne (np. "Zgodnie z Artykułem IV §1...")\n'
                    "- Analizuj konkretne liczby\n"
                    "- Ton profesjonalny ale nie przesadnie korporacyjny"
                )
                
                response_text = generuj_odpowiedz_ai(persona_name, final_prompt)
                
                first_round_responses[persona_name] = response_text
                last_responses[persona_name] = response_text
                save_to_chronicle(persona_name, response_text)
                
                prefix = "💬 [SPONTANICZNE] " if is_spontaneous else ""
                print_colored(f"\n{prefix}[{persona_name}]:", PERSONAS[persona_name]['color_code'])
                print_colored(response_text, PERSONAS[persona_name]['color_code'])
            
            # NOWY: Fight Club - Runda 2 jeśli wykryto konflikt
            if fight_club_enabled and is_controversial and len(all_responders) > 1:
                conflict_detected = detect_disagreement(first_round_responses)
                
                if conflict_detected:
                    print_colored("\n" + "="*80, "\033[91m")
                    print_colored("🥊 WYKRYTO KONFLIKT! Partnerzy mają różne zdania!", "\033[91m")
                    print_colored("   Uruchamiam rundę 2 - każdy może odpowiedzieć na innych...", "\033[91m")
                    print_colored("="*80 + "\n", "\033[91m")
                    
                    time.sleep(1)
                    
                    # Runda 2 - każdy odpowiada na innych
                    for persona_name in all_responders:
                        time.sleep(0.5)
                        
                        # Usuń własną odpowiedź z listy (nie odpowiada sam sobie)
                        other_responses = {k: v for k, v in first_round_responses.items() if k != persona_name}
                        
                        conflict_prompt = generate_conflict_prompt(
                            persona_name, 
                            user_message, 
                            other_responses,
                            stan_spolki_kompaktowy
                        )
                        
                        response_text = generuj_odpowiedz_ai(persona_name, conflict_prompt)
                        
                        last_responses[persona_name] = response_text
                        save_to_chronicle(persona_name, f"[RUNDA 2 - KONFLIKT] {response_text}")
                        
                        print_colored(f"\n🥊 [{persona_name}] - KONTRATAK:", PERSONAS[persona_name]['color_code'])
                        print_colored(response_text, PERSONAS[persona_name]['color_code'])
                        
                        # Zapisz konflikt do pamięci
                        for other_name in other_responses.keys():
                            if "nie zgadzam" in response_text.lower() or "mylisz" in response_text.lower():
                                save_conflict_memory(persona_name, other_name, user_message[:50])
                    
                    # Propozycja głosowania
                    print_colored("\n" + "="*80, "\033[95m")
                    print_colored("⚖️  SYTUACJA PATOWA - Partnerzy się nie zgadzają", "\033[95m")
                    print_colored("="*80, "\033[95m")
                    
                    odpowiedz = input("\n🗳️  Czy chcesz przeprowadzić głosowanie aby rozstrzygnąć? (tak/nie): ").strip().lower()
                    
                    if odpowiedz in ['tak', 't', 'yes', 'y']:
                        print_colored("\n💡 Sformułuj propozycję do głosowania na podstawie dyskusji.", "\033[93m")
                        propozycja = input("Propozycja: ").strip()
                        if propozycja:
                            # Zapisz kontekst i uruchom głosowanie w następnej iteracji
                            print_colored(f"\n✅ Propozycja zapisana: '{propozycja}'", "\033[92m")
                            print_colored("   Wpisz: glosowanie: " + propozycja, "\033[93m")
            
            # Przywróć tryb jeśli był zmieniony flagą
            if force_short or force_detailed:
                tryb_odpowiedzi = old_tryb
            print("-" * 80)

        except KeyboardInterrupt:
            print_colored("\n\n⚠️  Przerwano (Ctrl+C).", "\033[93m")
            generate_dashboard()
            break
        except Exception as e:
            print_colored(f"\n❌ Błąd: {e}", "\033[91m")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program przerwany przez użytkownika.")
    except Exception as e:
        print(f"\n❌ Nieoczekiwany błąd: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.stop()
            loop.close()
        except:
            pass