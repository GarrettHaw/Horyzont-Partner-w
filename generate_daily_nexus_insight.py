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
    """Oblicza sumę aktualnych kredytów"""
    kredyty = load_json_file('kredyty.json', default=[])
    if not isinstance(kredyty, list):
        return 0
    return sum(k.get('aktualna_kwota', 0) for k in kredyty if isinstance(k, dict))


def pobierz_dane_portfela():
    """
    Pobiera dane portfela z trading212_cache.json (to samo źródło co Streamlit/Nexus).
    Opcjonalnie odświeża dane przez update_trading212.py jeśli dostępne.
    """
    try:
        # Spróbuj odświeżyć dane (jeśli mamy API keys)
        if update_all_portfolio_data is not None:
            print("   Odświeżanie danych z Trading212 API...")
            try:
                update_all_portfolio_data()
                print("   ✅ Dane odświeżone")
            except Exception as e:
                print(f"   ⚠️ Nie udało się odświeżyć danych: {e}")
                print("   Użyję cache...")
        else:
            print("   Używam trading212_cache.json (brak update_trading212)")
        
        # Wczytaj z cache
        cache_file = 'trading212_cache.json'
        if not os.path.exists(cache_file):
            print(f"❌ Brak {cache_file}")
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Struktura cache: {'timestamp', 'akcje': {'wartosc_pln', 'pozycje': {...}}}
        if 'akcje' not in cache_data:
            print("❌ Nieprawidłowa struktura trading212_cache.json")
            return None
        
        akcje_val = cache_data.get('akcje', {}).get('wartosc_pln', 0)
        pozycje_count = len(cache_data.get('akcje', {}).get('pozycje', {}))
        
        print(f"   ✅ Załadowano cache: {pozycje_count} pozycji, wartość {akcje_val:.2f} PLN")
        
        # Zwróć w formacie stan_spolki
        stan_spolki = {
            'akcje': cache_data.get('akcje', {}),
            'krypto': cache_data.get('krypto', {'wartosc_pln': 0, 'pozycje': {}})
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
    
    # Update crypto value
    if krypto_data and isinstance(krypto_data, dict):
        crypto_positions = krypto_data.get('pozycje', {})
        crypto_value = sum(p.get('wartosc_pln', 0) for p in crypto_positions.values() if isinstance(p, dict))
        stan_spolki['krypto']['wartosc_pln'] = crypto_value
        stan_spolki['krypto']['pozycje'] = crypto_positions
        print(f"   Krypto: {crypto_value:.2f} PLN")
    
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
        
        # Generate response
        insight_text = nexus.generate_response(
            user_prompt=prompt,
            portfolio_context={
                'total_value': net_worth,
                'stocks_value': akcje_val,
                'crypto_value': krypto_val,
                'cash_reserve': rezerwa_val,
                'debt': dlugi_val,
                'net_worth': net_worth,
                'positions_count': len(stan_spolki.get('akcje', {}).get('pozycje', {}))
            },
            partner_responses=[],  # Brak odpowiedzi partnerów (daily insight)
            goals=cele,
            mood={}
        )
        
        if not insight_text:
            raise Exception("Nexus zwrócił None - błąd generowania")
        
        print(f"✅ Otrzymano analizę ({len(insight_text)} znaków)")
        
    except Exception as e:
        print(f"❌ Błąd generowania przez Nexusa: {e}")
        print("📝 Użyję fallback insight")
        
        insight_text = f"""Portfolio w stabilnej kondycji. Wartość netto: {net_worth:,.0f} PLN.

Dźwignia na poziomie {dlugi_val/(akcje_val+krypto_val+rezerwa_val)*100 if (akcje_val+krypto_val+rezerwa_val) > 0 else 0:.1f}% - monitoruj ryzyko zadłużenia.

Rezerwa gotówkowa: {rezerwa_val:,.0f} PLN ({cele.get('Rezerwa_gotowkowa_obecna_PLN', 0)/cele.get('Rezerwa_gotowkowa_PLN', 1)*100:.0f}% celu).

Utrzymuj dywersyfikację i spłacaj długi systematycznie."""
    
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
