"""
Persona Memory Manager - Prosty system zarządzania pamięcią AI
Używa persona_memory.json jako źródło prawdy
"""

import json
import os
from datetime import datetime

MEMORY_FILE = "persona_memory.json"

def load_memory():
    """Wczytaj pamięć wszystkich person"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    return {}

def save_memory(memory):
    """Zapisz pamięć"""
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def get_persona_context(persona_name):
    """
    Zwróć historyczny kontekst persony do wstrzyknięcia w prompt
    
    Returns:
        str: Sformatowany kontekst z track recordem i cechami
    """
    memory = load_memory()
    
    if persona_name not in memory or persona_name == "meta":
        return ""
    
    persona = memory[persona_name]
    stats = persona.get("stats", {})
    traits = persona.get("personality_traits", {})
    
    # Build context string
    context = f"""
╔══════════════════════════════════════════════════════════╗
║  TWOJA PAMIĘĆ I DOŚWIADCZENIE                           ║
╚══════════════════════════════════════════════════════════╝

📊 TWÓJ TRACK RECORD:
"""
    
    if stats.get("decisions_made", 0) > 0:
        context += f"""   • Sesje: {stats.get('sessions_participated', 0)}
   • Decyzje: {stats.get('decisions_made', 0)}
   • Trafne: {stats.get('successful_calls', 0)} ✓
   • Błędne: {stats.get('failed_calls', 0)} ✗
   • Wiarygodność: {stats.get('credibility_score', 1.0)*100:.0f}%
   • Wpływ: {stats.get('total_impact_pln', 0):,.0f} PLN
"""
    else:
        context += "   • To twoja pierwsza decyzja - brak historii\n"
    
    # Personality traits
    if traits:
        context += "\n🧬 TWÓJ CHARAKTER (ewoluuje z czasem):\n"
        for trait, value in traits.items():
            bars = "█" * int(value * 10) + "░" * (10 - int(value * 10))
            context += f"   • {trait.replace('_', ' ').title()}: [{bars}] {value:.1f}\n"
    
    # Recent lessons
    lessons = persona.get("key_lessons", [])
    if lessons:
        context += f"\n📚 KLUCZOWE LEKCJE:\n"
        for lesson in lessons[-3:]:
            if isinstance(lesson, dict):
                context += f"   • [{lesson.get('date', 'N/A')}] {lesson.get('lesson', '')}\n"
            else:
                context += f"   • {lesson}\n"
    
    # Recent audited decisions
    decisions = [d for d in persona.get("decision_history", []) 
                 if d.get("was_correct") is not None]
    if decisions:
        context += f"\n🎯 OSTATNIE ROZLICZONE DECYZJE:\n"
        for dec in decisions[-3:]:
            emoji = "✓" if dec.get("was_correct") else "✗"
            context += f"   {emoji} {dec.get('decision_type', '')} {dec.get('ticker', '')} "
            context += f"({dec.get('result_pct', 0):+.0f}%)\n"
    
    context += """
──────────────────────────────────────────────────────────
⚡ Ta historia wpływa na twoje dzisiejsze rekomendacje.
   Pamiętasz błędy. Uczysz się na doświadczeniu.
──────────────────────────────────────────────────────────

