import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

class AdvisorMemory:
    def __init__(self, memory_file: str = 'advisor_memory.json'):
        self.memory_file = memory_file
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict:
        """Ładuje pamięć konsultantów z pliku JSON"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Błąd ładowania pamięci: {e}")
                return self._initialize_memory()
        return self._initialize_memory()
        
    def _initialize_memory(self) -> Dict:
        """Inicjalizuje nową strukturę pamięci"""
        return {
            "advisors": {
                "Warren Buffett": {
                    "specialization": "value_investing",
                    "recommendations": [],
                    "performance_tracking": {},
                    "key_principles": [
                        "Margin of Safety",
                        "Long-term Perspective",
                        "Quality over Price",
                        "Circle of Competence"
                    ],
                    "preferred_metrics": [
                        "P/E Ratio",
                        "P/B Ratio",
                        "Debt/Equity",
                        "ROE",
                        "Dividend History"
                    ]
                },
                "Changpeng Zhao (CZ)": {
                    "specialization": "crypto_innovation",
                    "recommendations": [],
                    "performance_tracking": {},
                    "key_principles": [
                        "Technology First",
                        "Network Effects",
                        "Rapid Adaptation",
                        "Global Perspective"
                    ],
                    "preferred_metrics": [
                        "Network Growth",
                        "Technology Adoption",
                        "Market Dominance",
                        "Innovation Rate"
                    ]
                },
                "Ray Dalio": {
                    "specialization": "asset_allocation",
                    "recommendations": [],
                    "performance_tracking": {},
                    "key_principles": [
                        "Risk Parity",
                        "Economic Machine",
                        "All Weather Strategy",
                        "Correlation Analysis"
                    ],
                    "preferred_metrics": [
                        "Asset Correlation",
                        "Economic Cycles",
                        "Risk Adjusted Returns",
                        "Volatility"
                    ]
                }
            },
            "consensus_tracking": [],
            "market_conditions": {},
            "last_update": datetime.now().isoformat()
        }
        
    def save_memory(self):
        """Zapisuje pamięć do pliku"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
            
    def add_recommendation(self, advisor: str, recommendation: Dict):
        """Dodaje nową rekomendację od doradcy"""
        if advisor not in self.memory["advisors"]:
            raise ValueError(f"Nieznany doradca: {advisor}")
            
        recommendation["timestamp"] = datetime.now().isoformat()
        recommendation["status"] = "active"  # active, completed, failed
        self.memory["advisors"][advisor]["recommendations"].append(recommendation)
        self.save_memory()
        
    def track_recommendation_performance(self, advisor: str, rec_id: str, performance_data: Dict):
        """Śledzi wyniki rekomendacji"""
        for rec in self.memory["advisors"][advisor]["recommendations"]:
            if rec.get("id") == rec_id:
                if "performance_history" not in rec:
                    rec["performance_history"] = []
                rec["performance_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    **performance_data
                })
                self.save_memory()
                break
                
    def get_advisor_effectiveness(self, advisor: str) -> Dict:
        """Oblicza skuteczność rekomendacji doradcy"""
        if advisor not in self.memory["advisors"]:
            raise ValueError(f"Nieznany doradca: {advisor}")
            
        recommendations = self.memory["advisors"][advisor]["recommendations"]
        if not recommendations:
            return {"success_rate": 0, "total_recommendations": 0}
            
        successful = sum(1 for rec in recommendations 
                        if rec.get("status") == "completed" and 
                        rec.get("performance_history", []) and 
                        rec["performance_history"][-1].get("success", False))
                        
        return {
            "success_rate": successful / len(recommendations) if recommendations else 0,
            "total_recommendations": len(recommendations)
        }
        
    def analyze_portfolio_fit(self, portfolio_data: Dict, advisor: str) -> Dict:
        """Analizuje jak dobrze portfel pasuje do strategii danego doradcy"""
        if advisor not in self.memory["advisors"]:
            raise ValueError(f"Nieznany doradca: {advisor}")
            
        advisor_data = self.memory["advisors"][advisor]
        analysis = {
            "advisor": advisor,
            "specialization": advisor_data["specialization"],
            "alignment_score": 0,
            "recommendations": []
        }
        
        # Implementacja różnych strategii analizy dla różnych doradców
        if advisor == "Warren Buffett":
            analysis = self._analyze_buffett_strategy(portfolio_data, analysis)
        elif advisor == "Changpeng Zhao (CZ)":
            analysis = self._analyze_cz_strategy(portfolio_data, analysis)
        elif advisor == "Ray Dalio":
            analysis = self._analyze_dalio_strategy(portfolio_data, analysis)
            
        return analysis
        
    def _analyze_buffett_strategy(self, portfolio_data: Dict, analysis: Dict) -> Dict:
        """Analiza portfela według strategii Warrena Buffetta"""
        score = 0
        recommendations = []
        
        for ticker, data in portfolio_data.get("stocks", {}).items():
            # Analiza fundamentalna
            pe_ratio = data.get("PE", float('inf'))
            pb_ratio = data.get("priceToBook", float('inf'))
            dividend_yield = data.get("dywidenda_roczna", 0)
            
            # Scoring
            if pe_ratio < 15:
                score += 1
            if pb_ratio < 3:
                score += 1
            if dividend_yield > 0.02:  # 2% yield
                score += 1
                
            # Rekomendacje
            if pe_ratio > 25:
                recommendations.append(f"Wysokie P/E ({pe_ratio:.1f}) dla {ticker} - rozważ redukcję pozycji")
            if dividend_yield < 0.02 and data.get("kapitalizacja", 0) > 1e9:
                recommendations.append(f"Niska dywidenda dla dużej spółki {ticker} - przeanalizuj politykę dywidendową")
                
        analysis["alignment_score"] = min(score / (len(portfolio_data.get("stocks", {})) * 3), 1)
        analysis["recommendations"] = recommendations
        return analysis
        
    def _analyze_cz_strategy(self, portfolio_data: Dict, analysis: Dict) -> Dict:
        """Analiza portfela według strategii CZ"""
        score = 0
        recommendations = []
        
        crypto_allocation = sum(asset.get("value", 0) for asset in portfolio_data.get("crypto", {}).values())
        total_portfolio = portfolio_data.get("total_value", 1)
        crypto_percentage = crypto_allocation / total_portfolio if total_portfolio > 0 else 0
        
        # Scoring
        if 0.05 <= crypto_percentage <= 0.30:
            score += 2
        
        # Analiza dywersyfikacji krypto
        crypto_count = len(portfolio_data.get("crypto", {}))
        if crypto_count < 3:
            recommendations.append("Zbyt mała dywersyfikacja w krypto - rozważ dodanie więcej aktywów")
        elif crypto_count > 20:
            recommendations.append("Zbyt duża dywersyfikacja w krypto - rozważ konsolidację pozycji")
            
        analysis["alignment_score"] = min(score / 2, 1)
        analysis["recommendations"] = recommendations
        return analysis
        
    def _analyze_dalio_strategy(self, portfolio_data: Dict, analysis: Dict) -> Dict:
        """Analiza portfela według strategii Ray'a Dalio"""
        score = 0
        recommendations = []
        
        # Analiza alokacji aktywów
        asset_classes = {
            "stocks": sum(asset.get("value", 0) for asset in portfolio_data.get("stocks", {}).values()),
            "crypto": sum(asset.get("value", 0) for asset in portfolio_data.get("crypto", {}).values()),
            "cash": portfolio_data.get("cash", 0)
        }
        
        total = sum(asset_classes.values())
        if total > 0:
            ratios = {k: v/total for k, v in asset_classes.items()}
            
            # Scoring według zasady dywersyfikacji
            if 0.3 <= ratios["stocks"] <= 0.6:
                score += 1
            if 0.05 <= ratios["crypto"] <= 0.15:
                score += 1
            if 0.1 <= ratios["cash"] <= 0.3:
                score += 1
                
            # Rekomendacje
            if ratios["stocks"] > 0.6:
                recommendations.append("Zbyt duża ekspozycja na akcje - rozważ dywersyfikację")
            if ratios["crypto"] > 0.15:
                recommendations.append("Zbyt duża ekspozycja na krypto - rozważ redukcję ryzyka")
            if ratios["cash"] < 0.1:
                recommendations.append("Zbyt niski poziom gotówki - rozważ zwiększenie bufora")
                
        analysis["alignment_score"] = min(score / 3, 1)
        analysis["recommendations"] = recommendations
        return analysis
        
    def generate_monthly_report(self) -> Dict:
        """Generuje miesięczny raport z rekomendacjami wszystkich doradców"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "advisor_reports": {},
            "consensus": {
                "overall_portfolio_health": 0,
                "key_recommendations": [],
                "risk_factors": []
            }
        }
        
        # Zbierz raporty od wszystkich doradców
        for advisor in self.memory["advisors"]:
            effectiveness = self.get_advisor_effectiveness(advisor)
            report["advisor_reports"][advisor] = {
                "effectiveness": effectiveness,
                "recent_recommendations": self._get_recent_recommendations(advisor),
                "key_concerns": self._get_key_concerns(advisor)
            }
            
        # Generuj konsensus
        report["consensus"] = self._generate_consensus(report["advisor_reports"])
        
        return report
        
    def _get_recent_recommendations(self, advisor: str, limit: int = 5) -> List:
        """Pobiera ostatnie rekomendacje doradcy"""
        recommendations = self.memory["advisors"][advisor]["recommendations"]
        return sorted(recommendations, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
    def _get_key_concerns(self, advisor: str) -> List:
        """Identyfikuje główne obawy doradcy"""
        concerns = []
        recent_recs = self._get_recent_recommendations(advisor)
        
        # Analizuj wzorce w rekomendacjach
        for rec in recent_recs:
            if rec.get("priority", "normal") == "high" or rec.get("risk_level", "low") == "high":
                concerns.append({
                    "topic": rec.get("topic", "Unknown"),
                    "risk_level": rec.get("risk_level", "medium"),
                    "timestamp": rec["timestamp"]
                })
                
        return concerns
        
    def _generate_consensus(self, advisor_reports: Dict) -> Dict:
        """Generuje konsensus na podstawie raportów doradców"""
        consensus = {
            "overall_portfolio_health": 0,
            "key_recommendations": [],
            "risk_factors": []
        }
        
        # Oblicz ogólną ocenę portfela
        health_scores = []
        all_recommendations = []
        all_risks = []
        
        for advisor, report in advisor_reports.items():
            # Uwzględnij skuteczność doradcy w wadze jego oceny
            effectiveness = report["effectiveness"]["success_rate"]
            health_scores.append(effectiveness)
            
            # Zbierz rekomendacje
            for rec in report["recent_recommendations"]:
                if rec.get("priority", "normal") == "high":
                    all_recommendations.append(rec)
                    
            # Zbierz czynniki ryzyka
            all_risks.extend(report["key_concerns"])
            
        # Oblicz średnią ważoną ocenę
        consensus["overall_portfolio_health"] = sum(health_scores) / len(health_scores) if health_scores else 0
        
        # Wybierz najważniejsze rekomendacje
        consensus["key_recommendations"] = sorted(
            all_recommendations,
            key=lambda x: x.get("priority_score", 0),
            reverse=True
        )[:3]
        
        # Zidentyfikuj główne czynniki ryzyka
        risk_count = {}
        for risk in all_risks:
            topic = risk["topic"]
            risk_count[topic] = risk_count.get(topic, 0) + 1
            
        consensus["risk_factors"] = [
            {"topic": topic, "mentions": count}
            for topic, count in sorted(risk_count.items(), key=lambda x: x[1], reverse=True)
        ][:3]
        
        return consensus