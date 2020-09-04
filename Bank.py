import sqlite3
import time

import pip

pip install pyTelegramBotAPI

import telebot
import os
import re

# set current time to GMT+3
os.environ['TZ'] = 'Europe/Moscow'
time.tzset()

# define emoji to use
happy_emoji = ('\U0001F600', '\U0001F601', '\U0001F602', '\U0001F603',
               '\U0001F604', '\U0001F605', '\U0001F606', '\U0001F60A')
sad_emoji = ('\U0001F612', '\U0001F610', '\U0001F613', '\U0001F614',
             '\U0001F615', '\U0001F616', '\U0001F61E', '\U0001F61F')
angry_emoji = ('\U0001F620', '\U0001F62C', '\U0001F47F', '\U0001F624',
               '\U0001F480', '\U0001F621', '\U0001F620', '\U00002620')


def delete_tables():
  conn = sqlite3.connect('chat_bot.db')
  cur = conn.cursor()
  cur.execute('DROP TABLE IF EXISTS messages_1')
  cur.execute('DROP TABLE IF EXISTS session_1')
  conn.commit()

def create_tables():
  conn = sqlite3.connect('chat_bot.db')
  cur = conn.cursor()
  cur.execute('''CREATE TABLE IF NOT EXISTS messages_1 (
    message_id INTEGER,
    message_time TEXT,
    session_id INTEGER,
    message TEXT,
    client_id INTEGER

  )

  ''')

  cur.execute('''CREATE TABLE IF NOT EXISTS session_1 (
      session_id INTEGER PRIMARY KEY,
      ses_start TEXT,
      ses_end TEXT

  )

  ''')

  conn.commit()


# create chat_bot
bot = telebot.TeleBot('')

# commands
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
  if message.text == '/start':
    bot.send_message(message.from_user.id, 'Привет! Я могу реагировать на изменения в твоём настроении! '
                                           'Для начала новой сессии введи /start.')
    cur_time = time.strftime('%H %M %S')
    conn = sqlite3.connect('chat_bot.db')
    cur = conn.cursor()
    create_tables()
    cur.execute('INSERT INTO session_1 (ses_start) VALUES (?)', (cur_time,))
    conn.commit()

  elif message.text == '/help':
    bot.send_message(message.from_user.id, 'Чтобы я начал реагировать, введи смайлик (эмодзи).')

#bot reply
@bot.message_handler(content_types=['text'])
def reply(message):
  cur_time = time.strftime('%H %M %S')

  conn = sqlite3.connect('chat_bot.db')
  cur = conn.cursor()
  cur.execute("SELECT session_id FROM session_1 ORDER BY session_id DESC")
  (session, ) = cur.fetchone()
  cur.execute("INSERT INTO messages_1 (message_id, message_time, session_id, message, client_id) VALUES (?, ?, ?, ?, ?)", (message.message_id, cur_time, session, message.text, message.from_user.id))
  conn.commit()

  if bool(re.search('[а-яА-Я]', message.text)):
    bot.send_message(message.from_user.id, 'Я не понимаю')
    delete_tables()

  elif session == 1:
    if message.text in happy_emoji:
      bot.send_message(message.from_user.id, 'Ты такой весёлый!')

    elif message.text in sad_emoji:
      bot.send_message(message.from_user.id, 'Какой-то ты грустный(')

    elif message.text in angry_emoji:
      bot.send_message(message.from_user.id, 'Ух какой злой!')

  else:
    conn = sqlite3.connect('chat_bot.db')
    cur = conn.cursor()
    cur.execute("SELECT message FROM messages_1 ORDER BY message_time DESC LIMIT 1,1")
    (message_1, ) = cur.fetchone()
    print(type(message_1))
    if message.text in happy_emoji:

      if message_1 in happy_emoji:
        bot.send_message(message.from_user.id, 'Ничего не изменилось')
      elif message_1 in sad_emoji:
        bot.send_message(message.from_user.id, 'Тебе веселее!')
      elif message_1 in angry_emoji:
        bot.send_message(message.from_user.id, 'Хотя бы не такой злой')

    elif message.text in sad_emoji:

      if message_1 in happy_emoji:
        bot.send_message(message.from_user.id, 'Стало грустно')
      elif message_1 in sad_emoji:
        bot.send_message(message.from_user.id, 'Всё таже унылость')
      elif message_1 in angry_emoji:
        bot.send_message(message.from_user.id, 'Хотя бы не такой грустный')

    elif message.text in angry_emoji:

      if message_1 in happy_emoji:
        bot.send_message(message.from_user.id, 'Радость сменилась на злость')
      elif message_1 in sad_emoji:
        bot.send_message(message.from_user.id, 'Грусть сменилась на злость')
      elif message_1 in angry_emoji:
        bot.send_message(message.from_user.id, 'Всё так же злишься')

bot.polling()
