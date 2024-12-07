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
    keywords: List[str]
    full_text_link: str

def clean_html(raw_html: str) -> str:
    """Remove HTML tags from a string and unescape HTML entities."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return unescape(cleantext.strip())

def parse_format_4(url: str) -> List[StandardArticle]:
    """Parse RSS feeds for Format 4 (GeoScienceWorld journals)."""
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        # Extract publication date
        pub_date = None
        if 'published_parsed' in entry:
            pub_date = datetime(*entry.published_parsed[:6])

        # Clean and truncate summary
        summary = clean_html(entry.summary)
        summary = re.sub(r'^Abstract\s*', '', summary)  # Remove "Abstract" prefix
        summary = summary[:500] + '...' if len(summary) > 500 else summary

        # Extract journal name (hardcoded for now)
        journal = "Journal of Sedimentary Research"

        # Keywords are not provided in this feed
        keywords = []

        article = StandardArticle(
            title=clean_html(entry.title),
            link=entry.link,
            authors=[],  # Empty list as authors are not provided
            published_date=pub_date,
            summary=summary,
            journal=journal,
            keywords=keywords,
            full_text_link=entry.link
        )
        articles.append(article)

    return articles

# Example usage
if __name__ == "__main__":
    url = "https://pubs.geoscienceworld.org/rss/site_133/67.xml"  # Journal of Sedimentary Research
    parsed_articles = parse_format_4(url)
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