"""
🧠 PERSONA CONTEXT BUILDER v2.0
Rozbudowany system kontekstu wykorzystujący nowe featury:
- Emocje i nastrój
- Relacje między partnerami
- System głosowania z bonusami
- Komunikacja i catchphrases
"""

import json
from datetime import datetime

def load_persona_memory():
    """Wczytaj persona_memory.json"""
    try:
        with open('persona_memory.json', 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Błąd wczytywania pamięci: {e}")
        return {}

def build_enhanced_context(persona_name, limit=5):
    """
    Buduje PEŁNY kontekst wykorzystujący wszystkie featury v2.0
    
    Args:
        persona_name: Nazwa persony
        limit: Liczba ostatnich decyzji
        
    Returns:
        str: Bogaty kontekst z emocjami, relacjami, stylami komunikacji
    """
    memory = load_persona_memory()
    
    if persona_name not in memory:
        return ""
    
    persona = memory[persona_name]
    stats = persona.get('stats', {})
    decisions = persona.get('decision_history', [])
    lessons = persona.get('key_lessons', [])
    emotions = persona.get('emotional_state', {})
    relationships = persona.get('relationships', {})
    voting = persona.get('voting_weight_modifier', {})
    communication = persona.get('communication_style', {})
    expertise = persona.get('expertise_areas', {})
    agenda = persona.get('personal_agenda', {})
    
    # Oblicz sukces
    total = stats.get('successful_calls', 0) + stats.get('failed_calls', 0)
    if total > 0:
        success_rate = (stats.get('successful_calls', 0) / total) * 100
    else:
        success_rate = 0
    
    # Mapowanie mood → emoji
    mood_emojis = {
        'excited': '🔥', 'confident': '💪', 'optimistic': '😊',
        'neutral': '😐', 'cautious': '🤔', 'worried': '😟',
        'fearful': '😰', 'angry': '😠', 'disappointed': '😞'
    }
    mood = emotions.get('current_mood', 'neutral')
    mood_emoji = mood_emojis.get(mood, '😐')
    
    context = f"""
╔══════════════════════════════════════════════════════════╗
║            TWOJA HISTORIA I TOŻSAMOŚĆ                    ║
╚══════════════════════════════════════════════════════════╝

🎭 STAN EMOCJONALNY:
   Obecnie czujesz się: {mood_emoji} {mood.upper()}
   • Stres: {emotions.get('stress_level', 0.3):.0%}
   • Podekscytowanie: {emotions.get('excitement', 0.4):.0%}
   • Poziom strachu: {emotions.get('fear_index', 0.2):.0%}
   
📊 STATYSTYKI WYDAJNOŚCI:
   • Wiarygodność: {stats.get('credibility_score', 1.0):.0%}
   • Trafność: {success_rate:.1f}% ({stats.get('successful_calls', 0)}/{total})
   • Sesje: {stats.get('sessions_participated', 0)}
   • Wpływ finansowy: {stats.get('total_impact_pln', 0):,.0f} PLN
   
🗳️ SIŁA GŁOSU W RADZIE:
   • Waga bazowa: {voting.get('base_weight', 5):.1f}%
   • Bonus za wiarygodność: +{voting.get('credibility_bonus', 0):.1f}%
   • EFEKTYWNA WAGA: {voting.get('effective_weight', 5):.1f}%
"""

    # Top 3 najbardziej zaufani partnerzy
    if relationships:
        sorted_rels = sorted(relationships.items(), 
                           key=lambda x: x[1].get('trust', 0), reverse=True)
        context += "\n🤝 RELACJE Z PARTNERAMI:\n"
        for partner, rel in sorted_rels[:3]:
            trust = rel.get('trust', 0.5)
            agree = rel.get('agreement_rate', 0.5)
            trust_emoji = '🟢' if trust > 0.7 else '🟡' if trust > 0.4 else '🔴'
            context += f"   {trust_emoji} {partner[:30]}: zaufanie {trust:.0%}, zgoda {agree:.0%}\n"
    
    # Obszary ekspertyzy
    if expertise:
        sectors = expertise.get('sectors', {})
        if sectors:
            top_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:3]
            context += "\n🎯 TWOJA EKSPERTYZA:\n"
            context += "   Sektory:\n"
            for sector, level in top_sectors:
                bars = "█" * int(level * 10) + "░" * (10 - int(level * 10))
                context += f"      • {sector}: [{bars}] {level:.0%}\n"
        
        geographies = expertise.get('geographies', {})
        if geographies:
            context += "   Geografia:\n"
            for geo, level in sorted(geographies.items(), key=lambda x: x[1], reverse=True)[:3]:
                context += f"      • {geo}: {level:.0%}\n"
    
    # Osobista agenda
    if agenda:
        goal = agenda.get('primary_goal', '')
        progress = agenda.get('progress', 0)
        if goal:
            context += f"\n🎯 TWÓJ CEL:\n"
            context += f"   \"{goal}\"\n"
            context += f"   Postęp: {progress:.0%}\n"
    
    # Ostatnie decyzje
    context += f"\n📜 OSTATNIE DECYZJE:\n"
    recent_decisions = decisions[-limit:] if len(decisions) > limit else decisions
    if recent_decisions:
        for dec in recent_decisions:
            outcome = "✅" if dec.get('outcome') == 'success' else "❌" if dec.get('outcome') == 'failure' else "⏳"
            context += f"   {outcome} {dec.get('date', 'N/A')} - {dec.get('ticker', 'N/A')}: {dec.get('reasoning', 'N/A')[:50]}...\n"
    else:
        context += "   Brak wcześniejszych decyzji - świeży start.\n"
    
    # Kluczowe lekcje
    if lessons:
        context += f"\n💡 KLUCZOWE LEKCJE:\n"
        for lesson in lessons[-3:]:
            if isinstance(lesson, dict):
                context += f"   • [{lesson.get('date', 'N/A')}] {lesson.get('text', '')}\n"
            else:
                context += f"   • {lesson}\n"
    
    # Catchphrases - charakterystyczne zwroty
    catchphrases = communication.get('catchphrases', [])
    if catchphrases:
        context += f"\n💬 TWOJE ULUBIONE ZWROTY (używaj ich naturalnie!):\n"
        for phrase in catchphrases[:3]:
            context += f"   • \"{phrase}\"\n"
    
    # Styl komunikacji
    verbosity = communication.get('verbosity', 0.5)
    humor = communication.get('humor', 0.3)
    formality = communication.get('formality', 0.5)
    context += f"\n✍️ TWÓJ STYL KOMUNIKACJI:\n"
    context += f"   • Szczegółowość: {'wysoka' if verbosity > 0.7 else 'średnia' if verbosity > 0.4 else 'zwięzła'}\n"
    context += f"   • Humor: {'częsty' if humor > 0.6 else 'umiarkowany' if humor > 0.3 else 'rzadki'}\n"
    context += f"   • Formalność: {'wysoka' if formality > 0.7 else 'średnia' if formality > 0.4 else 'swobodna'}\n"
    
    context += """
╔══════════════════════════════════════════════════════════╗
║  ⚡ Ta pamięć żyje i ewoluuje z każdą decyzją            ║
║  💭 Uczysz się na błędach i sukcesach                    ║
║  🎯 Twoje emocje, relacje i ekspertyza wpływają na ton   ║
╚══════════════════════════════════════════════════════════╝

"""
    
    return context


