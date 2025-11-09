"""
📰 KNOWLEDGE BASE AUTO-UPDATER
System automatycznego pobierania artykułów finansowych co 12h

Źródła:
- Yahoo Finance RSS
- Seeking Alpha (via scraping)
- Bloomberg headlines
- WSJ Market News

Zapisuje do: knowledge_base/articles.json
Frequency: Co 12 godzin (Windows Task Scheduler)
"""

import json
import os
import requests
from datetime import datetime, timedelta
import feedparser
from bs4 import BeautifulSoup

# Folder na knowledge base
KB_FOLDER = 'knowledge_base'
ARTICLES_FILE = os.path.join(KB_FOLDER, 'articles.json')

# Utwórz folder jeśli nie istnieje
os.makedirs(KB_FOLDER, exist_ok=True)


def fetch_yahoo_finance_rss():
    """
    Pobierz najnowsze wiadomości z Yahoo Finance RSS
    """
    articles = []
    
    feeds = [
        'https://finance.yahoo.com/news/rssindex',
        'https://feeds.finance.yahoo.com/rss/2.0/headline'
    ]
    
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # Top 10 z każdego feed
                article = {
                    'id': f"yahoo_{entry.get('id', entry.link)}",
                    'date': datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else datetime.now().strftime('%Y-%m-%d'),
                    'source': 'Yahoo Finance',
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', '')[:500],  # Max 500 chars
                    'tags': extract_tags_from_text(entry.title + ' ' + entry.get('summary', '')),
                    'relevance_score': 0.5,  # Default, można later uaktualnić ML
                    'fetched_at': datetime.now().isoformat()
                }
                
                articles.append(article)
        
        except Exception as e:
            print(f"⚠️ Błąd pobierania Yahoo RSS {feed_url}: {e}")
    
    return articles


def fetch_seeking_alpha_headlines():
    """
    Pobierz nagłówki z Seeking Alpha (scraping)
    """
    articles = []
    
    try:
        url = 'https://seekingalpha.com/market-news'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Szukaj artykułów (struktura może się zmienić)
        headlines = soup.find_all('a', {'data-test-id': 'post-list-item-title'}, limit=15)
        
        for headline in headlines:
            title = headline.get_text(strip=True)
            link = 'https://seekingalpha.com' + headline.get('href', '')
            
            article = {
                'id': f"sa_{link}",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Seeking Alpha',
                'title': title,
                'link': link,
                'summary': '',
                'tags': extract_tags_from_text(title),
                'relevance_score': 0.6,  # SA zwykle bardziej relevantne
                'fetched_at': datetime.now().isoformat()
            }
            
            articles.append(article)
    
    except Exception as e:
        print(f"⚠️ Błąd scraping Seeking Alpha: {e}")
    
    return articles


def fetch_bloomberg_headlines():
    """
    Pobierz nagłówki z Bloomberg (RSS/scraping)
    """
    articles = []
    
    try:
        # Bloomberg RSS (może wymagać subscription)
        feed_url = 'https://www.bloomberg.com/feed/podcast/bloomberg-surveillance.xml'
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries[:10]:
            article = {
                'id': f"bloomberg_{entry.link}",
                'date': datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else datetime.now().strftime('%Y-%m-%d'),
                'source': 'Bloomberg',
                'title': entry.title,
                'link': entry.link,
                'summary': entry.get('summary', '')[:500],
                'tags': extract_tags_from_text(entry.title),
                'relevance_score': 0.7,  # Bloomberg często wysokiej jakości
                'fetched_at': datetime.now().isoformat()
            }
            
            articles.append(article)
    
    except Exception as e:
        print(f"⚠️ Błąd pobierania Bloomberg: {e}")
    
    return articles


def extract_tags_from_text(text):
    """
    Ekstrakcja tagów z tekstu (prosty keyword matching)
    """
    keywords = {
        'macro': ['fed', 'interest rate', 'inflation', 'recession', 'gdp', 'employment'],
        'tech': ['apple', 'microsoft', 'google', 'amazon', 'meta', 'nvidia', 'tesla'],
        'finance': ['bank', 'credit', 'loan', 'mortgage', 'jpmorgan', 'goldman'],
        'crypto': ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'binance'],
        'energy': ['oil', 'gas', 'exxon', 'chevron', 'renewable'],
        'healthcare': ['pharma', 'biotech', 'pfizer', 'moderna', 'healthcare'],
        'earnings': ['earnings', 'revenue', 'profit', 'eps', 'guidance'],
        'm&a': ['merger', 'acquisition', 'buyout', 'deal']
    }
    
    text_lower = text.lower()
    tags = []
    
    for tag, words in keywords.items():
        if any(word in text_lower for word in words):
            tags.append(tag)
    
    return tags if tags else ['general']


