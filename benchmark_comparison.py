"""
System Porównania z Benchmarkami - Horyzont Partnerów
====================================================
Porównuje portfel z rynkowymi indeksami:
- S&P 500 (^GSPC)
- WIG20 (^WIG20)
- Bitcoin (BTC-USD)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import yfinance as yf
import pandas as pd

# ============================================================
# KONFIGURACJA
# ============================================================

BENCHMARKS = {
    "SP500": {"ticker": "^GSPC", "name": "S&P 500", "color": "#1f77b4"},
    "WIG20": {"ticker": "^W20.PL", "name": "WIG20", "color": "#ff7f0e"},
    "BTC": {"ticker": "BTC-USD", "name": "Bitcoin", "color": "#2ca02c"}
}

CACHE_FILE = "benchmark_cache.json"
CACHE_TTL_HOURS = 1  # Cache na 1 godzinę

# ============================================================
# CACHE
# ============================================================

def load_cache() -> Dict:
    """Wczytuje cache z danymi benchmarków"""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache: Dict) -> bool:
    """Zapisuje cache"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def is_cache_valid(cache_entry: Dict) -> bool:
    """Sprawdza czy cache jest aktualny"""
    if 'timestamp' not in cache_entry:
        return False
    
    cache_time = datetime.fromisoformat(cache_entry['timestamp'])
    now = datetime.now()
    age = (now - cache_time).total_seconds() / 3600  # w godzinach
    
    return age < CACHE_TTL_HOURS

# ============================================================
# POBIERANIE DANYCH BENCHMARKÓW
# ============================================================

def fetch_benchmark_data(ticker: str, start_date: datetime, end_date: datetime = None) -> Optional[pd.DataFrame]:
    """
    Pobiera dane historyczne dla benchmarku
    """
    try:
        if end_date is None:
            end_date = datetime.now()
        
        print(f"📊 Pobieranie danych dla {ticker}...")
        
        benchmark = yf.Ticker(ticker)
        hist = benchmark.history(start=start_date, end=end_date)
        
        if hist.empty:
            print(f"⚠️ Brak danych dla {ticker}")
            return None
        
        # Zwróć tylko Close prices
        return hist[['Close']].copy()
        
    except Exception as e:
        print(f"⚠️ Błąd pobierania {ticker}: {e}")
        return None

def get_benchmark_data_cached(benchmark_id: str, start_date: datetime, end_date: datetime = None) -> Optional[pd.DataFrame]:
    """
    Pobiera dane benchmarku z cache lub z API
    """
    cache = load_cache()
    cache_key = f"{benchmark_id}_{start_date.strftime('%Y%m%d')}"
    
    # Sprawdź cache
    if cache_key in cache and is_cache_valid(cache[cache_key]):
        print(f"✅ Używam cache dla {benchmark_id}")
        data = cache[cache_key]['data']
        df = pd.DataFrame(data)
        df.index = pd.to_datetime(df.index)
        return df
    
    # Pobierz świeże dane
    ticker = BENCHMARKS[benchmark_id]['ticker']
    df = fetch_benchmark_data(ticker, start_date, end_date)
    
    if df is not None:
        # Zapisz do cache
        cache[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "data": df.to_dict()
        }
        save_cache(cache)
    
    return df

# ============================================================
# NORMALIZACJA DANYCH
# ============================================================

def normalize_to_100(series: pd.Series) -> pd.Series:
    """
    Normalizuje serię tak aby pierwszy punkt = 100
    """
    if series.empty or series.iloc[0] == 0:
        return series
    
    first_value = series.iloc[0]
    return (series / first_value) * 100

