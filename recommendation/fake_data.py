import os
from dotenv import load_dotenv
import pymysql
import random

load_dotenv()

db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USERNAME'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_DATABASE'),
}

# 生成虛構資料
user_ids = [23, 24, 25, 26, 27, 28, 29, 30, 31]
drama_ids = list(range(1, 200))

# 連接到 MySQL
connection = pymysql.connect(**db_config)

try:
    with connection.cursor() as cursor:
        # 插入虛構評分資料
        for user_id in user_ids:
            # 隨機生成每個使用者評分的數量
            num_ratings = random.randint(30, 100)

            # 隨機選擇該使用者評分的劇
            selected_drama_ids = random.sample(drama_ids, num_ratings)

            for drama_id in selected_drama_ids:
                score = random.randint(1, 5)
                sql = "INSERT INTO drama_score (user_id, drama_id, score) VALUES (%s, %s, %s)"
                cursor.execute(sql, (user_id, drama_id, score))
                connection.commit()
finally:
    # 關閉連接
    connection.close()
