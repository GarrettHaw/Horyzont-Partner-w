"""Naprawa zniekształconych emoji w menu Streamlit"""

# Wczytaj plik
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Znajdź i napraw linię z menu
for i, line in enumerate(lines):
    if 'Wybierz widok:' in line and i + 1 < len(lines):
        # Linia z listą jest następna
        if '["📊 Dashboard"' in lines[i+1] or '["' in lines[i+1] and 'Dashboard' in lines[i+1]:
            print(f"Znaleziono linię {i+2}: {lines[i+1][:80]}...")
            # Zastąp całą linię
            lines[i+1] = '            ["📊 Dashboard", "💳 Kredyty", "💬 Partnerzy", "📜 Kodeks", "📈 Analiza", "🌍 Rynki", "🕐 Timeline", "📸 Snapshots", "🎮 Symulacje", "⚙️ Ustawienia"],\n'
            print(f"Naprawiono! Nowa wersja: {lines[i+1][:80]}...")
            break

# Zapisz
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Plik naprawiony!")
