"""
DAILY NEXUS INSIGHT GENERATOR
==============================
Ten skrypt jest uruchamiany przez GitHub Action codziennie o 6:00 rano.
Generuje codzienną analizę portfela od Nexusa i zapisuje do daily_nexus_insight.json.

GitHub Action automatycznie commituje i pushuje plik, a Streamlit Cloud wyświetla analizę.
"""

import os
import sys
import json
from datetime import datetime

# Import Nexusa
try:
    from nexus_ai_engine import NexusAIEngine
except ImportError:
    print("❌ Nie można zaimportować nexus_ai_engine.py")
    sys.exit(1)

# Import update_trading212 do pobrania świeżych danych
try:
    from update_trading212 import update_all_portfolio_data
except ImportError:
    print("⚠️ Nie można zaimportować update_trading212.py - użyję cache")
    update_all_portfolio_data = None


def load_json_file(filename, default=None):
    """Bezpieczne wczytanie pliku JSON"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default if default is not None else {}
    except Exception as e:
        print(f"⚠️ Błąd wczytywania {filename}: {e}")
        return default if default is not None else {}


def get_suma_kredytow():
    """Oblicza sumę aktualnych kredytów (kwota_poczatkowa - splacono)"""
    kredyty_data = load_json_file('kredyty.json', default={})
    
    if not isinstance(kredyty_data, dict):
        return 0
    
    kredyty_list = kredyty_data.get('kredyty', [])
    
    if not isinstance(kredyty_list, list):
        return 0
    
    suma = 0
    for k in kredyty_list:
        if isinstance(k, dict):
            kwota_poczatkowa = k.get('kwota_poczatkowa', 0)
            splacono = k.get('splacono', 0)
            aktualna_kwota = kwota_poczatkowa - splacono
            suma += max(0, aktualna_kwota)  # Nie może być ujemna
    
    return suma


def pobierz_dane_portfela():
    """
    Pobiera dane portfela z trading212_cache.json (to samo źródło co Streamlit/Nexus).
    Przetwarza surowe dane API Trading212 do formatu używanego przez Nexusa.
    """
    try:
        # Wczytaj z cache
        cache_file = 'trading212_cache.json'
        if not os.path.exists(cache_file):
            print(f"❌ Brak {cache_file}")
            return None
        
        print(f"   Wczytywanie {cache_file}...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Cache ma strukturę: {"timestamp": "...", "data": {"positions": [...], "account": {...}}}
        trading212_data = cache_data.get('data', {})
        
        if not trading212_data:
            print("❌ Brak danych w cache (klucz 'data' nie istnieje)")
            return None
        
        # Parsuj pozycje Trading212
        positions = trading212_data.get('positions', [])
        
        if not positions:
            print("❌ Brak pozycji w trading212_cache.json")
            return None
        
        # Kurs USD->PLN (approx, można улучшyć później)
        kurs_usd_pln = 4.0
        
        # Przetworz pozycje
        akcje_pozycje = {}
        total_stocks_value_pln = 0
        
        for pos in positions:
            ticker = pos.get('ticker', 'UNKNOWN')
            quantity = pos.get('quantity', 0)
            current_price = pos.get('currentPrice', 0)
            avg_price = pos.get('averagePrice', 0)
            
            value_usd = quantity * current_price
            value_pln = value_usd * kurs_usd_pln
            
            akcje_pozycje[ticker] = {
                'ilosc': quantity,
                'cena_aktualna': current_price,
                'cena_srednia': avg_price,
                'wartosc_usd': value_usd,
                'wartosc_pln': value_pln,
                'frontend': pos.get('frontend', '')
            }
            
            total_stocks_value_pln += value_pln
        
        pozycje_count = len(akcje_pozycje)
        
        print(f"   ✅ Załadowano {pozycje_count} pozycji akcji, wartość {total_stocks_value_pln:.2f} PLN")
        
        # Zwróć w formacie stan_spolki
        stan_spolki = {
            'akcje': {
                'wartosc_pln': total_stocks_value_pln,
                'pozycje': akcje_pozycje,
                'liczba_pozycji': pozycje_count
            },
            'krypto': {
                'wartosc_pln': 0,
                'pozycje': {}
            }
        }
        
        return stan_spolki
        
    except Exception as e:
        print(f"❌ Błąd pobierania danych portfela: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_daily_insight():
    """Główna funkcja generująca dzienny insight od Nexusa"""
    
    print("🤖 === GENEROWANIE DZIENNEJ ANALIZY NEXUSA ===")
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Pobierz dane portfela
    print("\n📊 Pobieranie danych portfela...")
    stan_spolki = pobierz_dane_portfela()
    
    if not stan_spolki:
        print("❌ Nie można pobrać danych portfela - przerywam")
        sys.exit(1)
    
    # 2. Pobierz cele i crypto
    print("📋 Wczytywanie celów i krypto...")
    cele = load_json_file('cele.json')
    krypto_data = load_json_file('krypto.json')
    
    # Update crypto value (struktura: {"krypto": [...]})
    if krypto_data and isinstance(krypto_data, dict):
        crypto_list = krypto_data.get('krypto', [])
        
        if isinstance(crypto_list, list):
            # Oblicz wartość krypto (potrzebujemy API do cen - dla teraz użyj cache)
            crypto_value = 0
            crypto_positions = {}
            
            for coin in crypto_list:
                if isinstance(coin, dict):
                    symbol = coin.get('symbol', 'UNKNOWN')
                    ilosc = coin.get('ilosc', 0)
                    # Spróbuj użyć cached price lub cena_zakupu
                    cena = coin.get('cena_aktualna_usd', coin.get('cena_zakupu_usd', 0))
                    wartosc_usd = ilosc * cena
                    wartosc_pln = wartosc_usd * 4.0  # Approx USD->PLN (można улучшyć)
                    
                    crypto_positions[symbol] = {
                        'ilosc': ilosc,
                        'cena_usd': cena,
                        'wartosc_pln': wartosc_pln
                    }
                    crypto_value += wartosc_pln
            
            stan_spolki['krypto']['wartosc_pln'] = crypto_value
            stan_spolki['krypto']['pozycje'] = crypto_positions
            print(f"   Krypto: {crypto_value:.2f} PLN ({len(crypto_positions)} monet)")
        else:
            print(f"   ⚠️ Nieprawidłowa struktura krypto.json")
    else:
        print(f"   ⚠️ Brak danych krypto")
    
    # 3. Oblicz wartości
    akcje_val = stan_spolki.get('akcje', {}).get('wartosc_pln', 0)
    krypto_val = stan_spolki.get('krypto', {}).get('wartosc_pln', 0)
    rezerwa_val = cele.get('Rezerwa_gotowkowa_obecna_PLN', 0) if cele else 0
    dlugi_val = get_suma_kredytow()
    net_worth = akcje_val + krypto_val + rezerwa_val - dlugi_val
    
    print(f"\n💰 Wartości portfela:")
    print(f"   Akcje: {akcje_val:.2f} PLN")
    print(f"   Krypto: {krypto_val:.2f} PLN")
    print(f"   Rezerwa: {rezerwa_val:.2f} PLN")
    print(f"   Dług: {dlugi_val:.2f} PLN")
    print(f"   ═══════════════════════")
    print(f"   NET WORTH: {net_worth:.2f} PLN")
    
    # 4. Przygotuj portfolio summary
    portfolio_summary = f"""
