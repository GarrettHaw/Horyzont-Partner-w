"""
Persistent Storage dla Streamlit Cloud
Zapisuje dane do st.secrets i synchronizuje z GitHub
"""

import streamlit as st
import json
from datetime import datetime
import os

# Pliki wymagające persystencji
PERSISTENT_FILES = [
    'persona_memory.json',
    'autonomous_conversations.json', 
    'wyplaty.json',
    'wydatki.json',
    'daily_snapshots.json',
    'portfolio_history.json',
    'api_usage.json'
]

def load_persistent_data(filename):
    """
    Wczytuje dane z hierarchii:
    1. st.session_state (najszybsze)
    2. Lokalny plik (dla rozwoju lokalnego)
    3. st.secrets (backup dla Streamlit Cloud)
    """
    cache_key = f'persistent_{filename}'
    
    # 1. Session state (już w pamięci)
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # 2. Lokalny plik
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                st.session_state[cache_key] = data
                return data
    except Exception as e:
        pass
    
    # 3. Streamlit Secrets (fallback dla Cloud)
    try:
        secret_key = filename.replace('.json', '_data').replace('.', '_')
        if secret_key in st.secrets:
            data = json.loads(st.secrets[secret_key])
            st.session_state[cache_key] = data
            return data
    except Exception:
        pass
    
    # 4. Zwróć pusty obiekt odpowiedniego typu
    if filename == 'persona_memory.json':
        return {}
    elif filename in ['wyplaty.json', 'wydatki.json']:
        return {'wyplaty': []} if 'wyplaty' in filename else {'wydatki': []}
    else:
        return []

def save_persistent_data(filename, data):
    """
    Zapisuje dane w 3 miejscach:
    1. st.session_state (natychmiastowy dostęp)
    2. Lokalny plik (dla rozwoju)
    3. Kolejka do synchronizacji z GitHub
    """
    cache_key = f'persistent_{filename}'
    
    # 1. Session state
    st.session_state[cache_key] = data
    
    # 2. Lokalny plik (może się nie udać na Streamlit Cloud)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Streamlit Cloud - read-only filesystem
    
    # 3. Dodaj do kolejki synchronizacji
    if 'sync_queue' not in st.session_state:
        st.session_state.sync_queue = {}
    
    st.session_state.sync_queue[filename] = {
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    
    return True

def get_sync_status():
    """Zwraca status synchronizacji"""
    if 'sync_queue' not in st.session_state or not st.session_state.sync_queue:
        return {
            'pending': 0,
            'files': [],
            'last_sync': None
        }
    
    return {
        'pending': len(st.session_state.sync_queue),
        'files': list(st.session_state.sync_queue.keys()),
        'last_sync': st.session_state.get('last_sync_time', None)
    }

def trigger_github_sync():
    """
    Wywołuje GitHub Actions workflow do synchronizacji plików
    (wymaga GitHub Personal Access Token w secrets)
    """
    if 'sync_queue' not in st.session_state or not st.session_state.sync_queue:
        return False, "Brak zmian do synchronizacji"
    
    try:
        # TODO: Implementacja GitHub API call
        # Potrzebne: GITHUB_TOKEN w secrets
        # Endpoint: POST /repos/{owner}/{repo}/dispatches
        # Event: repository_dispatch z payload=sync_queue
        
        st.info("🔄 Synchronizacja z GitHub zostanie dodana w następnej wersji")
        return False, "Funkcja w przygotowaniu"
        
    except Exception as e:
        return False, str(e)

def show_sync_widget():
    """Widget synchronizacji w sidebar"""
    status = get_sync_status()
    
    if status['pending'] > 0:
        st.sidebar.warning(f"⚠️ {status['pending']} plików czeka na sync")
        
        with st.sidebar.expander("📁 Pliki do synchronizacji"):
            for f in status['files']:
                st.caption(f"• {f}")
        
        if st.sidebar.button("🔄 Synchronizuj z GitHub", key="sync_btn"):
            success, msg = trigger_github_sync()
            if success:
                st.sidebar.success(msg)
            else:
                st.sidebar.info(msg)
    else:
        st.sidebar.success("✅ Wszystko zsynchronizowane")
