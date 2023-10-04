import os
from dotenv import load_dotenv
import pandas as pd

import pymysql
from pymongo import MongoClient

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

# 連結到 Mongodb
password = os.getenv('mongo_password')
conn = MongoClient(f"mongodb+srv://hsuu816:{password}@watchnext.edwg2oq.mongodb.net/")
mongo_db = conn.watchnext
collection = mongo_db.drama

mapping = {
    '播出日期': 'date',
    '總集數': 'episode',
    'IMDb分數': 'imdb_score',
    '國家/地區': 'country',
    '編劇': 'screenwriter',
    '演員': 'actor',
    '導演': 'director',
    '製作公司': 'company'
}

# 整理drama的特徵屬性
df = pd.DataFrame()
drama_data = collection.find({})
for drama in drama_data:
    detail_dict = {}
    name = drama['name']
    categories = drama['categories']
    detail = drama['detail']
    for item in detail[1:]:
        key, value = item.split('：',1)
        eng_key = mapping.get(key, key)
        detail_dict[eng_key] = value

    # 在嘗試訪問值之前檢查字典中是否存在這個鍵
    date_value = detail_dict.get('date', '')
    country_value = detail_dict.get('country', '')

    # 創建一個包含 'Name'、'episode' 和 'imdb_score' 列的 DataFrame
    row = pd.DataFrame({'name': [name], 'country': [country_value], 'categories': [categories]})

    df = pd.concat([df, row], ignore_index=True)

    df_drama = pd.get_dummies(df, columns=['country'], prefix='', dtype=int).join(df['categories'].str.join('|').str.get_dummies())
    df_drama = df_drama.drop(['categories'], axis=1)

# 對照drama name & drama id
sql = """
    SELECT *
    FROM watchnext.drama
    ORDER BY id
"""
with connection.cursor() as cursor:
    cursor.execute(sql)
    result = cursor.fetchall()
    df_id = pd.DataFrame(result, columns=['drama_id', 'name'])

df = pd.merge(df_id, df_drama, on='name')
df = df.drop(['_'], axis=1)
df = df.drop(['name'], axis=1)
df.set_index('drama_id',inplace=True)

# cosine similarity
similarity_matrix = cosine_similarity(df)
similarity_matrix_df = pd.DataFrame(similarity_matrix, index=df.index, columns=df.index)
# print(similarity_matrix)

# 將similarity_matrix整理成存入mysql的tuple形式
similarity_tuples = []
for i, row in enumerate(similarity_matrix):
    for j, similarity in enumerate(row):
        if i != j :  # 只需要前半段matrix
            drama1_id = df.index[i]
            drama2_id = df.index[j]
            similarity_tuples.append((drama1_id, drama2_id, similarity))
# print(similarity_tuples)

# 存入mysql
insert_similarity_sql = """
    INSERT INTO drama_similarity_content_based (drama1_id, drama2_id, similarity)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE similarity = VALUES(similarity);
"""
with connection.cursor() as cursor:
    cursor.executemany(insert_similarity_sql, similarity_tuples)
    connection.commit()
connection.close()