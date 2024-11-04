import telebot
from telebot import types

from flask import Flask, request
import os
from src.mail import send_email_with_attachment
from src.utils import get_date_object, get_today_date, get_result_message, all_passes_message, get_number,get_date_from_start_date
from src.word import make_pass
from src.excel import fill_cells, fill_cells_gen_act, fill_cells_notification_act
from datetime import datetime, date, timedelta
from src.database import create_new_pass, get_all_passes_db,get_formatted_last_id, get_last_id_gen_act, get_last_id_notification_act
from config import LOCAL_DEV_TOKEN
import atexit
import requests
import io



bot = telebot.TeleBot(token=LOCAL_DEV_TOKEN)
# server = Flask(__name__)
date_start = str
users = {}
naryad = {}
files = {}
gen_act = {}

cancel_btn = types.KeyboardButton('Скасувати') 


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    create_pass_btn = types.KeyboardButton('Створити пропуск')
    check_all_passes = types.KeyboardButton('Переглянути всі дійсні пропуски')
    create_naryad = types.KeyboardButton('Створити наряд')
    create_gen_act_but = types.KeyboardButton('Створити ген акт')

    markup.add(create_pass_btn)
    markup.add(check_all_passes)
    markup.add(create_naryad)
    markup.add(create_gen_act_but)
    
    bot.send_message(
        chat_id=message.chat.id,
        text='Вітаю вас у боті для пропусків!',
        reply_markup=markup
    )


def landing_stage(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    create_pass_btn = types.KeyboardButton('Створити пропуск')
    view_all_passes_btn = types.KeyboardButton('Переглянути всі дійсні пропуски')
    create_naryad = types.KeyboardButton('Створити наряд')
    create_gen_act_but = types.KeyboardButton('Створити ген акт')
   
    markup.add(create_pass_btn)
    markup.add(view_all_passes_btn)
    markup.add(create_naryad)
    markup.add(create_gen_act_but)
  
    bot.send_message(
        chat_id=message.chat.id,
        reply_markup=markup,
        text="Щоб створити пропуск нажміть: Створити"
    )
    

@bot.message_handler(func = lambda message: message.text =='Переглянути всі дійсні пропуски')
def get_all_passes(message: types.Message):
    passes = get_all_passes_db()
    
    message_text = all_passes_message(passes)
    
    bot.send_message(chat_id=message.chat.id, text=message_text)
    
    return landing_stage(message)


@bot.message_handler(func=lambda message: message.text =="Створити пропуск")
def stage_1(message: types.Message):
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')
    
    markup.add(cancel_btn)
    
    bot.send_message(
        chat_id=message.chat.id,
        text="Введіть повне ім'я особи",
        reply_markup=markup
    )
    
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=stage_1_1
    )

def stage_1_1(message:types.Message):
    global users
    full_name = message.text
    if  full_name == 'Скасувати':
        return cancel_pass(message)
    users[message.chat.id]={'full_name':[full_name]}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')
    car_btn = types.KeyboardButton('Додати машину')
    non_car_btn = types.KeyboardButton('Не додавати машину')
    markup.add(cancel_btn,car_btn,non_car_btn)
    bot.send_message(
        chat_id=message.chat.id,
        text = 'Оберіть наступну дію',
        reply_markup= markup
    )



