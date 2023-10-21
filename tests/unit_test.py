import sys
from bs4 import BeautifulSoup
import time
import pytest
from unittest.mock import MagicMock
from unittest.mock import ANY

sys.path.append('../airflow/modules')
from ptt_crawler_daily import *

def test_get_article_urls():
    test_url = 'https://www.ptt.cc/bbs/China-Drama/index.html'
    article_urls, soup = get_article_urls(test_url)

    assert isinstance(article_urls, list)
    assert isinstance(soup, BeautifulSoup)

def test_get_article_content():
    test_url = 'https://www.ptt.cc/bbs/EAseries/M.1697817293.A.3F0.html'
    article_data = get_article_content(test_url)

    assert isinstance(article_data, dict)
    assert isinstance(article_data["comments_list"], list)

@pytest.fixture
def magic_mock_collection():
    return MagicMock()

def test_insert_to_mongo(magic_mock_collection):
    article_data = {
        "title": "Test Title",
        "release_time": "2023-01-01 12:00:00",
        "content": "Test Content",
        "comments_list": ["Comment 1", "Comment 2"],
        "url": "https://www.example.com",
    }

    insert_to_mongo(article_data, magic_mock_collection)

    magic_mock_collection.update_one.assert_called_once_with(
        {
            "source": "PTT",
            "title": "Test Title",
            "release_time": "2023-01-01 12:00:00"
        },
        {
            "$set": {
                "source": "PTT",
                "title": "Test Title",
                "release_time": "2023-01-01 12:00:00",
                "content": "Test Content",
                "comments": ["Comment 1", "Comment 2"],
                "comments_count": 2,
                "url": "https://www.example.com",
                "create_time": ANY
            }
        },
        upsert=True
    )

def test_get_next_page_url():
    html = """
    <html>
        <body>
            <a href="/next_page">‹ 上頁</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, 'html.parser')

    result = get_next_page_url(soup)

    assert result == "https://www.ptt.cc//next_page"