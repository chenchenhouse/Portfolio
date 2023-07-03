#html解析
from bs4 import BeautifulSoup
#記數
from collections import Counter
#非同步爬蟲
import nest_asyncio
import asyncio
from pyppeteer import launch,launcher
#xml解析
from lxml import etree
from pyquery import PyQuery as pq
#動態爬蟲
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#標籤轉換
from sklearn.preprocessing import LabelEncoder,StandardScaler,MinMaxScaler
#DEEP LEARNING
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout,GRU,BatchNormalization,Masking,ELU,LeakyReLU
from keras.callbacks import EarlyStopping
from keras.callbacks import ReduceLROnPlateau
from keras.regularizers import l2,l1,l1_l2
from tensorflow.keras.optimizers import Adagrad,Adadelta,Nadam,SGD,Adam
from keras.metrics import Precision, Recall,AUC
from keras.models import load_model
#時間處理
from datetime import datetime,timedelta,timezone
from time import sleep
#http基本認證
from requests.auth import HTTPBasicAuth


#數據處理
import pandas as pd
#使用正則表達式
import re
#發送http請求
import requests
#DEEP LEARNING
import tensorflow.keras.backend as K
import tensorflow as tf
#數值運算
import numpy as np
#響應用戶輸入事件
import tkinter
#數據序列化
import joblib
#解析json格式
import json
#呼叫模型
import pickle
#查詢檔案
import os
#SQL
import pyodbc
from requests.auth import HTTPBasicAuth as HBA
from urllib.parse import parse_qsl,quote
from werkzeug.security import generate_password_hash, check_password_hash

nest_asyncio.apply()
try:
    launcher.DEFAULT_ARGS.remove("--enable-automation")
except:
    pass

class MyLabelEncoder(LabelEncoder):
    def __init__(self, *args, **kwargs):
        self.classes_ = kwargs.pop('classes', None)
        super().__init__(*args, **kwargs)

    def fit(self, y):
        if self.classes_ is None:
            super().fit(y)
        else:
            self.classes_ = np.asarray(self.classes_)
            self.classes_dict_ = {c: i for i, c in enumerate(self.classes_)}
        return self

    def transform(self, y):
        if self.classes_ is None:
            return super().transform(y)
        else:
            return np.array([self.classes_dict_[x] if x in self.classes_dict_ else -1 for x in y])

