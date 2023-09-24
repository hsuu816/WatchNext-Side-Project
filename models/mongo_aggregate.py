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
    return hot_drama