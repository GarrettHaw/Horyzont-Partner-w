"""
🪙 CRYPTO PORTFOLIO MANAGER
System zarządzania portfelem kryptowalut z API CoinGecko (darmowe!)

Features:
- Real-time prices dla Top 100 crypto (+ custom)
- Metadata: full name, symbol, market_cap, rank
- Historical data (7d, 30d, 90d, 1y)
- Dominance tracking (BTC, ETH)
- Fear & Greed Index
- Cache system (5 min refresh dla cen, 1h dla metadata)

API: CoinGecko Free Tier
- 10-30 calls/min limit
- No API key required
- 250 cryptocurrencies
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Cache files
CRYPTO_PRICES_CACHE = "crypto_prices_cache.json"
CRYPTO_METADATA_CACHE = "crypto_metadata_cache.json"
CRYPTO_HISTORICAL_CACHE = "crypto_historical_cache.json"

# CoinGecko API
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# Rate limiting
LAST_API_CALL = 0
MIN_CALL_INTERVAL = 2  # 2 seconds between calls (safe for free tier)


class CryptoPortfolioManager:
    """Manager portfela kryptowalut z CoinGecko API"""
    
    def __init__(self):
        self.prices_cache = self._load_cache(CRYPTO_PRICES_CACHE)
        self.metadata_cache = self._load_cache(CRYPTO_METADATA_CACHE)
        self.historical_cache = self._load_cache(CRYPTO_HISTORICAL_CACHE)
    
    def _load_cache(self, filename: str) -> dict:
        """Wczytaj cache z pliku"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self, filename: str, data: dict):
        """Zapisz cache do pliku"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Błąd zapisu cache {filename}: {e}")
    
    def _rate_limit(self):
        """Rate limiting dla API calls"""
        global LAST_API_CALL
        elapsed = time.time() - LAST_API_CALL
        if elapsed < MIN_CALL_INTERVAL:
            time.sleep(MIN_CALL_INTERVAL - elapsed)
        LAST_API_CALL = time.time()
    
    def _api_call(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """Wykonaj API call z rate limiting i error handling"""
        self._rate_limit()
        
        try:
            url = f"{COINGECKO_BASE}/{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("⚠️ Rate limit exceeded - czekam 60s")
                time.sleep(60)
                return self._api_call(endpoint, params)  # Retry
            else:
                print(f"⚠️ API error {response.status_code}: {response.text}")
                return None
        
        except Exception as e:
            print(f"⚠️ Błąd API call: {e}")
            return None
    
    def get_coin_id_from_symbol(self, symbol: str) -> Optional[str]:
        """
        Konwertuj symbol (BTC, ETH) na coin_id (bitcoin, ethereum)
        Używa cache metadata
        """
        symbol = symbol.upper()
        
        # Sprawdź cache (pomiń specjalne klucze jak '_last_update')
        for coin_id, data in self.metadata_cache.items():
            if coin_id.startswith('_'):  # Pomiń metadata keys
                continue
            if isinstance(data, dict) and data.get('symbol', '').upper() == symbol:
                return coin_id
        
        # Jeśli nie ma w cache, pobierz listę (tylko raz)
        if not self.metadata_cache or self._is_cache_old(self.metadata_cache.get('_last_update'), hours=24):
            self._refresh_coins_list()
            
            # Spróbuj ponownie
            for coin_id, data in self.metadata_cache.items():
                if coin_id.startswith('_'):  # Pomiń metadata keys
                    continue
                if isinstance(data, dict) and data.get('symbol', '').upper() == symbol:
                    return coin_id
        
        # Fallback: common mappings
        common_mappings = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'XRP': 'ripple',
            'USDC': 'usd-coin',
            'ADA': 'cardano',
            'DOGE': 'dogecoin',
            'TRX': 'tron',
            'TON': 'the-open-network',
            'LINK': 'chainlink',
            'MATIC': 'matic-network',
            'DOT': 'polkadot',
            'DAI': 'dai',
            'SHIB': 'shiba-inu',
            'UNI': 'uniswap',
            'AVAX': 'avalanche-2',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'XLM': 'stellar',
            'ATOM': 'cosmos',
            'FIL': 'filecoin',
            'APT': 'aptos',
            'ARB': 'arbitrum',
            'OP': 'optimism',
            'INJ': 'injective-protocol',
            'SUI': 'sui',
            'HBAR': 'hedera-hashgraph',
            'IMX': 'immutable-x',
            'MKR': 'maker',
            'AAVE': 'aave',
            'GRT': 'the-graph',
            'RUNE': 'thorchain',
            'FTM': 'fantom',
            'ALGO': 'algorand',
            'NEAR': 'near',
            'VET': 'vechain',
            'SAND': 'the-sandbox',
            'MANA': 'decentraland',
            'AXS': 'axie-infinity',
            'ETC': 'ethereum-classic',
            'XTZ': 'tezos',
            'FLOW': 'flow',
            'ICP': 'internet-computer',
            'THETA': 'theta-token',
            'EOS': 'eos',
            'KAVA': 'kava',
            'XMR': 'monero',
            'CHZ': 'chiliz',
            'GALA': 'gala',
            'ZEC': 'zcash',
            'DASH': 'dash',
            'COMP': 'compound-governance-token',
            'CRV': 'curve-dao-token',
            'SNX': 'synthetix-network-token',
            'YFI': 'yearn-finance',
            'BAT': 'basic-attention-token',
            'ENJ': 'enjincoin',
            'LDO': 'lido-dao',
            '1INCH': '1inch',
            'SUSHI': 'sushi',
            'CAKE': 'pancakeswap-token'
        }
        
        return common_mappings.get(symbol)
    
    def _refresh_coins_list(self):
        """Odśwież listę wszystkich coinów (Top 250)"""
        print("🔄 Pobieram listę kryptowalut z CoinGecko...")
        
        # Pobierz Top 250 (free tier limit)
        data = self._api_call("coins/markets", {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 250,
            'page': 1,
            'sparkline': False
        })
        
        if data:
            metadata = {}
            for coin in data:
                coin_id = coin.get('id')
                metadata[coin_id] = {
                    'name': coin.get('name'),
                    'symbol': coin.get('symbol', '').upper(),
                    'market_cap_rank': coin.get('market_cap_rank'),
                    'image': coin.get('image'),
                    'market_cap': coin.get('market_cap'),
                    'total_volume': coin.get('total_volume'),
                    'circulating_supply': coin.get('circulating_supply'),
                    'total_supply': coin.get('total_supply'),
                    'max_supply': coin.get('max_supply')
                }
            
            metadata['_last_update'] = datetime.now().isoformat()
            self.metadata_cache = metadata
            self._save_cache(CRYPTO_METADATA_CACHE, metadata)
            
            print(f"✅ Pobrano {len(metadata)-1} kryptowalut")
        else:
            print("❌ Nie udało się pobrać listy coinów")
    
    def _is_cache_old(self, timestamp: str, minutes: int = 5, hours: int = 0) -> bool:
        """Sprawdź czy cache jest stary"""
        if not timestamp:
            return True
        
        try:
            cache_time = datetime.fromisoformat(timestamp)
            age = datetime.now() - cache_time
            threshold = timedelta(minutes=minutes, hours=hours)
            return age > threshold
        except:
            return True
    
    def _get_price_from_alternative_api(self, symbol: str) -> Optional[dict]:
        """
        Pobierz cenę z alternatywnych API dla tokenów niedostępnych w CoinGecko.
        Obsługuje: MX (MEXC), GUSD (Gemini Dollar)
        """
        symbol = symbol.upper()
        
        # MX Token - MEXC API (darmowe, bez klucza)
        if symbol == 'MX':
            try:
                response = requests.get(
                    'https://api.mexc.com/api/v3/ticker/price',
                    params={'symbol': 'MXUSDT'},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    price = float(data.get('price', 0))
                    if price > 0:
                        return {
                            'price_usd': price,
                            'price_pln': price * 3.65,  # Przybliżony PLN
                            'change_24h': 0,  # MEXC API nie daje 24h change w tym endpoint
                            'volume_24h': 0,
                            'market_cap': 0,
                            'full_name': 'MX Token',
                            'rank': 999,
                            'last_updated': datetime.now().isoformat(),
                            'coin_id': 'mx-token',
                            'source': 'MEXC API'
                        }
            except Exception as e:
                print(f"⚠️ Błąd MEXC API dla MX: {e}")
        
        # GUSD - Gate.io API (alternatywa)
        elif symbol == 'GUSD':
            try:
                response = requests.get(
                    'https://api.gateio.ws/api/v4/spot/tickers',
                    params={'currency_pair': 'GUSD_USDT'},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        price = float(data[0].get('last', 1.0))
                        change_24h = float(data[0].get('change_percentage', 0))
                        return {
                            'price_usd': price,
                            'price_pln': price * 3.65,
                            'change_24h': change_24h,
                            'volume_24h': float(data[0].get('quote_volume', 0)),
                            'market_cap': 0,
                            'full_name': 'Gemini Dollar',
                            'rank': 999,
                            'last_updated': datetime.now().isoformat(),
                            'coin_id': 'gemini-dollar',
                            'source': 'Gate.io API'
                        }
            except Exception as e:
                print(f"⚠️ Błąd Gate.io API dla GUSD: {e}")
        
        return None
    
    def get_current_prices(self, symbols: List[str], force_refresh: bool = False) -> Dict[str, dict]:
        """
        Pobierz aktualne ceny dla listy symboli
        
        Returns:
            Dict[symbol, {
                'price_usd': float,
                'price_pln': float,
                'change_24h': float,
                'volume_24h': float,
                'market_cap': float,
                'full_name': str,
                'rank': int,
                'last_updated': str
            }]
        """
        # Sprawdź cache (5 min freshness)
        if not force_refresh and not self._is_cache_old(self.prices_cache.get('_last_update'), minutes=5):
            print("✓ Używam cache cen crypto (wiek: <5 min)")
            
            results = {}
            for symbol in symbols:
                if symbol.upper() in self.prices_cache:
                    results[symbol.upper()] = self.prices_cache[symbol.upper()]
            
            if len(results) == len(symbols):
                return results
        
        print(f"🔄 Pobieram świeże ceny dla {len(symbols)} kryptowalut...")
        
        # Konwertuj symbole na coin_ids
        coin_ids = []
        symbol_to_id = {}
        
        for symbol in symbols:
            coin_id = self.get_coin_id_from_symbol(symbol)
            if coin_id:
                coin_ids.append(coin_id)
                symbol_to_id[coin_id] = symbol.upper()
            else:
                print(f"⚠️ Nie znaleziono coin_id dla {symbol}")
        
        if not coin_ids:
            return {}
        
        # Pobierz ceny (max 250 za raz)
        data = self._api_call("simple/price", {
            'ids': ','.join(coin_ids[:250]),  # Limit dla free tier
            'vs_currencies': 'usd,pln',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true',
            'include_last_updated_at': 'true'
        })
        
        if not data:
            # Jeśli API zawiedzie, użyj cache
            print("⚠️ API call failed, używam cache")
            results = {}
            for symbol in symbols:
                if symbol.upper() in self.prices_cache:
                    results[symbol.upper()] = self.prices_cache[symbol.upper()]
            return results
        
        # Przetworz wyniki
        results = {}
        
        for coin_id, prices in data.items():
            symbol = symbol_to_id.get(coin_id, '')
            if not symbol:
                continue
            
            # Pobierz metadata z cache
            metadata = self.metadata_cache.get(coin_id, {})
            
            result = {
                'price_usd': prices.get('usd', 0),
                'price_pln': prices.get('pln', 0),
                'change_24h': prices.get('usd_24h_change', 0),
                'volume_24h': prices.get('usd_24h_vol', 0),
                'market_cap': prices.get('usd_market_cap', 0),
                'full_name': metadata.get('name', symbol),
                'rank': metadata.get('market_cap_rank', 999),
                'last_updated': datetime.fromtimestamp(prices.get('last_updated_at', 0)).isoformat() if prices.get('last_updated_at') else datetime.now().isoformat(),
                'coin_id': coin_id
            }
            
            results[symbol] = result
            self.prices_cache[symbol] = result
        
        # Zapisz cache
        self.prices_cache['_last_update'] = datetime.now().isoformat()
        self._save_cache(CRYPTO_PRICES_CACHE, self.prices_cache)
        
        print(f"✅ Pobrano ceny dla {len(results)} kryptowalut")
        
        # === FALLBACK: Próbuj alternatywne API dla brakujących symboli ===
        missing_symbols = [s for s in symbols if s.upper() not in results]
        print(f"[DEBUG] Requested symbols: {symbols}")
        print(f"[DEBUG] Got results for: {list(results.keys())}")
        print(f"[DEBUG] Missing symbols: {missing_symbols}")
        
        if missing_symbols:
            print(f"🔄 Próbuję alternatywne API dla: {', '.join(missing_symbols)}")
            for symbol in missing_symbols:
                alt_data = self._get_price_from_alternative_api(symbol)
                if alt_data:
                    results[symbol.upper()] = alt_data
                    self.prices_cache[symbol.upper()] = alt_data
                    print(f"✅ Pobrano {symbol} z {alt_data.get('source', 'alternatywnego API')}")
            
            # Zapisz zaktualizowany cache
            if any(s.upper() in results for s in missing_symbols):
                self._save_cache(CRYPTO_PRICES_CACHE, self.prices_cache)
        
        return results
    
    def get_fear_greed_index(self) -> dict:
        """
        Pobierz Fear & Greed Index dla crypto
        """
        try:
            response = requests.get("https://api.alternative.me/fng/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                fng = data['data'][0]
                
                return {
                    'value': int(fng['value']),
                    'classification': fng['value_classification'],
                    'timestamp': fng['timestamp']
                }
        except:
            pass
        
        return {'value': 50, 'classification': 'Neutral', 'timestamp': ''}
    
    def calculate_portfolio_stats(self, holdings: Dict[str, float]) -> dict:
        """
        Oblicz statystyki portfela
        
        Args:
            holdings: Dict[symbol, quantity]
        
        Returns:
            Dict ze statystykami
        """
        if not holdings:
            return {}
        
        symbols = list(holdings.keys())
        prices = self.get_current_prices(symbols)
        
        total_value_usd = 0
        total_value_pln = 0
        positions = []
        
        for symbol, quantity in holdings.items():
            if symbol not in prices:
                continue
            
            price_data = prices[symbol]
            value_usd = quantity * price_data['price_usd']
            value_pln = quantity * price_data['price_pln']
            
            total_value_usd += value_usd
            total_value_pln += value_pln
            
            positions.append({
                'symbol': symbol,
                'full_name': price_data['full_name'],
                'quantity': quantity,
                'price_usd': price_data['price_usd'],
                'value_usd': value_usd,
                'value_pln': value_pln,
                'change_24h': price_data['change_24h'],
                'rank': price_data['rank'],
                'allocation_pct': 0  # Wypełnione później
            })
        
        # Oblicz alokacje
        for pos in positions:
            pos['allocation_pct'] = (pos['value_usd'] / total_value_usd * 100) if total_value_usd > 0 else 0
        
        # Sortuj po wartości
        positions.sort(key=lambda x: x['value_usd'], reverse=True)
        
        return {
            'total_value_usd': total_value_usd,
            'total_value_pln': total_value_pln,
            'positions_count': len(positions),
            'positions': positions,
            'top_10': positions[:10],
            'btc_dominance': positions[0]['allocation_pct'] if positions and positions[0]['symbol'] == 'BTC' else 0
        }


# Singleton instance
_manager = None

def get_crypto_manager() -> CryptoPortfolioManager:
    """Pobierz singleton instance managera"""
    global _manager
    if _manager is None:
        _manager = CryptoPortfolioManager()
    return _manager


# Convenience functions
def get_crypto_prices(symbols: List[str]) -> Dict[str, dict]:
    """Shortcut do pobierania cen"""
    manager = get_crypto_manager()
    return manager.get_current_prices(symbols)


def calculate_crypto_portfolio(holdings: Dict[str, float]) -> dict:
    """Shortcut do kalkulacji portfela"""
    manager = get_crypto_manager()
    return manager.calculate_portfolio_stats(holdings)


if __name__ == "__main__":
    # Test
    print("🧪 Test Crypto Portfolio Manager\n")
    
    manager = CryptoPortfolioManager()
    
    # Test 1: Symbol -> coin_id
    print("Test 1: Konwersja symboli")
    symbols = ['BTC', 'ETH', 'SOL', 'LINK', 'UNI']
    for symbol in symbols:
        coin_id = manager.get_coin_id_from_symbol(symbol)
        print(f"  {symbol} → {coin_id}")
    
    print("\nTest 2: Pobieranie cen")
    prices = manager.get_current_prices(['BTC', 'ETH', 'SOL'])
    for symbol, data in prices.items():
        print(f"  {symbol} ({data['full_name']}): ${data['price_usd']:,.2f} | Rank: #{data['rank']} | 24h: {data['change_24h']:+.2f}%")
    
    print("\nTest 3: Portfolio stats")
    holdings = {
        'BTC': 0.5,
        'ETH': 2.0,
        'SOL': 10.0
    }
    stats = manager.calculate_portfolio_stats(holdings)
    print(f"  Total: ${stats['total_value_usd']:,.2f} ({stats['total_value_pln']:,.2f} PLN)")
    print(f"  Positions: {stats['positions_count']}")
    for pos in stats['top_10']:
        print(f"    {pos['symbol']}: ${pos['value_usd']:,.2f} ({pos['allocation_pct']:.1f}%)")
    
    print("\n✅ Test zakończony!")
