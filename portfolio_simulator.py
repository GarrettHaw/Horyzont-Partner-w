"""
Portfolio Simulator - Analiza scenariuszy 'co jeśli'
Pozwala testować wpływ hipotetycznych transakcji na portfel
"""

import copy
from typing import Dict, List, Tuple, Any
from datetime import datetime

class PortfolioSimulator:
    """Symulator zmian w portfelu do analizy scenariuszy"""
    
    def __init__(self, current_portfolio: Dict[str, Any]):
        """Inicjalizacja symulatora z aktualnym portfelem"""
        self.original_portfolio = copy.deepcopy(current_portfolio)
        self.simulated_portfolio = copy.deepcopy(current_portfolio)
        self.transactions = []
        self.scenarios = {}
        
    def add_transaction(self, asset_type: str, ticker: str, quantity: float, price: float, operation: str = "buy") -> Dict[str, Any]:
        """
        Dodaj transakcję do symulacji
        
        Args:
            asset_type: 'stock', 'crypto', 'dividend'
            ticker: symbol papieru wartościowego
            quantity: ilość
            price: cena jednostkowa
            operation: 'buy' lub 'sell'
        """
        cost = quantity * price
        transaction = {
            'timestamp': datetime.now().isoformat(),
            'type': asset_type,
            'ticker': ticker,
            'quantity': quantity,
            'price': price,
            'operation': operation,
            'cost': cost,
            'impact_pln': cost * (1 if operation == 'buy' else -1)
        }
        
        self.transactions.append(transaction)
        
        # Zastosuj transakcję do symulowanego portfela
        self._apply_transaction(transaction)
        
        return transaction
    
    def _apply_transaction(self, transaction: Dict[str, Any]) -> None:
        """Zastosuj transakcję do symulowanego portfela"""
        asset_type = transaction['type']
        ticker = transaction['ticker']
        quantity = transaction['quantity']
        price = transaction['price']
        operation = transaction['operation']
        
        if asset_type == 'stock':
            if 'PORTFEL_AKCJI' not in self.simulated_portfolio:
                self.simulated_portfolio['PORTFEL_AKCJI'] = {'Pozycje': []}
            
            positions = self.simulated_portfolio['PORTFEL_AKCJI']['Pozycje']
            pos_idx = next((i for i, p in enumerate(positions) if p.get('ticker') == ticker), None)
            
            if operation == 'buy':
                if pos_idx is not None:
                    positions[pos_idx]['quantity'] += quantity
                    positions[pos_idx]['avg_price'] = (
                        (positions[pos_idx]['avg_price'] * (positions[pos_idx]['quantity'] - quantity) + price * quantity) /
                        positions[pos_idx]['quantity']
                    )
                else:
                    positions.append({
                        'ticker': ticker,
                        'quantity': quantity,
                        'avg_price': price,
                        'current_price': price
                    })
            elif operation == 'sell':
                if pos_idx is not None:
                    positions[pos_idx]['quantity'] -= quantity
                    if positions[pos_idx]['quantity'] <= 0:
                        del positions[pos_idx]
        
        elif asset_type == 'crypto':
            if 'PORTFEL_KRYPTO' not in self.simulated_portfolio:
                self.simulated_portfolio['PORTFEL_KRYPTO'] = {'pozycje': {}}
            
            crypto_dict = self.simulated_portfolio['PORTFEL_KRYPTO']['pozycje']
            
            if operation == 'buy':
                if ticker in crypto_dict:
                    old_qty = crypto_dict[ticker]['ilosc']
                    old_price = crypto_dict[ticker]['cena_średnia']
                    crypto_dict[ticker]['ilosc'] += quantity
                    crypto_dict[ticker]['cena_średnia'] = (
                        (old_price * old_qty + price * quantity) / crypto_dict[ticker]['ilosc']
                    )
                else:
                    crypto_dict[ticker] = {
                        'ilosc': quantity,
                        'cena_średnia': price,
                        'wartosc_usd': quantity * price
                    }
            elif operation == 'sell':
                if ticker in crypto_dict:
                    crypto_dict[ticker]['ilosc'] -= quantity
                    if crypto_dict[ticker]['ilosc'] <= 0:
                        del crypto_dict[ticker]
    
    def calculate_impact(self) -> Dict[str, Any]:
        """Oblicz wpływ wszystkich transakcji na portfel"""
        original_value = self._calculate_portfolio_value(self.original_portfolio)
        simulated_value = self._calculate_portfolio_value(self.simulated_portfolio)
        
        impact = {
            'original_value_pln': original_value,
            'simulated_value_pln': simulated_value,
            'absolute_change_pln': simulated_value - original_value,
            'percentage_change': ((simulated_value - original_value) / original_value * 100) if original_value else 0,
            'transactions_count': len(self.transactions),
            'transaction_list': self.transactions
        }
        
        return impact
    
    def _calculate_portfolio_value(self, portfolio: Dict[str, Any]) -> float:
        """Oblicz całkowitą wartość portfela"""
        value = 0
        
        # Wartość akcji
        if 'PORTFEL_AKCJI' in portfolio:
            for position in portfolio['PORTFEL_AKCJI'].get('Pozycje', []):
                value += position.get('quantity', 0) * position.get('current_price', 0)
        
        # Wartość krypto
        if 'PORTFEL_KRYPTO' in portfolio:
            for crypto, data in portfolio['PORTFEL_KRYPTO'].get('pozycje', {}).items():
                value += data.get('wartosc_usd', 0)
        
        # Wartość netto
        if 'PODSUMOWANIE' in portfolio:
            value += portfolio['PODSUMOWANIE'].get('Wartosc_netto_PLN', 0)
        
        return value
    
    def save_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Zapisz aktualny scenariusz do porównania"""
        scenario = {
            'name': scenario_name,
            'timestamp': datetime.now().isoformat(),
            'portfolio': copy.deepcopy(self.simulated_portfolio),
            'transactions': copy.deepcopy(self.transactions),
            'impact': self.calculate_impact()
        }
        self.scenarios[scenario_name] = scenario
        return scenario
    
    def compare_scenarios(self, scenario1: str, scenario2: str) -> Dict[str, Any]:
        """Porównaj dwa scenariusze"""
        if scenario1 not in self.scenarios or scenario2 not in self.scenarios:
            return {'error': 'Scenariusz nie znaleziony'}
        
        s1 = self.scenarios[scenario1]
        s2 = self.scenarios[scenario2]
        
        comparison = {
            'scenario1': scenario1,
            'scenario2': scenario2,
            'value_diff_pln': s2['impact']['simulated_value_pln'] - s1['impact']['simulated_value_pln'],
            'percentage_diff': s2['impact']['percentage_change'] - s1['impact']['percentage_change'],
            's1_impact': s1['impact'],
            's2_impact': s2['impact']
        }
        
        return comparison
    
    def get_recommendations(self) -> List[Dict[str, str]]:
        """Uzyskaj rekomendacje na podstawie analizy"""
        recommendations = []
        
        impact = self.calculate_impact()
        
        if impact['percentage_change'] > 10:
            recommendations.append({
                'type': '🚀 WZROST',
                'message': f"Scenariusz wskazuje wzrost portfela o {impact['percentage_change']:.2f}%",
                'value': impact['absolute_change_pln']
            })
        elif impact['percentage_change'] < -10:
            recommendations.append({
                'type': '⚠️ SPADEK',
                'message': f"Scenariusz wskazuje spadek portfela o {abs(impact['percentage_change']):.2f}%",
                'value': impact['absolute_change_pln']
            })
        else:
            recommendations.append({
                'type': '➡️ NEUTRALNIE',
                'message': f"Zmiana portfela: {impact['percentage_change']:+.2f}%",
                'value': impact['absolute_change_pln']
            })
        
        return recommendations
    
    def reset_to_original(self) -> None:
        """Resetuj symulację do oryginalnego portfela"""
        self.simulated_portfolio = copy.deepcopy(self.original_portfolio)
        self.transactions = []


class ScenarioAnalyzer:
    """Analizator predefiniowanych scenariuszy"""
    
    @staticmethod
    def create_bullish_scenario(portfolio: Dict[str, Any], growth_percentage: float = 20) -> PortfolioSimulator:
        """Scenariusz byczo: wzrost wartości aktywów"""
        simulator = PortfolioSimulator(portfolio)
        
        if 'PORTFEL_AKCJI' in portfolio:
            for position in portfolio['PORTFEL_AKCJI'].get('Pozycje', []):
                new_price = position.get('current_price', 0) * (1 + growth_percentage / 100)
                simulator.simulated_portfolio['PORTFEL_AKCJI']['Pozycje'][
                    portfolio['PORTFEL_AKCJI']['Pozycje'].index(position)
                ]['current_price'] = new_price
        
        return simulator
    
    @staticmethod
    def create_bearish_scenario(portfolio: Dict[str, Any], decline_percentage: float = 20) -> PortfolioSimulator:
        """Scenariusz niedźwiedzi: spadek wartości aktywów"""
        simulator = PortfolioSimulator(portfolio)
        
        if 'PORTFEL_AKCJI' in portfolio:
            for position in portfolio['PORTFEL_AKCJI'].get('Pozycje', []):
                new_price = position.get('current_price', 0) * (1 - decline_percentage / 100)
                simulator.simulated_portfolio['PORTFEL_AKCJI']['Pozycje'][
                    portfolio['PORTFEL_AKCJI']['Pozycje'].index(position)
                ]['current_price'] = new_price
        
        return simulator
    
    @staticmethod
    def create_dividend_scenario(portfolio: Dict[str, Any], dividend_boost: float = 5) -> PortfolioSimulator:
        """Scenariusz dywidend: wzrost z tytułu dywidend"""
        simulator = PortfolioSimulator(portfolio)
        
        if 'PODSUMOWANIE' in simulator.simulated_portfolio:
            current_value = simulator.simulated_portfolio['PODSUMOWANIE'].get('Wartosc_netto_PLN', 0)
            dividend_income = current_value * (dividend_boost / 100)
            simulator.simulated_portfolio['PODSUMOWANIE']['Wartosc_netto_PLN'] += dividend_income
        
        return simulator
