import os
from dotenv import load_dotenv
import pymysql
from pymongo import MongoClient
import random
from datetime import datetime
from bson import ObjectId
load_dotenv()

# 連結到 Mongodb
password = os.getenv('mongo_password')
conn = MongoClient(f"mongodb+srv://hsuu816:{password}@watchnext.edwg2oq.mongodb.net/")
mongo_db = conn.watchnext
drama_collection = mongo_db.drama
item_based_collection = mongo_db.drama_similarity_item_based
user_rating_collection = mongo_db.user_rating


def fake_data(user_ids, categories):
    dramas = drama_collection.find({}).limit(1000)
    drama_id_list = [drama['_id'] for drama in dramas]

    # 插入虛構評分資料
    for user_id in user_ids:
        # 隨機生成每個使用者評分的數量
        num_ratings = random.randint(100, 300)

        # 隨機選擇該使用者評分的劇
        selected_drama_ids = random.sample(drama_id_list, num_ratings)

        for drama_id in selected_drama_ids:
            drama = drama_collection.find_one({"_id": drama_id})
            if drama['categories']:
                drama_category = drama['categories'][0]
            else:
                drama_category = 'null'
            if drama_category in categories:
                min_rating, max_rating = 4, 5
            else:
                min_rating, max_rating = 1, 3
            
            rating = random.randint(min_rating, max_rating)

            query = {"user_id": ObjectId(user_id), "drama_id": drama_id}
            update_data = {
                "$set": {
                    "rating": rating,
                    "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            user_rating_collection.update_one(query, update_data, upsert=True)
            print(drama['name'], drama_category, rating)



fake_data(['6523ba16ab99ecb70f8ec834', '6523ba24ab99ecb70f8ec835'], ['恐怖','懸疑/驚悚', '犯罪'])
fake_data(['6523ba55ab99ecb70f8ec836', '6523ba5fab99ecb70f8ec837'], ['愛情','溫馨/家庭'])
fake_data(['6523ba68ab99ecb70f8ec838', '6523ba71ab99ecb70f8ec839'], ['動畫'])
fake_data(['6523ba97ab99ecb70f8ec83a', '6523baa3ab99ecb70f8ec83b'], ['冒險', '武俠'])
fake_data(['6523baadab99ecb70f8ec83c', '6523babcab99ecb70f8ec83d'], ['科幻'])
