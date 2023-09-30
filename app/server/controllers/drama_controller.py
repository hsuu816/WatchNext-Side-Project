from flask import render_template, jsonify
from flask_login import current_user
from sqlalchemy.dialects.mysql import insert
import urllib.parse
from server import app, db
from server.models.mongodb import MongoDBConnector
from server.models.mongo_aggregate import hot_drama, drama_detail, recommend_same_category_drama

from server.models.mysql_drama import Drama, DramaScore

# 連線mongodb
mongo_connect_comment = MongoDBConnector('watchnext', 'comment')
comment_collection = mongo_connect_comment.get_collection()
mongo_connect_drama = MongoDBConnector('watchnext', 'drama')
drama_collection = mongo_connect_drama.get_collection()


@app.route('/', methods=['GET'])
def get_drama():
    # 從mongodb中擷取資料
    drama_data = drama_collection.find({}).limit(20)
    hot_drama_data = comment_collection.aggregate(hot_drama())
    return render_template('index.html', dramas=drama_data, hot_drama=hot_drama_data)

@app.route('/api/v1/category/<category>', methods=['GET'])
def category_select(category):
    encoded_category = urllib.parse.unquote(category)
    drama_data = list(drama_collection.find({"categories": encoded_category}, {"_id": 0}).limit(20))
    return jsonify({"dramas": drama_data})


@app.route('/api/v1/detail/<name>',  methods=['GET'])
def get_drama_detail(name):
    encoded_name = urllib.parse.unquote(name)
    drama_detail_data = list(drama_collection.aggregate(drama_detail(encoded_name)))
    if drama_detail_data[0]["categories"]:
        category = drama_detail_data[0]["categories"][0] # 先只取一個類型標籤
    else:
        category = ""
    recommend_drama = drama_collection.aggregate(recommend_same_category_drama(category, encoded_name))
    if current_user.is_authenticated:
        user_id = current_user.id
        drama_id = Drama.find_id_by_name(name)
        score = DramaScore.find_score_by_ids(user_id, drama_id)
    return render_template('detail.html', dramas=drama_detail_data, recommend_drama=recommend_drama, score=score)

@app.route('/api/v1/score/<string:drama_name>/<int:score>', methods=['POST'])
def score(drama_name, score):
    if current_user.is_authenticated:
        user_id = current_user.id
        drama_id = Drama.find_id_by_name(drama_name)
        print(user_id, drama_id, score)
        # 存入資料庫
        stmt = insert(DramaScore).values(
            user_id=user_id,
            drama_id=drama_id,
            score=score
        )
        on_duplicate_key_stmt = stmt.on_duplicate_key_update(
            score=stmt.inserted.score,
            status='U'
            )

        try:
            db.session.execute(on_duplicate_key_stmt)
            db.session.commit()
        except Exception as e:
            # 處理例外情況
            print(f"Error: {e}")
            db.session.rollback()

    return jsonify({'score': score})