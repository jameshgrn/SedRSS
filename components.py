# components.py
import feedparser
import csv
from datetime import datetime, timedelta
import logging
import html
from typing import Dict, List, Any
import requests
from requests.exceptions import RequestException
import re
import random
from dateutil import parser as date_parser
import time
from parser_factory import get_parser
from logging_config import setup_logging

class RSSFeedFetcher:
    def __init__(self, csv_file='journals.csv'):
        self.logger = setup_logging()
        self.journals = self.load_journals(csv_file)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]

    def load_journals(self, csv_file: str) -> list:
        journals = []
        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    journals.append(row)
            if journals:
                self.logger.info(f"Successfully loaded {len(journals)} journals from {csv_file}")
            else:
                self.logger.warning(f"No journals loaded from {csv_file}")
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_file}")
        except csv.Error as e:
            self.logger.error(f"Error reading CSV file: {e}")
        return journals

    def fetch_all(self):
        all_articles = []
        for journal in self.journals:
            self.logger.info(f"Fetching articles for {journal['Journal Name']}...")
            articles = self.fetch_journal(journal)
            all_articles.extend(articles)
            self.logger.info(f"Fetched {len(articles)} articles from {journal['Journal Name']}")
        self.logger.info(f"Fetched a total of {len(all_articles)} articles from all journals")
        return all_articles

    def fetch(self, journal):
        articles = []
        try:
            articles = self.fetch_journal(journal)  # Call fetch_journal directly
            self.logger.info(f"Successfully fetched {len(articles)} articles from {journal['Journal Name']}")
        except Exception as e:
            self.logger.error(f"Error fetching articles from {journal['Journal Name']}: {str(e)}")
        return articles

    def fetch_journal(self, journal: Dict[str, str], max_articles: int = None, max_retries: int = 3) -> List[Dict[str, Any]]:
        for attempt in range(max_retries):
            try:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                response = requests.get(journal['RSS URL'], headers=headers, timeout=10)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                self.logger.info(f"Fetched {len(feed.entries)} entries from {journal['Journal Name']}")
                
                articles = []
                for entry in feed.entries[:max_articles]:
                    try:
                        article = self.parse_journal_rss(entry, journal['Journal Name'], int(journal['Format']))
                        if article:
                            articles.append(article)
                        if len(articles) == max_articles:
                            break
                    except Exception as e:
                        self.logger.error(f"Error parsing entry for {journal['Journal Name']}: {str(e)}")
                
                self.logger.info(f"Successfully parsed {len(articles)} articles from {journal['Journal Name']}")
                return articles
            except HTTPError as e:
                if e.response.status_code == 403:
                    self.logger.error(f"Access forbidden for {journal['Journal Name']}. Skipping this journal.")
                    return []  # Return an empty list for this journal
                else:
                    self.logger.error(f"Attempt {attempt + 1} failed for {journal['Journal Name']}: {str(e)}")
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.RequestException as e:
                self.logger.error(f"Attempt {attempt + 1} failed for {journal['Journal Name']}: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        self.logger.error(f"Failed to fetch {journal['Journal Name']} after {max_retries} attempts")
        return []

    def parse_entries(self, entries: list, format_type: int, journal_name: str) -> list:
        parsed_articles = []
        for entry in entries:
            try:
                article = self.parse_article(entry, format_type, journal_name)
                if article:
                    parsed_articles.append(article)
            except Exception as e:
                self.logger.error(f"Error parsing article from {journal_name}: {str(e)}")
        return parsed_articles

    def parse_article(self, entry: dict, format_type: int, journal_name: str) -> Dict[str, Any]:
        parser_method = get_parser(format_type)
        if parser_method:
            return parser_method(entry, journal_name)
        else:
            self.logger.warning(f"Unsupported format type {format_type} for {journal_name}")
            return None

    def parse_journal_rss(self, entry, journal_name, format_type):
        parser = get_parser(format_type)
        if parser:
            return parser(entry, journal_name)
        else:
            self.logger.warning(f"No parser available for format type {format_type}")
            return None

class DataStandardizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def standardize(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        standardized_articles = []
        for article in articles:
            try:
                standardized_article = self._standardize_article(article)
                standardized_articles.append(standardized_article)
            except Exception as e:
                self.logger.error(f"Error standardizing article: {str(e)}")
        return standardized_articles

    def _standardize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': self._standardize_title(article.get('title', '')),
            'authors': self._standardize_authors(article.get('authors', [])),
            'journal': article.get('journal', ''),
            'abstract': self._standardize_abstract(article.get('abstract', '')),
            'published_date': self._standardize_date(article.get('published_date', '')),
            'url': article.get('url', ''),
        }

    def _standardize_title(self, title: str) -> str:
        return title.strip().title()

    def _standardize_authors(self, authors: List[str]) -> List[str]:
        return [author.strip() for author in authors if author.strip()]

    def _standardize_abstract(self, abstract: str) -> str:
        # Remove HTML tags (simple approach, consider using BeautifulSoup for more complex HTML)
        abstract = re.sub('<[^<]+?>', '', abstract)
        return abstract.strip()

    def _standardize_date(self, date_string: str) -> str:
        try:
            date = datetime.fromisoformat(date_string)
            return date.strftime("%Y-%m-%d")
        except ValueError:
            self.logger.warning(f"Could not parse date: {date_string}")
            return date_string

import re
from typing import List, Dict, Any

class RelevanceScorer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.keywords = self._load_keywords()

    def _load_keywords(self):
        # TODO: Load keywords from a file or database
        return ["sediment", "fluvial", "geomorphology", "river", "alluvial"]

    def score(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored_articles = []
        for article in articles:
            score = self._calculate_score(article)
            scored_article = article.copy()
            scored_article['relevance_score'] = score
            scored_articles.append(scored_article)
        return scored_articles

    def _calculate_score(self, article: Dict[str, Any]) -> float:
        score = 0
        text = f"{article['title']} {article['abstract']}".lower()
        for keyword in self.keywords:
            if keyword in text:
                score += 1
        return score / len(self.keywords)

from typing import List, Dict, Any
from datetime import datetime, timedelta

class ArticleDatabase:
    def __init__(self):
        self.articles = []

    def store(self, articles: List[Dict[str, Any]]):
        self.articles.extend(articles)

    def get_recent_articles(self, days: int = 7) -> List[Dict[str, Any]]:
        cutoff_date = datetime.now().replace(tzinfo=None) - timedelta(days=days)
        recent_articles = [
            article for article in self.articles
            if self._parse_date(article['published_date']) > cutoff_date
        ]
        return recent_articles

    def _parse_date(self, date_string: str) -> datetime:
        try:
            # Try parsing as ISO format first
            return datetime.fromisoformat(date_string).replace(tzinfo=None)
        except ValueError:
            try:
                # If ISO parsing fails, try a more flexible parsing
                return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=None)
            except ValueError:
                # If all parsing fails, return a very old date
                return datetime.min

    def clear(self):
        self.articles = []

class NewsletterComposer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def compose(self, scored_articles: List[Dict[str, Any]]) -> str:
        newsletter = "SedRSS Weekly Newsletter\n\n"
        
        # Sort articles by relevance score in descending order
        sorted_articles = sorted(scored_articles, key=lambda x: x['relevance_score'], reverse=True)
        
        # Take top 5 articles
        top_articles = sorted_articles[:5]
        
        for article in top_articles:
            newsletter += f"Title: {article['title']}\n"
            newsletter += f"Authors: {', '.join(article['authors'])}\n"
            newsletter += f"Journal: {article['journal']}\n"
            newsletter += f"Published Date: {article['published_date']}\n"
            newsletter += f"Relevance Score: {article['relevance_score']:.2f}\n"
            newsletter += f"Abstract: {article['abstract'][:200]}...\n"
            newsletter += f"URL: {article['url']}\n\n"
        
        return newsletter