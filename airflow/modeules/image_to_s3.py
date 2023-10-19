from mongodb import MongoDBConnector
import boto3
from bs4 import BeautifulSoup
import requests
from io import BytesIO
import time

# 連線mongodb
mongo_connector = MongoDBConnector()
drama_collection = mongo_connector.get_collection('drama')

# 連線至s3
try:
    s3 = boto3.client('s3')
except:
    print("Error connecting to S3")

drama_data = drama_collection.find({"image": {"$not": {"$regex": "https://watchnext.s3.ap-southeast-2.amazonaws.com"}}})
drama_list = []
for drama in drama_data:
    drama_name = drama['name']
    drama_eng_name = drama['eng_name']
    drama_list.append([drama_name, drama_eng_name])
print(drama_list)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# 上傳圖片到 S3
def upload_s3(image, name):
    try:
        # 上傳圖片至 S3 Buckets，並設定
        image_key = f"drama_images/{name}"
        s3.upload_fileobj(image, 'watchnext', image_key, ExtraArgs={'ContentType': 'image/png', 'ACL': 'public-read'})

        # 產生圖片URL
        image_url = f"https://watchnext.s3.ap-southeast-2.amazonaws.com/{image_key}"
        return image_url
    except Exception as e:
        print(f"Error uploading image to S3: {str(e)}")
        return None

# 更改mongodb內圖片網址
def change_mongo_img_url(name, img_url):
    result = drama_collection.update_one({"name": name}, {"$set": {"image": img_url}})
    print(result)

for drama in drama_list:
    name = drama[0]
    eng_name = drama[1]
    url = f'https://www.imdb.com/find/?q={eng_name}=nv_sr_sm'
    r = requests.get(url, headers=headers)
    web_content = r.text
    soup = BeautifulSoup(web_content, 'html.parser')
    drama_div = soup.select_one('div.ipc-metadata-list-summary-item__tc a')
    if drama_div is not None:
        url = drama_div['href']
        drama_url = "https://www.imdb.com/" + url
        print(drama_url)
        r = requests.get(drama_url, headers=headers)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')
        img = soup.select_one('div.ipc-media img')['srcset']
        if img is not None:
            image_url = img.split(', ')[-1].split(' ')[0]
            print(image_url)
            response = requests.get(image_url)
            if response.status_code == 200:
                image_bytes = BytesIO(response.content)
                new_img_url = upload_s3(image_bytes, name)
                change_mongo_img_url(name, new_img_url)
                time.sleep(2)

    else:
        print(f"URL not found: {drama}")
    


