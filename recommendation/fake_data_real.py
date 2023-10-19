import sys
import random
from datetime import datetime
from bson import ObjectId

sys.path.append('../app/server/models')
from mongodb import MongoDBConnector

# 連結到 Mongodb
mongo_connector = MongoDBConnector()
drama_collection = mongo_connector.get_collection('drama')
user_rating_collection = mongo_connector.get_collection('user_rating')


def fake_data(user_ids, categories):
    dramas = drama_collection.find({})
    drama_id_list = [drama['_id'] for drama in dramas]
    categories_set = set(categories)

    # 插入虛構評分資料
    for user_id in user_ids:
        # 隨機生成每個使用者評分的數量
        num_ratings = random.randint(100, 300)

        # 隨機選擇該使用者評分的劇
        selected_drama_ids = random.sample(drama_id_list, num_ratings)

        for drama_id in selected_drama_ids:
            drama = drama_collection.find_one({"_id": drama_id})
            if drama['categories']:
                drama_category = drama['categories']
                drama_category_set = set(drama_category)
            else:
                drama_category = 'null'
            if drama_category_set.intersection(categories_set):
                min_rating, max_rating = 3, 5
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



fake_data(['6523ba16ab99ecb70f8ec834', '6523ba24ab99ecb70f8ec835', '6528b7f892cdc554b58eb138'], ['恐怖','懸疑/驚悚', '犯罪'])
fake_data(['6523ba55ab99ecb70f8ec836', '6523ba5fab99ecb70f8ec837', '6528b80c92cdc554b58eb139'], ['愛情','溫馨/家庭'])
fake_data(['6523ba68ab99ecb70f8ec838', '6523ba71ab99ecb70f8ec839', '6528b82b92cdc554b58eb13a'], ['動畫'])
fake_data(['6523ba97ab99ecb70f8ec83a', '6523baa3ab99ecb70f8ec83b', '6528b84192cdc554b58eb13b'], ['冒險', '武俠'])
fake_data(['6523baadab99ecb70f8ec83c', '6523babcab99ecb70f8ec83d', '6528b85692cdc554b58eb13c'], ['科幻'])
fake_data(['6527945092cdc554b58eb129', '6527945d92cdc554b58eb12a', '6528b86a92cdc554b58eb13d'], ['喜劇', '愛情'])
fake_data(['6527946992cdc554b58eb12b', '6527947892cdc554b58eb12c', '6528b90e92cdc554b58eb13e'], ['劇情'])
fake_data(['6527948392cdc554b58eb12d', '6527948d92cdc554b58eb12e', '6528b92592cdc554b58eb13f'], ['奇幻'])
fake_data(['6527949e92cdc554b58eb12f', '652794ac92cdc554b58eb130', '6528b93692cdc554b58eb140'], ['勵志', '紀錄片'])
fake_data(['652794be92cdc554b58eb131', '652794cf92cdc554b58eb132', '6528b94792cdc554b58eb141'], ['動畫'])
fake_data(['652794dc92cdc554b58eb133', '6528b95c92cdc554b58eb142', '6525239f92cdc554b58eb122'], ['恐怖'])
fake_data(['6528b66092cdc554b58eb134', '6528b67492cdc554b58eb135', '6528b97192cdc554b58eb143'], ['戰爭', '冒險'])
fake_data(['6528b68892cdc554b58eb136', '6528b69692cdc554b58eb137', '6528b98392cdc554b58eb144'], ['音樂/歌舞', '喜劇'])