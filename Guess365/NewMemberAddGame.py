from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import pyodbc
import requests
import json
from random import sample


class NewMemberAddGame:

    def __init__(self):
        _server_gamania = ''  # No TCP
        _database_gamania = ''
        _uid_gamania = ''
        _pwd_gamania = ''
        _port = ""

        self.conn_Guess365 = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + _server_gamania + ';Port=' + _port + ';DATABASE=' + _database_gamania + ';UID=' + _uid_gamania + ';PWD=' + _pwd_gamania)  # for MSSQL
        self.cursor = self.conn_Guess365.cursor()
        self.users = [
            {'username': 'rick', 'password': generate_password_hash('123rick456'), 'password_2': '123rick456'}
        ]

    def Participants(self):
        try:
            member_len = 0
            member_time = 0
            while member_len == 0:
                game, start_dd, end_dd = self.Contest()
                member_result = self.Usermember(game, start_dd, end_dd)
                member_len = len(member_result)
                member_time += 1
                if member_time > 4:
                    print("All bot are alreadly predict all game")
            member = member_result.sample(2)
            message = self.SelectMatch(game, member)
            print(message)
        except Exception as e:
            print("Error message: ", e)

    def Contest(self):
        SQL = '''
           SELECT *
            FROM [dbo].[PkSeason] as a
            inner join Games as b on a.Game_id = b.id
            inner join MatchEntry as c on a.SportCode = c.SportCode 
            where End_dd > '{0}' and MatchTime >= '{0}' and MatchTime <= '{1}'
        '''.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                   (datetime.now() + timedelta(days=7)).astimezone(timezone(timedelta(hours=8))).strftime(
                       '%Y-%m-%d %H:%M:%S.000'))
        print(SQL)
        result = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
        matchgame = result.sample(1)
        game = matchgame['game'].iloc[0]
        start_dd = matchgame['Start_dd'].iloc[0]
        end_dd = matchgame['End_dd'].iloc[0]
        return game, start_dd, end_dd

    def Usermember(self, game, start_dd, end_dd):
        SQL = '''
            SELECT a.UserId,a.member,a.[Password]
                FROM [dbo].[UserMember] as a
                where [Password] = '13579' and email is null and login_ip = '192.168.56.1'
                EXCEPT 
            select d.UserId,d.member,d.[Password]
                from PredictMatch as b
                inner join MatchEntry as c on b.EventCode = c.EventCode
                inner join UserMember as d on b.UserId = d.UserId
                where MatchTime >= '{}' and MatchTime <= '{}' and b.TournamentText = '{}'
        '''.format(start_dd, end_dd, game)
        print(SQL)
        result = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
        return result

    def SelectMatch(self, game, member):
        for i in range(len(member)):
            try:
                url = f'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/{game}/any'
                MatchEntrys = requests.get(url, verify=False,
                                           auth=(self.users[0]['username'], self.users[0]['password_2'])).text
                MatchEntrys = json.loads(MatchEntrys)['response']
                match = sample(MatchEntrys, 1)
                odds = sample(match[0]['odds'], 1)[0]
                url = 'https://ecocoapidev1.southeastasia.cloudapp.azure.com/PredictMatchEntry/'
                # url = 'http://192.168.56.1:3000/PredictMatchEntry/'
                data = {
                    'account': member['member'].iloc[i],
                    'password': member['Password'].iloc[i],
                    'GroupOptionCode': odds['GroupOptionCode'],
                    'OptionCode': odds['OptionCode'],
                    'EventCode': match[0]["EventCode"],
                    'PredictType': 'Forecast'
                }
                response_ = requests.post(url, verify=False, data=data,
                                          auth=(self.users[0]['username'], self.users[0]['password_2'])).text
                if 'Error' in response_:
                    return response_
                else:
                    successful_info = f"{member['member'].iloc[i]} is successful to predict!!"
                    print(successful_info)
            except Exception as e:
                return 'Error Info', e
        return f"Successful add new member({member['member'].iloc[0]} & {member['member'].iloc[1]}) to predict {game}!!"


if __name__ == "__main__":
    NewMemberAddGame = NewMemberAddGame()
    NewMemberAddGame.Participants()
