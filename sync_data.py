#!/usr/bin/env python3
"""
Sync Data Files - GitHub Actions
Synchronizuje pliki danych między Streamlit Cloud a GitHub
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Pliki do synchronizacji
DATA_FILES = [
    'persona_memory.json',
    'autonomous_conversations.json',
    'wyplaty.json',
    'wydatki.json', 
    'daily_snapshots.json',
    'portfolio_history.json',
    'api_usage.json',
    'cele.json',
    'kredyty.json',
    'krypto.json'
]

def ensure_file_exists(filepath):
    """Upewnij się że plik istnieje, jeśli nie - utwórz pusty"""
    if not os.path.exists(filepath):
        print(f"Creating missing file: {filepath}")
        
        # Określ domyślną strukturę na podstawie nazwy
        if 'persona_memory' in filepath:
            default_data = {}
        elif filepath in ['wyplaty.json', 'wydatki.json']:
            key = 'wyplaty' if 'wyplaty' in filepath else 'wydatki'
            default_data = {key: []}
        elif filepath in ['cele.json', 'kredyty.json', 'krypto.json']:
            default_data = {}
        else:
            default_data = []
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        
        return True
    return False

def validate_json(filepath):
    """Sprawdź czy JSON jest poprawny"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return False

def sync_files():
    """Główna funkcja synchronizacji"""
    print("🔄 Starting data synchronization...")
    
    created_count = 0
    validated_count = 0
    error_count = 0
    
    for filepath in DATA_FILES:
        print(f"\n📄 Processing: {filepath}")
        
        # Utwórz plik jeśli nie istnieje
        if ensure_file_exists(filepath):
            created_count += 1
        
        # Walidacja JSON
        if validate_json(filepath):
            validated_count += 1
            print(f"✅ {filepath} - OK")
        else:
            error_count += 1
            print(f"❌ {filepath} - ERROR")
    
    print("\n" + "="*50)
    print("📊 Synchronization Summary:")
    print(f"  • Created: {created_count} files")
    print(f"  • Validated: {validated_count} files")
    print(f"  • Errors: {error_count} files")
    print(f"  • Total: {len(DATA_FILES)} files")
    print("="*50)
    
    if error_count > 0:
        print("\n⚠️ Some files had errors - check logs above")
        return False
    
    print("\n✅ All files synchronized successfully!")
    return True

if __name__ == '__main__':
    success = sync_files()
    exit(0 if success else 1)
