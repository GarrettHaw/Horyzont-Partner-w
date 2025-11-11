"""
benchmark_comparison.py

Moduł do porównywania wydajności portfela z benchmarkami rynkowymi.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf


class BenchmarkComparison:
    """Porównanie portfela z popularnymi benchmarkami"""
    
    BENCHMARKS = {
        'SPY': 'S&P 500',
        'QQQ': 'NASDAQ-100',
        'IWM': 'Russell 2000',
        'EFA': 'MSCI EAFE',
        'AGG': 'US Aggregate Bond',
        'GLD': 'Gold',
        'BTC-USD': 'Bitcoin'
    }
    
    def __init__(self, cache_file: str = 'benchmark_cache.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Ładuje cache z danymi benchmarków"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_cache(self):
        """Zapisuje cache"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving benchmark cache: {e}")
    
    def get_benchmark_returns(self, period_days: int = 30) -> Dict[str, float]:
        """
        Pobiera zwroty benchmarków za określony okres
        
        Args:
            period_days: Liczba dni wstecz
            
        Returns:
            Słownik {symbol: return_percentage}
        """
        results = {}
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days + 5)  # +5 dni bufor
        
        for symbol, name in self.BENCHMARKS.items():
            try:
                # Sprawdź cache
                cache_key = f"{symbol}_{period_days}d"
                cache_entry = self.cache.get(cache_key, {})
                
                # Cache ważny przez 1 dzień
                if cache_entry and cache_entry.get('timestamp'):
                    cached_time = datetime.fromisoformat(cache_entry['timestamp'])
                    if datetime.now() - cached_time < timedelta(days=1):
                        results[symbol] = cache_entry['return']
                        continue
                
                # Pobierz dane
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
                
                if len(hist) < 2:
                    continue
                
                # Oblicz zwrot
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                ret = ((end_price - start_price) / start_price) * 100
                
                results[symbol] = round(ret, 2)
                
                # Cache
                self.cache[cache_key] = {
                    'return': ret,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
        
        self._save_cache()
        return results
    
    def compare_portfolio(self, portfolio_return: float, period_days: int = 30) -> Dict:
        """
        Porównuje zwrot portfela z benchmarkami
        
        Args:
            portfolio_return: Zwrot portfela w %
            period_days: Okres w dniach
            
        Returns:
            Dict z wynikami porównania
        """
        benchmark_returns = self.get_benchmark_returns(period_days)
        
        comparisons = []
        for symbol, bench_return in benchmark_returns.items():
            diff = portfolio_return - bench_return
            comparisons.append({
                'symbol': symbol,
                'name': self.BENCHMARKS[symbol],
                'return': bench_return,
                'difference': diff,
                'outperforming': diff > 0
            })
        
        # Sortuj po różnicy
        comparisons.sort(key=lambda x: x['difference'], reverse=True)
        
        # Statystyki
        outperforming_count = sum(1 for c in comparisons if c['outperforming'])
        
        return {
            'portfolio_return': portfolio_return,
            'period_days': period_days,
            'comparisons': comparisons,
            'outperforming_count': outperforming_count,
            'total_benchmarks': len(comparisons),
            'avg_benchmark_return': round(sum(c['return'] for c in comparisons) / len(comparisons), 2) if comparisons else 0
        }


def get_benchmark_comparison(portfolio_return: float, period_days: int = 30) -> Dict:
    """
    Helper function - porównuje portfel z benchmarkami
    
    Args:
        portfolio_return: Zwrot portfela w %
        period_days: Okres w dniach
        
    Returns:
        Dict z wynikami porównania
    """
    bc = BenchmarkComparison()
    return bc.compare_portfolio(portfolio_return, period_days)


if __name__ == "__main__":
    # Test
    bc = BenchmarkComparison()
    returns = bc.get_benchmark_returns(30)
    print("Benchmark Returns (30 days):")
    for symbol, ret in returns.items():
        print(f"  {symbol}: {ret:+.2f}%")
    
    # Test porównania
    comparison = bc.compare_portfolio(5.0, 30)
    print(f"\nPortfolio: +5.0%")
    print(f"Outperforming {comparison['outperforming_count']}/{comparison['total_benchmarks']} benchmarks")