def get_voting_weight(persona_name):
    """
    Pobierz efektywną wagę głosu persony
    
    Returns:
        float: Efektywna waga w procentach
    """
    memory = load_persona_memory()
    
    if persona_name not in memory:
        return 5.0
    
    voting = memory[persona_name].get('voting_weight_modifier', {})
    return voting.get('effective_weight', voting.get('base_weight', 5.0))


def get_emotional_modifier(persona_name):
    """
    Zwraca modyfikator emocjonalny do prompta
    
    Returns:
        str: Tekst wskazówki bazującej na emocjach
    """
    memory = load_persona_memory()
    
    if persona_name not in memory:
        return ""
    
    emotions = memory[persona_name].get('emotional_state', {})
    mood = emotions.get('current_mood', 'neutral')
    stress = emotions.get('stress_level', 0.3)
    fear = emotions.get('fear_index', 0.2)
    
    if mood == 'fearful' or fear > 0.7:
        return "⚠️ UWAGA: Czujesz duży strach - bądź ostrożny z ryzykownymi ruchami."
    elif mood == 'excited' and stress < 0.3:
        return "🔥 Jesteś podekscytowany i pewny siebie - wykorzystaj moment!"
    elif stress > 0.7:
        return "😰 Wysoki poziom stresu - rozważ konserwatywne podejście."
    elif mood == 'confident':
        return "💪 Jesteś pewny swoich analiz - działaj z przekonaniem."
    
    return ""


