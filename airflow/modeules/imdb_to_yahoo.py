import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import gzip
from io import BytesIO
from modeules.mongodb import MongoDBConnector

# 連線mongodb
mongo_connect = MongoDBConnector('watchnext', 'drama')
collection = mongo_connect.get_collection()

def imdb_yahoo_match(year):
    data = requests.get('https://datasets.imdbws.com/title.basics.tsv.gz')
    compressed_data = BytesIO(data.content)
    with gzip.open(compressed_data, 'rt', encoding='utf-8') as gzipped_file:
        header = gzipped_file.readline().strip().split('\t')
        for line in gzipped_file:
            # 拆分每一行成欄位
            fields = line.strip().split('\t')

            # 確保欄位數量與標頭行一致
            if len(fields) != len(header):
                continue

            # 建立欄位名稱到值的映射
            record = dict(zip(header, fields))

            # 如果 'types' 欄位的值是 'tv'，則處理這條記錄
            if record['titleType'] == 'tvSeries' and record['startYear'] == year:
                drama_name = record['primaryTitle']
                max_chars = 26
                if len(drama_name) > max_chars:
                # 捨去最後一個詞
                    truncated_name = drama_name[:max_chars].rsplit(' ', 1)[0]
                else:
                    truncated_name = drama_name
                url = f'https://movies.yahoo.com.tw/moviesearch_result.html?movie_type=drama&keyword={truncated_name}'
                r = requests.get(url)
                web_content = r.text
                soup = BeautifulSoup(web_content, 'html.parser')

                if soup.select('ul.release_list li'):
                    for drama in soup.select('ul.release_list li'):
                        drama_link = drama.select_one('div.release_foto a')
                        if drama_link is not None and 'href' in drama_link.attrs:
                            drama_url = drama_link['href']
                            print(drama_url)

                            r = requests.get(drama_url)
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
                                "image": image,
                                "url": drama_url,
                                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            query = {"name": drama_dict["name"]}
                            update_data = {"$set": drama_dict}
                            result = collection.update_one(query, update_data, upsert=True)
                            print(result)
                            print(name)
                            time.sleep(5)