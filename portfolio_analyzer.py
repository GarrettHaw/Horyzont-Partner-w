import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from advisor_memory import AdvisorMemory

class PortfolioAnalyzer:
    def __init__(self, advisor_memory: AdvisorMemory):
        self.advisor_memory = advisor_memory
        
    def analyze_portfolio(self, portfolio_data: Dict) -> Dict:
        """Przeprowadza pełną analizę portfela"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": self._calculate_portfolio_health(portfolio_data),
            "risk_analysis": self._analyze_risk(portfolio_data),
            "advisor_insights": self._get_advisor_insights(portfolio_data),
            "recommendations": self._generate_recommendations(portfolio_data),
            "metrics": self._calculate_metrics(portfolio_data)
        }
        return analysis
        
    def _calculate_portfolio_health(self, portfolio_data: Dict) -> Dict:
        """Oblicza ogólny stan portfela"""
        health = {
            "score": 0,
            "factors": [],
            "warnings": []
        }
        
        # Analiza dywersyfikacji
        stock_count = len(portfolio_data.get("stocks", {}))
        asset_classes = len([k for k in ["stocks", "crypto", "cash"] if portfolio_data.get(k)])
        
        if stock_count < 20:
            health["warnings"].append("Mała dywersyfikacja akcji")
        if asset_classes < 3:
            health["warnings"].append("Mała dywersyfikacja klas aktywów")
            
        # Analiza alokacji
        total_value = sum(asset.get("value", 0) for asset_type in ["stocks", "crypto"]
                         for asset in portfolio_data.get(asset_type, {}).values())
        
        if total_value > 0:
            for asset_type in ["stocks", "crypto"]:
                allocation = sum(asset.get("value", 0) for asset in portfolio_data.get(asset_type, {}).values()) / total_value
                if allocation > 0.7:
                    health["warnings"].append(f"Zbyt duża koncentracja w {asset_type}")
                    
        # Oblicz końcowy wynik
        health["score"] = 1.0 - (len(health["warnings"]) * 0.1)  # Każde ostrzeżenie obniża wynik o 10%
        return health
        
    def _analyze_risk(self, portfolio_data: Dict) -> Dict:
        """Analizuje różne aspekty ryzyka portfela"""
        risk_analysis = {
            "concentration_risk": self._analyze_concentration_risk(portfolio_data),
            "volatility_risk": self._analyze_volatility_risk(portfolio_data),
            "correlation_risk": self._analyze_correlation_risk(portfolio_data),
            "overall_risk_score": 0
        }
        
        # Oblicz ogólny poziom ryzyka jako średnią ważoną
        weights = {"concentration_risk": 0.4, "volatility_risk": 0.3, "correlation_risk": 0.3}
        risk_analysis["overall_risk_score"] = sum(
            risk_analysis[risk_type]["score"] * weight
            for risk_type, weight in weights.items()
        )
        
        return risk_analysis
        
    def _analyze_concentration_risk(self, portfolio_data: Dict) -> Dict:
        """Analizuje ryzyko koncentracji"""
        assets = []
        for asset_type in ["stocks", "crypto"]:
            for symbol, data in portfolio_data.get(asset_type, {}).items():
                assets.append({
                    "symbol": symbol,
                    "type": asset_type,
                    "value": data.get("value", 0)
                })
                
        total_value = sum(asset["value"] for asset in assets)
        if total_value == 0:
            return {"score": 0, "warnings": ["Brak aktywów w portfelu"]}
            
        # Oblicz koncentrację według HHI (Herfindahl-Hirschman Index)
        hhi = sum((asset["value"] / total_value) ** 2 for asset in assets)
        
        # Znajdź największe pozycje
        assets.sort(key=lambda x: x["value"], reverse=True)
        top_positions = assets[:3]
        
        warnings = []
        if hhi > 0.25:  # Wysoka koncentracja
            warnings.append("Wysoka koncentracja portfela")
        for pos in top_positions:
            if pos["value"] / total_value > 0.2:
                warnings.append(f"Duża pojedyncza pozycja: {pos['symbol']}")
                
        return {
            "score": min(1, hhi),
            "hhi": hhi,
            "top_positions": [
                {
                    "symbol": pos["symbol"],
                    "percentage": (pos["value"] / total_value) * 100
                }
                for pos in top_positions
            ],
            "warnings": warnings
        }
        
    def _analyze_volatility_risk(self, portfolio_data: Dict) -> Dict:
        """Analizuje ryzyko zmienności"""
        # Tutaj można dodać rzeczywiste obliczenia zmienności na podstawie historycznych danych
        # Na razie używamy uproszczonego modelu
        risk_scores = {
            "stocks": 0.5,  # Umiarkowane ryzyko
            "crypto": 0.8,  # Wysokie ryzyko
            "cash": 0.1     # Niskie ryzyko
        }
        
        total_value = sum(sum(asset.get("value", 0) for asset in assets.values())
                         for asset_type, assets in portfolio_data.items()
                         if asset_type in risk_scores)
                         
        if total_value == 0:
            return {"score": 0, "warnings": ["Brak aktywów w portfelu"]}
            
        # Oblicz ważoną średnią ryzyka
        weighted_risk = sum(
            sum(asset.get("value", 0) for asset in assets.values()) * risk_scores[asset_type] / total_value
            for asset_type, assets in portfolio_data.items()
            if asset_type in risk_scores
        )
        
        warnings = []
        if weighted_risk > 0.7:
            warnings.append("Wysoki poziom ryzyka zmienności w portfelu")
            
        return {
            "score": weighted_risk,
            "warnings": warnings
        }
        
    def _analyze_correlation_risk(self, portfolio_data: Dict) -> Dict:
        """Analizuje ryzyko korelacji między aktywami"""
        # Uproszczona analiza korelacji - można rozszerzyć o rzeczywiste dane historyczne
        correlations = {
            ("stocks", "crypto"): 0.3,  # Umiarkowana korelacja
            ("stocks", "cash"): -0.1,   # Lekka ujemna korelacja
            ("crypto", "cash"): -0.2    # Ujemna korelacja
        }
        
        warnings = []
        high_correlation_pairs = []
        
        for (asset1, asset2), corr in correlations.items():
            if abs(corr) > 0.7:
                high_correlation_pairs.append({
                    "pair": (asset1, asset2),
                    "correlation": corr
                })
                warnings.append(f"Wysoka korelacja między {asset1} i {asset2}")
                
        return {
            "score": len(high_correlation_pairs) * 0.2,  # Każda wysoka korelacja zwiększa ryzyko o 20%
            "high_correlations": high_correlation_pairs,
            "warnings": warnings
        }
        
    def _get_advisor_insights(self, portfolio_data: Dict) -> Dict:
        """Pobiera analizy od wszystkich doradców"""
        insights = {}
        for advisor in self.advisor_memory.memory["advisors"]:
            insights[advisor] = self.advisor_memory.analyze_portfolio_fit(portfolio_data, advisor)
        return insights
        
    def _generate_recommendations(self, portfolio_data: Dict) -> List[Dict]:
        """Generuje rekomendacje na podstawie wszystkich analiz"""
        recommendations = []
        
        # Zbierz wszystkie ostrzeżenia i analizy
        all_warnings = []
        for advisor, insight in self._get_advisor_insights(portfolio_data).items():
            all_warnings.extend([(warning, advisor) for warning in insight.get("recommendations", [])])
            
        # Dodaj ostrzeżenia z analizy ryzyka
        risk_analysis = self._analyze_risk(portfolio_data)
        for risk_type, analysis in risk_analysis.items():
            if isinstance(analysis, dict) and "warnings" in analysis:
                all_warnings.extend([(warning, "Risk Analysis") for warning in analysis["warnings"]])
                
        # Grupuj podobne ostrzeżenia
        grouped_warnings = {}
        for warning, source in all_warnings:
            if warning not in grouped_warnings:
                grouped_warnings[warning] = []
            grouped_warnings[warning].append(source)
            
        # Generuj rekomendacje
        for warning, sources in grouped_warnings.items():
            recommendations.append({
                "recommendation": warning,
                "sources": sources,
                "priority": "high" if len(sources) > 1 else "medium"
            })
            
        # Sortuj według priorytetu
        return sorted(recommendations, key=lambda x: len(x["sources"]), reverse=True)
        
    def _calculate_metrics(self, portfolio_data: Dict) -> Dict:
        """Oblicza kluczowe wskaźniki portfela"""
        metrics = {
            "diversification_score": 0,
            "risk_adjusted_return": 0,
            "dividend_yield": 0,
            "asset_allocation": {}
        }
        
        total_value = sum(sum(asset.get("value", 0) for asset in assets.values())
                         for asset_type, assets in portfolio_data.items()
                         if asset_type in ["stocks", "crypto", "cash"])
                         
        if total_value > 0:
            # Oblicz alokację aktywów
            for asset_type in ["stocks", "crypto", "cash"]:
                asset_sum = sum(asset.get("value", 0) for asset in portfolio_data.get(asset_type, {}).values())
                metrics["asset_allocation"][asset_type] = asset_sum / total_value
                
            # Oblicz średnią dywidendę dla akcji
            if portfolio_data.get("stocks"):
                total_dividend_yield = sum(
                    stock.get("dywidenda_roczna", 0) * stock.get("value", 0)
                    for stock in portfolio_data["stocks"].values()
                )
                total_stock_value = sum(stock.get("value", 0) for stock in portfolio_data["stocks"].values())
                if total_stock_value > 0:
                    metrics["dividend_yield"] = total_dividend_yield / total_stock_value
                    
            # Oblicz score dywersyfikacji
            asset_count = sum(1 for asset_type in ["stocks", "crypto", "cash"] if portfolio_data.get(asset_type))
            stock_count = len(portfolio_data.get("stocks", {}))
            metrics["diversification_score"] = min((asset_count / 3 + stock_count / 20) / 2, 1)
            
        return metrics