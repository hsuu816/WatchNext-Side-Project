from flask import render_template, jsonify, redirect, url_for
from flask_login import current_user
import urllib.parse
from bson import ObjectId, json_util
from datetime import datetime, timedelta
from server import app
from server.models.mongodb import MongoDBConnector
from server.models.mongo_aggregate import hot_drama, drama_detail, content_based_rec_drama, user_rating_drama, similarity_user_like


# 連線mongodb
mongo_connect_comment = MongoDBConnector('watchnext', 'comment')
comment_collection = mongo_connect_comment.get_collection()
mongo_connect_drama = MongoDBConnector('watchnext', 'drama')
drama_collection = mongo_connect_drama.get_collection()
mongo_connect_drama = MongoDBConnector('watchnext', 'user')
user_collection = mongo_connect_drama.get_collection()
mongo_user_rating = MongoDBConnector('watchnext', 'user_rating')
user_rating_collection = mongo_user_rating.get_collection()
mongo_connect_content_based = MongoDBConnector('watchnext', 'drama_similarity_content_based')
content_based_collection = mongo_connect_content_based.get_collection()
mongo_connect_user_based = MongoDBConnector('watchnext', 'drama_similarity_user_based')
user_based_collection = mongo_connect_user_based.get_collection()

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
        db.session.query(Drama.name, Drama.id, DramaScore.score)
        .join(DramaScore, DramaScore.drama_id == Drama.id)
        .filter(DramaScore.user_id == user_id)
        .all()
    )
    drama_list_name = [d[0] for d in rating_drama]
    drama_list_id = [d[1] for d in rating_drama]
    drama_score = {d[0]: d[2] for d in rating_drama}
    return drama_list_name, drama_list_id, drama_score



@app.route('/', methods=['GET'])
def get_drama():
    # 從mongodb中擷取資料
    drama_data = drama_collection.find({}).limit(100)
    hot_drama_data = list(comment_collection.aggregate(hot_drama(10, "2023-01-01 00:00:00")))
    return render_template('index.html', dramas=drama_data, hot_drama=hot_drama_data)

@app.route('/api/v1/category/<category>', methods=['GET'])
def category_select(category):
    encoded_category = urllib.parse.unquote(category)
    drama_data = list(drama_collection.find({"categories": encoded_category}))
    drama_data_json = json_util.dumps({"dramas": drama_data})
    return drama_data_json

@app.route('/api/v1/search/<keyword>', methods=['GET'])
def search(keyword):
    encoded_keyword = urllib.parse.unquote(keyword)
    drama_data = list(drama_collection.find({"name": {"$regex":encoded_keyword}}))
    drama_data_json = json_util.dumps({"dramas": drama_data})
    return drama_data_json

@app.route('/api/v1/detail/<id>',  methods=['GET'])
def get_drama_detail(id):
    drama_detail_data = list(drama_collection.aggregate(drama_detail(id)))
    recommend_drama = list(content_based_collection.aggregate(content_based_rec_drama(id)))

    rating = None
    if current_user.is_authenticated:
        print(current_user.id, id)
        user = user_rating_collection.find_one({"drama_id": ObjectId(id), "user_id": current_user.id})
        if user:
            rating = user.get("rating", {})
            print(rating)

    return render_template('detail.html', dramas=drama_detail_data, recommend_drama=recommend_drama, rating=rating)

@app.route('/api/v1/rating/<drama_id>/<int:rating>', methods=['POST'])
def rating(drama_id, rating):
    if current_user.is_authenticated:
        user_email = current_user.email
        user_id = current_user.id
        print(user_email, drama_id, rating, user_id)
        # 存入資料庫
        query = {"user_id": user_id, "drama_id": ObjectId(drama_id)}
        update_data = {
            "$set": {
                "rating": rating,
                "create_time": (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        user_rating_collection.update_one(query, update_data, upsert=True)
    return jsonify({'rating': rating})

@app.route('/member/recommendation', methods=['GET'])
def get_rating_drama():
    if current_user.is_authenticated:
        rating_drama_data = user_rating_collection.aggregate(user_rating_drama(current_user.id))

        user_based = user_based_collection.find_one({"user1_id": current_user.id}, sort=[("similarity", -1)])
        similarity_user_drama_data = None
        if user_based:
            similarity_user_id = user_based.get("user2_id")
            print(similarity_user_id)
            similarity_user_drama_data = user_rating_collection.aggregate(similarity_user_like(similarity_user_id))
        return render_template('member.html', dramas=rating_drama_data, rec_drama = similarity_user_drama_data)
    else:
        return redirect(url_for('get_drama'))