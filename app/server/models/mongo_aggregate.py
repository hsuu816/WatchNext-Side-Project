from bson import ObjectId

def drama_detail(id):
    drama_comment = [
        {
            "$match": {
                "_id": ObjectId(id)
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
                "_id": 1,
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

def content_based_rec_drama(id):
    content_based_rec_drama = [
        {"$match": {"drama1_id": ObjectId(id)}},
        {"$sort": { "similarity": -1 }},
        {"$limit": 4},
        {"$lookup": {
            "from": "drama",
            "localField": "drama2_id",
            "foreignField": "_id",
            "as": "detail"
            }
        },
        {"$project": {
            "_id": 0,
            "detail": {
                "_id": 1,
                "name": 1,
                "image": 1
                }
            }
        }
    ]
    return content_based_rec_drama

def user_rating_drama(user_id):
    user_rating_drama = [
        {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "drama",
            "localField": "drama_id",
            "foreignField": "_id",
            "as": "drama_data"
            }
        },
        {"$project": {
            "user_id":1,
            "drama_id": 1,
            "rating": 1,
            "create_time": 1,
            "drama_data":{"name":1,"image":1}
            }
        },
        {"$sort": {"create_time": -1}}
        ]
    return user_rating_drama

def similarity_user_like(user_id):
    similarity_user_like = [
        {"$match": {
            "user_id": user_id, 
            "rating": {"$in": [4, 5]}
            }
        },
        {"$lookup": {
            "from": "drama",
            "localField": "drama_id",
            "foreignField": "_id",
            "as": "drama_data"
            }
        },
        {"$project": {
            "rating": 1,
            "drama_data": {"_id":1, "name": 1, "image": 1, "categories": 1}
            }
        }
        ]
    return similarity_user_like