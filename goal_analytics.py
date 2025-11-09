"""
System Analizy Celów - Horyzont Partnerów
========================================
Inteligentna analiza i predykcja celów finansowych:
- Śledzenie historii modyfikacji celów
- Predykcja osiągnięcia na bazie trendów
- Rekomendacje oszczędzania
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np
from scipy import stats as scipy_stats

# ============================================================
# KONFIGURACJA
# ============================================================

GOALS_FILE = "cele.json"
GOALS_HISTORY_FILE = "cele_history.json"

# ============================================================
# FUNKCJE POMOCNICZE
# ============================================================

def load_json_file(filename: str, default: any = None) -> any:
    """Wczytuje plik JSON"""
    if not os.path.exists(filename):
        return default if default is not None else {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Błąd wczytywania {filename}: {e}")
        return default if default is not None else {}

def save_json_file(filename: str, data: any) -> bool:
    """Zapisuje dane do pliku JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Błąd zapisywania {filename}: {e}")
        return False

# ============================================================
# HISTORIA MODYFIKACJI CELÓW
# ============================================================

def log_goal_change(goal_id: str, action: str, user: str, old_value: any, new_value: any, reason: str = "") -> bool:
    """
    Loguje zmianę w celu do pliku historii
    
    Args:
        goal_id: ID celu
        action: 'created', 'modified', 'deleted', 'progress_update'
        user: Kto dokonał zmiany (Adam/Michał/System)
        old_value: Poprzednia wartość
        new_value: Nowa wartość
        reason: Powód zmiany
    """
    try:
        history = load_json_file(GOALS_HISTORY_FILE, {"changes": []})
        
        change_entry = {
            "id": len(history.get("changes", [])) + 1,
            "timestamp": datetime.now().isoformat(),
            "goal_id": goal_id,
            "action": action,
            "user": user,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason
        }
        
        if "changes" not in history:
            history["changes"] = []
        
        history["changes"].insert(0, change_entry)  # Najnowsze na początku
        
        # Ogranicz historię do 1000 wpisów
        history["changes"] = history["changes"][:1000]
        
        return save_json_file(GOALS_HISTORY_FILE, history)
        
    except Exception as e:
        print(f"⚠️ Błąd logowania zmiany: {e}")
        return False

def get_goal_history(goal_id: Optional[str] = None) -> List[Dict]:
    """
    Pobiera historię zmian dla konkretnego celu lub wszystkich
    """
    history = load_json_file(GOALS_HISTORY_FILE, {"changes": []})
    changes = history.get("changes", [])
    
    if goal_id:
        changes = [c for c in changes if c.get("goal_id") == goal_id]
    
    return changes

# ============================================================
# PREDYKCJA OSIĄGNIĘCIA CELÓW
# ============================================================

