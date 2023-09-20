from flask import Flask, render_template
from mongodb import MongoDBConnector


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
    }
]


@app.route('/', methods=['GET'])
def get_drama():
    # 從mongodb中擷取資料
    drama_data = drama_collection.aggregate(drama_comment)
    return render_template('index.html', dramas=drama_data)

@app.route('/api/v1/category/<category>', methods=['GET'])
def category_select(category):
    drama_data = drama_collection.find({"categories": {"$eq":category}})
    return render_template('category.html', dramas=drama_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')