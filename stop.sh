#!/bin/bash
# =============================================================================
# STOP - Zatrzymanie aplikacji
# =============================================================================

echo "🛑 Stopping Horyzont Partnerów..."

if systemctl list-unit-files | grep -q horyzont.service; then
    sudo systemctl stop horyzont
    echo "✅ Application stopped"
else
    echo "Killing streamlit processes..."
    pkill -f streamlit
    echo "✅ Done"
fi
