import os
import time
import requests
import logging
import telegram
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.DEBUG, 
    filename='homework.log', filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
Homework_url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)

def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] != 'approved':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'

def get_homeworks(current_timestamp):
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(Homework_url, headers=headers, params=params)
    return homework_statuses.json()

def send_message(message):
    logging.info('message sent')
    return bot.send_message(CHAT_ID, message)

def main():
    current_timestamp = int(time.time()) # Начальное значение timestamp  

    while True:
        try:
            homework = get_homeworks(current_timestamp).get('homeworks')
            if not homework:
                logging.info('I work, Im fine')
            else:
                send_message(parse_homework_status(homework[0]))
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            send_message(f'Бот упал с ошибкой: {e}')
            logging.error(e, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    logging.debug('starting bot')
    main()
