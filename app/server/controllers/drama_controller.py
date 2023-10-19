from flask import render_template, jsonify, redirect, url_for, request, abort
from flask_login import current_user
from flask_paginate import Pagination, get_page_parameter
import urllib.parse
import re
from bson import ObjectId, json_util
from datetime import datetime, timedelta
from server import app
from server.models.mongodb import MongoDBConnector
from server.models.mongo_aggregate import hot_drama, drama_detail, content_based_rec_drama, user_rating_drama, member_content_based_rec_drama, key_word_search


# 連線mongodb
mongo_connector = MongoDBConnector()
comment_collection = mongo_connector.get_collection('comment')
drama_collection = mongo_connector.get_collection('drama')
user_collection = mongo_connector.get_collection('user')
user_rating_collection = mongo_connector.get_collection('user_rating')
content_based_collection = mongo_connector.get_collection('drama_similarity_content_based')
item_based_collection = mongo_connector.get_collection('drama_similarity_item_based')


@app.route('/')
def get_drama():
    # 從mongodb中擷取資料
    page = request.args.get(get_page_parameter(), type=int, default=1)
    limit_value = 24
    offset_value=(24 * int(page)-24)
    total = drama_collection.count_documents({})
    pagination = Pagination(page=page, total=total, per_page=24)
    drama_data = drama_collection.find({}).skip(offset_value).limit(limit_value)
    hot_drama_data = list(comment_collection.aggregate(hot_drama(10)))
    return render_template('index.html', dramas=drama_data, hot_drama=hot_drama_data, pagination=pagination)

@app.route('/api/v1/category/<category>', methods=['GET'])
def category_select(category):
    encoded_category = urllib.parse.unquote(category)
    drama_data = list(drama_collection.find({"categories": encoded_category}))
    if not drama_data:
        abort(404)
    drama_data_json = json_util.dumps({"dramas": drama_data})
    return drama_data_json

@app.route('/api/v1/search/<keyword>', methods=['GET'])
def search(keyword):
    encoded_keyword = re.compile(urllib.parse.unquote(keyword), re.IGNORECASE)
    drama_data = list(drama_collection.find(key_word_search(encoded_keyword)))
    drama_data_json = json_util.dumps({"dramas": drama_data})
    return drama_data_json

@app.route('/api/v1/detail/<id>',  methods=['GET'])
def get_drama_detail(id):
    if not ObjectId.is_valid(id):
        abort(404)

    drama_detail_data = list(drama_collection.aggregate(drama_detail(id)))
    if not drama_detail_data:
        abort(404)
    recommend_drama = list(content_based_collection.aggregate(content_based_rec_drama(id)))

    rating = "尚未評分"
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
        user_rating = user_rating_collection.aggregate([{"$match": {"user_id": current_user.id, "rating": {"$in": [4, 5]}}}])
        rating_drama_list = [rating['drama_id'] for rating in user_rating]
        similarity_user_data = item_based_collection.aggregate(member_content_based_rec_drama(rating_drama_list, 20))
        similarity_user_data_list = list(similarity_user_data)
        similarity_user_data_len = len(similarity_user_data_list)
        similarity_user_drama_data = item_based_collection.aggregate(member_content_based_rec_drama(rating_drama_list, 20))

        return render_template('member.html', dramas=rating_drama_data, rec_drama = similarity_user_drama_data, similarity_user_data_len=similarity_user_data_len)
    else:
        return redirect(url_for('get_drama'))