import google.generativeai as genai
import os

# ------------------ KONFIGURACJA ------------------
# Wklej tutaj swój NOWY, świeżo wygenerowany klucz API
GOOGLE_API_KEY = "AIzaSyDRoccfX5dFHqD20mGfOCRWIO6gRRdiCnk"
NAZWA_PLIKU_HISTORII = "historia_firmy.txt"
NAZWA_PLIKU_WYJSCIOWEGO = "glowne_streszczenie.txt"
# ----------------------------------------------------

# Konfiguracja modelu
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-pro')

def print_colored(text, color_code):
    print(f"{color_code}{text}\033[0m")

def stworz_streszczenie():
    print_colored("Rozpoczynam tworzenie Głównego Streszczenia...", "\033[93m")
    
    if not os.path.exists(NAZWA_PLIKU_HISTORII):
        print_colored(f"BŁĄD: Nie znaleziono pliku '{NAZWA_PLIKU_HISTORII}'.", "\033[91m")
        return
        
    with open(NAZWA_PLIKU_HISTORII, 'r', encoding='utf-8') as f:
        pelna_historia = f.read()
    
    print_colored("Wysyłam całą historię do AI. To może potrwać kilka minut...", "\033[96m")
    
    prompt = f"""
    Przeanalizuj cały poniższy zapis rozmowy, który jest historią spotkań firmy 'Horyzont Partnerów'. 
    Twoim zadaniem jest stworzenie jednego, zwięzłego, ale szczegółowego streszczenia wszystkich kluczowych wydarzeń, decyzji, konfliktów i dyskusji. 
    Skup się na chronologii i najważniejszych punktach zwrotnych w historii firmy. 
    Twoja odpowiedź musi być wyłącznie tekstem tego streszczenia.

    Oto pełen zapis rozmowy:
    ---
    {pelna_historia}
    ---
    """
    
    try:
        response = model.generate_content(prompt)
        with open(NAZWA_PLIKU_WYJSCIOWEGO, 'w', encoding='utf-8') as f_out:
            f_out.write(response.text.strip())
        print_colored(f"Sukces! Główne Streszczenie zostało zapisane w pliku: '{NAZWA_PLIKU_WYJSCIOWEGO}'", "\033[92m")
    except Exception as e:
        print_colored(f"Wystąpił błąd: {e}", "\033[91m")
        print_colored("Prawdopodobnie plik historia_firmy.txt jest zbyt duży nawet na jedno zapytanie. Rozważ jego ręczne skrócenie do najważniejszych fragmentów.", "\033[93m")

if __name__ == "__main__":
    stworz_streszczenie()