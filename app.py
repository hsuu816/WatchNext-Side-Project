from flask import Flask, render_template, jsonify
from mongodb import MongoDBConnector
import urllib.parse

app = Flask(__name__)

# 連線mongodb
mongo_connect = MongoDBConnector('watchnext', 'drama')
drama_collection = mongo_connect.get_collection()

drama_comment = [
    {
        "$lookup": {
            "from": "comment",
            "localField": "name",
            "foreignField": "drama_name",
            "as": "comments",
            "pipeline": [
                {
                    "$project": {
                        "_id": 0,
                        "drama_name": 0
                    }
                }
            ]
        }
    },
    {
        "$limit": 20  # 限制數量
    }
]

hot_drama = [
    {
        "$lookup": {
            "from": "comment",
            "localField": "name",
            "foreignField": "drama_name",
            "as": "comments"
        }
    },
    {
        "$project": {
            "_id": 0,
            "name": 1,
            "image":1,
            "comment_count": { "$size": "$comments" } # 計算評論數
        }
    },
    {
        "$sort": { "comment_count": -1 } # 依照評論多到少排序
    },
    {
        "$limit": 10  # 只顯示前十名
    }
]


@app.route('/', methods=['GET'])
def get_drama():
    # 從mongodb中擷取資料
    drama_data = drama_collection.aggregate(drama_comment)
    hot_drama_data = drama_collection.aggregate(hot_drama)
    return render_template('index.html', dramas=drama_data, hot_drama=hot_drama_data)

@app.route('/api/v1/category/<category>', methods=['GET'])
def category_select(category):
    encoded_category = urllib.parse.unquote(category)
    drama_data = list(drama_collection.find({"categories": encoded_category}, {"_id": 0}).limit(20))
    return jsonify({"dramas": drama_data})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')