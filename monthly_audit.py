"""
🔍 Monthly Portfolio Audit System
Comiesięczny audyt portfela: analiza performance, compliance, risk metrics

Uruchamiany automatycznie 1. dnia każdego miesiąca przez GitHub Actions
Generuje:
- monthly_snapshot.json - snapshot stanu portfela
- compliance_log.json - log zgodności z regułami inwestycyjnymi
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import requests

def load_json_file(filepath: str, default: Any = None) -> Any:
    """Załaduj plik JSON z obsługą błędów"""
    if not os.path.exists(filepath):
        return default if default is not None else {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Błąd wczytywania {filepath}: {e}")
        return default if default is not None else {}

def save_json_file(filepath: str, data: Any) -> bool:
    """Zapisz dane do pliku JSON"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Zapisano: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Błąd zapisu {filepath}: {e}")
        return False

def get_usd_pln_rate() -> float:
    """Pobierz aktualny kurs USD/PLN z NBP"""
    try:
        response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['rates'][0]['mid']
    except Exception as e:
        print(f"⚠️ Błąd pobierania kursu USD/PLN: {e}")
    
    return 3.65  # Fallback rate

def analyze_trading212_portfolio() -> Dict[str, Any]:
    """Analiza portfela Trading212"""
    cache = load_json_file('trading212_cache.json')
    
    if not cache or 'data' not in cache:
        return {'total_value_usd': 0, 'positions': 0, 'cash_usd': 0}
    
    positions = cache.get('data', {}).get('positions', [])
    total_value = sum(float(pos.get('quantity', 0)) * float(pos.get('currentPrice', 0)) for pos in positions)
    cash = float(cache.get('data', {}).get('cash', 0))
    
    return {
        'total_value_usd': round(total_value, 2),
        'positions': len(positions),
        'cash_usd': round(cash, 2),
        'total_with_cash_usd': round(total_value + cash, 2)
    }

def analyze_crypto_portfolio() -> Dict[str, Any]:
    """Analiza portfela krypto"""
    krypto = load_json_file('krypto.json', {'krypto': []})
    
    positions = krypto.get('krypto', [])
    if not positions:
        return {'total_value_usd': 0, 'positions': 0}
    
    total_value = sum(
        float(pos.get('ilosc', 0)) * float(pos.get('cena_usd', 0))
        for pos in positions if isinstance(pos, dict)
    )
    
    return {
        'total_value_usd': round(total_value, 2),
        'positions': len(positions)
    }

def analyze_debt() -> Dict[str, Any]:
    """Analiza zadłużenia"""
    kredyty = load_json_file('kredyty.json', {'kredyty': []})
    
    loans = kredyty.get('kredyty', [])
    if not loans:
        return {'total_debt_pln': 0, 'active_loans': 0}
    
    total_debt = sum(
        float(loan.get('kwota_poczatkowa', 0)) - float(loan.get('splacono', 0))
        for loan in loans if isinstance(loan, dict)
    )
    
    return {
        'total_debt_pln': round(total_debt, 2),
        'active_loans': len(loans)
    }

def analyze_goals() -> Dict[str, Any]:
    """Analiza celów finansowych"""
    cele = load_json_file('cele.json', {})
    
    rezerwa_target = float(cele.get('rezerwa_bezpieczenstwa_cel', 10000))
    rezerwa_current = float(cele.get('rezerwa_bezpieczenstwa_aktualna', 0))
    add_target = float(cele.get('add_target_value', 50000))
    
    return {
        'emergency_fund_target': rezerwa_target,
        'emergency_fund_current': rezerwa_current,
        'emergency_fund_progress': round((rezerwa_current / rezerwa_target * 100), 1) if rezerwa_target > 0 else 0,
        'add_target': add_target
    }

