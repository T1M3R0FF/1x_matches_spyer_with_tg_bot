import telebot
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


token = "6919697012:AAGIm9cYVcAKt8kqxcdxJ6Yw7_RWIfnyryo"

bot = telebot.TeleBot(token)
sent_matches = {}


def stalkering():
    urls = [
        'https://1xstavka.ru/live/tennis/2377590-masters-russia-women',
        'https://1xstavka.ru/live/tennis/2377592-masters-russia',
        'https://1xstavka.ru/live/tennis/2377594-masters-pro-russia'
    ]
    info_pack = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        league_name = soup.find('div', class_='c-events__name').text.strip()
        if league_name in ['Мастерс. Россия', 'Мастерс. Россия. Женщины', 'Мастерс. Про. Россия']:
            all_matches = soup.find_all('div', class_='c-events-scoreboard__item')
            for match in all_matches:
                try:
                    link = "https://1xstavka.ru/" + match.find('a', class_='c-events__name')['href']
                    title = match.find('span', class_='c-events__teams').text.strip().split('\n')
                    score = match.find('div', class_='c-events-scoreboard__lines_tennis').text.replace('\n', '')
                    score = score.replace('(', ' ').replace(')', ' ').rstrip().split()
                    del score[1]
                    del score[2]
                    score = ''.join(score)
                    if score == '00':
                        match_key = f"{title[0]}-{title[1]}"
                        if match_key not in sent_matches:
                            msg = f"В текущем матче счет 0-0:\n{title[0]}-{title[1]}\n{link}"
                            info_pack.append(msg)
                            sent_matches[match_key] = datetime.now()  # Записываем время внесения матча
                except Exception:
                    continue
    return info_pack


def cleanup_sent_matches():
    current_time = datetime.now()
    for match_key, entry_time in list(sent_matches.items()):
        if (current_time - entry_time) > timedelta(hours=1):
            del sent_matches[match_key]


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Привет!\nС этого момента я буду присылать сюда информацию о только что стартовавших "
                     "матчах лиги Мастерс. Россия")

    while True:
        matches_list = stalkering()
        if matches_list:
            matches_string = '\n'.join(matches_list)
            print(matches_string)
            bot.send_message(message.chat.id, matches_string)
        cleanup_sent_matches()  # Очищаем старые матчи
        time.sleep(10)


bot.polling(non_stop=True)
