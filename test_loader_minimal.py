"""Minimalny test loadera PERSONAS - bez importu całego gra_rpg"""
import json

def load_personas_from_memory_json(filename="persona_memory.json"):
    """Test wersja - tylko logika loadera"""
    print(f"📂 Ładowanie z {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            memory_data = json.load(f)
    except Exception as e:
        print(f"❌ Błąd wczytywania: {e}")
        return {}
    
    personas = {}
    partner_mappings = {
        'Nexus': {
            'model_engine': 'nexus',
            'color_code': '\033[96m'
        },
        'Warren Buffett': {
            'model_engine': 'gemini',
            'color_code': '\033[92m'
        },
        'George Soros': {
            'model_engine': 'openrouter_mixtral',
            'color_code': '\033[91m'
        },
        'Changpeng Zhao (CZ)': {
            'model_engine': 'openrouter_glm',
            'color_code': '\033[97m'
        }
    }
    
    for partner_name, partner_data in memory_data.items():
        # Skip user
        if 'Partner Zarządzający' in partner_name:
            print(f"  ⏭️  Pomijam: {partner_name} (użytkownik)")
            continue
        
        # Get mapping
        if partner_name in partner_mappings:
            mapping = partner_mappings[partner_name]
            
            persona_config = {
                'model_engine': mapping['model_engine'],
                'system_instruction': partner_data.get('persona', {}).get('expertise', ''),
                'ukryty_cel': partner_data.get('personality', {}).get('hidden_goal', ''),
                'color_code': mapping['color_code']
            }
            
            personas[partner_name] = persona_config
            print(f"  ✅ {partner_name} → {mapping['model_engine']}")
        else:
            print(f"  ⚠️  Nieznany partner: {partner_name}")
    
    return personas

# Test
print("="*70)
print("🧪 TEST LOADERA PERSONAS (standalone)")
print("="*70)
print()

personas = load_personas_from_memory_json()

print()
print("="*70)
print(f"📊 WYNIK: Załadowano {len(personas)} partnerów AI")
print("="*70)

for i, (name, config) in enumerate(personas.items(), 1):
    print(f"\n{i}. {name}")
    print(f"   Engine: {config['model_engine']}")
    print(f"   Expertise: {config['system_instruction'][:80]}...")
    print(f"   Goal: {config['ukryty_cel'][:80]}...")

print()
print("="*70)
expected = {'Nexus', 'Warren Buffett', 'George Soros', 'Changpeng Zhao (CZ)'}
loaded = set(personas.keys())

if expected == loaded:
    print("✅ TEST PASSED! Wszystkie oczekiwane partnery załadowane!")
else:
    print("⚠️ TEST FAILED!")
    print(f"   Brakuje: {expected - loaded}")
    print(f"   Dodatkowe: {loaded - expected}")
