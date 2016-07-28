# ekolybelkin bot
"""
Мой первый бот

"""


import telebot

import constants

bot = telebot.TeleBot(constants.token)






@bot.message_handler(content_types=["text"])
def handler_text(message):
    if message.text == "привет бот":


        bot.send_message(message.chat.id, "Привет друг!")


    elif message.text == "бот что делаешь?":


        bot.send_message(message.chat.id, "Слушаю с Женей Татушек!")


    elif message.text == "ботя ты в порядке?":
        answer = "Естественно!"

        bot.send_message(message.chat.id, "Естественно!")
        log(message, answer)



bot.polling(none_stop=True, interval=0)