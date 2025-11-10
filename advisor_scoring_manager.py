#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advisor Scoring System - Win/Loss tracking and voting weight management
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os

SCORING_FILE = 'advisor_scoring.json'

def load_scoring_data() -> Dict:
    """Load scoring data from JSON file"""
    if not os.path.exists(SCORING_FILE):
        raise FileNotFoundError(f"{SCORING_FILE} not found. Run initialize first.")
    
    with open(SCORING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_scoring_data(data: Dict) -> None:
    """Save scoring data to JSON file"""
    data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    with open(SCORING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_prediction(
    advisor: str,
    prediction_text: str,
    prediction_type: str,
    asset: str,
    direction: str,
    confidence: float,
    metadata: Dict = None
) -> str:
    """
    Add a new prediction to track
    
    Args:
        advisor: Name of advisor making prediction
        prediction_type: 'price_movement', 'portfolio_action', 'market_timing', 'risk_warning'
        asset: Asset symbol (e.g., 'BTC', 'KGHM', 'S&P500')
        direction: 'up', 'down', 'buy', 'sell', 'hold', 'reduce_exposure'
        confidence: 0.0-1.0 confidence level
        metadata: Additional context
    
    Returns:
        prediction_id
    """
    data = load_scoring_data()
    
    if advisor not in data['advisors']:
        raise ValueError(f"Advisor '{advisor}' not found in scoring system")
    
    # Generate prediction ID
    prediction_id = f"pred_{advisor.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create prediction object
    prediction = {
        "prediction_id": prediction_id,
        "advisor": advisor,
        "date_created": datetime.now().strftime("%Y-%m-%d"),
        "date_evaluate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "prediction_type": prediction_type,
        "asset": asset,
        "prediction_text": prediction_text,
        "prediction_direction": direction,
        "confidence": confidence,
        "status": "pending",
        "outcome": None,
        "was_correct": None,
        "metadata": metadata or {}
    }
    
    # Add current price if available (for price_movement types)
    if prediction_type == "price_movement":
        prediction["current_price_at_prediction"] = None  # To be filled by caller
        prediction["actual_price_at_evaluation"] = None
    
    # Add to advisor's predictions list
    data['advisors'][advisor]['predictions'].append(prediction)
    data['advisors'][advisor]['pending_predictions'] += 1
    
    save_scoring_data(data)
    
    print(f"✅ Prediction added: {prediction_id}")
    print(f"   Advisor: {advisor}")
    print(f"   Type: {prediction_type}")
    print(f"   Asset: {asset}")
    print(f"   Direction: {direction}")
    print(f"   Confidence: {confidence:.0%}")
    print(f"   Evaluate on: {prediction['date_evaluate']}")
    
    return prediction_id

def evaluate_prediction(prediction_id: str, was_correct: bool, outcome_notes: str = "") -> None:
    """
    Evaluate a prediction and update advisor stats
    
    Args:
        prediction_id: ID of prediction to evaluate
        was_correct: True if prediction was correct
        outcome_notes: Additional notes about outcome
    """
    data = load_scoring_data()
    
    # Find prediction
    found = False
    for advisor_name, advisor_data in data['advisors'].items():
        if advisor_data['type'] == 'human':
            continue
            
        for pred in advisor_data['predictions']:
            if pred['prediction_id'] == prediction_id:
                if pred['status'] != 'pending':
                    print(f"⚠️ Prediction {prediction_id} already evaluated: {pred['status']}")
                    return
                
                # Update prediction
                pred['status'] = 'evaluated'
                pred['was_correct'] = was_correct
                pred['outcome'] = outcome_notes
                pred['evaluation_date'] = datetime.now().strftime("%Y-%m-%d")
                
                # Update advisor stats
                advisor_data['pending_predictions'] -= 1
                advisor_data['total_predictions'] += 1
                
                if was_correct:
                    advisor_data['correct_predictions'] += 1
                else:
                    advisor_data['incorrect_predictions'] += 1
                
                # Recalculate accuracy
                if advisor_data['total_predictions'] > 0:
                    advisor_data['accuracy_rate'] = (
                        advisor_data['correct_predictions'] / advisor_data['total_predictions']
                    )
                
                # Update confidence average
                confidences = [p['confidence'] for p in advisor_data['predictions'] if p['status'] == 'evaluated']
                if confidences:
                    advisor_data['confidence_avg'] = sum(confidences) / len(confidences)
                
                found = True
                
                print(f"{'✅' if was_correct else '❌'} Prediction evaluated: {prediction_id}")
                print(f"   Advisor: {advisor_name}")
                print(f"   Result: {'CORRECT' if was_correct else 'INCORRECT'}")
                print(f"   New accuracy: {advisor_data['accuracy_rate']:.1%}")
                print(f"   Total predictions: {advisor_data['total_predictions']}")
                
                break
        
        if found:
            break
    
    if not found:
        print(f"❌ Prediction {prediction_id} not found")
        return
    
    save_scoring_data(data)

def calculate_new_weights() -> Dict[str, float]:
    """
    Calculate new voting weights based on performance
    
    Returns:
        Dict mapping advisor names to new weights
    """
    data = load_scoring_data()
    base_weight = data['metadata']['base_weight_per_advisor']
    dynamic_pool = data['metadata']['dynamic_pool']
    min_weight = data['metadata']['weight_limits']['min']
    max_weight = data['metadata']['weight_limits']['max']
    
    # Calculate performance scores
    advisor_scores = {}
    for advisor_name, advisor_data in data['advisors'].items():
        if advisor_data['type'] == 'human':
            continue  # Skip human advisors
        
        accuracy = advisor_data['accuracy_rate']
        total_preds = advisor_data['total_predictions']
        
        # Performance relative to baseline (50%)
        # Only consider if advisor has made at least 3 predictions
        if total_preds >= 3:
            performance_delta = accuracy - 0.5  # -0.5 to +0.5
        else:
            performance_delta = 0  # Neutral if too few predictions
        
        advisor_scores[advisor_name] = performance_delta
    
    # Calculate weight adjustments
    new_weights = {}
    
    # Total performance delta (sum of all advisor deltas)
    total_delta = sum(advisor_scores.values())
    
    for advisor_name, advisor_data in data['advisors'].items():
        if advisor_data['type'] == 'human':
            # Human keeps fixed weight
            new_weights[advisor_name] = advisor_data['fixed_weight']
        else:
            perf_delta = advisor_scores[advisor_name]
            
            # Weight change based on relative performance
            # Scale by dynamic pool size and number of advisors
            if total_delta != 0:
                # Proportional share of dynamic pool based on performance
                pool_share = (perf_delta / abs(total_delta)) * dynamic_pool * 0.5
            else:
                pool_share = 0
            
            new_weight = base_weight + pool_share
            
            # Apply limits
            new_weight = max(min_weight, min(max_weight, new_weight))
            
            new_weights[advisor_name] = round(new_weight, 2)
    
    return new_weights

def rebalance_weights(reason: str = "Monthly rebalancing") -> None:
    """
    Perform monthly rebalancing - update all voting weights
    
    Args:
        reason: Reason for rebalancing (logged in history)
    """
    data = load_scoring_data()
    new_weights = calculate_new_weights()
    
    print("\n" + "=" * 60)
    print("📊 MONTHLY REBALANCING - Voting Weights Update")
    print("=" * 60)
    
    changes = []
    
    for advisor_name, new_weight in new_weights.items():
        advisor_data = data['advisors'][advisor_name]
        old_weight = advisor_data.get('current_weight', advisor_data.get('fixed_weight', 0))
        
        if advisor_data['type'] == 'human':
            print(f"\n👤 {advisor_name}: {old_weight:.2f}% (FIXED)")
            continue
        
        change = new_weight - old_weight
        
        # Update weight
        advisor_data['current_weight'] = new_weight
        
        # Add to history
        advisor_data['weight_history'].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weight": new_weight,
            "reason": reason,
            "accuracy": advisor_data['accuracy_rate'],
            "predictions_evaluated": advisor_data['total_predictions']
        })
        
        changes.append({
            "advisor": advisor_name,
            "old_weight": old_weight,
            "new_weight": new_weight,
            "change": change,
            "accuracy": advisor_data['accuracy_rate'],
            "total_predictions": advisor_data['total_predictions']
        })
        
        # Print update
        change_symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"\n{change_symbol} {advisor_name}:")
        print(f"   Old weight: {old_weight:.2f}%")
        print(f"   New weight: {new_weight:.2f}%")
        print(f"   Change: {change:+.2f}%")
        print(f"   Accuracy: {advisor_data['accuracy_rate']:.1%} ({advisor_data['total_predictions']} predictions)")
    
    # Create monthly report
    monthly_report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "reason": reason,
        "changes": changes,
        "total_predictions_evaluated": sum(
            data['advisors'][adv]['total_predictions'] 
            for adv in data['advisors'] 
            if data['advisors'][adv]['type'] == 'ai'
        )
    }
    
    data['monthly_reports'].append(monthly_report)
    
    # Update next rebalance date
    next_month = datetime.now().replace(day=1) + timedelta(days=32)
    data['metadata']['next_rebalance'] = next_month.replace(day=1).strftime("%Y-%m-%d")
    
    save_scoring_data(data)
    
    print("\n" + "=" * 60)
    print("✅ Rebalancing complete!")
    print(f"📅 Next rebalance: {data['metadata']['next_rebalance']}")
    print("=" * 60 + "\n")