@bot.message_handler(func=lambda message:message.text == 'Додати машину')
def add_auto_model(message:types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')
    markup.add(cancel_btn)
    bot.send_message(
        chat_id=message.chat.id,
        text ='Введіть марку авто: ',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=add_auto_plates
    )


def add_auto_plates(message:types.Message):
    auto_model = message.text
    if  auto_model == 'Скасувати':
        return cancel_pass(message)
    users[message.chat.id]['auto_model'] = auto_model
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')
    markup.add(cancel_btn)
    bot.send_message(
        chat_id=message.chat.id,
        text='Введіть гос. номер автомобіля: ',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=stage1_9
    )

@bot.message_handler(func=lambda message: message.text == "Додати ще людину")
def add_member(message:types.Message):
    if len(users[message.chat.id]['full_name']) == 10:
        return get_pass(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')

    markup.add(cancel_btn)
    
    
    bot.send_message(
        chat_id=message.chat.id,
        text="Введіть повне ім'я особи",
        reply_markup=markup
    )
    
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=check_member
    )
    

def check_member(message:types.Message):
    full_name = message.text
    if  full_name == 'Скасувати':
        return cancel_pass(message)
    
    if message.chat.id:
        users[message.chat.id]['full_name'].append(full_name)
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    cancel_btn = types.KeyboardButton('Скасувати')
    
    if len(users[message.chat.id]['full_name']) != 5:
        add_more_btn = types.KeyboardButton('Додати ще людину')
        
    form_pass_btn = types.KeyboardButton('Отримати пропуск')
    
    if len(users[message.chat.id]['full_name']) != 5:
        markup.add(add_more_btn)
        
    markup.add(cancel_btn,form_pass_btn)
    
    bot.send_message(
        chat_id=message.chat.id,
        text = f'Додано людину: {full_name}. Оберіть наступну дію',
        reply_markup=markup
    )

def stage1_9(message:types.Message):
    auto_plates = message.text
    if  auto_plates == 'Скасувати':
        return cancel_pass(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')

    markup.add(cancel_btn)
    users[message.chat.id]['auto_plates'] = auto_plates
    return stage_2(message)


@bot.message_handler(func=lambda message: message.text == "Не додавати машину")
def stage_2(message: types.Message):
    
    users[message.chat.id]['auto_plates'] = users[message.chat.id].get('auto_plates','')
    users[message.chat.id]['auto_model'] = users[message.chat.id].get('auto_model','')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    today_btn = types.KeyboardButton('Сьогодні')
    tomorrow_btn = types.KeyboardButton('Завтра')
    choose_bnt = types.KeyboardButton('Написати дату самостійно')
    cancel_btn = types.KeyboardButton('Скасувати')
    
    markup.add(today_btn,tomorrow_btn,choose_bnt,cancel_btn)
    
    if  message.text == 'Скасувати':
        return cancel_pass(message)
    
    bot.send_message(
        chat_id=message.chat.id,
        text="Оберіть з якої дати ви хочете оформити перепустки",
        reply_markup=markup
    )
    
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=stage_2_5
    )


def stage_2_5(message: types.Message):
    date_start = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')
    markup.add(cancel_btn)
    if date_start == 'Скасувати':
        return cancel_pass(message)

    elif date_start == 'Сьогодні':
        users[message.chat.id]['start_date'] = date.today()

        return stage_3(message)

    elif date_start == 'Завтра':
        users[message.chat.id]['start_date'] = get_date_from_start_date(date.today(),1)

        return stage_3(message)

    elif date_start == 'Написати дату самостійно':
        bot.send_message(
            chat_id=message.chat.id,
            text="Введіть початкову дату пропуску (Наприклад, 3.07.2023):",
            reply_markup=markup
        )

        bot.register_next_step_handler_by_chat_id(
            chat_id=message.chat.id,
            callback=stage_2_6
        )


def stage_2_6(message: types.Message):
    date_start = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')
    markup.add(cancel_btn)
    if date_start == 'Скасувати':
        return cancel_pass(message)
    try:
        date_start_obj = get_date_object(date_start)
        users[message.chat.id]['start_date'] = date_start_obj
    except ValueError:
        bot.send_message(
            chat_id=message.chat.id,
            text='Неправильний формат дати, спробуйте ще раз'
        )
        
        bot.register_next_step_handler_by_chat_id(
            chat_id=message.chat.id,
            callback=stage_2_6
        )  
        
        return 
    
    stage_3(message)


def stage_3(message: types.Message):

    if message.text == 'Скасувати':
        return cancel_pass(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')
    markup.add(cancel_btn)
    bot.send_message(
        chat_id=message.chat.id,
        text="Введіть кількість днів, на яку хочете зробити пропуск: ",
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=end_stage
    )
    

@bot.message_handler(func=lambda message: message.text == 'Створити наряд' )
def ask_picture(message:types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text = 'Надішліть фото коносаменту',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_gruz
    )

def ask_gruz(message: types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    photo_id = message.photo[-1].file_id

    # Получение информации о фотографии
    file_info = bot.get_file(photo_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

    # Загрузка фотографии и перевод в байты
    response = requests.get(file_url)
    if response.status_code == 200:
        photo_bytes = io.BytesIO(response.content)
    files[message.chat.id] = [{'file':photo_bytes,'name':'konosament.jpg'}]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')
    btn1 = types.KeyboardButton('ULSD 10 PPM / Паливо дизельне')
    btn2 = types.KeyboardButton('Gasoline 95 RON 10 PPM / Бензин А-95')  
    markup.add(btn1,btn2,cancel_btn)
    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть найменування вантажу',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback = ask_amount
    )


def ask_amount(message: types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    name_of_gruz = message.text
    if name_of_gruz not in ['ULSD 10 PPM / Паливо дизельне','Gasoline 95 RON 10 PPM / Бензин А-95']:
        return cancel_pass(message)
    naryad[message.chat.id] = {'name_of_gruz':name_of_gruz}
    if message.text == 'ULSD 10 PPM / Паливо дизельне':
        gng_num = '2710194300'
    if message.text == 'Gasoline 95 RON 10 PPM / Бензин А-95':
        gng_num = '2710124512'
    naryad[message.chat.id]['gng_num'] = gng_num
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть кількість тон дизеля / бензина у вакумі (Ця інформація є в коносаменті)',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_name_of_vessel
    )


def ask_name_of_vessel(message:types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    amount_of_gas = message.text
    naryad[message.chat.id]['amount_of_gas'] = amount_of_gas

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text='Укажіть назву судна (Ця інформація є в коносаменті)',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_country
    )

def ask_country(message: types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    vessel_name = message.text
    naryad[message.chat.id]['vessel_name'] = vessel_name

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text='Укажіть країну відправки (Ця інформація є в коносаменті)',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_num_of_manifest
    )

def ask_num_of_manifest(message: types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    country = message.text
    naryad[message.chat.id]['country'] = country

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text='Укажіть номер Маніфесту (Ця інформація є в коносаменті)',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_num_of_konosament
    )

def ask_num_of_konosament(message: types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    num_of_manifest = message.text
    naryad[message.chat.id]['num_of_manifest'] = num_of_manifest

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text='Укажіть номер коносаменту (Ця інформація є в коносаменті)',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_num_of_invoysya
    )


def ask_num_of_invoysya(message: types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    num_of_konosament = message.text
    naryad[message.chat.id]['num_of_konosament'] = num_of_konosament

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text='Укажіть номер інвойся (Цю інформацію треба дізнаватися у декларанта Сергія Пескового)',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_date_of_arrive
    )

def ask_date_of_arrive(message: types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    num_of_invoysya = message.text
    naryad[message.chat.id]['num_of_invoysya'] = num_of_invoysya

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text='Укажіть дату прибуття судна',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_name_of_reciever
    )


def ask_name_of_reciever(message:types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    date_of_arrival = message.text
    naryad[message.chat.id]['date_of_arrival'] = date_of_arrival
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    choose1_bnt = types.KeyboardButton('LLC Bel-Petrol Trading, Україна')
    choose2_bnt = types.KeyboardButton('LLC Peyd, Україна')
    choose3_bnt = types.KeyboardButton('LLC Wog Resurs, Україна')
    choose4_bnt = types.KeyboardButton('LLC Geomaks Resurs, Україна')
    choose5_bnt = types.KeyboardButton('Написати самостійно')
    markup.add(choose1_bnt,choose2_bnt,choose3_bnt,choose4_bnt,choose5_bnt,cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text ="Оберіть одержувача або напишіть його ім'я самостійно",
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=check_naryad_info
    )


def write_reciever_name(message:types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text = "Введіть найменування одержувача",
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=check_naryad_info
    )

def check_naryad_info(message: types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    if message.text =="Написати самостійно":
        return write_reciever_name(message)
    reciever_name = message.text
    naryad[message.chat.id]['reciever_name'] = reciever_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    send_naryad_btn = types.KeyboardButton('Відправити наряд')
    markup.add(cancel_bnt,send_naryad_btn)
    bot.send_message(
        chat_id = message.chat.id,
        text = f"Перевірте інформацію, яка буде наявна у наряді:\nНазва груза - {naryad[message.chat.id]['name_of_gruz']},\n Кількість тон дизеля / бензина - {naryad[message.chat.id]['amount_of_gas']},\n Назва судна - {naryad[message.chat.id]['vessel_name']},\n Країна відправлення - {naryad[message.chat.id]['country']},\n Номер маніфесту - {naryad[message.chat.id]['num_of_manifest']},\n Номер коносаменту - {naryad[message.chat.id]['num_of_konosament']},\n Номер інвойся - {naryad[message.chat.id]['num_of_invoysya']},\n Дата прибуття - {naryad[message.chat.id]['date_of_arrival']},\n Найменування одержувача - {naryad[message.chat.id]['reciever_name']}",
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback = send_naryad_to_gmail
    )



def send_naryad_to_gmail(message:types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    num = get_formatted_last_id()
    name,file = fill_cells(naryad_dict=naryad,chat_id=message.chat.id,naryad_num= num)
    files[message.chat.id].append({'name':name,'file':file})
    recipients = ['artmark90@gmail.com', 'nikhin24@outlook.com','tek-tehexp1@izmport.com.ua','10elmurzaevm@gmail.com']

    send_email_with_attachment(
        sender_email='viktoriya2008propuska@gmail.com',
        sender_password= "mimxzfykczjmequf",
        receiver_email=', '.join(recipients),
        # receiver_email='tgbotpassua@gmail.com',
        subject=f"Запрос на ордер {naryad[message.chat.id]['vessel_name']}",
        message='',
        attachments=files,
        chat_id=message.chat.id
    )
    bot.send_message(
        chat_id=message.chat.id,
        text = "Лист було надіслано, скоро він з'явиться на вашій пошті"
    )
    landing_stage(message)
    naryad.pop(message.chat.id)


def end_stage(message: types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    try:
        num_of_day_to_pass = int(message.text)
        if not 1<= num_of_day_to_pass <= 7:
            raise Exception
    except:
        bot.send_message(
            chat_id=message.chat.id,
            text ='Кількість днів має бути числом від 1 до 7'
        )
        
        bot.register_next_step_handler_by_chat_id(
            chat_id=message.chat.id,
            callback= end_stage
        )
        
        return
    
    if num_of_day_to_pass == 'Скасувати':
        return cancel_pass(message)

    date_end = get_date_from_start_date(users[message.chat.id]['start_date'],num_of_day_to_pass)

    users[message.chat.id]['end_date'] = date_end
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    add_person_btn = types.KeyboardButton('Додати ще людину')
    form_pass_btn = types.KeyboardButton('Отримати пропуск')
    cancel_btn = types.KeyboardButton('Скасувати')
    
    
    markup.add(cancel_btn)
    
    if len(users[message.chat.id]['full_name']) < 5:
        markup.add(add_person_btn)
        
    markup.add(form_pass_btn)
    
    today, today_str = get_today_date()
    users[message.chat.id]['created_at'] = today
    
    bot.send_message(
        chat_id=message.chat.id,
        text=get_result_message(users[message.chat.id]),
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text in ["Отримати пропуск"])
def get_pass(message: types.Message):
    new_pass = create_new_pass(
        names = users[message.chat.id]['full_name'],
        start_date= users[message.chat.id]['start_date'],
        end_date=users[message.chat.id]['end_date'],
        created_at=users[message.chat.id]['created_at'],
        auto_model=users[message.chat.id]['auto_model'],
        auto_plates=users[message.chat.id]['auto_plates']
    )
    
    file, name = make_pass(        
        names = users[message.chat.id]['full_name'],
        start_date= users[message.chat.id]['start_date'],
        end_date=users[message.chat.id]['end_date'],
        created_at=users[message.chat.id]['created_at'],
        auto_plates=users[message.chat.id]['auto_plates'],
        auto_model=users[message.chat.id]['auto_model'],
        num=get_number(new_pass.id)
    )
    files[message.chat.id] = [{'name':name,'file':file}]

    bot.send_document(message.chat.id, file.getvalue(), visible_file_name=name)
    
    recipients = ['smb.bp@izm.uspa.gov.ua', 'vd@izm.uspa.gov.ua', 'artmark90@gmail.com', 'nikhin24@outlook.com',' 10elmurzaevm@gmail.com']

    send_email_with_attachment(
        sender_email='viktoriya2008propuska@gmail.com',
        sender_password= "mimxzfykczjmequf",
        receiver_email=', '.join(recipients),
        subject=f'Пропуск: {name}',
        message='',
        attachments=files,
        chat_id=message.chat.id
        )
    users.pop(message.chat.id)
    files.pop(message.chat.id)
    landing_stage(message)


@bot.message_handler(func=lambda message: message.text == 'Створити ген акт')
def ask_recipient(message:types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)  
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати')  
    choose1_bnt = types.KeyboardButton('LLC Bel-Petrol Trading, Україна')
    choose2_bnt = types.KeyboardButton('LLC Peyd, Україна')
    choose3_bnt = types.KeyboardButton('LLC Wog Resurs, Україна')
    choose4_bnt = types.KeyboardButton('LLC Geomaks Resurs, Україна')
    choose5_bnt = types.KeyboardButton('Написати самостійно')    
    markup.add(choose1_bnt,choose2_bnt,choose3_bnt,choose4_bnt,choose5_bnt,cancel_btn)


    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть назву одержувача',
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_vessel_name
    )


def write_recipient_name(message:types.Message):
    if message.text == 'Скасувати':
        return cancel_pass(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_bnt = types.KeyboardButton('Скасувати')
    markup.add(cancel_bnt)
    bot.send_message(
        chat_id=message.chat.id,
        text = "Введіть найменування одержувача",
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_vessel_name
    )


def ask_vessel_name(message:types.Message):
    repicient = message.text
    if repicient == 'Скасувати':
        return cancel_pass(message)
    if repicient == 'Написати самостійно':
        return write_recipient_name(message)
    
    gen_act[message.chat.id] = {'repicient':repicient}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton('Скасувати') 

    markup.add(cancel_btn)
    
    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть назву судна',
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_country_name_gen_act
    )


def ask_country_name_gen_act(message: types.Message):
    vessel_name = message.text
    if vessel_name == 'Скасувати':
        return cancel_pass(message)
    
    gen_act[message.chat.id]['vessel_name'] = vessel_name

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_btn)

    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть країну відправки',
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_arrival_date_gen_act
    )   


def ask_arrival_date_gen_act(message: types.Message):
    country = message.text
    if country == 'Скасувати':
        return cancel_pass(message)
    gen_act[message.chat.id]['country'] = country
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_btn)

    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть дату приходу',
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_download_start_date_gen_act
    ) 

def ask_download_start_date_gen_act(message: types.Message):
    arrival_date = message.text
    if arrival_date == 'Скасувати':
        return cancel_pass(message)
    gen_act[message.chat.id]['arrival_date'] = arrival_date
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_btn)

    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть дату початку завантаження',
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_download_end_date_gen_act
    ) 


