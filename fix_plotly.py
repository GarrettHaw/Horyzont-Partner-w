import re

# Wczytaj plik
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Zamień deprecated syntax na nowy
content = re.sub(
    r'st\.plotly_chart\(fig, width="stretch"\)',
    'st.plotly_chart(fig, use_container_width=True)',
    content
)

# Zapisz
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Zamieniono wszystkie 9 instancji st.plotly_chart()")
