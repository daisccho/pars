import telebot
import pymysql
import time
import parser_volga
from text_parser import parse_text
from datetime import datetime
from config import *
from summa import *
from syn import *

bot = telebot.TeleBot(bot_hash)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Данный бот может отправлять новостную ленту с сайта volganet.net')

    text_global = ''

    @bot.message_handler(commands=['news'])
    def send_news(message):
        bot.send_message(message.chat.id, 'Хотите подписаться на новостную рассылку?')

        @bot.message_handler(content_types=['text'])
        def response(message):
            if message.text.lower() == 'да':
                bot.send_message(message.chat.id, 'Отлично! Теперь вы подписаны на новостную ленту нашего сайта.')
                parser_volga.db_update()
                sub_date = datetime.today()
                while True:
                    try:
                        connection = pymysql.connect(
                            host=host,
                            port=3306,
                            user=user,
                            password=password,
                            database=db_name,
                            cursorclass=pymysql.cursors.DictCursor
                        )
                        print("#" * 20)
                        print(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
                        print("Successfully connected")
                        print("#" * 20)

                        try:
                            with connection.cursor() as cursor:
                                query = "select * from `news` where `date` > '" + str(
                                    sub_date) + "' order by `date` desc limit 1;"
                                cursor.execute(query)
                                q = cursor.fetchall()
                                if len(q) != 0:
                                    print("Has an update! Transmitting...")
                                    id = q[0]['id']
                                    title = q[0]['title']
                                    text = q[0]['text']
                                    text_global = text
                                    href = q[0]['href']
                                    date = q[0]['date']
                                    list_n = []
                                    list_d = []
                                    list_n, list_d = parse_text(text)
                                    text_pers = ''
                                    for item in list_n:
                                        text_pers = text_pers + item + '\n'
                                    text_land = ''
                                    for item in list_d:
                                        text_land = text_land + item + '\n'
                                    print(q[0])
                                    bot.send_message(message.chat.id,
                                                     '<b>' + title + '</b>' + '\n\n' + text + '\n\n' + href + '\n\n' + text_pers + text_land,
                                                     parse_mode='html')
                                    bot.send_message(message.chat.id, '<b>Переделанная новость:</b>' + '\n\n' +
                                                     '<b>' + summarize_text(title) + '</b>' + '\n\n' + paraphrase_text(
                                        text) + '\n\n' + href + '\n\n' + text_pers + text_land + '\n\n' + analyze_sentiment(
                                        text),
                                                     parse_mode='html')
                                    dateStr = date.strftime("%Y-%m-%d %H:%M:%S")
                                    sub_date = dateStr
                                    print(str(id) + " Successfully transmitted to: " + str(message.chat.id))
                                    print("New sub date to " + str(message.chat.id) + " is " + sub_date)
                                else:
                                    print("No updates, skipping...")

                        finally:
                            connection.close()
                            print("#" * 20)
                            print(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
                            print("Disconnected")
                            print("#" * 20)

                    except Exception as ex:
                        print(datetime.today().strftime("%Y-%m-%d %H:%M:%S") + " Failed to connect")
                        print(ex)

                    time.sleep(600)


bot.infinity_polling()
