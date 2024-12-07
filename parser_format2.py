import feedparser
from datetime import datetime
from typing import List, Optional, TypedDict
import re
from html import unescape

class StandardArticle(TypedDict):
    title: str
    link: str
    authors: List[str]
    published_date: Optional[datetime]
    summary: str
    journal: str
    doi: Optional[str]
    keywords: List[str]
    full_text_link: Optional[str]

def clean_html(raw_html: str) -> str:
    """Remove HTML tags from a string."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return unescape(cleantext.strip())

def parse_format_2(url: str) -> List[StandardArticle]:
    """
    Parse RSS feeds for Format 2 (Wiley journals).
    
    Args:
        url (str): The RSS feed URL.
    
    Returns:
        List[StandardArticle]: A list of parsed articles in the standard format.
    """
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        # Extract authors
        authors = [author.strip() for author in entry.get('author', '').split(',') if author.strip()]

        # Extract publication date
        pub_date = None
        if 'published_parsed' in entry:
            pub_date = datetime(*entry.published_parsed[:6])

        # Extract DOI
        doi = entry.get('prism_doi', None)

        # Extract keywords (not available in this feed)
        keywords = []

        # Create summary
        summary = clean_html(entry.get('summary', ''))

        # Extract full text link
        full_text_link = entry.get('link', None)

        article = StandardArticle(
            title=clean_html(entry.title),
            link=entry.link,
            authors=authors,
            published_date=pub_date,
            summary=summary,
            journal=clean_html(feed.feed.title.replace("Wiley: ", "").replace(": Table of Contents", "")),
            doi=doi,
            keywords=keywords,
            full_text_link=full_text_link
        )
        articles.append(article)

    return articles

# Example usage
if __name__ == "__main__":
    url = "https://onlinelibrary.wiley.com/feed/10969837/most-recent"  # Earth Surface Processes and Landforms
    parsed_articles = parse_format_2(url)
    print(f"Parsed {len(parsed_articles)} articles from {parsed_articles[0]['journal']}")
    
    # Print details of the first article
    if parsed_articles:
        print("\nFirst article details:")
        for key, value in parsed_articles[0].items():
            if isinstance(value, list):
                print(f"{key}:")
                for item in value:
                    print(f"  - {item}")
            elif isinstance(value, datetime):
                print(f"{key}: {value.isoformat()}")
            else:
                print(f"{key}: {value}")