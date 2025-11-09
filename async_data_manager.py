import asyncio
import aiohttp
import yfinance as yf
import pandas as pd
import ssl
from datetime import datetime, timedelta
import json
import os
import certifi
from typing import List, Dict, Any
from cache_manager import CacheManager
import random

# Konfiguracja certyfikatów SSL
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()

class AsyncDataManager:
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.min_delay = 5.0  # 5 sekund między żądaniami
        self.last_request_time = {}  # Słownik do śledzenia czasu ostatniego żądania per host
        
        # Konfiguracja SSL
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
    async def initialize(self):
        """Inicjalizacja komponentów asynchronicznych"""
        # Te obiekty muszą być tworzone w kontekście pętli zdarzeń
        self.semaphore = asyncio.Semaphore(1)  # Limit do 1 połączenia na raz
        self.connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        self.session = aiohttp.ClientSession(connector=self.connector)
        
    async def delay_request(self, host: str):
        """Wprowadza opóźnienie między żądaniami do tego samego hosta"""
        now = datetime.now()
        if host in self.last_request_time:
            elapsed = (now - self.last_request_time[host]).total_seconds()
            if elapsed < self.min_delay:
                delay = self.min_delay - elapsed + random.uniform(0.1, 0.5)  # Dodaj losowy komponent
                await asyncio.sleep(delay)
        self.last_request_time[host] = datetime.now()
        
    async def fetch_url_with_retry(self, session: aiohttp.ClientSession, url: str, max_retries: int = 3) -> Dict:
        """Asynchroniczne pobieranie danych z URL z obsługą ponawiania prób i dłuższymi opóźnieniami"""
        host = url.split('/')[2]  # Wyciągnij domenę z URL
        attempt = 0
        base_delay = 2  # Zmniejszone początkowe opóźnienie do 2 sekund
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        while attempt < max_retries:
            try:
                async with self.semaphore:
                    async with session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status in [401, 403]:  # Unauthorized / Forbidden
                            print(f"⚠️ Błąd autoryzacji dla {url}. Próbuję alternatywne źródło...")
                            return None
                        elif response.status == 429:  # Too Many Requests
                            delay = base_delay * (2 ** attempt) + random.uniform(0.1, 1.0)
                            print(f"⚠️ Błąd 429 dla {url}. Czekam {delay:.1f}s przed ponowieniem...")
                            await asyncio.sleep(delay)
                            attempt += 1
                            continue
                        else:
                            print(f"⚠️ Błąd {response.status} dla {url}")
                            return None
                            
            except Exception as e:
                print(f"⚠️ Błąd pobierania {url}: {str(e)}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0.1, 1.0)
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue
                return None
                print(f"❌ Przekroczono limit prób dla {url}")
                return None
                
        return None

    async def fetch_stock_data(self, session: aiohttp.ClientSession, ticker: str) -> Dict:
        """Pobieranie danych dla pojedynczej spółki"""
        try:
            import requests
            # Konfiguracja sesji requests
            session = requests.Session()
            session.verify = certifi.where()
            session.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Użyj yfinance z własną sesją
            ticker_obj = yf.Ticker(ticker.split('_')[0])  # Usuń suffix _US_EQ
            ticker_obj.session = session
            
            # Pobierz podstawowe informacje
            info = ticker_obj.info
            if info:
                return {
                    "ticker": ticker,
                    "data": {
                        "price": {"regularMarketPrice": info.get('regularMarketPrice', 0)},
                        "summaryDetail": {
                            "dividendYield": info.get('dividendYield', 0),
                            "marketCap": info.get('marketCap', 0),
                            "dividendRate": info.get('dividendRate', 0)
                        }
                    }
                }
        except Exception as e:
            print(f"    [yfinance] ⚠️  Pominięto ticker '{ticker}'. Powód: {str(e)}")
        return None

    async def fetch_multiple_stocks(self, tickers: List[str]) -> Dict[str, Any]:
        """Równoległe pobieranie danych dla wielu spółek z kontrolowanym opóźnieniem"""
        print(f"🔄 Rozpoczynam pobieranie danych dla {len(tickers)} spółek...")
        results = {}
        
        try:
            # Upewnij się, że mamy zainicjalizowaną sesję
            if not hasattr(self, 'session'):
                await self.initialize()
            
            start_time = datetime.now()
            
            # Pobierz dane dla każdego tickera sekwencyjnie
            for i, ticker in enumerate(tickers, 1):
                try:
                    print(f"🔄 Przetwarzam ticker {i}/{len(tickers)}...")
                    data = await self.fetch_stock_data(self.session, ticker)
                    if data:
                        results[ticker] = data
                    else:
                        print(f"⚠️ Nie udało się pobrać danych dla {ticker}")
                except asyncio.CancelledError:
                    print("\n⚠️ Przerwano pobieranie danych...")
                    break
                except Exception as e:
                    print(f"⚠️ Błąd podczas pobierania {ticker}: {str(e)}")
                    continue
                    
        except asyncio.CancelledError:
            print("\n⚠️ Przerwano pobieranie danych...")
        except Exception as e:
            print(f"⚠️ Błąd podczas pobierania danych: {str(e)}")
        finally:
            if hasattr(self, 'session'):
                await self.session.close()
            
        return results
        
        async def process_chunk(session, ticker_chunk):
            tasks = [self.fetch_stock_data(session, ticker) for ticker in ticker_chunk]
            try:
                return await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                print(f"⚠️ Błąd podczas przetwarzania grupy: {str(e)}")
                return []
        
        try:
            connector = aiohttp.TCPConnector(limit=1, ssl=False)  # Limit połączeń TCP, wyłącz SSL dla lepszej wydajności
            timeout = aiohttp.ClientTimeout(total=600, connect=60, sock_connect=60, sock_read=60)  # Zwiększony timeout całkowity
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br'
            }
            async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
                chunk_size = 1  # Pobieramy po 1 tickerze na raz
                results = []
                
                # Podziel tickery na grupy
                chunks = [tickers[i:i+chunk_size] for i in range(0, len(tickers), chunk_size)]
                total_chunks = len(chunks)
                
                for i, chunk in enumerate(chunks, 1):
                    try:
                        print(f"🔄 Przetwarzam ticker {i}/{total_chunks}...")
                        chunk_results = await process_chunk(session, chunk)
                        results.extend([r for r in chunk_results if not isinstance(r, Exception)])
                        if i < total_chunks:  # Jeśli to nie ostatni ticker
                            await asyncio.sleep(7.0)  # 7 sekund przerwy między tickerami
                    except asyncio.CancelledError:
                        print("⚠️ Operacja przerwana")
                        break
                    except Exception as e:
                        print(f"⚠️ Błąd podczas przetwarzania grupy {i}: {str(e)}")
                        continue
                        
            # Przetwórz wyniki
            processed_data = {}
            for result in results:
                if result:
                    ticker = result["ticker"]
                    processed_data[ticker] = self.process_stock_data(result["data"])
                    
            elapsed_time = (datetime.now() - start_time).total_seconds()
            print(f"✅ Zakończono pobieranie danych w {elapsed_time:.2f}s")
            return processed_data
            
        except Exception as e:
            print(f"❌ Krytyczny błąd podczas pobierania danych: {str(e)}")
            return {}
            
        # Przetwarzanie wyników
        processed_data = {}
        for result in results:
            if result:
                ticker = result["ticker"]
                processed_data[ticker] = self.process_stock_data(result["data"])
                
        elapsed_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Zakończono pobieranie danych w {elapsed_time:.2f}s")
        return processed_data

    def process_stock_data(self, raw_data: Dict) -> Dict:
        """Przetwarzanie surowych danych z API"""
        try:
            price_data = raw_data.get("price", {})
            summary = raw_data.get("summaryDetail", {})
            stats = raw_data.get("defaultKeyStatistics", {})
            
            # Funkcja do bezpiecznego wyciągania wartości i konwertowania dat
            def get_raw_value(data_dict, key):
                try:
                    value = data_dict.get(key, {})
                    if isinstance(value, dict):
                        raw_value = value.get("raw")
                        # Konwertuj timestampy na ISO format
                        if key.lower().endswith("date") and raw_value:
                            return datetime.fromtimestamp(raw_value).isoformat()
                        return raw_value
                    return value
                except:
                    return None

            result = {
                "nazwa": price_data.get("longName", ""),
                "sektor": price_data.get("sector", "N/A"),
                "branza": price_data.get("industry", "N/A"),
                "kapitalizacja": get_raw_value(price_data, "marketCap"),
                "currentPrice": get_raw_value(price_data, "regularMarketPrice"),
                "previousClose": get_raw_value(price_data, "regularMarketPreviousClose"),
                "volume": get_raw_value(price_data, "regularMarketVolume"),
                "PE": get_raw_value(summary, "trailingPE"),
                "przyszle_PE": get_raw_value(summary, "forwardPE"),
                "dywidenda_roczna": get_raw_value(summary, "dividendYield") or 0,
                "dividendRate": get_raw_value(summary, "dividendRate"),
                "lastDividendValue": get_raw_value(summary, "lastDividendValue"),
                "lastDividendDate": get_raw_value(summary, "lastDividendDate"),
                "beta": get_raw_value(summary, "beta"),
                "bookValue": get_raw_value(stats, "bookValue"),
                "priceToBook": get_raw_value(stats, "priceToBook")
            }
            
            # Usuń None wartości aby uniknąć problemów z serializacją
            return {k: v for k, v in result.items() if v is not None}
            
        except Exception as e:
            print(f"⚠️ Błąd przetwarzania danych: {str(e)}")
            return {}

    def run_async_fetch(self, tickers: List[str]) -> Dict[str, Any]:
        """Wrapper do uruchamiania asynchronicznego pobierania z inteligentnym cache"""
        try:
            # Sprawdź cache dla każdego tickera
            cached_data = {}
            tickers_to_fetch = []
            
            for ticker in tickers:
                cache_key = f"stock_data_{ticker}"
                data = self.cache.get_data(cache_key)
                if data:
                    cached_data[ticker] = data
                else:
                    tickers_to_fetch.append(ticker)
            
            if not tickers_to_fetch:
                print("✓ Wszystkie dane dostępne w cache")
                return cached_data
            
            print(f"🔄 Pobieram brakujące dane dla {len(tickers_to_fetch)} spółek...")
            
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    fresh_data = loop.run_until_complete(self.fetch_multiple_stocks(tickers_to_fetch))
                finally:
                    loop.close()
            else:
                fresh_data = loop.create_task(self.fetch_multiple_stocks(tickers_to_fetch))
            
            # Zapisz nowe dane do cache
            for ticker, data in fresh_data.items():
                cache_key = f"stock_data_{ticker}"
                self.cache.set_data(cache_key, data)
            
            # Połącz dane z cache i świeżo pobrane
            return {**cached_data, **fresh_data}
                
        except KeyboardInterrupt:
            print("\n⚠️ Przerwano pobieranie danych...")
            return cached_data  # Zwróć przynajmniej dane z cache
        except Exception as e:
            print(f"⚠️ Błąd podczas pobierania danych: {str(e)}")
            return cached_data  # Zwróć przynajmniej dane z cache