def get_leaderboard() -> List[Tuple[str, float, float]]:
    """
    Get current leaderboard
    
    Returns:
        List of (advisor_name, current_weight, accuracy) sorted by weight
    """
    data = load_scoring_data()
    
    leaderboard = []
    for advisor_name, advisor_data in data['advisors'].items():
        weight = advisor_data.get('current_weight', advisor_data.get('fixed_weight', 0))
        accuracy = advisor_data.get('accuracy_rate', 0)
        total_preds = advisor_data.get('total_predictions', 0)
        
        leaderboard.append((advisor_name, weight, accuracy, total_preds))
    
    # Sort by weight (descending)
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    
    return leaderboard

def print_leaderboard() -> None:
    """Print current leaderboard"""
    leaderboard = get_leaderboard()
    
    print("\n" + "=" * 70)
    print("🏆 ADVISOR LEADERBOARD - Current Voting Weights")
    print("=" * 70)
    print(f"{'Rank':<6} {'Advisor':<30} {'Weight':<10} {'Accuracy':<12} {'Predictions'}")
    print("-" * 70)
    
    for i, (name, weight, accuracy, total_preds) in enumerate(leaderboard, 1):
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        acc_str = f"{accuracy:.1%}" if total_preds > 0 else "N/A"
        
        print(f"{rank_emoji:<6} {name:<30} {weight:>6.2f}% {acc_str:>10} {total_preds:>8}")
    
    print("=" * 70 + "\n")

