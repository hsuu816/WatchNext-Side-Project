import os
import requests
from bs4 import BeautifulSoup
from mongodb import MongoDBConnector


# 連線mongodb
mongo_connect = MongoDBConnector('watchnext', 'drama')
collection = mongo_connect.get_collection()

drama_urls = []
def fetch_drama_url(page):
    url = f'https://movies.yahoo.com.tw/drama_intheaters.html?page={page}'
    print("URL:", url)
    try:
        r = requests.get(url)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')

        for drama in soup.select('ul.release_list li'):
            drama_url = drama.select_one('div.release_foto a')['href']
            drama_urls.append(drama_url)
            
    except Exception as e:
        print("ERROR:", url, e)

def fetch_drama_detail(drama_urls):
    for drama in drama_urls:
        r = requests.get(drama)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')
        image = soup.select_one('div.movie_intro_foto').find('img').get('src').strip()
        name = soup.select_one('div.movie_intro_foto').find('img').get('alt').strip()
        eng_name = soup.select_one('div.movie_intro_info_r').find('h3').text
        category_elements = soup.select('div.level_name_box div.level_name')
        if category_elements:
            categories = [element.text.strip() for element in category_elements]
        else:
            categories = []
        detail_elements = soup.select('div.movie_intro_info_r span')
        detail = [element.text.strip().replace(' ', '').replace('\n','') for element in detail_elements]
        platform = soup.select_one('div.evaluate_txt_finish').text.strip()
        description = soup.select_one('#story').text.strip()

        drama_dict = {
            "name": name,
            "eng_name": eng_name,
            "platform": platform,
            "categories": categories,
            "detail": detail,
            "description": description,
            "image": image
        }
        query = {"title": drama_dict["name"]}
        update_data = {"$set": drama_dict}
        result = collection.update_one(query, update_data, upsert=True)
        print(result)

for page in range(1):
    fetch_drama_url(page)
fetch_drama_detail(drama_urls)