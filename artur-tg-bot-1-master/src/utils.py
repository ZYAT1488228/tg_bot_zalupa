from datetime import datetime, date, timedelta

from src.models import Pass

import codecs

def get_date_object(date: str):
    datetime_format = "%d.%m.%Y"
    
    date_object = datetime.strptime(date, datetime_format)
    
    return date_object

def get_today_date():
    today = date.today()
    return today, today.strftime("%d.%m.%Y")

def get_result_message(data: dict):
    start_date = data['start_date']
    end_date = data['end_date']
    message = 'В пропуск буде вписана наступна інформація:'
    
    for idx, full_name in enumerate(data['full_name']):
        person = f"\n\nІм'я: {full_name}\n"
        person += f"Дата старту: {start_date.strftime('%d.%m.%Y')}\n"
        person += f"Дата кінцю: {end_date.strftime('%d.%m.%Y')}\n"

        message += person

    return message

def get_number(number: int):
    second_num = (number - 1) % 99 + 1
    
    first_num = (number - 1) // 99 + 1
    
    return f"{first_num:02d}/{second_num:02d}"

def all_passes_message(passes: list[Pass]):
    if not passes:
        return "Дійсних пропусків немає"
    
    message = "Всі пропуски:\n\n"
    
    for i, _pass in enumerate(passes):
        message += f"{i + 1}.\n"
        message += f"Імена людей: {', '.join([person.name for person in _pass.people])}\n"
        message += f"Пропуск дійсний до: {_pass.date_end}\n"
        message += "\n"
        
    return message
        

def get_date_from_start_date(date_start: date, num_of_days: int) -> date:

    end_date = date_start + timedelta(days=num_of_days)

    return end_date
