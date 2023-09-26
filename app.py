from flask import Flask, render_template, jsonify
import urllib.parse

from models.mongodb import MongoDBConnector
from models.mongo_aggregate import *

app = Flask(__name__)

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
    return render_template('detail.html', dramas=drama_detail_data, recommend_drama=recommend_drama)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')