from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta, timezone
import pandas as pd
import pyodbc
import requests
import warnings

warnings.filterwarnings('ignore')


class FBPushBot:

    def __init__(self, data=None):
        self.conn_Guess365 = pyodbc.connect(server=web_config.production().server,
                                    database=web_config.production().database,
                                    user=web_config.production().username,
                                    password=quote(web_config.production().password), 
                                    tds_version = '7.3',
                                    port = 1433,
                                    driver = '/home/linuxbrew/.linuxbrew/lib/libtdsodbc.so') 
        self.useEmail = 'gohit.cc@gmail.com'
        self.usePass = '123Gohitcc'

    def FBPush(self, eventcode=None, action=None):
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("headless")
        browser = webdriver.Chrome(options=options)
        browser.get('http://www.facebook.com')
        account = browser.find_element_by_id("email")
        account.send_keys(self.useEmail)
        password = browser.find_element_by_id('pass')
        password.send_keys(self.usePass)
        password.send_keys(Keys.RETURN)
        sleep(2)
        browser.get(
            'https://business.facebook.com/latest/composer?asset_id=101206799481441&nav_ref=profile_plus_admin_tool&ref=biz_web_home&context_ref=HOME')
        sleep(2)
        presentation = browser.find_element_by_xpath('//*[@aria-label="在對話方塊中寫點內容，即可為貼文加上文字。"]')
        if action == 'predict':
            message = self.GetMatch(eventcode)
        else:
            message = self.ResultPush()
        presentation.send_keys(message)
        sleep(2)
        browser.find_element_by_xpath(
            '/html/body/div[1]/div[1]/div/div[1]/div[1]/div/div/div[2]/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div[2]/div/div[2]/div/span/div/div/div').click()
        print('Push home is successful!!')
        sleep(5)
        browser.get("https://www.facebook.com/profile.php?id=100087443327573")
        browser.find_element_by_xpath('//*[@aria-label="立即切換"]').click()
        sleep(2)
        browser.get('https://www.facebook.com/groups/3283784315209430')
        sleep(2)
        presentation = browser.find_element_by_class_name('xi81zsa.x1lkfr7t.xkjl1po.x1mzt3pk.xh8yej3.x13faqbe')
        presentation.click()
        sleep(2)
        placeholder = browser.find_element_by_xpath('//*[@aria-label="建立公開貼文……"]')
        placeholder.send_keys(message)
        sleep(2)
        browser.find_element_by_xpath('//*[@aria-label="發佈"]').click()
        print('Push society is successful!!')

    def GetMatch(self, eventcode):
        SQL = '''
        SELECT b.MatchTime,a.GroupOptionCode,a.TournamentText,OptionCode,SpecialBetValue,HomeTeam,AwayTeam,c.name as Away,d.name as Home
          FROM [dbo].[LINEPushMatch] as a
          inner join MatchEntry as b on a.EventCode = b.EventCode
          full outer join teams as c on b.AwayTeam = c.team 
          full outer join teams as d on b.HomeTeam = d.team 
          where a.EventCode in {}
        '''.format(tuple(eventcode))
        print(SQL)
        result = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
        message = self.message(result)
        return message

    def message(self, result):
        TournamentText = result['TournamentText'].iloc[0]
        premessage = self.PreMessage(result)
        fbmessage = '''
        Guess365 大數據模型預測推薦
賽事 : {}
*****************賽事推薦*****************
{}
*****************賽事推薦*****************
精準賽事預測與分享，盡在Guess365
官網：https://user198088.psee.io/4jq5tt

#Guess365盃全競賽 #資料數據分析公司 #AI分析
#預測 #Guess365規則透明公開 #運動經濟 #預測賽事 #賽後閒談 
#體育分析 #籃球 #棒球 #足球 #NBA #MLB #LOL #python
        '''.format(TournamentText, premessage)
        return fbmessage

    def PreMessage(self, result):
        matchmessage = ""
        for i in range(len(result)):
            MatchTime = result['MatchTime'].iloc[i]
            HomeTeam = result['Home'].iloc[i]
            if HomeTeam is None:
                HomeTeam = result['HomeTeam'].iloc[i]
            AwayTeam = result['Away'].iloc[i]
            if AwayTeam is None:
                AwayTeam = result['AwayTeam'].iloc[i]
            GroupOptionCode = result['GroupOptionCode'].iloc[i]
            OptionCode = result['OptionCode'].iloc[i]
            if GroupOptionCode == '20':
                groupname = '強弱盤'
                if OptionCode == '1':
                    option = "主勝"
                else:
                    option = "客勝"
            elif GroupOptionCode in ['60', '52']:
                groupname = '大小盤'
                SpecialBetValue = result['SpecialBetValue'].iloc[ic]
                if OptionCode == 'Over':
                    option = f"大於{SpecialBetValue}"
                else:
                    option = f"小於{SpecialBetValue}"
            elif GroupOptionCode in ['228', '51']:
                groupname = '讓分盤'
                SpecialBetValue = result['SpecialBetValue'].iloc[i]
                if int(SpecialBetValue) > 0:
                    SpecialBetValue = "+" + str(SpecialBetValue)
                if OptionCode == '1':
                    option = f"主{SpecialBetValue}"
                else:
                    option = f"客{SpecialBetValue}"
            message = '''{} {}(主) vs {}(客) | {} | {} \n'''.format(MatchTime, HomeTeam, AwayTeam, groupname, option)
            matchmessage += message
        return matchmessage

    def PredictResultPushMessage(self):
        DatetimeTop = (datetime.now().astimezone(timezone(timedelta(hours=8))) - timedelta(days=1)).replace(hour=0,
                                                                                                            minute=0,
                                                                                                            second=0).strftime(
            '%Y-%m-%d %H:%M:%S.000')
        DatetimeBottom = (datetime.now().astimezone(timezone(timedelta(hours=8))) - timedelta(days=1)).replace(hour=23,
                                                                                                               minute=59,
                                                                                                               second=59).strftime(
            '%Y-%m-%d %H:%M:%S.000')
        SQL = '''  
        SELECT b.MatchTime,a.TournamentText,a.GroupOptionCode,a.OptionCode,a.SpecialBetValue,b.HomeTeam,b.AwayTeam,d.name as Home,c.name as Away,b.HomeScore,b.AwayScore
            FROM [dbo].[LINEPushMatch] as a
            inner join MatchResults as b on a.EventCode = b.EventCode
            full outer join teams as c on b.AwayTeam = c.team 
            full outer join teams as d on b.HomeTeam = d.team 
            where b.MatchTime >= '{}' and b.MatchTime < '{}' and b.time_status = 'Ended'
        '''.format(DatetimeTop, DatetimeBottom)
        print(SQL)
        PredictResults = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
        return PredictResults

    def ResultPush(self):
        PredictResults = self.PredictResultPushMessage()
        tournamentText = set(PredictResults['TournamentText'])
        match_list = []
        for t in tournamentText:
            matchresult = self.ResultMessage(t,PredictResults)
            message_dict = {
                "賽事": t,
                "MatchResult": matchresult
            }
            match_list.append(message_dict)
        match = pd.DataFrame(match_list)
        message_match = ""
        for m in range(len(match)):
            tournamentText = match['賽事'].iloc[m]
            matchresult = match['MatchResult'].iloc[m]
            matchmessage = '''
賽事 : {}
*****************賽事結果*****************
{}
*****************賽事結果***************** \n
            '''.format(tournamentText, matchresult)
            message_match += matchmessage
        fbmessage = '''
Guess365 大數據模型預測結果
{}
精準賽事預測與分享，盡在Guess365
官網：https://user198088.psee.io/4jq5tt

#Guess365盃全競賽 #資料數據分析公司 #AI分析
#預測 #Guess365規則透明公開 #運動經濟 #預測賽事 #賽後閒談 
#體育分析 #籃球 #棒球 #足球 #NBA #MLB #LOL #python
        '''.format(message_match)
        return fbmessage

    def ResultMessage(self,tournamentText,PredictResults):
        tournameone = PredictResults[PredictResults['TournamentText'] == tournamentText]
        matchmessage = ""
        for i in range(len(tournameone)):
            MatchTime = tournameone['MatchTime'].iloc[i]
            HomeTeam = tournameone['Home'].iloc[i]
            if HomeTeam is None:
                HomeTeam = tournameone['HomeTeam'].iloc[i]
            AwayTeam = tournameone['Away'].iloc[i]
            if AwayTeam is None:
                AwayTeam = tournameone['AwayTeam'].iloc[i]
            GroupOptionCode = tournameone['GroupOptionCode'].iloc[i]
            OptionCode = tournameone['OptionCode'].iloc[i]
            HomeScore = int(tournameone['HomeScore'].iloc[i])
            AwayScore = int(tournameone['AwayScore'].iloc[i])
            if GroupOptionCode == '20':
                groupname = '強弱盤'
                if OptionCode == '1':
                    option = "主勝"
                    if HomeScore > AwayScore:
                        game_result = '✔️'
                    elif HomeScore < AwayScore:
                        game_result = '❌'
                    else:
                        game_result = '❕'
                else:
                    option = "客勝"
                    if HomeScore > AwayScore:
                        game_result = '❌'
                    elif HomeScore < AwayScore:
                        game_result = '✔️'
                    else:
                        game_result = '❕'
            elif GroupOptionCode in ['60', '52']:
                groupname = '大小盤'
                SpecialBetValue = float(tournameone['SpecialBetValue'].iloc[i])
                if OptionCode == 'Over':
                    option = f"大於{SpecialBetValue}"
                    if HomeScore + AwayScore > SpecialBetValue:
                        game_result = '✔️'
                    elif HomeScore + AwayScore < SpecialBetValue:
                        game_result = '❌'
                    else:
                        game_result = '❕'
                else:
                    option = f"小於{SpecialBetValue}"
                    if HomeScore + AwayScore > SpecialBetValue:
                        game_result = '❌'
                    elif HomeScore + AwayScore < SpecialBetValue:
                        game_result = '✔️'
                    else:
                        game_result = '❕'
            elif GroupOptionCode in ['228', '51']:
                groupname = '讓分盤'
                SpecialBetValue = float(tournameone['SpecialBetValue'].iloc[i])
                if int(SpecialBetValue) > 0:
                    SpecialBetValue = "+" + str(SpecialBetValue)
                if OptionCode == '1':
                    option = f"主{SpecialBetValue}"
                    if HomeScoree + SpecialBetValue > AwayScore:
                        game_result = '✔️'
                    elif HomeScore + SpecialBetValue < AwayScore:
                        game_result = '❌'
                    else:
                        game_result = '❕'
                else:
                    option = f"客{SpecialBetValue}"
                    if HomeScoree + SpecialBetValue > AwayScore:
                        game_result = '❌'
                    elif HomeScore + SpecialBetValue < AwayScore:
                        game_result = '✔️'
                    else:
                        game_result = '❕'
            message = '''{} {} {}(主) vs {}(客) | {} | {} \n'''.format(game_result, MatchTime, HomeTeam, AwayTeam,
                                                                     groupname, option)
            matchmessage += message
        return matchmessage

    def PushBot(self, action):
        df_pred = pd.DataFrame(self.predlist)
        if action == 'predict':
            try:
                eventcode = df_pred['EventCode']
                self.FBPush(eventcode, action)
            except Exception as e:
                print("Error", e)
        elif action == 'result':
            try:
                self.FBPush(action)
            except Exception as e:
                print("Error", e)
        else:
            print("The parameter is error")


if __name__ == '__main__':
    FBPushBot = FBPushBot(data)
    FBPushBot.PushBot(action)
