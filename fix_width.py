import re

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Zamień use_container_width=True na width="stretch"
content = re.sub(r'use_container_width\s*=\s*True', 'width="stretch"', content)

with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Zamieniono wszystkie wystąpienia use_container_width")
