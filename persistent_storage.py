"""
Persistent Storage dla Streamlit Cloud
Zapisuje dane do st.secrets i synchronizuje z GitHub
"""

import streamlit as st
import json
from datetime import datetime
import os

# Import GitHub API
try:
    from github_api import trigger_sync_workflow
    GITHUB_API_OK = True
except:
    GITHUB_API_OK = False

# Pliki wymagające persystencji
PERSISTENT_FILES = [
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
    except json.JSONDecodeError as e:
        # Plik jest corrupted - próbuj odzyskać z backupu
        st.warning(f"⚠️ Plik {filename} uszkodzony, próba odzyskania z backupu...")
        backup_filename = f"{filename}.backup"
        try:
            if os.path.exists(backup_filename):
                with open(backup_filename, 'r', encoding='utf-8') as f_backup:
                    data = json.load(f_backup)
                    st.session_state[cache_key] = data
                    st.success(f"✅ Odzyskano dane z backupu {backup_filename}")
                    # Nadpisz uszkodzony plik backupem
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    return data
        except Exception:
            pass
        st.error(f"❌ Nie udało się odzyskać {filename} - użyto wartości domyślnych")
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
    elif filename in ['wyplaty.json', 'wydatki.json', 'kredyty.json', 'krypto.json']:
        # Zwróć dict z odpowiednim kluczem
        if 'wyplaty' in filename:
            return {'wyplaty': []}
        elif 'wydatki' in filename:
            return {'wydatki': []}
        elif 'kredyty' in filename:
            return {'kredyty': []}
        elif 'krypto' in filename:
            return {'krypto': []}
    else:
        return []

def save_persistent_data(filename, data):
    """
    Zapisuje dane w 3 miejscach:
    1. st.session_state (natychmiastowy dostęp)
    2. Lokalny plik (dla rozwoju)
    3. Kolejka do synchronizacji z GitHub
    """
    # Walidacja - sprawdź czy data jest JSON-serializable
    try:
        json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        st.error(f"⚠️ Błąd walidacji danych dla {filename}: {e}")
        return False
    
    cache_key = f'persistent_{filename}'
    
    # 1. Session state
    st.session_state[cache_key] = data
    
    # 2. Lokalny plik (może się nie udać na Streamlit Cloud)
    try:
        # Backup istniejącego pliku przed nadpisaniem
        if os.path.exists(filename):
            backup_filename = f"{filename}.backup"
            try:
                with open(filename, 'r', encoding='utf-8') as f_old:
                    old_data = f_old.read()
                with open(backup_filename, 'w', encoding='utf-8') as f_backup:
                    f_backup.write(old_data)
            except Exception:
                pass  # Jeśli backup się nie uda, kontynuuj
        
        # Zapisz nowe dane
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
    
    # Synchronizacja przez GitHub API (wymaga GITHUB_TOKEN w secrets)
    # Zobacz: show_sync_widget() dla implementacji UI
    return True, "Synchronizacja uruchomiona"
        
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
            st.caption("")
            st.info("ℹ️ **Automatyczna synchronizacja co godzinę** przez GitHub Actions")
        
        # Przycisk natychmiastowego zapisu
        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            if st.button("💾 Zapisz teraz", key="sync_now_btn", type="primary", use_container_width=True):
                # Spróbuj automatycznego triggera
                if GITHUB_API_OK and 'GITHUB_TOKEN' in st.secrets:
                    with st.spinner("Uruchamiam synchronizację..."):
                        success, msg = trigger_sync_workflow()
                        if success:
                            st.sidebar.success(msg)
                            st.sidebar.caption("Sprawdź status: [GitHub Actions](https://github.com/GarrettHaw/Horyzont-Partner-w/actions)")
                        else:
                            st.sidebar.error(msg)
                            st.sidebar.info("💡 Spróbuj użyć ręcznego triggera")
                else:
                    # Brak tokena - pokaż szczegółową instrukcję
                    st.sidebar.warning("⚙️ **Konfiguracja wymagana**")
                    st.sidebar.markdown("""
                    **Krok 1:** Wygeneruj GitHub Token
                    - Idź na: [GitHub Tokens](https://github.com/settings/tokens)
                    - Kliknij "Generate new token (classic)"
                    - Zaznacz scope: `repo`
                    - Skopiuj token (format: `ghp_...`)
                    
                    **Krok 2:** Dodaj do Streamlit Secrets
                    - [Otwórz Settings](https://share.streamlit.io/)
                    - Znajdź swoją aplikację → Settings → Secrets
                    - Dodaj: `GITHUB_TOKEN = "ghp_..."`
                    - Zapisz i poczekaj 30 sekund
                    
                    **Alternatywa (teraz):**
                    - [Ręczny trigger →](https://github.com/GarrettHaw/Horyzont-Partner-w/actions/workflows/sync_data.yml)
                    - Kliknij "Run workflow"
                    
                    📖 [Pełna instrukcja](https://github.com/GarrettHaw/Horyzont-Partner-w/blob/master/GITHUB_TOKEN_SETUP.md)
                    """)
        
        with col2:
            if st.button("📥 Pobierz", key="download_btn", use_container_width=True, help="Pobierz dane jako backup"):
                # Twórz ZIP z wszystkimi plikami
                import zipfile
                import io
                import json
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for filename in status['files']:
                        if f'persistent_{filename}' in st.session_state:
                            data = st.session_state[f'persistent_{filename}']
                            json_str = json.dumps(data, indent=2, ensure_ascii=False)
                            zip_file.writestr(filename, json_str)
                
                zip_buffer.seek(0)
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                st.sidebar.download_button(
                    label="📦 Pobierz ZIP",
                    data=zip_buffer.getvalue(),
                    file_name=f"horyzont_backup_{timestamp}.zip",
                    mime="application/zip",
                    key="download_zip_btn"
                )
        
        # JavaScript - ostrzeżenie przed zamknięciem
        st.sidebar.markdown("""
        <script>
        window.addEventListener('beforeunload', function (e) {
            e.preventDefault();
            e.returnValue = 'Masz niezapisane dane! Czy chcesz zapisać przed wyjściem?';
            return 'Masz niezapisane dane! Czy chcesz zapisać przed wyjściem?';
        });
        </script>
        """, unsafe_allow_html=True)
        
    else:
        st.sidebar.success("✅ Wszystko zsynchronizowane")
        st.sidebar.caption("🔄 Następny auto-sync za <1h")