class NPBPredictModel(object):
    '''
    groupoptioncode: 20強弱盤
    optioncode:1主 2客
    '''
    def __init__(self):
        self.remake = False
        self.teams = {
            '火腿斗士' : 1,
            '海灣之星' : 2,
            '野牛' : 3,
            '水手' : 4,
            '中日龍' : 5,
            '阪神老虎' : 6,
            '金鷹' : 7,
            '鯉魚' : 8, 
            '巨人' : 9, 
            '燕子' : 10,
            '銀鷹' : 11, 
            '西武獅' : 12
        }

        self.teams_changename = {
            "歐力士野牛" : "歐力士猛牛",
            "中日龍" : "中日龍",
            "北海道日本火腿斗士" : "日本火腿鬥士",
            "埼玉西武獅" : "西武獅",
            "橫濱海灣之星" : "橫濱DeNA灣星",
            "讀賣巨人" : "讀賣巨人",
            "阪神老虎" : "阪神虎",
            "養樂多燕子" : "養樂多燕子",
            "福岡軟銀鷹" : "軟體銀行鷹",
            "東北樂天金鷹" : "樂天金鷹",
            "廣島鯉魚" : "廣島東洋鯉魚",
            "千葉羅德水手" : "羅德海洋"
        }
        self.teams_changename_en = {
            "Orix Buffaloes" : "歐力士猛牛",
            "Chunichi Dragons" : "中日龍",
            "Nippon Ham Fighters" : "日本火腿鬥士",
            "Seibu Lions" : "西武獅",
            "Yokohama BayStars" : "橫濱DeNA灣星",
            "Yomiuri Giants" : "讀賣巨人",
            "Hanshin Tigers" : "阪神虎",
            "Yakult Swallows" : "養樂多燕子",
            "Fukuoka S. Hawks" : "軟體銀行鷹",
            "Rakuten Gold. Eagles" : "樂天金鷹",
            "Hiroshima Carp" : "廣島東洋鯉魚",
            "Chiba Lotte Marines" : "羅德海洋"
        }

        self.teams_changename_en2 = {
            "Orix Buffaloes" : "歐力士猛牛",
            "Chunichi Dragons" : "中日龍",
            "Hokkaido Nippon Ham Fighters" : "日本火腿鬥士",
            "Saitama Seibu Lions" : "西武獅",
            "Yokohama Bay Stars" : "橫濱DeNA灣星",
            "Yomiuri Giants" : "讀賣巨人",
            "Hanshin Tigers" : "阪神虎",
            "Yakult Swallows" : "養樂多燕子",
            "Fukuoka Softbank Hawks" : "軟體銀行鷹",
            "Tohoku Rakuten Golden Eagles" : "樂天金鷹",
            "Hiroshima Carp" : "廣島東洋鯉魚",
            "Chiba Lotte Marines" : "羅德海洋"
        }

        self.final_change = {
            "橫濱DeNA灣星" : "橫濱海灣之星"
        }
        
        
        self.today = datetime.now()+ timedelta(days=0)
        self.date_before = (self.today + timedelta(days=-1)).strftime("%Y-%m-%d")
        self.matchdate = (self.today + timedelta(days=0))
        self.yesterday = (self.today + timedelta(days=-1))
        #npb資料儲存處
        self.path_model = r'C:\Users\user\NPB建模'
        self.path = f'{self.path_model}/{self.matchdate.strftime("%Y%m%d")}'
        self.path_b = f'{self.path_model}/{self.yesterday.strftime("%Y%m%d")}'
        #chrome.exe儲存處
        self.excutable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.central ={
            "2023" : "e62e602d"
        }
        self.pacific={
            "2023" : "06956421",
        }
        
    #取得賽程(球探網)
    def crawler_titan(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('chromedriver',options=options)
        browser = webdriver.Chrome(options=options)
        data_all = []
        year = self.today.year
        match_month = self.matchdate.month
        before_month = self.yesterday.month
        day = self.today.day
        date_start = self.yesterday
        for i in range(before_month,match_month+1):
            browser.get(f"http://sports.titan007.com/big/infoData/baseball/Normal.aspx?y={str(year)}&m={i}&matchSeason={str(year)}&SclassID=2")
            soup = BeautifulSoup(browser.page_source,"lxml")
            loading = soup.find("div",{"id":"subSpnLoading"})
            if "數據加載出錯！！！" not in loading:
                tr = soup.find("table",{"id":"scheTab"}).find_all("tr",{"align":"center"})
                for t in range(len(tr)):
                    td = tr[t].find_all("td")
                    dateFormatter = "%Y%m-%d%H:%M"
                    game_time = datetime.strptime(str(year) + td[1].text,dateFormatter)
                    if len(tr[t].find_all("td")[3].text.split("-")) == 2 and len(tr[t].find_all("td")[7]) != 0 and game_time.strftime("%Y-%m-%d") >= date_start.strftime("%Y-%m-%d"):
                        home_name = tr[t].find_all("td")[2].text
                        away_name = tr[t].find_all("td")[4].text
                        home_score = tr[t].find_all("td")[3].text.split("-")[0]
                        away_score = tr[t].find_all("td")[3].text.split("-")[1]
                        odd_score = tr[t].find_all("td")[5].text
                        odd_sum = tr[t].find_all("td")[6].text
                        evencode = re.sub("\D","",tr[t].find_all("td")[7].find_all("a")[0].get("href"))
                        data_one = {
                            "Date": pd.to_datetime(game_time.strftime("%Y-%m-%d")),
                            "主隊" : home_name,
                            "主隊得分" : home_score,
                            "客隊" : away_name,
                            "客隊得分" : away_score,
                            "讓分" : odd_score,
                            "總分" : odd_sum,
                            "Eventcode" : evencode
                        }
                        data_all.append(data_one)
                        print(f"{str(game_time)} {home_name} vs {away_name} successful!!")
                    elif len(tr[t].find_all("td")[7]) != 0 and game_time.strftime("%Y-%m-%d") ==self.matchdate.strftime("%Y-%m-%d") :
                        dateFormatter = "%Y%m-%d%H:%M"
                        game_time = datetime.strptime(str(year) + td[1].text,dateFormatter)
                        home_name = tr[t].find_all("td")[2].text
                        away_name = tr[t].find_all("td")[4].text
                        home_score = ""
                        away_score = ""
                        odd_score = tr[t].find_all("td")[5].text
                        odd_sum = tr[t].find_all("td")[6].text
                        evencode = re.sub("\D","",tr[t].find_all("td")[7].find_all("a")[0].get("href"))
                        data_one = {
                            "Date": pd.to_datetime(game_time.strftime("%Y-%m-%d")),
                            "主隊" : home_name,
                            "主隊得分" : home_score,
                            "客隊" : away_name,
                            "客隊得分" : away_score,
                            "讓分" : odd_score,
                            "總分" : odd_sum,
                            "Eventcode" : evencode
                        }
                        data_all.append(data_one)
                        print(f"{str(game_time)} {home_name} vs {away_name} successful!!")
        df_sch = pd.DataFrame(data_all)
        df_sch.index = df_sch["Date"]
        df_sch.drop(["Date"],axis= 1, inplace=True)
        df_sch.to_excel(f"{self.path}/sch.xlsx")
        df_sch = pd.read_excel(f"{self.path}/sch.xlsx",index_col='Date')
        return df_sch
    
    #爬取資料(球探網)
    def titain_data(self,df_sch):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('chromedriver',options=options)
        browser = webdriver.Chrome(options=options)
        data_all = []
        for i in range(0,len(df_sch)):
            matchtime = df_sch.index[i]
            eventcode = df_sch['Eventcode'].iloc[i]
            url = f"https://sports.titan007.com/analysis/baseball/{eventcode}.htm"
            browser.get(url)
            sleep(2)
            soup_all = BeautifulSoup(browser.page_source,"lxml")
            data_one = {
                "Date" : matchtime,
                "Eventcode" : eventcode,
                "html" : soup_all
            }
            data_all.append(data_one)
            print(f"{eventcode} web crawler successful!!")
            if (i+1) == len(df_sch):
                data_html = []
                for html in range(len(data_all)):
                    try:
                        date = data_all[html]['Date']
                        eventcode = data_all[html]['Eventcode']
                        soup = data_all[html]['html']
                        data_one = {
                            "Date" : date,
                            "Eventcode" : eventcode
                        }

                        rank_div = soup.find("div",{"style":"{leaguenoneorblock}"})
                        #主隊
                        homerank_label = rank_div.find("label",{"id":"homeRank"})
                        homerank = homerank_label.find("font").text
                        home_rank = {
                            "Home_Rank" : homerank
                        }
                        data_one = dict(**data_one,**home_rank)
                        homerank_e = rank_div.find("div",{"id":"e"})
                        tr = homerank_e.find_all("tr",{"bgcolor":"#FEFAF8"})
                        for t in range(0,len(tr)):
                            td = tr[t].find_all("td")
                            locate_ch = td[0].text
                            if locate_ch == '总':
                                locate = 'Total'
                            elif locate_ch == '主':
                                locate = 'Home'
                            elif locate_ch == '客':
                                locate = 'Away'
                            elif locate_ch == '近6场':
                                locate = 'six'
                            game = td[1].text
                            win = td[2].text
                            lose = td[3].text
                            win_rate = round(int(td[4].text.replace("%",'')) / 100,2)

                            data_home_rank = {
                                f"Home_Game_In{locate}" : game,
                                f"Home_Win_In{locate}" : win,
                                f"Home_Lose_In{locate}" : lose,
                                f"Home_WinRate_In{locate}" : win_rate,
                            }
                            data_one = dict(**data_one,**data_home_rank)

                        #客隊
                        awayrank_label = rank_div.find("label",{"id":"guestRank"})
                        awayrank = awayrank_label.find("font").text
                        away_rank = {
                            "Away_Rank" : awayrank
                        }

                        data_one = dict(**data_one,**away_rank)
                        awayRank_e = rank_div.find("div",{"id":"f"})
                        tr = awayRank_e.find_all("tr",{"bgcolor":"#F2F9FD"})
                        for t in range(0,len(tr)):
                            td = tr[t].find_all("td")
                            locate_ch = td[0].text
                            if locate_ch == '总':
                                locate = 'Total'
                            elif locate_ch == '主':
                                locate = 'Home'
                            elif locate_ch == '客':
                                locate = 'Away'
                            elif locate_ch == '近6场':
                                locate = 'six'
                            game = td[1].text
                            win = td[2].text
                            lose = td[3].text
                            win_rate = round(int(td[4].text.replace("%",'')) / 100,2)

                            data_away_rank = {
                                f"Away_Game_In{locate}" : game,
                                f"Away_Win_In{locate}" : win,
                                f"Away_Lose_In{locate}" : lose,
                                f"Away_WinRate_In{locate}" : win_rate,
                            }
                            data_one = dict(**data_one,**data_away_rank)

                        #對戰
                        bettle_div = soup.find("div",{"style":"{cupnoneorblock}"})

                        #雙方對戰
                        both_bettle = bettle_div.find("div",{"id":"v"}).find_all('tr')[-1].find("td").find_all("font")[2].text.replace("%","")

                        #主隊對戰
                        home_bettle = bettle_div.find("div",{"id":"h"}).find_all('tr')[-1].find("td").find_all("font")[1].text.replace("%","")

                        #客隊對戰
                        away_bettle = bettle_div.find("div",{"id":"a"}).find_all('tr')[-1].find("td").find_all("font")[1].text.replace("%","")
                        bettle_one = {
                            "Both_bettle" : both_bettle,
                            "Home_bettle" : home_bettle,
                            "Away_bettle" : away_bettle,
                        }  
                        data_one = dict(**data_one,**bettle_one)
                        #未來三場
                        #主
                        tr = bettle_div.find_all("table")[-4].find_all("tr",{"bgcolor":"#FFECEC"})
                        for t in range(3):
                            try:
                                td = tr[t].find_all("td")
                                next_date = td[1].text
                                next_locate = td[2].text
                                next_oppo = td[3].text
                            except:
                                next_date = None
                                next_locate = 0
                                next_oppo = 0
                            next_match = {
                                f"Home_NextDate{(t+1)}" : next_date,
                                f"Home_NextLocate{(t+1)}" : next_locate,
                                f"Home_NextOppo{(t+1)}" : next_oppo,
                            }
                            data_one = dict(**data_one,**next_match)

                        #客
                        tr = bettle_div.find_all("table")[-2].find_all("tr",{"bgcolor":"#FFECEC"})
                        for t in range(3):
                            try:
                                td = tr[t].find_all("td")
                                next_date = td[1].text
                                next_locate = td[2].text
                                next_oppo = td[3].text
                            except:
                                next_date = None
                                next_locate = 0
                                next_oppo = 0
                            next_match = {
                                f"Away_NextDate{(t+1)}" : next_date,
                                f"Away_NextLocate{(t+1)}" : next_locate,
                                f"Away_NextOppo{(t+1)}" : next_oppo,
                            }
                            data_one = dict(**data_one,**next_match)
                        data_html.append(data_one)
                        print(str(eventcode) + " insert data successful!!")
                    except:
                        print(str(eventcode) + " insert data fail!!")
                        pass
                df_all = pd.DataFrame(data_html)
                df_all.index = df_all['Date']
                df_all = df_all.sort_index()
                df_all.drop('Date',axis=1,inplace=True)
                for team in ['Home','Away']:
                    for n in range(1,4):
                        try:
                            df_all[f'{team}_NextDate{n}'] = (pd.to_datetime(df_all[f'{team}_NextDate{n}']) - df_all.index).apply(lambda x:round((x.days)+(x.seconds/60/60/24),2) if x != None else x).fillna(0)
                            df_all[f'{team}_NextOppo{n}'] = df_all[f'{team}_NextOppo{n}'].replace(self.teams)
                            df_all[f'{team}_NextLocate{n}'] = df_all[f'{team}_NextLocate{n}'].replace('主','1').replace('客','2')
                        except:
                            pass
                df_all.to_excel(f"{self.path}/titan.xlsx")
        df_all = pd.read_excel(f"{self.path}/titan.xlsx",index_col='Date')
        return df_all
    
    #爬取賽況(運彩報馬仔)
    def crawler_lottonavi(self,df_sch):
        df_havedata = df_sch.index.strftime("%Y%m%d").unique()
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('chromedriver',options=options)
        browser = webdriver.Chrome(options=options)
        data_all = []
        for d in range(len(df_havedata)):
            date_only = df_havedata[d]
            browser.get(f"https://www.lottonavi.com/matches/npb/{date_only}")
            soup = BeautifulSoup(browser.page_source,"lxml")
            havegame = soup.find_all("h5")
            for g in range(len(havegame)):
                noplay = havegame[g].text.split(",")
                tr = soup.find_all("table",{"class":"table table-bordered table-striped"})[g].find("tbody").find_all("tr")
                if ((len(noplay) == 2) or (len(noplay) == 3 and ('系列賽' in noplay[2]))) or ((d < len(df_havedata)-1) and (tr[0].find_all("th")[2].text != '')):
                    team = noplay[0].split(" vs. ")
                    awayteam = team[0].split(" ")[0]
                    hometeam = team[1].split(" ")[0]
                    awayrank = team[0].split(" ")[1].replace("(","").replace(")","")
                    homerank = team[1].split(" ")[1].replace("(","").replace(")","")
                    #客隊
                    awaydata = tr[0].find_all("th")
                    away_href = awaydata[0].find("a").get("href")
                    if datetime.strptime(df_havedata[d],"%Y%m%d") < (self.matchdate):
                        away_score = awaydata[2].text
                    else:
                        away_score = np.nan
                    away_sp_name = awaydata[3].text
                    away_sp_href = awaydata[3].find("a").get("href")
                    away_sp_winlose = awaydata[4].text
                    away_sp_win = away_sp_winlose[0]
                    away_sp_lose = away_sp_winlose[0]
                    try:
                        away_sp_winrate =  round(int(away_sp_win) / (int(away_sp_win) + int(away_sp_lose)),2)
                    except:
                        away_sp_winrate = 0
                    away_sp_era = awaydata[5].text
                    away_team_winlose = awaydata[6].text.split(", ")[0]
                    away_team_win = away_team_winlose.split("-")[0]
                    away_team_lose = away_team_winlose.split("-")[1]
                    away_team_tie = away_team_winlose.split("-")[2]
                    try:
                        away_team_winrate = round(int(away_team_win)/ (int(away_team_win) + int(away_team_lose) + int(away_team_tie)),2)
                    except:
                        away_team_winrate = 0
                    away_inaway_winlose = awaydata[6].text.split(", ")[1]
                    away_inaway_win = away_team_winlose.split("-")[0]
                    away_inaway_lose = away_team_winlose.split("-")[1]
                    away_inaway_tie = away_team_winlose.split("-")[2]
                    try:
                        away_inaway_winrate = round(int(away_inaway_win)/ (int(away_inaway_win) + int(away_inaway_lose) + int(away_inaway_tie)),2)
                    except:
                        away_inaway_winrate = 0
                    away_team_now = awaydata[7].text
                    away_team_avgscore = awaydata[9].text
                    away_team_obp = awaydata[10].text
                    away_team_avg = awaydata[11].text
                    away_team_era = awaydata[12].text
                    #主隊
                    homedata = tr[1].find_all("th")
                    home_href = homedata[0].find("a").get("href")
                    if datetime.strptime(df_havedata[d],"%Y%m%d") < (self.matchdate):
                        home_score = homedata[2].text
                    else:
                        home_score = np.nan
                    home_sp_name = homedata[3].text
                    home_sp_href = homedata[3].find("a").get("href")
                    home_sp_winlose = homedata[4].text.split("-")
                    home_sp_win = home_sp_winlose[0]
                    home_sp_lose = home_sp_winlose[0]
                    try:
                        home_sp_winrate =  round(int(home_sp_win) / (int(home_sp_win) + int(home_sp_lose)),2)
                    except:
                        home_sp_winrate = 0
                    home_sp_era = homedata[5].text
                    home_team_winlose = homedata[6].text.split(", ")[0]
                    home_team_win = home_team_winlose.split("-")[0]
                    home_team_lose = home_team_winlose.split("-")[1]
                    home_team_tie = home_team_winlose.split("-")[2]
                    try:
                        home_team_winrate = round(int(home_team_win)/ (int(home_team_win) + int(home_team_lose) + int(home_team_tie)),2)
                    except:
                        home_team_winrate = 0
                    home_inhome_winlose = homedata[6].text.split(", ")[1]
                    home_inhome_win = home_team_winlose.split("-")[0]
                    home_inhome_lose = home_team_winlose.split("-")[1]
                    home_inhome_tie = home_team_winlose.split("-")[2]
                    try:
                        home_inhome_winrate = round(int(home_inhome_win)/ (int(home_inhome_win) + int(home_inhome_lose) + int(home_inhome_tie)),2)
                    except:
                        home_inhome_winrate = 0
                    home_team_now = homedata[7].text
                    home_team_avgscore = homedata[9].text
                    home_team_obp = homedata[10].text
                    home_team_avg = homedata[11].text
                    home_team_era = homedata[12].text
                    #先發打序
                    firest_player = tr[2].find_all("th")[-1]
                    firest_player_href = firest_player.find_all("a",{"style":"padding-right:5px;"})[2].get("href")
                    #game_href
                    game_href = awaydata[2].find("a").get("href")
                    data = {
                        "Date" : df_havedata[d],
                        "主隊" : hometeam,
                        "主隊得分" : home_score,
                        "Home_Rank" : homerank,
                        "客隊" : awayteam,
                        "客隊得分" : away_score,
                        "Away_Rank" : awayrank,
                        "game_href" : game_href,
                        "Home_href" : home_href,
                        "Home_SP" : home_sp_name,
                        "Home_SP_href" : home_sp_href,
                        "Home_SP_win" : home_sp_win,
                        "Home_SP_lose" : home_sp_lose,
                        "Home_SP_winrate" : home_sp_winrate,
                        "Home_SP_ERA" : home_sp_era,
                        "Away_href" : away_href,
                        "Away_SP" : away_sp_name,
                        "Away_SP_href" : away_sp_href,
                        "Away_SP_win" : away_sp_win,
                        "Away_SP_lose" : away_sp_lose,
                        "Away_SP_winrate" : away_sp_winrate,
                        "Away_SP_ERA" : away_sp_era,
                        "FP_href" : firest_player_href
                        }
                    data_all.append(data)
                    print(f"{df_havedata[d]} : {noplay[0]} successful!!")
        df_n = pd.DataFrame(data_all)
        df_n.index = df_n["Date"]
        df_n.drop("Date",axis = 1,inplace=True) 
        df_n.index = pd.to_datetime(df_n.index, format='%Y%m%d')
        df_n.to_excel(f"{self.path}/lottonavi.xlsx")
        df_n = pd.read_excel(f"{self.path}/lottonavi.xlsx",index_col='Date')
        return df_n
    
    #先發投手數據更新
    def SP_update(self,df_lottonavi):
        home_sp = df_lottonavi['Home_SP_href']
        away_sp = df_lottonavi['Away_SP_href']
        all_sp = home_sp.append(away_sp)
        all_sp = all_sp.unique()

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('chromedriver',options=options)
        browser = webdriver.Chrome(options=options)
        name = os.listdir(f"{self.path_model}/SP")
        for i,sp in enumerate(all_sp):
            player_name = sp.split("/")[-2]
            if f"{player_name}.xlsx" in name:
                start_year = self.matchdate.year
                end_year = self.matchdate.year+1
            else:
                start_year = 2011
                end_year = self.matchdate.year+1
            data_all = []
            for y in range(start_year,end_year):
                browser.get(f"{sp}/{y}-regular-season/game-logs/")
                soup = BeautifulSoup(browser.page_source,"lxml")
                tr = soup.find("table",{"class":"table table-bordered table-striped"}).find_all("tr")
                for t in range(len(tr)):
                    th = tr[t].find_all("th")
                    if "/" in th[0].text:
                        MatchTime = datetime.strptime(str(y) + "/" + th[0].text,"%Y/%m/%d")
                        home_away = th[1].text.split("\xa0")
                        home_or_away = home_away[0]
                        team = home_away[1]

                        score_href = th[2].find("a").get("href")
                        team_win = th[3].text
                        sp_win = th[4].text
                        ip = th[5].text
                        nop = th[6].text
                        hits = th[7].text
                        ra = th[8].text
                        er = th[9].text
                        hr = th[10].text
                        bb = th[11].text
                        so = th[12].text
                        win = th[13].text
                        lose = th[14].text
                        cp = th[15].text
                        era = th[16].text
                        if era != '-.--':
                            data = {
                                "Date" : MatchTime,
                                "主客場" : home_or_away,
                                "敵隊" : team,
                                "score_href" : score_href,
                                "球隊" : team_win,
                                "投手" : sp_win,
                                "局數" : round(float(ip),1),
                                "球數" : int(nop),
                                "安打" : int(hits),
                                "失分" : int(ra),
                                "自責失分" : int(er),
                                "全壘打" : int(hr),
                                "保送" : int(bb),
                                "三振" : int(so),
                                "勝投" : int(win),
                                "敗投" : int(lose),
                                "救援" : int(cp),
                                "防禦率" : round(float(era),2)
                            }
                            data_all.append(data)
                        else:
                            continue
                print(f"{player_name} {y} successful!!")
            try:
                df_1 = pd.DataFrame(data_all)
                df_1.index = df_1["Date"]
                df_1.drop(["Date"],axis = 1,inplace=True)
                df_1 = df_1.sort_index()
                print(f"{player_name} update successful!!")
            except:
                df_1 = pd.DataFrame()
                print(f"{player_name} no data need to update!!")
            if f"{player_name}.xlsx" in name:
                df_have = pd.read_excel(f"{self.path_model}/SP/{player_name}.xlsx",index_col='Date')
                df_have = df_have[df_have.index < str(end_year)]
                df_1 = df_have.append(df_1)
            df_1.to_excel(f"{self.path_model}/SP/{player_name}.xlsx")
    
    #先發投手數據
    def SP_data(self,df_lottonavi):
        data_all = []
        for i in range(len(df_lottonavi)):
            date = df_lottonavi.index[i]
            home = df_lottonavi['主隊'].iloc[i]
            away = df_lottonavi['客隊'].iloc[i]
            eventcode = df_lottonavi['Eventcode'].iloc[i]
            data_one = {
                "Date" : date,
                "主隊" : home,
                "客隊" : away,
                "Eventcode" : eventcode
            }
            home_sp = df_lottonavi['Home_SP_href'].iloc[i].split("/")[-2]
            away_sp = df_lottonavi['Away_SP_href'].iloc[i].split("/")[-2]
            home_sp_data = pd.read_excel(f"{self.path_model}/SP/{home_sp}.xlsx",index_col='Date')
            home_sp_data_now = home_sp_data[home_sp_data.index == date]
            if len(home_sp_data_now) > 0:
                home_sp_data_now = home_sp_data_now.iloc[0]
                col = []
                for c in home_sp_data_now.index:
                    c = 'Home_' + c
                    col.append(c)
                home_sp_data_now.index = col
                home_sp_data_now_dict = dict(home_sp_data_now)
                data_one = dict(**data_one,**home_sp_data_now_dict)


            away_sp_data = pd.read_excel(f"{self.path_model}/SP/{away_sp}.xlsx",index_col='Date')
            away_sp_data_now = away_sp_data[away_sp_data.index == date]
            if len(away_sp_data_now) > 0:
                away_sp_data_now = away_sp_data_now.iloc[0]
                col = []
                for c in away_sp_data_now.index:
                    c = 'Away_' + c
                    col.append(c)
                away_sp_data_now.index = col
                away_sp_data_now_dict = dict(away_sp_data_now)
                data_one = dict(**data_one,**away_sp_data_now_dict)
                data_all.append(data_one)
                print(f"{date} {home} vs {away} successful!!")
        df_sp = pd.DataFrame(data_all)
        df_sp.set_index('Date',inplace=True)
        df_sp['Home_球隊'] = df_sp['Home_球隊'].replace('勝','1').replace('負','0').replace(np.nan,'-1')
        df_sp['Home_投手'] = df_sp['Home_投手'].replace('勝','1').replace('負','0').replace(np.nan,'-1')
        df_sp['Away_球隊'] = df_sp['Away_球隊'].replace('勝','1').replace('負','0').replace(np.nan,'-1')
        df_sp['Away_投手'] = df_sp['Away_投手'].replace('勝','1').replace('負','0').replace(np.nan,'-1')
        df_sp.to_excel(f"{self.path}/sp_data.xlsx")
        df_sp = pd.read_excel(f"{self.path}/sp_data.xlsx",index_col='Date')
        return df_sp
    
    #球隊基本數據抓取
    def pitcher_data(self,df_base_and_sp):
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            date = df_n_notomorrow.index[event]
            home = df_n_notomorrow["主隊"][event]
            away = df_n_notomorrow["客隊"][event]
            eventcode = df_n_notomorrow['game_href'][event]
            start_parm = {
                "executablePath" : f"{self.excutable_path}",
                "headless" : True,
                "args" : ['--disable-infobars',
                          '-log-level=30',
                          '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
                          '--no-sadbox',
                          '--start-maximized'          
                ],
            }
            browser = await launch(**start_parm)
            page = await browser.newPage()
            tk_ = tkinter.Tk()
            width = tk_.winfo_screenwidth()
            heigh = tk_.winfo_screenwidth()
            tk_.quit()
            await page.setViewport(viewport={'width':width,'height':heigh}) 

            js_text = """
            () =>{
                Object.defineProperties(navigator,{ webdriver:{ get:() => false}});
                window.navigator.chrom = { runtime: {}, };
                Object.defineProperty(navigator, 'languages',{get:() => ['en-US','en']});
                Object.defineProperty(navigator, 'plugins',{get:() => [1,2,3,4,5,6],});
            }"""
            await page.evaluateOnNewDocument(js_text)
            url = eventcode
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            #await asyncio.sleep(3)
            await page.goto(url,options = options )
            html = await page.content()
            data_one = {
                "Date" :date,
                "主隊" : home,
                "客隊" : away,
                "game_href" : eventcode,
                "html" : html
            }
            data_all.append(data_one)
            print(str(eventcode) + " web crawler successful!!")
            await browser.close()




        if __name__ == '__main__':
            data_all = []
            df_n_notomorrow = df_base_and_sp[df_base_and_sp.index < self.matchdate.strftime("%Y-%m-%d")]
            loop = asyncio.get_event_loop()
            for i in range(0,len(df_n_notomorrow),5):
                if ((i+5) % len(df_n_notomorrow)) < 5:
                    mi = 5 - ((i+5) - len(df_n_notomorrow))
                else:
                    mi = 5
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+mi)]
                loop.run_until_complete(asyncio.wait(tasks))
                if ((i+5) >= len(df_n_notomorrow)):
                    data_html = []
                    for html in range(len(data_all)):
                        date = data_all[html]['Date']
                        home = data_all[html]["主隊"]
                        away = data_all[html]["客隊"]
                        eventcode = data_all[html]['game_href']
                        html_data = data_all[html]['html']
                        data_0 = {
                            "Date" :date,
                            "主隊" : home,
                            "客隊" : away,
                            "game_href" : eventcode
                        }
                        soup = BeautifulSoup(html_data, 'lxml')
                        tr = soup.find_all("tr",{"class":"column-subtotal"})
                        table_bullpen = soup.find_all("table",{"class":"table table-bordered table-striped"})
                        #客隊打擊
                        th = tr[0].find_all("th")
                        data_1 = {
                            "game_href" : eventcode,
                            "Away_batting_打數" : th[1].text,
                            "Away_batting_得分" : th[2].text,
                            "Away_batting_安打" : th[3].text,
                            "Away_batting_全壘打" : th[4].text,
                            "Away_batting_打點" : th[5].text,
                            "Away_batting_保送" : th[6].text,
                            "Away_batting_三振" : th[7].text,
                            "Away_batting_打擊" : th[8].text,
                        }
                        #客隊投球
                        th = tr[2].find_all("th")
                        data_2 = {
                            "Away_patching_局數" : th[1].text,
                            "Away_patching_安打" : th[2].text,
                            "Away_patching_失分" : th[3].text,
                            "Away_patching_責失" : th[4].text,
                            "Away_patching_四壞" : th[5].text,
                            "Away_patching_三振" : th[6].text,
                            "Away_patching_全壘打" : th[7].text,
                            "Away_patching_防禦率" : th[8].text,
                        }
                        #牛棚投球
                        th_sp = table_bullpen[2].find("tbody").find("tr").find_all("th")
                        data_5 = {
                            "Away_bullpenpatching_局數" : round(float(th[1].text) - float(th_sp[1].text),2),
                            "Away_bullpenpatching_安打" : round(int(th[2].text) - int(th_sp[2].text),2),
                            "Away_bullpenpatching_失分" : round(int(th[3].text) - int(th_sp[3].text),2),
                            "Away_bullpenpatching_責失" : round(int(th[4].text) - int(th_sp[4].text),2),
                            "Away_bullpenpatching_四壞" : round(int(th[5].text) - int(th_sp[5].text),2),
                            "Away_bullpenpatching_三振" : round(int(th[6].text) - int(th_sp[6].text),2),
                            "Away_bullpenpatching_全壘打" : round(int(th[7].text) - int(th_sp[7].text),2),
                        }
                        #主隊打擊
                        th = tr[1].find_all("th")
                        data_3 = {
                            "Home_batting_打數" : th[1].text,
                            "Home_batting_得分" : th[2].text,
                            "Home_batting_安打" : th[3].text,
                            "Home_batting_全壘打" : th[4].text,
                            "Home_batting_打點" : th[5].text,
                            "Home_batting_保送" : th[6].text,
                            "Home_batting_三振" : th[7].text,
                            "Home_batting_打擊" : th[8].text,
                        }
                        #主隊投球
                        th = tr[3].find_all("th")
                        data_4 = {
                            "Home_patching_局數" : th[1].text,
                            "Home_patching_安打" : th[2].text,
                            "Home_patching_失分" : th[3].text,
                            "Home_patching_責失" : th[4].text,
                            "Home_patching_四壞" : th[5].text,
                            "Home_patching_三振" : th[6].text,
                            "Home_patching_全壘打" : th[7].text,
                            "Home_patching_防禦率" : th[8].text,
                        }
                        #牛棚投球
                        th_sp = table_bullpen[3].find("tbody").find("tr").find_all("th")
                        data_6 = {
                            "Home_bullpenpatching_局數" : round(float(th[1].text) - float(th_sp[1].text),2),
                            "Home_bullpenpatching_安打" : round(int(th[2].text) - int(th_sp[2].text),2),
                            "Home_bullpenpatching_失分" : round(int(th[3].text) - int(th_sp[3].text),2),
                            "Home_bullpenpatching_責失" : round(int(th[4].text) - int(th_sp[4].text),2),
                            "Home_bullpenpatching_四壞" : round(int(th[5].text) - int(th_sp[5].text),2),
                            "Home_bullpenpatching_三振" : round(int(th[6].text) - int(th_sp[6].text),2),
                            "Home_bullpenpatching_全壘打" : round(int(th[7].text) - int(th_sp[7].text),2),
                        }
                        data = {**data_0,**data_1, **data_2, **data_3, **data_4, **data_5, **data_6}
                        data_html.append(data)
                        print(f"{date} {home} v.s {away} successful!!")
                    df_boxscore = pd.DataFrame(data_html)
                    df_boxscore.index = df_boxscore["Date"]
                    df_boxscore.drop("Date",axis = 1,inplace=True)
                    df_boxscore.to_excel(f"{self.path}/boxscore.xlsx")
                    df_boxscore_before = pd.read_excel(f"{self.path_b}/boxscore_all.xlsx",index_col='Date')
                    df_boxscore_before = df_boxscore_before.sort_index()
                    df_boxscore_before = df_boxscore_before[df_boxscore_before.index < self.yesterday.strftime("%Y-%m-%d")]
                    df_boxscore_all = df_boxscore_before.append(df_boxscore)
                    df_boxscore_all = df_boxscore_all.sort_index()
                    df_boxscore_all.to_excel(f"{self.path}/boxscore_all.xlsx")
                    return df_boxscore_all
    
    #賠率網址抓取
    def oddsportal_href(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(options=options)
        data_all = []
        url = f"https://www.oddsportal.com/baseball/japan/npb/results/#/page/1/"
        browser.get(url)
        browser.get(url)
        browser.execute_script('window.scrollTo(0, 3000)')
        sleep(1)
        browser.execute_script('window.scrollTo(0, 3000)')
        sleep(1)
        browser.execute_script('window.scrollTo(0, 3000)')
        sleep(1)
        soup = BeautifulSoup(browser.page_source,"lxml")
        span = soup.find("div",{"id":"pagination"}).find_all("span")
        a = soup.find_all("a",{'class':"flex items-start justify-start min-w-0 gap-1 cursor-pointer justify-content next-m:!items-center next-m:!justify-center min-sm:min-w-[180px] next-m:!gap-2"})
        for j in range(len(a)):
            href = a[j].get("href")
            data_all.append(href)
            print(f"{href} successfull!!")
        df_href = pd.DataFrame(data_all,columns=['href'])
        return df_href
    
    #更新昨日賠率
    def oddsportal_odds_before(self,df_href):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(options=options)

        data_html = []
        for event in range(len(df_href)):
            href = df_href['href'].iloc[event]
            url = f"https://www.oddsportal.com{href}"
            print(f'crawer {url}')
            browser.get(url)
            browser.get(url)
            # 等待 Body 載入
            wait = WebDriverWait(browser, 10)
            element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)
            soup = BeautifulSoup(browser.page_source,"lxml")
            hometeam = soup.find('p',{'class':'max-sm:w-full order-first max-mm:!order-last truncate min-mm:!ml-auto h-7 flex-center'}).text
            awayteam = soup.find('p',{'class':'truncate h-7 flex-center'}).text
            matchtime = datetime.strptime(soup.find('div',{'class':'flex text-xs font-normal text-gray-dark font-main item-center gap-1'}).text.split(",")[1].replace("\xa0"," "),'%d %b  %Y')
            if  matchtime >= datetime.strptime(self.yesterday.strftime("%Y-%m-%d"),"%Y-%m-%d"):
                if matchtime.strftime("%Y-%m-%d") < self.matchdate.strftime("%Y-%m-%d"):
                    homescore = soup.find('div',{'class':'flex flex-wrap w-full gap-2 text-gray-dark'}).text
                    awayscore = soup.find('div',{'class':'flex-wrap gap-2 flex-center max-sm:mr-0 text-gray-dark'}).text
                elif self.matchdate.strftime("%Y-%m-%d") < datetime.now().strftime("%Y-%m-%d"):
                    homescore = soup.find('div',{'class':'flex flex-wrap w-full gap-2 text-gray-dark'}).text
                    awayscore = soup.find('div',{'class':'flex-wrap gap-2 flex-center max-sm:mr-0 text-gray-dark'}).text   
                else:
                    homescore = np.nan
                    awayscore = np.nan
                odds = soup.find("div",{"class":"flex text-xs h-9 border-b border-black-borders border-l border-r bg-gray-light"}).find_all("p",{"class":"height-content"})
                homeodds = odds[1].text
                awayodds = odds[2].text
                odds_return = odds[3].text
                data_odds = {
                    'Date' : matchtime,
                    "主隊" : hometeam,
                    "主隊得分" : homescore,
                    "客隊" : awayteam,
                    "客隊得分" : awayscore,
                    "Homeodds" : homeodds,
                    "Awayodds" : awayodds,
                    "Odds_return" : odds_return
                }
                data_html.append(data_odds)
                print(f"{matchtime} {hometeam} vs {awayteam} insert data successful!!")
        df_all = pd.DataFrame(data_html)
        df_all.index = df_all['Date']
        df_all = df_all.sort_index()
        df_all.drop('Date',axis=1,inplace=True)
        df_all.to_excel(f"{self.path}/odds.xlsx")
        df_all = pd.read_excel(f"{self.path}/odds.xlsx",index_col='Date')
        df_all.index = pd.to_datetime(df_all.index.strftime("%Y-%m-%d"))
        df_all['主隊'] = df_all['主隊'].replace(self.teams_changename_en)
        df_all['客隊'] = df_all['客隊'].replace(self.teams_changename_en)
        df_all['Odds_return'] = df_all['Odds_return'].apply(lambda x:x.replace("%",''))
        return df_all
    
    #抓取最新賽事的賠率
    def oddsportal_odds(self,df_href):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(options=options)
        start_year = self.matchdate.year
        end_year = self.matchdate.year+1
        data_all = []
        url = f"https://www.oddsportal.com/baseball/japan/npb/"
        browser.get(url)
        soup = BeautifulSoup(browser.page_source,"lxml")
        span = soup.find("div",{"class":"flex flex-col w-full text-xs eventRow"})
        a = soup.find_all("a",{'class':"flex items-start justify-start min-w-0 gap-1 cursor-pointer justify-content next-m:!items-center next-m:!justify-center min-sm:min-w-[180px] next-m:!gap-2"})
        for j in range(len(a)):
            href = a[j].get("href")
            data_all.append(href)
            print(f"{href} successfull!!")

        df_href = pd.DataFrame(data_all,columns=['href'])
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            href = df_href['href'].iloc[event]
            start_parm = {
                "executablePath" : f"{self.excutable_path}",
                "headless" : True,
                "args" : ['--disable-infobars',
                          '-log-level=30',
                          '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
                          '--no-sadbox',
                          '--start-maximized'          
                ],
            }
            browser = await launch(**start_parm)
            page = await browser.newPage()
            tk_ = tkinter.Tk()
            width = tk_.winfo_screenwidth()
            heigh = tk_.winfo_screenwidth()
            tk_.quit()
            await page.setViewport(viewport={'width':width,'height':heigh}) 

            js_text = """
            () =>{
                Object.defineProperties(navigator,{ webdriver:{ get:() => false}});
                window.navigator.chrom = { runtime: {}, };
                Object.defineProperty(navigator, 'languages',{get:() => ['en-US','en']});
                Object.defineProperty(navigator, 'plugins',{get:() => [1,2,3,4,5,6],});
            }"""
            await page.evaluateOnNewDocument(js_text)
            url = f"https://www.oddsportal.com{href}"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            await asyncio.sleep(3)
            #await page.goto(url,options = options )
            html = await page.content()
            data_one = {
                "html" : html
            }
            data_all.append(data_one)
            print(str(href) + " web crawler successful!!")
            await browser.close()

        if __name__ == '__main__':
            data_all = []
            loop = asyncio.get_event_loop()
            for i in range(0,len(df_href),5):
                if ((i+5) % len(df_href)) < 5:
                    mi = 5 - ((i+5) - len(df_href))
                else:
                    mi = 5
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+mi)]
                loop.run_until_complete(asyncio.wait(tasks))
                if ((i+5) >= len(df_href)):
                    data_html = []
                    for html in range(len(data_all)):
                        try:
                            html_data = data_all[html]['html']
                            soup = BeautifulSoup(html_data, 'lxml')
                            hometeam = soup.find('p',{'class':'max-sm:w-full order-first max-mm:!order-last truncate min-mm:!ml-auto h-7 flex-center'}).text
                            awayteam = soup.find('p',{'class':'truncate h-7 flex-center'}).text
                            matchtime = datetime.strptime(soup.find('div',{'class':'flex text-xs font-normal text-gray-dark font-main item-center gap-1'}).text.replace("Today,",""),'%d %b  %Y,%H:%M')
                            if  matchtime >= datetime.strptime(self.yesterday.strftime("%Y-%m-%d"),"%Y-%m-%d"):
                                if matchtime.strftime("%Y-%m-%d") < self.matchdate.strftime("%Y-%m-%d"):
                                    homescore = soup.find('div',{'class':'flex flex-wrap w-full gap-2 text-gray-dark'}).text
                                    awayscore = soup.find('div',{'class':'flex-wrap gap-2 flex-center max-sm:mr-0 text-gray-dark'}).text
                                else:
                                    homescore = np.nan
                                    awayscore = np.nan
                                odds = soup.find("div",{"class":"flex text-xs h-9 border-b border-black-borders border-l border-r bg-gray-light"}).find_all("p",{"class":"height-content"})
                                homeodds = odds[1].text
                                awayodds = odds[2].text
                                odds_return = odds[3].text
                                data_odds = {
                                    'Date' : matchtime,
                                    "主隊" : hometeam,
                                    "主隊得分" : homescore,
                                    "客隊" : awayteam,
                                    "客隊得分" : awayscore,
                                    "Homeodds" : homeodds,
                                    "Awayodds" : awayodds,
                                    "Odds_return" : odds_return
                                }
                                data_html.append(data_odds)
                                print(f"{matchtime} {hometeam} vs {awayteam} insert data successful!!")
                        except:
                            print(f"{matchtime} {hometeam} vs {awayteam} insert data fail!!")
                    if len(data_html) != 0:
                        df_all2 = pd.DataFrame(data_html)
                        df_all2.index = df_all2['Date']
                        df_all2 = df_all2.sort_index()
                        df_all2.drop('Date',axis=1,inplace=True)
                        df_all2.to_excel(f"{self.path}/odds_now.xlsx")
                    else:
                        print('no any odds data!!')
        df_all2 = pd.read_excel(f"{self.path}/odds_now.xlsx",index_col='Date')
        return df_all2
    
    #球隊勝率計算
    def update_winrate(self,all_sch):
        teams = ['西武獅', '讀賣巨人', '日本火腿鬥士', '歐力士猛牛', '橫濱DeNA灣星', '中日龍', '阪神虎',
           '養樂多燕子', '軟體銀行鷹', '樂天金鷹', '廣島東洋鯉魚', '羅德海洋']
        for team in teams:
            team_windata = []
            #找出主客是該隊伍的比賽
            team_data = all_sch[(all_sch['主隊'] == team) | (all_sch['客隊'] == team)]
            #戰績初始化
            team_win = 0
            team_lose = 0
            team_tie = 0

            team_season_win = 0
            team_season_lose = 0
            team_season_tie = 0

            team_inhome_win = 0
            team_inhome_lose = 0
            team_inhome_tie = 0

            team_inhome_season_win = 0
            team_inhome_season_lose = 0
            team_inhome_season_tie = 0

            team_inaway_win = 0
            team_inaway_lose = 0
            team_inaway_tie = 0

            team_inaway_season_win = 0
            team_inaway_season_lose = 0
            team_inaway_season_tie = 0
            for d in range(len(team_data)):
                date = team_data.index[d]
                #賽季不同時初始化
                if (d !=0) and (team_data.index[d-1].year != date.year):
                    team_season_win = 0
                    team_season_lose = 0
                    team_season_tie = 0
                    team_inhome_season_win = 0
                    team_inhome_season_lose = 0
                    team_inhome_season_tie = 0
                    team_inaway_season_win = 0
                    team_inaway_season_lose = 0
                    team_inaway_season_tie = 0

                eventcode = team_data['Eventcode'].iloc[d]
                hometeam = team_data['主隊'].iloc[d]
                awayteam = team_data['客隊'].iloc[d]
                homescore = team_data['主隊得分'].iloc[d]
                awayscore = team_data['客隊得分'].iloc[d]
                #判斷勝負
                if team == hometeam:
                    if homescore > awayscore:
                        team_win += 1
                        team_season_win += 1

                        team_inhome_win += 1
                        team_inhome_season_win += 1
                    elif homescore < awayscore:
                        team_lose += 1
                        team_season_lose += 1

                        team_inhome_lose += 1
                        team_inhome_season_lose += 1 
                    else:
                        team_tie += 1
                        team_season_tie += 1

                        team_inhome_tie += 1 
                        team_inhome_season_tie += 1
                else:
                    if homescore < awayscore:
                        team_win += 1
                        team_season_win += 1

                        team_inaway_win += 1
                        team_inaway_season_win += 1
                    elif homescore > awayscore:
                        team_lose += 1
                        team_season_lose += 1

                        team_inaway_lose += 1
                        team_inaway_season_lose += 1
                    else:
                        team_tie += 1
                        team_season_tie += 1

                        team_inaway_tie += 1
                        team_inaway_season_tie +=1

                #計算勝率
                game = (team_win + team_lose + team_tie)
                game_season = (team_season_win + team_season_lose + team_season_tie)

                game_inhome = (team_inhome_win + team_inhome_lose + team_inhome_tie)
                game_inhome_season = (team_inhome_season_win + team_inhome_season_lose + team_inhome_season_tie)

                game_inaway = (team_inaway_win + team_inaway_lose + team_inaway_tie)
                game_inaway_season = (team_inaway_season_win + team_inaway_season_lose + team_inaway_season_tie)


                try:
                    team_winrate = round(team_win / game,2)
                except:
                    team_winrate = 0
                try:
                    team_season_winrate = round(team_season_win / game_season,2)
                except:
                    team_season_winrate = 0
                try:
                    team_inhome_winrate = round(team_inhome_win / game_inhome,2)
                except:
                    team_inhome_winrate = 0
                try:
                    team_inhome_season_winrate = round(team_inhome_season_win / game_inhome_season,2)
                except:
                    team_inhome_season_winrate = 0
                try:
                    team_inaway_winrate = round(team_inaway_win / game_inaway,2)
                except:
                    team_inaway_winrate = 0
                try:
                    team_inaway_season_winrate = round(team_inaway_season_win / game_inaway_season,2)
                except:
                    team_inaway_season_winrate = 0
                team_one = {
                    "Date" : date,
                    "Eventcode" : eventcode,
                    "主隊" : hometeam,
                    "主隊得分" : homescore,
                    "客隊" : awayteam,
                    "客隊得分" : awayscore,
                    #總成績
                    "Game_InTotal" : game,
                    "Win_InTotal" : team_win,
                    "Lose_InTotal" : team_lose,
                    "Tie_InTotal" : team_tie,
                    "WinRate_InTotal" : team_winrate,
                    #賽季總成績
                    "Game_InSeason" : game_season,
                    "Win_InSeason" : team_season_win,
                    "Lose_InSeason" : team_season_lose,
                    "Tie_InSeason" : team_season_tie,
                    "WinRate_InSeason" : team_season_winrate,
                    #總主場成績
                    "Game_inhome_InTotal" : game_inhome,
                    "Win_inhome_InTotal" : team_inhome_win,
                    "Lose_inhome_InTotal" : team_inhome_lose,
                    "Tie_inhome_InTotal" : team_inhome_tie,
                    "WinRate_inhome_InTotal" : team_inhome_winrate,
                    #賽季主場成績
                    "Game_inhome_InSeason" : game_inhome_season,
                    "Win_inhome_InSeason" : team_inhome_season_win,
                    "Lose_inhome_InSeason" : team_inhome_season_lose,
                    "Tie_inhome_InSeason" : team_inhome_season_tie,
                    "WinRate_inhome_InSeason" : team_inhome_season_winrate,
                    #總客場成績
                    "Game_inaway_InTotal" : game_inaway,
                    "Win_inaway_InTotal" : team_inaway_win,
                    "Lose_inaway_InTotal" : team_inaway_lose,
                    "Tie_inaway_InTotal" : team_inaway_tie,
                    "WinRate_inaway_InTotal" : team_inaway_winrate,
                    #賽季主場成績
                    "Game_inaway_InSeason" : game_inaway_season,
                    "Win_inaway_InSeason" : team_inaway_season_win,
                    "Lose_inaway_InSeason" : team_inaway_season_lose,
                    "Tie_inaway_InSeason" : team_inaway_season_tie,
                    "WinRate_inaway_InSeason" : team_inaway_season_winrate,  
                }
                team_windata.append(team_one)
            df_teams = pd.DataFrame(team_windata)
            df_teams.set_index('Date',inplace=True)
            df_teams.to_excel(f"{self.path}/{team}.xlsx")
    
    
    def winrateate_data(self,df_base_and_sp3):
        西武獅 = pd.read_excel(f"{self.path}/{'西武獅'}.xlsx",index_col='Date')
        讀賣巨人 = pd.read_excel(f"{self.path}/{'讀賣巨人'}.xlsx",index_col='Date')
        日本火腿鬥士 = pd.read_excel(f"{self.path}/{'日本火腿鬥士'}.xlsx",index_col='Date')
        歐力士猛牛 = pd.read_excel(f"{self.path}/{'歐力士猛牛'}.xlsx",index_col='Date')
        橫濱DeNA灣星 = pd.read_excel(f"{self.path}/{'橫濱DeNA灣星'}.xlsx",index_col='Date')
        中日龍 = pd.read_excel(f"{self.path}/{'中日龍'}.xlsx",index_col='Date')
        阪神虎 = pd.read_excel(f"{self.path}/{'阪神虎'}.xlsx",index_col='Date')
        養樂多燕子 = pd.read_excel(f"{self.path}/{'養樂多燕子'}.xlsx",index_col='Date')
        軟體銀行鷹 = pd.read_excel(f"{self.path}/{'軟體銀行鷹'}.xlsx",index_col='Date')
        樂天金鷹 = pd.read_excel(f"{self.path}/{'樂天金鷹'}.xlsx",index_col='Date')
        廣島東洋鯉魚 = pd.read_excel(f"{self.path}/{'廣島東洋鯉魚'}.xlsx",index_col='Date')
        羅德海洋 = pd.read_excel(f"{self.path}/{'羅德海洋'}.xlsx",index_col='Date')
        self.team_name=  {
            '西武獅' : 西武獅,
            '讀賣巨人':讀賣巨人, 
            '日本火腿鬥士':日本火腿鬥士, 
            '歐力士猛牛':歐力士猛牛, 
            '橫濱DeNA灣星':橫濱DeNA灣星, 
            '中日龍':中日龍, 
            '阪神虎':阪神虎,
            '養樂多燕子':養樂多燕子, 
            '軟體銀行鷹':軟體銀行鷹, 
            '樂天金鷹':樂天金鷹, 
            '廣島東洋鯉魚':廣島東洋鯉魚, 
            '羅德海洋':羅德海洋
        }
        data_all = []
        for i in range(len(df_base_and_sp3)):
            date = df_base_and_sp3.index[i]
            hometeam = df_base_and_sp3['主隊'].iloc[i]
            awayteam = df_base_and_sp3['客隊'].iloc[i]
            eventcode = df_base_and_sp3['Eventcode'].iloc[i]
            data_one = {
                "Date" : date,
                "主隊" : hometeam,
                "客隊" : awayteam,
                "Eventcode" : eventcode
            }
            #主隊戰況
            home_data =self.team_name[hometeam].copy()
            lastbefore_data = home_data[home_data.index < date].sort_index().iloc[-1,5:]
            team_data = dict(lastbefore_data)
            new_Hometeam_data = {}
            for key,value in team_data.items():
                new_key = f"Home_{key}"
                new_Hometeam_data[new_key] = value
            data_one = dict(**data_one,**new_Hometeam_data)

            #客隊戰況
            away_data = self.team_name[awayteam].copy()
            lastbefore_data = away_data[away_data.index < date].sort_index().iloc[-1,5:]
            team_data = dict(lastbefore_data)
            new_Awayteam_data = {}
            for key,value in team_data.items():
                new_key = f"Away_{key}"
                new_Awayteam_data[new_key] = value
            data_one = dict(**data_one,**new_Awayteam_data)
            data_all.append(data_one)
            print(f"{date} {eventcode} successful!!")
        df_winrate = pd.DataFrame(data_all)
        df_winrate.set_index('Date',inplace=True)
        df_winrate.to_excel(f"{self.path}/winrate.xlsx")
        df_winrate = pd.read_excel(f"{self.path}/winrate.xlsx",index_col='Date')
        return df_winrate
    
    def rank(self,df_base_and_sp4):
        for type_ in ['rank_total','rank_season','rank_inhome','rank_inhome_season','rank_inaway','rank_inaway_season']:
            with open(f"{self.path_b}/{type_}", "rb") as f:
                if type_ == 'rank_total':
                    rank_total = pickle.load(f)
                elif type_ == 'rank_season':
                    rank_season = pickle.load(f)
                elif type_ == 'rank_inhome':
                    rank_inhome = pickle.load(f)
                elif type_ == 'rank_inhome_season':
                    rank_inhome_season = pickle.load(f)
                elif type_ == 'rank_inaway':
                    rank_inaway = pickle.load(f)
                elif type_ == 'rank_inaway_season':
                    rank_inaway_season = pickle.load(f)
        data_all = []
        for i in range(len(df_base_and_sp4)):
            date = df_base_and_sp4.index[i]
            eventcode = df_base_and_sp4['Eventcode'].iloc[i]
            home = df_base_and_sp4['主隊'].iloc[i]
            away = df_base_and_sp4['客隊'].iloc[i]
            data_one = {
                "Date" : date,
                "主隊" : home,
                "客隊" : away,
                "Eventcode" : eventcode
            }
            rank_total[home] = df_base_and_sp4['Home_WinRate_InTotal'].iloc[i]
            rank_season[home]  = df_base_and_sp4['Home_WinRate_InSeason'].iloc[i]
            rank_inhome[home] = df_base_and_sp4['Home_WinRate_inhome_InTotal'].iloc[i]
            rank_inhome_season[home] = df_base_and_sp4['Home_WinRate_inhome_InSeason'].iloc[i]
            rank_inaway[home] = df_base_and_sp4['Home_WinRate_inaway_InTotal'].iloc[i]
            rank_inaway_season[home] = df_base_and_sp4['Home_WinRate_inaway_InSeason'].iloc[i]
            rank_total[away]  = df_base_and_sp4['Away_WinRate_InTotal'].iloc[i]
            rank_season[away]   = df_base_and_sp4['Away_WinRate_InSeason'].iloc[i]
            rank_inhome[away]   = df_base_and_sp4['Away_WinRate_inhome_InTotal'].iloc[i]
            rank_inhome_season[away]   = df_base_and_sp4['Away_WinRate_inhome_InSeason'].iloc[i]
            rank_inaway[away]   = df_base_and_sp4['Away_WinRate_inaway_InTotal'].iloc[i]
            rank_inaway_season[away]   = df_base_and_sp4['Away_WinRate_inaway_InSeason'].iloc[i]

            rank_title = [rank_total,rank_season,rank_inhome,rank_inhome_season,rank_inaway,rank_inaway_season]
            rank_name= ["Rank_Total","Rank_Season","Rank_InHome","Rank_InHome_Season","Rank_InAway","Rank_InAway_Season"]
            #主隊
            for rank,name in zip(rank_title,rank_name):
                sorted_rank = sorted(rank.items(), key=lambda x: x[1], reverse=True)
                for s in range(len(sorted_rank)):
                    if sorted_rank[s][0] == home:
                        rank_one = {
                            f"Home_{name}" : s+1
                        }
                        data_one = dict(**data_one,**rank_one)
                        break
            #客隊       
            for rank,name in zip(rank_title,rank_name):
                sorted_rank = sorted(rank.items(), key=lambda x: x[1], reverse=True)
                for s in range(len(sorted_rank)):
                    if sorted_rank[s][0] == away:
                        rank_one = {
                            f"Away_{name}" : s+1
                        }
                        data_one = dict(**data_one,**rank_one)
                        break

            data_all.append(data_one)
            print(f"{date} {eventcode} successful!!")
        rank_df = pd.DataFrame(data_all)
        rank_df.set_index('Date',inplace=True)
        rank_df.to_excel(f"{self.path}/rank.xlsx")
        for dict_,type_ in zip([rank_total,rank_season,rank_inhome,rank_inhome_season,rank_inaway,rank_inaway_season],['rank_total','rank_season','rank_inhome','rank_inhome_season','rank_inaway','rank_inaway_season']):
            with open(f"{self.path}/{type_}", "wb") as f:
                pickle.dump(dict_, f)
        rank_df = pd.read_excel(f"{self.path}/rank.xlsx",index_col='Date')
        return rank_df
    
    #更新ELO
    def elo(self,df_base_and_sp5):
        tf = open(f"{self.path_b}/ELO_aftre.json", "r")
        ELO_first = json.load(tf)
        df_yesterday = df_base_and_sp5[df_base_and_sp5.index <= self.matchdate.strftime("%Y-%m-%d")]
        df_yesterday = df_yesterday[(df_yesterday['主隊得分'] != df_yesterday['客隊得分'])  ]
        df_yesterday['W/L'] = np.where(np.isnan(df_yesterday['主隊得分']) & np.isnan(df_yesterday['客隊得分']), np.nan, (df_yesterday['主隊得分'] > df_yesterday['客隊得分'])*1)
        ELO_all = []
        for i in range(len(df_yesterday)):
            date = df_yesterday.index[i]
            away_team = df_yesterday["客隊"][i]
            home_team = df_yesterday["主隊"][i]
            df_eventcode = df_yesterday['Eventcode'][i]
            ELO_one = {
                "客隊ELO" : round(ELO_first[away_team],4),
                "主隊ELO" : round(ELO_first[home_team],4)
            }
            ELO_all.append(ELO_one)
            if date < self.matchdate:
                if (self.remake == True) and (i == 0):
                    for e in ELO_first:
                        ELO_first[e] = 1500 + (ELO_first[e]*0.3)        
                if ELO_first[away_team] >= 2400:
                    k_a = 16
                elif ELO_first[away_team] >= 2100:
                    k_a = 24
                else:
                    k_a = 36
                if ELO_first[home_team] >= 2400:
                    k_h = 16
                elif ELO_first[home_team] >= 2100:
                    k_h = 24
                else:
                    k_h = 36
                Ra = ELO_first[away_team]
                Rb = ELO_first[home_team]
                Ea = 1 / (1 + 10**((Rb - Ra)/400))
                Eb = 1 / (1 + 10**((Ra - Rb)/400))
                Sa = df_yesterday["W/L"][i]
                if Sa == 0:
                    ELO_first[away_team] +=  (k_a * (1 - Ea))
                    ELO_first[home_team] += -(k_h * (1 - Ea))
                elif Sa == 1:
                    ELO_first[away_team] += -(k_a * (1 - Ea))
                    ELO_first[home_team] +=  (k_h * (1 - Ea))
                print(f"{df_yesterday.index[i]} {away_team} vs {home_team} 結果為 客隊:{round(ELO_first[away_team],4)} 主隊:{round(ELO_first[home_team],4)}")
        elo_a = pd.DataFrame(ELO_all)
        elo_a.index = df_yesterday.index
        df_yesterday["客隊ELO"] = elo_a["客隊ELO"]
        df_yesterday["主隊ELO"] = elo_a["主隊ELO"]
        df_yesterday.to_excel(f"{self.path}/data_base_sp_elo.xlsx")
        df_yesterday = pd.read_excel(f"{self.path}/data_base_sp_elo.xlsx",index_col='Date')
        with open(f"{self.path}/ELO_aftre.json", "w") as f:
            json.dump(ELO_first, f)
        return df_yesterday
    
    #計算進階數據
    def argumentvanced_data(self,boxscore_all,df_yesterday):
        matchtime = df_yesterday.index.unique()
        era_avg = []
        fip_avg = []
        whip_avg = []
        k9_avg= []
        bat_avg = []
        for i in matchtime:
            year = i.year - 1
            before_data = boxscore_all[(boxscore_all.index < i) & (boxscore_all.index >= str(year))]

            #era
            earned = before_data['Home_patching_失分'].sum() + before_data['Away_patching_失分'].sum()
            inning = before_data['Home_patching_局數'].sum() + before_data['Away_patching_局數'].sum()
            era_avg_now = (earned / inning) * 9
            era_avg_dict = {
                "Date" : i,
                "ERA_avg" : era_avg_now
            }
            era_avg.append(era_avg_dict)

            #fip
            hr = before_data['Home_patching_全壘打'].sum() + before_data['Away_patching_全壘打'].sum()
            bb_hbp = before_data['Home_batting_保送'].sum() + before_data['Away_batting_保送'].sum()
            k = before_data['Home_patching_三振'].sum() + before_data['Away_patching_三振'].sum()
            fip_avg_now = (hr*13 + bb_hbp*3 - k*2) / inning + 3.2
            fip_avg_dict = {
                "Date" : i,
                "FIP_avg" : fip_avg_now
            }
            fip_avg.append(fip_avg_dict)

            #whip
            h = before_data['Home_patching_安打'].sum() + before_data['Away_patching_安打'].sum()
            bb = before_data['Home_patching_四壞'].sum() + before_data['Away_patching_四壞'].sum()
            whip_avg_now = (h+bb) / inning 
            whip_avg_dict = {
                "Date" : i,
                "WHIP_avg" : whip_avg_now
            }
            whip_avg.append(whip_avg_dict)

            #K9
            k9_avg_now = (k / inning)*9
            k9_avg_dict = {
                "Date" : i,
                "K9_avg" : k9_avg_now
            }
            k9_avg.append(k9_avg_dict)


        era_avg_df = pd.DataFrame(era_avg)
        era_avg_df.set_index('Date',inplace=True)

        fip_avg_df = pd.DataFrame(fip_avg)
        fip_avg_df.set_index('Date',inplace=True)

        whip_avg_df = pd.DataFrame(whip_avg)
        whip_avg_df.set_index('Date',inplace=True)

        k9_avg_df = pd.DataFrame(k9_avg)
        k9_avg_df.set_index('Date',inplace=True)
        df_argumentvanced = df_yesterday.merge(era_avg_df,on=['Date'])
        df_argumentvanced = df_argumentvanced.merge(fip_avg_df,on=['Date'])
        df_argumentvanced = df_argumentvanced.merge(whip_avg_df,on=['Date'])
        df_argumentvanced = df_argumentvanced.merge(k9_avg_df,on=['Date'])
        df_argumentvanced = df_argumentvanced[df_argumentvanced['ERA_avg'].isna() ==False]
        df_argumentvanced['Home_patching_ERA+'] = df_argumentvanced['ERA_avg'] - (df_argumentvanced['Home_patching_失分'] / df_argumentvanced['Home_patching_局數'].replace(0,1))
        df_argumentvanced['Away_patching_ERA+'] = df_argumentvanced['ERA_avg'] - (df_argumentvanced['Away_patching_失分'] / df_argumentvanced['Away_patching_局數'].replace(0,1))

        df_argumentvanced['Home_bullpenpatching_ERA+'] = df_argumentvanced['ERA_avg'] - (df_argumentvanced['Home_bullpenpatching_失分'] / df_argumentvanced['Home_bullpenpatching_局數'].replace(0,1))
        df_argumentvanced['Away_bullpenpatching_ERA+'] = df_argumentvanced['ERA_avg'] - (df_argumentvanced['Away_bullpenpatching_失分'] / df_argumentvanced['Away_bullpenpatching_局數'].replace(0,1))

        df_argumentvanced['Home_ERA+'] = df_argumentvanced['ERA_avg'] - (df_argumentvanced['Home_失分'] / df_argumentvanced['Home_局數'].replace(0,1))
        df_argumentvanced['Away_ERA+'] = df_argumentvanced['ERA_avg'] - (df_argumentvanced['Away_失分'] / df_argumentvanced['Away_局數'].replace(0,1))


        home_FIP = (df_argumentvanced['Home_patching_全壘打']*13 + df_argumentvanced['Home_batting_保送']*3 - df_argumentvanced['Home_patching_三振']*2) / df_argumentvanced['Home_patching_局數'].replace(0,1) + 3.2
        away_FIP = (df_argumentvanced['Away_patching_全壘打']*13 + df_argumentvanced['Away_batting_保送']*3 - df_argumentvanced['Away_patching_三振']*2) / df_argumentvanced['Away_patching_局數'].replace(0,1) + 3.2
        df_argumentvanced['Home_patching_FIP-'] = ((df_argumentvanced['FIP_avg'] - home_FIP) / df_argumentvanced['ERA_avg'])*100
        df_argumentvanced['Away_patching_FIP-'] = ((df_argumentvanced['FIP_avg'] - away_FIP) / df_argumentvanced['ERA_avg'])*100

        home_FIP = (df_argumentvanced['Home_bullpenpatching_全壘打']*13 + df_argumentvanced['Home_batting_保送']*3 - df_argumentvanced['Home_bullpenpatching_三振']*2) / df_argumentvanced['Home_bullpenpatching_局數'].replace(0,1) + 3.2
        away_FIP = (df_argumentvanced['Away_bullpenpatching_全壘打']*13 + df_argumentvanced['Away_batting_保送']*3 - df_argumentvanced['Away_bullpenpatching_三振']*2) / df_argumentvanced['Away_bullpenpatching_局數'].replace(0,1) + 3.2
        df_argumentvanced['Home_bullpenpatching_FIP-'] = ((df_argumentvanced['FIP_avg'] - home_FIP) / df_argumentvanced['ERA_avg'])*100
        df_argumentvanced['Away_bullpenpatching_FIP-'] = ((df_argumentvanced['FIP_avg'] - away_FIP) / df_argumentvanced['ERA_avg'])*100

        home_FIP = (df_argumentvanced['Home_全壘打']*13 + df_argumentvanced['Home_保送']*3 - df_argumentvanced['Home_三振']*2) / df_argumentvanced['Home_局數'].replace(0,1) + 3.2
        away_FIP = (df_argumentvanced['Away_全壘打']*13 + df_argumentvanced['Away_保送']*3 - df_argumentvanced['Away_三振']*2) / df_argumentvanced['Away_局數'].replace(0,1) + 3.2
        df_argumentvanced['Home_FIP-'] = ((df_argumentvanced['FIP_avg'] - home_FIP) / df_argumentvanced['ERA_avg'])*100
        df_argumentvanced['Away_FIP-'] = ((df_argumentvanced['FIP_avg'] - away_FIP) / df_argumentvanced['ERA_avg'])*100                                     



        home_whip = (df_argumentvanced['Home_patching_安打'] + df_argumentvanced['Home_patching_四壞']) / df_argumentvanced['Home_patching_局數'].replace(0,1)
        away_whip = (df_argumentvanced['Away_patching_安打'] + df_argumentvanced['Away_patching_四壞']) / df_argumentvanced['Away_patching_局數'].replace(0,1)
        df_argumentvanced['Home_patching_WHIP-'] = df_argumentvanced['WHIP_avg'] / home_whip.replace(0,1)
        df_argumentvanced['Away_patching_WHIP-'] = df_argumentvanced['WHIP_avg'] / away_whip.replace(0,1)

        home_whip = (df_argumentvanced['Home_bullpenpatching_安打'] + df_argumentvanced['Home_bullpenpatching_四壞']) / df_argumentvanced['Home_bullpenpatching_局數'].replace(0,1)
        away_whip = (df_argumentvanced['Away_bullpenpatching_安打'] + df_argumentvanced['Away_bullpenpatching_四壞']) / df_argumentvanced['Away_bullpenpatching_局數'].replace(0,1)
        df_argumentvanced['Home_bullpenpatching_WHIP-'] = df_argumentvanced['WHIP_avg'] / home_whip.replace(0,1)
        df_argumentvanced['Away_bullpenpatching_WHIP-'] = df_argumentvanced['WHIP_avg'] / away_whip.replace(0,1)

        home_whip = (df_argumentvanced['Home_安打'] + df_argumentvanced['Home_保送']) / df_argumentvanced['Home_局數'].replace(0,1)
        away_whip = (df_argumentvanced['Away_安打'] + df_argumentvanced['Away_保送']) / df_argumentvanced['Away_局數'].replace(0,1)
        df_argumentvanced['Home_WHIP-'] = df_argumentvanced['WHIP_avg'] / home_whip.replace(0,1)
        df_argumentvanced['Away_WHIP-'] = df_argumentvanced['WHIP_avg'] / away_whip.replace(0,1)



        home_k9 = df_argumentvanced['Home_patching_三振'] / df_argumentvanced['Home_patching_局數'].replace(0,1)
        away_k9 = df_argumentvanced['Away_patching_三振'] / df_argumentvanced['Away_patching_局數'].replace(0,1)
        df_argumentvanced['Home_patching_k9+'] =  home_k9 - df_argumentvanced['K9_avg']
        df_argumentvanced['Away_patching_k9+'] =  away_k9 - df_argumentvanced['K9_avg']

        home_k9 = df_argumentvanced['Home_bullpenpatching_三振'] / df_argumentvanced['Home_bullpenpatching_局數'].replace(0,1)
        away_k9 = df_argumentvanced['Away_bullpenpatching_三振'] / df_argumentvanced['Away_bullpenpatching_局數'].replace(0,1)
        df_argumentvanced['Home_bullpenpatching_k9+'] =  home_k9 - df_argumentvanced['K9_avg']
        df_argumentvanced['Away_bullpenpatching_k9+'] =  away_k9 - df_argumentvanced['K9_avg']

        home_k9 = (df_argumentvanced['Home_三振'] / df_argumentvanced['Home_局數'].replace(0,1))*9
        away_k9 = (df_argumentvanced['Away_三振'] / df_argumentvanced['Away_局數'].replace(0,1))*9
        df_argumentvanced['Home_k9+'] =  home_k9 - df_argumentvanced['K9_avg']
        df_argumentvanced['Away_k9+'] =  away_k9 - df_argumentvanced['K9_avg']
        return df_argumentvanced
    
    #抓取Baseball reference年資料
    def reference_pitcher_year(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        prefs = {"profile.managed_default_content_settings.images": 2, "profile.managed_default_content_settings.plugins": 2}
        options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome('chromedriver',options=options)
        browser = webdriver.Chrome(options=options)

        central_all = pd.DataFrame()
        for i in range(self.matchdate.year,self.matchdate.year+1):
            #central
            id_ = self.central[str(i)]
            url = f"https://www.baseball-reference.com/register/league.cgi?id={id_}"
            browser.get(url)
            soup = BeautifulSoup(browser.page_source,"lxml")

            #batting
            central_batting = []
            tr = soup.find("table",{"id":"league_batting"}).find("tbody").find_all("tr")
            for t in range(len(tr)):
                team_name = tr[t].find("th").text
                team_href = tr[t].find("th").find("a").get('href')
                data_one = {
                    "Year" : i,
                    "Team" : team_name,
                    "Href" : team_href
                }
                td = tr[t].find_all('td')[1:]
                for d in range(len(td)):
                    feature_name = td[d].get("data-stat")
                    feature = td[d].text
                    data_feature = {
                        f"Batting_{feature_name}":feature
                    }
                    data_one = dict(**data_one,**data_feature)
                central_batting.append(data_one)
            central_batting_df = pd.DataFrame(central_batting)
            central_batting_df.set_index("Year",inplace=True)

            #pitching
            central_pitching = []
            tr = soup.find("table",{"id":"league_pitching"}).find("tbody").find_all("tr")
            for t in range(len(tr)):
                team_name = tr[t].find("th").text
                data_one = {
                    "Year" : i,
                    "Team" : team_name
                }
                td = tr[t].find_all('td')[1:]
                for d in range(len(td)):
                    feature_name = td[d].get("data-stat")
                    feature = td[d].text
                    data_feature = {
                        f"Patching_{feature_name}":feature
                    }
                    data_one = dict(**data_one,**data_feature)
                central_pitching.append(data_one)
            central_pitching_df = pd.DataFrame(central_pitching)
            central_pitching_df.set_index("Year",inplace=True)
            #fielding
            central_fielding = []
            tr = soup.find("table",{"id":"league_fielding"}).find("tbody").find_all("tr")
            for t in range(len(tr)):
                team_name = tr[t].find("th").text
                data_one = {
                    "Year" : i,
                    "Team" : team_name
                }
                td = tr[t].find_all('td')[3:9]
                for d in range(len(td)):
                    feature_name = td[d].get("data-stat")
                    feature = td[d].text
                    data_feature = {
                        f"Fielding_{feature_name}":feature
                    }
                    data_one = dict(**data_one,**data_feature)
                central_fielding.append(data_one)
            central_fielding_df = pd.DataFrame(central_fielding)
            central_fielding_df.set_index("Year",inplace=True)

            central_all_df = central_batting_df.merge(central_pitching_df,on=['Year','Team'])
            central_all_df = central_all_df.merge(central_fielding_df,on=['Year','Team'])
            central_all = central_all.append(central_all_df)
            print(f"{i} central suceesful!!")
            
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('chromedriver',options=options)
        browser = webdriver.Chrome(options=options)

        pacific_all = pd.DataFrame()
        for i in range(self.matchdate.year,self.matchdate.year+1):
            #central
            id_ = self.pacific[str(i)]
            url = f"https://www.baseball-reference.com/register/league.cgi?id={id_}"
            browser.get(url)
            soup = BeautifulSoup(browser.page_source,"lxml")

            #batting
            pacific_batting = []
            tr = soup.find("table",{"id":"league_batting"}).find("tbody").find_all("tr")
            for t in range(len(tr)):
                team_name = tr[t].find("th").text
                team_href = tr[t].find("th").find("a").get('href')
                data_one = {
                    "Year" : i,
                    "Team" : team_name,
                    "Href" : team_href
                }
                td = tr[t].find_all('td')[1:]
                for d in range(len(td)):
                    feature_name = td[d].get("data-stat")
                    feature = td[d].text
                    data_feature = {
                        f"Batting_{feature_name}":feature
                    }
                    data_one = dict(**data_one,**data_feature)
                pacific_batting.append(data_one)
            pacific_batting_df = pd.DataFrame(pacific_batting)
            pacific_batting_df.set_index("Year",inplace=True)

            #pitching
            pacific_pitching = []
            tr = soup.find("table",{"id":"league_pitching"}).find("tbody").find_all("tr")
            for t in range(len(tr)):
                team_name = tr[t].find("th").text
                data_one = {
                    "Year" : i,
                    "Team" : team_name
                }
                td = tr[t].find_all('td')[1:]
                for d in range(len(td)):
                    feature_name = td[d].get("data-stat")
                    feature = td[d].text
                    data_feature = {
                        f"Patching_{feature_name}":feature
                    }
                    data_one = dict(**data_one,**data_feature)
                pacific_pitching.append(data_one)
            pacific_pitching_df = pd.DataFrame(pacific_pitching)
            pacific_pitching_df.set_index("Year",inplace=True)
            #fielding
            pacific_fielding = []
            tr = soup.find("table",{"id":"league_fielding"}).find("tbody").find_all("tr")
            for t in range(len(tr)):
                team_name = tr[t].find("th").text
                data_one = {
                    "Year" : i,
                    "Team" : team_name
                }
                td = tr[t].find_all('td')[3:9]
                for d in range(len(td)):
                    feature_name = td[d].get("data-stat")
                    feature = td[d].text
                    data_feature = {
                        f"Fielding_{feature_name}":feature
                    }
                    data_one = dict(**data_one,**data_feature)
                pacific_fielding.append(data_one)
            pacific_fielding_df = pd.DataFrame(pacific_fielding)
            pacific_fielding_df.set_index("Year",inplace=True)

            pacific_all_df = pacific_batting_df.merge(pacific_pitching_df,on=['Year','Team'])
            pacific_all_df = pacific_all_df.merge(pacific_fielding_df,on=['Year','Team'])
            pacific_all = pacific_all.append(pacific_all_df)
            print(f"{i} central suceesful!!")
            
        df_all  = central_all.append(pacific_all)
        df_all.sort_index()
        df_all['Team'] = df_all['Team'].replace(self.teams_changename_en2)
        df_all.to_excel(f"{self.path}/team_years.xlsx")
        df_all = pd.read_excel(f"{self.path}/team_years.xlsx",index_col='Year')
        return df_all
    
    def reference_pitcherer_year_data(self,df_all):
        options = Options()
        prefs = {"profile.managed_default_content_settings.images": 2, 
         "profile.managed_default_content_settings.plugins": 2,
         "profile.managed_default_content_settings.popups": 2,
         "profile.managed_default_content_settings.geolocation": 2,
         "profile.managed_default_content_settings.notifications": 2,
         "profile.managed_default_content_settings.media_stream": 2}
        options.add_experimental_option("prefs", prefs)
        #options.add_argument('--headless')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        browser = webdriver.Chrome('chromedriver',options=options)
        browser = webdriver.Chrome(options=options)
        batting_all =[]
        pitching_all =[]
        for i in range(len(df_all)):
            year = df_all.index[i]
            team = df_all['Team'].iloc[i]
            href = df_all['Href'].iloc[i]
            url = f"https://www.baseball-reference.com{href}"
            browser.get(url)
            soup = BeautifulSoup(browser.page_source,"lxml")

            #batting
            tr = soup.find("table",{"id":"team_batting"}).find("tbody").find_all("tr")
            for t in range(len(tr)):
                data_one = {
                    "Year" : year,
                    "Team" : team,
                    "Href" : href
                }
                th = tr[t].find_all("th")
                if len(th) == 1:
                    td = tr[t].find_all("td")[:-1]
                    for d in range(len(td)):
                        if d == 0:
                            player_name = td[d].text
                            player_href = td[d].find('a').get("href")
                            data_feature = {
                                "Player" : player_name,
                                "Player_href" : player_href
                            }
                        else:
                            feature_name = td[d].get('data-stat')
                            feature = td[d].text
                            data_feature = {
                                f"Batting_player_{feature_name}_year" : feature
                            }
                        data_one = dict(**data_one,**data_feature)
                    batting_all.append(data_one)
                    print(f"{year} {player_name} successful!!")

            #pitching
            tr = soup.find("table",{"id":"team_pitching"}).find("tbody").find_all("tr")
            for t in range(len(tr)):
                data_one = {
                    "Year" : year,
                    "Team" : team,
                    "Href" : href
                }
                th = tr[t].find_all("th")
                if len(th) == 1:
                    td = tr[t].find_all("td")[:-1]
                    for d in range(len(td)):
                        if d == 0:
                            player_name = td[d].text
                            player_href = td[d].find('a').get("href")
                            data_feature = {
                                "Player" : player_name,
                                "Player_href" : player_href
                            }
                        else:
                            feature_name = td[d].get('data-stat')
                            feature = td[d].text
                            data_feature = {
                                f"Patching_player_{feature_name}_year" : feature
                            }
                        data_one = dict(**data_one,**data_feature)
                    pitching_all.append(data_one)
                    print(f"{year} {player_name} successful!!")
            print(f"{year} {team} successful!!")
        batting_player_df = pd.DataFrame(batting_all)
        batting_player_df.set_index('Year',inplace=True)
        batting_player_df.to_excel(f"{self.path}/batting_year.xlsx")
        batting_player_df = pd.read_excel(f"{self.path}/batting_year.xlsx",index_col='Year')
        pitching_player_df = pd.DataFrame(pitching_all)
        pitching_player_df.set_index('Year',inplace=True)
        pitching_player_df.to_excel(f"{self.path}/pitching_year.xlsx")
        pitching_player_df = pd.read_excel(f"{self.path}/pitching_year.xlsx",index_col='Year')
        return batting_player_df,pitching_player_df
    
    # 運彩報馬仔投手球隊與生日抓取(為了合併英文名稱使用)
    def chinese_sp_connect(self,sp_all):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('chromedriver',options=options)
        browser = webdriver.Chrome(options=options)
        data_all = []
        for i in range(len(sp_all)):
            sp_team = sp_all['Team'].iloc[i]
            sp_name = sp_all['SP'].iloc[i]
            sp_href = sp_all['SP_href'].iloc[i]
            browser.get(sp_href)
            soup = BeautifulSoup(browser.page_source,"lxml")
            birthday = soup.find("div",{"class":"row ssmt"}).find_all("div",{"class":"fls"})[1].find_all("div")[2].text.split(",")[0]
            data_one = {
                "Team" : sp_team,
                "SP" : sp_name,
                "SP_href" : sp_href,
                'Birthday' : birthday
            }
            data_all.append(data_one)
            print(f"{sp_name} successful!!")
        sp_df = pd.DataFrame(data_all)
        sp_df.set_index('SP',inplace=True)
        sp_df.to_excel(f"{self.path}/sp_bir.xlsx")
        sp_df = pd.read_excel(f"{self.path}/sp_bir.xlsx",index_col='SP')
        return sp_df
    
    def english_sp_connect(self,pitching_player_df):
        options = Options()
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        prefs = {"profile.managed_default_content_settings.images": 2, "profile.managed_default_content_settings.plugins": 2}
        options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome('chromedriver',options=options)
        browser = webdriver.Chrome(options=options)
        data_all = []
        sp_p = pitching_player_df[['Team','Player','Player_href']].drop_duplicates('Player_href',keep='first')
        for i in range(len(sp_p)):
            sp_team = sp_p['Team'].iloc[i]
            sp_name = sp_p['Player'].iloc[i]
            sp_href = sp_p['Player_href'].iloc[i]
            sp_bir_b = pd.read_excel(f"{self.path_b}/sp_bir_reference.xlsx",index_col='SP')
            sp_same = sp_bir_b[sp_bir_b.index == sp_name]
            if len(sp_same) == 0:
                url = f"https://www.baseball-reference.com{sp_href}"
                browser.get(url)
                soup = BeautifulSoup(browser.page_source,"lxml")
                birthday = soup.find("span",{"id":"necro-birth"}).get("data-birth")
            else:
                birthday = sp_same['Birthday'].iloc[0]
            data_one = {
                "Team" : sp_team,
                "SP" : sp_name,
                "SP_href" : sp_href,
                'Birthday' : birthday
            }
            data_all.append(data_one)
            print(f"{sp_name} successful!!")
        sp_all2 = pd.DataFrame(data_all)
        sp_all2.set_index('SP',inplace=True)
        sp_all2.to_excel(f"{self.path}/sp_bir_reference.xlsx")
        sp_all2 = pd.read_excel(f"{self.path}/sp_bir_reference.xlsx",index_col='SP')
        return sp_all2
    
    #最新投手年資料合併
    def sp_year_data(self,df_argumentvanced,pitcher_year,sp_df):
        data_all = []
        for i in range(len(df_argumentvanced)):
            date = df_argumentvanced.index[i]
            home = df_argumentvanced['主隊'].iloc[i]
            away = df_argumentvanced['客隊'].iloc[i]
            home_sp = df_argumentvanced['Home_SP'].iloc[i]
            away_sp = df_argumentvanced['Away_SP'].iloc[i]
            eventcode = df_argumentvanced['Eventcode'].iloc[i]
            data_one = {
                "Date" : date,
                "主隊" : home,
                "客隊" : away,
                "Eventcode" : eventcode
            }
            #主隊
            home_sp_data = pitcher_year[(pitcher_year['Player_lottonavi'] == home_sp) & (pitcher_year.index == date.year)]
            if len(home_sp_data) > 0:
                home_sp_data = home_sp_data.iloc[0][6:]
                col = []
                for c in home_sp_data.index:
                    c = "Home_SP_" + c
                    col.append(c)
                home_sp_data.index = col
                home_sp_dict = dict(home_sp_data)
            else:
                home_sp_data = pitcher_year[(pitcher_year['Player_lottonavi'] == home_sp) & (pitcher_year.index == date.year)]
                if len(home_sp_data) > 0:
                    sp_year = home_sp_data.iloc[0][6]
                else:
                    sp_df['Birthday'] = pd.to_datetime(sp_df['Birthday'])
                    sp_year = int((self.today - sp_df[sp_df.index == home_sp]['Birthday'].iloc[0]).days / 365)
                home_sp_dict = {"Home_SP_Patching_player_age_year" : sp_year,
                 'Home_SP_Patching_player_W_year': 0,
                 'Home_SP_Patching_player_L_year': 0,
                 'Home_SP_Patching_player_win_loss_perc_year': 0,
                 'Home_SP_Patching_player_earned_run_avg_year': 0,
                 'Home_SP_Patching_player_G_year': 0,
                 'Home_SP_Patching_player_GS_year': 0,
                 'Home_SP_Patching_player_GF_year': 0,
                 'Home_SP_Patching_player_CG_year': 0,
                 'Home_SP_Patching_player_SHO_year': 0,
                 'Home_SP_Patching_player_SV_year': 0,
                 'Home_SP_Patching_player_IP_year': 0,
                 'Home_SP_Patching_player_H_year': 0,
                 'Home_SP_Patching_player_R_year': 0,
                 'Home_SP_Patching_player_ER_year': 0,
                 'Home_SP_Patching_player_HR_year': 0,
                 'Home_SP_Patching_player_BB_year': 0,
                 'Home_SP_Patching_player_IBB_year': 0,
                 'Home_SP_Patching_player_SO_year': 0,
                 'Home_SP_Patching_player_HBP_year': 0,
                 'Home_SP_Patching_player_BK_year': 0,
                 'Home_SP_Patching_player_WP_year': 0,
                 'Home_SP_Patching_player_batters_faced_year': 0,
                 'Home_SP_Patching_player_whip_year': 0,
                 'Home_SP_Patching_player_hits_per_nine_year': 0,
                 'Home_SP_Patching_player_home_runs_per_nine_year': 0,
                 'Home_SP_Patching_player_bases_on_balls_per_nine_year': 0,
                 'Home_SP_Patching_player_strikeouts_per_nine_year': 0,
                 'Home_SP_Patching_player_strikeouts_per_base_on_balls_year': 0}
            data_one = dict(**data_one,**home_sp_dict)

            #客隊
            away_sp_data = pitcher_year[(pitcher_year['Player_lottonavi'] == away_sp) & (pitcher_year.index == date.year)]
            if len(away_sp_data) > 0:
                away_sp_data = away_sp_data.iloc[0][6:]
                col = []
                for c in away_sp_data.index:
                    c = "Away_SP_" + c
                    col.append(c)
                away_sp_data.index = col
                away_sp_dict = dict(away_sp_data)
            else:
                away_sp_data = pitcher_year[(pitcher_year['Player_lottonavi'] == away_sp) & (pitcher_year.index == date.year)]
                if len(away_sp_data) > 0:
                    sp_year = away_sp_data.iloc[0][6]
                else:
                    sp_df['Birthday'] = pd.to_datetime(sp_df['Birthday'])
                    sp_year = int((self.today - sp_df[sp_df.index == away_sp]['Birthday'].iloc[0]).days / 365)
                away_sp_dict = {'Away_SP_Patching_player_age_year': sp_year,
                 'Away_SP_Patching_player_W_year': 0,
                 'Away_SP_Patching_player_L_year': 0,
                 'Away_SP_Patching_player_win_loss_perc_year': 0,
                 'Away_SP_Patching_player_earned_run_avg_year': 0,
                 'Away_SP_Patching_player_G_year': 0,
                 'Away_SP_Patching_player_GS_year': 0,
                 'Away_SP_Patching_player_GF_year': 0,
                 'Away_SP_Patching_player_CG_year': 0,
                 'Away_SP_Patching_player_SHO_year': 0,
                 'Away_SP_Patching_player_SV_year': 0,
                 'Away_SP_Patching_player_IP_year': 0,
                 'Away_SP_Patching_player_H_year': 0,
                 'Away_SP_Patching_player_R_year': 0,
                 'Away_SP_Patching_player_ER_year': 0,
                 'Away_SP_Patching_player_HR_year': 0,
                 'Away_SP_Patching_player_BB_year': 0,
                 'Away_SP_Patching_player_IBB_year': 0,
                 'Away_SP_Patching_player_SO_year': 0,
                 'Away_SP_Patching_player_HBP_year': 0,
                 'Away_SP_Patching_player_BK_year': 0,
                 'Away_SP_Patching_player_WP_year': 0,
                 'Away_SP_Patching_player_batters_faced_year': 0,
                 'Away_SP_Patching_player_whip_year': 0,
                 'Away_SP_Patching_player_hits_per_nine_year': 0,
                 'Away_SP_Patching_player_home_runs_per_nine_year': 0,
                 'Away_SP_Patching_player_bases_on_balls_per_nine_year': 0,
                 'Away_SP_Patching_player_strikeouts_per_nine_year': 0,
                 'Away_SP_Patching_player_strikeouts_per_base_on_balls_year': 0}

            data_one = dict(**data_one,**away_sp_dict)       
            data_all.append(data_one)
            print(f"{date} {home} vs {away} successful")
        sp_df_all = pd.DataFrame(data_all)
        sp_df_all.set_index("Date",inplace=True)
        sp_df_all.to_excel(f"{self.path}/sp_data_y.xlsx")
        return sp_df_all
    
    def years_data(self,df_data):
        team_year = pd.read_excel(f"{self.path}/team_years.xlsx",index_col='Year')
        data_year = []
        for i in range(len(df_data)):
            date = df_data.index[i]
            home = df_data['主隊'].iloc[i]
            away = df_data['客隊'].iloc[i]
            eventcode = df_data['Eventcode'].iloc[i]
            data_one = {
                "Date" : date,
                "主隊" : home,
                "客隊" : away,
                "Eventcode" : eventcode
            }
            #主隊
            home_year = team_year[(team_year.index == date.year) & (team_year['Team'] == home)].iloc[0,1:]
            col = []
            for c in home_year.index:
                c = 'Home_' + c + "_year"
                col.append(c)
            home_year.index = col
            home_year_dict = dict(home_year)
            data_one = dict(**data_one,**home_year_dict)

            #客隊
            away_year = team_year[(team_year.index == date.year) & (team_year['Team'] == away)].iloc[0,1:]
            col = []
            for c in away_year.index:
                c = 'Away_' + c + "_year"
                col.append(c)
            away_year.index= col
            away_year_dict = dict(away_year)
            data_one = dict(**data_one,**away_year_dict)
            data_year.append(data_one)
            print(f"{date} {home} vs {away} successful!!")
            
        df_year = pd.DataFrame(data_year)
        df_year.set_index('Date',inplace=True)
        df_year.to_excel(f"{self.path}/base_data_y.xlsx")
        df_year = pd.read_excel(f"{self.path}/base_data_y.xlsx",index_col='Date')
        return df_year
    
    def before10_data(self,df_final_newdata,df_final_alldata):
        # 按照日期排序
        df_sort = df_final_alldata.sort_values(by='Date')
        # 設置時間步長
        lookback = 10

        # 創建空的數據集
        X = []
        y= []
        team_encoder = joblib.load(f'{self.path_model}/gru_team.pkl')

        sp_name_new = df_final_newdata['Home_SP'].append(df_final_newdata['Away_SP']).unique()
        #sp_encoder = joblib.load(f'{path_b}\gru_sp_name.pkl')
        sp_encoder = joblib.load(f'{self.path_b}/gru_sp_name.pkl')
        class_ = sp_encoder.classes_
        sp_name_new2 = np.setdiff1d(sp_name_new,class_)
        sp_name_all = np.concatenate((class_,sp_name_new2))
        sp_encoder = MyLabelEncoder(classes=sp_name_all)
        sp_encoder.fit(sp_name_all)
        with open(f'{self.path}\gru_sp_name.pkl', 'wb') as f:
            pickle.dump(sp_encoder, f)

        # 遍歷每一行資料
        for i in range(lookback, len(df_sort)):
            # 當前比賽的主隊和客隊
            date = df_sort.index[i]
            if date >= self.yesterday:
                home_team = df_sort['主隊'].iloc[i]
                away_team = df_sort['客隊'].iloc[i]

                # 從歷史數據中選擇與當天主客隊相同的比賽數據
                #雙方對戰
                history_both = df_sort.loc[(df_sort.index < date) &
                                        (((df_sort['主隊'] == home_team) & (df_sort['客隊'] == away_team)) |
                                        ((df_sort['主隊'] == away_team) & (df_sort['客隊'] == home_team)))][-lookback:]
                #主隊對戰
                history_home = df_sort.loc[(df_sort.index < date) &
                                        (((df_sort['主隊'] == home_team) & (df_sort['客隊'] != away_team)) |
                                        ((df_sort['主隊'] != away_team) & (df_sort['客隊'] == home_team)))][-lookback:]
                #客隊對戰
                history_away = df_sort.loc[(df_sort.index < date) &
                                        (((df_sort['主隊'] == away_team) & (df_sort['客隊'] != home_team)) |
                                        ((df_sort['主隊'] != home_team) & (df_sort['客隊'] == away_team)))][-lookback:]

                history_subset = pd.concat([history_both,history_home,history_away])
                history_subset = history_subset.sort_index()
                if len(history_subset)> 0:
                    history_subset.drop(['FP_href','game_href', 'Home_href','Away_href',
                                         'Home_score_href','Away_score_href','Home_投手','Away_投手',
                                        'Home_主客場','Home_敵隊','Home_球隊','Away_主客場','Away_敵隊',
                                         'Away_球隊'],axis=1,inplace=True)

                    # 將歷史數據和當天賠率數據合併
                    now_need= ['主隊','客隊','Eventcode','Home_SP_href','Away_SP_href','Home_NextDate1',
                           'Home_NextLocate1', 'Home_NextOppo1', 'Home_NextDate2',
                           'Home_NextLocate2', 'Home_NextOppo2', 'Home_NextDate3',
                           'Home_NextLocate3', 'Home_NextOppo3', 'Away_NextDate1',
                           'Away_NextLocate1', 'Away_NextOppo1', 'Away_NextDate2',
                           'Away_NextLocate2', 'Away_NextOppo2', 'Away_NextDate3',
                           'Away_NextLocate3', 'Away_NextOppo3', 'Home_SP','Home_SP_ERA',
                           'Away_SP','Away_SP_ERA','Home_SP_win',
                            'Home_SP_lose','Home_SP_winrate','Away_SP_win','Away_SP_lose',
                            'Away_SP_winrate','Homeodds','Awayodds','Odds_return',
                            '客隊ELO','主隊ELO','year','Both_bettle','Home_bettle','Away_bettle',
                            'Home_Game_InTotal','Home_Win_InTotal',
                            'Home_Lose_InTotal','Home_Tie_InTotal','Home_WinRate_InTotal',
                            'Home_Game_InSeason','Home_Win_InSeason','Home_Lose_InSeason',
                            'Home_Tie_InSeason','Home_WinRate_InSeason','Home_Game_inhome_InTotal',
                            'Home_Win_inhome_InTotal','Home_Lose_inhome_InTotal','Home_Tie_inhome_InTotal',
                            'Home_WinRate_inhome_InTotal','Home_Game_inhome_InSeason',
                            'Home_Win_inhome_InSeason','Home_Lose_inhome_InSeason','Home_Tie_inhome_InSeason',
                            'Home_WinRate_inhome_InSeason','Home_Game_inaway_InTotal',
                            'Home_Win_inaway_InTotal','Home_Lose_inaway_InTotal','Home_Tie_inaway_InTotal',
                            'Home_WinRate_inaway_InTotal','Home_Game_inaway_InSeason',
                            'Home_Win_inaway_InSeason','Home_Lose_inaway_InSeason','Home_Tie_inaway_InSeason',
                            'Home_WinRate_inaway_InSeason','Away_Game_InTotal','Away_Win_InTotal',
                            'Away_Lose_InTotal','Away_Tie_InTotal','Away_WinRate_InTotal','Away_Game_InSeason',
                            'Away_Win_InSeason','Away_Lose_InSeason','Away_Tie_InSeason',
                            'Away_WinRate_InSeason','Away_Game_inhome_InTotal','Away_Win_inhome_InTotal',
                            'Away_Lose_inhome_InTotal','Away_Tie_inhome_InTotal','Away_WinRate_inhome_InTotal',
                            'Away_Game_inhome_InSeason','Away_Win_inhome_InSeason','Away_Lose_inhome_InSeason',
                            'Away_Tie_inhome_InSeason','Away_WinRate_inhome_InSeason',
                            'Away_Game_inaway_InTotal','Away_Win_inaway_InTotal','Away_Lose_inaway_InTotal',
                            'Away_Tie_inaway_InTotal','Away_WinRate_inaway_InTotal',
                            'Away_Game_inaway_InSeason','Away_Win_inaway_InSeason',
                            'Away_Lose_inaway_InSeason','Away_Tie_inaway_InSeason',
                            'Away_WinRate_inaway_InSeason','Home_Rank_Total','Home_Rank_Season',
                            'Home_Rank_InHome','Home_Rank_InHome_Season','Home_Rank_InAway',
                            'Home_Rank_InAway_Season','Away_Rank_Total','Away_Rank_Season',
                            'Away_Rank_InHome','Away_Rank_InHome_Season','Away_Rank_InAway',
                            'Away_Rank_InAway_Season','ERA_avg','FIP_avg','WHIP_avg','K9_avg',
                            'Home_SP_Patching_player_age_year',
                               'Home_SP_Patching_player_W_year', 'Home_SP_Patching_player_L_year',
                               'Home_SP_Patching_player_win_loss_perc_year',
                               'Home_SP_Patching_player_earned_run_avg_year',
                               'Home_SP_Patching_player_G_year',
                               'Home_SP_Patching_player_GS_year',
                               'Home_SP_Patching_player_GF_year',
                               'Home_SP_Patching_player_CG_year',
                               'Home_SP_Patching_player_SHO_year',
                               'Home_SP_Patching_player_SV_year',
                               'Home_SP_Patching_player_IP_year',
                               'Home_SP_Patching_player_H_year', 'Home_SP_Patching_player_R_year',
                               'Home_SP_Patching_player_ER_year',
                               'Home_SP_Patching_player_HR_year',
                               'Home_SP_Patching_player_BB_year',
                               'Home_SP_Patching_player_IBB_year',
                               'Home_SP_Patching_player_SO_year',
                               'Home_SP_Patching_player_HBP_year',
                               'Home_SP_Patching_player_BK_year',
                               'Home_SP_Patching_player_WP_year',
                               'Home_SP_Patching_player_batters_faced_year',
                               'Home_SP_Patching_player_whip_year',
                               'Home_SP_Patching_player_hits_per_nine_year',
                               'Home_SP_Patching_player_home_runs_per_nine_year',
                               'Home_SP_Patching_player_bases_on_balls_per_nine_year',
                               'Home_SP_Patching_player_strikeouts_per_nine_year',
                               'Home_SP_Patching_player_strikeouts_per_base_on_balls_year',
                               'Away_SP_Patching_player_age_year',
                               'Away_SP_Patching_player_W_year', 'Away_SP_Patching_player_L_year',
                               'Away_SP_Patching_player_win_loss_perc_year',
                               'Away_SP_Patching_player_earned_run_avg_year',
                               'Away_SP_Patching_player_G_year',
                               'Away_SP_Patching_player_GS_year',
                               'Away_SP_Patching_player_GF_year',
                               'Away_SP_Patching_player_CG_year',
                               'Away_SP_Patching_player_SHO_year',
                               'Away_SP_Patching_player_SV_year',
                               'Away_SP_Patching_player_IP_year',
                               'Away_SP_Patching_player_H_year', 'Away_SP_Patching_player_R_year',
                               'Away_SP_Patching_player_ER_year',
                               'Away_SP_Patching_player_HR_year',
                               'Away_SP_Patching_player_BB_year',
                               'Away_SP_Patching_player_IBB_year',
                               'Away_SP_Patching_player_SO_year',
                               'Away_SP_Patching_player_HBP_year',
                               'Away_SP_Patching_player_BK_year',
                               'Away_SP_Patching_player_WP_year',
                               'Away_SP_Patching_player_batters_faced_year',
                               'Away_SP_Patching_player_whip_year',
                               'Away_SP_Patching_player_hits_per_nine_year',
                               'Away_SP_Patching_player_home_runs_per_nine_year',
                               'Away_SP_Patching_player_bases_on_balls_per_nine_year',
                               'Away_SP_Patching_player_strikeouts_per_nine_year',
                               'Away_SP_Patching_player_strikeouts_per_base_on_balls_year',
                            'Home_Batting_age_bat_year', 'Home_Batting_runs_per_game_year',
                           'Home_Batting_G_year', 'Home_Batting_PA_year',
                           'Home_Batting_AB_year', 'Home_Batting_R_year',
                           'Home_Batting_H_year', 'Home_Batting_2B_year',
                           'Home_Batting_3B_year', 'Home_Batting_HR_year',
                           'Home_Batting_RBI_year', 'Home_Batting_SB_year',
                           'Home_Batting_CS_year', 'Home_Batting_BB_year',
                           'Home_Batting_SO_year', 'Home_Batting_batting_avg_year',
                           'Home_Batting_onbase_perc_year', 'Home_Batting_slugging_perc_year',
                           'Home_Batting_onbase_plus_slugging_year', 'Home_Batting_TB_year',
                           'Home_Batting_GIDP_year', 'Home_Batting_HBP_year',
                           'Home_Batting_SH_year', 'Home_Batting_SF_year',
                           'Home_Batting_IBB_year', 'Home_Patching_age_pit_year',
                           'Home_Patching_runs_per_game_year', 'Home_Patching_W_year',
                           'Home_Patching_L_year', 'Home_Patching_win_loss_perc_year',
                           'Home_Patching_earned_run_avg_year', 'Home_Patching_run_avg_year',
                           'Home_Patching_G_year', 'Home_Patching_GS_year',
                           'Home_Patching_GF_year', 'Home_Patching_CG_year',
                           'Home_Patching_SHO_year', 'Home_Patching_SV_year',
                           'Home_Patching_IP_year', 'Home_Patching_H_year',
                           'Home_Patching_R_year', 'Home_Patching_ER_year',
                           'Home_Patching_HR_year', 'Home_Patching_BB_year',
                           'Home_Patching_IBB_year', 'Home_Patching_SO_year',
                           'Home_Patching_HBP_year', 'Home_Patching_BK_year',
                           'Home_Patching_WP_year', 'Home_Patching_batters_faced_year',
                           'Home_Patching_whip_year', 'Home_Patching_hits_per_nine_year',
                           'Home_Patching_home_runs_per_nine_year',
                           'Home_Patching_bases_on_balls_per_nine_year',
                           'Home_Patching_strikeouts_per_nine_year',
                           'Home_Patching_strikeouts_per_base_on_balls_year',
                           'Home_Fielding_PO_year', 'Home_Fielding_A_year',
                           'Home_Fielding_E_def_year', 'Home_Fielding_DP_def_year',
                           'Home_Fielding_fielding_perc_year', 'Home_Fielding_PB_year',
                           'Away_Batting_age_bat_year', 'Away_Batting_runs_per_game_year',
                           'Away_Batting_G_year', 'Away_Batting_PA_year',
                           'Away_Batting_AB_year', 'Away_Batting_R_year',
                           'Away_Batting_H_year', 'Away_Batting_2B_year',
                           'Away_Batting_3B_year', 'Away_Batting_HR_year',
                           'Away_Batting_RBI_year', 'Away_Batting_SB_year',
                           'Away_Batting_CS_year', 'Away_Batting_BB_year',
                           'Away_Batting_SO_year', 'Away_Batting_batting_avg_year',
                           'Away_Batting_onbase_perc_year', 'Away_Batting_slugging_perc_year',
                           'Away_Batting_onbase_plus_slugging_year', 'Away_Batting_TB_year',
                           'Away_Batting_GIDP_year', 'Away_Batting_HBP_year',
                           'Away_Batting_SH_year', 'Away_Batting_SF_year',
                           'Away_Batting_IBB_year', 'Away_Patching_age_pit_year',
                           'Away_Patching_runs_per_game_year', 'Away_Patching_W_year',
                           'Away_Patching_L_year', 'Away_Patching_win_loss_perc_year',
                           'Away_Patching_earned_run_avg_year', 'Away_Patching_run_avg_year',
                           'Away_Patching_G_year', 'Away_Patching_GS_year',
                           'Away_Patching_GF_year', 'Away_Patching_CG_year',
                           'Away_Patching_SHO_year', 'Away_Patching_SV_year',
                           'Away_Patching_IP_year', 'Away_Patching_H_year',
                           'Away_Patching_R_year', 'Away_Patching_ER_year',
                           'Away_Patching_HR_year', 'Away_Patching_BB_year',
                           'Away_Patching_IBB_year', 'Away_Patching_SO_year',
                           'Away_Patching_HBP_year', 'Away_Patching_BK_year',
                           'Away_Patching_WP_year', 'Away_Patching_batters_faced_year',
                           'Away_Patching_whip_year', 'Away_Patching_hits_per_nine_year',
                           'Away_Patching_home_runs_per_nine_year',
                           'Away_Patching_bases_on_balls_per_nine_year',
                           'Away_Patching_strikeouts_per_nine_year',
                           'Away_Patching_strikeouts_per_base_on_balls_year',
                           'Away_Fielding_PO_year', 'Away_Fielding_A_year',
                           'Away_Fielding_E_def_year', 'Away_Fielding_DP_def_year',
                           'Away_Fielding_fielding_perc_year', 'Away_Fielding_PB_year'
                              ]


                    #當場賽事的加權平均


                    # 將歷史數據和當天賠率數據合併
                    X_i =pd.concat([history_subset,df_sort.iloc[i:i+1][now_need]])
                    X_i['主隊'] = team_encoder.transform(X_i['主隊'])
                    X_i['客隊'] = team_encoder.transform(X_i['客隊'])
                    X_i['Home_SP'] = sp_encoder.transform(X_i['Home_SP'])
                    X_i['Away_SP'] = sp_encoder.transform(X_i['Away_SP'])
                    X_i['year'] = date.year
                    X_i['Date_Now'] = date
                    X_i['Eventcode_Now'] = df_sort['Eventcode'].iloc[i]
                    y_i = df_sort['W/L'].iloc[i]

                    # 添加到數據集中
                    X.append(X_i)
                    y.append(y_i)
                    print(f"{date} {home_team} vs {away_team} successful!!")
        # 合并两个DataFrame
        merged_df = pd.concat(X)
        merged_df['Home_NextOppo1'] = merged_df['Home_NextOppo1'].replace(self.teams)
        merged_df['Home_NextOppo2'] = merged_df['Home_NextOppo2'].replace(self.teams)
        merged_df['Home_NextOppo3'] = merged_df['Home_NextOppo3'].replace(self.teams)
        merged_df['Away_NextOppo1'] = merged_df['Away_NextOppo1'].replace(self.teams)
        merged_df['Away_NextOppo2'] = merged_df['Away_NextOppo2'].replace(self.teams)
        merged_df['Away_NextOppo3'] = merged_df['Away_NextOppo3'].replace(self.teams)
        merged_df = merged_df.replace('---','0').replace('-','0')
        merged_df.to_excel(f"{self.path}/before_preddata_2.xlsx")
        merged_df = pd.read_excel(f"{self.path}/before_preddata_2.xlsx",index_col='Date')
        return merged_df
    
    def data_fill(self,merged_df):
        eventcode_have31 = []
        eventcode_now_all = merged_df['Eventcode_Now'].unique()
        for i in range(len(eventcode_now_all)):
            eventcode_now = eventcode_now_all[i]
            data_one_havenow = merged_df[merged_df['Eventcode_Now'] == eventcode_now]
            if len(data_one_havenow) == 31:
                date_now =  data_one_havenow[data_one_havenow['Eventcode'] == eventcode_now]
                date = date_now.index[0]
                eventcode = date_now['Eventcode'].iloc[0]
                home = date_now['主隊'].iloc[0]
                away = date_now['客隊'].iloc[0]
                dict_one = {
                    "Date" : date,
                    "主隊" : home,
                    "客隊" : away,
                    "Eventcode" : eventcode,
                }
                data_one = data_one_havenow[:-1]
                #主隊在主隊
                data_inhome = data_one[data_one['主隊'] == home]
                col = []
                for c in data_inhome.columns:
                    if (c == '主隊得分') or ((('batting' in c) or ('patching' in c)) and ('Home_' in c)):
                        col.append(c)
                data_home_inhome = data_inhome[col]
                col = []
                for c in data_home_inhome.columns:
                    c = c.replace("主隊",'').replace("Home_",'')
                    col.append(c)
                data_home_inhome.columns = col

                #主隊在客隊
                data_inaway = data_one[data_one['客隊'] == home]
                col = []
                for c in data_inaway.columns:
                    if (c == '客隊得分') or ((('batting' in c) or ('patching' in c)) and ('Away_' in c)):
                        col.append(c)
                data_home_inaway = data_inaway[col]
                col = []
                for c in data_home_inaway.columns:
                    c = c.replace("客隊",'').replace("Away_",'')
                    col.append(c)
                data_home_inaway.columns = col

                data_home_all = data_home_inhome.append(data_home_inaway)
                col = []
                for c in data_home_all.columns:
                    if c == '得分':
                        c = '主隊' + c
                    else:
                        c = 'Home_' + c
                    col.append(c)
                data_home_all.columns = col
                #home_mean = dict(data_home_all.mean())
                n_days =  len(data_home_all)  # 使用過去天的資料
                data_diff = (data_one_havenow.index[-1] -data_home_all.index).days
                weights = np.exp((data_diff/n_days))
                data_weights = weights / np.sum(weights)
                weighted_mean =np.average(data_home_all.astype('float'), axis=0, weights=data_weights)
                weighted_mean_data_home_all = dict(pd.DataFrame(weighted_mean,index=data_home_all.columns)[0])

                dict_one = dict(**dict_one,**weighted_mean_data_home_all)


                #客隊在主隊
                data_inhome = data_one[data_one['主隊'] == away]
                col = []
                for c in data_inhome.columns:
                    if (c == '主隊得分') or ((('batting' in c) or ('patching' in c)) and ('Home_' in c)):
                        col.append(c)
                data_away_inhome = data_inhome[col]
                col = []
                for c in data_away_inhome.columns:
                    c = c.replace("主隊",'').replace("Home_",'')
                    col.append(c)
                data_away_inhome.columns = col

                #客隊在客隊
                data_inaway = data_one[data_one['客隊'] == away]
                col = []
                for c in data_inaway.columns:
                    if (c == '客隊得分') or ((('batting' in c) or ('patching' in c)) and ('Away_' in c)):
                        col.append(c)
                data_away_inaway = data_inaway[col]
                col = []
                for c in data_away_inaway.columns:
                    c = c.replace("客隊",'').replace("Away_",'')
                    col.append(c)
                data_away_inaway.columns = col
                data_away_all = data_away_inhome.append(data_away_inaway)
                col = []
                for c in data_away_all.columns:
                    if c == '得分':
                        c = '客隊' + c
                    else:
                        c = 'Away_' + c
                    col.append(c)
                data_away_all.columns = col
                #away_mean = dict(data_away_all.mean())
                n_days =  len(data_away_all)  # 使用過去天的資料
                data_diff = (data_one_havenow.index[-1] -data_away_all.index).days
                weights = np.exp((data_diff/n_days))
                data_weights = weights / np.sum(weights)
                weighted_mean =np.average(data_away_all.astype('float'), axis=0, weights=data_weights)
                weighted_mean_data_away_all = dict(pd.DataFrame(weighted_mean,index=data_away_all.columns)[0])
                dict_one = dict(**dict_one,**weighted_mean_data_away_all)


                #w/l
                #隊伍位置相同
                data_both_same = data_one[((data_one['主隊'] == home) & (data_one['客隊'] == away))]
                col = []
                for c in data_both_same.columns:
                    if (c == 'W/L'):
                        col.append(c)
                data_wl_same = data_both_same[col]
                #隊伍位置交換
                data_both_change = data_one[((data_one['主隊'] == away) & (data_one['客隊'] == home))]
                col = []
                for c in data_both_change.columns:
                    if (c == 'W/L'):
                        col.append(c)
                data_wl_change = data_both_change[col]
                data_wl_change['W/L'] = data_wl_change['W/L'].apply(lambda x : float(str(int(x)).replace('1','0')) if x == 1 else float(str(int(x)).replace('0','1')))


                #投手
                #主隊
                sp_home_data = data_one_havenow.iloc[-1:][['Home_SP_href',
                'Home_局數', 'Home_球數', 'Home_安打', 'Home_失分', 'Home_自責失分',
                'Home_全壘打', 'Home_保送', 'Home_三振', 'Home_勝投', 'Home_敗投', 'Home_救援',
                'Home_防禦率','Home_ERA+','Home_FIP-','Home_WHIP-','Home_k9+','ERA_avg','FIP_avg','WHIP_avg','K9_avg']]
                sp_name = sp_home_data['Home_SP_href'].iloc[0].split("/")[-2]
                sp_data = pd.read_excel(f"{self.path_model}/SP/{sp_name}.xlsx",index_col='Date')
                sp_before = sp_data[sp_data.index < sp_home_data.index[0]]
                sp_before_data = sp_before.iloc[-5:,5:-4]
                if len(sp_before_data) > 0:
                    n_days = len(sp_before_data)   # 使用過去天的資料
                    data_diff = (sp_before_data.index - sp_home_data.index[0]).days
                    weights = np.exp((data_diff/n_days))
                    data_weights = weights / np.sum(weights)
                    weighted_mean =np.average(sp_before_data.astype('float'), axis=0, weights=data_weights)
                    weighted_mean_data_home_sp = pd.DataFrame(weighted_mean,index=sp_before_data.columns)[0]
                    sp_data_era = round(weighted_mean_data_home_sp['自責失分']*9/float(str(weighted_mean_data_home_sp['局數']).replace('0','1')),2)
                    sp_era = sp_home_data['ERA_avg'].iloc[0] - sp_data_era
                    FIP = (weighted_mean_data_home_sp['全壘打']*13 + weighted_mean_data_home_sp['保送']*3 - weighted_mean_data_home_sp['三振']*2) /float(str(weighted_mean_data_home_sp['局數']).replace('0','1')) + 3.2
                    sp_fip = ((sp_home_data['FIP_avg'].iloc[0] - FIP) / sp_home_data['ERA_avg'].iloc[0])*100
                    whip = (weighted_mean_data_home_sp['安打'] + weighted_mean_data_home_sp['保送']) / float(str(weighted_mean_data_home_sp['局數']).replace('0','1'))
                    sp_whip = sp_home_data['WHIP_avg'].iloc[0] / whip
                    k9 = weighted_mean_data_home_sp['三振'] / float(str(weighted_mean_data_home_sp['局數']).replace('0','1'))
                    sp_k9 =  k9 - sp_home_data['K9_avg'].iloc[0]
                    weighted_mean_data_home_sp['勝投'] = sp_before.iloc[-1:]['勝投'].iloc[0]
                    weighted_mean_data_home_sp['敗投'] = sp_before.iloc[-1:]['敗投'].iloc[0]
                    weighted_mean_data_home_sp['救援'] = sp_before.iloc[-1:]['救援'].iloc[0]
                    weighted_mean_data_home_sp['防禦率'] = sp_data_era
                    weighted_mean_data_home_sp['ERA+'] = sp_era
                    weighted_mean_data_home_sp['FIP-'] = sp_fip
                    weighted_mean_data_home_sp['WHIP-'] = sp_whip
                    weighted_mean_data_home_sp['k9+'] = sp_k9
                    col = []
                    for c in weighted_mean_data_home_sp.index:
                        c = "Home_" + c
                        col.append(c)
                    weighted_mean_data_home_sp.index = col
                    sp_home_dict = dict(weighted_mean_data_home_sp)
                else:
                    sp_home_dict = {
                        'Home_局數' : 0,
                        'Home_球數' : 0,
                        'Home_安打' : 0,
                        'Home_失分' : 0,
                        'Home_自責失分' : 0,
                        'Home_全壘打' : 0, 
                        'Home_保送' : 0, 
                        'Home_三振' : 0, 
                        'Home_勝投' : 0, 
                        'Home_敗投' : 0, 
                        'Home_救援' : 0,
                        'Home_防禦率' : 0,
                        'Home_ERA+' : 0, 
                        'Home_FIP-' : 0, 
                        'Home_WHIP-' : 0, 
                        'Home_k9+' : 0, 

                    }
                dict_one = dict(**dict_one,**sp_home_dict)

                #客隊
                sp_away_data = data_one_havenow.iloc[-1:][['Away_SP_href',
                'Away_局數', 'Away_球數', 'Away_安打', 'Away_失分', 'Away_自責失分',
                'Away_全壘打', 'Away_保送', 'Away_三振', 'Away_勝投', 'Away_敗投', 'Away_救援',
                'Away_防禦率', 'Away_ERA+', 'Away_FIP-','Away_WHIP-', 'Away_k9+','ERA_avg','FIP_avg','WHIP_avg','K9_avg']]
                sp_name = sp_away_data['Away_SP_href'].iloc[0].split("/")[-2]
                sp_data = pd.read_excel(f"{self.path_model}/SP/{sp_name}.xlsx",index_col='Date')
                sp_before = sp_data[sp_data.index < sp_home_data.index[0]]
                sp_before_data = sp_before.iloc[-5:,5:-4]
                if len(sp_before_data) > 0:
                    n_days = len(sp_before_data)   # 使用過去天的資料
                    data_diff = (sp_before_data.index - sp_home_data.index[0]).days
                    weights = np.exp((data_diff/n_days))
                    data_weights = weights / np.sum(weights)
                    weighted_mean =np.average(sp_before_data.astype('float'), axis=0, weights=data_weights)
                    weighted_mean_data_away_sp = pd.DataFrame(weighted_mean,index=sp_before_data.columns)[0]
                    sp_data_era = round(weighted_mean_data_away_sp['自責失分']*9/weighted_mean_data_away_sp['局數'],2)
                    sp_era = sp_away_data['ERA_avg'].iloc[0] - sp_data_era
                    FIP = (weighted_mean_data_away_sp['全壘打']*13 + weighted_mean_data_away_sp['保送']*3 - weighted_mean_data_away_sp['三振']*2) / float(str(weighted_mean_data_away_sp['局數']).replace('0','1')) + 3.2
                    sp_fip = ((sp_away_data['FIP_avg'].iloc[0] - FIP) / sp_away_data['ERA_avg'].iloc[0])*100
                    whip = (weighted_mean_data_away_sp['安打'] + weighted_mean_data_away_sp['保送']) / float(str(weighted_mean_data_away_sp['局數']).replace('0','1'))
                    sp_whip = sp_away_data['WHIP_avg'].iloc[0] / whip
                    k9 = weighted_mean_data_away_sp['三振'] / float(str(weighted_mean_data_away_sp['局數']).replace('0','1'))
                    sp_k9 =  k9 - sp_away_data['K9_avg'].iloc[0]
                    weighted_mean_data_away_sp['勝投'] = sp_before.iloc[-1:]['勝投'].iloc[0]
                    weighted_mean_data_away_sp['敗投'] = sp_before.iloc[-1:]['敗投'].iloc[0]
                    weighted_mean_data_away_sp['救援'] = sp_before.iloc[-1:]['救援'].iloc[0]
                    weighted_mean_data_away_sp['防禦率'] = sp_data_era
                    weighted_mean_data_away_sp['ERA+'] = sp_era
                    weighted_mean_data_away_sp['FIP-'] = sp_fip
                    weighted_mean_data_away_sp['WHIP-'] = sp_whip
                    weighted_mean_data_away_sp['k9+'] = sp_k9
                    col = []
                    for c in weighted_mean_data_away_sp.index:
                        c = "Away_" + c
                        col.append(c)
                    weighted_mean_data_away_sp.index = col
                    sp_away_dict = dict(weighted_mean_data_away_sp)
                else:
                    sp_away_dict = {
                        'Away_局數' : 0,
                        'Away_球數' : 0,
                        'Away_安打' : 0,
                        'Away_失分' : 0,
                        'Away_自責失分' : 0,
                        'Away_全壘打' : 0, 
                        'Away_保送' : 0, 
                        'Away_三振' : 0, 
                        'Away_勝投' : 0, 
                        'Away_敗投' : 0, 
                        'Away_救援' : 0,
                        'Away_防禦率' : 0,
                        'Away_ERA+' : 0,
                        'Away_FIP-' : 0,
                        'Away_WHIP-' : 0,
                        'Away_k9+' : 0
                    }
                dict_one = dict(**dict_one,**sp_away_dict)

                data_wl_all = data_wl_same.append(data_wl_change)
                data_wl_meam = dict(round(data_wl_all.mean(),2))
                dict_one = dict(**dict_one,**data_wl_meam)
                #dict_all.append(dict_one)
                data_one_havenow_new = data_one_havenow.fillna(dict_one)
                merged_df[merged_df['Eventcode_Now'] == eventcode_now] = data_one_havenow_new
                eventcode_have31.append(eventcode_now)
                print(f"{date} {eventcode} successful!!")
        merged_df2 = merged_df[merged_df['Eventcode_Now'].isin(eventcode_have31)]
        merged_df2['Home_batting_打擊率'] = merged_df2['Home_batting_安打']/merged_df2['Home_batting_打數']
        merged_df2['Away_batting_打擊率'] = merged_df2['Away_batting_安打']/merged_df2['Away_batting_打數']

        merged_df2['Home_patching_防禦'] = merged_df2['Home_patching_失分']*9/(merged_df2['Home_patching_局數']).replace(0,1)
        merged_df2['Away_patching_防禦'] = merged_df2['Away_patching_失分']*9/(merged_df2['Away_patching_局數']).replace(0,1)

        merged_df2['Home_bullpenpatching_防禦率'] = merged_df2['Home_bullpenpatching_責失']*9/(merged_df2['Home_bullpenpatching_局數']).replace(0,1)
        merged_df2['Away_bullpenpatching_防禦率'] = merged_df2['Away_bullpenpatching_責失']*9/(merged_df2['Away_bullpenpatching_局數']).replace(0,1)

        merged_df2['Home_防禦率'] = merged_df2['Home_自責失分']*9/(merged_df2['Home_局數']).replace(0,1)
        merged_df2['Away_防禦率'] = merged_df2['Away_自責失分']*9/(merged_df2['Away_局數']).replace(0,1)

        merged_df2['odds'] = round(merged_df2['Awayodds'] / merged_df2['Homeodds'],2)
        merged_df2.drop(['Home_SP_href','Away_SP_href'],axis=1,inplace=True)
        eventcode_now = merged_df2['Eventcode_Now']
        merged_df2.drop('Eventcode_Now',axis=1,inplace=True)
        merged_df2['Eventcode_Now'] = eventcode_now
        merged_df2 = merged_df2.replace(np.inf,0)
        merged_df2.to_excel(f"{self.path}/fillna_to_predictdata_v3.xlsx")
        merged_df2 = pd.read_excel(f"{self.path}/fillna_to_predictdata_v3.xlsx",index_col='Date')
        merged_df2.drop(['Eventcode','Date_Now'],axis=1,inplace=True)
        return merged_df2
    
        
    def NPB_predict(self):
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        print('**********取得賽程(球探網) 爬取開始**********')
        df_sch = self.crawler_titan()
        print('**********取得賽程(球探網) 爬取結束**********')
        print('**********取得資料(球探網) 爬取開始**********')
        df_all = self.titain_data(df_sch)
        print('**********取得資料(球探網) 爬取結束**********')
        df_all2 = df_all[['Eventcode','Both_bettle', 'Home_bettle', 'Away_bettle','Home_NextDate1',
           'Home_NextLocate1', 'Home_NextOppo1', 'Home_NextDate2',
           'Home_NextLocate2', 'Home_NextOppo2', 'Home_NextDate3',
           'Home_NextLocate3', 'Home_NextOppo3', 'Away_NextDate1',
           'Away_NextLocate1', 'Away_NextOppo1', 'Away_NextDate2',
           'Away_NextLocate2', 'Away_NextOppo2', 'Away_NextDate3',
           'Away_NextLocate3', 'Away_NextOppo3']]
        df_titan = df_sch.merge(df_all2,on=['Date','Eventcode'])
        print('**********取得資料(運彩報馬仔) 爬取開始**********')
        df_n = self.crawler_lottonavi(df_sch)
        print('**********取得資料(運彩報馬仔) 爬取結束**********')
        df_titan['客隊'] = df_titan['客隊'].replace(self.teams_changename)
        df_titan['主隊'] = df_titan['主隊'].replace(self.teams_changename)
        df_titan['客隊得分'] = df_titan['客隊得分'].replace('',np.nan)
        df_titan['主隊得分'] = df_titan['主隊得分'].replace('',np.nan)
        df_lottonavi = df_titan.merge(df_n,on=['Date','主隊','主隊得分','客隊','客隊得分'])
        print('**********更新先發投手數據 爬取開始**********')
        self.SP_update(df_lottonavi)
        print('**********更新先發投手數據 爬取結束**********')
        print('**********爬取先發投手數據 爬取開始**********')
        df_sp = self.SP_data(df_lottonavi)
        print('**********爬取先發投手數據 爬取結束**********')
        df_base_and_sp = df_lottonavi.merge(df_sp,on=['Date','主隊','客隊','Eventcode'],how='outer')
        print('**********爬取投手數據 爬取開始**********')
        df_boxscore_all = self.pitcher_data(df_base_and_sp)
        df_boxscore = pd.read_excel(f"{self.path}/boxscore.xlsx",index_col='Date')
        print('**********爬取投手數據 爬取結束**********')
        df_base_and_sp2 = df_base_and_sp.merge(df_boxscore,on=['Date','主隊','客隊','game_href'],how='outer')
        print('**********賠率數據 爬取開始**********')
        df_href = self.oddsportal_href()
        df_all = self.oddsportal_odds_before(df_href)
        df_all2 = self.oddsportal_odds(df_href)
        print('**********賠率數據 爬取結束**********')
        if datetime.now().strftime("%Y-%m-%d") != self.matchdate.strftime("%Y-%m-%d"):
            df_odds =df_all
        else:
            df_odds =df_all.append(df_all2)
        df_odds.index = pd.to_datetime(df_odds.index.strftime("%Y-%m-%d"))
        df_odds['主隊'] = df_odds['主隊'].replace(self.teams_changename_en)
        df_odds['客隊'] = df_odds['客隊'].replace(self.teams_changename_en)
        df_odds['Odds_return'] = df_odds['Odds_return'].apply(lambda x:x.replace("%",''))
        df_odds.to_excel(f"{self.path}/odds_all.xlsx")
        df_odds = pd.read_excel(f"{self.path}/odds_all.xlsx",index_col='Date')
        df_base_and_sp3 = df_base_and_sp2.merge(df_odds,on=['Date','主隊','主隊得分','客隊','客隊得分'])
        df_base_and_sp3 = df_base_and_sp3.drop_duplicates('Eventcode',keep='first')
        df_before_sch = pd.read_excel(f"{self.path_b}/sch_all2.xlsx",index_col='Date')
        df_before_sch = df_before_sch[df_before_sch.index < datetime.strptime(self.yesterday.strftime("%Y-%m-%d"),"%Y-%m-%d")]
        all_sch = df_before_sch.append(df_sch)
        all_sch['主隊'] = all_sch['主隊'].replace(self.teams_changename)
        all_sch['客隊'] = all_sch['客隊'].replace(self.teams_changename)
        all_sch.to_excel(f"{self.path}/sch_all2.xlsx")
        all_sch = pd.read_excel(f"{self.path}/sch_all2.xlsx",index_col='Date')
        print('**********勝率計算 開始**********')
        self.update_winrate(all_sch)
        df_winrate = self.winrateate_data(df_base_and_sp3)
        print('**********勝率計算 結束**********')
        df_base_and_sp4 = df_base_and_sp3.merge(df_winrate,on=['Date','主隊','客隊','Eventcode'])
        print('**********排行計算 開始**********')
        rank_df = self.rank(df_base_and_sp4)
        print('**********排行計算 結束**********')
        df_base_and_sp5 = df_base_and_sp4.merge(rank_df,on=['Date','主隊','客隊','Eventcode'])
        print('**********ELO計算 開始**********')
        df_yesterday = self.elo(df_base_and_sp5)
        print('**********ELO計算 結束**********')
        boxscore_all = pd.read_excel(f"{self.path}/boxscore_all.xlsx",index_col='Date')
        df_argumentvanced = self.argumentvanced_data(boxscore_all,df_yesterday)
        print('**********reference年資料 爬蟲開始**********')
        df_all = self.reference_pitcher_year()
        batting_player_df,pitching_player_df = self.reference_pitcherer_year_data(df_all)
        print('**********reference年資料 爬蟲結束**********')
        h_sp = df_argumentvanced[['主隊','Home_SP','Home_SP_href']]
        h_sp.columns = ['Team','SP','SP_href']
        a_sp = df_argumentvanced[['客隊','Away_SP','Away_SP_href']]
        a_sp.columns = ['Team','SP','SP_href']
        sp_all = pd.concat([h_sp,a_sp],axis=0).drop_duplicates('SP_href',keep='first')
        sp_df = self.chinese_sp_connect(sp_all)
        pitching_player_df = pd.read_excel(f"{self.path}/pitching_year.xlsx",index_col='Year')
        sp_bir_b = pd.read_excel(f"{self.path_b}/sp_bir_reference.xlsx",index_col='SP')
        sp_all2 = self.english_sp_connect(pitching_player_df)
        sp_all3 = sp_all2.reset_index()
        sp_df3 = sp_df.reset_index()
        sp_all3.loc[sp_all3['SP'] == 'Yuki Nishi', 'Birthday'] = '1990-11-10'
        sp_all3[sp_all3['SP'] == 'Yuki Nishi']['Birthday']
        sp_all4 = sp_all3.merge(sp_df3,on=['Birthday','Team'])
        sp_all4.set_index('Birthday',inplace=True)
        sp_all4.to_excel(f"{self.path}/merge_player.xlsx")
        sp_all4 = pd.read_excel(f"{self.path}/merge_player.xlsx",index_col='Birthday')
        sp_all4.columns = ['Player','Team','Player_href','Player_lottonavi','Player_excel']
        pitching_player_df2 = pitching_player_df.reset_index()
        sp_all5 = sp_all4.merge(pitching_player_df2,on=['Player','Player_href'])
        sp_all5.set_index('Year',inplace=True)
        sp_all5 = sp_all5.fillna(0)
        sp_all5.to_excel(f"{self.path}/pitcher_year_v2.xlsx")
        pitcher_year = pd.read_excel(f"{self.path}/pitcher_year_v2.xlsx",index_col='Year')
        sp_df_all = self.sp_year_data(df_argumentvanced,pitcher_year,sp_df)
        df_data = df_argumentvanced.merge(sp_df_all,on=['Date','主隊','客隊','Eventcode'])
        df_year = self.years_data(df_data)
        df_final_newdata = df_data.merge(df_year,on=['Date','主隊','客隊','Eventcode'])
        df_final_newdata.to_excel(f"{self.path}/pred_new.xlsx")
        df_final_newdata = pd.read_excel(f"{self.path}/pred_new.xlsx",index_col='Date')
        df_b = pd.read_csv(f"{self.path_b}/before_preddata.csv",encoding='utf-8-sig',index_col='Date')
        df_b.index = pd.to_datetime(df_b.index)
        df_b = df_b[df_b.index < datetime.strptime(self.yesterday.strftime("%Y-%m-%d"),"%Y-%m-%d")]
        df_now =  df_b[df_b.index > datetime.strptime(self.yesterday.strftime("%Y-%m-%d"),"%Y-%m-%d")]
        col = []
        for c in df_now.columns:
            if 'href' not in c:
                col.append(c)
        df_now = df_now[col]
        _server_gamania = 'ecoco-analysis.database.windows.net'  # No TCP
        _database_gamania = 'Analysis' 
        _uid_gamania = 'crawl'
        _pwd_gamania = '@Guess365123!'
        _port = "1433"

        conn_Guess365 = pyodbc.connect('DRIVER={SQL Server};SERVER='+_server_gamania+';Port='+_port+';DATABASE='+_database_gamania+';UID='+_uid_gamania+';PWD='+_pwd_gamania)  # for MSSQL
        cursor = conn_Guess365.cursor()
        sql = '''INSERT INTO NPB_Date VALUES '''
        for i in range(len(df_now)):
            sql_values = f"{tuple(df_now.iloc[i].values)}"
            sql_values = one.replace(" ","N")
            sql += sql_values
            cursor = conn_Guess365.cursor()
            cursor.execute(sql)
            cursor.commit()
            print(f'{i} isert successful!!')
            sql = '''INSERT INTO NPB_Date VALUES '''
        df_final_newdata['year'] = df_final_newdata.index.year
        df_final_newdata = df_final_newdata[df_b.columns]
        df_final_alldata = df_b.append(df_final_newdata)
        df_final_alldata.to_csv(f"{self.path}/before_preddata.csv",encoding='utf-8-sig')
        
        merged_df =  self.before10_data(df_final_newdata,df_final_alldata)
        merged_df2 = self.data_fill(merged_df)
        from sklearn.preprocessing import StandardScaler,MinMaxScaler
        # 初始化 StandardScaler
        #scaler = StandardScaler()
        scaler = joblib.load(f'{self.path_model}/gru_minmaxscaler.pkl') # 創建MinMaxScaler對象

        eventcode_now_pre = merged_df2['Eventcode_Now']
        x_pre_scaler = round(pd.DataFrame(scaler.transform(merged_df2), columns=merged_df2.columns),4)
        x_pre_scaler['Eventcode_Now'] = eventcode_now_pre.values
        data_array_to_3d = x_pre_scaler.copy()
        eventcode_ns = data_array_to_3d['Eventcode_Now'].unique()

        array_3d = []
        for eventcode_n in eventcode_ns:
            data_2d = data_array_to_3d[(data_array_to_3d['Eventcode_Now'] == eventcode_n)]
            if len(data_2d) > 0:
                array_2d = data_2d.values
                array_3d.append(array_2d)
                print(f"{eventcode_n} successful!!")
        max_shape = tuple(max(s) for s in zip(*[arr.shape for arr in array_3d]))
        filled_arrays_3d = []
        for arr in array_3d:
            new_arr = np.empty(max_shape, dtype=object)
            new_arr[:arr.shape[0], :arr.shape[1]] = arr
            filled_arrays_3d.append(new_arr)
        x_pre_3d = np.stack(filled_arrays_3d,axis=0)
        x_pre2 = x_pre_3d[:,:,:-1]
        def balanced_binary_crossentropy(y_true, y_pred, pos_weight=1, epsilon=1e-7):
            """
            pos_weight: 正樣本權重，默認為1
            epsilon: 避免除以0，默認為1e-7
            """
            # 將y_true轉換為float32，以便與y_pred進行相乘
            y_true = tf.cast(y_true, tf.float32)
            # 計算損失
            loss = -(pos_weight * y_true * K.log(y_pred + epsilon) + (1 - y_true) * K.log(1 - y_pred + epsilon))
            return K.mean(loss)

        def f1_score(y_true, y_pred):
            y_true = K.round(y_true)
            y_pred = K.round(y_pred)
            tp = K.sum(K.cast(y_true * y_pred, 'float'), axis=0)
            fp = K.sum(K.cast((1 - y_true) * y_pred, 'float'), axis=0)
            fn = K.sum(K.cast(y_true * (1 - y_pred), 'float'), axis=0)
            precision = tp / (tp + fp + K.epsilon())
            recall = tp / (tp + fn + K.epsilon())
            f1_score = 2 * precision * recall / (precision + recall + K.epsilon())
            return K.mean(f1_score)
        model = tf.keras.models.load_model(f'{self.path_model}/gru_61_model.h5', custom_objects={
            'balanced_binary_crossentropy': lambda y_true, y_pred: balanced_binary_crossentropy(y_true, y_pred, pos_weight=0.85),
            'f1_score': f1_score
        }, compile=False)
        # 預測
        predictions = model.predict(x_pre2.astype('float32'))
        y_pre = np.where(predictions >= 0.5, 1, 0)
        pre_event = []
        for eventcode,pre,prediction in zip(eventcode_ns,y_pre,predictions):
            pre_event_one = {
                "Date" : datetime.strptime(self.matchdate.strftime("%Y-%m-%d"),"%Y-%m-%d"),
                "Eventcode" : eventcode,
                "pre_win" : pre[0],
                "pre" : prediction[0]
            }
            pre_event.append(pre_event_one)
        pre_event_df = pd.DataFrame(pre_event)
        pre_event_df.set_index('Date',inplace=True)
        pre_df = df_final_newdata[['主隊', '主隊得分', '客隊', '客隊得分', 'Eventcode','Homeodds', 'Awayodds','W/L']]
        pre_df  = pre_df.reset_index()
        pre_df = pre_df.merge(pre_event_df,on=['Eventcode'])
        pre_df['主隊'] = pre_df['主隊'].replace(self.final_change)
        pre_df['客隊'] = pre_df['客隊'].replace(self.final_change)
        pre_df.set_index('Date',inplace=True)
        predlist = []
        data_vs = []
        for i in range(len(pre_df)):
            pre = pre_df['pre'].iloc[i]
            v = pre_df["客隊"].iloc[i]
            h = pre_df["主隊"].iloc[i]
            url = 'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/NPB/any'
            response = requests.get(url,verify=False,auth=HTTPBasicAuth('rick', '123rick456')).text
            j = json.loads(response)
            json_data = j['response']
            have_update = False
            for d in range(len(json_data)):
                team_name_v = json_data[d]["AwayTeam"][1]
                team_name_h = json_data[d]["HomeTeam"][1]
                odd = json_data[d]['odds']
                if team_name_v == v and team_name_h == h:
                    if odd != []:
                        for o in range(len(odd)):
                            if odd[o]["GroupOptionCode"] == "20":
                                if odd[o]["OptionCode"] == '1':
                                    HomeOdds = odd[o]["OptionRate"]
                                elif odd[o]["OptionCode"] == '2':
                                    AwayOdds = odd[o]["OptionRate"]
                    else:
                        print(v + " v.s " + h + "無賠率" )
                        continue

                if team_name_v == v and team_name_h == h and "_" not in json_data[d]["EventCode"] and json_data[d]["MatchTime"].split(" ")[0] == self.matchdate.strftime("%Y-%m-%d"):
                    have_update = True
                    EventCode = json_data[d]["EventCode"]
                    if pre  > 0.5:
                        homeresult = 'WIN'
                        awayresult = 'LOSE'
                        print(v + " (LOSE) v.s " + h + " (WIN)" )
                        OptionCode = "1"   
                    else:
                        homeresult = 'LOSE'
                        awayresult = 'WIN'
                        print(v + " (WIN) v.s " + h + " (LOSE)" )
                        OptionCode = "2"
                    if (int(round( (1 - pre) * 100,0)) >= 60) or (int(round((pre) * 100,0)) >= 60):
                        main = '1'
                    else:
                        main = '0'
                    if ((pre > 0.5) & (float(HomeOdds) > 1.28)) or ((pre < 0.5) & (float(AwayOdds) > 1.28)): 
                        #url = "https://ecocoapidev1.southeastasia.cloudapp.azure.com/PredictMatchEntry/"
                        data = {'account':"i945win",
                        'password':"adsads2323",
                        'GroupOptionCode':20,
                        'OptionCode':int(OptionCode),
                        'EventCode':EventCode,
                        'predict_type':'Selling',
                        "HomeOdds":float(HomeOdds),
                        "AwayOdds":float(AwayOdds),
                        "HomeConfidence":str(int(round( (pre) * 100,0))) + "%",
                        "AwayConfidence":str(int(round((1-pre) * 100,0))) + "%",
                        "main" : main}
                        predlist.append(data)
                        print(data)
                    vs_one = {
                        "NewModel_Home" : h,
                        "NewModel_HomeResult" : homeresult,
                        "NewModel_HomeConfidence":str(int(round( (pre) * 100,0))) + "%",
                        "NewModel_Away" : v,
                        "NewModel_AwayResult" : awayresult,
                        "NewModel_AwayConfidence":str(int(round((1-pre) * 100,0))) + "%",
                    }
                    data_vs.append(vs_one)
            vs = pd.DataFrame(data_vs)
            vs.to_excel(f"{self.path}/newmodel_pre.xlsx")
            url =f'https://{self.domain_name}/UserMemberSellingPushMessage'
            json_= {"SubscribeLevels":"free/NPB/VIP",
                    "predict_winrate":"58.7%",
                    "title":"本季準確度 : ",
                    "body_data":"2021賽季回測|39050|852過500|58.7%",
                    "TournamentText_icon":"https://i.imgur.com/4YeALVb.jpeg",
                    "body_image":"https://i.imgur.com/w4MQwdZ.png",
                    "predlist":predlist,
                    "connect":False,
                    "banner":"NPB",
                    "check":False}
            response = requests.post(url, json = json_, auth=HTTPBasicAuth('rick', '123rick456'), verify=False).text
            print(response)
            print(predlist)
            
if __name__ == '__main__':
    NPBPredict = NPBPredictModel()
    NPBPredict.NPB_predict()
