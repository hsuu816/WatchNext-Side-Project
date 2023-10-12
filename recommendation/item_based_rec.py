import os
from dotenv import load_dotenv
import pandas as pd
from collections import defaultdict
import numpy as np
from pymongo import MongoClient

from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# 連結到 Mongodb
password = os.getenv('mongo_password')
conn = MongoClient(f"mongodb+srv://hsuu816:{password}@watchnext.edwg2oq.mongodb.net/")
mongo_db = conn.watchnext
drama_collection = mongo_db.drama
user_rating_collection = mongo_db.user_rating
item_based_collection = mongo_db.drama_similarity_item_based

user_dramas = defaultdict(list)
user_rating_data = user_rating_collection.find({})
for rating_data in user_rating_data:
    user = rating_data['user_id']
    drama = rating_data['drama_id']
    rating  = rating_data['rating']
    user_dramas[user].append((drama, rating))
# print(user_dramas)

# 標準化
normalized_user_dramas = defaultdict(list)
for user, dramas in user_dramas.items():
    rating_sum = sum([drama[1]for drama in dramas])
    rating_count = len(dramas)
    rating_avg = rating_sum / rating_count
    for drama in dramas:
        normalized_user_dramas[user].append((drama[0], drama[1] - rating_avg))
# print(normalized_user_dramas)

# 每位使用者對不同drama間的評分配對
drama_pair_ratings = defaultdict(list)
for user, dramas in normalized_user_dramas.items():
    for drama_rating1 in dramas:
        for drama_rating2 in dramas:
            if drama_rating1[0] != drama_rating2[0]:
                drama_pair_ratings[(drama_rating1[0], drama_rating2[0])].append((drama_rating1[1], drama_rating2[1]))
# print(drama_pair_ratings)              

# cosine similarity
similarity_tuples = []
for drama_pair, rating_pairs in drama_pair_ratings.items():
    if len(rating_pairs) < 2:
        continue
    v1 = np.array([rating_pair[0] for rating_pair in rating_pairs]).reshape(1, -1)
    v2 = np.array([rating_pair[1] for rating_pair in rating_pairs]).reshape(1, -1)
    similarity_matrix = cosine_similarity(v1, v2)
    similarity = similarity_matrix[0, 0]
    query = {"drama1_id": drama_pair[0], "drama2_id": drama_pair[1]}
    update_data = {"$set": {"similarity": similarity}}
    item_based_collection.update_one(query, update_data, upsert=True)