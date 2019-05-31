import requests

from telebot import types

client_id = 'f35c6306bd0c443d83a9e371cd525413'
oauth_url = f'https://oauth.yandex.ru/authorize?response_type=token&client_id={client_id}'

set_token_msg = 'Для работы с ботом Вам необходимо установить OAuth' \
                'token, для этого воспользуйтесь командой /settoken.'


def get_headers_for_request(token):
    return {'oauth_token': token,
            'Authorization': f'OAuth {token}',
            'Content-Type': 'application/json'}


def get_response_json(url, params=None, **kwargs):
    response = requests.get(url, params=params, **kwargs)
    return response.status_code, response.json()


def get_ym_response_json(token, api_section, method_name, version='v1', params=None):
    headers = get_headers_for_request(token)
    request_url = f'https://api-metrika.yandex.net/{api_section}/{version}/{method_name}'
    return get_response_json(request_url, params=params, headers=headers)


def get_inline_markup_for_ym_counters(counters, stat_id):
    buttons = []
    for counter in counters:
        buttons.append(types.InlineKeyboardButton(counter["name"],
                                                  callback_data=f'{stat_id}_{counter["id"]}'))
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(*tuple(buttons))
    return markup
