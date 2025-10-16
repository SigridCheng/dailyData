import os
import requests
import datetime
from dotenv import load_dotenv
import pytz
import time

# 加载环境变量
load_dotenv()

# 获取环境变量
NOTION_TOKEN = os.getenv("NOTION_TOKEN")  # 从环境变量中加载Token
DATABASE_ID = os.getenv("DATABASE_ID")  # 从环境变量中加载Database ID

# Notion API基础URL
NOTION_API_URL = "https://api.notion.com/v1/pages"

# 设置头部信息
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"  # 使用合适的Notion API版本
}

china_tz = pytz.timezone("Asia/Shanghai")
today_date = datetime.datetime.now(china_tz).strftime("%Y-%m-%d")

# 查询数据库，看看是否已经存在今天的页面
def check_existing_page():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    query_payload = {
        "filter": {
            "property": "Date",
            "date": {
                "equals": today_date
            }
        }
    }

    response = requests.post(url, json=query_payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if len(results) > 0:
            print(f"Page for {today_date} already exists.")
            return True  # 页面已存在
        else:
            print(f"No page found for {today_date}.")
            return False  # 页面不存在
    else:
        print(f"Failed to query database: {response.status_code}, {response.text}")
        return False

# 创建新页面
def create_page():
    url = NOTION_API_URL
    data = {
        "parent": {
            "database_id": DATABASE_ID
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": today_date
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": today_date
                }
            }
        }
    }

    response = requests.post(url, json=data, headers=headers)
    return response

# 带有重试机制的创建页面方法
def create_page_with_retry(retries=3, delay=2):
    attempt = 0
    while attempt < retries:
        response = create_page()
        if response.status_code == 200:
            print(f"Page created successfully for {today_date}.")
            return
        else:
            print(f"Attempt {attempt + 1} failed: {response.text}")
            attempt += 1
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)  # 等待一段时间后重试
            else:
                print("Max retry attempts reached. Failed to create page.")

# 主逻辑
def main():
    if not check_existing_page():
        create_page_with_retry()  # 创建页面时带有重试机制
    else:
        print("Page for today already exists.")

if __name__ == "__main__":
    main()
