"""
API Usage Tracker - Monitorowanie wykorzystania limitów API
Zapewnia, że autonomiczne rozmowy używają max 60% dziennego limitu
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

# Ścieżki plików
USAGE_FILE = "api_usage.json"
CONFIG_FILE = "api_limits_config.json"

# Domyślne limity API (możesz edytować w api_limits_config.json)
DEFAULT_LIMITS = {
    "claude": {
        "daily_limit": 50,  # Szacunkowe wywołania dziennie
        "autonomous_percentage": 60,  # Ile % dostępne dla autonomicznych rozmów
        "cost_per_call": 0.01  # USD (szacunkowe)
    },
    "gemini": {
        "daily_limit": 50,
        "autonomous_percentage": 60,
        "cost_per_call": 0.005
    },
    "openai": {
        "daily_limit": 50,
        "autonomous_percentage": 60,
        "cost_per_call": 0.02
    }
}


class APIUsageTracker:
    """Śledzi wykorzystanie API i egzekwuje limity"""
    
    def __init__(self):
        self.config = self._load_config()
        self.usage = self._load_usage()
        self._check_daily_reset()
    
    def _load_config(self) -> Dict:
        """Załaduj konfigurację limitów"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Stwórz domyślną konfigurację
            self._save_config(DEFAULT_LIMITS)
            return DEFAULT_LIMITS
    
    def _save_config(self, config: Dict):
        """Zapisz konfigurację"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _load_usage(self) -> Dict:
        """Załaduj dzisiejsze wykorzystanie"""
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._create_empty_usage()
    
    def _create_empty_usage(self) -> Dict:
        """Stwórz pustą strukturę usage"""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "usage": {
                "claude": {"user": 0, "autonomous": 0, "total": 0},
                "gemini": {"user": 0, "autonomous": 0, "total": 0},
                "openai": {"user": 0, "autonomous": 0, "total": 0}
            },
            "autonomous_conversations_today": 0,
            "total_cost_usd": 0.0
        }
    
    def _save_usage(self):
        """Zapisz aktualne wykorzystanie"""
        with open(USAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.usage, f, indent=2, ensure_ascii=False)
    
    def _check_daily_reset(self):
        """Sprawdź czy nowy dzień - jeśli tak, zresetuj"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.usage.get("date") != today:
            # Archiwizuj wczorajsze dane
            self._archive_yesterday()
            # Reset na nowy dzień
            self.usage = self._create_empty_usage()
            self._save_usage()
            print(f"📊 API Usage: Nowy dzień - limity zresetowane ({today})")
    
    def _archive_yesterday(self):
        """Zapisz wczorajsze dane do historii"""
        archive_file = "api_usage_history.json"
        history = []
        
        if os.path.exists(archive_file):
            with open(archive_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append(self.usage)
        
        # Zachowaj ostatnie 30 dni
        if len(history) > 30:
            history = history[-30:]
        
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def track_call(self, api_name: str, is_autonomous: bool = False) -> bool:
        """
        Zarejestruj wywołanie API
        
        Args:
            api_name: "claude", "gemini", lub "openai"
            is_autonomous: True jeśli to autonomiczna rozmowa, False jeśli user
        
        Returns:
            bool: True jeśli wywołanie dozwolone, False jeśli przekroczono limit
        """
        if api_name not in self.config:
            print(f"⚠️ Nieznane API: {api_name}")
            return True  # Nie blokuj nieznanych API
        
        # Sprawdź czy można wykonać wywołanie
        if is_autonomous and not self.can_make_autonomous_call(api_name):
            print(f"🚫 Limit autonomiczny przekroczony dla {api_name}")
            return False
        
        # Zarejestruj wywołanie
        if is_autonomous:
            self.usage["usage"][api_name]["autonomous"] += 1
        else:
            self.usage["usage"][api_name]["user"] += 1
        
        self.usage["usage"][api_name]["total"] += 1
        
        # Aktualizuj koszt
        cost = self.config[api_name]["cost_per_call"]
        self.usage["total_cost_usd"] += cost
        
        self._save_usage()
        return True
    
    def can_make_autonomous_call(self, api_name: str) -> bool:
        """Sprawdź czy można wykonać autonomiczne wywołanie"""
        if api_name not in self.config:
            return True
        
        config = self.config[api_name]
        current_autonomous = self.usage["usage"][api_name]["autonomous"]
        
        # Oblicz maksymalny limit autonomiczny
        max_autonomous = int(config["daily_limit"] * config["autonomous_percentage"] / 100)
        
        return current_autonomous < max_autonomous
    
    def get_remaining_budget(self, api_name: str) -> Dict:
        """Zwróć pozostały budżet dla API"""
        if api_name not in self.config:
            return {"error": "Unknown API"}
        
        config = self.config[api_name]
        usage = self.usage["usage"][api_name]
        
        max_autonomous = int(config["daily_limit"] * config["autonomous_percentage"] / 100)
        max_user = config["daily_limit"] - max_autonomous
        
        return {
            "api": api_name,
            "date": self.usage["date"],
            "autonomous": {
                "used": usage["autonomous"],
                "limit": max_autonomous,
                "remaining": max_autonomous - usage["autonomous"],
                "percentage_used": round(usage["autonomous"] / max_autonomous * 100, 1) if max_autonomous > 0 else 0
            },
            "user": {
                "used": usage["user"],
                "limit": max_user,
                "remaining": max_user - usage["user"],
                "percentage_used": round(usage["user"] / max_user * 100, 1) if max_user > 0 else 0
            },
            "total": {
                "used": usage["total"],
                "limit": config["daily_limit"],
                "remaining": config["daily_limit"] - usage["total"],
                "percentage_used": round(usage["total"] / config["daily_limit"] * 100, 1)
            }
        }
    
    def get_all_budgets(self) -> Dict:
        """Zwróć budżety dla wszystkich API"""
        return {
            api_name: self.get_remaining_budget(api_name)
            for api_name in self.config.keys()
        }
    
    def increment_autonomous_conversation(self):
        """Zwiększ licznik autonomicznych rozmów"""
        self.usage["autonomous_conversations_today"] += 1
        self._save_usage()
    
    def get_today_summary(self) -> Dict:
        """Zwróć podsumowanie dzisiejszego dnia"""
        total_calls = sum(api["total"] for api in self.usage["usage"].values())
        autonomous_calls = sum(api["autonomous"] for api in self.usage["usage"].values())
        user_calls = sum(api["user"] for api in self.usage["usage"].values())
        
        return {
            "date": self.usage["date"],
            "total_calls": total_calls,
            "user_calls": user_calls,
            "autonomous_calls": autonomous_calls,
            "autonomous_conversations": self.usage["autonomous_conversations_today"],
            "total_cost_usd": round(self.usage["total_cost_usd"], 2),
            "by_api": self.usage["usage"]
        }
    
    def print_status(self):
        """Wydrukuj status limitów (debug)"""
        print("\n" + "="*60)
        print(f"📊 API USAGE STATUS - {self.usage['date']}")
        print("="*60)
        
        for api_name in self.config.keys():
            budget = self.get_remaining_budget(api_name)
            print(f"\n🔹 {api_name.upper()}")
            print(f"   Autonomous: {budget['autonomous']['used']}/{budget['autonomous']['limit']} "
                  f"({budget['autonomous']['percentage_used']}%)")
            print(f"   User: {budget['user']['used']}/{budget['user']['limit']} "
                  f"({budget['user']['percentage_used']}%)")
            print(f"   Total: {budget['total']['used']}/{budget['total']['limit']} "
                  f"({budget['total']['percentage_used']}%)")
        
        summary = self.get_today_summary()
        print(f"\n💰 Total Cost Today: ${summary['total_cost_usd']}")
        print(f"🤖 Autonomous Conversations: {summary['autonomous_conversations']}")
        print("="*60 + "\n")


# Singleton instance
_tracker_instance = None

def get_tracker() -> APIUsageTracker:
    """Zwróć singleton instance trackera"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = APIUsageTracker()
    return _tracker_instance


if __name__ == "__main__":
    # Test
    tracker = get_tracker()
    tracker.print_status()
    
    # Symulacja użycia
    print("\n🧪 Test: Symulacja 5 wywołań autonomous Claude...")
    for i in range(5):
        success = tracker.track_call("claude", is_autonomous=True)
        print(f"   Call {i+1}: {'✅ Success' if success else '🚫 Blocked'}")
    
    print("\n🧪 Test: Symulacja 3 wywołań user Gemini...")
    for i in range(3):
        success = tracker.track_call("gemini", is_autonomous=False)
        print(f"   Call {i+1}: {'✅ Success' if success else '🚫 Blocked'}")
    
    tracker.print_status()
