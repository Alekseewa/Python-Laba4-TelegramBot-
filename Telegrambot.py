from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup as bs
import telebot
import requests
import os
import re
import logging

bot = telebot.TeleBot('241846034:AAEyQusHGpoh4xdlAIm1BysfcwIjElK8VBs')


@bot.message_handler(commands=['start'])
def SendInfo(message):
    bot.send_message(message.chat.id, 'Привет, друг. Чем я могу тебе помочь?')

@bot.message_handler(commands=['help'])
def SendHelp(message):
    bot.send_message(message.chat.id, "Список доступных команд: /start, /text, ")


@bot.message_handler(content_types='text')
def SendMessage(message):
    bot.send_message(message.chat.id,
                     "Подожди немного, скоро ты увидишь твою картинку. А пока подумай над тем, почему котики такие милые.")
    images = SearchGoogleImages(message.text, message.chat.id)
    for image in images:
        bot.send_photo(message.chat.id, open(image, 'rb'))


def SearchGoogleImages(query, id):
    path = os.path.abspath(os.curdir)
    path = os.path.join(path, str(id))

    if not os.path.exists(path):
        os.makedirs(path)

    query = query.split()
    query = '+'.join(query)
    query = 'https://www.google.ru/search?' \
            'q= ' + query + \
            '&newwindow=l' \
            '&source=lnms' \
            '&tbm=isch'

    req = requests.get(query, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/54.0.2840.99 Safari/537.36'})
    soup = bs(req.content, "html.parser")

    images = soup.find_all('img', {'data-src': re.compile('gstatic.com')})

    imagePaths = []
    for number, tag in enumerate(images[:10]):
        data = requests.get(tag['data-src'])
        image = Image.open(BytesIO(data.content))
        imagePath = os.path.join(path, str(number) + '.' + image.format.lower())
        image.save(imagePath)
        imagePaths.append(imagePath)

    return imagePaths


if __name__ == '__main__':
    logging.basicConfig(filename='botLog.log',
                        format='%(filename)s[LINE:%(lineno)d]# '
                               '%(levelname)-8s [%(asctime)s] '
                               '%(message)s',
                        level=logging.DEBUG)

    logging.info('Start the bot.')

    try:
        bot.polling(none_stop=True)
    except Exception:
        logging.critical('ERROR...')
    finally:
        bot.polling(none_stop=True)
