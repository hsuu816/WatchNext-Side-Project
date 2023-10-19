import sys
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append('../app/server/models')
from mongodb import MongoDBConnector

# 連結到 Mongodb
mongo_connector = MongoDBConnector()
drama_collection = mongo_connector.get_collection('drama')
content_based_collection = mongo_connector.get_collection('drama_similarity_content_based')

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
drama_data = drama_collection.find({})
for drama in drama_data:
    detail_dict = {}
    drama_id = drama['_id']
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
    row = pd.DataFrame({'drama_id': [drama_id], 'country': [country_value], 'categories': [categories]})

    df = pd.concat([df, row], ignore_index=True)

    df_drama = pd.get_dummies(df, columns=['country'], prefix='', dtype=int).join(df['categories'].str.join('|').str.get_dummies())
    df_drama = df_drama.drop(['categories'], axis=1)

df_drama.set_index('drama_id',inplace=True)
df = df_drama.drop(['_'], axis=1)
# print(df)

# cosine similarity
similarity_matrix = cosine_similarity(df)
similarity_matrix_df = pd.DataFrame(similarity_matrix, index=df.index, columns=df.index)
# print(similarity_matrix)

# 存入mongodb
documents_to_insert = []
batch_size = 10000
for i, row in enumerate(similarity_matrix):
    for j, similarity in enumerate(row):
        if i != j and similarity != 0:
            drama1_id = df.index[i]
            drama2_id = df.index[j]
            content_based_similarity = {
                "drama1_id": drama1_id,
                "drama2_id": drama2_id,
                "similarity": similarity
            }
            documents_to_insert.append(content_based_similarity)

            if len(documents_to_insert) == batch_size:
                content_based_collection.insert_many(documents_to_insert)
                documents_to_insert = []

if documents_to_insert:
    content_based_collection.insert_many(documents_to_insert)