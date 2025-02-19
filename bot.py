import time

from random import*

import telebot

import requests

import urllib.request

import json

import time
import requests
import threading
from flask import Flask

CR_TOKEN  = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjEzNDQ3Y2M3LWE0NDMtNDQ3OC05ZmM2LTRkYzA1YjgxZjk4YiIsImlhdCI6MTczOTk0NTg1NSwic3ViIjoiZGV2ZWxvcGVyLzIxZTg1YjhhLTYxNmYtYmRhYS0zMzNlLTE1NWI1ODI3OTBhNiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIzNS4xNjAuMTIwLjEyNiIsIjQ0LjIzMy4xNTEuMjciLCIzNC4yMTEuMjAwLjg1Il0sInR5cGUiOiJjbGllbnQifV19.N9JxImBP0qOqsUeVzbyVJ0jJi-f7dGDOO1lj5Hxp4AsZs3i2yJdk8M2JqZfE2uxh6j9WrrqG7aylk9vQnsimWg"

BASE_URL = "https://api.clashroyale.com/v1"

BOT_TOKEN = "5038305798:AAHtfwS9YpdVuUbT5zc5ee_1c-6wMhMa-GI"

CLAN_TAG = "#QUP0RL88"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

bot.delete_webhook()
time.sleep(1)

# 🔹 2. Створюємо Flask-сервер (щоб Render бачив відкритий порт)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Render потребує PORT
    app.run(host="0.0.0.0", port=port, debug=False)

# 🔹 3. Keep-Alive пінг (щоб Render не "вбивав" сервіс через неактивність)
def keep_alive():
    url = "https://твій-домен-на-render.com"  # Замінити на справжній Render URL
    while True:
        try:
            requests.get(url)
            print(f"✅ Пінг серверу успішний: {url}")
        except Exception as e:
            print(f"⚠️ Помилка пінгу: {e}")
        time.sleep(240)  # Пінг кожні 4 хвилини

# 🔹 4. Запускаємо Flask-сервер у фоновому потоці
threading.Thread(target=run_flask).start()

# 🔹 5. Запускаємо Keep-Alive пінг у фоновому потоці
threading.Thread(target=keep_alive).start()

u=list('')

headers = {
    "Authorization": f"Bearer {CR_TOKEN}",
    "Accept": "application/json"
}

data_file = "player_mapping.json"
try:
    with open(data_file, "r") as f:
        player_telegram_mapping = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    player_telegram_mapping = {}

def save_mappings():
    with open(data_file, "w") as f:
        json.dump(player_telegram_mapping, f)

def get_clan_war_info():
    url = f"{BASE_URL}/clans/{CLAN_TAG.replace('#', '%23')}/currentriverrace"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_clan_members():
    url = f"{BASE_URL}/clans/{CLAN_TAG.replace('#', '%23')}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("memberList", [])
    return []



@bot.message_handler(commands=['log'])
def log_player(message):
    try:
        _, player_tag, tg_nick = message.text.split()
        player_telegram_mapping[player_tag] = tg_nick
        save_mappings()
        bot.reply_to(message, f"✅ {player_tag} прив'язано до {tg_nick}")
    except ValueError:
        bot.reply_to(message, "❌ Невірний формат. Використовуйте /log #тегГравця @нік")


@bot.message_handler(commands=['remove'])
def remove_player(message):
    try:
        _, player_tag = message.text.split()
        if player_tag in player_telegram_mapping:
            del player_telegram_mapping[player_tag]
            save_mappings()
            bot.reply_to(message, f"✅ {player_tag} видалено зі списку")
        else:
            bot.reply_to(message, "❌ Гравець не знайдений у списку")
    except ValueError:
        bot.reply_to(message, "❌ Невірний формат. Використовуйте /remove #тегГравця")


@bot.message_handler(commands=['topclans'])
def top_clans_status(message):
    data = get_clan_war_info()
    if not data:
        bot.reply_to(message, "Не вдалося отримати дані про війну кланів.")
        return

    standings = data.get("clans", [])
    top_clans = sorted(standings, key=lambda x: x.get("fame", 0), reverse=True)[:5]

    response_text = "🏆 Топ 5 кланів у річній гонці:\n"
    for idx, clan in enumerate(top_clans, 1):
        battles_played = clan.get("battlesPlayed", 1)
        battles_won = clan.get("wins", 0)
        win_rate = (battles_won / battles_played) * 100 if battles_played else 0
        remaining_attacks = sum(
            p.get("decksAvailable", 4) - p.get("decksUsedToday", 0) for p in clan.get("participants", []))
        response_text += f"{idx}. {clan['name']} - {clan['fame']} очок\n"
        response_text += f"   🏅 Середній вінрейт: {win_rate:.2f}%\n"
        response_text += f"   ⚔️ Залишилось атак: {remaining_attacks}\n"

    bot.reply_to(message, response_text)


