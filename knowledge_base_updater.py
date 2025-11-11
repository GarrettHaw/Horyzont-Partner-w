"""
📰 Knowledge Base Updater
Tygodniowy update bazy wiedzy z najnowszymi wiadomościami rynkowymi

Uruchamiany automatycznie w poniedziałki o 08:00 UTC przez GitHub Actions
Źródła:
- Google News RSS (market trends, S&P500, crypto news)
- Aktualizuje knowledge_base/articles.json
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib

try:
    import feedparser
    FEEDPARSER_OK = True
except ImportError:
    FEEDPARSER_OK = False
    print("⚠️ feedparser not installed - install with: pip install feedparser")

KNOWLEDGE_BASE_DIR = "knowledge_base"
ARTICLES_FILE = os.path.join(KNOWLEDGE_BASE_DIR, "articles.json")

# RSS feeds dla wiadomości rynkowych
NEWS_FEEDS = {
    'market_trends': [
        'https://news.google.com/rss/search?q=stock+market+trends&hl=en-US&gl=US&ceid=US:en',
        'https://news.google.com/rss/search?q=S%26P+500&hl=en-US&gl=US&ceid=US:en',
        'https://news.google.com/rss/search?q=dividend+stocks&hl=en-US&gl=US&ceid=US:en',
    ],
    'crypto': [
        'https://news.google.com/rss/search?q=cryptocurrency+market&hl=en-US&gl=US&ceid=US:en',
        'https://news.google.com/rss/search?q=bitcoin+ethereum&hl=en-US&gl=US&ceid=US:en',
    ],
    'economy': [
        'https://news.google.com/rss/search?q=federal+reserve+interest+rates&hl=en-US&gl=US&ceid=US:en',
        'https://news.google.com/rss/search?q=inflation+data&hl=en-US&gl=US&ceid=US:en',
    ]
}

MAX_ARTICLES = 50  # Maksymalna liczba artykułów do zachowania
DAYS_TO_KEEP = 30  # Usuń artykuły starsze niż 30 dni

def load_existing_articles() -> Dict[str, Any]:
    """Załaduj istniejące artykuły"""
    if not os.path.exists(ARTICLES_FILE):
        return {
            'last_updated': None,
            'total_articles': 0,
            'articles': []
        }
    
    try:
        with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading articles: {e}")
        return {
            'last_updated': None,
            'total_articles': 0,
            'articles': []
        }

def generate_article_id(title: str, url: str) -> str:
    """Generuj unikalny ID artykułu"""
    content = f"{title}{url}"
    return hashlib.md5(content.encode()).hexdigest()[:16]

def fetch_news_from_feed(feed_url: str, category: str) -> List[Dict[str, Any]]:
    """Pobierz wiadomości z RSS feed"""
    if not FEEDPARSER_OK:
        return []
    
    articles = []
    
    try:
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries[:5]:  # Max 5 artykułów z każdego feed
            # Parsuj datę
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).isoformat()
            else:
                published = datetime.now().isoformat()
            
            article = {
                'id': generate_article_id(entry.title, entry.link),
                'date': published,
                'title': entry.title,
                'source': entry.source.title if hasattr(entry, 'source') else 'Unknown',
                'url': entry.link,
                'summary': entry.summary if hasattr(entry, 'summary') else '',
                'ticker': None,  # Można rozszerzyć o ekstrakcję tickerów z tytułu
                'type': category,
                'relevance': 7,  # Domyślna relevance
                'added_at': datetime.now().isoformat()
            }
            
            articles.append(article)
    
    except Exception as e:
        print(f"⚠️ Error fetching feed {feed_url}: {e}")
    
    return articles

def update_knowledge_base() -> Dict[str, Any]:
    """Aktualizuj bazę wiedzy z najnowszymi wiadomościami"""
    print("📰 Knowledge Base Update - START")
    print(f"📅 {datetime.now().isoformat()}")
    print("-" * 60)
    
    # Załaduj istniejące artykuły
    existing_data = load_existing_articles()
    existing_articles = existing_data.get('articles', [])
    existing_ids = {article['id'] for article in existing_articles}
    
    print(f"📚 Existing articles: {len(existing_articles)}")
    
    # Pobierz nowe artykuły
    new_articles = []
    
    if not FEEDPARSER_OK:
        print("⚠️ feedparser not available - skipping RSS fetch")
        print("💡 Install with: pip install feedparser")
    else:
        for category, feeds in NEWS_FEEDS.items():
            print(f"\n🔍 Fetching {category} news...")
            for feed_url in feeds:
                articles = fetch_news_from_feed(feed_url, category)
                
                # Dodaj tylko nowe artykuły
                for article in articles:
                    if article['id'] not in existing_ids:
                        new_articles.append(article)
                        print(f"  ✅ New: {article['title'][:60]}...")
    
    print(f"\n📰 New articles found: {len(new_articles)}")
    
    # Połącz istniejące i nowe artykuły
    all_articles = existing_articles + new_articles
    
    # Usuń stare artykuły (starsze niż DAYS_TO_KEEP)
    cutoff_date = datetime.now() - timedelta(days=DAYS_TO_KEEP)
    filtered_articles = []
    
    for article in all_articles:
        try:
            article_date = datetime.fromisoformat(article['date'].replace('Z', '+00:00'))
            if article_date > cutoff_date:
                filtered_articles.append(article)
        except:
            # Jeśli nie można sparsować daty, zachowaj artykuł
            filtered_articles.append(article)
    
    removed_count = len(all_articles) - len(filtered_articles)
    if removed_count > 0:
        print(f"🗑️ Removed {removed_count} old articles (>{DAYS_TO_KEEP} days)")
    
    # Ogranicz do MAX_ARTICLES (najnowsze)
    filtered_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    filtered_articles = filtered_articles[:MAX_ARTICLES]
    
    # Przygotuj zaktualizowane dane
    updated_data = {
        'last_updated': datetime.now().isoformat(),
        'total_articles': len(filtered_articles),
        'articles': filtered_articles
    }
    
    return updated_data

def save_knowledge_base(data: Dict[str, Any]) -> bool:
    """Zapisz bazę wiedzy do pliku"""
    # Upewnij się że katalog istnieje
    os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
    
    try:
        with open(ARTICLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved: {ARTICLES_FILE}")
        print(f"📊 Total articles: {data['total_articles']}")
        return True
    
    except Exception as e:
        print(f"❌ Error saving knowledge base: {e}")
        return False

def main():
    """Główna funkcja update"""
    try:
        # Aktualizuj bazę wiedzy
        updated_data = update_knowledge_base()
        
        # Zapisz
        success = save_knowledge_base(updated_data)
        
        print("-" * 60)
        if success:
            print("📰 Knowledge Base Update - COMPLETE ✅")
            return 0
        else:
            print("❌ Knowledge Base Update - FAILED")
            return 1
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
