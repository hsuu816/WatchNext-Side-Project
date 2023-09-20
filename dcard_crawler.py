from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from datetime import datetime
import undetected_chromedriver as uc
from mongodb import MongoDBConnector

# 連線mongodb
mongo_connect = MongoDBConnector('watchnext', 'comment')
collection = mongo_connect.get_collection()

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--log-level=3") # 設置 log 級別為 WARNING
user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/117.0.5938.89 Safari/537.36"
)
chrome_options.add_argument(f"user-agent={user_agent}") 

def get_url(url):
    # 使用 undetected_chromedriver 初始化 Chrome 瀏覽器
    driver = uc.Chrome()
    driver.get(url)

    # 等待頁面載入
    sleep(5)

    all_urls = set()
    while len(all_urls) < 100:
        wait = WebDriverWait(driver, 10)
        articles = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))

        # 提取文章的連結
        for article in articles:
            url = article.find_element(By.TAG_NAME, "a").get_attribute("href")
            all_urls.add(url)
            # print(url)

        # 滾動加載更多頁面
        for i in range(2):
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            sleep(2)
    driver.quit()
    return all_urls

def get_articles_detail(urls_set):
    for url in urls_set:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        sleep(3)
        wait = WebDriverWait(driver, 10)
        sleep(3)
        title = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "atm_w6_1hnarqo"))).text
        original_time = wait.until(EC.presence_of_element_located((By.XPATH, "//time"))).get_attribute("datetime")
        time_struct = datetime.strptime(original_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        release_time = time_struct.strftime("%Y-%m-%d %H:%M:%S")
        comments_list = []
        comment_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "atm_vv_1btx8ck")))
        content = comment_elements[0].text
        for i in range(10):
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            comment_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "atm_vv_1btx8ck")))
            for element in comment_elements[1:]:
                if element.text not in comments_list:
                    comments_list.append(element.text)
            sleep(2)
        driver.quit()
        article_dict = {
            "source": "Dcard",
            "title": title,
            "release_time": release_time,
            "content": content,
            "comments": comments_list,
            "comments_count": len(comments_list)
        }
        query = {
        "source":article_dict["source"],
        "title": article_dict["title"],
        "release_time": article_dict["release_time"]
        }
    
        update_data = {"$set": article_dict}
        result = collection.update_one(query, update_data, upsert=True)
        print(result)
        print(title, release_time)


all_urls = get_url('https://www.dcard.tw/f/kr_drama?tab=latest')
print(all_urls)
get_articles_detail(all_urls)