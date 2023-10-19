from modeules.mongodb import MongoDBConnector
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

mongo_connector = MongoDBConnector()
user_rating_collection = mongo_connector.get_collection('user_rating')
item_based_collection = mongo_connector.get_collection('drama_similarity_item_based')

def item_based_rec():
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
    item_based_collection.drop()
    documents_to_insert = []
    batch_size = 10000
    for drama_pair, rating_pairs in drama_pair_ratings.items():
        if len(rating_pairs) < 2:
            continue
        v1 = np.array([rating_pair[0] for rating_pair in rating_pairs]).reshape(1, -1)
        v2 = np.array([rating_pair[1] for rating_pair in rating_pairs]).reshape(1, -1)
        similarity_matrix = cosine_similarity(v1, v2)
        similarity = similarity_matrix[0, 0]
        item_based_similarity = {
            "drama1_id": drama_pair[0],
            "drama2_id": drama_pair[1],
            "similarity": similarity
        }
        documents_to_insert.append(item_based_similarity)

        if len(documents_to_insert) == batch_size:
            item_based_collection.insert_many(documents_to_insert)
            documents_to_insert = []
            print("Successfully inserted into Mongodb")
    if documents_to_insert:
        item_based_collection.insert_many(documents_to_insert)
        print("Done")