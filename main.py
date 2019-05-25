#!/usr/bin/env python3.7
import re
import requests

from telebot import TeleBot
from telebot import types

from host import Host
from helper import *

tb = TeleBot('741854622:AAGbBUJEHWrFLPH8PAhzZiLh18vOZJ4cy9E')
host = Host()


@tb.message_handler(commands=['start'])
def start_command(message: types.Message):
    tb.send_message(message.chat.id,
                    f'*Добро пожаловать в Metrika Bot*\n'
                    f'{set_token_msg}',
                    disable_notification=True,
                    parse_mode='Markdown')


@tb.message_handler(commands=['settoken'])
def set_token_command(message: types.Message):
    msg = tb.send_message(message.chat.id,
                          f'*Установка OAuth token*\n'
                          f'Для установки OAuth token перейдите по [ссылке]({oauth_url}), '
                          f'нажмите "Разрешить" и отправьте результат боту в ответ на это '
                          f'письмо. В случае успеха вы получите соответсвующее сообщение.',
                          reply_markup=types.ForceReply(),
                          disable_notification=True,
                          parse_mode='Markdown')
    tb.register_for_reply(msg, set_token)


@tb.message_handler(commands=['attendance'])
def attendance_command(message: types.Message):
    user_id = message.from_user.id
    if host.contains_token(user_id):
        token = host.get_token(user_id)
        status_code, response = get_ym_response_json(token, 'management', 'counters')
        if status_code == 200:
            counters = response['counters']
            markup = get_inline_markup_for_ym_counters(counters, 'att')

            if markup.keyboard:
                message_text = f'_Выберите счётчик для получения статистики посещаемости_'
            else:
                message_text = f'_У вас нет счётчиков, создайте их на Яндекс.Метрика_'

            tb.send_message(message.chat.id, message_text, reply_markup=markup,
                            disable_notification=True, parse_mode='Markdown')
        else:
            error_sender(message.chat.id, status_code)
    else:
        tb.send_message(message.chat.id, f'*Ошибка!*\n{set_token_msg}',
                        disable_notification=True, parse_mode='Markdown')


@tb.callback_query_handler(func=lambda call: re.match(r'^att_\d+', call.data))
def attendance_sender(call: types.CallbackQuery):
    user_id = call.from_user.id
    if host.contains_token(user_id):
        token = host.get_token(user_id)
        params = {'dimensions': 'ym:s:date',
                  'metrics': 'ym:s:users',
                  'sort': '-ym:s:date',
                  'limit': '30',
                  'filters': "ym:s:isNewUser=='Yes'",
                  'id': call.data[4:]}
        status_code, response = get_ym_response_json(token, 'stat', 'data', params=params)
        if status_code == 200:
            data = response['data']
            day, week, month = 0, 0, 0
            for i, d in enumerate(data):
                value = int(d['metrics'][0])
                if i < 1:
                    day += value
                if i < 6:
                    week += value
                month += value

            tb.edit_message_text(f'*Статистика новых посетителей*\n'
                                 f'За сегодня: _{day}_\n'
                                 f'За неделю: _{week}_\n'
                                 f'За месяц: _{month}_',
                                 call.message.chat.id,
                                 call.message.message_id,
                                 parse_mode='Markdown')
        else:
            error_sender(call.message.chat.id, status_code)
    else:
        tb.send_message(call.message.chat.id, f'*Ошибка!*\n{set_token_msg}',
                        disable_notification=True, parse_mode='Markdown')


def error_sender(chat_id, error_code):
    if error_code == 403:
        error_message = 'Неверный OAuth-токен.\n' \
                        'Воспользуйтесь командой /settoken.'
    elif error_code == 503:
        error_message = 'Ошибка сервера.\n' \
                        'Попробуйте еще раз.'
    elif error_code == 429:
        error_message = 'Превышен лимит количества запросов к API для пользователя.\n' \
                        'Попробуйте позже.'
    elif error_code == 504:
        error_message = 'Запрос выполняется дольше отведенного времени.\n' \
                        'Попробуйте еще раз.'
    elif error_code == 503:
        error_message = 'Ошибка сервера.\n' \
                        'Попробуйте еще раз.'
    else:
        error_message = 'Неизвестная ошибка.\n' \
                        'Попробуйте еще раз.'

    tb.send_message(chat_id, f'*Ошибка!*\n{error_message}',
                    disable_notification=True, parse_mode='Markdown')


def set_token(message: types.Message):
    token = message.text
    if re.match(r'^[A-Z0-9_-]+$', token, re.IGNORECASE):
        if host.contains_token(message.from_user.id):
            host.update_token(message.from_user.id, token)
        else:
            host.add_token(message.from_user.id, token)
        message_text = '*Ваш ключ успешно установлен!*'
    else:
        message_text = '*Ошибка!\n*Ключ указан неверно.'

    tb.send_message(message.chat.id, message_text,
                    disable_notification=True, parse_mode='Markdown')


tb.polling(none_stop=True)
