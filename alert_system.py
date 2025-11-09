"""
System Alertów i Notyfikacji - Horyzont Partnerów
================================================
Wykrywa i zarządza wszystkimi alertami portfelowymi:
- Nowe pozycje w portfelu
- Znaczące zmiany cen (>10%)
- Zbliżające się terminy płatności kredytów
- Osiągnięte cele finansowe
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import yfinance as yf

# ============================================================
# KONFIGURACJA
# ============================================================

ALERTS_FILE = "alerts.json"
GOAL_ACHIEVEMENTS_FILE = "goal_achievements.json"
PRICE_CHANGE_THRESHOLD = 10.0  # procent
LOAN_WARNING_DAYS = [7, 3, 1]  # dni przed terminem

# ============================================================
# POMOCNICZE FUNKCJE
# ============================================================

def load_json_file(filename: str, default: Any = None) -> Any:
    """Wczytuje plik JSON z obsługą błędów"""
    if not os.path.exists(filename):
        return default if default is not None else {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Błąd wczytywania {filename}: {e}")
        return default if default is not None else {}

def save_json_file(filename: str, data: Any) -> bool:
    """Zapisuje dane do pliku JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Błąd zapisywania {filename}: {e}")
        return False

def get_alerts_history() -> List[Dict]:
    """Pobiera historię wszystkich alertów"""
    alerts = load_json_file(ALERTS_FILE, {"history": []})
    return alerts.get("history", [])

def add_alert(alert_type: str, title: str, message: str, severity: str = "info", metadata: Dict = None) -> bool:
    """Dodaje nowy alert do historii"""
    alerts = load_json_file(ALERTS_FILE, {"history": []})
    
    new_alert = {
        "id": len(alerts.get("history", [])) + 1,
        "timestamp": datetime.now().isoformat(),
        "type": alert_type,  # new_position, price_change, loan_due, goal_achieved
        "severity": severity,  # info, warning, critical, success
        "title": title,
        "message": message,
        "read": False,
        "metadata": metadata or {}
    }
    
    if "history" not in alerts:
        alerts["history"] = []
    
    alerts["history"].insert(0, new_alert)  # Najnowsze na początku
    
    # Ogranicz historię do 500 alertów
    alerts["history"] = alerts["history"][:500]
    
    return save_json_file(ALERTS_FILE, alerts)

# ============================================================
# 1. WYKRYWANIE NOWYCH POZYCJI
# ============================================================

def detect_new_positions() -> List[Dict]:
    """
    Porównuje aktualny portfel z ostatnim snapshotem
    Zwraca listę nowych pozycji
    """
    try:
        import daily_snapshot as ds
        import gra_rpg
        
        # Pobierz historię snapshots
        history = ds.load_snapshot_history()
        if len(history) < 2:
            return []
        
        # Ostatnie 2 snapshoty
        latest = history[-1]
        previous = history[-2]
        
        # Pobierz aktualne dane
        cele = load_json_file("cele.json", {})
        current_state = gra_rpg.pobierz_stan_spolki(cele)
        
        new_positions = []
        
        # Sprawdź akcje
        current_stocks = current_state.get('PORTFEL_AKCJI', {}).get('Pozycje', {})
        previous_stocks_breakdown = previous.get('stocks', {}).get('breakdown', {})
        
        for ticker, data in current_stocks.items():
            if ticker not in previous_stocks_breakdown:
                new_positions.append({
                    "type": "stock",
                    "ticker": ticker,
                    "name": data.get('nazwa', ticker),
                    "quantity": data.get('ilosc', 0),
                    "price_usd": data.get('cena_usd', 0),
                    "value_usd": data.get('wartosc_usd', 0),
                    "detected_at": datetime.now().isoformat()
                })
                
                # Dodaj alert
                add_alert(
                    alert_type="new_position",
                    title=f"🆕 Nowa akcja: {ticker}",
                    message=f"Dodano {data.get('ilosc', 0)} akcji {data.get('nazwa', ticker)} po ${data.get('cena_usd', 0):.2f}",
                    severity="info",
                    metadata={
                        "ticker": ticker,
                        "type": "stock",
                        "quantity": data.get('ilosc', 0),
                        "price": data.get('cena_usd', 0)
                    }
                )
        
        # Sprawdź krypto
        current_crypto = current_state.get('PORTFEL_KRYPTO', {}).get('Pozycje', {})
        previous_crypto_breakdown = previous.get('crypto', {}).get('breakdown', {})
        
        for symbol, data in current_crypto.items():
            if symbol not in previous_crypto_breakdown:
                new_positions.append({
                    "type": "crypto",
                    "symbol": symbol,
                    "name": data.get('nazwa', symbol),
                    "quantity": data.get('ilosc', 0),
                    "price_usd": data.get('cena_usd', 0),
                    "value_usd": data.get('wartosc_usd', 0),
                    "detected_at": datetime.now().isoformat()
                })
                
                # Dodaj alert
                add_alert(
                    alert_type="new_position",
                    title=f"🆕 Nowe krypto: {symbol}",
                    message=f"Dodano {data.get('ilosc', 0):.4f} {data.get('nazwa', symbol)} po ${data.get('cena_usd', 0):.2f}",
                    severity="info",
                    metadata={
                        "symbol": symbol,
                        "type": "crypto",
                        "quantity": data.get('ilosc', 0),
                        "price": data.get('cena_usd', 0)
                    }
                )
        
        return new_positions
        
    except Exception as e:
        print(f"⚠️ Błąd wykrywania nowych pozycji: {e}")
        return []