def ask_download_end_date_gen_act(message: types.Message):
    download_start_date = message.text
    if download_start_date == 'Скасувати':
        return cancel_pass(message)
    gen_act[message.chat.id]['download_start_date'] = download_start_date
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_btn)

    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть дату кінця завантаження',
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_cargo_name_gen_act
    )

def ask_cargo_name_gen_act(message: types.Message):
    download_end_date = message.text
    if download_end_date == 'Скасувати':
        return cancel_pass(message)
    gen_act[message.chat.id]['download_end_date'] = download_end_date
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    gasoline_btn = 'Бензин А-95'
    dyz_toplyvo_btn = 'Дизпаливо    ULSD 10 PPM'
    markup.add(cancel_btn)
    markup.add(gasoline_btn,dyz_toplyvo_btn)
    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть найменування вантажу',
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_konosament_weight_gen_act
    )

def ask_konosament_weight_gen_act(message: types.Message):
    cargo_name = message.text
    if cargo_name == 'Скасувати':
        return cancel_pass(message)
    gen_act[message.chat.id]['cargo_name'] = cargo_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_btn)
    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть вагу вантажу по коносаменту',
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_actual_weight_gen_act
    )


def ask_actual_weight_gen_act(message: types.Message):
    konosament_weight = message.text
    if konosament_weight == 'Скасувати':
        return cancel_pass(message)
    gen_act[message.chat.id]['konosament_weight'] = konosament_weight
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_btn)
    bot.send_message(
        chat_id=message.chat.id,
        text = 'Укажіть фактичну вагу вантажу',
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=ask_if_data_is_correct_gen_act
    )


