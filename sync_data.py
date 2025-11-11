"""
🔄 Data Synchronization Script
Sprawdza obecność kluczowych plików danych przed commitowaniem

Uruchamiany automatycznie co godzinę przez GitHub Actions workflow
Cel: Walidacja integralności danych przed sync do repo
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any

# Kluczowe pliki danych do monitorowania
DATA_FILES = [
    'persona_memory.json',
    'autonomous_conversations.json',
    'partner_conversations.json',
    'user_preferences.json',
    'wyplaty.json',
    'wydatki.json',
    'kredyty.json',
    'cele.json',
    'krypto.json',
    'notification_config.json',
    'daily_snapshots.json',
    'portfolio_history.json',
    'api_usage.json',
    'trading212_cache.json',
    'advisor_scoring.json'
]

def validate_json_file(filepath: str) -> Dict[str, Any]:
    """
    Waliduj plik JSON
    
    Returns:
        dict: {'valid': bool, 'size': int, 'error': str}
    """
    result = {
        'file': filepath,
        'exists': False,
        'valid': False,
        'size': 0,
        'error': None
    }
    
    if not os.path.exists(filepath):
        result['error'] = 'File not found'
        return result
    
    result['exists'] = True
    result['size'] = os.path.getsize(filepath)
    
    # Sprawdź czy to poprawny JSON
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        result['valid'] = True
    except json.JSONDecodeError as e:
        result['error'] = f'Invalid JSON: {str(e)}'
    except Exception as e:
        result['error'] = f'Read error: {str(e)}'
    
    return result

def sync_data():
    """Główna funkcja synchronizacji"""
    print("🔄 Data Synchronization - START")
    print(f"📅 {datetime.now().isoformat()}")
    print("-" * 60)
    
    total_files = len(DATA_FILES)
    valid_files = 0
    missing_files = 0
    invalid_files = 0
    
    results = []
    
    for filepath in DATA_FILES:
        result = validate_json_file(filepath)
        results.append(result)
        
        # Status
        if not result['exists']:
            status = "❌ MISSING"
            missing_files += 1
        elif not result['valid']:
            status = f"⚠️ INVALID: {result['error']}"
            invalid_files += 1
        else:
            status = f"✅ OK ({result['size']:,} bytes)"
            valid_files += 1
        
        print(f"{status:40s} {filepath}")
    
    print("-" * 60)
    print(f"📊 Summary:")
    print(f"   Total files: {total_files}")
    print(f"   ✅ Valid: {valid_files}")
    print(f"   ❌ Missing: {missing_files}")
    print(f"   ⚠️ Invalid: {invalid_files}")
    print("-" * 60)
    
    # Ostrzeżenia dla krytycznych plików
    critical_files = ['trading212_cache.json', 'krypto.json', 'cele.json']
    for filepath in critical_files:
        result = next((r for r in results if r['file'] == filepath), None)
        if result and not result['valid']:
            print(f"⚠️ WARNING: Critical file {filepath} has issues!")
    
    print("🔄 Data Synchronization - COMPLETE ✅")
    
    # Return exit code 0 (success) nawet jeśli niektóre pliki missing
    # Workflow może commitować co jest dostępne
    return 0

if __name__ == "__main__":
    exit(sync_data())