def predict_goal_achievement(goal_id: str, snapshots: List[Dict]) -> Optional[Dict]:
    """
    Przewiduje kiedy cel zostanie osiągnięty na bazie historycznych snapshots
    Używa linear regression
    
    Returns:
        {
            "goal_id": str,
            "goal_name": str,
            "current_value": float,
            "target_value": float,
            "progress_pct": float,
            "predicted_days": int,  # dni do osiągnięcia
            "predicted_date": str,   # przewidywana data
            "daily_rate": float,     # średni dzienny przyrost
            "confidence": str        # low/medium/high
        }
    """
    try:
        # Wczytaj cele
        goals = load_json_file(GOALS_FILE)
        
        if goal_id not in goals:
            return None
        
        goal = goals[goal_id]
        target = goal.get('cel', 0)
        current = goal.get('aktualnie', 0)
        
        if target <= 0:
            return None
        
        # Jeśli już osiągnięty
        if current >= target:
            return {
                "goal_id": goal_id,
                "goal_name": goal.get('nazwa', goal_id),
                "current_value": current,
                "target_value": target,
                "progress_pct": (current / target) * 100,
                "status": "achieved",
                "message": "Cel już osiągnięty! 🎉"
            }
        
        # Potrzebujemy co najmniej 3 snapshoty
        if len(snapshots) < 3:
            return {
                "goal_id": goal_id,
                "goal_name": goal.get('nazwa', goal_id),
                "current_value": current,
                "target_value": target,
                "progress_pct": (current / target) * 100,
                "status": "insufficient_data",
                "message": "Za mało danych do predykcji (minimum 3 snapshoty)"
            }
        
        # Przygotuj dane do regresji
        dates = []
        values = []
        
        for snapshot in snapshots:
            date = datetime.fromisoformat(snapshot['date'])
            dates.append(date)
            
            # Wartość netto jako proxy dla postępu celów
            values.append(snapshot['totals']['net_worth_pln'])
        
        # Konwertuj daty na dni od początku
        start_date = dates[0]
        x = np.array([(d - start_date).days for d in dates])
        y = np.array(values)
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x, y)
        
        # Oblicz ile dni do osiągnięcia celu
        # Zakładamy że cel rośnie proporcjonalnie do net worth
        current_net_worth = y[-1]
        if slope <= 0:
            return {
                "goal_id": goal_id,
                "goal_name": goal.get('nazwa', goal_id),
                "current_value": current,
                "target_value": target,
                "progress_pct": (current / target) * 100,
                "status": "negative_trend",
                "message": "Trend spadkowy - osiągnięcie celu nieprzewidywalne",
                "daily_rate": slope
            }
        
        # Proporcja: ile % celu mamy teraz
        current_progress = current / target
        
        # Ile jeszcze potrzeba
        remaining_value = target - current
        
        # Tempo wzrostu w PLN/dzień
        daily_rate_pln = slope
        
        # Zakładamy że cel rośnie w tym samym tempie co net worth
        # remaining_value / (daily_rate_pln * current_progress)
        # Uproszczenie: dni = remaining / (daily_rate * current/current_net_worth)
        
        # Bardziej realistycznie: linear extrapolation
        days_so_far = x[-1]
        rate_of_progress = (current - 0) / days_so_far if days_so_far > 0 else 0
        
        if rate_of_progress <= 0:
            days_to_goal = 999999
        else:
            days_to_goal = int(remaining_value / rate_of_progress)
        
        predicted_date = datetime.now() + timedelta(days=days_to_goal)
        
        # Confidence based on R-squared
        r_squared = r_value ** 2
        if r_squared > 0.8:
            confidence = "high"
        elif r_squared > 0.5:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "goal_id": goal_id,
            "goal_name": goal.get('nazwa', goal_id),
            "current_value": current,
            "target_value": target,
            "progress_pct": (current / target) * 100,
            "predicted_days": days_to_goal,
            "predicted_date": predicted_date.strftime("%Y-%m-%d"),
            "daily_rate": rate_of_progress,
            "confidence": confidence,
            "r_squared": r_squared,
            "status": "predicted"
        }
        
    except Exception as e:
        print(f"⚠️ Błąd predykcji dla {goal_id}: {e}")
        return None

def predict_all_goals(snapshots: List[Dict]) -> Dict[str, Dict]:
    """
    Przewiduje osiągnięcie wszystkich celów
    """
    goals = load_json_file(GOALS_FILE)
    predictions = {}
    
    for goal_id in goals.keys():
        if isinstance(goals[goal_id], dict):
            prediction = predict_goal_achievement(goal_id, snapshots)
            if prediction:
                predictions[goal_id] = prediction
    
    return predictions

# ============================================================
# REKOMENDACJE OSZCZĘDZANIA
# ============================================================

def calculate_savings_recommendation(goal_id: str, deadline_months: int = 12) -> Optional[Dict]:
    """
    Oblicza ile trzeba odkładać miesięcznie aby osiągnąć cel w zadanym terminie
    
    Args:
        goal_id: ID celu
        deadline_months: W ciągu ilu miesięcy chcemy osiągnąć cel
    
    Returns:
        {
            "goal_id": str,
            "goal_name": str,
            "current_value": float,
            "target_value": float,
            "gap": float,
            "deadline_months": int,
            "required_monthly": float,
            "required_daily": float,
            "recommendation": str
        }
    """
    try:
        goals = load_json_file(GOALS_FILE)
        
        if goal_id not in goals:
            return None
        
        goal = goals[goal_id]
        target = goal.get('cel', 0)
        current = goal.get('aktualnie', 0)
        goal_name = goal.get('nazwa', goal_id)
        
        if target <= 0:
            return None
        
        # Jeśli już osiągnięty
        if current >= target:
            return {
                "goal_id": goal_id,
                "goal_name": goal_name,
                "current_value": current,
                "target_value": target,
                "status": "achieved",
                "message": f"Cel '{goal_name}' już osiągnięty! 🎉"
            }
        
        gap = target - current
        
        required_monthly = gap / deadline_months
        required_daily = required_monthly / 30
        
        # Deadline date
        deadline_date = datetime.now() + timedelta(days=deadline_months * 30)
        
        return {
            "goal_id": goal_id,
            "goal_name": goal_name,
            "current_value": current,
            "target_value": target,
            "gap": gap,
            "progress_pct": (current / target) * 100,
            "deadline_months": deadline_months,
            "deadline_date": deadline_date.strftime("%Y-%m-%d"),
            "required_monthly": required_monthly,
            "required_daily": required_daily,
            "recommendation": f"Musisz odkładać {required_monthly:.2f} PLN/miesiąc aby osiągnąć cel '{goal_name}' do {deadline_date.strftime('%Y-%m-%d')}",
            "status": "needs_savings"
        }
        
    except Exception as e:
        print(f"⚠️ Błąd obliczania rekomendacji dla {goal_id}: {e}")
        return None