# ============================================================
# 2. ALERTY ZMIAN CEN >10%
# ============================================================

def detect_price_changes() -> List[Dict]:
    """
    Porównuje dzisiejsze ceny z wczorajszymi
    Zwraca pozycje ze zmianą >10%
    """
    try:
        import daily_snapshot as ds
        
        history = ds.load_snapshot_history()
        if len(history) < 2:
            return []
        
        latest = history[-1]
        previous = history[-2]
        
        significant_changes = []
        
        # Sprawdź akcje
        latest_stocks = latest.get('stocks', {}).get('breakdown', {})
        previous_stocks = previous.get('stocks', {}).get('breakdown', {})
        
        for ticker, latest_data in latest_stocks.items():
            if ticker in previous_stocks:
                latest_price = latest_data.get('price_usd', 0)
                previous_price = previous_stocks[ticker].get('price_usd', 0)
                
                if previous_price > 0:
                    change_pct = ((latest_price - previous_price) / previous_price) * 100
                    
                    if abs(change_pct) >= PRICE_CHANGE_THRESHOLD:
                        significant_changes.append({
                            "type": "stock",
                            "ticker": ticker,
                            "name": latest_data.get('name', ticker),
                            "previous_price": previous_price,
                            "current_price": latest_price,
                            "change_pct": change_pct,
                            "detected_at": datetime.now().isoformat()
                        })
                        
                        # Dodaj alert
                        emoji = "🔴📉" if change_pct < 0 else "🟢📈"
                        severity = "warning" if abs(change_pct) > 20 else "info"
                        
                        add_alert(
                            alert_type="price_change",
                            title=f"{emoji} {ticker}: {change_pct:+.1f}%",
                            message=f"{latest_data.get('name', ticker)}: ${previous_price:.2f} → ${latest_price:.2f} ({change_pct:+.1f}%)",
                            severity=severity,
                            metadata={
                                "ticker": ticker,
                                "type": "stock",
                                "change_pct": change_pct,
                                "previous_price": previous_price,
                                "current_price": latest_price
                            }
                        )
        
        # Sprawdź krypto
        latest_crypto = latest.get('crypto', {}).get('breakdown', {})
        previous_crypto = previous.get('crypto', {}).get('breakdown', {})
        
        for symbol, latest_data in latest_crypto.items():
            if symbol in previous_crypto:
                latest_price = latest_data.get('price_usd', 0)
                previous_price = previous_crypto[symbol].get('price_usd', 0)
                
                if previous_price > 0:
                    change_pct = ((latest_price - previous_price) / previous_price) * 100
                    
                    if abs(change_pct) >= PRICE_CHANGE_THRESHOLD:
                        significant_changes.append({
                            "type": "crypto",
                            "symbol": symbol,
                            "name": latest_data.get('name', symbol),
                            "previous_price": previous_price,
                            "current_price": latest_price,
                            "change_pct": change_pct,
                            "detected_at": datetime.now().isoformat()
                        })
                        
                        # Dodaj alert
                        emoji = "🔴📉" if change_pct < 0 else "🟢📈"
                        severity = "warning" if abs(change_pct) > 20 else "info"
                        
                        add_alert(
                            alert_type="price_change",
                            title=f"{emoji} {symbol}: {change_pct:+.1f}%",
                            message=f"{latest_data.get('name', symbol)}: ${previous_price:.2f} → ${latest_price:.2f} ({change_pct:+.1f}%)",
                            severity=severity,
                            metadata={
                                "symbol": symbol,
                                "type": "crypto",
                                "change_pct": change_pct,
                                "previous_price": previous_price,
                                "current_price": latest_price
                            }
                        )
        
        return significant_changes
        
    except Exception as e:
        print(f"⚠️ Błąd wykrywania zmian cen: {e}")
        return []

