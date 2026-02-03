import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import re

def get_feed_urls():
    """Returns list of RSS feed URLs"""
    return [
        {"url": "https://www.latent.space/feed"},
        {"url": "https://simonwillison.net/atom/entries/"},
        {"url": "https://blog.pragmaticengineer.com/rss/"},
        {"url": "https://www.swyx.io/rss.xml"},
        {"url": "https://github.blog/changelog/feed/"},
        {"url": "https://openai.com/news/rss.xml"},
        {"url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml"},
        {"url": "https://www.reddit.com/r/ClaudeAI.rss"},
        {"url": "https://www.reddit.com/r/AI_Agents.rss"},
        {"url": "https://github.blog/changelog/label/copilot/"}
    ]

def parse_date(date_string):
    """Parse various date formats found in RSS/Atom feeds. Always returns timezone-aware datetime."""
    if not date_string:
        return None

    try:
        # Try RFC 2822 format (common in RSS) - returns timezone-aware datetime
        return parsedate_to_datetime(date_string)
    except:
        pass

    try:
        # Try ISO 8601 format (common in Atom)
        # Handle formats like: 2024-01-31T12:00:00Z or 2024-01-31T12:00:00+00:00
        date_string = date_string.strip()
        if 'T' in date_string:
            # Check if it has timezone info
            if date_string.endswith('Z'):
                date_string = date_string.rstrip('Z')
                dt = datetime.fromisoformat(date_string)
                return dt.replace(tzinfo=timezone.utc)
            elif re.search(r'[+-]\d{2}:\d{2}$', date_string):
                # Has timezone offset, fromisoformat can handle it in Python 3.7+
                return datetime.fromisoformat(date_string)
            else:
                # No timezone, assume UTC
                dt = datetime.fromisoformat(date_string)
                return dt.replace(tzinfo=timezone.utc)
    except:
        pass

    return None

def fetch_feed(url, days_back=7):
    """Fetch and parse RSS/Atom feed, returning entries from the past week"""
    try:
        # Set a user agent to avoid being blocked
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (RSS Reader)'}
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()

        # Parse XML
        root = ET.fromstring(content)

        # Determine feed type (RSS vs Atom)
        is_atom = root.tag.endswith('feed')

        # Calculate cutoff date (7 days ago) - use UTC timezone for comparison
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        entries = []

        if is_atom:
            # Parse Atom feed
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns)
                link = entry.find('atom:link', ns)
                published = entry.find('atom:published', ns)
                updated = entry.find('atom:updated', ns)
                summary = entry.find('atom:summary', ns)
                content = entry.find('atom:content', ns)

                # Get date
                date_elem = published if published is not None else updated
                entry_date = None
                if date_elem is not None:
                    entry_date = parse_date(date_elem.text)

                # Filter by date
                if entry_date and entry_date >= cutoff_date:
                    entry_dict = {
                        'title': title.text if title is not None else 'No title',
                        'link': link.get('href') if link is not None else '',
                        'date': entry_date.strftime('%Y-%m-%d %H:%M') if entry_date else '',
                        'description': (content.text if content is not None else
                                      summary.text if summary is not None else '')[:10000]
                    }
                    entries.append(entry_dict)
        else:
            # Parse RSS feed
            channel = root.find('channel')
            if channel is not None:
                for item in channel.findall('item'):
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    description = item.find('description')

                    # Get date
                    entry_date = None
                    if pub_date is not None:
                        entry_date = parse_date(pub_date.text)

                    # Filter by date
                    if entry_date and entry_date >= cutoff_date:
                        entry_dict = {
                            'title': title.text if title is not None else 'No title',
                            'link': link.text if link is not None else '',
                            'date': entry_date.strftime('%Y-%m-%d %H:%M') if entry_date else '',
                            'description': (description.text if description is not None else '')[:10000]
                        }
                        entries.append(entry_dict)

        return entries

    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return []

def format_feed_output(feed_url, entries, max_chars=100000):
    """Format feed entries into a string limited to max_chars"""
    output = f"\n{'='*80}\n"
    output += f"Feed: {feed_url}\n"
    output += f"Entries found: {len(entries)}\n"
    output += f"{'='*80}\n\n"

    for entry in entries:
        entry_text = f"Title: {entry['title']}\n"
        entry_text += f"Date: {entry['date']}\n"
        entry_text += f"Link: {entry['link']}\n"

        if entry['description']:
            # Clean HTML tags from description
            desc = re.sub(r'<[^>]+>', '', entry['description'])
            entry_text += f"Description: {desc}\n"

        entry_text += f"{'-'*40}\n\n"

        # Check if adding this entry would exceed the limit
        if len(output) + len(entry_text) > max_chars:
            output += f"\n[Output truncated at {max_chars} characters]\n"
            break

        output += entry_text

    return output[:max_chars]

def get_weekly_news():
    """Main function to fetch and display weekly news from all feeds"""
    feeds = get_feed_urls()
    all_results = []

    print("Fetching RSS feeds for the past week...\n")

    for feed_info in feeds:
        url = feed_info['url']
        print(f"Processing: {url}")

        entries = fetch_feed(url)
        formatted = format_feed_output(url, entries)
        all_results.append(formatted)

    # Combine all results
    final_output = "\n\n".join(all_results)

    return final_output

if __name__ == "__main__":
    news = get_weekly_news()
    print("\n" + news)

    # Optionally save to file
    with open('weekly_news.txt', 'w', encoding='utf-8') as f:
        f.write(news)
    print("\n\nResults saved to weekly_news.txt")