Wartość Netto: {net_worth:,.0f} PLN  
• Akcje: {akcje_val:,.0f} PLN ({akcje_val/(akcje_val+krypto_val+rezerwa_val)*100 if (akcje_val+krypto_val+rezerwa_val) > 0 else 0:.0f}%)  
• Krypto: {krypto_val:,.0f} PLN ({krypto_val/(akcje_val+krypto_val+rezerwa_val)*100 if (akcje_val+krypto_val+rezerwa_val) > 0 else 0:.0f}%)  
• Rezerwa: {rezerwa_val:,.0f} PLN ({rezerwa_val/(akcje_val+krypto_val+rezerwa_val)*100 if (akcje_val+krypto_val+rezerwa_val) > 0 else 0:.0f}%)  
• Zobowiązania: {dlugi_val:,.0f} PLN  
• Dźwignia: {dlugi_val/(akcje_val+krypto_val+rezerwa_val)*100 if (akcje_val+krypto_val+rezerwa_val) > 0 else 0:.1f}%
    """.strip()
    
    # 5. Przygotuj prompt dla Nexusa
    prompt = f"""Jesteś Nexus - meta-doradca AI Rady Partnerów "Horyzont Partnerów".

TWOJE ZADANIE:
Wygeneruj KRÓTKĄ (3-5 zdań) codzienną ocenę portfela użytkownika. To jest automatyczna analiza wyświetlana na dashboardzie.

PORTFOLIO UŻYTKOWNIKA:
{portfolio_summary}

CELE FINANSOWE:
- Rezerwa gotówkowa: {cele.get('Rezerwa_gotowkowa_obecna_PLN', 0):.0f} / {cele.get('Rezerwa_gotowkowa_PLN', 0):.0f} PLN ({cele.get('Rezerwa_gotowkowa_obecna_PLN', 0)/cele.get('Rezerwa_gotowkowa_PLN', 1)*100:.0f}%)
- Dług do spłaty: {dlugi_val:.0f} PLN (cel: 70% z {cele.get('Dlugi_poczatkowe_PLN', 0):.0f} PLN)

