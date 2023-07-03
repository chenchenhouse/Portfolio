#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#html解析
from bs4 import BeautifulSoup
#動態爬蟲
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
#DEEP LEARNING
from sklearn.preprocessing import StandardScaler
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


class FIFAPredict(object):
    def __init__(self):
        self.column_name = ["Eventcode"]
        self.beforetime = ((datetime.now() - timedelta(days=1)).replace(hour=0,minute=0,second=0))
        self.nexttime = ((datetime.now() + timedelta(days=1)).replace(hour=23,minute=59,second=59))
        self.changname = {'Brazil': '巴西','Russia': '俄羅斯','Ecuador': '厄瓜多','Belarus': '白俄羅斯','France': '法國','Netherlands': '荷蘭',
                          'Guyana': '蓋亞那','Argentina': '阿根廷','Bulgaria': '保加利亞','Serbia': '塞爾維亞','Canada': '加拿大','Poland': '波蘭',
                          'Switzerland': '瑞士','NorthMacedonia': '北馬其頓','Wales': '威爾斯','Ireland': '愛爾蘭','Qatar': '卡達','Japan': '日本',
                          'Iraq': '伊拉克','Bolivia': '玻利維亞','Iran': '伊朗','Belgium': '比利時','CostaRica': '哥斯大黎加','Spain': '西班牙',
                          'Mexico': '墨西哥','Chile': '智利','USA': '美國','Iceland': '冰島','Croatia': '克羅埃西亞','Romania': '羅馬尼亞',
                          'Honduras': '宏都拉斯','Germany': '德國','Venezuela': '委內瑞拉','Oman': '阿曼','SouthKorea': '南韓','Tunisia': '突尼西亞',
                          'SaudiArabia': '沙烏地阿拉伯','CapeVerde': '維德角','Albania': '阿爾巴尼亞','Panama': '巴拿馬','Turkey': '土耳其','Gabon': '加彭',
                          'Morocco': '摩洛哥','Yemen': '葉門','Bahrain': '巴林','Kuwait': '科威特','Namibia': '納米比亞','Ghana': '迦納','Angola': '安哥拉',
                          'IvoryCoast': '象牙海岸','Niger': '尼日','Togo': '多哥','Sweden': '瑞典','Greece': '希臘','Portugal': '葡萄牙','Cyprus': '賽普勒斯',
                          'BurkinaFaso': '布吉納法索','Mali': '馬利','Israel': '以色列','Uruguay': '烏拉圭','Kazakhstan': '哈薩克','Cameroon': '喀麥隆',
                          'Scotland': '蘇格蘭','CzechRepublic': '捷克','Tanzania': '坦尚尼亞','Senegal': '塞內加爾','Australia': '澳洲','Jordan': '約旦',
                          'Azerbaijan': '亞塞拜然','Denmark': '丹麥','Peru': '秘魯','Ukraine': '烏克蘭','Lebanon': '黎巴嫩','Moldova': '摩爾多瓦',
                          'Sudan': '蘇丹','SierraLeone': '獅子山','China': '中國','DRCongo': '剛果民主共和國','Lesotho': '賴索托','EquatorialGuinea': '赤道幾內亞',
                          'Liberia': '賴比瑞亞','Uzbekistan': '烏茲別克','Italy': '義大利','Nigeria': '奈及利亞','Colombia': '哥倫比亞','Zambia': '尚比亞',
                          'Liechtenstein': '列支敦斯登','Georgia': '佐治亞','Malta': '馬爾他','NorthernIreland': '北愛爾蘭','Finland': '芬蘭','Estonia': '愛沙尼亞',
                          'Andorra': '安道爾','FaroeIslands': '法羅群島','Paraguay': '巴拉圭','SanMarino': '聖馬利諾','Armenia': '亞美尼亞','Norway': '挪威',
                          'Jamaica': '牙買加','Thailand': '泰國','NewZealand': '紐西蘭','Austria': '奧地利','Slovenia': '斯洛維尼亞','Egypt': '埃及','SouthAfrica': '南非',
                          'Palestine': '巴勒斯坦','Zimbabwe': '辛巴威','Ethiopia': '衣索比亞','Libya': '利比亞','England': '英格蘭','Montenegro': '蒙特內哥羅','Hungary': '匈牙利',
                          'Kosovo': '科索沃','TrinidadandTobago': '千里達及托巴哥','Bosnia&Herzegovina': '波士尼亞與赫塞哥維納','Gibraltar': '直布羅陀','Botswana': '波札那',
                          'Guatemala': '瓜地馬拉','Slovakia': '斯洛伐克','UnitedArabEmirates': '阿拉伯聯合大公國','Guinea': '幾內亞','Luxembourg': '盧森堡','HongKong': '香港',
                          'ElSalvador': '薩爾瓦多','Uganda': '烏干達','NorthKorea': '北韓','Indonesia': '印尼','PuertoRico': '波多黎各','NorthernIreland': '北愛爾蘭',
                          'Maldives': '馬爾地夫','Dominica': '多米尼克','Latvia': '拉脫維亞','Lithuania': '立陶宛','Turkmenistan': '土庫曼','Myanmar': '緬甸',
                          'Kyrgyzstan': '吉爾吉斯','Olympiacos': '奧林匹亞科斯足球俱樂部','SãoToméandPríncipe': '聖多美普林西比','Rwanda': '盧安達','Gambia': '甘比亞',
                          'India': '印度','Afghanistan': '阿富汗','Tajikistan': '塔吉克','Belize': '貝里斯','Syria': '敘利亞','Algeria': '阿爾及利亞','Singapore': '新加坡',
                          'Comoros': '葛摩','Madagascar': '馬達加斯加','Mauritania': '茅利塔尼亞','Bangladesh': '孟加拉','Cambodia': '柬埔寨','Laos': '寮國',
                          'EastTimor': '東帝汶','Guam': '關島','Bhutan': '不丹','Mozambique': '莫三比克','Djibouti': '吉布地','Burundi': '蒲隆地','Mauritius': '模里西斯',
                          'NKOmiš': '克羅埃西亞','Martinique': '馬丁尼克','Benin': '貝南','Guinea-Bissau': '幾內亞比索','ChineseTaipei': '台灣','CentralAfricanRepublic': '中非共和國',
                          'Mongolia': '蒙古','CaymanIslands': '開曼群島','Aruba': '荷屬阿魯巴','SriLanka': '斯里蘭卡','Nepal': '尼泊爾','Suriname': '蘇利南','Grenada': '格瑞那達',
                          'Lazio': '拉齊奧體育俱樂部','Fiorentina': '佛倫提那足球俱樂部','Tahiti': '大溪地','Malaysia': '馬來西亞','SloveniaB': '斯洛維尼亞','Philippines': '菲律賓',
                          'IranU23': '伊朗','Barbados': '巴貝多','SouthSudan': '南蘇丹','Guadeloupe': '瓜地洛普','CroatiaU23' : '克羅埃西亞','RealBetisBalompié' : '皇家貝提斯',
                          'Haiti' : '海地','SaintVincentandtheGrenadines' : '聖文森及格瑞那丁','Cuba' : '古巴','Catalonia' : '加泰隆尼亞','BasqueCountry' : '巴斯克自治區',
                          'Bermuda' : '百慕達','FrenchGuiana' : '法屬圭亞那','Nicaragua' : '尼加拉瓜','Curaçao' : '庫拉索','CongoRepublic' : '剛果','Kenya' : '肯亞',
                          'Eswatini' : '史瓦帝尼王國','Malawi' : '馬拉威','SaintKittsandNevis' : '聖克里斯多福及尼維斯','Vietnam' : '越南'}
        self.changname2 = {'卡塔爾' : '卡達','哥斯達黎加' : '哥斯大黎加','厄瓜多爾' : '厄瓜多','阿聯酋' : '阿拉伯聯合大公國','洪都拉斯' : '宏都拉斯','千里達' : '千里達及托巴哥',
                            '尼日利亞' : '奈及利亞','沙地阿拉伯' : '沙烏地阿拉伯','意大利' : '義大利','克羅地亞' : '克羅埃西亞','黑山' : '蒙特內哥羅','科摩羅' : '葛摩',
                            '馬拉維' : '馬拉威','委内瑞拉' : '委內瑞拉','肯雅' : '肯亞','加納' : '迦納','格魯吉亞' : '喬治亞','阿塞拜疆' : '亞塞拜然','吉爾吉斯坦' : '吉爾吉斯',
                            '斯威士蘭' : '史瓦帝尼王國','波斯尼亞' : '波士尼亞與赫塞哥維納','畿內亞比紹' : '幾內亞比索','斯洛文尼亞' : '斯洛維尼亞','列支敦士登' : '列支敦斯登',
                            '聖馬力諾' : '聖馬利諾','科特迪瓦' : '象牙海岸','贊比亞' : '尚比亞','毛里塔尼亞' : '茅利塔尼亞','畿內亞' : '幾內亞','埃塞俄比亞' : '衣索比亞',
                            '赤道畿內亞' : '赤道幾內亞','阿美尼亞' : '亞美尼亞','佛得角共和國' : '維德角','布基納法索' : '布吉納法索','剛果(金)' : '剛果民主共和國',
                            '馬里' : '馬利','布隆迪' : '蒲隆地','尼日爾' : '尼日','馬提尼克' : '馬丁尼克','莫桑比克' : '莫三比克','津巴布韋' : '辛巴威','盧旺達' : '盧安達',
                            '中國香港' : '香港'}
        self.lastname = {
            "威爾斯" : "威爾士"
        }
        self.today = datetime.now()+ timedelta(days=0)
        self.path = f'C:/Users/Guess365User/世足/世足資料/{self.today.strftime("%Y%m%d")}'
        self.path_b = f'C:/Users/Guess365User/世足/世足資料/{self.beforetime.strftime("%Y%m%d")}'
        self.domain_name = '01b4-220-130-85-186.ngrok-free.app'
        
    def schedule(self):
        print("*************************** update schedult start!! ***************************")
        df = pd.read_excel(r"C:/Users/Guess365User/世足/世足資料/team.xlsx",index_col='Rank')
        options = Options()
        # 禁用瀏覽器彈窗避免預設路徑載入失敗
        prefs = {
            'profile.default_content_setting_values':
                {
                    'notifications': 2
                }
        }

        #找到Google擴充套件的檔案位置
        options.add_extension(r'C:\Users\Guess365User\AppData\Local\Google\Chrome\User Data\Default\Extensions\extension_7_0_18_0.crx')
        #將擴充套件放入至Webdriver的開啟網頁內容
        options.add_experimental_option('prefs', prefs)
        #隱藏『Chrome正在受到自動軟體的控制』這項資訊
        options.add_argument("disable-infobars") 
        #options.add_argument('--headless') 
        browser = webdriver.Chrome(options=options)
        #啟動擴充套件連上VPN 
        #連結套件的html位置 chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html
        browser.get("chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html")
        #進入迴圈設定點擊次數、點擊目標、間斷時間
        sleep(5)
        vpb = browser.find_element_by_xpath('//*[@id="screenMain"]/div[3]/div[1]').click()
        sleep(2)
        data_all = []
        new_sch = []
        for i in range(len(df)):
            team = df['Team'].iloc[i]
            eventcode = df['網址'].iloc[i]
            for b in range(2):
                sleep(2)
                browser.get(eventcode)
            sleep(1)
            soup = BeautifulSoup(browser.page_source,"lxml")
            tr = soup.find_all("table",{"class":"tdlink"})[1].find_all("tr")[1:-1]
            count = 0
            for t in range(len(tr)-1):
                td = tr[t].find_all("td")
                if len(td) > 1:
                    date = td[1].text
                    matchtime = datetime.strptime(date,"%Y/%m/%d %H:%M")
                    if matchtime >= self.beforetime and matchtime <= self.nexttime:
                        if td[5].text != "":
                            game = td[0].text
                            home = td[2].text
                            away = td[4].text
                            home_score = td[3].text.split("-")[0]
                            away_score = td[3].text.split("-")[1]
                            eventcode = td[3].find("a").get("href")
                            home_halfscore = td[5].text.split("-")[0]
                            away_halfscore = td[5].text.split("-")[1]
                            data_one = {
                                "Game" : game,
                                "Date" : date,
                                "Eventcode" : eventcode,
                                "Home" : home,
                                "Home_score" : home_score,
                                "Away" : away,
                                "Away_score" : away_score,
                                "Home_halfscore" : home_halfscore,
                                "Away_halfscore" : away_halfscore
                            }
                            data_all.append(data_one)
                            count += 1
                            print(f"{date} {team} before successful!!")
                        else:
                            if '取消' not in td[3].text:
                                game = td[0].text
                                home = td[2].text
                                away = td[4].text
                                home_score = ""
                                away_score = ""
                                eventcode = td[3].find("a").get("href")
                                home_halfscore = ""
                                away_halfscore = ""
                                data_one = {
                                    "Game" : game,
                                    "Date" : date,
                                    "Eventcode" : eventcode,
                                    "Home" : home,
                                    "Home_score" : home_score,
                                    "Away" : away,
                                    "Away_score" : away_score,
                                    "Home_halfscore" : home_halfscore,
                                    "Away_halfscore" : away_halfscore
                                }
                                new_sch.append(data_one)
                                count += 1
                                print(f"{date} {team} newgame successful!!")
            if count == 0:
                print(f"{team} has not newgame need to update!!")
        if data_all != []:
            df_y = pd.DataFrame(data_all)
            df_y.index = df_y['Date']
            df_y.drop('Date',axis=1,inplace=True)
            try:
                df_before = pd.read_excel(f"{path_b}/schedule_all.xlsx",index_col = 'Date')
            except:
                df_before = pd.read_excel(r"C:/Users/Guess365User/世足/世足資料/schedule_all.xlsx",index_col = 'Date')
            df_all = pd.concat([df_before,df_y],axis=0)
            df_all.index = pd.to_datetime(df_all.index)
            df_all = df_all.sort_index()
            df_all['Home'] = df_all['Home'].apply(lambda x : x.replace("1","").replace("2","").replace("3","").replace("B隊","").replace("U23","").replace("U2","").replace("U",""))
            df_all['Away'] = df_all['Away'].apply(lambda x : x.replace("1","").replace("2","").replace("3","").replace("B隊","").replace("U23","").replace("U2","").replace("U",""))
            df_all.drop_duplicates(subset=self.column_name,keep="first",inplace =True)
            df_all.to_excel(f"{self.path}/schedule_all.xlsx")
            df_all = pd.read_excel(f"{self.path}/schedule_all.xlsx",index_col='Date')
            df_yesterday = df_all[df_all.index > self.beforetime]
        else:
            print("Yesterday is no game need to update!!")
            df_yesterday = pd.DataFrame()
        
        if new_sch != []:
            df_sch = pd.DataFrame(new_sch)
            df_sch.index = df_sch['Date']
            df_sch.drop('Date',axis=1,inplace=True)    
            df_sch['Home'] = df_sch['Home'].apply(lambda x : x.replace("1","").replace("2","").replace("3","").replace("B隊","").replace("U23","").replace("U2","").replace("U",""))
            df_sch['Away'] = df_sch['Away'].apply(lambda x : x.replace("1","").replace("2","").replace("3","").replace("B隊","").replace("U23","").replace("U2","").replace("U","")) 
            df_sch.drop_duplicates(subset=self.column_name,keep="last",inplace =True)
            df_sch.to_excel(f"{self.path}/schedule_new.xlsx")
            df_sch = pd.read_excel(f"{self.path}/schedule_new.xlsx",index_col='Date')
            print("*************************** update schedult successful!! ***************************")
        else:
            print("Tomorrow is no game need to update!!")
        return df_sch,df_yesterday

    def update_basedata(self,df_sch,df_yesterday):
        print("*************************** update basedata start!! ***************************")
        #昨日資料更新
        if len(df_yesterday) > 0:
            print(df_yesterday)
            df_base_yesterday = self.basedata(df_yesterday,-1)
            try:
                df_b = pd.read_excel(f"{self.path_b}/basedata.xlsx",index_col='Date')
            except:
                df_b = pd.read_excel(r"C:/Users/Guess365User/世足/世足資料/basedata.xlsx",index_col='Date')
            df_b_all = pd.concat([df_b,df_y],axis=0)
            df_b_all.drop_duplicates(subset=self.column_name,keep="first",inplace =True)
            df_b_all.index = pd.to_datetime(df_b_all.index)
            df_b_all = df_b_all.sort_index()
            df_b_all.to_excel(f"{self.path}/basedata.xlsx")
            df_b_all = pd.read_excel_excel(f"{self.path}/basedata.xlsx")
        else:
            df_b_all = pd.read_excel(f"{self.path}/basedata.xlsx",index_col='Date')
        #隔日比賽資料抓取    
        if len(df_sch) > 0:
            print(df_sch)
            df_base_new = self.basedata(df_sch,1)
            print("*************************** update basedata successful!! ***************************")
        else:
            df_base_new = pd.DataFrame()
        df_base_new = df_base_new[df_base_new.index <= self.nexttime]
        return df_base_new,df_base_yesterday,df_b_all
        
        
    def basedata(self,df_sch,day):
        options = Options()
        # 禁用瀏覽器彈窗避免預設路徑載入失敗
        prefs = {
            'profile.default_content_setting_values':
                {
                    'notifications': 2
                }
        }

        #找到Google擴充套件的檔案位置
        options.add_extension(r'C:\Users\Guess365User\AppData\Local\Google\Chrome\User Data\Default\Extensions\extension_7_0_18_0.crx')
        #將擴充套件放入至Webdriver的開啟網頁內容
        options.add_experimental_option('prefs', prefs)
        #隱藏『Chrome正在受到自動軟體的控制』這項資訊
        options.add_argument("disable-infobars") 
        browser = webdriver.Chrome(options=options)
        #啟動擴充套件連上VPN 
        #連結套件的html位置 chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html
        browser.get("chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html")
        #進入迴圈設定點擊次數、點擊目標、間斷時間
        sleep(5)
        vpb = browser.find_element_by_xpath('//*[@id="screenMain"]/div[3]/div[1]').click()
        sleep(2)
        data_all = [] 
        for i in range(len(df_sch)):
            try:
                sleep(3)
                date = df_sch.index[i]
                eventcode = df_sch['Eventcode'].iloc[i]
                browser.get(eventcode)
                soup = BeautifulSoup(browser.page_source,"lxml")
                sleep(2) 
                try:
                    matchitem = soup.find('div',{"class":"vs"}).find_all("div")[2].find_all("label")
                    weather = matchitem[1].split("：")[1]
                    temperature = matchitem[2].split("：")[1][0]
                except:
                    weather = None
                    temperature = None
                if len(soup.find_all(id="trCornerTotal")) == 2:
                    td = soup.find_all(id="trCornerTotal")[0].find_all("td")
                    td_home_fhandicap = float(td[1].text)
                    td_handicap_firest = float(td[2].text)
                    td_away_fhandicap = float(td[3].text)
                    td_home_ehandicap = float(td[5].text)
                    td_handicap_end = float(td[6].text)
                    td_away_ehandicap = float(td[7].text)
                    td = soup.find_all(id="trCornerTotal")[1].find_all("td")
                    td_home_fgoal = float(td[1].text)
                    td_goal_firest = float(td[2].text)
                    td_away_fgoal = float(td[3].text)
                    td_home_egoal = float(td[5].text)
                    td_goal_end = float(td[6].text)
                    td_away_egoal = float(td[7].text)
                elif len(soup.find_all(id="trCornerTotal")) == 1:
                    td = soup.find(id="trCornerTotal").find_all("td")
                    td_home_fgoal = float(td[1].text)
                    td_goal_firest = float(td[2].text)
                    td_away_fgoal = float(td[3].text)
                    td_home_egoal = float(td[5].text)
                    td_goal_end = float(td[6].text)
                    td_away_egoal = float(td[7].text)
                    td_home_fhandicap = None
                    td_handicap_firest = None
                    td_away_fhandicap = None
                    td_home_ehandicap = None
                    td_handicap_end = None
                    td_away_ehandicap = None
                else:
                    td_home_fgoal = None
                    td_goal_firest = None
                    td_away_fgoal = None
                    td_home_egoal = None
                    td_goal_end = None
                    td_away_egoal = None
                    td_home_fhandicap = None
                    td_handicap_firest = None
                    td_away_fhandicap = None
                    td_home_ehandicap = None
                    td_handicap_end = None
                    td_away_ehandicap = None
                data_one = {
                    "Date" : date,
                    "Eventcode" : eventcode,
                    "Weather" : weather,
                    "Temperature" : temperature,
                    "Home_讓球初盤" : td_home_fhandicap,
                    "讓球初盤" : td_handicap_firest,
                    "Away_讓球初盤" : td_away_fhandicap,
                    "Home_讓球終盤" : td_home_ehandicap,
                    "讓球終盤" : td_handicap_end,
                    "Away_讓球終盤" : td_away_ehandicap,
                    "Home_進球數初盤" : td_home_fgoal,
                    "進球數初盤" : td_goal_firest,
                    "Away_進球數初盤" : td_away_fgoal,
                    "Home_進球數終盤" : td_home_egoal,
                    "進球數終盤" : td_goal_end,
                    "Away_進球數終盤" : td_away_egoal
                }
                if day == -1:
                    #本場技術統計
                    li = soup.find(id="teamTechDiv").find_all("li")
                    for t in range(len(li)):
                        item = li[t].find("div",{"class":"data"}).find_all("span")[1].text
                        if "率" in item:
                            home = float(li[t].find("div",{"class":"data"}).find_all("span")[0].text.replace("%",""))
                            away = float(li[t].find("div",{"class":"data"}).find_all("span")[2].text.replace("%",""))
                            data_one[f'Home_{item}'] = home
                            data_one[f'Away_{item}'] = away
                        elif item == '先開球' or '第壹' in item or "最後" in item:
                            home = len(li[t].find("div",{"class":"data"}).find_all("span")[0].find_all("img"))
                            away = len(li[t].find("div",{"class":"data"}).find_all("span")[2].find_all("img"))
                            if home == 1 and away == 0:
                                data_one[item] = 1
                            else:
                                data_one[item] = 0
                        else:
                            home = int(li[t].find("div",{"class":"data"}).find_all("span")[0].text)
                            away = int(li[t].find("div",{"class":"data"}).find_all("span")[2].text)
                            data_one[f'Home_{item}'] = home
                            data_one[f'Away_{item}'] = away
                #陣容
                try:
                    home_team = soup.find("div",{"class":"homeN"}).text.split(" ")[1]
                    away_team = soup.find("div",{"class":"guestN"}).text.split(" ")[1]
                except:
                    home_team = None
                    away_team = None
                data_one[f'Home_陣容'] = home_team
                data_one[f'Away_陣容'] = away_team

                #技統數據
                table = soup.find("div",{"class":"content two"}).find_all("table")
                table1 = table[0].find_all("tr")
                table2 = table[1].find_all("tr")
                #進球
                home_gold3 = float(table1[3].find_all("td")[0].text.replace("-","0"))
                home_gold10 = float(table1[3].find_all("td")[1].text.replace("-","0"))
                away_gold3 = float(table1[3].find_all("td")[3].text.replace("-","0"))
                away_gold10 = float(table1[3].find_all("td")[4].text.replace("-","0"))
                #失球
                home_missedshot3 = float(table1[4].find_all("td")[0].text.replace("-","0"))
                home_missedshot10 = float(table1[4].find_all("td")[1].text.replace("-","0"))
                away_missedshot3 = float(table1[4].find_all("td")[3].text.replace("-","0"))
                away_missedshot10 = float(table1[4].find_all("td")[4].text.replace("-","0"))
                #被射門
                home_beshoted3 = float(table1[5].find_all("td")[0].text.replace("-","0"))
                home_beshoted10 = float(table1[5].find_all("td")[1].text.replace("-","0"))
                away_beshoted3 = float(table1[5].find_all("td")[3].text.replace("-","0"))
                away_beshoted10 = float(table1[5].find_all("td")[4].text.replace("-","0"))
                #角球
                home_corner_kick3 = float(table1[6].find_all("td")[0].text.replace("-","0"))
                home_corner_kick10 = float(table1[6].find_all("td")[1].text.replace("-","0"))
                away_corner_kick3 = float(table1[6].find_all("td")[3].text.replace("-","0"))
                away_corner_kick10 = float(table1[6].find_all("td")[4].text.replace("-","0"))
                #黃牌
                home_yellow_card3 = float(table1[7].find_all("td")[0].text.replace("-","0"))
                home_yellow_card10 = float(table1[7].find_all("td")[1].text.replace("-","0"))
                away_yellow_card3 = float(table1[7].find_all("td")[3].text.replace("-","0"))
                away_yellow_card10 = float(table1[7].find_all("td")[4].text.replace("-","0"))
                #犯規
                home_foul3 = float(table1[8].find_all("td")[0].text.replace("-","0"))
                home_foul10 = float(table1[8].find_all("td")[1].text.replace("-","0"))
                away_foul3 = float(table1[8].find_all("td")[3].text.replace("-","0"))
                away_foul10 = float(table1[8].find_all("td")[4].text.replace("-","0"))
                #控球率
                home_possession3 = float(table1[9].find_all("td")[0].text.replace("%","").replace("-","0"))
                home_possession10 = float(table1[9].find_all("td")[1].text.replace("%","").replace("-","0"))
                away_possession3 = float(table1[9].find_all("td")[3].text.replace("%","").replace("-","0"))
                away_possession10 = float(table1[9].find_all("td")[4].text.replace("%","").replace("-","0"))

                #進失球機率
                #1~15
                home_15min_gold = float(table2[3].find_all("td")[0].text.replace("%",""))
                home_15min_missedshot = float(table2[3].find_all("td")[1].text.replace("%",""))
                away_15min_gold = float(table2[3].find_all("td")[3].text.replace("%",""))
                away_15min_missedshot = float(table2[3].find_all("td")[4].text.replace("%",""))
                #16~30
                home_30min_gold = float(table2[4].find_all("td")[0].text.replace("%",""))
                home_30min_missedshot = float(table2[4].find_all("td")[1].text.replace("%",""))
                away_30min_gold = float(table2[4].find_all("td")[3].text.replace("%",""))
                away_30min_missedshot = float(table2[4].find_all("td")[4].text.replace("%",""))
                #31~45
                home_45min_gold = float(table2[5].find_all("td")[0].text.replace("%",""))
                home_45min_missedshot = float(table2[5].find_all("td")[1].text.replace("%",""))
                away_45min_gold = float(table2[5].find_all("td")[3].text.replace("%",""))
                away_45min_missedshot = float(table2[5].find_all("td")[4].text.replace("%",""))
                #46~60
                home_60min_gold = float(table2[6].find_all("td")[0].text.replace("%",""))
                home_60min_missedshot = float(table2[6].find_all("td")[1].text.replace("%",""))
                away_60min_gold = float(table2[6].find_all("td")[3].text.replace("%",""))
                away_60min_missedshot = float(table2[6].find_all("td")[4].text.replace("%",""))
                #61~75
                home_75min_gold = float(table2[7].find_all("td")[0].text.replace("%",""))
                home_75min_missedshot = float(table2[7].find_all("td")[1].text.replace("%",""))
                away_75min_gold = float(table2[7].find_all("td")[3].text.replace("%",""))
                away_75min_missedshot = float(table2[7].find_all("td")[4].text.replace("%",""))
                #76~90
                home_90min_gold = float(table2[8].find_all("td")[0].text.replace("%",""))
                home_90min_missedshot = float(table2[8].find_all("td")[1].text.replace("%",""))
                away_90min_gold = float(table2[8].find_all("td")[3].text.replace("%",""))
                away_90min_missedshot = float(table2[8].find_all("td")[4].text.replace("%",""))
                data_one2 = {
                    "Home_進球(近3場)" : home_gold3,
                    "Away_進球(近3場)" : away_gold3,
                    "Home_失球(近3場)" : home_missedshot3,
                    "Away_失球(近3場)" : away_missedshot3,
                    "Home_被射門(近3場)" : home_beshoted3,
                    "Away_被射門(近3場)" : away_beshoted3,
                    "Home_角球(近3場)" : home_corner_kick3,
                    "Away_角球(近3場)" : away_corner_kick3,
                    "Home_黃牌(近3場)" : home_yellow_card3,
                    "Away_黃牌(近3場)" : away_yellow_card3,
                    "Home_犯規(近3場)" : home_foul3,
                    "Away_犯規(近3場)" : away_foul3,
                    "Home_控球率(近3場)" : home_possession3,
                    "Away_控球率(近3場)" : away_possession3,
                    "Home_進球(近10場)" : home_gold10,
                    "Away_進球(近10場)" : away_gold10,
                    "Home_失球(近10場)" : home_missedshot10,
                    "Away_失球(近10場)" : away_missedshot10,
                    "Home_被射門(近10場)" : home_beshoted10,
                    "Away_被射門(近10場)" : away_beshoted10,
                    "Home_角球(近10場)" : home_corner_kick10,
                    "Away_角球(近10場)" : away_corner_kick10,
                    "Home_黃牌(近10場)" : home_yellow_card10,
                    "Away_黃牌(近10場)" : away_yellow_card10,
                    "Home_犯規(近10場)" : home_foul10,
                    "Away_犯規(近10場)" : away_foul10,
                    "Home_控球率(近10場)" : home_possession10,
                    "Away_控球率(近10場)" : away_possession10,
                    "Home_進球率(15m)" : home_15min_gold,
                    "Away_進球率(15m)" : away_15min_gold,
                    "Home_進球率(30m)" : home_30min_gold,
                    "Away_進球率(30m)" : away_30min_gold,
                    "Home_進球率(45m)" : home_45min_gold,
                    "Away_進球率(45m)" : away_45min_gold,
                    "Home_進球率(60m)" : home_60min_gold,
                    "Away_進球率(60m)" : away_60min_gold,
                    "Home_進球率(75m)" : home_75min_gold,
                    "Away_進球率(75m)" : away_75min_gold,
                    "Home_進球率(90m)" : home_90min_gold,
                    "Away_進球率(90m)" : away_90min_gold,
                    "Home_失球率(15m)" : home_15min_missedshot,
                    "Away_失球率(15m)" : away_15min_missedshot,
                    "Home_失球率(30m)" : home_30min_missedshot,
                    "Away_失球率(30m)" : away_30min_missedshot,
                    "Home_失球率(45m)" : home_45min_missedshot,
                    "Away_失球率(45m)" : away_45min_missedshot,
                    "Home_失球率(60m)" : home_60min_missedshot,
                    "Away_失球率(60m)" : away_60min_missedshot,
                    "Home_失球率(75m)" : home_75min_missedshot,
                    "Away_失球率(75m)" : away_75min_missedshot,
                    "Home_失球率(90m)" : home_90min_missedshot,
                    "Away_失球率(90m)" : away_90min_missedshot,
                }
                data_one = dict(**data_one,**data_one2)
                data_all.append(data_one)
                print(f"{date} {eventcode} {td_home_egoal} vs {td_away_egoal} successful!!")
            except Exception as e:
                print(e)
                print(f"{date} {eventcode} fail!!")
        df_base = pd.DataFrame(data_all)
        df_base.index = df_base['Date']
        df_base.drop("Date",axis = 1,inplace=True)
        df_base_all = df_sch.merge(df_base,on=['Date','Eventcode'])
        df_base_all.drop_duplicates(subset=self.column_name,keep="last",inplace =True)
        df_base_all = df_base_all.sort_index()
        df_base_all.to_excel(f"{self.path}/newbasefata.xlsx") 
        df_base_all  = pd.read_excel(f"{self.path}/newbasefata.xlsx",index_col='Date') 
        return df_base_all
    
    def before_basedata(self,df_sch,df_base_new,df_b_all):
        data_all = []
        for i in range(len(df_sch)):
            #home
            ##inhome
            home = df_sch['Home'].iloc[i]
            eventcode = df_sch['Eventcode'].iloc[i]
            date = df_sch.index[i]
            data_one = {
                "Date" : date,
                "Eventcode" : eventcode,
            }
            df_home_inh = df_b_all[(df_b_all['Home'] == home) & (df_b_all.index < date)]
            df_home_inh = df_home_inh[['Home_角球', 'Away_角球', 'Home_半場角球', 'Away_半場角球',
                       'Home_黃牌', 'Away_黃牌', 'Home_射門', 'Away_射門', 'Home_射正', 'Away_射正',
                       'Home_進攻', 'Away_進攻', 'Home_危險進攻', 'Away_危險進攻', 'Home_射門不中',
                       'Away_射門不中', 'Home_控球率', 'Away_控球率', 'Home_半場控球率', 'Away_半場控球率','Home_任意球',
                       'Away_任意球', 'Home_犯規', 'Away_犯規', 'Home_越位', 'Away_越位', 'Home_救球',
                       'Away_救球','Home_傳球', 'Away_傳球','Home_界外球', 'Away_界外球', 'Home_成功搶斷', 'Away_成功搶斷']]

            col = []
            for c in df_home_inh.columns:
                if "Home_" in c:
                    col.append(c)
            df_home_inh = df_home_inh[col]
            col = []
            for c in df_home_inh.columns:
                c = c.replace("Home_","")
                col.append(c)
            df_home_inh.columns = col
            home_sum_inh = df_home_inh.sum()
            home_len_inh  = len(df_home_inh)
            home_avg_inh = home_sum_inh / home_len_inh
            col = []
            for c in home_avg_inh.index:
                col.append("Home_" + c + "_inhome")
            home_avg_inh.index = col
            data_one = dict(**data_one,**dict(home_avg_inh))
            ##inaway
            df_home_ina = df_b_all[(df_b_all['Away'] == home) & (df_b_all.index < date)]
            df_home_ina = df_home_ina[['Home_角球', 'Away_角球', 'Home_半場角球', 'Away_半場角球',
                       'Home_黃牌', 'Away_黃牌', 'Home_射門', 'Away_射門', 'Home_射正', 'Away_射正',
                       'Home_進攻', 'Away_進攻', 'Home_危險進攻', 'Away_危險進攻', 'Home_射門不中',
                       'Away_射門不中', 'Home_控球率', 'Away_控球率', 'Home_半場控球率', 'Away_半場控球率','Home_任意球',
                       'Away_任意球', 'Home_犯規', 'Away_犯規', 'Home_越位', 'Away_越位', 'Home_救球',
                       'Away_救球','Home_傳球', 'Away_傳球','Home_界外球', 'Away_界外球', 'Home_成功搶斷', 'Away_成功搶斷']]
            col = []
            for c in df_home_ina.columns:
                if "Away_" in c:
                    col.append(c)
            df_home_ina = df_home_ina[col]
            col = []
            for c in df_home_ina.columns:
                c = c.replace("Away_","")
                col.append(c)
            df_home_ina.columns = col
            home_sum_ina = df_home_ina.sum()
            home_len_ina  = len(df_home_ina)
            home_avg_ina = home_sum_ina / home_len_ina
            col = []
            for c in home_avg_ina.index:
                col.append("Home_" + c + "_inaway")
            home_avg_ina.index = col
            data_one = dict(**data_one,**dict(home_avg_ina))
            ##total
            home_avg = (home_sum_inh + home_sum_ina) / (home_len_inh + home_len_ina)
            col = []
            for c in home_avg.index:
                col.append("Home_" + c)
            home_avg.index = col
            data_one = dict(**data_one,**dict(home_avg))

            #away
            ##inhome
            away = df_sch['Away'].iloc[i]
            df_away_inh = df_b_all[(df_b_all['Home'] == away) & (df_b_all.index < date)]
            df_away_inh = df_away_inh[['Home_角球', 'Away_角球', 'Home_半場角球', 'Away_半場角球',
                       'Home_黃牌', 'Away_黃牌', 'Home_射門', 'Away_射門', 'Home_射正', 'Away_射正',
                       'Home_進攻', 'Away_進攻', 'Home_危險進攻', 'Away_危險進攻', 'Home_射門不中',
                       'Away_射門不中', 'Home_控球率', 'Away_控球率', 'Home_半場控球率', 'Away_半場控球率','Home_任意球',
                       'Away_任意球', 'Home_犯規', 'Away_犯規', 'Home_越位', 'Away_越位', 'Home_救球',
                       'Away_救球','Home_傳球', 'Away_傳球','Home_界外球', 'Away_界外球', 'Home_成功搶斷', 'Away_成功搶斷']]
            col = []
            for c in df_away_inh.columns:
                if "Home_" in c:
                    col.append(c)
            df_away_inh = df_away_inh[col]
            col = []
            for c in df_away_inh.columns:
                c = c.replace("Home_","")
                col.append(c)
            df_away_inh.columns = col
            away_sum_inh = df_away_inh.sum()
            away_len_inh  = len(df_away_inh)
            away_avg_inh = away_sum_inh / away_len_inh
            col = []
            for c in away_avg_inh.index:
                col.append("Away_" + c + "_inhome")
            away_avg_inh.index = col
            data_one = dict(**data_one,**dict(away_avg_inh))
            ##inaway
            df_away_ina = df_b_all[(df_b_all['Away'] == away) & (df_b_all.index < date)]
            df_away_ina = df_away_ina[['Home_角球', 'Away_角球', 'Home_半場角球', 'Away_半場角球',
                       'Home_黃牌', 'Away_黃牌', 'Home_射門', 'Away_射門', 'Home_射正', 'Away_射正',
                       'Home_進攻', 'Away_進攻', 'Home_危險進攻', 'Away_危險進攻', 'Home_射門不中',
                       'Away_射門不中', 'Home_控球率', 'Away_控球率', 'Home_半場控球率', 'Away_半場控球率','Home_任意球',
                       'Away_任意球', 'Home_犯規', 'Away_犯規', 'Home_越位', 'Away_越位', 'Home_救球',
                       'Away_救球','Home_傳球', 'Away_傳球','Home_界外球', 'Away_界外球', 'Home_成功搶斷','Away_成功搶斷']]
            col = []
            for c in df_away_ina.columns:
                if "Away_" in c:
                    col.append(c)
            df_away_ina = df_away_ina[col]
            col = []
            for c in df_away_ina.columns:
                c = c.replace("Away_","")
                col.append(c)
            df_away_ina.columns = col
            away_sum_ina = df_away_ina.sum()
            away_len_ina  = len(df_away_ina)
            away_avg_ina = away_sum_ina / away_len_ina
            col = []
            for c in away_avg_ina.index:
                col.append("Away_" + c + "_inaway")
            away_avg_ina.index = col
            data_one = dict(**data_one,**dict(away_avg_ina))
            ##total
            away_avg = (away_sum_inh + away_sum_ina) / (away_len_inh + away_len_ina)
            col = []
            for c in away_avg.index:
                col.append("Away_" + c)
            away_avg.index = col
            data_one = dict(**data_one,**dict(away_avg))
            data_all.append(data_one)
            print(f"{date} {eventcode} successful!!")
        df_a = pd.DataFrame(data_all)
        df_a.index = df_a['Date']
        df_a.drop('Date',axis=1,inplace=True)
        df_a.index = pd.to_datetime(df_a.index)
        df_new = df_s.merge(df_a,on=['Date','Eventcode'])
        df_new.index = pd.to_datetime(pd.to_datetime(df_new.index).strftime("%Y-%m-%d"))
        df_new.to_excel(f"{self.path}/newbeforedata.xlsx")
        df_b = pd.read_excel(f"{self.path}/data-base.xlsx",index_col='Date')
        df_all = pd.concat([df_b,df_new],axis=0)
        df_all.index = pd.to_datetime(df_all.index)
        df_all.drop_duplicates(subset=column_name,keep="last",inplace =True)
        df_all = df_all.sort_index()
        df_all.to_excel(f"{self.path}/data-base.xlsx")
        df_all = pd.read_excel(f"{self.path}/data-base.xlsx",index_col='Date')
        return df_all
    
    
    def odds_update(self,df_all):
        print("*************************** update odds start!! ***************************")
        options = Options()
        # 禁用瀏覽器彈窗避免預設路徑載入失敗
        prefs = {
            'profile.default_content_setting_values':
                {
                    'notifications': 2
                }
        }

        #找到Google擴充套件的檔案位置(注意路徑需使用雙斜線 "\\")
        options.add_extension(r'C:\Users\Guess365User\AppData\Local\Google\Chrome\User Data\Default\Extensions\extension_7_0_18_0.crx')
        #將擴充套件放入至Webdriver的開啟網頁內容
        options.add_experimental_option('prefs', prefs)
        #隱藏『Chrome正在受到自動軟體的控制』這項資訊
        options.add_argument("disable-infobars") 
        browser = webdriver.Chrome(options=options)
        #啟動擴充套件連上VPN 
        #連結套件的html位置 chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html
        browser.get("chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html")
        #進入迴圈設定點擊次數、點擊目標、間斷時間
        sleep(5)
        vpb = browser.find_element_by_xpath('//*[@id="screenMain"]/div[3]/div[1]').click()
        sleep(2)
        data_all = []
        if len(df_all) > 0:
            for i in range(len(df_all)):
                date = df_all.index[i]
                home = df_all['Home'].iloc[i]
                away = df_all['Away'].iloc[i]
                eventcode = df_all['Eventcode'].iloc[i].split("/")[-1]
                browser.get(f"http://1x2.titan007.com/oddslist/{eventcode}")
                soup = BeautifulSoup(browser.page_source,"lxml")
                td = soup.find(id='divFooterFload').find("tbody").find(id = 'avgFObj').find_all("td")
                home_fodd = td[1].text
                tie_fodd = td[2].text
                away_fodd = td[3].text
                home_fwinrate = td[4].text
                tie_fwinrate = td[5].text
                away_fwinrate = td[6].text
                return_ratef = td[7].text
                kelly_home = td[8].text
                kelly_tie = td[9].text
                kelly_away = td[10].text
                td = soup.find(id='divFooterFload').find("tbody").find(id = 'avgRObj').find_all("td")
                home_lodd = td[1].text
                tie_lodd = td[2].text
                away_lodd = td[3].text
                home_lwinrate = td[4].text
                tie_lwinrate = td[5].text
                away_lwinrate = td[6].text
                return_ratel = td[7].text
                data_one = {
                    "Date" : date,
                    "Eventcode" : df_all['Eventcode'].iloc[i],
                    "Home_odd(f)" : home_fodd,
                    "Tie_odd(f)" : tie_fodd,
                    "Away_odd(f)" : away_fodd,
                    "Home_oddrate(f)":home_fwinrate,
                    "Tie_oddrate(f)" : tie_fwinrate,
                    "Away_oddrate(f)" : away_fwinrate,
                    "Return_rate(f)" : return_ratef,
                    "Home_kelly(f)" : kelly_home,
                    "Tie_kelly(f)" : kelly_tie,
                    "Away_kelly(f)" : kelly_away,
                    "Home_odd(l)" : home_lodd,

                    "Tie_odd(l)" : tie_lodd,
                    "Away_odd(l)" : away_lodd,
                    "Home_oddrate(l)":home_lwinrate,
                    "Tie_oddrate(l)" : tie_lwinrate,
                    "Away_oddrate(l)" : away_lwinrate,
                    "Return_rate(l)" : return_ratel,
                }
                data_all.append(data_one)
                print(f"{date} {home} vs {away} successful!!")
            df_odds_n = pd.DataFrame(data_all)
            df_odds_n.index = df_odds_n['Date']
            df_odds_n.drop("Date",axis = 1,inplace=True)
            df_odds = pd.read_excel(f"{self.path}/odds.xlsx",index_col='Date')
            df_odds = pd.concat([df_odds,df_n],axis=0)
            df_odds.index = pd.to_datetime(pd.to_datetime(df_odds.index).strftime("%Y-%m-%d"))
            df_odds.drop_duplicates(subset=self.column_name,keep="last",inplace =True)
            df_odds.to_excel(f"{self.path}/odds.xlsx")
            df_odds = df_odds.sort_index()
            print("*************************** update odds successful!! ***************************")
            return df_odds_n
        else:
            return pd.DataFrame()
    
    def update_sofascore(self):
        next_d = ((datetime.now() + timedelta(days=2)).replace(hour=1,minute=59,second=59))
        options = Options()
        # 禁用瀏覽器彈窗避免預設路徑載入失敗
        prefs = {
            'profile.default_content_setting_values':
                {
                    'notifications': 2
                }
        }

        #找到Google擴充套件的檔案位置(注意路徑需使用雙斜線 "\\")
        options.add_extension(r'C:\Users\Guess365User\AppData\Local\Google\Chrome\User Data\Default\Extensions\extension_7_0_18_0.crx')
        #將擴充套件放入至Webdriver的開啟網頁內容
        options.add_experimental_option('prefs', prefs)
        #隱藏『Chrome正在受到自動軟體的控制』這項資訊
        options.add_argument("disable-infobars") 
        browser = webdriver.Chrome(options=options)
        #啟動擴充套件連上VPN 
        #連結套件的html位置 chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html
        browser.get("chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html")
        #進入迴圈設定點擊次數、點擊目標、間斷時間
        sleep(5)
        vpb = browser.find_element_by_xpath('//*[@id="screenMain"]/div[3]/div[1]').click()
        sleep(2)
        data_all = []
        teams = pd.read_excel(r"C:\Users\Guess365User\世足\世足資料\sofascore_team.xlsx",index_col='Rank')
        for t in range(len(teams)):
            eventcode = teams['網址'].iloc[t]
            browser.get(eventcode)
            browser.execute_script('window.scrollTo(0, 700)')
            sleep(3)
            game = browser.find_elements_by_class_name("sc-hLBbgP.dRtNhU.sc-9199a964-1.kusmLq")
            sleep(1)
            count = 0
            for m in range(1,len(game)):
                soup = BeautifulSoup(browser.page_source,"lxml")
                match = soup.find_all("div",{"class":"sc-hLBbgP gudtvp"})
                try:
                    date = datetime.strptime(match[m].find("span").text.replace("AET","").replace("FT","").replace("Canceled",""),"%d/%m/%y")
                except:
                    time = match[m].find("span").text.replace("AET","").replace("FT","").replace("Canceled","")
                    hour = int(time.split(":")[0])
                    minute = int(time.split(":")[1])
                    date = datetime.strptime(datetime.now().strftime("%d/%m/%y"),"%d/%m/%y").replace(hour=hour,minute=minute)
                if date >= self.beforetime and date <= self.nexttime:
                    if date > datetime.now():
                        if count != 0:
                            game[m].click() 
                            count += 1 
                    else:
                        game[m].click() 
                        count += 1
                    sleep(3)
                    if len(browser.find_elements_by_class_name('sc-hLBbgP.sc-eDvSVe.hjLuvI.fRddxb')) > 0:
                        whowin = browser.find_element_by_class_name('sc-hLBbgP.sc-eDvSVe.hjLuvI.fRddxb').click()
                        sleep(3)
                        soup = BeautifulSoup(browser.page_source,"lxml")
                        team = soup.find_all("div",{"class":"sc-hLBbgP eIlfTT","style":"overflow: hidden;"})[m]
                        hometeam = team.find_all("div")[0].text.replace(" ","")
                        awayteam = team.find_all("div")[1].text.replace(" ","")
                        if date > datetime.now():
                            home_score = ""
                            away_score = ""
                        else:
                            score = soup.find_all("div",{"class":"sc-hLBbgP sc-eDvSVe kEuuAX fTFJIj"})[m].find_all("div",{"class":"sc-hLBbgP sc-eDvSVe fuUKnP bMwHQt sc-9199a964-2 kgwLqG score-box"})
                            home_score = score[0].find("span").text
                            away_score = score[1].find("span").text
                        count = soup.find("div",{"class":"sc-hLBbgP sc-eDvSVe lbbBRU ezUKOh"})
                        home_wincount = int(count.find("span",{"color":"secondary.default"}).text.replace(" (You)",""))
                        tie_wincount = int(count.find("span",{"color":"neutral.default"}).text.replace(" ",""))
                        away_wincount = int(count.find("span",{"color":"primary.default"}).text.replace(" ",""))
                        winrate = soup.find_all("span",{"style":"opacity: 1;"})
                        sum_wincount = home_wincount + tie_wincount + away_wincount
                        if len(winrate) == 3:
                            homewinrate = round(float(winrate[0].text.replace("%","")),2)
                            tiewinrate = round(float(winrate[1].text.replace("%","")),2)
                            awaywinrate = round(float(winrate[2].text.replace("%","")),2)
                        else:
                            homewinrate = round((home_wincount/sum_wincount)*100,2)
                            tiewinrate = round((tie_wincount/sum_wincount)*100,2)
                            awaywinrate =  round((away_wincount/sum_wincount)*100,2)
                        data_one = {
                            "Date":date,
                            "Home" : hometeam,
                            "Home_score" : home_score,
                            "Away" : awayteam,
                            "Away_score" : away_score,
                            "Home_wincount" : home_wincount,
                            "Home_winrate" : homewinrate,
                            "Away_wincount" : away_wincount,
                            "Away_winrate" : awaywinrate,
                            "Tie_wincount" : tie_wincount,
                            "Tie_winrate" : tiewinrate,
                        }
                        data_all.append(data_one)
                        print(f"{date} {hometeam} vs {awayteam} successful!!") 
        if data_all != []:
            df_n = pd.DataFrame(data_all)
            df_n.index = df_n['Date']
            df_n.drop('Date',axis=1,inplace=True)
            try:
                df_b = pd.read_excel(f"{self.path_b}/sofascore/sofascore_all.xlsx",index_col='Date')
            except:
                df_b = pd.read_excel(r"C:\Users\Guess365User\世足\世足資料\sofascore\sofascore_all.xlsx",index_col='Date')
            df_sofa = pd.concat([df_b,df_n],axis=0)
            df_sofa.index = pd.to_datetime(pd.to_datetime(df_sofa.index).strftime("%Y-%m-%d"))
            df_sofa = df_sofa.sort_index()
            column_name = ['Home','Home_score','Away','Away_score','Home_wincount']
            df_sofa.drop_duplicates(subset=self.column_name,keep="last",inplace =True)
            df_sofa.to_excel(f"{self.path}/sofascore/sofascore_all.xlsx")
            df_sofascore = df_n[(df_n['Home_score'] == '') & (df_n.index > datetime.now())]
            df_sofascore.drop_duplicates(subset=column_name,keep="last",inplace =True)
        else:
            exit()
        print("*************************** update sofascore successful!! ***************************")
        return df_sofascore
    
    def updat_elo(self,df_before):
        print("*************************** update elo start!! ***************************")
        tf = open(f"{self.path_b}/202201119ELO.json", "r")
        ELO_forst = json.load(tf)
        ELO_all = []
        for i in range(len(df_before)):
            away_team = df_before['Home'][i]
            home_team = df_before['Away'][i]
            y = df_before.index[i]
            if df_before.index[i].year != df_before.index[i-1].year and df_before.index[i].year != 2016:
                for e in ELO_forst:
                    ELO_forst[e] = (ELO_forst[e] * 0.3) +1500
            if ELO_forst[away_team] >= 2400:
                k_a = 16
            elif ELO_forst[away_team] >= 2100:
                k_a = 24
            else:
                k_a = 36
            if ELO_forst[home_team] >= 2400:
                k_h = 16
            elif ELO_forst[home_team] >= 2100:
                k_h = 24
            else:
                k_h = 36
            Ra = ELO_forst[away_team]
            Rb = ELO_forst[home_team]
            Ea = 1 / (1 + 10**((Rb - Ra)/400))
            Eb = 1 / (1 + 10**((Ra - Rb)/400))
            Sa = df_before["win"][i]
            ELO_one = {
                "客隊ELO" : round(ELO_forst[away_team],4),
                "主隊ELO" : round(ELO_forst[home_team],4)
            }
            ELO_all.append(ELO_one)
            if Sa == -1:
                ELO_forst[away_team] +=  (k_a * (1 - Ea))
                ELO_forst[home_team] += -(k_h * (1 - Ea))
            elif Sa == 1:
                ELO_forst[away_team] += -(k_a * (1 - Ea))
                ELO_forst[home_team] +=  (k_h * (1 - Ea))
            elif Sa == 0:
                ELO_forst[away_team] += 0
                ELO_forst[home_team] += 0
            print(f"{df_before.index[i]} {away_team} vs {home_team} 結果為 客隊:{round(ELO_forst[away_team],4)} 主隊:{round(ELO_forst[home_team],4)}")
        tf = open(f"{self.path}/202201119ELO.json", "w")
        json.dump(ELO_forst,tf)
        tf.close()
        print("*************************** update elo successful!! ***************************")
    
    def predict_fifa(self):
        df_sch,df_yesterday = self.schedule()
        df_base_new,df_base_yesterday,df_b_all = self.update_basedata(df_sch,df_yesterday)
        df_all = self.before_basedata(df_sch,df_base_new,df_b_all)
        df_all.index = pd.to_datetime(pd.to_datetime(df_all.index).strftime("%Y-%m-%d"))
        df_odds_b = self.odds_update(df_base_yesterday)
        df_odds = self.odds_update(df_base_new)
        df_base_odds = df_all.merge(df_odds,on=['Date','Eventcode'])
        df_base_odds['Home'] = df_base_odds['Home'].replace(self.changname2)
        df_base_odds['Away'] = df_base_odds['Away'].replace(self.changname2)
        
        df_sofascore = self.update_sofascore()
        column_name = ['Home','Home_score','Away','Away_score']
        df_sofascore.drop_duplicates(subset=column_name,keep="last",inplace =True)
        df_sofascore['Home'] = df_sofascore['Home'].replace(self.changname)
        df_sofascore['Away'] = df_sofascore['Away'].replace(self.changname)
        df_sofascore.index = pd.to_datetime(df_sofascore.index.strftime("%Y-%m-%d"))

        df_final = df_base_odds.merge(df_sofascore,on=['Home','Home_score','Away','Away_score'])
        df_final.index = df_base_odds.index

        df_before = df_base_yesterday.copy()
        df_before['Home'] = df_before['Home'].replace(self.changname2)
        df_before['Away'] = df_before['Away'].replace(self.changname2)
        win = []
        for i in range(len(df_before)):
            home_score = df_before['Home_score'].iloc[i]
            away_score = df_before['Away_score'].iloc[i]
            if home_score > away_score:
                win.append(1)
            elif home_score < away_score:
                win.append(-1)
            else:
                win.append(0)
        df_before['win'] = win
        self.updat_elo(df_before)
        tf = open(f"{self.path}/202201119ELO.json", "r")
        ELO_forst = json.load(tf)
        df_final['主隊ELO'] = df_final['Home'].replace(ELO_forst)
        df_final['客隊ELO'] = df_final['Away'].replace(ELO_forst)
        gamename = joblib.load(r"C:\Users\Guess365User\世足\世足資料\FIFA_changename.model")
        df_final['Game'] = gamename.transform(df_final['Game'])
        df_final_n = df_final[['Game', 'Home_進球數初盤', '進球數初盤', 'Away_進球數初盤', 'Home_進球數終盤', '進球數終盤',
           'Away_進球數終盤', 'Home_角球_inhome', 'Home_半場角球_inhome',
           'Home_黃牌_inhome', 'Home_射門_inhome', 'Home_射正_inhome',
           'Home_進攻_inhome', 'Home_危險進攻_inhome', 'Home_射門不中_inhome',
           'Home_控球率_inhome', 'Home_半場控球率_inhome', 'Home_任意球_inhome',
           'Home_犯規_inhome', 'Home_越位_inhome', 'Home_救球_inhome',
           'Home_角球_inaway', 'Home_半場角球_inaway', 'Home_黃牌_inaway',
           'Home_射門_inaway', 'Home_射正_inaway', 'Home_進攻_inaway',
           'Home_危險進攻_inaway', 'Home_射門不中_inaway', 'Home_控球率_inaway',
           'Home_半場控球率_inaway', 'Home_任意球_inaway', 'Home_犯規_inaway',
           'Home_越位_inaway', 'Home_救球_inaway', 'Home_角球', 'Home_半場角球',
           'Home_黃牌', 'Home_射門', 'Home_射正', 'Home_進攻', 'Home_危險進攻',
           'Home_射門不中', 'Home_控球率', 'Home_半場控球率', 'Home_任意球', 'Home_犯規',
           'Home_越位', 'Home_救球', 'Away_角球_inhome', 'Away_半場角球_inhome',
           'Away_黃牌_inhome', 'Away_射門_inhome', 'Away_射正_inhome',
           'Away_進攻_inhome', 'Away_危險進攻_inhome', 'Away_射門不中_inhome',
           'Away_控球率_inhome', 'Away_半場控球率_inhome', 'Away_任意球_inhome',
           'Away_犯規_inhome', 'Away_越位_inhome', 'Away_救球_inhome',
           'Away_角球_inaway', 'Away_半場角球_inaway', 'Away_黃牌_inaway',
           'Away_射門_inaway', 'Away_射正_inaway', 'Away_進攻_inaway',
           'Away_危險進攻_inaway', 'Away_射門不中_inaway', 'Away_控球率_inaway',
           'Away_半場控球率_inaway', 'Away_任意球_inaway', 'Away_犯規_inaway',
           'Away_越位_inaway', 'Away_救球_inaway', 'Away_角球', 'Away_半場角球',
           'Away_黃牌', 'Away_射門', 'Away_射正', 'Away_進攻', 'Away_危險進攻',
           'Away_射門不中', 'Away_控球率', 'Away_半場控球率', 'Away_任意球', 'Away_犯規',
           'Away_越位', 'Away_救球', 'Home_odd(f)', 'Tie_odd(f)', 'Away_odd(f)',
           'Home_oddrate(f)', 'Tie_oddrate(f)', 'Away_oddrate(f)',
           'Return_rate(f)', 'Home_kelly(f)', 'Tie_kelly(f)', 'Away_kelly(f)',
           'Home_odd(l)', 'Tie_odd(l)', 'Away_odd(l)', 'Home_oddrate(l)',
           'Tie_oddrate(l)', 'Away_oddrate(l)', 'Return_rate(l)', '客隊ELO',
           '主隊ELO', 'Home_wincount', 'Home_winrate', 'Away_wincount',
           'Away_winrate', 'Tie_wincount', 'Tie_winrate', 'Home_進球(近3場)',
           'Away_進球(近3場)', 'Home_失球(近3場)', 'Away_失球(近3場)', 'Home_被射門(近3場)',
           'Away_被射門(近3場)', 'Home_角球(近3場)', 'Away_角球(近3場)', 'Home_黃牌(近3場)',
           'Away_黃牌(近3場)', 'Home_犯規(近3場)', 'Away_犯規(近3場)', 'Home_控球率(近3場)',
           'Away_控球率(近3場)', 'Home_進球(近10場)', 'Away_進球(近10場)', 'Home_失球(近10場)',
           'Away_失球(近10場)', 'Home_被射門(近10場)', 'Away_被射門(近10場)',
           'Home_角球(近10場)', 'Away_角球(近10場)', 'Home_黃牌(近10場)', 'Away_黃牌(近10場)',
           'Home_犯規(近10場)', 'Away_犯規(近10場)', 'Home_控球率(近10場)',
           'Away_控球率(近10場)', 'Home_進球率(15m)', 'Away_進球率(15m)',
           'Home_進球率(30m)', 'Away_進球率(30m)', 'Home_進球率(45m)', 'Away_進球率(45m)',
           'Home_進球率(60m)', 'Away_進球率(60m)', 'Home_進球率(75m)', 'Away_進球率(75m)',
           'Home_進球率(90m)', 'Away_進球率(90m)', 'Home_失球率(15m)', 'Away_失球率(15m)',
           'Home_失球率(30m)', 'Away_失球率(30m)', 'Home_失球率(45m)', 'Away_失球率(45m)',
           'Home_失球率(60m)', 'Away_失球率(60m)', 'Home_失球率(75m)', 'Away_失球率(75m)',
           'Home_失球率(90m)', 'Away_失球率(90m)']]
        scaler = joblib.load( r"C:\Users\Guess365User\世足\世足資料\FIFA_minmax.model")
        x_furture = scaler.transform(df_final_n)
        with open(f'C:\Users\Guess365User\世足\世足資料\FIFA_flaml_85%.pkl', 'rb') as f:
            loaded_classifier = pickle.load(f)

        # predict
        result = loaded_classifier.predict(x_furture)
        pre = loaded_classifier.predict_proba(x_furture)
        df_final['Away'] = df_final['Away'].replace(self.lastname)
        df_final['Home'] = df_final['Home'].replace(self.lastname)
        url = 'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/World Cup 2022/any'
        response = requests.get(url,verify=False,auth=HTTPBasicAuth('rick', '123rick456')).text
        j = json.loads(response)
        json_data = j['response']
        predlist = []
        for i in range(0,len(result)):
            v = df_final["Away"][i]
            h = df_final["Home"][i]
            have_update = False
            for d in range(len(json_data)):
                team_name_v = json_data[d]["AwayTeam"][1]
                team_name_h = json_data[d]["HomeTeam"][1]
                odd = json_data[d]["odds"]
                if team_name_v == v and team_name_h == h:
                    if odd != []:
                        for o in range(len(odd)):
                            if odd[o]["GroupOptionCode"] == "10":
                                if odd[o]["OptionCode"] == '1':
                                    HomeOdds = odd[o]["OptionRate"]
                                elif odd[o]["OptionCode"] == '2':
                                    AwayOdds = odd[o]["OptionRate"]
                                elif odd[o]["OptionCode"] == 'X':
                                    TieOdds = odd[o]["OptionRate"]
                    else:
                        print(v + " v.s " + h + "無賠率" )
                        continue
                if team_name_v == v and team_name_h == h and "_" not in json_data[d]["EventCode"]:
                    have_update = True
                    EventCode = json_data[d]["EventCode"]
            if  have_update== True:
                if result[i] == 1:
                    print(v + " (LOSE) v.s " + h + " (WIN)" )
                    OptionCode = "1"  
                elif result[i]  == -1 :
                    print(v + " (WIN) v.s " + h + " (LOSE)" )
                    OptionCode = "2"
                elif result[i] == 0 :
                    print(v + " (Tie) v.s " + h + " (Tie)" )
                    OptionCode = "X"
                else:
                     print(v + " v.s " + h + "信性度不夠" )
                url = "https://ecocoapidev1.southeastasia.cloudapp.azure.com/PredictMatchEntry/"
                data = {'account':"f108120102",
                 'password':"adsads2323",
                 'GroupOptionCode':10,
                 'OptionCode':OptionCode,
                 'EventCode':EventCode,
                 'predict_type':'Selling',
                 "HomeOdds":float(HomeOdds),
                 "AwayOdds":float(AwayOdds),
                 "TieOdds": float(TieOdds),
                 "HomeConfidence":str(int(round(pre[i][2] * 100,0))) + "%",
                 "AwayConfidence":str(int(round(pre[i][0] * 100,0))) + "%",
                 "TieConfidence" :str(int(round(pre[i][1] * 100,0))) + "%"}
                predlist.append(data)
            else:
                 print(v + " v.s " + h + " 無賽事" )
        vs = pd.DataFrame(data_vs)
        vs.to_excel(f"{self.path}/newmodel_pre.xlsx")
        print(predlist)
        url =f'https://{self.domain_name}/UserMemberSellingPushMessage'
        json_= {"SubscribeLevels":"free",
                "predict_winrate":"58.7%",
                "title":"本季準確度 : ",
                "body_data":"2021賽季回測|39050|852過500|58.7%",
                "TournamentText_icon":"https://i.imgur.com/4YeALVb.jpeg",
                "body_image":"https://i.imgur.com/w4MQwdZ.png",
                "predlist":predlist,
                "connect":False,
                "banner":"FIFA3"}
        response = requests.post(url, json = json_, auth=HTTPBasicAuth('rick', '123rick456'), verify=False).text
        print(response)
        
if __name__ == '__main__':
    FIFAPredict = FIFAPredict()
    FIFAPredict.predict_fifa()

