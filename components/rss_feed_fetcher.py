from typing import List, Dict, Optional, Any, Union
import feedparser
import requests
import logging
from datetime import datetime
from urllib.parse import urlparse
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from feedparser.util import FeedParserDict

class RSSFeedFetcher:
    def __init__(self, timeout: int = 30):
        """Initialize RSS feed fetcher with configurable timeout"""
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        
    async def fetch_all(self, feed_urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fetch multiple RSS feeds concurrently
        
        Args:
            feed_urls: List of RSS feed URLs. If None, uses configured feeds.
            
        Returns:
            List of standardized article dictionaries
        """
        if not feed_urls:
            self.logger.warning("No feed URLs provided")
            return []
            
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_single(url, session) for url in feed_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        # Flatten results and filter out errors
        articles = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Failed to fetch feed: {str(result)}")
                continue
            if isinstance(result, list):  # Type guard
                articles.extend(result)
            
        return articles
    
    async def fetch_single(self, url: str, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """
        Fetch and parse a single RSS feed
        
        Args:
            url: RSS feed URL
            session: Aiohttp session for making requests
            
        Returns:
            List of article dictionaries from this feed
        
        Raises:
            ValueError: If URL is invalid
            RequestError: If feed cannot be fetched
            ParseError: If feed cannot be parsed
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError(f"Invalid URL: {url}")
            
            # Fetch feed content
            async with session.get(url, timeout=self.timeout) as response:
                response.raise_for_status()
                content = await response.text()
            
            # Parse feed
            feed = feedparser.parse(content)
            if feed.bozo:  # feedparser's error flag
                raise ParseError(f"Feed parsing error: {feed.bozo_exception}")
            
            # Extract and standardize articles
            articles = []
            for entry in feed.entries:
                try:
                    article = self._standardize_entry(entry, feed.feed)
                    articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Failed to process entry: {str(e)}")
                    continue
                    
            return articles
            
        except aiohttp.ClientError as e:
            raise RequestError(f"Failed to fetch feed {url}: {str(e)}")
        except Exception as e:
            raise FetchError(f"Unexpected error fetching {url}: {str(e)}")
    
    def _standardize_entry(self, entry: FeedParserDict, feed_info: FeedParserDict) -> Dict[str, Any]:
        """
        Convert feed entry to standardized article format
        
        Args:
            entry: Raw feed entry
            feed_info: Feed metadata
            
        Returns:
            Standardized article dictionary
        """
        # Extract date with fallbacks
        published_date = None
        for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, date_field):
                parsed_time = getattr(entry, date_field)
                if parsed_time:
                    published_date = datetime(*parsed_time[:6]).isoformat()
                    break
        if not published_date:
            published_date = datetime.now().isoformat()
            
        # Extract text content
        content: str = ''
        if hasattr(entry, 'content') and entry.content:
            content = str(entry.content[0].get('value', ''))
        elif hasattr(entry, 'summary'):
            content = str(entry.summary)
        
        # Clean content
        if content:
            soup = BeautifulSoup(str(content), 'html.parser')
            content = soup.get_text(separator=' ', strip=True)
        
        return {
            'title': getattr(entry, 'title', ''),
            'journal': getattr(feed_info, 'title', ''),
            'published_date': published_date,
            'abstract': content[:1000] if content else '',  # Limit abstract length
            'url': getattr(entry, 'link', ''),
            'authors': [
                getattr(author, 'name', '') 
                for author in getattr(entry, 'authors', [])
            ]
        }

class FetchError(Exception):
    """Base class for feed fetching errors"""
    pass

class RequestError(FetchError):
    """Error occurred while requesting feed"""
    pass

class ParseError(FetchError):
    """Error occurred while parsing feed"""
    pass 