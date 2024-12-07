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

def parse_format_1(entry, journal_name):
    """
    Parse RSS feeds for Format 1 (ScienceDirect journals).
    
    Args:
        entry: The RSS feed entry.
        journal_name: The name of the journal.
    
    Returns:
        List[StandardArticle]: A list of parsed articles in the standard format.
    """
    description = clean_html(entry.description)
    
    # Extract publication date
    pub_date_match = re.search(r'Publication date: (\d+ \w+ \d{4})', description)
    pub_date_str = pub_date_match.group(1) if pub_date_match else None
    pub_date = None
    if pub_date_str:
        try:
            pub_date = datetime.strptime(pub_date_str, "%d %B %Y")
        except ValueError:
            # If parsing fails, keep pub_date as None
            pass

    # Extract authors
    authors_match = re.search(r'Author\(s\): (.+)', description)
    authors = authors_match.group(1).split(', ') if authors_match else []

    # Create a clean summary
    summary_parts = []
    source_match = re.search(r'Source: (.+)', description)
    if source_match:
        summary_parts.append(f"Source: {source_match.group(1)}")
    if pub_date_str:
        summary_parts.append(f"Published: {pub_date_str}")
    summary = " | ".join(summary_parts)

    article = StandardArticle(
        title=clean_html(entry.title),
        link=entry.link,
        authors=authors,
        published_date=pub_date,
        summary=summary,
        journal=journal_name,
        doi=None,  # We're not including the DOI
        keywords=[],  # ScienceDirect RSS doesn't provide keywords
        full_text_link=entry.link
    )
    return article

# Example usage
if __name__ == "__main__":
    url = "https://rss.sciencedirect.com/publication/science/0169555X"  # Geomorphology
    parsed_articles = parse_format_1(url)
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