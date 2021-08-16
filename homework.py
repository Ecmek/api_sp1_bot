import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    result = {
        'approved': 'Ревьюеру всё понравилось, работа зачтена!',
        'rejected': 'К сожалению, в работе нашлись ошибки.',
        'reviewing': 'Работа принята на ревью',
    }
    homework_name = homework.get('homework_name')
    verdict = result.get(homework.get('status'))
    if not homework_name or not verdict:
        raise Exception(f'homework_name or status is None\n{homework}')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    homework_url = (
        'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    )
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            homework_url, headers=headers, params=params
        )
        return homework_statuses.json()
    except requests.exceptions.HTTPError as e:
        raise e


def send_message(message):
    logger.info(f'message sent: {message}')
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            response = get_homeworks(current_timestamp)
            homework = response.get('homeworks')
            current_timestamp = response.get('current_date')
            if not current_timestamp:
                current_timestamp = int(time.time())
            if not homework:
                logger.info('I work, Im fine')
            else:
                send_message(parse_homework_status(homework[0]))
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            send_message(f'Бот упал с ошибкой: {e}')
            logger.error(e, exc_info=True)
            time.sleep(60)


if __name__ == '__main__':
    logger.debug('starting bot')
    main()