# ============================================================
# 3. ALERTY TERMINÓW PŁATNOŚCI KREDYTÓW
# ============================================================

def detect_loan_due_dates() -> List[Dict]:
    """
    Sprawdza zbliżające się terminy płatności kredytów
    Zwraca alerty dla terminów w ciągu 7/3/1 dni
    """
    try:
        loans_data = load_json_file("kredyty.json", {})
        
        due_soon = []
        today = datetime.now().date()
        
        for loan_name, loan_info in loans_data.items():
            if isinstance(loan_info, dict) and 'termin_platnosci' in loan_info:
                try:
                    due_date_str = loan_info['termin_platnosci']
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                    
                    days_until_due = (due_date - today).days
                    
                    if days_until_due in LOAN_WARNING_DAYS:
                        amount = loan_info.get('kwota_raty', loan_info.get('saldo', 0))
                        
                        due_soon.append({
                            "loan_name": loan_name,
                            "due_date": due_date_str,
                            "days_until_due": days_until_due,
                            "amount": amount,
                            "detected_at": datetime.now().isoformat()
                        })
                        
                        # Dodaj alert
                        severity = "critical" if days_until_due == 1 else ("warning" if days_until_due == 3 else "info")
                        emoji = "🔴" if days_until_due == 1 else ("🟠" if days_until_due == 3 else "🟡")
                        
                        add_alert(
                            alert_type="loan_due",
                            title=f"{emoji} Płatność kredytu za {days_until_due} dni",
                            message=f"{loan_name}: {amount:.2f} PLN - termin: {due_date_str}",
                            severity=severity,
                            metadata={
                                "loan_name": loan_name,
                                "due_date": due_date_str,
                                "days_until_due": days_until_due,
                                "amount": amount
                            }
                        )
                
                except Exception as e:
                    print(f"⚠️ Błąd parsowania daty dla {loan_name}: {e}")
                    continue
        
        return due_soon
        
    except Exception as e:
        print(f"⚠️ Błąd wykrywania terminów kredytów: {e}")
        return []

# ============================================================
# 4. NOTYFIKACJE OSIĄGNIĘTYCH CELÓW
# ============================================================