def ask_if_data_is_correct_gen_act(message: types.Message):
    actual_weight = message.text
    if actual_weight == 'Скасувати':
        return cancel_pass(message)
    
    gen_act[message.chat.id]['actual_weight'] = actual_weight
    
    if gen_act[message.chat.id]['konosament_weight'] != actual_weight:
        return ask_num_of_konosament_gen_act(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    get_gen_act_btn = 'Отримати ген акт'
    markup.add(get_gen_act_btn,cancel_btn)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Перевірте інформацію, яка буде вказана в ген акті:\nОдержувач - {gen_act[message.chat.id]['repicient']}\nНазва судна - {gen_act[message.chat.id]['vessel_name']}\nКраїна відправки - {gen_act[message.chat.id]['country']}\nДата приходу - {gen_act[message.chat.id]['arrival_date']}\nДата початку завантаження - {gen_act[message.chat.id]['download_start_date']}\nДата кінця завантаження - {gen_act[message.chat.id]['download_end_date']}\nНайменування вантажу - {gen_act[message.chat.id]['cargo_name']}\nВага вантажу по коносаменту - {gen_act[message.chat.id]['konosament_weight']}\nФактична вага вантажу - {gen_act[message.chat.id]['actual_weight']}",
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=get_gen_act
    )

def ask_num_of_konosament_gen_act(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_btn)

    bot.send_message(
        chat_id=message.chat.id,
        text='Укажіть номер коносаменту',
        reply_markup=markup
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=check_gen_and_notification_act_info
    )

