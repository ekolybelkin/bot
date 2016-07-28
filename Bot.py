import telebot
import json # Представляет словарь в строку
import os # Для проверки на существование файла
import requests # Для осуществления запросов
import urllib # Для загрузки картинки с сервера
from io import BytesIO # Для отправки картинки к пользователю
import time # Представляет время в читаемый формат
 
bot = telebot.TeleBot('235338226:AAF0fd_MmM3VzwsOuHwOGTmRBwd_Jr0FCuo')
 
app_id = "5559823"
 
users = {}
 
users_dump = "base.json" # Название файла для сохранения базы
 
link = "https://oauth.vk.com/authorize?\
client_id=%s&display=mobile&scope=friends,wall,offline&response_type=token&v=5.45" %app_id
 
def process_item(message, text=None, attachment=None, date=None, *args, **kwargs):
    if attachment:
        typeof = attachment.get("type", False)
        if typeof == "photo":
            file = urllib.request.urlopen(attachment["photo"]["src_big"])
            raw_bytes = BytesIO(file.read()) # Байты картинки
            raw_bytes.name = "photo.png"
            bot.send_photo(message.chat.id, raw_bytes) # Отправить фото адресату
            # Закрыть соединение
            file.close()
            raw_bytes.close()
        elif typeof == "link":
            # Если вложение - ссылка, то просто отпралвляем
            bot.send_message(message.chat.id, "%s|%s" %(attachment["link"]["url"], attachment["link"]["title"]))
    bot.send_message(message.chat.id, time.strftime("%d.%m.%y %X", time.gmtime(date)))
    if text:
        # Отправить текст
        for partial in telebot.util.split_string(text.replace("<br>", "\n"), 3000):
            bot.send_message(message.chat.id, partial) # Отправляем частями
            time.sleep(2)
        bot.send_message(message.chat.id, "-----------------------------------------") # Разделитель
            
if os.path.isfile(users_dump):
    with open(users_dump, 'r') as base:
        users = json.loads(base.read()) # Загрузка данных из файла
 
@bot.message_handler(commands=['start'])
def start(message):
    users[str(message.chat.id)] = False
    bot.reply_to(message, 'Привет, ' + message.from_user.first_name)
 
@bot.message_handler(commands=['help'])
def Help(message):
    bot.reply_to(message, "Чтобы бот заработал надо сделать следующее: \n \
                 1. Переидти по ссылке %s \n \
                 2. Авторизироваться и дать права приложению \n \
                 3. Скопировать из адресной строки token (будет выглядеть так access_token=ваш_токен) \n \
                 4. Отправить сообщение боту /token ваш_токен" %link)
 
@bot.message_handler(commands=['token'])
def setToken(message):
    stringToken = message.text.split("/token ")
    try:
        users[str(message.chat.id)] = stringToken[1]
        with open(users_dump, 'w') as base:
            base.write(json.dumps(users))
        bot.reply_to(message, "Установка token успешно завершена!") # Если всё хорошо
    except:
        bot.reply_to(message, "Установка token обернулась ошибкой!") # Если ошибка
 
@bot.message_handler(commands=['feed'])
def getFeed(message):
    #Оповещение для отладки
    print("Пользователь %s запросил ленту" %message.from_user.username)
    stringToken = users.get(str(message.chat.id), False) # Получаем token
    # Если token установлен
    if stringToken:
        response = requests.get("https://api.vk.com/method/newsfeed.get?count=5&access_token=%s" %stringToken)
        if response.status_code == 200:
            newsfeed = json.loads(response.text).get("response", False)
            if not newsfeed:
                bot.send_message(message.chat.id, "Запрос вернул некорректные данные. Детали: %s" %response.text)
            else:
                for item in newsfeed["items"]:
                    # Если не пост, то пропускаем
                    if item["type"] != "post":
                        continue
                    # Разборка вложения
                    attachment = item.get("attachment") # Если одно вложение
                    attachments = item.get("attachments") # Если несколько вложений
                    if attachment:
                        process_item(message, text=item.get("text"), attachment=attachment, date=item.get("date"))
                    elif attachments:
                        for attachment in attachments:
                            process_item(message, text=item.get("text"), attachment=attachment, date=item.get("date"))
                    else:
                        process_item(message, text=item.get("text"), date=item.get("date"))
                    time.sleep(5)
        else:
            bot.send_message(message.chat.id, "Ошибка при получении ленты. Проверьте token. Детали: %s" %response.text)
    else:
        Help(message)
        
 
@bot.message_handler(commands=['curToken'])
def curToken(message):
    stringToken = users.get(str(message.chat.id), False)
 
    if stringToken:
        bot.reply_to(message, stringToken) # Отвечает текущим token
 
    else:
        bot.reply_to(message, "Token не установлен") # Если нет token
 
 
 
bot.polling()
