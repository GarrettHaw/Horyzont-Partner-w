"""
Monthly Audit v2.0 - Automatyczne rozliczenie decyzji AI Partners
Uruchamiaj co miesiąc aby ocenić czy prognozy person się sprawdziły

NOWE FEATURY v2.0:
- Aktualizacja emocji bazując na wynikach
- Ewolucja personality traits
- System bonusów do voting weight
- Rozliczanie predictions (nowy format)
"""

import persona_memory_manager as pmm
from persona_context_builder import update_emotional_state, load_persona_memory
import json
import yfinance as yf
from datetime import datetime, timedelta

def get_current_price(ticker):
    """Pobierz aktualną cenę tickera"""
    try:
        # Obsługa różnych formatów
        if ticker.endswith('_EQ'):
            ticker = ticker.replace('_EQ', '')
        
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except Exception as e:
        print(f"⚠️ Błąd pobierania ceny {ticker}: {e}")
    
    return None

def auto_audit_all_pending():
    """
    Automatycznie oceń wszystkie nierozliczone decyzje
    które są starsze niż 30 dni
    """
    print("🔍 Rozpoczynam miesięczny audit decyzji AI...")
    print("="*60)
    
    pending = pmm.get_all_pending_decisions()
    
    if not pending:
        print("✓ Brak nierozliczonych decyzji")
        return
    
    print(f"Znaleziono {len(pending)} nierozliczonych decyzji\n")
    
    audited_count = 0
    skipped_count = 0
    
    for item in pending:
        persona = item["persona"]
        dec = item["decision"]
        
        # Sprawdź wiek decyzji
        dec_date = datetime.fromisoformat(dec["timestamp"])
        age_days = (datetime.now() - dec_date).days
        
        # Audit tylko decyzji starszych niż 30 dni
        if age_days < 30:
            print(f"⏭️  {persona} - {dec['ticker']}: za młoda ({age_days} dni)")
            skipped_count += 1
            continue
        
        print(f"\n🔎 Audytuję: {persona} → {dec['decision_type']} {dec['ticker']}")
        print(f"   Data decyzji: {dec['date']}")
        print(f"   Cena przy decyzji: {dec['current_price']:.2f}")
        print(f"   Uzasadnienie: {dec['reasoning'][:60]}...")
        
        # Pobierz aktualną cenę
        current_price = get_current_price(dec['ticker'])
        
        if current_price is None:
            print(f"   ⚠️ Nie można pobrać ceny - pomijam")
            skipped_count += 1
            continue
        
        # Oblicz zmianę
        change_pct = ((current_price - dec['current_price']) / dec['current_price']) * 100
        
        # Określ outcome
        if abs(change_pct) < 2:
            outcome = "Stabilizacja"
        elif change_pct > 10:
            outcome = "Silny wzrost"
        elif change_pct > 0:
            outcome = "Wzrost"
        elif change_pct < -10:
            outcome = "Silny spadek"
        else:
            outcome = "Spadek"
        
        # Szacuj wpływ finansowy (przykładowe - dostosuj do rzeczywistych kwot)
        # Zakładamy że średnia pozycja to 500 PLN
        impact_pln = 500 * (change_pct / 100)
        
        # Wykonaj audit
        result = pmm.audit_decision(
            decision_id=dec['id'],
            current_price=current_price,
            actual_outcome=outcome,
            impact_pln=impact_pln
        )
        
        if result:
            correct_emoji = "✓" if result['was_correct'] else "✗"
            print(f"   {correct_emoji} Wynik: {current_price:.2f} ({change_pct:+.1f}%)")
            print(f"   {correct_emoji} {'POPRAWNA' if result['was_correct'] else 'BŁĘDNA'} prognoza")
            audited_count += 1
        else:
            print(f"   ⚠️ Błąd auditu")
            skipped_count += 1
    
    print("\n" + "="*60)
    print(f"✓ Audit zakończony:")
    print(f"  • Ocenione: {audited_count}")
    print(f"  • Pominięte: {skipped_count}")
    print(f"  • Pozostałe: {len(pending) - audited_count - skipped_count}")
    
    # Pokaż nowy leaderboard
    print("\n🏆 RANKING WIARYGODNOŚCI PO AUDICIE:")
    print("="*60)
    leaderboard = pmm.get_leaderboard()
    for i, entry in enumerate(leaderboard, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        print(f"{emoji} {entry['persona']}: {entry['credibility']*100:.0f}% ({entry['correct']}/{entry['total']})")

def evolve_personalities_based_on_results():
    """
    Automatycznie zmień cechy charakteru person bazując na wynikach
    """
    print("\n🧬 Ewolucja person bazując na wynikach...")
    print("="*60)
    
    memory = pmm.load_memory()
    
    for persona_name, data in memory.items():
        if persona_name == "meta":
            continue
        
        stats = data.get("stats", {})
        total = stats.get("successful_calls", 0) + stats.get("failed_calls", 0)
        
        if total == 0:
            continue
        
        credibility = stats.get("credibility_score", 0)
        
        print(f"\n{persona_name}:")
        print(f"  Wiarygodność: {credibility*100:.0f}% ({stats.get('successful_calls', 0)}/{total})")
        
        # Ewolucja bazując na wynikach
        if credibility > 0.7:
            # Wysoka wiarygodność → zwiększ pewność siebie
            delta = 0.05
            trait = "optimism_bias" if "optimism_bias" in data.get("personality_traits", {}) else None
            if trait:
                result = pmm.evolve_trait(persona_name, trait, delta)
                if result:
                    print(f"  ✓ {trait}: {result[0]:.2f} → {result[1]:.2f} (sukces!)")
        
        elif credibility < 0.4:
            # Niska wiarygodność → zwiększ ostrożność
            delta = -0.05
            trait = "risk_tolerance" if "risk_tolerance" in data.get("personality_traits", {}) else None
            if trait:
                result = pmm.evolve_trait(persona_name, trait, delta)
                if result:
                    print(f"  ✓ {trait}: {result[0]:.2f} → {result[1]:.2f} (więcej ostrożności)")
            
            # Dodaj lekcję
            pmm.add_lesson(
                persona_name,
                f"Seria błędnych prognoz - muszę być bardziej ostrożny w swoich rekomendacjach (credibility: {credibility*100:.0f}%)"
            )
            print(f"  📚 Dodano lekcję o ostrożności")

if __name__ == "__main__":
    print("🤖 MIESIĘCZNY AUDIT DECYZJI AI PARTNERÓW")
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print()
    
    # 1. Oceń wszystkie nierozliczone decyzje
    auto_audit_all_pending()
    
    # 2. Ewoluuj persony bazując na wynikach
    evolve_personalities_based_on_results()
    
    print("\n" + "="*60)
    print("✓ Miesięczny audit zakończony!")
    print("="*60)
