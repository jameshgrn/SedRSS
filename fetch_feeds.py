import feedparser
import pandas as pd

def read_journals_from_csv(file_path):
    """Read the CSV file and return a dictionary of journal names and their RSS URLs."""
    df = pd.read_csv(file_path, header=0)
    journals = df.set_index('Journal Name')['RSS URL'].to_dict()
    return journals

def get_feed_entries(rss_url):
    """Fetch the RSS feed and return the entries."""
    feed = feedparser.parse(rss_url)
    entries = feed.entries
    return entries
