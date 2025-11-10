"""Test ładowania PERSONAS z persona_memory.json"""
import os
os.environ['GOOGLE_API_KEY'] = "AIzaSyDRoccfX5dFHqD20mGfOCRWIO6gRRdiCnk"

print("🧪 TESTING PERSONAS LOADING FROM persona_memory.json\n")
print("="*60)

try:
    from gra_rpg import PERSONAS
    
    print(f"\n✅ SUCCESS! Loaded {len(PERSONAS)} partners:")
    print("-" * 60)
    
    for i, (name, config) in enumerate(PERSONAS.items(), 1):
        model = config.get('model_engine', 'unknown')
        color = config.get('color_code', '')
        
        print(f"{i}. {name}")
        print(f"   Model: {model}")
        print(f"   System: {config.get('system_instruction', 'N/A')[:60]}...")
        print(f"   Goal: {config.get('ukryty_cel', 'N/A')[:60]}...")
        print()
    
    print("="*60)
    print(f"\n🎯 EXPECTED: 4 partners (Nexus, Warren, Soros, CZ)")
    print(f"📊 ACTUAL: {len(PERSONAS)} partners")
    
    expected = {'Nexus', 'Warren Buffett', 'George Soros', 'Changpeng Zhao (CZ)'}
    loaded = set(PERSONAS.keys())
    
    if expected == loaded:
        print("✅ ALL EXPECTED PARTNERS LOADED!")
    else:
        print(f"⚠️ MISMATCH!")
        print(f"   Missing: {expected - loaded}")
        print(f"   Extra: {loaded - expected}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
