"""
Naprawia kodowanie w persona_memory.json
"""
import json

# Wczytaj plik z błędnym kodowaniem
with open('persona_memory.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Napraw znaki
replacements = {
    'ZarzÄ…dzajÄ…cy': 'Zarządzający',
    'przygodÄ™': 'przygodę',
    'RadÄ…': 'Radą',
    'PartnerĂłw': 'Partnerów',
    'dzieĹ„': 'dzień',
    'JakoĹ›ci': 'Jakości',
    'AktywĂłw': 'Aktywów',
    'wpĹ‚yw': 'wpływ',
    'filozoficzny': 'filozoficzny',
    'strategicznych': 'strategicznych',
    'doĹ›wiadczenie': 'doświadczenie',
    'spekulacji': 'spekulacji',
    'dĹ‚ugiej': 'długiej',
    'perspektywie': 'perspektywie',
    'inwestycji': 'inwestycji',
    'cyfrowych': 'cyfrowych',
    'spekulujÄ™': 'spekuluję',
    'inwestujÄ™': 'inwestuję',
    'Ĺ›wiadomie': 'świadomie',
    'DĹ‚ugookresowe': 'Długookresowe',
    'bezpieczeĹ„stwo': 'bezpieczeństwo',
    'inwestowania': 'inwestowania',
    'WĹ‚aĹ›ciwe': 'Właściwe',
    'wyceny': 'wyceny',
    'Ĺ›rodki': 'środki',
    'zrozumienie': 'zrozumienie',
    'technologii': 'technologii',
    'decyzjami': 'decyzjami',
    'Spekulacja': 'Spekulacja',
    'kontrolowana': 'kontrolowana',
    'może': 'może',
    'być': 'być',
    'zyskowna': 'zyskowna',
    'RĂłwnowaĹĽenie': 'Równoważenie',
    'portfela': 'portfela',
    'miÄ™dzy': 'między',
    'tradycyjnymi': 'tradycyjnymi',
    'aktywami': 'aktywami',
    'jest': 'jest',
    'kluczowe': 'kluczowe',
}

for bad, good in replacements.items():
    content = content.replace(bad, good)

# Zapisz naprawiony plik
with open('persona_memory.json', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Naprawiono kodowanie w persona_memory.json")

# Zweryfikuj że można wczytać jako JSON
try:
    with open('persona_memory.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Plik JSON jest poprawny ({len(data)} partnerów)")
except Exception as e:
    print(f"❌ Błąd: {e}")
