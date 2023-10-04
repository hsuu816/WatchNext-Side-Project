from flask import render_template, jsonify, redirect, url_for
from flask_login import current_user
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import not_
import urllib.parse
from server import app, db
from server.models.mongodb import MongoDBConnector
from server.models.mongo_aggregate import hot_drama, drama_detail
from server.models.mysql_drama import Drama, DramaScore, DramaSimilarityContentBased, DramaSimilarityItemBased


# 連線mongodb
mongo_connect_comment = MongoDBConnector('watchnext', 'comment')
comment_collection = mongo_connect_comment.get_collection()
mongo_connect_drama = MongoDBConnector('watchnext', 'drama')
drama_collection = mongo_connect_drama.get_collection()


# Content-based Recommendation
def find_content_based_rec(drama_name):
    drama = db.session.query(Drama).filter_by(name=drama_name).first()
    if drama:
        similar_dramas = (
            db.session.query(Drama.name)
            .join(DramaSimilarityContentBased, DramaSimilarityContentBased.drama2_id == Drama.id)
            .filter(DramaSimilarityContentBased.drama1_id == drama.id)
            .order_by(DramaSimilarityContentBased.similarity.desc())
            .limit(4)
            .all()
        )
        drama_list = [d[0] for d in similar_dramas]
        return drama_list
    else:
        return []
    
# Item-based Collaborative
def find_item_based_rec(drama_list_id):
    similar_dramas = (
        db.session.query(Drama.name)
        .join(DramaSimilarityItemBased, DramaSimilarityItemBased.drama2_id == Drama.id)
        .filter(
            DramaSimilarityItemBased.drama1_id.in_(drama_list_id),
            not_(DramaSimilarityItemBased.drama2_id.in_(drama_list_id))
            )
        .order_by(DramaSimilarityItemBased.similarity.desc())
        .limit(20)
        .all()
    )
    drama_list = [d[0] for d in similar_dramas]
    return drama_list

def find_user_rating_drama():
    user_id = current_user.id
    rating_drama = (
        db.session.query(Drama.name, Drama.id)
        .join(DramaScore, DramaScore.drama_id == Drama.id)
        .filter(DramaScore.user_id == user_id)
        .all()
    )
    drama_list_name = [d[0] for d in rating_drama]
    drama_list_id = [d[1] for d in rating_drama]
    return drama_list_name, drama_list_id



@app.route('/', methods=['GET'])
def get_drama():
    # 從mongodb中擷取資料
    drama_data = drama_collection.find({})
    hot_drama_data = comment_collection.aggregate(hot_drama())
    return render_template('index.html', dramas=drama_data, hot_drama=hot_drama_data)

@app.route('/api/v1/category/<category>', methods=['GET'])
def category_select(category):
    encoded_category = urllib.parse.unquote(category)
    drama_data = list(drama_collection.find({"categories": encoded_category}, {"_id": 0}))
    return jsonify({"dramas": drama_data})

@app.route('/api/v1/search/<keyword>', methods=['GET'])
def search(keyword):
    encoded_keyword = urllib.parse.unquote(keyword)
    drama_data = list(drama_collection.find({"name": {"$regex":encoded_keyword}}, {"_id": 0}))
    return jsonify({"dramas": drama_data})

@app.route('/api/v1/detail/<name>',  methods=['GET'])
def get_drama_detail(name):
    encoded_name = urllib.parse.unquote(name)
    drama_detail_data = list(drama_collection.aggregate(drama_detail(encoded_name)))
    rec_drama_list = find_content_based_rec(name)
    recommend_drama = drama_collection.find({"name":{'$in': rec_drama_list}})

    score = None
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

@app.route('/member/recommendation', methods=['GET'])
def get_rating_drama():
    if current_user.is_authenticated:
        drama_list_name, drama_list_id = find_user_rating_drama()
        rating_drama_data = drama_collection.find({"name":{'$in': drama_list_name}})
        rec_drama_data = find_item_based_rec(drama_list_id)
        rec_drama = drama_collection.find({"name":{'$in': rec_drama_data}})
        return render_template('member.html', dramas=rating_drama_data, rec_drama=rec_drama)
    else:
        return redirect(url_for('get_drama'))