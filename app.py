from flask import Flask, render_template, jsonify
import urllib.parse

from models.mongodb import MongoDBConnector
from models.mongo_aggregate import *

app = Flask(__name__)

# 連線mongodb
mongo_connect = MongoDBConnector('watchnext', 'drama')
drama_collection = mongo_connect.get_collection()


@app.route('/', methods=['GET'])
def get_drama():
    # 從mongodb中擷取資料
    drama_data = drama_collection.find({}).limit(20)
    hot_drama_data = drama_collection.aggregate(hot_drama())
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
    return render_template('detail.html', dramas=drama_detail_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')