from modeules.mongodb import MongoDBConnector

# 連線mongodb
mongo_connect_comment = MongoDBConnector('watchnext', 'comment')
comment_collection = mongo_connect_comment.get_collection()
mongo_connect_drama = MongoDBConnector('watchnext', 'drama')
drama_collection = mongo_connect_drama.get_collection()

def comment_to_drama():
    drama_data = drama_collection.find({})
    drama_list = []
    for drama in drama_data:
        drama_list.append(drama["name"])
    
    # 找出還沒有被貼戲劇標籤的評論
    comment_data = comment_collection.find({"drama_name": {"$exists": False}})
    
    for comment in comment_data:
        title = comment["title"]
        for drama in drama_list:
            if drama in title:
                result = comment_collection.update_one({"_id": comment["_id"]}, {"$set": {"drama_name": drama}})
                print(result)