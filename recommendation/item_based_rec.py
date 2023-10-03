import os
from dotenv import load_dotenv
import pandas as pd
from collections import defaultdict
import numpy as np

import pymysql

from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# 連接到 MySQL
db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USERNAME'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_DATABASE'),
}
connection = pymysql.connect(**db_config)

sql = """
    SELECT user_id, drama_id, score
    FROM watchnext.drama_score
"""
with connection.cursor() as cursor:
    cursor.execute(sql)
    result = cursor.fetchall()

user_dramas = defaultdict(list)
for rating_data in result:
    user = rating_data[0]
    drama = rating_data[1]
    score = rating_data[2]
    user_dramas[user].append((drama, score))
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

        similarity_tuples.append((
            drama_pair[0],
            drama_pair[1],
            float(similarity)
        ))
# print(similarity_tuples)

# 存入mysql
insert_similarity_sql = """
    INSERT INTO drama_similarity_item_based (drama1_id, drama2_id, similarity)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE similarity = VALUES(similarity);
"""
with connection.cursor() as cursor:
    cursor.executemany(insert_similarity_sql, similarity_tuples)
    connection.commit()
connection.close()