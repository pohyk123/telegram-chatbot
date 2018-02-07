import json
import requests
import time
import urllib
from pythonlangutil.overload import Overload, signature

import intents
import tfl

import config


TOKEN = config.telegram_bot_token
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode('utf8')
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + 'getUpdates'
    if offset:
        url += '?offset={}'.format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates['result']:
        update_ids.append(int(update['update_id']))
    return max(update_ids)


def echo_all(updates):
    for update in updates['result']:
        text = update['message']['text']
        chat = update['message']['chat']['id']
        send_message(text, chat)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates['result'])
    last_update = num_updates - 1
    text = updates['result'][last_update]['message']['text']
    chat_id = updates['result'][last_update]['message']['chat']['id']
    return (text, chat_id)


def send_message(text, chat_id, reply_markup='{}'):
    text = urllib.parse.quote_plus(text)
    url = URL + 'sendMessage?text={}&chat_id={}&reply_markup={}'.format(text, chat_id, reply_markup)
    get_url(url)


def validate_bot():
    url = URL + 'getme'
    js = get_json_from_url(url)
    botStat = {'status':'Unknown','id':0}
    botStat['id'] = js['result']['id']
    if (js['ok'] == True):
        botStat['status'] = 'Online'
    else:
        botStat['status'] = 'Offline'
    return botStat


def get_responses(updates):
    responses = []
    for update in updates['result']:
        if ('location' in update['message']):
            text = str(update['message']['location'])
        elif ('text' in update['message']):
            text = update['message']['text']
        chat_id = update['message']['chat']['id']
        response = {'response':intents.getIntentResponse(text,chat_id),'chat_id':chat_id}
        responses.append(response)
    return responses


def get_responses_message(updates):
    responses = get_responses(updates)
    for response in responses:
        response['response'] = response['response']['message']
    responses_message_only = responses
    return responses_message_only


def reply_to_sender(responses_message_only):
    for response in responses_message_only:
        send_message(response['response']['message'],response['chat_id'],response['response']['reply_markup'])


def main():
    last_update_id = None
    botStat = validate_bot()

    print('Validating bot...')
    print('Status: '+ botStat['status'])
    print('Bot ID: '+ str(botStat['id']))

    while True:
        try:
            updates = get_updates(last_update_id)
            print(updates)
            if len(updates['result']) > 0:
                last_update_id = get_last_update_id(updates) + 1
                responses = get_responses(updates)
                reply_to_sender(responses)
        except: {}
        time.sleep(2)

if __name__ == '__main__':
    main()