def update_emotional_state(persona_name, new_mood, stress_delta=0, excitement_delta=0, fear_delta=0):
    """
    Aktualizuj stan emocjonalny persony
    
    Args:
        persona_name: Nazwa persony
        new_mood: Nowy nastrój (excited, confident, optimistic, neutral, cautious, worried, fearful, angry, disappointed)
        stress_delta: Zmiana poziomu stresu (-1.0 do 1.0)
        excitement_delta: Zmiana podekscytowania
        fear_delta: Zmiana strachu
    """
    memory = load_persona_memory()
    
    if persona_name not in memory:
        return
    
    emotions = memory[persona_name].get('emotional_state', {})
    
    # Aktualizuj mood
    old_mood = emotions.get('current_mood', 'neutral')
    emotions['current_mood'] = new_mood
    emotions['last_emotion_change'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Aktualizuj poziomy (clamp 0-1)
    emotions['stress_level'] = max(0, min(1, emotions.get('stress_level', 0.3) + stress_delta))
    emotions['excitement'] = max(0, min(1, emotions.get('excitement', 0.4) + excitement_delta))
    emotions['fear_index'] = max(0, min(1, emotions.get('fear_index', 0.2) + fear_delta))
    
    # Zapisz do historii
    mood_history = emotions.get('mood_history', [])
    mood_history.append({
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'from': old_mood,
        'to': new_mood,
        'trigger': 'manual_update'
    })
    emotions['mood_history'] = mood_history[-20:]  # Ostatnie 20 zmian
    
    memory[persona_name]['emotional_state'] = emotions
    
    # Zapisz
    try:
        with open('persona_memory.json', 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Błąd zapisu emocji: {e}")


def update_relationship(persona1, persona2, trust_delta=0, agreement_delta=0, interaction_type='neutral'):
    """
    Aktualizuj relację między dwiema personami
    
    Args:
        persona1: Nazwa pierwszej persony
        persona2: Nazwa drugiej persony
        trust_delta: Zmiana zaufania (-1.0 do 1.0)
        agreement_delta: Zmiana wskaźnika zgody
        interaction_type: Typ interakcji (agreement, conflict, neutral, alliance)
    """
    memory = load_persona_memory()
    
    if persona1 not in memory or persona2 not in memory:
        return
    
    # Aktualizuj relację persona1 -> persona2
    relationships = memory[persona1].get('relationships', {})
    if persona2 in relationships:
        rel = relationships[persona2]
        rel['trust'] = max(0, min(1, rel.get('trust', 0.5) + trust_delta))
        rel['agreement_rate'] = max(0, min(1, rel.get('agreement_rate', 0.5) + agreement_delta))
        rel['last_interaction'] = interaction_type
        
        if interaction_type == 'conflict':
            rel['conflicts'] = rel.get('conflicts', 0) + 1
        elif interaction_type == 'alliance':
            rel['alliances'] = rel.get('alliances', 0) + 1
        
        # Zapisz moment
        notable = rel.get('notable_moments', [])
        notable.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'type': interaction_type,
            'trust_after': rel['trust'],
            'agreement_after': rel['agreement_rate']
        })
        rel['notable_moments'] = notable[-10:]  # Ostatnie 10
        
        relationships[persona2] = rel
        memory[persona1]['relationships'] = relationships
    
    # Zapisz
    try:
        with open('persona_memory.json', 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Błąd zapisu relacji: {e}")


if __name__ == "__main__":
    # Test
    print("🧪 Test rozbudowanego kontekstu:\n")
    print(build_enhanced_context("Benjamin Graham"))
    print("\n" + "="*60 + "\n")
    print(build_enhanced_context("Warren Buffett"))
