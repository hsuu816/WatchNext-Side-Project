import requests
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from modules.mongodb import MongoDBConnector

# connect to mongodb
mongo_connector = MongoDBConnector()
comment_collection = mongo_connector.get_collection('comment')

# get ptt article urls
def get_article_urls(url):
    article_urls = []
    r = requests.get(url)
    web_content = r.text
    soup = BeautifulSoup(web_content, 'html.parser')
    articles = soup.select('div.title')

    for article in articles:
        if article.a: # skip deleted article
            page_url = "https://www.ptt.cc" + article.a['href']
            article_urls.append(page_url)
    return article_urls, soup


# get article content
def get_article_content(url):
    r = requests.get(url)
    web_content = r.text
    soup = BeautifulSoup(web_content, 'html.parser')
    main_content = soup.select_one('#main-content')
    article_info = main_content.select('span.article-meta-value')

    title = ""
    release_time = ""
    content = ""
    comments_list = []

    if len(article_info) >= 4:
        title = article_info[2].text
        original_time = article_info[3].text
        time_parts = original_time.split()
        if len(time_parts) >= 5:
            time_str = " ".join(time_parts[1:5])  # take only the time
            time_struct = datetime.strptime(time_str, "%b %d %H:%M:%S %Y")
            release_time = time_struct.strftime("%Y-%m-%d %H:%M:%S")

    all_text = main_content.text
    pre_texts = all_text.split("--")[:-1]
    one_text = "--".join(pre_texts)
    texts = one_text.split('\n')[1:]
    content = "\n".join(texts)

    comments = main_content.select('div.push')
    for comment in comments:
        push_element = comment.select_one('span.push-content')
        if push_element:
            push_content = push_element.text.strip(": ")
            comments_list.append(push_content)

    article_data = {
        "title": title,
        "release_time": release_time,
        "content": content,
        "comments_list": comments_list,
        "url": url
    }

    return article_data

# insert into mongodb
def insert_to_mongo(article_data, collection):
    article_dict = {
        "source": "PTT",
        "title": article_data["title"],
        "release_time": article_data["release_time"],
        "content": article_data["content"],
        "comments": article_data["comments_list"],
        "comments_count": len(article_data["comments_list"]),
        "url": article_data["url"],
        "create_time": (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    }

    query = {
        "source": article_dict["source"],
        "title": article_dict["title"],
        "release_time": article_dict["release_time"]
    }

    update_data = {"$set": article_dict}
    result = collection.update_one(query, update_data, upsert=True)
    print(article_data["title"], article_data["release_time"], len(article_data["comments_list"]))
    print(result)

# get the url of the next page
def get_next_page_url(soup):
    next_page_link = soup.find("a", string="‹ 上頁")
    if next_page_link and "disabled" not in next_page_link.get("class", []):
        return "https://www.ptt.cc/" + next_page_link["href"]
    return None

# daily run the ptt crawler
def fetch_ptt_comment_daily(url, pages):
    for _ in range(pages):
        article_urls, soup = get_article_urls(url)

        for article_url in article_urls:
            article_data = get_article_content(article_url)
            insert_to_mongo(article_data, comment_collection)

        next_page_url = get_next_page_url(soup)
        if next_page_url:
            url = next_page_url
            print(url)
            time.sleep(3)
        else:
            break

# crawler ptt all article
def fetch_all_ptt_comments(url):
    while url:
        article_urls, soup = get_article_urls(url)

        for article_url in article_urls:
            article_data = get_article_content(article_url)
            insert_to_mongo(article_data, comment_collection)

        next_page_url = get_next_page_url(soup)
        if next_page_url:
            url = next_page_url
            print(url)
            time.sleep(3)
        else:
            print('Done')
            break

if __name__ == "__main__":
    fetch_ptt_comment_daily('https://www.ptt.cc/bbs/China-Drama/index.html', 3)
    fetch_ptt_comment_daily('https://www.ptt.cc//bbs/KoreaDrama/index.html', 3)
    fetch_ptt_comment_daily('https://www.ptt.cc/bbs/Japandrama/index.html', 3)
    fetch_ptt_comment_daily('https://www.ptt.cc/bbs/TaiwanDrama/index.html', 3)
    fetch_ptt_comment_daily('https://www.ptt.cc/bbs/EAseries/index.html', 3)
