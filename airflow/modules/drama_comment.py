from modules.mongodb import MongoDBConnector

# connect to mongodb
mongo_connector = MongoDBConnector()
comment_collection = mongo_connector.get_collection('comment')
drama_collection = mongo_connector.get_collection('drama')

def comment_to_drama():
    drama_data = drama_collection.find({})
    drama_list = []
    for drama in drama_data:
        drama_list.append(drama["name"])
    
    # Find comments that have not been tagged with drama name
    comment_data = comment_collection.find({"drama_name": {"$exists": False}})
    
    for comment in comment_data:
        title = comment["title"]
        for drama in drama_list:
            if drama in title:
                result = comment_collection.update_one({"_id": comment["_id"]}, {"$set": {"drama_name": drama}})
                print(result)