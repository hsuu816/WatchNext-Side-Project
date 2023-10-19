import sys
import pandas as pd
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append('../app/server/models')
from mongodb import MongoDBConnector

# 連結到 Mongodb
mongo_connector = MongoDBConnector()
user_rating_collection = mongo_connector.get_collection('user_rating')
user_based_collection = mongo_connector.get_collection('drama_similarity_user_based')

user_dramas = defaultdict(list)
user_rating_data = user_rating_collection.find({})
for rating_data in user_rating_data:
    user = rating_data['user_id']
    drama = rating_data['drama_id']
    rating  = rating_data['rating']
    user_dramas[drama].append((user, rating))

# 標準化
normalized_user_dramas = defaultdict(list)
for drama, users in user_dramas.items():
    rating_sum = sum([user[1]for user in users])
    rating_count = len(users)
    rating_avg = rating_sum / rating_count
    for user in users:
        normalized_user_dramas[drama].append((user[0], user[1] - rating_avg))

# 每部drama對不同使用者的評分配對
drama_pair_ratings = defaultdict(list)
for drama, users in normalized_user_dramas.items():
    for user_rating1 in users:
        for user_rating2 in users:
            if user_rating1[0] != user_rating2[0]:
                drama_pair_ratings[(user_rating1[0], user_rating2[0])].append((user_rating1[1], user_rating2[1]))             

# cosine similarity
similarity_tuples = []
for user_pair, rating_pairs in drama_pair_ratings.items():
    if len(rating_pairs) < 2:
        continue
    v1 = np.array([rating_pair[0] for rating_pair in rating_pairs]).reshape(1, -1)
    v2 = np.array([rating_pair[1] for rating_pair in rating_pairs]).reshape(1, -1)
    similarity_matrix = cosine_similarity(v1, v2)
    similarity = similarity_matrix[0, 0]
    query = {"user1_id": user_pair[0], "user2_id": user_pair[1]}
    update_data = {"$set": {"similarity": similarity}}
    user_based_collection.update_one(query, update_data, upsert=True)
