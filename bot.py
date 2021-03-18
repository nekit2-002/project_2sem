import telebot
import requests
from requests.exceptions import HTTPError
#import schedule
#import pycron
import time

requests.get('https://api.github.com')
bot = telebot.TeleBot("1644508993:AAHywAyEf6dPbbVM57Hz0xsimAA8rfG5zWg")
name = ''
surname = ''
age = 0
@bot.message_handler(content_types=['text'])



def greeting(message):
    if message.text == 'Привет':
        bot.send_message(message.from_user.id, "Привет чем я могу тебе помочь?")
        connect(message)
    elif message.text == 'Статья':
        start(message)
    elif message.text== '/help':
        help(message)
    else:
        bot.send_message(message.from_user.id, 'Напиши /help')
def help(message):
        bot.send_message(message.from_user.id, "Напиши Привет чтобы бот ответил приветствием")
        bot.send_message(message.from_user.id, "Напиши Статья чтобы дать информацию о себе")


def start(message):
        bot.send_message(message.from_user.id, "Как тебя зовут?")
        bot.register_next_step_handler(message, get_name) #следующий шаг – функция get_name

def get_name(message): #получаем фамилию
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id,'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)
def get_age(message):
    global age
    age= int(message.text)
    bot.send_message(message.from_user.id, 'Тебе ' + str(age) + ' лет, тебя зовут ' + name + ' ' + surname + '?')



def connect(message):
    for url in ['https://github.com/nekit2-002/project_2sem']:
        try:
            response = requests.get(url)

            # если ответ успешен, исключения задействованы не будут
            response.raise_for_status()
        except HTTPError as http_err:
            bot.send_message(message.from_user.id, f'HTTP error occurred: {http_err}')
        except Exception as err:
            bot.send_message(message.from_user.id,f'Other error occurred: {err}')
        else:
            bot.send_message(message.from_user.id, 'Успех')
        time.sleep(10)


    while True:
        connect(message)

bot.polling(none_stop=True, interval=0)