def calculate_relevance_to_portfolio(article, portfolio_tickers=None):
    """
    Oblicz relevance artykułu do portfolio (0-1)
    
    Bazuje na:
    - Czy wspomina tickery z portfolio
    - Czy ma tagi pasujące do sektorów w portfolio
    """
    if portfolio_tickers is None:
        return 0.5  # Default
    
    relevance = 0.5
    text = (article['title'] + ' ' + article['summary']).lower()
    
    # Sprawdź czy wspomina nasze tickery
    mentioned_tickers = [t for t in portfolio_tickers if t.lower() in text]
    if mentioned_tickers:
        relevance = min(1.0, 0.7 + (len(mentioned_tickers) * 0.1))
    
    # Sprawdź tagi
    high_priority_tags = ['macro', 'earnings', 'tech', 'finance']
    if any(tag in article['tags'] for tag in high_priority_tags):
        relevance += 0.1
    
    return min(1.0, relevance)


def load_existing_articles():
    """Wczytaj istniejące artykuły"""
    if not os.path.exists(ARTICLES_FILE):
        return []
    
    try:
        with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('articles', [])
    except Exception as e:
        print(f"⚠️ Błąd wczytywania articles.json: {e}")
        return []


def save_articles(articles):
    """Zapisz artykuły do JSON"""
    data = {
        'last_updated': datetime.now().isoformat(),
        'total_articles': len(articles),
        'articles': articles
    }
    
    try:
        with open(ARTICLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Zapisano {len(articles)} artykułów do {ARTICLES_FILE}")
    except Exception as e:
        print(f"❌ Błąd zapisu articles.json: {e}")


def remove_old_articles(articles, days=14):
    """Usuń artykuły starsze niż X dni"""
    cutoff = datetime.now() - timedelta(days=days)
    
    filtered = [
        a for a in articles 
        if datetime.fromisoformat(a['date']) > cutoff
    ]
    
    removed = len(articles) - len(filtered)
    if removed > 0:
        print(f"🗑️ Usunięto {removed} starych artykułów (>{days} dni)")
    
    return filtered


def deduplicate_articles(articles):
    """Usuń duplikaty bazując na ID"""
    seen = set()
    unique = []
    
    for article in articles:
        if article['id'] not in seen:
            seen.add(article['id'])
            unique.append(article)
    
    duplicates = len(articles) - len(unique)
    if duplicates > 0:
        print(f"🔄 Usunięto {duplicates} duplikatów")
    
    return unique


def run_knowledge_base_update():
    """
    Główna funkcja - pobierz nowe artykuły i zaktualizuj bazę
    """
    print("="*70)
    print("📰 KNOWLEDGE BASE AUTO-UPDATE")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    
    # Wczytaj istniejące
    existing = load_existing_articles()
    print(f"📚 Istniejące artykuły: {len(existing)}")
    
    # Pobierz nowe ze wszystkich źródeł
    new_articles = []
    
    print("\n🔍 Pobieranie z Yahoo Finance...")
    new_articles.extend(fetch_yahoo_finance_rss())
    
    print("🔍 Pobieranie z Seeking Alpha...")
    new_articles.extend(fetch_seeking_alpha_headlines())
    
    print("🔍 Pobieranie z Bloomberg...")
    new_articles.extend(fetch_bloomberg_headlines())
    
    print(f"\n✅ Pobrano {len(new_articles)} nowych artykułów")
    
    # Połącz z istniejącymi
    all_articles = existing + new_articles
    
    # Usuń duplikaty
    all_articles = deduplicate_articles(all_articles)
    
    # Usuń stare artykuły
    all_articles = remove_old_articles(all_articles, days=14)
    
    # Sortuj po dacie (najnowsze na górze)
    all_articles.sort(key=lambda x: x['date'], reverse=True)
    
    # Zapisz
    save_articles(all_articles)
    
    print("\n" + "="*70)
    print("✅ Aktualizacja knowledge base zakończona!")
    print(f"📊 Łączna liczba artykułów: {len(all_articles)}")
    print("="*70)


if __name__ == "__main__":
    run_knowledge_base_update()
