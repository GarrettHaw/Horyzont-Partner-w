"""
GitHub API Integration
Umożliwia wywołanie GitHub Actions workflow z poziomu Streamlit
"""

import requests
import streamlit as st
import json

def trigger_sync_workflow():
    """
    Wywołuje GitHub Actions workflow 'sync_data.yml' przez GitHub API
    Wymaga GITHUB_TOKEN w secrets
    """
    
    # Sprawdź czy mamy token
    if 'GITHUB_TOKEN' not in st.secrets:
        return False, "Brak GITHUB_TOKEN w secrets - użyj ręcznego triggera"
    
    token = st.secrets['GITHUB_TOKEN']
    
    # GitHub API endpoint dla repository_dispatch
    owner = "GarrettHaw"
    repo = "Horyzont-Partner-w"
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/sync_data.yml/dispatches"
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    
    # Payload - wywołaj workflow na głównej gałęzi
    payload = {
        'ref': 'master'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 204:
            return True, "✅ Synchronizacja uruchomiona! Sprawdź status w GitHub Actions."
        elif response.status_code == 404:
            return False, "❌ Workflow nie znaleziony - sprawdź nazwę pliku"
        elif response.status_code == 401:
            return False, "❌ Nieprawidłowy token GitHub"
        else:
            return False, f"❌ Błąd API: {response.status_code} - {response.text}"
    
    except requests.exceptions.Timeout:
        return False, "⏱️ Timeout - spróbuj ponownie"
    except Exception as e:
        return False, f"❌ Błąd: {str(e)}"

def save_files_to_github_directly(files_data):
    """
    ALTERNATYWNA METODA: Bezpośredni commit plików przez GitHub API
    Omija workflow - szybsze ale wymaga więcej konfiguracji
    """
    
    if 'GITHUB_TOKEN' not in st.secrets:
        return False, "Brak GITHUB_TOKEN"
    
    token = st.secrets['GITHUB_TOKEN']
    owner = "GarrettHaw"
    repo = "Horyzont-Partner-w"
    
    # TODO: Implementacja multi-file commit
    # Wymaga: GET sha dla każdego pliku, UPDATE z nowym contentem
    
    return False, "Funkcja w przygotowaniu - użyj trigger_sync_workflow()"
