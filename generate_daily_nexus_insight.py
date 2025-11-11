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
import gspread
from google.oauth2.service_account import Credentials

# Import Nexusa
try:
    from nexus_ai_engine import NexusAIEngine
except ImportError:
    print("❌ Nie można zaimportować nexus_ai_engine.py")
    sys.exit(1)


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


def pobierz_dane_z_google_sheets():
    """Pobiera dane portfela z Google Sheets"""
    try:
        # Load credentials
        creds_path = 'credentials.json'
        if not os.path.exists(creds_path):
            print("❌ Brak credentials.json")
            return None
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        print("   Ładowanie credentials...")
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        
        print("   Otwieranie arkusza 'Horyzont Partnerów - Stan Spółki'...")
        spreadsheet = client.open("Horyzont Partnerów - Stan Spółki")
        
        print("   Pobieranie worksheetu 'Portfolio Data'...")
        worksheet = spreadsheet.worksheet("Portfolio Data")
        
        print("   Pobieranie danych z arkusza...")
        # Get all data
        all_data = worksheet.get_all_values()
        
        print(f"   Pobrano {len(all_data)} wierszy")
        
        if len(all_data) < 2:
            print("❌ Brak danych w arkuszu")
            return None
        
        # Parse headers and data
        headers = all_data[0]
        data_rows = all_data[1:]
        
        print(f"   Nagłówki: {headers[:5]}...")  # Pierwsze 5 kolumn
        
        # Build portfolio structure
        akcje_pozycje = {}
        total_stocks_value = 0
        
        for row in data_rows:
            if len(row) < len(headers):
                continue
            
            row_dict = dict(zip(headers, row))
            ticker = row_dict.get('Ticker', '').strip()
            
            if not ticker:
                continue
            
            try:
                ilosc = float(row_dict.get('Ilość', 0))
                cena = float(row_dict.get('Cena Aktualna', 0))
                wartosc = ilosc * cena
                
                akcje_pozycje[ticker] = {
                    'ilosc': ilosc,
                    'cena_aktualna': cena,
                    'wartosc_pln': wartosc,
                    'nazwa': row_dict.get('Nazwa', ticker)
                }
                
                total_stocks_value += wartosc
            except (ValueError, TypeError):
                continue
        
        stan_spolki = {
            'akcje': {
                'wartosc_pln': total_stocks_value,
                'pozycje': akcje_pozycje
            },
            'krypto': {
                'wartosc_pln': 0,  # Crypto handled separately
                'pozycje': {}
            }
        }
        
        print(f"✅ Pobrano {len(akcje_pozycje)} pozycji akcji, wartość: {total_stocks_value:.2f} PLN")
        return stan_spolki
        
    except gspread.exceptions.SpreadsheetNotFound:
        print("❌ Nie znaleziono arkusza 'Horyzont Partnerów - Stan Spółki'")
        print("   Sprawdź czy arkusz jest udostępniony dla service account!")
        return None
    except gspread.exceptions.WorksheetNotFound:
        print("❌ Nie znaleziono zakładki 'Portfolio Data'")
        print("   Dostępne zakładki:")
        try:
            spreadsheet = client.open("Horyzont Partnerów - Stan Spółki")
            for ws in spreadsheet.worksheets():
                print(f"   - {ws.title}")
        except:
            pass
        return None
    except Exception as e:
        print(f"❌ Błąd pobierania z Google Sheets: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_daily_insight():
    """Główna funkcja generująca dzienny insight od Nexusa"""
    
    print("🤖 === GENEROWANIE DZIENNEJ ANALIZY NEXUSA ===")
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Pobierz dane portfela
    print("\n📊 Pobieranie danych portfela...")
    stan_spolki = pobierz_dane_z_google_sheets()
    
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