def prepare_comparison_data(portfolio_history: List[Dict], start_date: datetime = None) -> Dict:
    """
    Przygotowuje dane do porównania:
    - Portfolio (z daily_snapshots.json)
    - S&P 500
    - WIG20
    - Bitcoin
    
    Wszystkie znormalizowane do 100 na start
    """
    try:
        if not portfolio_history:
            return {"error": "Brak danych portfolio"}
        
        # Określ zakres dat
        if start_date is None:
            first_snapshot = portfolio_history[0]
            start_date = datetime.fromisoformat(first_snapshot['date'])
        
        end_date = datetime.now()
        
        # Przygotuj dane portfolio
        portfolio_dates = []
        portfolio_values = []
        
        for snapshot in portfolio_history:
            date = datetime.fromisoformat(snapshot['date'])
            if date >= start_date:
                portfolio_dates.append(date)
                portfolio_values.append(snapshot['totals']['net_worth_pln'])
        
        portfolio_series = pd.Series(portfolio_values, index=portfolio_dates)
        portfolio_normalized = normalize_to_100(portfolio_series)
        
        # Przygotuj dane benchmarków
        benchmarks_data = {}
        
        for bench_id, bench_info in BENCHMARKS.items():
            df = get_benchmark_data_cached(bench_id, start_date, end_date)
            
            if df is not None:
                # Normalizuj
                normalized = normalize_to_100(df['Close'])
                
                benchmarks_data[bench_id] = {
                    "name": bench_info['name'],
                    "color": bench_info['color'],
                    "dates": [d.isoformat() for d in normalized.index],
                    "values": normalized.tolist()
                }
        
        # Zwróć wszystkie dane
        return {
            "portfolio": {
                "name": "Twój Portfel",
                "color": "#d62728",
                "dates": [d.isoformat() for d in portfolio_normalized.index],
                "values": portfolio_normalized.tolist()
            },
            "benchmarks": benchmarks_data,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
    except Exception as e:
        print(f"⚠️ Błąd przygotowania danych: {e}")
        return {"error": str(e)}

# ============================================================
# STATYSTYKI PORÓWNAWCZE
# ============================================================

def calculate_comparison_stats(portfolio_history: List[Dict]) -> Dict:
    """
    Oblicza statystyki porównawcze:
    - Całkowity zwrot (%)
    - Outperformance vs każdy benchmark
    """
    try:
        if len(portfolio_history) < 2:
            return {"error": "Za mało danych"}
        
        # Portfolio performance
        first = portfolio_history[0]['totals']['net_worth_pln']
        last = portfolio_history[-1]['totals']['net_worth_pln']
        portfolio_return = ((last - first) / first) * 100
        
        # Zakres dat
        start_date = datetime.fromisoformat(portfolio_history[0]['date'])
        end_date = datetime.fromisoformat(portfolio_history[-1]['date'])
        days = (end_date - start_date).days
        
        stats = {
            "portfolio": {
                "total_return_pct": portfolio_return,
                "start_value": first,
                "end_value": last,
                "days": days
            },
            "benchmarks": {}
        }
        
        # Benchmark performance
        for bench_id, bench_info in BENCHMARKS.items():
            df = get_benchmark_data_cached(bench_id, start_date, end_date)
            
            if df is not None and len(df) >= 2:
                bench_first = df['Close'].iloc[0]
                bench_last = df['Close'].iloc[-1]
                bench_return = ((bench_last - bench_first) / bench_first) * 100
                
                outperformance = portfolio_return - bench_return
                
                stats["benchmarks"][bench_id] = {
                    "name": bench_info['name'],
                    "total_return_pct": bench_return,
                    "outperformance_pct": outperformance
                }
        
        return stats
        
    except Exception as e:
        print(f"⚠️ Błąd obliczania statystyk: {e}")
        return {"error": str(e)}

# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    import daily_snapshot as ds
    
    history = ds.load_snapshot_history()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "compare":
            # Porównaj z benchmarkami
            data = prepare_comparison_data(history)
            
            if "error" in data:
                print(f"❌ {data['error']}")
            else:
                print("\n📊 Dane porównawcze przygotowane!")
                print(f"Portfolio: {len(data['portfolio']['dates'])} punktów")
                for bench_id, bench_data in data['benchmarks'].items():
                    print(f"{bench_data['name']}: {len(bench_data['dates'])} punktów")
        
        elif command == "stats":
            # Pokaż statystyki
            stats = calculate_comparison_stats(history)
            
            if "error" in stats:
                print(f"❌ {stats['error']}")
            else:
                print("\n📈 STATYSTYKI PORÓWNAWCZE")
                print("=" * 50)
                print(f"\n💼 Twój Portfel:")
                print(f"   Zwrot: {stats['portfolio']['total_return_pct']:+.2f}%")
                print(f"   Okres: {stats['portfolio']['days']} dni")
                print(f"   Start: {stats['portfolio']['start_value']:.2f} PLN")
                print(f"   Teraz: {stats['portfolio']['end_value']:.2f} PLN")
                
                print(f"\n📊 Benchmarki:")
                for bench_id, bench_stats in stats['benchmarks'].items():
                    emoji = "🟢" if bench_stats['outperformance_pct'] > 0 else "🔴"
                    print(f"\n   {bench_stats['name']}:")
                    print(f"   Zwrot: {bench_stats['total_return_pct']:+.2f}%")
                    print(f"   {emoji} Różnica: {bench_stats['outperformance_pct']:+.2f}%")
        
        elif command == "clear-cache":
            # Wyczyść cache
            if os.path.exists(CACHE_FILE):
                os.remove(CACHE_FILE)
                print("✅ Cache wyczyszczony")
        
        else:
            print(f"⚠️ Nieznana komenda: {command}")
            print("\nDostępne komendy:")
            print("  python benchmark_comparison.py compare       - Pobierz dane do porównania")
            print("  python benchmark_comparison.py stats         - Pokaż statystyki")
            print("  python benchmark_comparison.py clear-cache   - Wyczyść cache")
    
    else:
        # Domyślnie pokaż statystyki
        stats = calculate_comparison_stats(history)
        
        if "error" not in stats:
            print("\n📈 SZYBKIE STATYSTYKI:")
            print(f"Portfolio: {stats['portfolio']['total_return_pct']:+.2f}%")
            for bench_id, bench_stats in stats['benchmarks'].items():
                emoji = "🟢" if bench_stats['outperformance_pct'] > 0 else "🔴"
                print(f"{bench_stats['name']}: {bench_stats['total_return_pct']:+.2f}% {emoji} ({bench_stats['outperformance_pct']:+.2f}%)")
