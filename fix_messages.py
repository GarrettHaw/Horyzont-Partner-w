import re

# Czytaj plik
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Znajdź początek i koniec funkcji show_partners_page
start_marker = "def show_partners_page():"
end_marker = "\ndef show_consultations_page():"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find function boundaries")
    exit(1)

# Wyciągnij funkcję
before_function = content[:start_idx]
function_content = content[start_idx:end_idx]
after_function = content[end_idx:]

# Zamiany wewnątrz funkcji (tylko w show_partners_page)
replacements = [
    (r'st\.session_state\.messages\.append\(', 'add_message('),
    (r'st\.session_state\.messages\s*=\s*\[\]', 'clear_messages()'),
    (r'for msg in st\.session_state\.messages:', 'for msg in get_messages():'),
    (r'\[m for m in st\.session_state\.messages if', '[m for m in get_messages() if'),
]

modified_function = function_content
for pattern, replacement in replacements:
    modified_function = re.sub(pattern, replacement, modified_function)

# Złóż z powrotem
new_content = before_function + modified_function + after_function

# Zapisz
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Fixed all st.session_state.messages references in show_partners_page()")
