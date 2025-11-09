"""
Upgrade persona_memory.json do wersji 2.0 - EPIC AI SYSTEM
Dodaje: emotions, relationships, expertise, predictions, personality, knowledge, agendas, meta-learning
"""

import json
import os
from datetime import datetime

MEMORY_FILE = "persona_memory.json"

def upgrade_persona_memory():
    """Upgrade existing memory to v2.0 with all new systems"""
    
    print("🚀 Upgrading Persona Memory to v2.0...")
    
    # Load existing
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory = json.load(f)
    else:
        print("❌ persona_memory.json not found!")
        return
    
    all_personas = [p for p in memory.keys() if p != "meta"]
    
    for persona_name in all_personas:
        persona = memory[persona_name]
        
        print(f"\n📝 Upgrading {persona_name}...")
        
        # 1. EMOTIONAL STATE
        if "emotional_state" not in persona:
            persona["emotional_state"] = {
                "current_mood": "neutral",  # happy, confident, worried, frustrated, cautious
                "stress_level": 0.3,
                "excitement": 0.4,
                "fear_index": 0.2,
                "last_emotion_change": datetime.now().strftime("%Y-%m-%d"),
                "mood_history": []
            }
            print("  ✓ Added emotional_state")
        
        # 2. RELATIONSHIPS (with other personas)
        if "relationships" not in persona:
            relationships = {}
            for other_persona in all_personas:
                if other_persona != persona_name:
                    # Initialize neutral relationship
                    relationships[other_persona] = {
                        "trust": 0.5,
                        "agreement_rate": 0.5,
                        "conflicts": 0,
                        "alliances": 0,
                        "last_interaction": "neutral",
                        "notable_moments": []
                    }
            persona["relationships"] = relationships
            print(f"  ✓ Added relationships ({len(relationships)} personas)")
        
        # 3. EXPERTISE AREAS
        if "expertise" not in persona:
            persona["expertise"] = {
                "sectors": {
                    "Technology": 0.5,
                    "Financials": 0.5,
                    "Healthcare": 0.5,
                    "Energy": 0.5,
                    "Consumer": 0.5,
                    "Industrials": 0.5
                },
                "market_caps": {
                    "mega_cap": 0.7,
                    "large_cap": 0.6,
                    "mid_cap": 0.5,
                    "small_cap": 0.4
                },
                "geographies": {
                    "US": 0.8,
                    "Europe": 0.6,
                    "Asia": 0.5,
                    "Emerging": 0.4
                },
                "asset_classes": {
                    "stocks": 0.8,
                    "crypto": 0.3,
                    "bonds": 0.4,
                    "commodities": 0.3
                }
            }
            print("  ✓ Added expertise areas")
        
        # 4. PREDICTIONS SYSTEM
        if "predictions" not in persona:
            persona["predictions"] = []
            persona["prediction_stats"] = {
                "total_predictions": 0,
                "correct_predictions": 0,
                "prediction_accuracy": 0.0,
                "best_category": None,
                "worst_category": None
            }
            print("  ✓ Added predictions system")
        
        # 5. COMMUNICATION STYLE
        if "communication_style" not in persona:
            persona["communication_style"] = {
                "verbosity": 0.6,
                "technicality": 0.6,
                "humor": 0.2,
                "formality": 0.7,
                "emoji_usage": 0.1,
                "catchphrases": [],
                "typical_opening": "",
                "signature_style": ""
            }
            print("  ✓ Added communication_style")
        
        # 6. KNOWLEDGE BASE REFERENCES
        if "knowledge_references" not in persona:
            persona["knowledge_references"] = []
            persona["knowledge_stats"] = {
                "articles_read": 0,
                "articles_referenced": 0,
                "favorite_sources": [],
                "last_knowledge_update": datetime.now().strftime("%Y-%m-%d")
            }
            print("  ✓ Added knowledge_references")
        
        # 7. PERSONAL AGENDA
        if "personal_agenda" not in persona:
            persona["personal_agenda"] = {
                "primary_goal": "Support portfolio growth",
                "progress": 0.0,
                "tactics": [],
                "milestones": [],
                "secret_motivations": []
            }
            print("  ✓ Added personal_agenda")
        
        # 8. META-LEARNING
        if "meta_learning" not in persona:
            persona["meta_learning"] = {
                "mistake_categories": {
                    "overconfidence": 0,
                    "ignored_warnings": 0,
                    "herd_mentality": 0,
                    "timing_errors": 0,
                    "scope_creep": 0
                },
                "improvement_strategies": [],
                "learning_rate": 0.5,
                "adaptation_speed": 0.5,
                "meta_credibility": 1.0
            }
            print("  ✓ Added meta_learning")
        
        # 9. VOTING SYSTEM (dynamic weights)
        if "voting" not in persona:
            # Get base weight from Kodeks
            base_weights = {
                "Partner Zarządzający (JA)": 35,
                "Ja (Partner Strategiczny)": 30,
                "Partner ds. Jakości Biznesowej": 5,
                "Partner ds. Aktywów Cyfrowych": 5,
                "Benjamin Graham": 5,
                "Philip Fisher": 5,
                "George Soros": 5,
                "Warren Buffett": 5,
                "Changpeng Zhao (CZ)": 5
            }
            
            base_weight = base_weights.get(persona_name, 5)
            
            persona["voting"] = {
                "base_weight": base_weight,
                "credibility_bonus": 0,
                "recent_streak_bonus": 0,
                "effective_weight": base_weight,
                "voting_history": [],
                "influence_score": 1.0
            }
            print(f"  ✓ Added voting (base: {base_weight}%)")
    
    # Update meta
    memory["meta"]["schema_version"] = "2.0"
    memory["meta"]["last_upgrade"] = datetime.now().isoformat()
    memory["meta"]["features"] = [
        "emotional_state",
        "relationships",
        "expertise",
        "predictions",
        "communication_style",
        "knowledge_base",
        "personal_agenda",
        "meta_learning",
        "dynamic_voting"
    ]
    
    # Save
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Upgrade complete!")
    print(f"   Schema: v2.0")
    print(f"   Personas upgraded: {len(all_personas)}")
    print(f"   New features: {len(memory['meta']['features'])}")
    print(f"\n💾 Saved to {MEMORY_FILE}")

if __name__ == "__main__":
    upgrade_persona_memory()
