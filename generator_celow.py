import google.generativeai as genai
import os
import time
import pprint

# ------------------ KONFIGURACJA ------------------
# KROK 1: Wklej tutaj swój NOWY klucz API Gemini
GOOGLE_API_KEY = "AIzaSyDRoccfX5dFHqD20mGfOCRWIO6gRRdiCnk"

# KROK 2: Upewnij się, że ten plik istnieje. Skrypt wczyta z niego wspomnienia.
NAZWA_PLIKU_WSPOMNIEN = "NOWE_skompilowane_persony.txt"
# Nazwa pliku, w którym zostanie zapisany wynik
NAZWA_PLIKU_WYJSCIOWEGO = "finalna_konfiguracja_person.txt"

# KROK 3: Skopiuj i wklej tutaj swój bazowy słownik `PERSONAS` (tylko z opisami)
PERSONAS_DO_ANALIZY = {
    # --- PARTNERZY ZARZĄDZAJĄCY ---
    "Partner Strategiczny": {
        "system_instruction": """Jesteś Partnerem Strategicznym w Horyzont Partnerów, posiadasz 30% głosów. Jesteś analitykiem i strażnikiem waszej wspólnej filozofii. Twoją rolą jest dostarczanie obiektywnych danych, kwestionowanie założeń i przedstawianie alternatywnych scenariuszy, aby każda decyzja była maksymalnie przemyślana.""",
        "color_code": "\033[96m" # Cyjan
    },
    # --- PARTNERZY MNIEJSZOŚCIOWI ---
    "Partner ds. Jakości Biznesowej": {
        "system_instruction": """Jesteś Partnerem ds. Jakości Biznesowej, posiadasz 5% głosów. Jesteś łącznikiem ze światem realnej gospodarki, przedsiębiorcą-operatorem. Twoim zadaniem jest ocena inwestycji z perspektywy praktyka, który wie, jak działają prawdziwe firmy.""",
        "color_code": "\033[92m" # Zielony
    },
    "Partner ds. Aktywów Cyfrowych": {
        "system_instruction": """Jesteś Partnerem ds. Aktywów Cyfrowych, posiadasz 5% głosów. Jesteś ekspertem i przewodnikiem po świecie nowych technologii finansowych. Twoją rolą jest identyfikowanie realnych innowacji i oddzielanie ich od spekulacyjnego szumu, zarządzając działem krypto.""",
        "color_code": "\033[95m" # Fioletowy
    },
    # --- RADA NADZORCZA ---
    "Benjamin Graham": {
        "system_instruction": """Jesteś Benjaminem Grahamem, członkiem Rady Nadzorczej. Jesteś głównym analitykiem ryzyka i strażnikiem kapitału. Twoim zadaniem jest przypominanie o 'marginesie bezpieczeństwa' i bezwzględne kwestionowanie każdej zbyt optymistycznej wyceny.""",
        "color_code": "\033[93m"
    },
    "Philip Fisher": {
        "system_instruction": """Jesteś Philipem Fisherem, członkiem Rady Nadzorczej. Jesteś głównym skautem i łowcą 'pereł'. Twoją rolą jest zmuszanie zarządu do myślenia o przyszłości i koncentrowania kapitału w naprawdę wyjątkowych, innowacyjnych firmach.""",
        "color_code": "\033[93m"
    },
    "George Soros": {
        "system_instruction": """Jesteś George'em Sorosem, członkiem Rady Nadzorczej. Jesteś strategiem makroekonomicznym i mistrzem gry. Twoim zadaniem jest przypominanie, że spółki nie działają w próżni, a największe okazje rodzą się, gdy rynek się myli.""",
        "color_code": "\033[93m"
    },
    "Warren Buffett": {
        "system_instruction": """Jesteś Warrenem Buffettem, cichym przewodniczącym Rady Nadzorczej. Twoją rolą jest przypominanie o cierpliwości, prostocie i myśleniu o akcjach jak o udziałach w realnym biznesie. Łączysz mądrość Grahama i Fishera.""",
        "color_code": "\033[93m"
    },
    # --- KONSULTANT ---
    "Changpeng Zhao (CZ)": {
        "system_instruction": """Jesteś Changpeng Zhao (CZ), konsultantem strategicznym ds. innowacji. Twoim zadaniem jest dostarczanie perspektywy ze świata, który działa według zupełnie innych zasad, kwestionowanie tradycyjnego myślenia i wskazywanie rewolucyjnych trendów.""",
        "color_code": "\033[94m"
    }
}
# ----------------------------------------------------

