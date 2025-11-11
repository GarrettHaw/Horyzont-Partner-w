"""
goal_analytics.py

Moduł do analizy i predykcji osiągnięcia celów finansowych.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from sklearn.linear_model import LinearRegression


class GoalAnalytics:
    """Analiza i predykcja celów finansowych"""
    
    def __init__(self, goals_file: str = 'cele.json'):
        self.goals_file = goals_file
        self.goals = self._load_goals()
    
    def _load_goals(self) -> Dict:
        """Ładuje cele z pliku JSON"""
        try:
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def get_goal_progress(self, goal_key: str, current_value: float) -> Dict:
        """
        Oblicza postęp dla danego celu
        
        Args:
            goal_key: Klucz celu w cele.json
            current_value: Obecna wartość
            
        Returns:
            Dict z informacją o postępie
        """
        target_value = self.goals.get(goal_key)
        
        if target_value is None:
            return {
                'status': 'not_found',
                'message': f'Cel {goal_key} nie istnieje'
            }
        
        progress_pct = (current_value / target_value) * 100
        remaining = target_value - current_value
        
        return {
            'status': 'active',
            'goal_key': goal_key,
            'target_value': target_value,
            'current_value': current_value,
            'progress_pct': min(progress_pct, 100),
            'remaining': max(remaining, 0),
            'achieved': current_value >= target_value
        }
    
    def predict_goal_achievement(
        self, 
        goal_key: str, 
        snapshots: List[Dict]
    ) -> Dict:
        """
        Przewiduje kiedy cel zostanie osiągnięty na podstawie historycznych danych
        
        Args:
            goal_key: Klucz celu
            snapshots: Lista snapshots z daily_snapshot
            
        Returns:
            Dict z predykcją
        """
        target_value = self.goals.get(goal_key)
        
        if not target_value or not snapshots or len(snapshots) < 3:
            return {
                'status': 'insufficient_data',
                'message': 'Za mało danych do predykcji',
                'goal_name': goal_key
            }
        
        # Sortuj snapshots po dacie
        sorted_snapshots = sorted(snapshots, key=lambda x: x.get('timestamp', ''))
        
        # Wybierz odpowiednią metrykę z snapshots
        metric_map = {
            'Rezerwa_gotowkowa_PLN': 'total_assets',
            'Rezerwa_gotowkowa_obecna_PLN': 'total_assets',
            'ADD_wartosc_docelowa_PLN': 'total_assets',
        }
        
        metric_key = metric_map.get(goal_key, 'total_assets')
        
        # Zbierz dane do regresji
        dates = []
        values = []
        
        base_date = datetime.fromisoformat(sorted_snapshots[0]['timestamp'][:10])
        
        for snap in sorted_snapshots[-30:]:  # Ostatnie 30 snapshots
            try:
                date_obj = datetime.fromisoformat(snap['timestamp'][:10])
                value = snap.get(metric_key, 0)
                
                days_diff = (date_obj - base_date).days
                dates.append(days_diff)
                values.append(value)
            except:
                continue
        
        if len(dates) < 3:
            return {
                'status': 'insufficient_data',
                'message': 'Za mało punktów danych',
                'goal_name': goal_key
            }
        
        # Regresja liniowa
        X = np.array(dates).reshape(-1, 1)
        y = np.array(values)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # R² score
        r_squared = model.score(X, y)
        
        # Aktualna wartość
        current_value = values[-1]
        
        # Jeśli cel osiągnięty
        if current_value >= target_value:
            return {
                'status': 'achieved',
                'goal_name': goal_key,
                'current_value': current_value,
                'target_value': target_value,
                'progress_pct': 100,
                'message': '🎉 Cel osiągnięty!'
            }
        
        # Tempo wzrostu (slope)
        daily_rate = model.coef_[0]
        
        if daily_rate <= 0:
            return {
                'status': 'negative_trend',
                'goal_name': goal_key,
                'current_value': current_value,
                'target_value': target_value,
                'progress_pct': (current_value / target_value) * 100,
                'message': 'Wartość nie rośnie - cel może nie zostać osiągnięty',
                'daily_rate': daily_rate
            }
        
        # Dni do osiągnięcia celu
        remaining = target_value - current_value
        days_to_goal = int(remaining / daily_rate)
        
        predicted_date = datetime.now() + timedelta(days=days_to_goal)
        
        # Poziom pewności na podstawie R²
        if r_squared > 0.8:
            confidence = 'high'
        elif r_squared > 0.5:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return {
            'status': 'predicted',
            'goal_name': goal_key,
            'current_value': current_value,
            'target_value': target_value,
            'progress_pct': (current_value / target_value) * 100,
            'remaining': remaining,
            'daily_rate': daily_rate,
            'predicted_days': days_to_goal,
            'predicted_date': predicted_date.strftime('%Y-%m-%d'),
            'confidence': confidence,
            'r_squared': r_squared,
            'message': f'Cel przewidywany za {days_to_goal} dni ({predicted_date.strftime("%Y-%m-%d")})'
        }


def predict_all_goals(snapshots: List[Dict]) -> Dict[str, Dict]:
    """
    Przewiduje wszystkie cele z cele.json
    
    Args:
        snapshots: Lista snapshots z daily_snapshot
        
    Returns:
        Dict {goal_key: prediction_result}
    """
    ga = GoalAnalytics()
    results = {}
    
    # Lista celów do trackowania (wartości liczbowe)
    trackable_goals = [
        'Rezerwa_gotowkowa_PLN',
        'Rezerwa_gotowkowa_obecna_PLN',
        'ADD_wartosc_docelowa_PLN'
    ]
    
    for goal_key in trackable_goals:
        if goal_key in ga.goals:
            prediction = ga.predict_goal_achievement(goal_key, snapshots)
            results[goal_key] = prediction
    
    return results


def check_goal_alerts(snapshots: List[Dict]) -> List[Dict]:
    """
    Sprawdza czy jakieś cele zostały osiągnięte
    
    Args:
        snapshots: Lista snapshots
        
    Returns:
        Lista alertów o osiągniętych celach
    """
    predictions = predict_all_goals(snapshots)
    alerts = []
    
    for goal_key, pred in predictions.items():
        if pred.get('status') == 'achieved':
            alerts.append({
                'type': 'goal_achieved',
                'severity': 'success',
                'title': f'🎉 Cel osiągnięty: {goal_key}',
                'message': pred.get('message', 'Gratulacje!'),
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'goal_name': goal_key,
                    'target_value': pred.get('target_value'),
                    'current_value': pred.get('current_value'),
                    'progress_pct': 100
                }
            })
    
    return alerts


if __name__ == "__main__":
    # Test
    ga = GoalAnalytics()
    print("Loaded goals:", list(ga.goals.keys())[:5])
    
    # Test progress
    progress = ga.get_goal_progress('Rezerwa_gotowkowa_PLN', 5000)
    print(f"\nProgress: {progress['progress_pct']:.1f}%")
