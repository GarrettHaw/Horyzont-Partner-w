"""
Advanced Risk Analytics & Portfolio Metrics
Oblicza metryki ryzyka i wydajności portfela
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import json
import os


class RiskAnalytics:
    """Zaawansowana analiza ryzyka portfela"""
    
    def __init__(self, portfolio_data: Dict[str, Any], historical_data: Optional[List[Dict]] = None):
        """
        Inicjalizacja analityki ryzyka
        
        Args:
            portfolio_data: Aktualne dane portfela
            historical_data: Historia portfela (opcjonalna)
        """
        self.portfolio = portfolio_data
        self.history = historical_data or []
        self.risk_free_rate = 0.05  # 5% roczna stopa wolna od ryzyka (obligacje)
        
    def calculate_sharpe_ratio(self, returns: np.ndarray, period: str = 'daily') -> float:
        """
        Oblicz Sharpe Ratio - miara efektywności portfela względem ryzyka
        
        Args:
            returns: Tablica zwrotów
            period: 'daily', 'monthly', 'yearly'
        
        Returns:
            Sharpe Ratio (wyższe = lepsze)
        """
        if len(returns) < 2:
            return 0.0
        
        # Annualizacja w zależności od okresu
        periods_per_year = {'daily': 252, 'monthly': 12, 'yearly': 1}
        multiplier = periods_per_year.get(period, 252)
        
        # Średni zwrot
        avg_return = np.mean(returns)
        
        # Odchylenie standardowe
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Sharpe Ratio = (średni zwrot - stopa wolna od ryzyka) / odchylenie standardowe
        annual_return = avg_return * multiplier
        annual_std = std_return * np.sqrt(multiplier)
        
        sharpe = (annual_return - self.risk_free_rate) / annual_std
        
        return sharpe
    
    def calculate_sortino_ratio(self, returns: np.ndarray, period: str = 'daily') -> float:
        """
        Oblicz Sortino Ratio - podobny do Sharpe, ale uwzględnia tylko negatywne odchylenia
        
        Args:
            returns: Tablica zwrotów
            period: 'daily', 'monthly', 'yearly'
        
        Returns:
            Sortino Ratio (wyższe = lepsze)
        """
        if len(returns) < 2:
            return 0.0
        
        periods_per_year = {'daily': 252, 'monthly': 12, 'yearly': 1}
        multiplier = periods_per_year.get(period, 252)
        
        avg_return = np.mean(returns)
        
        # Tylko negatywne zwroty
        negative_returns = returns[returns < 0]
        
        if len(negative_returns) == 0:
            return float('inf')  # Brak strat
        
        downside_std = np.std(negative_returns)
        
        if downside_std == 0:
            return 0.0
        
        annual_return = avg_return * multiplier
        annual_downside_std = downside_std * np.sqrt(multiplier)
        
        sortino = (annual_return - self.risk_free_rate) / annual_downside_std
        
        return sortino
    
    def calculate_max_drawdown(self, values: np.ndarray) -> Tuple[float, int, int]:
        """
        Oblicz Maximum Drawdown - największy spadek od szczytu
        
        Args:
            values: Tablica wartości portfela w czasie
        
        Returns:
            (max_drawdown_percent, start_idx, end_idx)
        """
        if len(values) < 2:
            return 0.0, 0, 0
        
        # Oblicz cumulative maximum
        cummax = np.maximum.accumulate(values)
        
        # Oblicz drawdown
        drawdown = (values - cummax) / cummax
        
        # Znajdź maximum drawdown
        max_dd_idx = np.argmin(drawdown)
        max_dd = drawdown[max_dd_idx]
        
        # Znajdź początek drawdown (ostatni szczyt przed max DD)
        start_idx = np.argmax(values[:max_dd_idx]) if max_dd_idx > 0 else 0
        
        return abs(max_dd) * 100, start_idx, max_dd_idx
    
    def calculate_var(self, returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """
        Oblicz Value at Risk (VaR) - maksymalna przewidywana strata
        
        Args:
            returns: Tablica zwrotów
            confidence_level: Poziom ufności (0.95 = 95%)
        
        Returns:
            VaR jako procent (np. 5.2 = 5.2% maksymalna strata przy 95% pewności)
        """
        if len(returns) < 2:
            return 0.0
        
        # Historyczny VaR (percentyl)
        var = np.percentile(returns, (1 - confidence_level) * 100)
        
        return abs(var) * 100
    
    def calculate_cvar(self, returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """
        Oblicz Conditional VaR (CVaR/Expected Shortfall) - średnia strata przekraczająca VaR
        
        Args:
            returns: Tablica zwrotów
            confidence_level: Poziom ufności
        
        Returns:
            CVaR jako procent
        """
        if len(returns) < 2:
            return 0.0
        
        var = np.percentile(returns, (1 - confidence_level) * 100)
        
        # Średnia ze zwrotów gorszych niż VaR
        tail_losses = returns[returns <= var]
        
        if len(tail_losses) == 0:
            return abs(var) * 100
        
        cvar = np.mean(tail_losses)
        
        return abs(cvar) * 100
    
    def calculate_beta(self, portfolio_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """
        Oblicz Beta - zmienność portfela względem rynku
        
        Args:
            portfolio_returns: Zwroty portfela
            market_returns: Zwroty rynku (benchmark)
        
        Returns:
            Beta (1.0 = tak samo jak rynek, >1 = bardziej zmienny, <1 = mniej zmienny)
        """
        if len(portfolio_returns) < 2 or len(market_returns) < 2:
            return 1.0
        
        # Upewnij się, że mają tę samą długość
        min_len = min(len(portfolio_returns), len(market_returns))
        portfolio_returns = portfolio_returns[:min_len]
        market_returns = market_returns[:min_len]
        
        # Kowariancja i wariancja
        covariance = np.cov(portfolio_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        
        return beta
    
    def calculate_correlation_matrix(self, asset_returns: Dict[str, np.ndarray]) -> pd.DataFrame:
        """
        Oblicz macierz korelacji między aktywami
        
        Args:
            asset_returns: Słownik {nazwa_aktywa: tablica_zwrotów}
        
        Returns:
            DataFrame z macierzą korelacji
        """
        if not asset_returns:
            return pd.DataFrame()
        
        # Utwórz DataFrame ze zwrotów
        df = pd.DataFrame(asset_returns)
        
        # Oblicz korelację
        correlation_matrix = df.corr()
        
        return correlation_matrix
    
    def calculate_portfolio_volatility(self, returns: np.ndarray, period: str = 'daily') -> float:
        """
        Oblicz zmienność (volatility) portfela
        
        Args:
            returns: Tablica zwrotów
            period: Okres zwrotów
        
        Returns:
            Roczna zmienność jako procent
        """
        if len(returns) < 2:
            return 0.0
        
        periods_per_year = {'daily': 252, 'monthly': 12, 'yearly': 1}
        multiplier = periods_per_year.get(period, 252)
        
        std = np.std(returns)
        annual_volatility = std * np.sqrt(multiplier) * 100
        
        return annual_volatility
    
    def generate_risk_report(self) -> Dict[str, Any]:
        """
        Generuj kompletny raport ryzyka
        
        Returns:
            Słownik z wszystkimi metrykami ryzyka
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {}
        }
        
        # Jeśli mamy historię, oblicz metryki
        if len(self.history) >= 2:
            # Wyciągnij wartości portfela z historii - OBSŁUGA RÓŻNYCH FORMATÓW
            values = []
            for h in self.history:
                # Nowy format (daily_snapshots.json): totals.net_worth_pln
                if 'totals' in h and 'net_worth_pln' in h['totals']:
                    values.append(h['totals']['net_worth_pln'])
                # Stary format: value lub wartosc_netto
                elif 'value' in h:
                    values.append(h['value'])
                elif 'wartosc_netto' in h:
                    values.append(h['wartosc_netto'])
                else:
                    # Fallback - spróbuj obliczyć z assets - debt
                    assets = h.get('totals', {}).get('assets_pln', 0) if 'totals' in h else h.get('assets', 0)
                    debt = h.get('totals', {}).get('debt_pln', 0) if 'totals' in h else h.get('debt', 0)
                    values.append(assets - debt)
            
            values = np.array(values)
            
            # Oblicz zwroty
            returns = np.diff(values) / values[:-1]
            
            # Sharpe Ratio
            report['metrics']['sharpe_ratio'] = self.calculate_sharpe_ratio(returns)
            
            # Sortino Ratio
            report['metrics']['sortino_ratio'] = self.calculate_sortino_ratio(returns)
            
            # Maximum Drawdown
            max_dd, start_idx, end_idx = self.calculate_max_drawdown(values)
            report['metrics']['max_drawdown_percent'] = max_dd
            report['metrics']['max_drawdown_period'] = f"{start_idx} -> {end_idx}"
            
            # VaR
            report['metrics']['var_95'] = self.calculate_var(returns, 0.95)
            report['metrics']['var_99'] = self.calculate_var(returns, 0.99)
            
            # CVaR
            report['metrics']['cvar_95'] = self.calculate_cvar(returns, 0.95)
            
            # Volatility
            report['metrics']['annual_volatility_percent'] = self.calculate_portfolio_volatility(returns)
            
            # Średni zwrot
            report['metrics']['average_return_percent'] = np.mean(returns) * 100
            
            # Całkowity zwrot
            if values[0] != 0:
                total_return = ((values[-1] - values[0]) / values[0]) * 100
                report['metrics']['total_return_percent'] = total_return
        
        # Aktualna wartość portfela - obsłuż różne formaty
        if 'PODSUMOWANIE' in self.portfolio and 'Wartosc_netto_PLN' in self.portfolio['PODSUMOWANIE']:
            current_value = self.portfolio['PODSUMOWANIE']['Wartosc_netto_PLN']
        elif 'totals' in self.portfolio and 'net_worth_pln' in self.portfolio['totals']:
            current_value = self.portfolio['totals']['net_worth_pln']
        elif 'wartosc_netto_pln' in self.portfolio:
            current_value = self.portfolio['wartosc_netto_pln']
        else:
            # Spróbuj obliczyć z aktywów i zobowiązań
            assets = self.portfolio.get('wartosc_aktywow_pln', 0)
            debt = self.portfolio.get('zobowiazania_pln', 0)
            current_value = assets - debt
        
        report['current_portfolio_value'] = current_value
        
        # Dźwignia
        report['leverage_ratio'] = self.portfolio.get('PODSUMOWANIE', {}).get('Leverage_ratio', 0)
        
        return report
    
    def risk_score(self) -> Tuple[str, int, str]:
        """
        Oblicz ogólny poziom ryzyka portfela
        
        Returns:
            (poziom_ryzyka, score_0_100, opis)
        """
        report = self.generate_risk_report()
        metrics = report.get('metrics', {})
        
        score = 50  # Bazowy score
        
        # Sharpe Ratio (wyższe = lepsze, niższe ryzyko relatywne)
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe > 2:
            score += 15
        elif sharpe > 1:
            score += 10
        elif sharpe < 0.5:
            score -= 10
        
        # Max Drawdown (niższe = lepsze)
        max_dd = metrics.get('max_drawdown_percent', 0)
        if max_dd < 10:
            score += 10
        elif max_dd < 20:
            score += 5
        elif max_dd > 40:
            score -= 15
        
        # Volatility (niższa = niższe ryzyko)
        volatility = metrics.get('annual_volatility_percent', 0)
        if volatility < 15:
            score += 10
        elif volatility < 25:
            score += 5
        elif volatility > 40:
            score -= 10
        
        # VaR
        var_95 = metrics.get('var_95', 0)
        if var_95 < 3:
            score += 5
        elif var_95 > 10:
            score -= 10
        
        # Dźwignia
        leverage = report.get('leverage_ratio', 0)
        if leverage < 20:
            score += 5
        elif leverage > 50:
            score -= 15
        
        # Ogranicz score do 0-100
        score = max(0, min(100, score))
        
        # Określ poziom ryzyka
        if score >= 80:
            level = "NISKIE"
            description = "Portfel wykazuje niskie ryzyko z dobrą dywersyfikacją"
        elif score >= 60:
            level = "UMIARKOWANE"
            description = "Portfel ma zrównoważony profil ryzyka"
        elif score >= 40:
            level = "PODWYŻSZONE"
            description = "Portfel wykazuje zwiększone ryzyko, rozważ rebalansowanie"
        else:
            level = "WYSOKIE"
            description = "⚠️ Portfel ma wysokie ryzyko, zalecane działanie"
        
        return level, score, description


class PortfolioHistory:
    """Zarządzanie historią portfela"""
    
    def __init__(self, history_file: str = 'portfolio_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Załaduj historię z pliku"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_snapshot(self, portfolio_data: Dict[str, Any]) -> None:
        """Zapisz snapshot portfela"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'value': portfolio_data.get('PODSUMOWANIE', {}).get('Wartosc_netto_PLN', 0),
            'value_usd': portfolio_data.get('PODSUMOWANIE', {}).get('Wartosc_netto_USD', 0),
            'leverage': portfolio_data.get('PODSUMOWANIE', {}).get('Leverage_ratio', 0),
            'stocks_count': len(portfolio_data.get('PORTFEL_AKCJI', {}).get('Pozycje', [])),
            'crypto_count': len(portfolio_data.get('PORTFEL_KRYPTO', {}).get('pozycje', {}))
        }
        
        self.history.append(snapshot)
        
        # Zachowaj tylko ostatnie 365 dni
        if len(self.history) > 365:
            self.history = self.history[-365:]
        
        # Zapisz do pliku
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def get_history(self, days: int = None) -> List[Dict]:
        """Pobierz historię"""
        if days:
            return self.history[-days:]
        return self.history