def check_gen_and_notification_act_info(message: types.Message):
    konosam_num = message.text
    if konosam_num == 'Скасувати':
        return cancel_pass
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    get_both_acts = 'Отримати ген акт та акт повідомлення'
    markup.add(get_both_acts,cancel_btn)

    gen_act[message.chat.id]['konosam_num'] = konosam_num

    bot.send_message(
        chat_id=message.chat.id,
        text =f"Перевірте вказану вами інформацію:\nОдержувач - {gen_act[message.chat.id]['repicient']}\nНазва судна - {gen_act[message.chat.id]['vessel_name']}\nКраїна відправки - {gen_act[message.chat.id]['country']}\nДата приходу - {gen_act[message.chat.id]['arrival_date']}\nДата початку завантаження - {gen_act[message.chat.id]['download_start_date']}\nДата кінця завантаження - {gen_act[message.chat.id]['download_end_date']}\nНайменування вантажу - {gen_act[message.chat.id]['cargo_name']}\nВага вантажу по коносаменту - {gen_act[message.chat.id]['konosament_weight']}\nФактична вага вантажу - {gen_act[message.chat.id]['actual_weight']}\nНомер коносаменту - {gen_act[message.chat.id]['konosam_num']}",
        reply_markup=markup
    ) 

    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=get_gen_act
    )


