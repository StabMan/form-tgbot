import config #конфиг с токеном и айди чата
import sqlite3 # SQL
import telebot #библиотека бота
from telebot import types  #библиотека для кнопок
from string import Template #для нормальной работы формы
import time

bot = telebot.TeleBot(config.token)
conn = sqlite3.connect('ledo.db', check_same_thread=False)
#conn.row_factory = sqlite3.Row
cursor = conn.cursor()
user_dict = {}

def db_table_val(user_id: int, user_name: str):
    cursor.execute('INSERT or IGNORE INTO login (uid, name) VALUES (?, ?)', (user_id, user_name))
    conn.commit()
def get_answer(message):
    id, name = config.bd()
    bot.send_message(id, 'Здравствуйте, ' + name + ', ваша заявка была принята. '
'Теперь с вами будет работать @'+ config.leader)

class User:
    def __init__(self, problem):
        self.problem = problem

        keys = ['fullname', 'phone', 'email']

        for key in keys:
            self.key = None
# вызов команды /help, /start
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn1 = types.KeyboardButton('/about')
    itembtn2 = types.KeyboardButton('/form')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, "Здравствуйте, "
                     + message.from_user.first_name
                     + ", я бот, вы хотите заполнить заявку?"
                       "Тогда выберите вариант /form."
                       "\nИли если вам хочется узнать информацию обо мне, выберите /about", reply_markup=markup)
# кнопка /about
@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(message.chat.id, "Используя данного бота можно составить простую форму"
                                      + " и отправить ее, чтобы с вами смог связаться специалист")
# кнопка /form сама форма
@bot.message_handler(commands=["form"])
def user_data(message):
    config.idget(message)
    us_id = message.from_user.id
    if not message.from_user.username:
        us_name = message.from_user.first_name
    else:
        us_name = message.from_user.username
    db_table_val(user_id=us_id, user_name=us_name)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Необходим новый сайт')
    itembtn2 = types.KeyboardButton('Сломалось оборудование')
    itembtn3 = types.KeyboardButton('Надо обновить ПО')
    itembtn4 = types.KeyboardButton('Другая проблема')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    msg = bot.send_message(message.chat.id, 'Какая у вас проблема?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_problem_step)

def process_problem_step(message):
    chat_id = message.chat.id
    user_dict[chat_id] = User(message.text)
    markup = types.ReplyKeyboardRemove(selective=False)

    msg = bot.send_message(chat_id, 'ФИО', reply_markup=markup)
    bot.register_next_step_handler(msg, process_fullname_step)

def process_fullname_step(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.fullname = message.text

    msg = bot.send_message(chat_id, 'Номер телефона')
    bot.register_next_step_handler(msg, process_phone_step)

def process_phone_step(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.phone = message.text

    msg = bot.send_message(chat_id, 'Электронная почта')
    bot.register_next_step_handler(msg, process_end_step)

def process_end_step(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.email = message.text
    # формирование заявки
    bot.send_message(chat_id, getData(user, 'Ваша заявка сформирована, '
    '', message.from_user.first_name+'.'), parse_mode="Markdown")
    # пересылка в чат
    bot.send_message(config.chat_id, getData(user, 'Новая заявка от пользователя '
    '', message.from_user.username), parse_mode="Markdown")
    bot.register_next_step_handler(get_answer(message))
# форма заявки
def getData(user, title, name):
    t = Template(
        '$title *$name* \n ФИО: *$fullname* \n Телефон: *$phone* '
        '\n Электонная почта: *$email* \n Проблема: *$userProblem*')
    return t.substitute({
        'title': title,
        'name': name,
        'fullname': user.fullname,
        'phone': user.phone,
        'email': user.email,
        'userProblem': user.problem,
    })

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(1)
            print(e)