def get_pending_evaluations() -> List[Dict]:
    """Get list of predictions ready for evaluation (30 days passed)"""
    data = load_scoring_data()
    today = datetime.now()
    
    pending = []
    
    for advisor_name, advisor_data in data['advisors'].items():
        if advisor_data['type'] == 'human':
            continue
        
        for pred in advisor_data['predictions']:
            if pred['status'] == 'pending':
                eval_date = datetime.strptime(pred['date_evaluate'], "%Y-%m-%d")
                
                if today >= eval_date:
                    pending.append({
                        'advisor': advisor_name,
                        'prediction_id': pred['prediction_id'],
                        'prediction_text': pred['prediction_text'],
                        'asset': pred['asset'],
                        'created': pred['date_created'],
                        'eval_date': pred['date_evaluate'],
                        'days_overdue': (today - eval_date).days
                    })
    
    return pending

# CLI Interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python advisor_scoring_manager.py leaderboard")
        print("  python advisor_scoring_manager.py pending")
        print("  python advisor_scoring_manager.py rebalance")
        print("  python advisor_scoring_manager.py add_prediction <advisor> <text> <type> <asset> <direction> <confidence>")
        print("  python advisor_scoring_manager.py evaluate <prediction_id> <correct/incorrect> [notes]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "leaderboard":
        print_leaderboard()
    
    elif command == "pending":
        pending = get_pending_evaluations()
        if not pending:
            print("✅ No predictions pending evaluation")
        else:
            print(f"\n⏰ {len(pending)} predictions ready for evaluation:\n")
            for p in pending:
                print(f"ID: {p['prediction_id']}")
                print(f"   Advisor: {p['advisor']}")
                print(f"   Prediction: {p['prediction_text']}")
                print(f"   Asset: {p['asset']}")
                print(f"   Created: {p['created']}")
                print(f"   Days overdue: {p['days_overdue']}")
                print()
    
    elif command == "rebalance":
        rebalance_weights()
        print_leaderboard()
    
    elif command == "add_prediction":
        if len(sys.argv) < 8:
            print("Error: add_prediction requires: advisor text type asset direction confidence")
            sys.exit(1)
        
        advisor = sys.argv[2]
        text = sys.argv[3]
        pred_type = sys.argv[4]
        asset = sys.argv[5]
        direction = sys.argv[6]
        confidence = float(sys.argv[7])
        
        add_prediction(advisor, text, pred_type, asset, direction, confidence)
    
    elif command == "evaluate":
        if len(sys.argv) < 4:
            print("Error: evaluate requires: prediction_id correct/incorrect [notes]")
            sys.exit(1)
        
        pred_id = sys.argv[2]
        was_correct = sys.argv[3].lower() in ['correct', 'true', 'yes', '1']
        notes = sys.argv[4] if len(sys.argv) > 4 else ""
        
        evaluate_prediction(pred_id, was_correct, notes)
        print_leaderboard()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