@bot.message_handler(commands=['clanplayers'])
def all_players_status(message):
    members = get_clan_members()
    war_data = get_clan_war_info()
    participants = war_data.get("clans", []) if war_data else []
    our_clan = next((clan for clan in participants if clan["tag"] == CLAN_TAG), None)

    response_text = "📋 Список гравців у клані:\n"
    if our_clan:
        war_participants = {p["tag"]: p for p in our_clan.get("participants", [])}
        for member in members:
            player_tag = member["tag"]
            decks_used = war_participants.get(player_tag, {}).get("decksUsedToday", 0)
            decks_available = war_participants.get(player_tag, {}).get("decksAvailable", 4)
            response_text += f"{member['name']} - {player_tag} | Атак залишилось: {decks_available - decks_used}\n"
    else:
        for member in members:
            response_text += f"{member['name']} - {member['tag']}\n"

    bot.reply_to(message, response_text)


@bot.message_handler(commands=['unplayedtag'])
def unplayed_tag(message):
    data = get_clan_war_info()
    if not data:
        bot.reply_to(message, "Не вдалося отримати дані про війну кланів.")
        return

    our_clan = next((clan for clan in data.get("clans", []) if clan["tag"] == CLAN_TAG), None)
    if our_clan:
        participants = our_clan.get("participants", [])
        clan_members = {member["tag"] for member in get_clan_members()}

        unplayed = [
            p for p in participants
            if p.get("decksUsedToday", 0) < p.get("decksAvailable", 4) and p["tag"] in clan_members
        ]

        mentions = []
        for player in unplayed:
            tg_nick = player_telegram_mapping.get(player["tag"], None)
            if tg_nick and tg_nick.startswith("@"):
                mentions.append(tg_nick)

        if mentions:
            bot.reply_to(message, "🔔 Гравці, які ще не зіграли:\n" + " ".join(mentions))
        else:
            bot.reply_to(message, "✅ Всі гравці зіграли свої атаки.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
   bot.reply_to(message, "Do you want to discover who are you in the gym? \n If you do not khown what to do write me /help")

@bot.message_handler(commands=['help'])
def send_welcome(message):
   bot.reply_to(message, "List of command: \n /discover \n /clanplayers \n /topclans \n /help \n /list \n /ask \n /lastres \n /unplayedtag" )

@bot.message_handler(commands=['yes'])
def send_welcome(message):
   bot.reply_to(message, "You are a good person")

@bot.message_handler(commands=['list'])
def send_welcome(message):
   bot.reply_to(message, "List of participants in gym: \n fucking slave \n jabroni \n leatherman \n bot of the gym \n dungeon master \n gachiman \n mayor gachiman \n full master \n boss of the gym \n King: \n       Billy Herrington")

@bot.message_handler(commands=['no'])
def send_welcome(message):
   bot.reply_to(message, "Fuck your mother and your father")

@bot.message_handler(commands=['discover'])
def send_welcome(message):
   n = randint(1, 10000)

   b = ('You are')

   if n < 1000:
      time.sleep(0.5)
      b += (' fucking slave')
      g=('Your last rank: \n fucking slave')
      u.clear()
      u.append(g)
   elif n < 2000:
      time.sleep(0.5)
      b += (' jabroni')
      g = ('Your last rank: \n jabroni')
      u.clear()
      u.append(g)
   elif n < 3000:
      time.sleep(0.5)
      b += (' leatherman')
      g = ('Your last rank: \n leatherman')
      u.clear()
      u.append(g)
   elif n < 4000:
      time.sleep(0.5)
      b += (' bot of the gym')
      g = ('Your last rank: \n bot of the gym')
      u.clear()
      u.append(g)
   elif n < 5000:
      time.sleep(0.5)
      b += (' dungeon master')
      g = ('Your last rank: \n dungeon master')
      u.clear()
      u.append(g)
   elif n < 6000:
      time.sleep(0.5)
      b += (' gachiman')
      g = ('Your last rank: \n gachiman')
      u.clear()
      u.append(g)
   elif n < 7000:
      time.sleep(0.5)
      b += (' mayor gachiman')
      g = ('Your last rank: \n mayor gachiman')
      u.clear()
      u.append(g)
   elif n < 8000:
      time.sleep(0.5)
      b += (' full master')
      g = ('Your last rank: \n full master')
      u.clear()
      u.append(g)
   elif n < 9000:
      time.sleep(0.5)
      b += (' boss of the gym')
      g = ('Your last rank: \n boss of the gym')
      u.clear()
      u.append(g)
   else:
      time.sleep(0.1)
      b += (' Billy Herrington')
      g = ('Your last rank: \n Billy Herrington')
      u.clear()
      u.append(g)
   bot.reply_to(message, b)

@bot.message_handler(commands=['dicktest'])
def send_welcome(message):
    n = str(randint(1, 15))

    b = ('Твій dick = ')

    d= 'см'

    g = "\nМаєш файний BIG dick"

    c = b + n + d + g

    bot.reply_to(message, c)

@bot.message_handler(commands=['test'])
def send_welcome(message):
   bot.reply_to(message, "write /ask if you want a secret question")

@bot.message_handler(commands=['ask'])
def send_welcome(message):
   bot.reply_to(message, "do you love gym? /yes or /no")

@bot.message_handler(commands=['lastres'])
def send_welcome(message):
    for i in u:
        bot.reply_to(message, i)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)


bot.infinity_polling()  # Запускає бота