def get_gen_act(message: types.Message):
    if message.text == 'Скасувати':
        return  cancel_pass(message)
    gen_act_num = get_last_id_gen_act()
    name, file = fill_cells_gen_act(gen_act,message.chat.id, gen_act_num)
    bot.send_document(chat_id = message.chat.id,document = file.getvalue(), visible_file_name=name)
    if gen_act[message.chat.id]['konosament_weight'] != gen_act[message.chat.id]['actual_weight']:
        ntf_act_num = get_last_id_notification_act()
        name, file = fill_cells_notification_act(gen_act,message.chat.id, ntf_act_num)
        bot.send_document(chat_id=message.chat.id, document=file.getvalue(),visible_file_name=name)
    gen_act.pop(message.chat.id)
    landing_stage(message)


# @bot.message_handler(func=lambda message: message.text == 'Скасувати')
# def cancel_pass(message: types.Message):
#     if message.chat.id in users:
#         users.pop(message.chat.id)

#     landing_stage(message)

    
# @server.route('/' + TOKEN, methods=['POST'])
# def getMessage():
#     json_string = request.get_data().decode('utf-8')
#     update = telebot.types.Update.de_json(json_string)
#     bot.process_new_updates([update])
#     return "!", 200


# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url='https://tg-pass-bot-6baa39b01dcb.herokuapp.com/' + TOKEN)
#     return "!", 200


# if __name__ == "__main__":
#     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

bot.polling()
