import feedparser

def parse_format_6():
    url = 'https://www.nature.com/ngeo.rss'
    print(f"Parsing feed from: {url}")
    
    feed = feedparser.parse(url)
    
    if feed.bozo:
        print(f"Error parsing feed: {feed.bozo_exception}")
        return
    
    print(f"Feed title: {feed.feed.title}")
    print(f"Number of entries: {len(feed.entries)}")
    
    for entry in feed.entries:
        print(f"- {entry.title}")
        print(f"  Link: {entry.link}")
        
        # Adaptive date extraction
        date_fields = ['published', 'updated', 'created', 'pubDate']
        for field in date_fields:
            if hasattr(entry, field):
                print(f"  Date ({field}): {getattr(entry, field)}")
                break
        else:
            print("  No date information available")
        
        # Flexible content extraction
        content_fields = ['summary', 'description', 'content']
        for field in content_fields:
            if hasattr(entry, field):
                content = getattr(entry, field)
                if isinstance(content, list) and content:
                    content = content[0].value
                print(f"  {field.capitalize()}: {content[:100]}...")  # Print first 100 characters
                break
        else:
            print("  No content available")
        
        print()

if __name__ == "__main__":
    parse_format_6()