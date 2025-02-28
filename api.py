import requests
from environs import Env
env = Env()
env.read_env()
import json
URL= f"{env.str('BASE_URL')}/api"
def create_user(telegram_id:str,language:str=None,name:str=None):
    try:
        response = requests.post(url=f"{URL}/botuser/",
                                 data={'telegram_id': telegram_id, 'name': name, 'language': language})
        return 'Ok'
    except:
        return 'Bad'
def get_all_users():
    try:
        response = requests.get(url=f"{URL}/botuser/",
                                 )
        return json.loads(response.text)

    except:
        return []
def get_user(telegram_id):
    try:
        response = requests.post(url=f"{URL}/user/", data={'telegram_id': telegram_id})
        if response.status_code == 204:
            return 'Not Found'
        else:
            return json.loads(response.text)
    except:
        return {}


def change_user_language(telegram_id,language):
    try:
        response = requests.post(url=f"{URL}/lang/", data={'telegram_id': telegram_id, 'language': language})
        if response.status_code == 204:
            return 'Not Found'
        else:
            return json.loads(response.text)
    except:
        pass
def add_channel(channel_id:str,channel_name:str=None,channel_members_count:str=None):
    try:
        response = requests.post(url=f"{URL}/channels/", data={'channel_id': channel_id, 'channel_name': channel_name,'channel_members_count':channel_members_count})
        if response.status_code == 201:
            return 'ok'
        else:
            return 'bad'
    except:
        pass
def get_all_channels():
    try:
        response = requests.get(url=f"{URL}/channels/",
                                 )
        return json.loads(response.text)

    except:
        return []
def get_channel(channel_id):
    try:
        response = requests.post(url=f"{URL}/channel/",
                                 data={'channel_id':channel_id})
        if response.status_code==206:
            return json.loads(response.text)
        else:
            return {}

    except:
        return {}
def delete_channel(channel_id):
    try:
        response = requests.post(url=f"{URL}/delete_channel/",
                                 data={'channel_id':channel_id})
        if response.status_code==200:
            return 'Ok'
        else:
            return "Bad"
    except:
        return "Bad"
