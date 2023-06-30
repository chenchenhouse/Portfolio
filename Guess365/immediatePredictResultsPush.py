

import requests
from werkzeug.security import generate_password_hash
import FBAutoBot as fb
import web_config

def immeduate():
    accounts="winwin666,i945win"
    users = [
        {'username': 'rick', 'password': generate_password_hash('123rick456'), 'password_2': '123rick456'}
    ]
    DateBetween = "2022-09-20~2022-09-22"
    #domain_name = 'ecocoapidev1.southeastasia.cloudapp.azure.com'
    domain_name = '3f14-220-130-85-186.ngrok-free.app'
    UserId = 'U2ac744af2efee83323ec7042627b6c9d'

    requests.get(f"https://{domain_name}/immediatePredictResultsPush",verify=False, auth=(users[0]['username'],users[0]['password_2']))

def FBPush():
    FBPushBot = fb.FBPushBot()
    FBPushBot.PushBot('result')

if __name__ == '__main__':
    immeduate()
    FBPush()