"""
    
    return context

def record_decision(persona_name, decision_type, ticker, reasoning, 
                   current_price, confidence=0.5):
    """
    Zapisz decyzję persony
    
    Args:
        persona_name: Nazwa persony
        decision_type: BUY/SELL/HOLD/WARN/RECOMMEND
        ticker: Symbol
        reasoning: Uzasadnienie
        current_price: Cena przy decyzji
        confidence: 0-1
        
    Returns:
        dict: Decision record z ID
    """
    memory = load_memory()
    
    if persona_name not in memory or persona_name == "meta":
        return None
    
    decision_id = f"{persona_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    decision = {
        "id": decision_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "decision_type": decision_type,
        "ticker": ticker,
        "reasoning": reasoning[:200],  # Limit length
        "current_price": current_price,
        "confidence": confidence,
        "outcome": None,
        "result_price": None,
        "result_pct": None,
        "was_correct": None,
        "impact_pln": None
    }
    
    memory[persona_name]["decision_history"].append(decision)
    memory[persona_name]["stats"]["decisions_made"] += 1
    memory[persona_name]["stats"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    memory["meta"]["total_decisions"] += 1
    
    save_memory(memory)
    
    return decision

def increment_session(persona_name):
    """Zwiększ licznik sesji"""
    memory = load_memory()
    
    if persona_name in memory and persona_name != "meta":
        memory[persona_name]["stats"]["sessions_participated"] += 1
        memory["meta"]["total_sessions"] = memory["meta"].get("total_sessions", 0) + 1
        save_memory(memory)

def get_all_pending_decisions():
    """Zwróć wszystkie nierozliczone decyzje (outcome = None)"""
    memory = load_memory()
    pending = []
    
    for persona_name, data in memory.items():
        if persona_name == "meta":
            continue
        
        for decision in data.get("decision_history", []):
            if decision.get("outcome") is None:
                pending.append({
                    "persona": persona_name,
                    "decision": decision
                })
    
    return pending

def audit_decision(decision_id, current_price, actual_outcome, impact_pln=0):
    """
    Oceń decyzję - czy się sprawdziła?
    
    Returns:
        dict: Updated decision lub None
    """
    memory = load_memory()
    
    for persona_name, data in memory.items():
        if persona_name == "meta":
            continue
        
        for i, dec in enumerate(data.get("decision_history", [])):
            if dec.get("id") == decision_id:
                # Calculate result
                result_pct = ((current_price - dec["current_price"]) / dec["current_price"]) * 100
                
                # Determine correctness
                was_correct = False
                dec_type = dec.get("decision_type", "")
                
                if dec_type == "BUY" and result_pct > 0:
                    was_correct = True
                elif dec_type == "SELL" and result_pct < 0:
                    was_correct = True
                elif dec_type == "WARN" and result_pct < -5:
                    was_correct = True
                elif dec_type == "HOLD" and abs(result_pct) < 10:
                    was_correct = True
                
                # Update decision
                memory[persona_name]["decision_history"][i].update({
                    "outcome": actual_outcome,
                    "result_price": current_price,
                    "result_pct": round(result_pct, 2),
                    "was_correct": was_correct,
                    "impact_pln": impact_pln,
                    "audit_date": datetime.now().strftime("%Y-%m-%d")
                })
                
                # Update stats
                if was_correct:
                    memory[persona_name]["stats"]["successful_calls"] += 1
                else:
                    memory[persona_name]["stats"]["failed_calls"] += 1
                
                memory[persona_name]["stats"]["total_impact_pln"] += impact_pln
                
                # Recalculate credibility
                total = (memory[persona_name]["stats"]["successful_calls"] + 
                        memory[persona_name]["stats"]["failed_calls"])
                if total > 0:
                    memory[persona_name]["stats"]["credibility_score"] = round(
                        memory[persona_name]["stats"]["successful_calls"] / total, 3
                    )
                
                save_memory(memory)
                
                return memory[persona_name]["decision_history"][i]
    
    return None

def add_lesson(persona_name, lesson):
    """Dodaj lekcję do pamięci persony"""
    memory = load_memory()
    
    if persona_name in memory and persona_name != "meta":
        memory[persona_name]["key_lessons"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "lesson": lesson
        })
        save_memory(memory)

def evolve_trait(persona_name, trait, delta):
    """
    Zmień cechę charakteru
    
    Args:
        trait: np. "risk_tolerance"
        delta: zmiana -1 do 1
    """
    memory = load_memory()
    
    if persona_name in memory and persona_name != "meta":
        traits = memory[persona_name].get("personality_traits", {})
        if trait in traits:
            old_value = traits[trait]
            new_value = max(0.0, min(1.0, old_value + delta))
            memory[persona_name]["personality_traits"][trait] = round(new_value, 2)
            save_memory(memory)
            
            return (old_value, new_value)
    
    return None

def get_leaderboard():
    """Ranking person według wiarygodności"""
    memory = load_memory()
    
    leaderboard = []
    for persona_name, data in memory.items():
        if persona_name == "meta":
            continue
        
        stats = data.get("stats", {})
        total = stats.get("successful_calls", 0) + stats.get("failed_calls", 0)
        
        if total > 0:
            leaderboard.append({
                "persona": persona_name,
                "credibility": stats.get("credibility_score", 0),
                "correct": stats.get("successful_calls", 0),
                "total": total,
                "impact": stats.get("total_impact_pln", 0)
            })
    
    leaderboard.sort(key=lambda x: x["credibility"], reverse=True)
    
    return leaderboard
