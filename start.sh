#!/bin/bash
# =============================================================================
# QUICK START - Szybkie uruchomienie aplikacji
# =============================================================================
# Użyj tego skryptu jeśli aplikacja jest już zainstalowana
# =============================================================================

echo "🚀 Starting Horyzont Partnerów..."

# Sprawdź czy service istnieje
if systemctl list-unit-files | grep -q horyzont.service; then
    echo "📦 Using systemd service..."
    sudo systemctl start horyzont
    sudo systemctl status horyzont --no-pager
    
    echo ""
    echo "✅ Application started!"
    echo "🌐 Access: http://$(hostname -I | awk '{print $1}'):8501"
    
    if systemctl is-active --quiet cloudflared; then
        echo "☁️  Cloudflare Tunnel: Active"
        echo "📱 External access available"
    fi
else
    echo "📦 Service not found, starting manually..."
    cd ~/horyzont
    source venv/bin/activate
    streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
fi
