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


def hot_drama():
    hot_drama = [
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
            "$limit": 10
        },
        {
            "$lookup": {
                "from": "drama",
                "localField": "_id",
                "foreignField": "name",
                "as": "detail"
        }},
        {
            "$project": {
              "_id": 0,
              "count": 1,
              "detail": {
                "name":1,
                "image": 1
                }
            }
        }
    ]
    return hot_drama