import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
from mongodb import MongoDBConnector

# 連線mongodb
mongo_connect = MongoDBConnector('watchnext', 'comment')
collection = mongo_connect.get_collection()

# 獲取文章連結
def get_all_articles(url):
    while url:
        r = requests.get(url)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')
        articles = soup.select('div.title')

        for article in articles:
            if article.a: # 跳過被刪除的文章
                page_url = "https://www.ptt.cc" + article.a['href']
                get_articles_detail(page_url)

        next_page_link = soup.find("a", string="‹ 上頁")
        if next_page_link and "disabled" not in next_page_link.get("class", []):
            url = "https://www.ptt.cc/" + next_page_link["href"]
            print(url)
            time.sleep(0.1)
        else:
            url = None
            print('Done')

# 獲取文章內容並插入mongo db
def get_articles_detail(url):
    r = requests.get(url)
    web_content = r.text
    soup = BeautifulSoup(web_content, 'html.parser')
    main_content = soup.select_one('#main-content')
    article_info = main_content.select('span.article-meta-value')
    if len(article_info) >= 4:
        title = article_info[2].text
        original_time = article_info[3].text
        time_parts = original_time.split()
        if len(time_parts) >= 5:
            time_str = " ".join(time_parts[1:5])  # 只取時間
            time_struct = datetime.strptime(time_str, "%b %d %H:%M:%S %Y")
            release_time = time_struct.strftime("%Y-%m-%d %H:%M:%S")
        else:
            release_time = ""
    else:
        title = ""
        release_time = ""
    all_text = main_content.text
    pre_texts = all_text.split("--")[:-1]
    one_text = "--".join(pre_texts)
    texts = one_text.split('\n')[1:]
    content = "\n".join(texts)
    comments = main_content.select('div.push')
    comments_list = []
    for comment in comments:
        push_element = comment.select_one('span.push-content')
        if push_element:
            push_content = push_element.text.strip(": ")
            comments_list.append(push_content)
        else:
            push_content = ""

    article_dict = {
        "source": "PTT",
        "title": title,
        "release_time": release_time,
        "content": content,
        "comments": comments_list,
        "comments_count": len(comments_list)
    }
    query = {
        "source":article_dict["source"],
        "title": article_dict["title"],
        "release_time": article_dict["release_time"]
        }
    
    update_data = {"$set": article_dict}
    result = collection.update_one(query, update_data, upsert=True)
    print(result)
    print(title, release_time)

article_urls = get_all_articles('https://www.ptt.cc/bbs/China-Drama/index.html')