# Konfiguracja modelu
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('models/gemini-2.5-pro')
except Exception as e:
    print(f"BŁĄD KRYTYCZNY: Nie udało się skonfigurować API Gemini. Sprawdź swój klucz API. Szczegóły: {e}")
    exit()

def print_colored(text, color_code):
    print(f"{color_code}{text}\033[0m")

def wczytaj_wspomnienia(nazwa_pliku):
    """Wczytuje i parsuje wspomnienia z pliku wyjściowego kompilatora."""
    wspomnienia = {}
    if not os.path.exists(nazwa_pliku):
        print_colored(f"Informacja: Plik wspomnień '{nazwa_pliku}' nie został znaleziony. Placeholdery pozostaną puste.", "\033[93m")
        return wspomnienia

    with open(nazwa_pliku, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.split('# Pamięć dla postaci: ')[1:]
    for block in blocks:
        try:
            lines = block.strip().split('\n')
            persona_name = lines[0].strip()
            start_index = block.find('"""') + 3
            end_index = block.rfind('"""')
            memory_content = block[start_index:end_index].strip()
            wspomnienia[persona_name] = memory_content
        except IndexError:
            continue
    
    print_colored(f"Pomyślnie wczytano wspomnienia dla {len(wspomnienia)} postaci z pliku '{nazwa_pliku}'.", "\033[92m")
    return wspomnienia

def generuj_ukryte_cele():
    """Generuje ukryte cele i przygotowuje pełną konfigurację postaci."""
    wczytane_wspomnienia = wczytaj_wspomnienia(NAZWA_PLIKU_WSPOMNIEN)
    print_colored("Rozpoczynam generowanie ukrytych celów dla postaci...", "\033[93m")
    
    zaktualizowane_persony = {}

    for persona_name, persona_data in PERSONAS_DO_ANALIZY.items():
        print(f"  - Analizuję osobowość: {persona_name}...")
        
        prompt = f"""
        Przeanalizuj opis postaci z firmy 'Horyzont Partnerów'. Stwórz dla niej jeden, zwięzły i wiarygodny tajny cel (ukryty_cel), wynikający z jej charakteru.
        Odpowiedz wyłącznie tekstem samego celu.
        Opis postaci:
        ---
        {persona_data['system_instruction']}
        ---
        """
        
        try:
            response = model.generate_content(prompt)
            nowy_cel = response.text.strip()
            nowa_persona = persona_data.copy()
            nowa_persona['ukryty_cel'] = nowy_cel
            
            wspomnienia_postaci = wczytane_wspomnienia.get(persona_name, "[WSPOMNIENIA NIE ZNALEZIONE - URUCHOM KOMPILATOR]")
            
            finalna_instrukcja = f"""{nowa_persona['system_instruction'].strip()}

Oto Twoje najważniejsze wspomnienia, które kształtują Twoją obecną perspektywę:
{wspomnienia_postaci}
"""
            nowa_persona['system_instruction'] = finalna_instrukcja

            zaktualizowane_persony[persona_name] = nowa_persona
            print_colored(f"    ... Wygenerowano cel dla {persona_name}.", "\033[92m")

        except Exception as e:
            print_colored(f"    ... Wystąpił błąd podczas przetwarzania postaci {persona_name}: {e}", "\033[91m")
            zaktualizowane_persony[persona_name] = persona_data

        # Zwiększono czas oczekiwania dla większej stabilności
        print_colored(f"    ... Czekam 20 sekund, aby nie przekroczyć limitu API...", "\033[90m")
        time.sleep(20)
    
    print_colored("\n\n--- GOTOWA KONFIGURACJA `PERSONAS` DO WKLEJENIA W `gra_rpg.py` ---", "\033[96m")
    
    final_string = "PERSONAS = " + pprint.pformat(zaktualizowane_persony, indent=4, width=120)
    print(final_string)
    
    # Zapis do pliku
    try:
        with open(NAZWA_PLIKU_WYJSCIOWEGO, 'w', encoding='utf-8') as f:
            f.write(final_string)
        print_colored(f"\nKonfiguracja została również zapisana do pliku: '{NAZWA_PLIKU_WYJSCIOWEGO}'", "\033[92m")
    except Exception as e:
        print_colored(f"\nNie udało się zapisać wyniku do pliku. Błąd: {e}", "\03g[91m")
    
    print_colored("\n--- SKOPIUJ ZAWARTOŚĆ Z PLIKU LUB POWYŻSZY KOD ---", "\033[96m")


if __name__ == "__main__":
    generuj_ukryte_cele()

