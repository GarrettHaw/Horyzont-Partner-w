#!/usr/bin/env python3
"""
Update Trading212 Data
Pobiera dane z Trading212 API i zapisuje do cache.
Uruchamiane przez GitHub Actions co 6 godzin.
"""

import os
import json
import requests
from datetime import datetime

# Konfiguracja
TRADING212_BASE_URL = "https://live.trading212.com/api/v0"
TRADING212_CACHE_FILE = "trading212_cache.json"

def pobierz_dane_trading212():
    """Pobiera dane z Trading212 API."""
    api_key = os.getenv("TRADING212_API_KEY")
    
    if not api_key:
        print("❌ Brak klucza TRADING212_API_KEY w zmiennych środowiskowych")
        return None
    
    print("📊 Pobieram dane z Trading212 API...")
    
    headers = {
        "Authorization": api_key
    }
    
    dane_t212 = {}
    
    try:
        # 1. Pobierz pozycje w portfelu
        print("  ↪ Pobieram pozycje...")
        response = requests.get(
            f"{TRADING212_BASE_URL}/equity/portfolio",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        dane_t212["positions"] = response.json()
        print(f"  ✓ Pobrano {len(dane_t212['positions'])} pozycji")
        
        # 2. Pobierz informacje o koncie (saldo gotówkowe)
        print("  ↪ Pobieram info o koncie...")
        response = requests.get(
            f"{TRADING212_BASE_URL}/equity/account/cash",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        dane_t212["account"] = response.json()
        cash = dane_t212['account'].get('free', 0)
        currency = dane_t212['account'].get('currencyCode', 'USD')
        print(f"  ✓ Saldo: {cash:.2f} {currency}")
        
        # 3. Pobierz historię dywidend (ostatnie 2 lata)
        print("  ↪ Pobieram historię dywidend...")
        try:
            from datetime import timedelta
            
            # Trading212 API wymaga parametrów cursor lub limit
            # Pobierz maksymalnie 500 ostatnich dywidend (limit API)
            response = requests.get(
                f"{TRADING212_BASE_URL}/history/dividends",
                headers=headers,
                params={"limit": 500},  # Maksymalny limit API
                timeout=10
            )
            response.raise_for_status()
            dividends_response = response.json()
            
            # Debug: sprawdź strukturę odpowiedzi
            print(f"  📝 Debug - typ odpowiedzi: {type(dividends_response)}")
            if isinstance(dividends_response, dict):
                print(f"  📝 Debug - klucze w dict: {list(dividends_response.keys())}")
            
            # API może zwracać dict z 'items' lub bezpośrednio listę
            if isinstance(dividends_response, dict):
                dane_t212["dividends"] = dividends_response.get("items", dividends_response.get("data", []))
            elif isinstance(dividends_response, list):
                dane_t212["dividends"] = dividends_response
            else:
                dane_t212["dividends"] = []
            
            print(f"  ✓ Pobrano {len(dane_t212['dividends'])} dywidend")
            
            # Debug: pokaż przykład pierwszej dywidendy jeśli istnieje
            if dane_t212["dividends"] and len(dane_t212["dividends"]) > 0:
                first_div = dane_t212["dividends"][0]
                print(f"  📝 Przykład: {first_div.get('ticker', 'N/A')} - {first_div.get('amount', 0)} USD")
                
        except Exception as e:
            print(f"  ⚠️ Nie udało się pobrać dywidend: {e}")
            import traceback
            traceback.print_exc()
            dane_t212["dividends"] = []
        
        # 4. Pobierz metadata (opcjonalne)
        try:
            response = requests.get(
                f"{TRADING212_BASE_URL}/equity/metadata/instruments",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                dane_t212["instruments_metadata"] = response.json()
                print(f"  ✓ Pobrano metadata instrumentów")
        except:
            pass
        
        return dane_t212
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"❌ Błąd autoryzacji Trading212: Nieprawidłowy API Key!")
        elif e.response.status_code == 429:
            print(f"⚠️ Przekroczono limit requestów Trading212")
        else:
            print(f"❌ Błąd HTTP Trading212: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
        return None
        
    except Exception as e:
        print(f"❌ Błąd pobierania z Trading212 API: {e}")
        return None

def zapisz_cache(dane):
    """Zapisuje dane do pliku cache."""
    if not dane:
        print("⚠️ Brak danych do zapisania")
        return False
    
    try:
        cache = {
            "timestamp": datetime.now().isoformat(),
            "data": dane
        }
        
        with open(TRADING212_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(TRADING212_CACHE_FILE)
        print(f"✓ Cache zapisany: {file_size} bajtów ({file_size/1024:.1f} KB)")
        return True
        
    except Exception as e:
        print(f"❌ Błąd zapisu cache: {e}")
        return False

def main():
    """Główna funkcja."""
    print("=" * 60)
    print("📊 TRADING212 DATA UPDATE")
    print("=" * 60)
    print(f"🕐 Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Pobierz dane
    dane = pobierz_dane_trading212()
    
    if dane:
        # Zapisz do cache
        if zapisz_cache(dane):
            print()
            print("=" * 60)
            print("✅ SUKCES - Dane Trading212 zaktualizowane")
            print("=" * 60)
            
            # Podsumowanie
            positions = len(dane.get('positions', []))
            dividends = len(dane.get('dividends', []))
            cash = dane.get('account', {}).get('free', 0)
            
            print(f"📈 Pozycje: {positions}")
            print(f"💰 Gotówka: {cash:.2f} USD")
            print(f"💵 Dywidendy: {dividends} transakcji")
            
            return 0
        else:
            print()
            print("=" * 60)
            print("❌ BŁĄD - Nie udało się zapisać cache")
            print("=" * 60)
            return 1
    else:
        print()
        print("=" * 60)
        print("❌ BŁĄD - Nie udało się pobrać danych z Trading212")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit(main())
