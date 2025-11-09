# -*- coding: utf-8 -*-
"""Fix emoji encoding in streamlit_app.py"""

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix corrupted emojis
content = content.replace(
    'elif page == "�️ Rozmowy Rady":',
    'elif page == "🗣️ Rozmowy Rady":'
)

content = content.replace(
    'elif page == "�📜 Kodeks":',
    'elif page == "📜 Kodeks":'
)

with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed emoji encoding in routing!")
