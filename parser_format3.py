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
    """Remove HTML tags from a string and unescape HTML entities."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return unescape(cleantext.strip())

def parse_format_3(url: str) -> List[StandardArticle]:
    """Parse RSS feeds for Format 3 (Copernicus journals)."""
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        # Extract authors
        authors = []
        if 'summary' in entry:
            author_match = re.search(r'<br />\s*(.*?)<br />', entry.summary)
            if author_match:
                authors = [author.strip() for author in author_match.group(1).split(',') if author.strip()]
                # Remove 'and' from the last author if present
                if authors and authors[-1].startswith('and '):
                    authors[-1] = authors[-1][4:].strip()

        # Extract publication date
        pub_date = datetime(*entry.published_parsed[:6]) if 'published_parsed' in entry else None

        # Extract DOI
        doi = entry.get('id', '').replace('https://doi.org/', '')

        # Create summary
        summary = clean_html(entry.get('summary', ''))
        # Remove the title, author information, and journal details from the summary
        summary = re.sub(r'^.*?Earth Surf\. Dynam\..*?, \d{4}\s*', '', summary, flags=re.DOTALL)

        # Extract journal information
        journal = "Earth Surface Dynamics"

        # Keywords are not clearly defined in this format, so we'll leave it empty
        keywords = []

        article = StandardArticle(
            title=entry.title,
            link=entry.link,
            authors=authors,
            published_date=pub_date,
            summary=summary,
            journal=journal,
            doi=doi,
            keywords=keywords,
            full_text_link=entry.link
        )
        articles.append(article)

    return articles

# Example usage
if __name__ == "__main__":
    url = "https://esurf.copernicus.org/xml/rss2_0.xml"  # Earth Surface Dynamics
    parsed_articles = parse_format_3(url)
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