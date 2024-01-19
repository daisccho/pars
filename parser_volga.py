import pymysql
import requests
import time
from bs4 import BeautifulSoup
from config import *
from datetime import datetime

url = "https://volganet.net/category/aktualno/page/"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36"
}


def db_update():
    try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Successfully connected")
        print("#" * 20)

        try:
            tries = 0
            for i in range(1, 350):
                try:
                    print(url + str(i))
                    req = requests.get(url + str(i), headers=headers)
                    get = req.text
                    with open("doc.html", "w", encoding="utf-8") as file:
                        file.write(get)

                except Exception as ex:
                    print("Parsing failed")
                    print(ex)

                with open("doc.html", encoding="utf-8") as file:
                    src = file.read()

                soup = BeautifulSoup(src, "lxml")
                all_news = soup.find_all(class_="entry-body")
                for item in all_news:
                    article_href = item.find('h3').find('a').get("href")

                    if tries >= 15:
                        print('DB is up to date, stopping...')
                        return

                    with connection.cursor() as cursor:
                        query = "SELECT count(*) as count FROM `news` WHERE `href` LIKE '" + article_href + "';"
                        cursor.execute(query)
                        res = cursor.fetchall()
                        count = res[0]['count']

                    if count > 0:
                        print(str(time.localtime(time.time()).tm_hour) + ":" + str(
                            time.localtime(time.time()).tm_min) + ":" + str(
                            time.localtime(time.time()).tm_sec) + ": " + article_href + ": Already exists")
                        tries += 1
                        continue

                    else:
                        tries = 0
                        req_news = requests.get(article_href)
                        soup = BeautifulSoup(req_news.text, "lxml")

                        article_title = soup.find('h1', class_='g1-mega').text
                        article_date = soup.find(class_="entry-date")
                        article_date_obj = datetime.strptime(article_date.text, "%d.%m.%Y, %H:%M")
                        req = requests.get(article_href, headers=headers)
                        get = req.text
                        soup = BeautifulSoup(get, "lxml")
                        news = soup.find(class_="entry-content g1-typography-xl").find_all('p')
                        news_text = ''
                        for item in news:
                            news_text += item.text
                            news_text += " "

                        with connection.cursor() as cursor:
                            if count == 0:
                                insert_query = "INSERT INTO `news` (`title`, `date`, `text`, `href`) VALUES ('" + article_title + "', '" + str(
                                    article_date_obj) + "', '" + news_text + "', '" + article_href + "');"
                                cursor.execute(insert_query)
                                connection.commit()
                                print(str(time.localtime(time.time()).tm_hour) + ":" + str(
                                    time.localtime(time.time()).tm_min) + ":" + str(
                                    time.localtime(time.time()).tm_sec) + ": " + article_href + ": Successful")

        finally:
            connection.close()

    except Exception as ex:
        print("Failed to connect")
        print(ex)

db_update()