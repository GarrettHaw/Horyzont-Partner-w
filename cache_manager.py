import json
import os
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.default_duration = timedelta(hours=1)
        # Różne czasy odświeżania dla różnych typów danych
        self.cache_durations = {
            'market_data': timedelta(hours=1),     # Dane rynkowe - co godzinę
            'dividend_data': timedelta(days=1),    # Dane o dywidendach - co 24h
            'history_data': timedelta(days=7),     # Dane historyczne - co tydzień
            'price_data': timedelta(minutes=15),   # Ceny - co 15 minut
        }
        self.cache = self._load_cache()
        
    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    
                # Migracja starego formatu cache'u
                if "last_update" in cache_data:
                    # Konwertuj stary format na nowy
                    old_data = cache_data["data"]
                    old_timestamp = cache_data.get("last_update")
                    cache_data = {
                        "timestamps": {},
                        "data": old_data
                    }
                    if old_timestamp:
                        cache_data["timestamps"]["market_data"] = old_timestamp
                
                # Upewnij się, że mamy wymagane klucze
                if "timestamps" not in cache_data:
                    cache_data["timestamps"] = {}
                if "data" not in cache_data:
                    cache_data["data"] = {}
                    
                # Konwersja timestampów na obiekty datetime
                cache_data["timestamps"] = {
                    k: datetime.fromisoformat(v) if v else None
                    for k, v in cache_data["timestamps"].items()
                }
                
                return cache_data
            except Exception as e:
                print(f"⚠️ Błąd ładowania cache'u: {str(e)}")
                return {"timestamps": {}, "data": {}}
        return {"timestamps": {}, "data": {}}

    def _save_cache(self):
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
            
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, default=datetime_handler)

    def is_cache_valid(self, key):
        """Sprawdza czy cache dla danego klucza jest aktualny"""
        try:
            # Sprawdź czy mamy timestamps w cache
            if "timestamps" not in self.cache:
                self.cache["timestamps"] = {}
                return False
                
            if key not in self.cache["timestamps"]:
                return False
                
            last_update = self.cache["timestamps"].get(key)
            if not last_update:
                return False
        except Exception as e:
            print(f"⚠️ Błąd sprawdzania ważności cache'u: {str(e)}")
            return False
            
        # Określ czas ważności cache'u na podstawie typu danych
        for data_type, duration in self.cache_durations.items():
            if data_type in key:
                cache_duration = duration
                break
        else:
            cache_duration = self.default_duration
            
        return datetime.now() - last_update < cache_duration

    def get_data(self, key, ignore_cache=False):
        """
        Pobiera dane z cache'u jeśli są aktualne
        ignore_cache=True wymusza pobranie świeżych danych
        """
        if not ignore_cache and self.is_cache_valid(key):
            cache_age = datetime.now() - self.cache["timestamps"][key]
            print(f"📥 Używam cache'u dla {key} (wiek: {cache_age.total_seconds()/60:.1f}min)")
            return self.cache["data"].get(key)
        return None

    def set_data(self, key, data):
        """Zapisuje dane do cache'u"""
        self.cache["timestamps"][key] = datetime.now()
        self.cache["data"][key] = data
        self._save_cache()
        
        # Określ typ danych na podstawie klucza
        data_type = next((t for t in self.cache_durations.keys() if t in key), "other")
        duration = self.cache_durations.get(data_type, self.default_duration)
        print(f"💾 Zapisano do cache'u: {key} (odświeżanie co {duration})")

    def clear(self, key=None):
        """
        Czyści cache.
        Jeśli podano key, czyści tylko ten konkretny klucz.
        """
        try:
            # Upewnij się, że mamy prawidłową strukturę cache'u
            if "timestamps" not in self.cache:
                self.cache["timestamps"] = {}
            if "data" not in self.cache:
                self.cache["data"] = {}
                
            if key:
                if key in self.cache["data"]:
                    del self.cache["data"][key]
                if key in self.cache["timestamps"]:
                    del self.cache["timestamps"][key]
                print(f"🧹 Wyczyszczono cache dla: {key}")
            else:
                self.cache = {"timestamps": {}, "data": {}}
                print("🧹 Wyczyszczono cały cache")
            
            self._save_cache()
        except Exception as e:
            print(f"⚠️ Błąd podczas czyszczenia cache'u: {str(e)}")
            # Zresetuj cache do domyślnego stanu
            self.cache = {"timestamps": {}, "data": {}}
            self._save_cache()

    def get_cache_info(self):
        """Zwraca informacje o stanie cache'u"""
        info = {"status": {}}
        for key in self.cache["data"].keys():
            last_update = self.cache["timestamps"].get(key)
            if last_update:
                age = datetime.now() - last_update
                is_valid = self.is_cache_valid(key)
                info["status"][key] = {
                    "last_update": last_update.isoformat(),
                    "age": str(age),
                    "is_valid": is_valid
                }
        return info