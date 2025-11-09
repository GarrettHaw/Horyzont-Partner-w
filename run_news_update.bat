@echo off
REM News Aggregator Auto-Update
REM Pobiera najnowsze newsy finansowe z Google News i Trading212

cd /d "%~dp0"

REM Aktywuj venv jeśli istnieje
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat

REM Uruchom update
echo ============================================
echo NEWS AGGREGATOR - Auto Update
echo ============================================
echo.

python news_aggregator.py update

echo.
echo ============================================
echo Update zakonczony o %date% %time%
echo ============================================