def get_all_savings_recommendations(deadline_months: int = 12) -> Dict[str, Dict]:
    """
    Oblicza rekomendacje dla wszystkich celów
    """
    goals = load_json_file(GOALS_FILE)
    recommendations = {}
    
    for goal_id in goals.keys():
        if isinstance(goals[goal_id], dict):
            rec = calculate_savings_recommendation(goal_id, deadline_months)
            if rec:
                recommendations[goal_id] = rec
    
    return recommendations

# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "predict":
            # Predykcja celów
            import daily_snapshot as ds
            snapshots = ds.load_snapshot_history()
            
            predictions = predict_all_goals(snapshots)
            
            print("\n🔮 PREDYKCJE OSIĄGNIĘCIA CELÓW")
            print("=" * 60)
            
            for goal_id, pred in predictions.items():
                print(f"\n📌 {pred['goal_name']}")
                print(f"   Status: {pred['status']}")
                print(f"   Postęp: {pred['current_value']:.2f} / {pred['target_value']:.2f} ({pred['progress_pct']:.1f}%)")
                
                if pred['status'] == 'predicted':
                    print(f"   ⏱️  Przewidywane osiągnięcie: za {pred['predicted_days']} dni ({pred['predicted_date']})")
                    print(f"   📈 Tempo: {pred['daily_rate']:.2f} PLN/dzień")
                    print(f"   🎯 Pewność: {pred['confidence']}")
                elif pred['status'] == 'achieved':
                    print(f"   ✅ {pred['message']}")
                else:
                    print(f"   ℹ️  {pred.get('message', 'Brak danych')}")
        
        elif command == "recommend":
            # Rekomendacje oszczędzania
            months = int(sys.argv[2]) if len(sys.argv) > 2 else 12
            
            recommendations = get_all_savings_recommendations(months)
            
            print(f"\n💰 REKOMENDACJE OSZCZĘDZANIA ({months} miesięcy)")
            print("=" * 60)
            
            for goal_id, rec in recommendations.items():
                print(f"\n📌 {rec['goal_name']}")
                
                if rec['status'] == 'achieved':
                    print(f"   ✅ {rec['message']}")
                else:
                    print(f"   Brakuje: {rec['gap']:.2f} PLN")
                    print(f"   💵 Miesięcznie: {rec['required_monthly']:.2f} PLN")
                    print(f"   📅 Dziennie: {rec['required_daily']:.2f} PLN")
                    print(f"   🎯 Termin: {rec['deadline_date']}")
        
        elif command == "history":
            # Historia zmian celów
            goal_id = sys.argv[2] if len(sys.argv) > 2 else None
            
            changes = get_goal_history(goal_id)
            
            print(f"\n📜 HISTORIA ZMIAN CELÓW")
            if goal_id:
                print(f"Cel: {goal_id}")
            print("=" * 60)
            
            for change in changes[:20]:  # Ostatnie 20
                timestamp = datetime.fromisoformat(change['timestamp']).strftime("%Y-%m-%d %H:%M")
                print(f"\n{timestamp} | {change['user']} | {change['action']}")
                print(f"   Cel: {change['goal_id']}")
                if change.get('reason'):
                    print(f"   Powód: {change['reason']}")
                print(f"   {change.get('old_value')} → {change.get('new_value')}")
        
        else:
            print(f"⚠️ Nieznana komenda: {command}")
            print("\nDostępne komendy:")
            print("  python goal_analytics.py predict              - Predykcja osiągnięcia celów")
            print("  python goal_analytics.py recommend [months]   - Rekomendacje oszczędzania")
            print("  python goal_analytics.py history [goal_id]    - Historia zmian celów")
    
    else:
        # Domyślnie pokaż predykcje
        import daily_snapshot as ds
        snapshots = ds.load_snapshot_history()
        predictions = predict_all_goals(snapshots)
        
        print("\n🎯 SZYBKIE PREDYKCJE:")
        for goal_id, pred in predictions.items():
            if pred['status'] == 'predicted':
                print(f"{pred['goal_name']}: za {pred['predicted_days']} dni ({pred['progress_pct']:.0f}%)")
            elif pred['status'] == 'achieved':
                print(f"{pred['goal_name']}: ✅ Osiągnięty")
