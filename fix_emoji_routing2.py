# -*- coding: utf-8 -*-
"""Fix emoji routing in streamlit_app.py - part 2"""

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    # Fix Powiadomienia
    if 'elif page == "' in line and 'Powiadomienia":' in line:
        line = '    elif page == "📧 Powiadomienia":\n'
    # Fix Kodeks (jeśli jeszcze nie naprawione)
    elif 'elif page == "' in line and 'Kodeks":' in line and '📜' not in line:
        line = '    elif page == "📜 Kodeks":\n'
    
    fixed_lines.append(line)

with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('✅ Fixed emoji routing!')
