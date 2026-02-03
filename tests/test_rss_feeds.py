"""Tests for RSS feed parsing functionality."""

import sys
from pathlib import Path
from datetime import datetime, timezone

# Add workflows directory to path so we can import rss_feeds
sys.path.insert(0, str(Path(__file__).parent.parent / "workflows"))

import rss_feeds


class TestParseDateFunction:
    """Tests for the parse_date function."""

    def test_parse_rfc2822_format(self):
        """Verify RFC 2822 date parsing (RSS standard)."""
        date_str = "Mon, 15 Jan 2024 10:30:00 GMT"
        result = rss_feeds.parse_date(date_str)
        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_iso8601_with_z(self):
        """Verify ISO 8601 with Z suffix (Atom standard)."""
        date_str = "2024-01-15T10:30:00Z"
        result = rss_feeds.parse_date(date_str)
        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_iso8601_with_offset(self):
        """Verify ISO 8601 with timezone offset."""
        date_str = "2024-01-15T10:30:00-05:00"
        result = rss_feeds.parse_date(date_str)
        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_invalid_date_returns_none(self):
        """Verify None/empty/invalid dates return None."""
        assert rss_feeds.parse_date(None) is None
        assert rss_feeds.parse_date("") is None
        assert rss_feeds.parse_date("invalid date string") is None
        assert rss_feeds.parse_date("2024-99-99") is None


class TestGetFeedUrls:
    """Tests for the get_feed_urls function."""

    def test_returns_list(self):
        """Returns a list."""
        result = rss_feeds.get_feed_urls()
        assert isinstance(result, list)

    def test_has_ten_feeds(self):
        """Has exactly 10 feeds."""
        result = rss_feeds.get_feed_urls()
        assert len(result) == 10

    def test_each_item_has_url_key(self):
        """Each item is dict with 'url' key starting with https://."""
        result = rss_feeds.get_feed_urls()
        for item in result:
            assert isinstance(item, dict)
            assert "url" in item
            assert isinstance(item["url"], str)
            assert item["url"].startswith("https://")

    def test_no_duplicate_urls(self):
        """No duplicate URLs in list."""
        result = rss_feeds.get_feed_urls()
        urls = [item["url"] for item in result]
        assert len(urls) == len(set(urls))


class TestFormatFeedOutput:
    """Tests for the format_feed_output function."""

    def test_includes_feed_url_header(self):
        """Output includes feed URL header."""
        feed_url = "https://example.com/feed"
        entries = []
        result = rss_feeds.format_feed_output(feed_url, entries)
        assert "Feed: https://example.com/feed" in result

    def test_includes_entry_count(self):
        """Output includes entry count."""
        feed_url = "https://example.com/feed"
        entries = [
            {
                "title": "Test Entry 1",
                "date": "2024-01-15 10:00",
                "link": "https://example.com/entry1",
                "description": "Test description 1"
            },
            {
                "title": "Test Entry 2",
                "date": "2024-01-16 10:00",
                "link": "https://example.com/entry2",
                "description": "Test description 2"
            }
        ]
        result = rss_feeds.format_feed_output(feed_url, entries)
        assert "Entries found: 2" in result

    def test_formats_entry_fields(self):
        """Formats title, date, link, description correctly."""
        feed_url = "https://example.com/feed"
        entries = [{
            "title": "Test Article",
            "date": "2024-01-15 10:00",
            "link": "https://example.com/article",
            "description": "This is a test description"
        }]
        result = rss_feeds.format_feed_output(feed_url, entries)
        assert "Title: Test Article" in result
        assert "Date: 2024-01-15 10:00" in result
        assert "Link: https://example.com/article" in result
        assert "Description: This is a test description" in result

    def test_strips_html_from_description(self):
        """Removes HTML tags from descriptions."""
        feed_url = "https://example.com/feed"
        entries = [{
            "title": "Test Article",
            "date": "2024-01-15 10:00",
            "link": "https://example.com/article",
            "description": "<p>This is <strong>bold</strong> text with <a href='#'>a link</a></p>"
        }]
        result = rss_feeds.format_feed_output(feed_url, entries)
        assert "<p>" not in result
        assert "<strong>" not in result
        assert "<a href=" not in result
        assert "This is bold text with a link" in result

    def test_respects_max_chars_limit(self):
        """Truncates output at max_chars."""
        feed_url = "https://example.com/feed"
        entries = [{
            "title": "A" * 1000,
            "date": "2024-01-15 10:00",
            "link": "https://example.com/article",
            "description": "B" * 1000
        }]
        result = rss_feeds.format_feed_output(feed_url, entries, max_chars=500)
        assert len(result) <= 500

    def test_shows_truncation_message(self):
        """Shows truncation message when limit exceeded."""
        feed_url = "https://example.com/feed"
        entries = [{
            "title": "A" * 1000,
            "date": "2024-01-15 10:00",
            "link": "https://example.com/article",
            "description": "B" * 1000
        }]
        result = rss_feeds.format_feed_output(feed_url, entries, max_chars=500)
        assert "[Output truncated at" in result or len(result) == 500
