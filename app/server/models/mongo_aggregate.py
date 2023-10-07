def drama_detail(name):
    drama_comment = [
        {
            "$match": {
                "name": name  # 只匹配指定的 name
            }
        },
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
            "$project":{
                "_id": 0
            }
        }
    ]
    return drama_comment


def hot_drama(limit, release_time):
    hot_drama = [
        {
            "$match": {
                "release_time":{
                    "$gt": release_time
                    }
                }
  
        },
        {
            "$group": {
                "_id": "$drama_name",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": { "count": -1 }
        },
        {
            "$skip":1
        },
        {
            "$limit": limit
        },
        {
            "$lookup": {
                "from": "drama",
                "localField": "_id",
                "foreignField": "name",
                "as": "detail"
            }
        },
        {
            "$project": {
              "_id": 0,
              "count": 1,
              "detail": {
                "name": 1,
                "image": 1,
                "categories": 1
                }
            }
        }
    ]
    return hot_drama

def recommend_same_category_drama(category, name):
    recommend_same_category_drama = [
        {
            "$match": {
            "categories": category,
            "name": { "$ne": name }
            }
        },
        {
            "$limit": 50
        },
        {
            "$lookup": {
            "from": "comment",
            "localField": "name",
            "foreignField": "drama_name",
            "as": "comment"
            }
        },
        {
            "$project": {
            "name": 1,
            "image": 1,
            "comment_count": { "$size": "$comment" }
            }
        },
        {
            "$sort": {"comment_count": -1}
        },
        {
            "$limit": 4
        }
]
    return recommend_same_category_drama