# -*- coding: utf-8 -*-
"""Fix emoji routing in streamlit_app.py - part 3"""

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all broken emojis in routing
replacements = [
    ('elif page == "�️ Konsultacje":', 'elif page == "🗳️ Konsultacje":'),
    ('elif page == "�📜 Kodeks":', 'elif page == "📜 Kodeks":'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f'✅ Fixed: {old[:30]}...')

with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ All emoji routing fixed!')
