import feedparser
from datetime import datetime
from typing import List, Optional, TypedDict
import re

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
    """Remove HTML tags from a string."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def parse_authors(author_string: str) -> List[str]:
    """Parse the author string into a list of individual authors."""
    # Split the string by uppercase letters followed by lowercase letters
    potential_names = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z]\.?\s*[A-Z][a-z]+)*', author_string)
    
    # Filter out institution names and keep only likely author names
    authors = []
    for name in potential_names:
        if len(name.split()) <= 4 and not any(word in name.lower() for word in ['department', 'university', 'school', 'college']):
            authors.append(name)
    
    return authors[:6]  # Limit to first 6 authors

def parse_format_5(url: str) -> List[StandardArticle]:
    """Parse RSS feeds for Format 5 (PNAS-Geo)."""
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        # Extract authors
        authors = parse_authors(entry.get('author', ''))

        # Extract publication date
        pub_date = None
        if 'updated_parsed' in entry:
            pub_date = datetime(*entry.updated_parsed[:6])

        # Clean and truncate summary
        summary = clean_html(entry.get('summary', ''))
        summary = summary[:500] + '...' if len(summary) > 500 else summary

        # Extract journal name
        journal = entry.get('prism_publicationname', "Proceedings of the National Academy of Sciences")

        # Keywords are not provided in this feed
        keywords = []

        article = StandardArticle(
            title=clean_html(entry.title),
            link=entry.link,
            authors=authors,
            published_date=pub_date,
            summary=summary,
            journal=journal,
            keywords=keywords,
            full_text_link=entry.get('prism_url', entry.link)
        )
        articles.append(article)

    return articles

# Example usage
if __name__ == "__main__":
    url = "https://www.pnas.org/action/showFeed?type=searchTopic&taxonomyCode=topic&tagCode=earth-sci"
    parsed_articles = parse_format_5(url)
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