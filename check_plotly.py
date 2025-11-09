import re

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Znajdź wszystkie st.plotly_chart z tylko fig i width
# Nic nie musimy zmieniać - width="stretch" jest OK dla Streamlit
# Problem może być z innymi argumentami przekazywanymi do plotly

# Sprawdźmy czy są jakieś inne argumenty
matches = re.findall(r'st\.plotly_chart\([^)]+\)', content)
print("Znalezione wywołania st.plotly_chart:")
for i, match in enumerate(matches[:5], 1):  # Pokaż pierwsze 5
    print(f"{i}. {match}")
