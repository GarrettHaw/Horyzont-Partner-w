#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild persona_memory.json - keep only 5 partners
"""
import json
from datetime import datetime

# Load current file
with open('persona_memory.json', 'r', encoding='utf-8') as f:
    old_data = json.load(f)

# Partners to KEEP (4 + we'll add Nexus later)
KEEP_PARTNERS = [
    "Partner Zarządzający (JA)",
    "Warren Buffett",
    "George Soros",
    "Changpeng Zhao (CZ)"
]

# Create new structure with only kept partners
new_data = {}

for partner_name in KEEP_PARTNERS:
    if partner_name in old_data:
        partner_data = old_data[partner_name].copy()
        
        # Clean up relationships - remove deleted partners
        if "relationships" in partner_data:
            cleaned_relationships = {}
            for rel_partner, rel_data in partner_data["relationships"].items():
                if rel_partner in KEEP_PARTNERS:
                    cleaned_relationships[rel_partner] = rel_data
            partner_data["relationships"] = cleaned_relationships
        
        new_data[partner_name] = partner_data
        print(f"✅ Kept: {partner_name}")
    else:
        print(f"⚠️ Not found: {partner_name}")

# Add Nexus AI Strategic Advisor
new_data["Nexus"] = {
    "stats": {
        "sessions_participated": 0,
        "decisions_made": 0,
        "successful_calls": 0,
        "failed_calls": 0,
        "credibility_score": 1.0,
        "total_impact_pln": 0,
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    },
    "personality_traits": {
        "risk_tolerance": 0.5,
        "analytical_depth": 1.0,
        "emotional_stability": 1.0,
        "data_dependency": 1.0,
        "pragmatism": 0.95,
        "optimism_bias": 0.0,
        "confidence_level": 0.9
    },
    "decision_history": [],
    "relationships": {
        "Partner Zarządzający (JA)": {
            "trust": 0.9,
            "agreement_rate": 0.0,
            "collaborative_decisions": 0
        },
        "Warren Buffett": {
            "trust": 0.8,
            "agreement_rate": 0.0,
            "collaborative_decisions": 0
        },
        "George Soros": {
            "trust": 0.8,
            "agreement_rate": 0.0,
            "collaborative_decisions": 0
        },
        "Changpeng Zhao (CZ)": {
            "trust": 0.85,
            "agreement_rate": 0.0,
            "collaborative_decisions": 0
        }
    },
    "expertise": {
        "sectors": [
            "Portfolio Optimization",
            "Risk Management",
            "Quantitative Analysis",
            "Tax Optimization",
            "Asset Allocation"
        ],
        "market_caps": ["All"],
        "geographies": ["Global"],
        "asset_classes": ["Stocks", "Crypto", "Bonds", "Commodities", "Real Estate"],
        "special_skills": [
            "Monte Carlo Simulation",
            "Machine Learning",
            "Sentiment Analysis",
            "Multi-model Ensemble",
            "Real-time Data Integration"
        ]
    },
    "predictions": [],
    "communication_style": {
        "opening": "Widzę [problem/okazję]. Analiza zakończona.",
        "body": "Dane pokazują: [facts]. Rekomendacja: [action] (confidence: X%)",
        "closing": "Questions? / Gotowy na implementację.",
        "when_wrong": "Noted. Aktualizuję model.",
        "tone": "concise, data-driven, professional",
        "use_emotions": False
    },
    "voting": {
        "base_weight": 13.75,
        "credibility_bonus": 0.0,
        "effective_weight": 13.75
    },
    "ai_config": {
        "models": ["gpt-4", "claude-3.5-sonnet", "gemini-pro"],
        "ensemble_weights": {
            "gpt-4": 0.4,
            "claude-3.5-sonnet": 0.4,
            "gemini-pro": 0.2
        },
        "tools_access": [
            "CoinGecko API",
            "Yahoo Finance API",
            "FRED API",
            "Trading212 API",
            "Fear & Greed Index",
            "NewsAPI"
        ],
        "data_sources": {
            "tier_1_local": [
                "transactions.json",
                "portfolio",
                "kredyty.json",
                "wyplaty.json",
                "calendar_events.json",
                "daily_snapshots.json",
                "cele.json"
            ],
            "tier_2_apis": [
                "CoinGecko",
                "Yahoo Finance",
                "FRED",
                "Fear & Greed Index"
            ],
            "tier_3_broker": [
                "Trading212"
            ]
        }
    },
    "scoring": {
        "predictions_tracked": [],
        "win_count": 0,
        "loss_count": 0,
        "win_rate": 0.0,
        "current_weight": 13.75,
        "weight_history": [
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "weight": 13.75,
                "reason": "Initial setup"
            }
        ],
        "monthly_performance": []
    }
}

# Update relationships for existing partners to include Nexus
for partner_name in KEEP_PARTNERS:
    if partner_name in new_data:
        if "relationships" not in new_data[partner_name]:
            new_data[partner_name]["relationships"] = {}
        
        # Add Nexus to their relationships
        new_data[partner_name]["relationships"]["Nexus"] = {
            "trust": 0.75,
            "agreement_rate": 0.0,
            "collaborative_decisions": 0
        }

# Reorder: JA first, then Nexus, then alphabetically
ordered_data = {}
ordered_data["Partner Zarządzający (JA)"] = new_data["Partner Zarządzający (JA)"]
ordered_data["Nexus"] = new_data["Nexus"]
ordered_data["Warren Buffett"] = new_data["Warren Buffett"]
ordered_data["George Soros"] = new_data["George Soros"]
ordered_data["Changpeng Zhao (CZ)"] = new_data["Changpeng Zhao (CZ)"]

# Save new file
with open('persona_memory.json', 'w', encoding='utf-8') as f:
    json.dump(ordered_data, f, indent=2, ensure_ascii=False)

print("\n" + "="*50)
print("✅ REBUILD COMPLETE!")
print("="*50)
print(f"Old partners: {len(old_data)}")
print(f"New partners: {len(ordered_data)}")
print("\nFinal lineup:")
for i, name in enumerate(ordered_data.keys(), 1):
    print(f"  {i}. {name}")