def check_compliance() -> List[Dict[str, Any]]:
    """Sprawdź zgodność z zasadami inwestycyjnymi"""
    issues = []
    
    # Sprawdź rezerwa bezpieczeństwa
    cele = load_json_file('cele.json', {})
    rezerwa_target = float(cele.get('rezerwa_bezpieczenstwa_cel', 10000))
    rezerwa_current = float(cele.get('rezerwa_bezpieczenstwa_aktualna', 0))
    
    if rezerwa_current < rezerwa_target:
        issues.append({
            'category': 'emergency_fund',
            'severity': 'warning',
            'message': f'Rezerwa bezpieczeństwa poniżej celu: {rezerwa_current:.0f} PLN / {rezerwa_target:.0f} PLN',
            'recommendation': 'Zwiększ rezerwę przed większymi inwestycjami'
        })
    
    # Sprawdź dywersyfikację akcji
    cache = load_json_file('trading212_cache.json')
    if cache and 'data' in cache:
        positions = cache.get('data', {}).get('positions', [])
        if positions:
            total_value = sum(float(pos.get('quantity', 0)) * float(pos.get('currentPrice', 0)) for pos in positions)
            
            for pos in positions:
                ticker = pos.get('ticker', '')
                position_value = float(pos.get('quantity', 0)) * float(pos.get('currentPrice', 0))
                percentage = (position_value / total_value * 100) if total_value > 0 else 0
                
                # Ostrzeżenie jeśli pojedyncza pozycja > 15% portfela
                if percentage > 15:
                    issues.append({
                        'category': 'diversification',
                        'severity': 'info',
                        'message': f'{ticker} stanowi {percentage:.1f}% portfela (>15%)',
                        'recommendation': 'Rozważ rebalansowanie przy kolejnych wpłatach'
                    })
    
    return issues

def generate_monthly_snapshot() -> Dict[str, Any]:
    """Generuj miesięczny snapshot portfela"""
    timestamp = datetime.now().isoformat()
    usd_pln = get_usd_pln_rate()
    
    stocks = analyze_trading212_portfolio()
    crypto = analyze_crypto_portfolio()
    debt = analyze_debt()
    goals = analyze_goals()
    compliance = check_compliance()
    
    # Oblicz net worth
    total_assets_usd = stocks['total_with_cash_usd'] + crypto['total_value_usd']
    total_assets_pln = total_assets_usd * usd_pln
    net_worth_pln = total_assets_pln - debt['total_debt_pln']
    
    snapshot = {
        'timestamp': timestamp,
        'month': datetime.now().strftime('%Y-%m'),
        'exchange_rate_usd_pln': round(usd_pln, 4),
        'portfolio': {
            'stocks': stocks,
            'crypto': crypto,
            'total_assets_usd': round(total_assets_usd, 2),
            'total_assets_pln': round(total_assets_pln, 2)
        },
        'debt': debt,
        'net_worth_pln': round(net_worth_pln, 2),
        'goals': goals,
        'compliance': {
            'issues_count': len(compliance),
            'status': 'pass' if len(compliance) == 0 else 'warnings' if all(i['severity'] != 'critical' for i in compliance) else 'critical'
        }
    }
    
    return snapshot

def generate_compliance_log(compliance_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generuj log compliance"""
    timestamp = datetime.now().isoformat()
    
    # Załaduj historię compliance
    compliance_log = load_json_file('compliance_log.json', {'history': []})
    
    # Dodaj nowy wpis
    new_entry = {
        'timestamp': timestamp,
        'month': datetime.now().strftime('%Y-%m'),
        'issues': compliance_issues,
        'status': 'pass' if len(compliance_issues) == 0 else 'warnings'
    }
    
    compliance_log['history'].insert(0, new_entry)
    
    # Zachowaj ostatnie 24 miesiące
    compliance_log['history'] = compliance_log['history'][:24]
    
    return compliance_log

def main():
    """Główna funkcja audytu"""
    print("🔍 Monthly Portfolio Audit - START")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Generuj snapshot
    print("\n📸 Generating monthly snapshot...")
    snapshot = generate_monthly_snapshot()
    
    # Zapisz snapshot
    if save_json_file('monthly_snapshot.json', snapshot):
        print(f"✅ Total Assets: ${snapshot['portfolio']['total_assets_usd']:,.2f}")
        print(f"✅ Net Worth: {snapshot['net_worth_pln']:,.2f} PLN")
        print(f"✅ Compliance Status: {snapshot['compliance']['status']}")
    
    # Generuj compliance log
    print("\n📋 Checking compliance...")
    compliance_issues = check_compliance()
    compliance_log = generate_compliance_log(compliance_issues)
    
    if save_json_file('compliance_log.json', compliance_log):
        print(f"✅ Issues found: {len(compliance_issues)}")
        for issue in compliance_issues:
            severity_icon = "⚠️" if issue['severity'] == 'warning' else "ℹ️"
            print(f"  {severity_icon} [{issue['category']}] {issue['message']}")
    
    print("\n" + "-" * 50)
    print("🔍 Monthly Portfolio Audit - COMPLETE ✅")

if __name__ == "__main__":
    main()
