"""
📸 Daily Snapshot System v1.0
Automatyczny system codziennego zapisywania stanu portfela

CECHY:
- Zapis o stałej godzinie (domyślnie 21:00)
- Pełny snapshot wszystkich aktywów (akcje, crypto, kredyty)
- Historia w formacie daily_snapshots.json
- Automatyczna rotacja starych danych (przechowujemy 365 dni)
- Deduplikacja (1 snapshot na dzień)
- Wsparcie dla wykresów long-term

UŻYCIE:
1. Automatyczne: uruchom jako Windows Task Scheduler o 21:00
2. Ręczne: python daily_snapshot.py
3. Z Streamlit: importuj i wywołaj save_daily_snapshot()
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

# Import istniejących modułów
try:
    import gra_rpg as main_app
    GRA_RPG_OK = True
except ImportError:
    GRA_RPG_OK = False
    print("⚠️ Nie można zaimportować gra_rpg.py")

try:
    from crypto_portfolio_manager import CryptoPortfolioManager
except ImportError:
    CryptoPortfolioManager = None

SNAPSHOT_FILE = "daily_snapshots.json"
MONTHLY_SNAPSHOT_FILE = "monthly_snapshot.json"
MAX_HISTORY_DAYS = 365  # Przechowuj rok historii

def migrate_monthly_to_daily_snapshots() -> int:
    """
    Migruj dane z monthly_snapshot.json do daily_snapshots.json
    Używa się TYLKO RAZ aby zainicjować historię
    
    Returns:
        int: Liczba zmigrowanych snapshots
    """
    if not os.path.exists(MONTHLY_SNAPSHOT_FILE):
        print("⚠️ Brak monthly_snapshot.json do migracji")
        return 0
    
    try:
        with open(MONTHLY_SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
            monthly_data = json.load(f)
        
        # Konwertuj format monthly → daily
        stan = monthly_data.get('stan', {})
        
        # Parsuj dane
        portfel_akcji = stan.get('PORTFEL_AKCJI', {})
        portfel_krypto = stan.get('PORTFEL_KRYPTO', {})
        portfel_zobowiazania = stan.get('PORTFEL_ZOBOWIAZANIA', {})
        
        stocks_usd = portfel_akcji.get('Suma_USD', 0)
        stocks_pln = portfel_akcji.get('Suma_PLN', 0)
        crypto_usd = portfel_krypto.get('Suma_USD', 0)
        crypto_pln = portfel_krypto.get('Suma_PLN', 0)
        debt_pln = portfel_zobowiazania.get('Suma_PLN', 0)
        
        migrated_snapshot = {
            'date': monthly_data.get('data', '2025-10-19 19:14:04'),
            'date_only': monthly_data.get('data', '2025-10-19')[:10],
            'usd_pln_rate': stan.get('Kurs_USD_PLN', 3.64),
            'stocks': {
                'value_usd': round(stocks_usd, 2),
                'value_pln': round(stocks_pln, 2),
                'positions': portfel_akcji.get('Liczba_pozycji_calkowita', 0),
                'cash_usd': portfel_akcji.get('Cash_free_USD', 0)
            } if stocks_usd > 0 else None,
            'crypto': {
                'value_usd': round(crypto_usd, 2),
                'value_pln': round(crypto_pln, 2),
                'positions': portfel_krypto.get('Liczba_pozycji', 0)
            } if crypto_usd > 0 else None,
            'debt': {
                'total_pln': round(debt_pln, 2),
                'loans_count': portfel_zobowiazania.get('Liczba_kredytow', 0)
            } if debt_pln > 0 else None,
            'totals': {
                'assets_usd': round(stocks_usd + crypto_usd, 2),
                'assets_pln': round(stocks_pln + crypto_pln, 2),
                'debt_pln': round(debt_pln, 2),
                'net_worth_pln': round(stocks_pln + crypto_pln - debt_pln, 2)
            },
            '_migrated_from': 'monthly_snapshot.json'
        }
        
        # Wczytaj istniejącą historię daily
        history = load_snapshot_history()
        
        # Dodaj zmigrowany snapshot jeśli nie istnieje
        date_only = migrated_snapshot['date_only']
        existing_dates = [s['date'][:10] for s in history]
        
        if date_only not in existing_dates:
            history.append(migrated_snapshot)
            if save_snapshot_history(history):
                print(f"✅ Zmigrowano snapshot z {date_only}")
                return 1
        else:
            print(f"ℹ️ Snapshot z {date_only} już istnieje - pomijam")
            return 0
            
    except Exception as e:
        print(f"❌ Błąd migracji: {e}")
        return 0

def get_portfolio_data_from_main() -> Optional[Dict]:
    """Pobierz dane z głównego programu (gra_rpg.py)"""
    if not GRA_RPG_OK:
        return None
    
    try:
        # Wczytaj cele (wymagane do pobierz_stan_spolki)
        cele = main_app.wczytaj_cele()
        
        # Użyj funkcji z gra_rpg.py do pobrania pełnych danych
        stan_spolki = main_app.pobierz_stan_spolki(cele)
        return stan_spolki
    except Exception as e:
        print(f"⚠️ Błąd pobierania danych z gra_rpg.py: {e}")
        return None

def get_crypto_data() -> Optional[Dict]:
    """Pobierz dane crypto z lokalnego pliku + live prices"""
    try:
        if not os.path.exists('krypto.json'):
            return None
            
        with open('krypto.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Obsługa różnych formatów (może być bezpośrednio lista lub {'krypto': lista})
        if isinstance(data, dict) and 'krypto' in data:
            crypto_holdings = data['krypto']
        elif isinstance(data, list):
            crypto_holdings = data
        else:
            return None
        
        # Podstawowe dane z pliku
        total_amount = sum(k.get('kwota_usd', 0) for k in crypto_holdings)
        
        # Spróbuj pobrać live prices jeśli manager dostępny
        if CryptoPortfolioManager:
            try:
                manager = CryptoPortfolioManager()
                symbols = [k.get('symbol') for k in crypto_holdings if k.get('symbol')]
                prices = manager.get_current_prices(symbols)
                
                # Przelicz z live prices
                live_value = 0
                for holding in crypto_holdings:
                    symbol = holding.get('symbol')
                    quantity = holding.get('ilosc', 0)
                    if symbol and symbol in prices:
                        price_data = prices.get(symbol, {})
                        current_price = price_data.get('current_price', 0)
                        if current_price > 0:
                            live_value += quantity * current_price
                
                if live_value > 0:
                    total_amount = live_value
                    print(f"✅ Użyto live prices crypto: ${live_value:,.2f}")
            except Exception as e:
                print(f"⚠️ Live crypto prices niedostępne: {e}")
        
        return {
            'total_value_usd': total_amount,
            'positions_count': len(crypto_holdings)
        }
    except Exception as e:
        print(f"⚠️ Błąd crypto: {e}")
    return None

def get_kredyty_data() -> Optional[Dict]:
    """Pobierz dane o zobowiązaniach"""
    try:
        if not os.path.exists('kredyty.json'):
            return None
            
        with open('kredyty.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Obsługa różnych formatów
        if isinstance(data, dict) and 'kredyty' in data:
            kredyty = data['kredyty']
        elif isinstance(data, list):
            kredyty = data
        else:
            return None
        
        total_debt = sum(k.get('pozostalo_do_splaty', 0) for k in kredyty)
        
        return {
            'total_debt_pln': total_debt,
            'loans_count': len(kredyty)
        }
    except Exception as e:
        print(f"⚠️ Błąd kredyty: {e}")
    return None

def get_usd_pln_rate() -> float:
    """Pobierz aktualny kurs USD/PLN"""
    try:
        response = requests.get(
            'https://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json',
            timeout=5
        )
        if response.status_code == 200:
            return response.json()['rates'][0]['mid']
    except:
        pass
    return 3.65  # Fallback jeśli API nie działa

def load_snapshot_history() -> List[Dict]:
    """Wczytaj historię snapshots"""
    if not os.path.exists(SNAPSHOT_FILE):
        return []
    
    try:
        with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Błąd wczytywania historii: {e}")
        return []

def save_snapshot_history(history: List[Dict]):
    """Zapisz historię snapshots"""
    try:
        # Sortuj po dacie (najnowsze na końcu)
        history.sort(key=lambda x: x['date'])
        
        # Usuń duplikaty (ten sam dzień)
        unique_history = {}
        for snapshot in history:
            date_key = snapshot['date'][:10]  # Tylko YYYY-MM-DD
            unique_history[date_key] = snapshot
        
        # Konwertuj z powrotem na listę
        history = list(unique_history.values())
        
        # Rotacja - zachowaj tylko ostatnie X dni
        cutoff_date = (datetime.now() - timedelta(days=MAX_HISTORY_DAYS)).strftime('%Y-%m-%d')
        history = [s for s in history if s['date'][:10] >= cutoff_date]
        
        with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"⚠️ Błąd zapisu historii: {e}")
        return False

def save_daily_snapshot(api_key: Optional[str] = None) -> bool:
    """
    Główna funkcja - zapisz snapshot stanu portfela
    
    Args:
        api_key: Trading212 API key (DEPRECATED - używa gra_rpg.py)
    
    Returns:
        bool: True jeśli snapshot zapisany, False jeśli błąd
    """
    print("="*60)
    print(f"📸 Daily Snapshot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Pobierz aktualny kurs
    usd_pln = get_usd_pln_rate()
    print(f"💱 USD/PLN: {usd_pln:.4f}")
    
    # Pobierz pełne dane z głównego programu
    stan_spolki = get_portfolio_data_from_main()
    
    if not stan_spolki:
        print("❌ Nie można pobrać danych portfela z gra_rpg.py!")
        print("   Sprawdź czy główny program działa poprawnie")
        return False
    
    # Parsuj dane ze struktury gra_rpg
    try:
        # Akcje - bezpośrednio w głównej strukturze
        portfel_akcji = stan_spolki.get('PORTFEL_AKCJI', {})
        stocks_usd = portfel_akcji.get('Suma_USD', 0)
        stocks_pln = portfel_akcji.get('Suma_PLN', 0)
        stocks_positions = portfel_akcji.get('Liczba_pozycji_calkowita', 0)
        stocks_cash = portfel_akcji.get('Cash_free_USD', 0)
        
        # Crypto - bezpośrednio w głównej strukturze
        portfel_krypto = stan_spolki.get('PORTFEL_KRYPTO', {})
        crypto_usd = portfel_krypto.get('Suma_USD', 0)
        crypto_pln = portfel_krypto.get('Suma_PLN', 0)
        crypto_positions = portfel_krypto.get('Liczba_pozycji', 0)
        
        # Zobowiązania - bezpośrednio w głównej strukturze
        portfel_zobowiazania = stan_spolki.get('PORTFEL_ZOBOWIAZANIA', {})
        debt_pln = portfel_zobowiazania.get('Suma_PLN', 0)
        debt_count = portfel_zobowiazania.get('Liczba_kredytow', 0)
        
        # Totale
        total_usd = stocks_usd + crypto_usd
        total_pln = stocks_pln + crypto_pln
        net_worth_pln = total_pln - debt_pln
        
    except Exception as e:
        print(f"❌ Błąd parsowania danych: {e}")
        return False
    
    # Stwórz snapshot
    snapshot = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_only': datetime.now().strftime('%Y-%m-%d'),  # Dla deduplikacji
        'usd_pln_rate': usd_pln,
        
        'stocks': {
            'value_usd': round(stocks_usd, 2),
            'value_pln': round(stocks_pln, 2),
            'positions': stocks_positions,
            'cash_usd': round(stocks_cash, 2)
        } if stocks_usd > 0 else None,
        
        'crypto': {
            'value_usd': round(crypto_usd, 2),
            'value_pln': round(crypto_pln, 2),
            'positions': crypto_positions
        } if crypto_usd > 0 else None,
        
        'debt': {
            'total_pln': round(debt_pln, 2),
            'loans_count': debt_count
        } if debt_pln > 0 else None,
        
        'totals': {
            'assets_usd': round(total_usd, 2),
            'assets_pln': round(total_pln, 2),
            'debt_pln': round(debt_pln, 2),
            'net_worth_pln': round(net_worth_pln, 2)
        }
    }
    
    # Wczytaj historię
    history = load_snapshot_history()
    
    # Dodaj nowy snapshot
    history.append(snapshot)
    
    # Zapisz
    if save_snapshot_history(history):
        print("\n✅ SNAPSHOT ZAPISANY")
        print(f"   📊 Akcje: ${stocks_usd:,.2f}")
        print(f"   ₿ Crypto: ${crypto_usd:,.2f}")
        print(f"   💰 Total Assets: {total_pln:,.2f} PLN")
        print(f"   💳 Zobowiązania: {debt_pln:,.2f} PLN")
        print(f"   💎 Net Worth: {net_worth_pln:,.2f} PLN")
        print(f"\n📈 Historia: {len(history)} snapshots (ostatnie {MAX_HISTORY_DAYS} dni)")
        
        # Sprawdź czy to pierwszy snapshot dzisiaj
        today = datetime.now().strftime('%Y-%m-%d')
        today_snapshots = [s for s in history if s['date'][:10] == today]
        if len(today_snapshots) > 1:
            print(f"   ℹ️ To {len(today_snapshots)}. snapshot dzisiaj (nadpisany)")
        
        return True
    else:
        print("❌ Błąd zapisu snapshot!")
        return False

def get_snapshot_stats() -> Dict:
    """Zwróć statystyki snapshot history"""
    history = load_snapshot_history()
    
    if not history:
        return {'count': 0}
    
    # Sortuj po dacie
    history.sort(key=lambda x: x['date'])
    
    first_date = datetime.fromisoformat(history[0]['date'])
    last_date = datetime.fromisoformat(history[-1]['date'])
    days_tracked = (last_date - first_date).days
    
    # Oblicz wzrost net worth
    first_nw = history[0]['totals']['net_worth_pln']
    last_nw = history[-1]['totals']['net_worth_pln']
    nw_change_pct = ((last_nw - first_nw) / first_nw * 100) if first_nw > 0 else 0
    
    return {
        'count': len(history),
        'first_date': history[0]['date'][:10],
        'last_date': history[-1]['date'][:10],
        'days_tracked': days_tracked,
        'first_net_worth': first_nw,
        'last_net_worth': last_nw,
        'net_worth_change_pct': round(nw_change_pct, 2),
        'avg_snapshots_per_week': round(len(history) / (days_tracked / 7), 1) if days_tracked > 0 else 0
    }

def should_create_snapshot(target_hour: int = 21) -> bool:
    """
    Sprawdź czy powinniśmy utworzyć snapshot
    
    Args:
        target_hour: Docelowa godzina (0-23), domyślnie 21:00
    
    Returns:
        bool: True jeśli brak dzisiejszego snapshotu i jest po target_hour
    """
    history = load_snapshot_history()
    today = datetime.now().strftime('%Y-%m-%d')
    current_hour = datetime.now().hour
    
    # Sprawdź czy już jest snapshot z dzisiaj
    today_snapshots = [s for s in history if s['date'][:10] == today]
    
    if today_snapshots:
        return False  # Już mamy snapshot z dzisiaj
    
    # Sprawdź czy minęła target_hour
    return current_hour >= target_hour

if __name__ == "__main__":
    # Uruchomienie z linii komend
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            # Wyświetl statystyki
            stats = get_snapshot_stats()
            print("\n📊 STATYSTYKI DAILY SNAPSHOTS")
            print("="*60)
            if stats['count'] == 0:
                print("Brak zapisanych snapshots")
            else:
                print(f"📈 Liczba snapshots: {stats['count']}")
                print(f"📅 Pierwszy: {stats['first_date']}")
                print(f"📅 Ostatni: {stats['last_date']}")
                print(f"⏱️  Dni śledzenia: {stats['days_tracked']}")
                print(f"💎 Net Worth pierwszy: {stats['first_net_worth']:,.2f} PLN")
                print(f"💎 Net Worth ostatni: {stats['last_net_worth']:,.2f} PLN")
                print(f"📊 Zmiana: {stats['net_worth_change_pct']:+.2f}%")
                print(f"⚡ Avg snapshots/tydzień: {stats['avg_snapshots_per_week']}")
        elif sys.argv[1] == "check":
            # Sprawdź czy trzeba snapshot
            if should_create_snapshot():
                print("✅ Pora na snapshot! (po 21:00, brak dzisiejszego)")
                sys.exit(0)
            else:
                print("⏳ Nie teraz (za wcześnie lub już jest dzisiejszy)")
                sys.exit(1)
        elif sys.argv[1] == "migrate":
            # Migruj monthly_snapshot.json → daily_snapshots.json
            print("\n🔄 MIGRACJA MONTHLY → DAILY SNAPSHOTS")
            print("="*60)
            count = migrate_monthly_to_daily_snapshots()
            if count > 0:
                print(f"\n✅ Zmigrowano {count} snapshot")
                print("Teraz uruchom 'python daily_snapshot.py stats' aby zobaczyć historię")
            else:
                print("\nℹ️ Brak nowych danych do migracji")
    else:
        # Normalny zapis snapshot
        save_daily_snapshot()
