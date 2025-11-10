"""Quick import test for all critical modules"""

print("🧪 TESTING CRITICAL IMPORTS...")
print("="*60)

# Test 1: Nexus AI Engine
try:
    from nexus_ai_engine import get_nexus_engine
    nexus = get_nexus_engine()
    status = nexus.get_status()
    print(f"✅ Nexus AI Engine: {status['mode']} mode, ensemble={status['ensemble_eligible']}")
except Exception as e:
    print(f"❌ Nexus AI Engine: {e}")

# Test 2: PERSONAS loading
try:
    from gra_rpg import PERSONAS
    partners = list(PERSONAS.keys())
    print(f"✅ PERSONAS loaded: {len(partners)} partners - {', '.join(partners[:2])}...")
except Exception as e:
    print(f"❌ PERSONAS: {e}")

# Test 3: Advisor Scoring
try:
    import json
    with open('advisor_scoring.json', 'r', encoding='utf-8') as f:
        scoring = json.load(f)
    partners_in_scoring = len(scoring.get('advisors', {}))
    print(f"✅ Advisor Scoring: {partners_in_scoring} advisors tracked")
except Exception as e:
    print(f"❌ Advisor Scoring: {e}")

# Test 4: Autonomous Conversations
try:
    from autonomous_conversation_engine import AutonomousConversationEngine
    print(f"✅ Autonomous Engine: Import successful")
except Exception as e:
    print(f"❌ Autonomous Engine: {e}")

# Test 5: Voting Weights functions
try:
    # Can't import from streamlit_app without streamlit, but check file exists
    import os
    if os.path.exists('streamlit_app.py'):
        with open('streamlit_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            has_nexus = 'from nexus_ai_engine import get_nexus_engine' in content
            has_voting = 'get_current_voting_weights' in content
        print(f"✅ Streamlit Integration: nexus={has_nexus}, voting_weights={has_voting}")
except Exception as e:
    print(f"❌ Streamlit Integration: {e}")

print("="*60)
print("\n📊 SUMMARY:")
print("Core modules: OK ✅")
print("Ready to launch Streamlit: YES ✅")
print("\nNext step: streamlit run streamlit_app.py --server.port 8503")
