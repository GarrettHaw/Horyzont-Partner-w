import google.generativeai as genai
import os
import time

# ------------------ KONFIGURACJA ------------------
# WAŻNE: Wklej tutaj swój NOWY, świeżo wygenerowany klucz API
GOOGLE_API_KEY = "AIzaSyDRoccfX5dFHqD20mGfOCRWIO6gRRdiCnk"

# Lista postaci AI do przetworzenia
PERSONAS_DO_ANALIZY = [
    "Partner Strategiczny",
    "Partner ds. Jakości Biznesowej",
    "Partner ds. Aktywów Cyfrowych",
    "Benjamin Graham",
    "Philip Fisher",
    "George Soros",
    "Warren Buffett",
    "Changpeng Zhao (CZ)"
]

# Pliki, które zostaną połączone w jedną, spójną historię
PLIKI_Z_HISTORIA = ["historia_firmy.txt", "kronika_spotkan.txt"]
# ----------------------------------------------------

# Konfiguracja modelu
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-pro')

def print_colored(text, color_code):
    """Drukuje tekst w kolorze."""
    print(f"{color_code}{text}\033[0m")

def kompiluj_pamiec():
    """Główna funkcja kompilująca wspomnienia postaci."""
    print_colored("Rozpoczynam kompilację pamięci dla 'Horyzont Partnerów'...", "\033[93m")

    pelna_historia = ""
    for plik in PLIKI_Z_HISTORIA:
        if os.path.exists(plik):
            try:
                with open(plik, 'r', encoding='utf-8') as f:
                    pelna_historia += f.read() + "\n\n"
                print_colored(f"Pomyślnie wczytano wspomnienia z pliku: '{plik}'.", "\033[92m")
            except Exception as e:
                print_colored(f"Błąd odczytu pliku '{plik}': {e}", "\033[91m")
        else:
            print_colored(f"Informacja: Plik '{plik}' nie został znaleziony, pomijam.", "\033[96m")

    if not pelna_historia:
        print_colored("BŁĄD: Nie wczytano żadnej historii. Przerwanie kompilacji.", "\033[91m")
        return

    print_colored("\nGenerowanie zaktualizowanych bloków pamięci. To potrwa ponad 8 minut...", "\033[93m")

    wynikowy_plik = "NOWE_skompilowane_persony.txt"
    # Otwieramy plik w trybie 'w' (write), aby go wyczyścić przed pętlą
    with open(wynikowy_plik, 'w', encoding='utf-8') as f_out:
        pass # To tylko tworzy/czyści plik

    for persona_name in PERSONAS_DO_ANALIZY:
        print(f"  - Przetwarzanie nowej pamięci dla: {persona_name}...")

        prompt = f"""
        Przeanalizuj cały poniższy zapis rozmowy, który jest historią spotkań firmy 'Horyzont Partnerów'. Wciel się w postać '{persona_name}' i stwórz dla niej zwięzły blok wspomnień w pierwszej osobie. Skup się na kluczowych decyzjach, dyskusjach, relacjach z innymi partnerami i najważniejszych wydarzeniach, które ukształtowały Twoją obecną perspektywę. Twoja odpowiedź musi być wyłącznie tekstem tych wspomnień.

        Oto pełen zapis rozmowy:
        ---
        {pelna_historia}
        ---
        """

        try:
            response = model.generate_content(prompt)

            # Otwieramy plik w trybie 'a' (append), aby dopisywać kolejne wspomnienia
            with open(wynikowy_plik, 'a', encoding='utf-8') as f_out:
                f_out.write(f'# Pamięć dla postaci: {persona_name}\n')
                f_out.write('wspomnienia = """\n')
                f_out.write(response.text.strip())
                f_out.write('\n"""\n\n')

            print_colored(f"    ... Pamięć dla {persona_name} została pomyślnie zaktualizowana.", "\033[92m")

        except Exception as e:
            print_colored(f"    ... Wystąpił błąd podczas przetwarzania postaci {persona_name}: {e}", "\033[91m")

        # Pauza ZAWSZE po każdej próbie, aby nie przekroczyć limitu
        print_colored(f"    ... Czekam 60 sekund, aby nie przekroczyć limitu API...", "\033[90m")
        time.sleep(60)

    print_colored(f"\nGotowe! Nowe, zaktualizowane wspomnienia zapisano w pliku: '{wynikowy_plik}'", "\033[93m")

if __name__ == "__main__":
    kompiluj_pamiec()