CO NAPISAĆ:
1. Szybka ocena stanu portfela (dobry/neutralny/wymaga uwagi)
2. Kluczowa obserwacja (np. alokacja, ryzyko, cele)
3. Jedna konkretna rekomendacja lub przestroga

STYL:
- Konkretny, data-driven
- Bez ogólników
- Może być prowokacyjny jeśli sytuacja tego wymaga
- 3-5 zdań MAX

Twoja ocena:"""
    
    # 6. Wygeneruj odpowiedź od Nexusa
    print("\n🤖 Generowanie analizy od Nexusa...")
    
    try:
        # Get Nexus engine
        nexus = NexusAIEngine()
        
        # Build context dict (Nexus oczekuje 'context' dict, nie oddzielnych parametrów)
        context = {
            'portfolio': {
                'total_value': net_worth,
                'stocks_value': akcje_val,
                'crypto_value': krypto_val,
                'cash_reserve': rezerwa_val,
                'debt': dlugi_val,
                'net_worth': net_worth,
                'positions_count': len(stan_spolki.get('akcje', {}).get('pozycje', {}))
            },
            'goals': cele,
            'mood': {},
            'partner_responses': []
        }
        
        # Generate response (używamy NOWEJ sygnatury z nexus_ai_engine.py)
        response = nexus.generate_response(
            prompt=prompt,
            context=context,
            use_ensemble=False
        )
        
        # Nexus zwraca dict {'response': str, 'confidence': float, ...} lub None
        if response and isinstance(response, dict):
            insight_text = response.get('response', '')
            if not insight_text:
                raise Exception("Nexus zwrócił pustą odpowiedź")
            print(f"✅ Otrzymano analizę ({len(insight_text)} znaków)")
        else:
            raise Exception("Nexus zwrócił None lub nieprawidłowy format")
        
    except Exception as e:
        print(f"❌ Błąd generowania przez Nexusa: {e}")
        print("📝 Użyję fallback insight")
        
        # Lepszy fallback z analizą długu
        leverage_pct = (dlugi_val/(akcje_val+krypto_val+rezerwa_val)*100) if (akcje_val+krypto_val+rezerwa_val) > 0 else 0
        reserve_progress = (cele.get('Rezerwa_gotowkowa_obecna_PLN', 0)/cele.get('Rezerwa_gotowkowa_PLN', 1)*100) if cele else 0
        
        insight_parts = []
        
        # Ocena stanu
        if net_worth > 50000:
            insight_parts.append(f"💪 Silna pozycja finansowa. Net worth: {net_worth:,.0f} PLN.")
        elif net_worth > 0:
            insight_parts.append(f"📊 Portfolio w rozwoju. Net worth: {net_worth:,.0f} PLN.")
        else:
            insight_parts.append(f"⚠️ UWAGA: Ujemna wartość netto ({net_worth:,.0f} PLN) - priorytet: redukcja długu!")
        
        # Dług
        if dlugi_val > 0:
            insight_parts.append(f"Dług: {dlugi_val:,.0f} PLN (dźwignia {leverage_pct:.1f}%) - systematyczna spłata to klucz.")
        else:
            insight_parts.append("✅ Brak zadłużenia - dobra pozycja startowa.")
        
        # Rezerwa
        if reserve_progress >= 100:
            insight_parts.append(f"🎯 Cel rezerwy gotówkowej osiągnięty ({rezerwa_val:,.0f} PLN)!")
        elif reserve_progress >= 50:
            insight_parts.append(f"📈 Rezerwa: {rezerwa_val:,.0f} PLN ({reserve_progress:.0f}% celu) - dobry postęp.")
        else:
            insight_parts.append(f"💰 Rezerwa: {rezerwa_val:,.0f} PLN ({reserve_progress:.0f}% celu) - zwiększ bezpieczeństwo finansowe.")
        
        # Alokacja
        crypto_allocation = (krypto_val/(akcje_val+krypto_val)*100) if (akcje_val+krypto_val) > 0 else 0
        if crypto_allocation > 60:
            insight_parts.append(f"⚠️ Krypto {crypto_allocation:.0f}% - rozważ większą dywersyfikację w akcje.")
        
        insight_text = " ".join(insight_parts)
    
    # 7. Zapisz do pliku JSON
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'insight_text': insight_text,
        'portfolio_summary': portfolio_summary,
        'metadata': {
            'net_worth': net_worth,
            'stocks_value': akcje_val,
            'crypto_value': krypto_val,
            'cash_reserve': rezerwa_val,
            'debt': dlugi_val
        }
    }
    
    output_file = 'daily_nexus_insight.json'
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Zapisano do {output_file}")
        print(f"📄 Zawartość:\n{json.dumps(output_data, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ Błąd zapisu do pliku: {e}")
        sys.exit(1)
    
    print("\n🎉 === ZAKOŃCZONO POMYŚLNIE ===")


if __name__ == "__main__":
    generate_daily_insight()
