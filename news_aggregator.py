"""
News Aggregator - Horyzont Partnerów
====================================
Automatyczne pobieranie newsów finansowych z dwóch źródeł:
1. Trading212 API - newsy o Twoich konkretnych pozycjach
2. Google News API - ogólne trendy rynkowe i makroekonomiczne

Usage:
    python news_aggregator.py update    # Pobierz i zapisz newsy
    python news_aggregator.py show      # Pokaż ostatnie newsy
    python news_aggregator.py clear     # Wyczyść cache
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from urllib.parse import quote

# ============================================================
# KONFIGURACJA
# ============================================================

NEWS_FILE = "knowledge_base/articles.json"
CACHE_FILE = "news_cache.json"
CACHE_TTL_HOURS = 6  # Odświeżaj co 6h

# Google News RSS (darmowe, bez API key)
GOOGLE_NEWS_BASE = "https://news.google.com/rss/search"

# Trading212 API
T212_API_BASE = "https://live.trading212.com/api/v0"

# Keywords dla Google News (trendy rynkowe)
MARKET_KEYWORDS = [
    "fed rate decision",
    "stock market",
    "inflation report",
    "crypto market",
    "dividend stocks",
    "market crash",
    "bull market",
    "bear market"
]

# ============================================================
# POMOCNICZE FUNKCJE
# ============================================================

def load_json(filepath: str, default=None):
    """Wczytaj JSON z obsługą błędów"""
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Błąd wczytywania {filepath}: {e}")
        return default if default is not None else {}

def save_json(filepath: str, data):
    """Zapisz JSON"""
    try:
        # Utwórz folder jeśli nie istnieje (tylko dla NEWS_FILE z folderm knowledge_base/)
        dirpath = os.path.dirname(filepath)
        if dirpath:  # Jeśli jest folder w ścieżce
            os.makedirs(dirpath, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Błąd zapisywania {filepath}: {e}")
        return False

def is_cache_valid() -> bool:
    """Sprawdź czy cache jest aktualny"""
    cache = load_json(CACHE_FILE, {})
    if 'last_update' not in cache:
        return False
    
    last_update = datetime.fromisoformat(cache['last_update'])
    age_hours = (datetime.now() - last_update).total_seconds() / 3600
    
    return age_hours < CACHE_TTL_HOURS

# ============================================================
# 1. TRADING212 NEWS - Newsy o Twoich pozycjach
# ============================================================

def get_t212_api_key() -> Optional[str]:
    """Pobierz klucz API Trading212 z credentials.json"""
    try:
        creds = load_json("credentials.json", {})
        return creds.get("trading212_api_key")
    except:
        return None

def fetch_trading212_news() -> List[Dict]:
    """
    Pobiera newsy z Trading212 o pozycjach w portfelu
    
    UWAGA: Trading212 API nie ma dedykowanego endpointu /news
    Alternatywa: Użyję yfinance dla każdego tickera z portfela
    """
    print("📊 Pobieranie newsów o Twoich spółkach...")
    
    try:
        import yfinance as yf
        import gra_rpg
        
        # Pobierz portfel
        cele = load_json("cele.json", {})
        stan = gra_rpg.pobierz_stan_spolki(cele)
        
        # Wyciągnij tickery
        tickers = []
        
        # Akcje
        portfel_akcji = stan.get('PORTFEL_AKCJI', {}).get('Pozycje', {})
        for ticker, data in portfel_akcji.items():
            if ticker and isinstance(data, dict):
                tickers.append(ticker)
        
        # Krypto (jako -USD)
        portfel_crypto = stan.get('PORTFEL_KRYPTO', {}).get('Pozycje', {})
        for symbol in portfel_crypto.keys():
            if symbol != 'USDT':  # Pomijamy stablecoiny
                tickers.append(f"{symbol}-USD")
        
        print(f"   📈 Sprawdzam newsy dla {len(tickers)} pozycji...")
        
        all_news = []
        
        for ticker in tickers[:20]:  # Max 20 tickerów (limit yfinance)
            try:
                stock = yf.Ticker(ticker)
                news = stock.news
                
                if news:
                    for article in news[:3]:  # Top 3 na ticker
                        all_news.append({
                            "id": f"t212_{ticker}_{article.get('uuid', '')}",
                            "date": datetime.fromtimestamp(article.get('providerPublishTime', 0)).isoformat(),
                            "title": article.get('title', ''),
                            "source": article.get('publisher', 'Unknown'),
                            "url": article.get('link', ''),
                            "summary": article.get('title', ''),  # yfinance nie daje summary
                            "ticker": ticker,
                            "type": "portfolio",
                            "relevance": 10  # Highest relevance - Twoje spółki!
                        })
                
            except Exception as e:
                print(f"   ⚠️ Błąd dla {ticker}: {e}")
                continue
        
        print(f"   ✅ Pobrano {len(all_news)} newsów o Twoich spółkach")
        return all_news
        
    except Exception as e:
        print(f"⚠️ Błąd pobierania T212 news: {e}")
        return []

# ============================================================
# 2. GOOGLE NEWS - Ogólne trendy rynkowe
# ============================================================

def fetch_google_news() -> List[Dict]:
    """
    Pobiera ogólne newsy finansowe z Google News RSS
    """
    print("🌍 Pobieranie ogólnych newsów rynkowych z Google News...")
    
    all_news = []
    
    try:
        import feedparser
        
        for keyword in MARKET_KEYWORDS[:5]:  # Top 5 keywords
            try:
                # Buduj URL do RSS
                query = quote(f"{keyword} finance")
                rss_url = f"{GOOGLE_NEWS_BASE}?q={query}&hl=en-US&gl=US&ceid=US:en"
                
                print(f"   🔍 Szukam: {keyword}...")
                
                # Parsuj RSS
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:3]:  # Top 3 na keyword
                    # Parsuj datę
                    pub_date = datetime.now().isoformat()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6]).isoformat()
                    
                    all_news.append({
                        "id": f"gnews_{entry.get('id', '')}",
                        "date": pub_date,
                        "title": entry.get('title', ''),
                        "source": entry.get('source', {}).get('title', 'Google News'),
                        "url": entry.get('link', ''),
                        "summary": entry.get('summary', ''),
                        "ticker": None,
                        "type": "market_trend",
                        "keyword": keyword,
                        "relevance": 7  # Medium relevance - ogólne newsy
                    })
                
            except Exception as e:
                print(f"   ⚠️ Błąd dla '{keyword}': {e}")
                continue
        
        print(f"   ✅ Pobrano {len(all_news)} ogólnych newsów")
        return all_news
        
    except ImportError:
        print("⚠️ Zainstaluj feedparser: pip install feedparser")
        return []
    except Exception as e:
        print(f"⚠️ Błąd pobierania Google News: {e}")
        return []

# ============================================================
# 3. AGREGACJA I RANKING
# ============================================================

def rank_and_filter_news(news: List[Dict], limit: int = 20) -> List[Dict]:
    """
    Rankinguje i filtruje newsy
    - Priorytet: newsy o Twoich spółkach > ogólne trendy
    - Usuwa duplikaty (ten sam tytuł)
    - Sortuje po dacie (najnowsze pierwsze)
    """
    # Usuń duplikaty po tytule
    seen_titles = set()
    unique_news = []
    
    for article in news:
        title = article.get('title', '').lower().strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_news.append(article)
    
    # Sortuj: najpierw po relevance (desc), potem po dacie (desc)
    sorted_news = sorted(
        unique_news,
        key=lambda x: (x.get('relevance', 0), x.get('date', '')),
        reverse=True
    )
    
    return sorted_news[:limit]

# ============================================================
# 4. ZAPISYWANIE DO KNOWLEDGE BASE
# ============================================================

def update_knowledge_base(news: List[Dict]) -> bool:
    """
    Aktualizuje knowledge_base/articles.json z nowymi newsami
    Zachowuje stare artykuły (max 100 ostatnich)
    """
    print("\n💾 Zapisuję do knowledge base...")
    
    # Wczytaj istniejące artykuły
    kb = load_json(NEWS_FILE, {"articles": []})
    existing_articles = kb.get("articles", [])
    
    # Dodaj nowe (na początek)
    new_articles = [{
        "id": article.get('id'),
        "date": article.get('date'),
        "title": article.get('title'),
        "source": article.get('source'),
        "url": article.get('url'),
        "summary": article.get('summary', article.get('title', '')),
        "ticker": article.get('ticker'),
        "type": article.get('type'),
        "relevance": article.get('relevance'),
        "added_at": datetime.now().isoformat()
    } for article in news]
    
    # Merge: nowe + stare (usuń duplikaty po ID)
    seen_ids = set()
    merged = []
    
    for article in new_articles + existing_articles:
        article_id = article.get('id')
        if article_id and article_id not in seen_ids:
            seen_ids.add(article_id)
            merged.append(article)
    
    # Ogranicz do 100 artykułów
    kb['articles'] = merged[:100]
    kb['last_update'] = datetime.now().isoformat()
    
    if save_json(NEWS_FILE, kb):
        print(f"   ✅ Zapisano {len(new_articles)} nowych artykułów")
        print(f"   📚 Łącznie w bazie: {len(kb['articles'])} artykułów")
        return True
    else:
        print("   ❌ Błąd zapisu")
        return False

# ============================================================
# 5. GŁÓWNA FUNKCJA UPDATE
# ============================================================

def update_news(force: bool = False) -> Dict:
    """
    Główna funkcja - pobiera newsy z obu źródeł i zapisuje
    """
    print("\n🔄 AKTUALIZACJA NEWSÓW")
    print("=" * 60)
    
    # Sprawdź cache
    if not force and is_cache_valid():
        print("✅ Cache aktualny (< 6h). Użyj --force aby wymusić update.")
        cache = load_json(CACHE_FILE, {})
        return cache
    
    all_news = []
    
    # 1. Trading212 / yfinance (Twoje spółki)
    t212_news = fetch_trading212_news()
    all_news.extend(t212_news)
    
    # 2. Google News (ogólne trendy)
    google_news = fetch_google_news()
    all_news.extend(google_news)
    
    # 3. Ranking i filtrowanie
    print(f"\n🎯 Ranking i filtrowanie {len(all_news)} artykułów...")
    top_news = rank_and_filter_news(all_news, limit=20)
    
    # 4. Zapisz do knowledge base
    update_knowledge_base(top_news)
    
    # 5. Zapisz cache
    cache_data = {
        "last_update": datetime.now().isoformat(),
        "total_fetched": len(all_news),
        "top_news": top_news
    }
    save_json(CACHE_FILE, cache_data)
    
    print("\n" + "=" * 60)
    print(f"✅ UPDATE ZAKOŃCZONY")
    print(f"   📊 Trading212 news: {len(t212_news)}")
    print(f"   🌍 Google News: {len(google_news)}")
    print(f"   🎯 Top ranked: {len(top_news)}")
    
    return cache_data

# ============================================================
# 6. FUNKCJE POMOCNICZE DLA STREAMLIT
# ============================================================

def get_latest_news(limit: int = 10, max_age_hours: int = 48) -> List[Dict]:
    """
    Zwraca najnowsze newsy dla wyświetlenia w UI lub przekazania do AI
    """
    kb = load_json(NEWS_FILE, {"articles": []})
    articles = kb.get("articles", [])
    
    # Filtruj po wieku
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    recent = []
    
    for article in articles:
        try:
            article_date = datetime.fromisoformat(article.get('date', ''))
            if article_date >= cutoff:
                recent.append(article)
        except:
            continue
    
    return recent[:limit]

def format_news_for_ai(limit: int = 5) -> str:
    """
    Formatuje newsy do przekazania partnerom AI
    """
    news = get_latest_news(limit=limit, max_age_hours=24)
    
    if not news:
        return ""
    
    lines = ["\n📰 NAJNOWSZE ARTYKUŁY FINANSOWE (ostatnie 24h):"]
    lines.append("")
    
    for i, article in enumerate(news, 1):
        date_str = article.get('date', '')[:10]  # YYYY-MM-DD
        title = article.get('title', 'Brak tytułu')
        source = article.get('source', 'Unknown')
        ticker = article.get('ticker')
        article_type = article.get('type')
        
        # Emoji na podstawie typu
        if article_type == 'portfolio':
            emoji = "🎯"
            label = f"[TWOJA SPÓŁKA: {ticker}]"
        else:
            emoji = "🌍"
            label = "[TREND RYNKOWY]"
        
        lines.append(f"{i}. {emoji} {label}")
        lines.append(f"   Tytuł: {title}")
        lines.append(f"   Źródło: {source} | Data: {date_str}")
        lines.append("")
    
    return "\n".join(lines)

# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "update":
            force = "--force" in sys.argv
            update_news(force=force)
        
        elif command == "show":
            news = get_latest_news(limit=10)
            print(f"\n📰 OSTATNIE NEWSY ({len(news)} artykułów):\n")
            for i, article in enumerate(news, 1):
                print(f"{i}. [{article.get('date', '')[:10]}] {article.get('title')}")
                print(f"   Źródło: {article.get('source')} | Typ: {article.get('type')}")
                if article.get('ticker'):
                    print(f"   🎯 Ticker: {article.get('ticker')}")
                print()
        
        elif command == "clear":
            if save_json(CACHE_FILE, {}):
                print("✅ Cache wyczyszczony")
        
        elif command == "ai-format":
            print(format_news_for_ai())
        
        else:
            print(f"⚠️ Nieznana komenda: {command}")
            print("\nDostępne komendy:")
            print("  python news_aggregator.py update         - Pobierz i zapisz newsy")
            print("  python news_aggregator.py update --force - Wymuś update (ignoruj cache)")
            print("  python news_aggregator.py show           - Pokaż ostatnie newsy")
            print("  python news_aggregator.py ai-format      - Format dla AI partnera")
            print("  python news_aggregator.py clear          - Wyczyść cache")
    
    else:
        # Domyślnie: update
        update_news()
