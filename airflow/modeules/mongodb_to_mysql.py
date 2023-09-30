from modeules.mongodb import MongoDBConnector
from modeules.mysql import MySQLConnector

# 連線mongodb
mongo_connect = MongoDBConnector('watchnext', 'drama')
collection = mongo_connect.get_collection()

mysql_db = MySQLConnector()
mysql_cursor = mysql_db.connect()

def mongodb_to_mysql():
    drama_data = collection.find({})
    for drama in drama_data:
        name = drama['name']
        insert_sql = "INSERT IGNORE INTO drama(name) VALUES (%s);"
        mysql_cursor.execute(insert_sql, name)
        print(f"{name}insert into mysql success.")
    mysql_db.disconnect()