def detect_achieved_goals() -> List[Dict]:
    """
    Sprawdza czy jakieś cele zostały osiągnięte (100% lub więcej)
    Zapisuje do goal_achievements.json i tworzy alert
    """
    try:
        cele = load_json_file("cele.json", {})
        achievements = load_json_file(GOAL_ACHIEVEMENTS_FILE, {"achieved": []})
        
        # Lista już osiągniętych celów
        already_achieved = {a['goal_id'] for a in achievements.get("achieved", [])}
        
        newly_achieved = []
        
        for goal_id, goal_data in cele.items():
            if isinstance(goal_data, dict):
                target = goal_data.get('cel', 0)
                current = goal_data.get('aktualnie', 0)
                
                if target > 0:
                    progress = (current / target) * 100
                    
                    if progress >= 100 and goal_id not in already_achieved:
                        achievement = {
                            "goal_id": goal_id,
                            "goal_name": goal_data.get('nazwa', goal_id),
                            "target": target,
                            "achieved_value": current,
                            "progress_pct": progress,
                            "achieved_at": datetime.now().isoformat()
                        }
                        
                        newly_achieved.append(achievement)
                        
                        # Zapisz do achievements
                        if "achieved" not in achievements:
                            achievements["achieved"] = []
                        achievements["achieved"].append(achievement)
                        
                        # Dodaj alert
                        add_alert(
                            alert_type="goal_achieved",
                            title=f"🎉 Cel osiągnięty: {goal_data.get('nazwa', goal_id)}",
                            message=f"Gratulacje! Osiągnięto {current:.2f} / {target:.2f} ({progress:.1f}%)",
                            severity="success",
                            metadata={
                                "goal_id": goal_id,
                                "goal_name": goal_data.get('nazwa', goal_id),
                                "target": target,
                                "achieved_value": current,
                                "progress_pct": progress
                            }
                        )
        
        if newly_achieved:
            save_json_file(GOAL_ACHIEVEMENTS_FILE, achievements)
        
        return newly_achieved
        
    except Exception as e:
        print(f"⚠️ Błąd wykrywania osiągniętych celów: {e}")
        return []

# ============================================================
# FUNKCJA GŁÓWNA - URUCHOM WSZYSTKIE DETEKTORY
# ============================================================

def run_all_detectors(verbose: bool = True) -> Dict[str, List]:
    """
    Uruchamia wszystkie detektory alertów
    Zwraca słownik z wynikami
    """
    results = {
        "new_positions": [],
        "price_changes": [],
        "loan_due_dates": [],
        "achieved_goals": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if verbose:
        print("🔍 Uruchamiam system wykrywania alertów...")
        print("=" * 50)
    
    # 1. Nowe pozycje
    if verbose:
        print("\n1️⃣ Wykrywanie nowych pozycji...")
    results["new_positions"] = detect_new_positions()
    if verbose:
        print(f"   ✅ Znaleziono: {len(results['new_positions'])}")
    
    # 2. Zmiany cen >10%
    if verbose:
        print("\n2️⃣ Wykrywanie znaczących zmian cen...")
    results["price_changes"] = detect_price_changes()
    if verbose:
        print(f"   ✅ Znaleziono: {len(results['price_changes'])}")
    
    # 3. Terminy kredytów
    if verbose:
        print("\n3️⃣ Sprawdzanie terminów płatności kredytów...")
    results["loan_due_dates"] = detect_loan_due_dates()
    if verbose:
        print(f"   ✅ Znaleziono: {len(results['loan_due_dates'])}")
    
    # 4. Osiągnięte cele
    if verbose:
        print("\n4️⃣ Sprawdzanie osiągniętych celów...")
    results["achieved_goals"] = detect_achieved_goals()
    if verbose:
        print(f"   ✅ Znaleziono: {len(results['achieved_goals'])}")
    
    if verbose:
        print("\n" + "=" * 50)
        total_alerts = sum(len(v) if isinstance(v, list) else 0 for v in results.values())
        print(f"✅ Zakończono. Łącznie nowych alertów: {total_alerts}")
    
    return results

# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "run":
            # Uruchom wszystkie detektory
            run_all_detectors(verbose=True)
        
        elif command == "history":
            # Pokaż historię alertów
            alerts = get_alerts_history()
            print(f"\n📋 Historia alertów ({len(alerts)} wpisów):\n")
            for alert in alerts[:10]:  # Ostatnie 10
                timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%Y-%m-%d %H:%M")
                print(f"{timestamp} | {alert['title']}")
                print(f"   {alert['message']}")
                print()
        
        elif command == "clear":
            # Wyczyść historię
            if save_json_file(ALERTS_FILE, {"history": []}):
                print("✅ Historia alertów wyczyszczona")
        
        else:
            print(f"⚠️ Nieznana komenda: {command}")
            print("\nDostępne komendy:")
            print("  python alert_system.py run      - Uruchom wszystkie detektory")
            print("  python alert_system.py history  - Pokaż historię alertów")
            print("  python alert_system.py clear    - Wyczyść historię alertów")
    
    else:
        # Domyślnie uruchom wszystkie detektory
        run_all_detectors(verbose=True)
