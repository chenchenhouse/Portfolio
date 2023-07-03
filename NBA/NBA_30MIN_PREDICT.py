import nest_asyncio
import asyncio
from bs4 import BeautifulSoup
from pyppeteer import launch,launcher
from datetime import datetime,timedelta,timezone
from requests.auth import HTTPBasicAuth
from time import sleep


import pandas as pd
import pyodbc
import requests
import numpy as np
import asyncio
import logging
import tkinter
import joblib
import json
import pickle
import os

nest_asyncio.apply()
try:
    launcher.DEFAULT_ARGS.remove("--enable-automation")
except:
    pass

class NBAPredictModel(object):
    '''
    groupoptioncode: 20強弱盤
    optioncode:1主 2客
    '''
    def __init__(self):
        self.today = (datetime.now() + timedelta(days=-1))
        self.matchdate = (self.today + timedelta(days=1)).strftime("%Y%m%d")
        self.time = self.today.strftime("%Y%m%d%H%M")
        self.path = f'C:/Users/walt/Database/{self.matchdate}'
        #self.name = pd.read_excel(r"C:\Users\user\NBA預測\20221217\database\playername.xslx",index_col='英全')
        self.name = {
            '波士顿凯尔特人' : "BOS", '金州勇士' : "GSW", '底特律活塞' : "DET", '印第安纳步行者' : "IND", 
            '亚特兰大老鹰' : "ATL", '布鲁克林篮网' : "BRK", '迈阿密热火' : "MIA",'多伦多猛龙' : "TOR", 
            '孟菲斯灰熊' : "MEM", '明尼苏达森林狼' : "MIN", '圣安东尼奥马刺': "SAS", '犹他爵士' : "UTA", 
            '菲尼克斯太阳' : "PHO",'萨克拉门托国王' : "SAC", '费城76人' : "PHI",'洛杉矶湖人' : "LAL", 
            '夏洛特黄蜂' : "CHO", '华盛顿奇才' : "WAS", '纽约尼克斯' : "NYK", '休斯顿火箭' : "HOU",
            '波特兰开拓者' : "POR", '奥兰多魔术' : "ORL", '芝加哥公牛' : "CHI", '密尔沃基雄鹿' : "MIL", 
            '达拉斯独行侠' : "DAL", '丹佛掘金' : "DEN", '克里夫兰骑士' : "CLE",'新奥尔良鹈鹕' : "NOP", 
            '俄克拉荷马城雷霆' : "OKC", '洛杉矶快船' : "LAC"
        }
        self.name_n  = {"Atlanta Hawks":"ATL","Boston Celtics":"BOS","Charlotte Hornets":"CHO","Chicago Bulls":"CHI",
            "Cleveland Cavaliers":"CLE","Dallas Mavericks":"DAL","Denver Nuggets":"DEN","Detroit Pistons":"DET",
            "Golden State Warriors":"GSW","Houston Rockets":"HOU","Indiana Pacers":"IND","Los Angeles Clippers":"LAC",
            "Los Angeles Lakers":"LAL","Memphis Grizzlies":"MEM","Miami Heat":"MIA","Milwaukee Bucks":"MIL",
            "Minnesota Timberwolves":"MIN","Brooklyn Nets":"BRK","New Orleans Pelicans":"NOP","New York Knicks":"NYK",
            "Oklahoma City Thunder":"OKC","Orlando Magic":"ORL","Philadelphia 76ers":"PHI","Phoenix Suns":"PHO",
            "Portland Trail Blazers":"POR","Sacramento Kings":"SAC","San Antonio Spurs":"SAS","Toronto Raptors":"TOR",
            "Utah Jazz":"UTA","Washington Wizards":"WAS","New Orleans Hornets":"NOP","Charlotte Bobcats":"CHO","New Jersey Nets":"BRK"
        }
        self.name2 = {"ATL":"亞特蘭大老鷹","BOS":"波士頓塞爾提克","CHO":"夏洛特黃蜂","CHI":"芝加哥公牛","CLE":"克里夫蘭騎士",
                    "DAL":"達拉斯獨行俠","DEN":"丹佛金塊","DET":"底特律活塞","GSW":"金州勇士","HOU":"休士頓火箭",
                    "IND":"印第安那溜馬","LAC":"洛杉磯快艇","LAL":"洛杉磯湖人","MEM":"曼斐斯灰熊","MIA":"邁阿密熱火",
                    "MIL":"密爾瓦基公鹿","MIN":"明尼蘇達灰狼","BRK":"布魯克林籃網","NOP":"紐奧良鵜鶘","NYK":"紐約尼克",
                    "OKC":"奧克拉荷馬雷霆","ORL":"奧蘭多魔術","PHI":"費城76人","PHO":"鳳凰城太陽","POR":"波特蘭拓荒者",
                    "SAC":"沙加緬度國王","SAS":"聖安東尼奧馬刺","TOR":"多倫多暴龍","UTA":"猶他爵士","WAS":"華盛頓巫師"}
        self.path_b = r'C:/Users/walt/Database/' + str((self.today).strftime("%Y%m%d"))
        self.domain_name = '8da9-220-130-85-186.jp.ngrok.io'


    #賠率抓取
    def odds(self,odds_sch):
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            matchtime = odds_sch.index[event]
            eventcode = odds_sch['Eventcode_x'].iloc[event]
            start_parm = {
                "executablePath" : r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "headless" : True,
                "args" : ['--disable-infobars',
                          '-log-level=30',
                          '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
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
            url = f"http://nba.titan007.com/1x2/oddslist/{eventcode}"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            html = await page.content()
            data_one = {
                "Matchtime" : matchtime,
                "Eventcode_x" : eventcode,
                "html" : html
            }
            data_all.append(data_one)
            print(eventcode + " web crawler successful!!")
            await browser.close()

        data_all= []
        loop = asyncio.get_event_loop()
        for i in range(0,len(odds_sch),5):
            if ((i+5) % len(odds_sch)) < 5:
                mi = 5 - ((i+5) - len(odds_sch))
            else:
                mi = 5
            tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+mi)]
            loop.run_until_complete(asyncio.wait(tasks))
            if (i+5) >= len(odds_sch):
                data_html = []

                for html in range(len(data_all)):
                    matchtime = data_all[html]['Matchtime']
                    eventcode = data_all[html]['Eventcode_x']
                    html_data = data_all[html]['html']
                    data_one = {
                        "Matchtime" : matchtime,
                        "Eventcode_x" : eventcode
                    }
                    soup = BeautifulSoup(html_data,"lxml")
                    avgf = soup.find("tr",{"id":"avgFObj"}).find_all("td")
                    homeodd_f = avgf[1].text
                    awayodd_f = avgf[2].text
                    homerate_f = avgf[3].text
                    awayrate_f = avgf[4].text
                    oddreturn_f = avgf[5].text
                    homekelly_f = avgf[6].text
                    awaykelly_f = avgf[7].text
                    avgr = soup.find("tr",{"id":"avgRObj"}).find_all("td")
                    homeodd_r = avgr[1].text
                    awayodd_r = avgr[2].text
                    homerate_r = avgr[3].text
                    awayrate_r = avgr[4].text
                    oddreturn_r = avgr[5].text
                    data_odd = {
                        "主勝(初)" : homeodd_f,
                        "客勝(初)" : awayodd_f,
                        "主勝率(初)" : homerate_f,
                        "客勝率(初)" : awayrate_f,
                        "凱利指數(初)" : homekelly_f,
                        "凱利指數(終)" : awaykelly_f,
                        "主勝(終)" : homeodd_r,
                        "客勝(終)" : awayodd_r,
                        "主勝率(終)" : homerate_r,
                        "客勝率(終)" : awayrate_r,
                    }
                    data_one = dict(**data_one,**data_odd)
                    data_html.append(data_one)
                    print(eventcode + " odds data successful!!")
                df_all = pd.DataFrame(data_html)
                df_all.index = df_all['Matchtime']
                df_all = df_all.sort_index()
                df_all.drop('Matchtime',axis=1,inplace=True)
                df_all.to_excel(f"{self.path}/{self.time}/odds.xlsx")
        odds_all = odds_sch.merge(df_all,on=['Matchtime','Eventcode_x'])
        odds_all['Home'] = odds_all['Home'].replace(self.name)
        odds_all['Away'] = odds_all['Away'].replace(self.name)
        odds_all.to_excel(f"{self.path}/{self.time}/odds_all.xlsx")
        odds_all = pd.read_excel(f"{self.path}/{self.time}/odds_all.xlsx",index_col='Matchtime')
        return odds_all

    def check_odds(self,odds_all):
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            matchtime = odds_all.index[event]
            eventcode = odds_all['Eventcode_x'].iloc[event]
            start_parm = {
                "executablePath" : r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "headless" : True,
                "args" : ['--disable-infobars',
                          '-log-level=30',
                          '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
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
            #讓分
            url = f"http://nba.titan007.com/odds/AsianOdds_n.aspx?id={eventcode.replace('.htm','')}"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            html = await page.content()
            #總分
            url = f"http://nba.titan007.com/odds//OverDown_n.aspx?id={eventcode.replace('.htm','')}"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            html2 = await page.content()
            data_one = {
                "Matchtime" : matchtime,
                "Eventcode_x" : eventcode,
                "html" : html,
                "html2" : html2
            }
            data_all.append(data_one)
            print(eventcode + " web crawler successful!!")
            await browser.close()

        data_all= []
        loop = asyncio.get_event_loop()
        for i in range(0,len(odds_all),5):
            if ((i+5) % len(odds_all)) < 5:
                mi = 5 - ((i+5) - len(odds_all))
            else:
                mi = 5
            tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+mi)]
            loop.run_until_complete(asyncio.wait(tasks))
            if (i+5) >= len(odds_all):
                data_html = []
                for html in range(len(data_all)):
                    matchtime = data_all[html]['Matchtime']
                    eventcode = data_all[html]['Eventcode_x']
                    html_data = data_all[html]['html']
                    html_data2 = data_all[html]['html2']
                    data_one = {
                        "Matchtime" : matchtime,
                        "Eventcode_x" : eventcode
                    }
                    soup = BeautifulSoup(html_data,"lxml")
                    #讓分
                    tr = soup.find("table",{"id":"odds"}).find("tbody").find_all("tr")
                    have1 = False
                    have2 = False
                    for t in range(len(tr)):
                        if '易*' in tr[t].find("td").text and have1 == False:
                            td = tr[t].find('td',{"id":"td3"}).text.replace("\n",'').replace(" ",'')
                            have1 = True
                        if '36*' in tr[t].find("td").text and have2 == False:
                            td2 = tr[t].find('td',{"id":"td3"}).text.replace("\n",'').replace(" ",'')
                            have2 = True
                    if td != '\xa0':
                        handicap = td
                    else:
                        handicap = td2
                    #總分
                    soup = BeautifulSoup(html_data2,"lxml")

                    tr = soup.find("table",{"id":"odds"}).find("tbody").find_all("tr")
                    have1 = False
                    have2 = False
                    for t in range(len(tr)):
                        if '易*' in tr[t].find("td").text and have1 == False:
                            td = tr[t].find('td',{"id":"td2"}).text.replace("\n",'').replace(" ",'')
                            have1 = True
                        if '36*' in tr[t].find("td").text and have2 == False:
                            td2 = tr[t].find('td',{"id":"td2"}).text.replace("\n",'').replace(" ",'')
                            have2 = True
                    if td != '\xa0':
                        overdown = td
                    else:
                        overdown = td2
                    data_odd = {
                        "讓分" : handicap,
                        "總分" : overdown,
                    }
                    data_one = dict(**data_one,**data_odd)
                    data_html.append(data_one)
                    print(eventcode + " odds data successful!!")
                df_all = pd.DataFrame(data_html)
                df_all.index = df_all['Matchtime']
                df_all = df_all.sort_index()
                df_all.drop('Matchtime',axis=1,inplace=True)
                df_all.to_excel(f"{self.path}/{self.time}/odds.xlsx")
        odds_all.drop(['讓分','總分'],axis=1,inplace=True)
        odds_all2 = odds_all.merge(df_all,on=['Matchtime','Eventcode_x'])
        odds_all2['Home'] = odds_all2['Home'].replace(self.name)
        odds_all2['Away'] = odds_all2['Away'].replace(self.name)
        odds_all2.to_excel(f"{self.path}/{self.time}/odds_hand_over.xlsx")
        odds_all2 = pd.read_excel(f"{self.path}/{self.time}/odds_hand_over.xlsx",index_col='Matchtime')
        return odds_all2

    #抓取最新賽事預估先發球員
    def Lineups(self):
        res = requests.get('https://www.rotowire.com/basketball/nba-lineups.php')
        soup = BeautifulSoup(res.text,'lxml')
        game = soup.find("main",{"data-sportfull":"basketball"}).find_all("div",{"class":"lineup is-nba"})
        if len(game) == 0:
            game = soup.find("main",{"data-sportfull":"basketball"}).find_all("div",{"class":"lineup is-nba has-started"})
        data_all = []
        for g in range(len(game)):
            time_g = (self.today.strftime("%Y-%m-%d")) + " " + game[g].find("div",{"class":"lineup__meta flex-row"}).find('div').text.replace(" ET","")
            matchtime = (datetime.strptime(time_g, "%Y-%m-%d %I:%M %p") + timedelta(hours = 12))
            away = game[g].find("a",{"class":"lineup__team is-visit"}).find("div").text
            home = game[g].find("a",{"class":"lineup__team is-home"}).find("div").text
            situation_a = game[g].find("ul",{"class":"lineup__list is-visit"}).find_all("li")[0].text.replace("\n",'').replace('\r','').replace('            ','')
            situation_h = game[g].find("ul",{"class":"lineup__list is-home"}).find_all("li")[0].text.replace("\n",'').replace('\r','').replace('            ','')
            #if  (matchtime > (datetime.now())) and (matchtime <= (datetime.now() + timedelta(minutes=30))) and (situation_a == 'Confirmed Lineup') and (situation_h == 'Confirmed Lineup'):
            if  (matchtime > (datetime.now())) and (matchtime <= (datetime.now() + timedelta(minutes=30))):
            #if away == 'CHA' and home == 'DAL':
                li = game[g].find("ul",{"class":"lineup__list is-visit"}).find_all("li")[1:6]
                away_pg = li[0].find("a").get("title")
                away_sg = li[1].find("a").get("title")
                away_sf = li[2].find("a").get("title")
                away_pf = li[3].find("a").get("title")
                away_c = li[4].find("a").get("title")

                li = game[g].find("ul",{"class":"lineup__list is-home"}).find_all("li")[1:6]
                home_pg = li[0].find("a").get("title")
                home_sg = li[1].find("a").get("title")
                home_sf = li[2].find("a").get("title")
                home_pf = li[3].find("a").get("title")
                home_c = li[4].find("a").get("title")
                data_one = {
                    "Matchtime" : matchtime,
                    "Away" : away,
                    "Home" : home,
                    'Away_confirmed' : situation_a,
                    'Home_confirmed' : situation_h,
                    "Away_Starters1" : away_pg,
                    "Away_Starters2" : away_sg,
                    "Away_Starters3" : away_sf,
                    "Away_Starters4" : away_pf,
                    "Away_Starters5" : away_c,
                    "Home_Starters1" : home_pg,
                    "Home_Starters2" : home_sg,
                    "Home_Starters3" : home_sf,
                    "Home_Starters4" : home_pf,
                    "Home_Starters5" : home_c,
                }
                data_all.append(data_one)
        df_player = pd.DataFrame(data_all)
        df_player.index = df_player['Matchtime']
        df_player.drop('Matchtime',axis=1,inplace=True)
        df_player.to_excel(f"{self.path}/{self.time}/players.xlsx")
        return df_player 

    def crawler_player(self,df_player):
        df_all_players = pd.read_excel(f"{self.path_b}/player_changename_all.xlsx",index_col='ROTOWIRE_name')
        player_list = list()
        for t in ['Away','Home']:
            for i in range(1,6):
                player = list(df_player[f'{t}_Starters{str(i)}'])
                player_list += player
        player_list_have = list(set(player_list) & set(df_all_players.index))        
        player_list_no = list(set(player_list) - set(df_all_players.index))        

        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            name = player_list_no[event].replace('.','')
            name_rotowire_f = name.split(' ')[0]
            name_rotowire_l = name.split(' ')[1]
            start_parm = {
                "executablePath" : r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "headless" : True,
                "args" : ['--disable-infobars',
                          '-log-level=30',
                          '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
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
            url = f"https://www.basketball-reference.com/search/search.fcgi?search={name}"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            html = await page.content()
            data_one = {
                "name" : player_list_no[event],
                "html" : html
            }
            data_all.append(data_one)
            #print(html)
            print(name + " web crawler successful!!")
            await browser.close()

        fail_data = []
        data_all = []
        loop = asyncio.get_event_loop()
        if len(player_list_no) != 0:
            for i in range(0,len(player_list_no),5):
                if ((i+5) % len(player_list_no)) < 5:
                    mi = 5 - ((i+5) - len(player_list_no))
                else:
                    mi = 5
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+mi)]
                loop.run_until_complete(asyncio.wait(tasks))
                if (i+5) >= len(player_list_no):
                    data_html = []
                    for html in range(len(data_all)):
                        name = data_all[html]['name']
                        html_data = data_all[html]['html']
                        soup = BeautifulSoup(html_data, 'lxml')
                        try:
                            players = soup.find("div",{'id':"players"}).find_all("div",{"class":"search-item"})
                            find = False
                            for p in range(0,len(players)):
                                if find == False: 
                                    list_p = players[p].find("a").text.split(" (")
                                    name_list = list_p[0]
                                    name_f = name_list.split(" ")[0]
                                    name_l = name_list.split(" ")[1]
                                    car = list_p[1].replace(")","").split('-')
                                    if len(car) > 1:
                                        career = car[1]
                                    else:
                                        career = car[0]
                                    if career == '2023':
                                        player_eventcode = players[p].find("div",{"class":"search-item-url"}).text
                                        data_one = {
                                            "ROTOWIRE_name" : name,
                                            "REFERENCE_name" : name_list,
                                            "Player_Eventcode" : player_eventcode
                                        }
                                        data_html.append(data_one)
                                        find = True
                                        print(f"{name} {player_eventcode} successful!!")
                                    else:
                                        fail_data.append(name)
                        except:
                            name_list = soup.find("div",{"id":"meta"}).find("h1").find("span").text
                            player_eventcode = soup.find("link",{"rel":"canonical"}).get("href").split(".com")[1]
                            data_one = {
                                "ROTOWIRE_name" : name,
                                "REFERENCE_name" : name_list,
                                "Player_Eventcode" : player_eventcode
                            }
                            data_html.append(data_one)
                            print(f"{name} {player_eventcode} insert data successful!!")
                    player_event_no = pd.DataFrame(data_html)
                    player_event_no.index = player_event_no['ROTOWIRE_name']
                    player_event_no.drop('ROTOWIRE_name',axis=1,inplace=True)
                    player_event_no.to_excel(f"{self.path}/playername_no.xlsx")
                    df_all_players_n= pd.concat([df_all_players,player_event_no])
                    df_all_players_n = df_all_players_n.drop_duplicates(subset='Player_Eventcode',keep='first')
                    df_all_players_n.to_excel(f"{self.path}/player_changename_all.xlsx")
                else:
                    df_all_players.to_excel(f"{self.path}/player_changename_all.xlsx")
        else:
            player_event_no = pd.DataFrame()
        df_have = []
        for p in range(len(player_list_have)):
            df_playerone = df_all_players[df_all_players.index == player_list_have[p]]
            ROTOWIRE_name = df_playerone.index[0]
            REFERENCE_name = df_playerone['REFERENCE_name'].iloc[0]
            Player_Eventcode = df_playerone['Player_Eventcode'].iloc[0]
            data_one = {
                    "ROTOWIRE_name" : ROTOWIRE_name,
                    "REFERENCE_name" : REFERENCE_name,
                    "Player_Eventcode" : Player_Eventcode
                }
            df_have.append(data_one)
        player_event_have = pd.DataFrame(df_have)
        player_event_have.index = player_event_have['ROTOWIRE_name']
        player_event_have.drop('ROTOWIRE_name',axis=1,inplace=True)
        player_event_have.to_excel(f"{self.path}/{self.time}/playername_have.xlsx")
        player_event = pd.concat([player_event_no,player_event_have])
        player_event.to_excel(f"{self.path}/{self.time}/player_changename.xlsx")
        player_event = pd.read_excel(f"{self.path}/{self.time}/player_changename.xlsx",index_col='ROTOWIRE_name')
        return player_event

    def change_playername(self,df_player,player_event):
        player_all = []
        for i in range(len(df_player)):
            matchtime = df_player.index[i]
            away = df_player['Away'].iloc[i]
            home = df_player['Home'].iloc[i]
            Away_confirmed = df_player['Away_confirmed'].iloc[i]
            Home_confirmed = df_player['Home_confirmed'].iloc[i]
            data_one = {
                "Matchtime" : matchtime,    
                "Away" : away,
                "Home" : home,
                'Away_confirmed' : Away_confirmed,
                'Home_confirmed' : Home_confirmed}
            for t in ['Away','Home']:
                for s in range(1,6):
                    player_n = df_player[f"{t}_Starters{s}"].iloc[i]
                    starts = player_event[player_event.index == player_n]['REFERENCE_name'][0]
                    starts_event = player_event[player_event.index == player_n]['Player_Eventcode'][0]
                    data_start = {
                        f"{t}_Starters{s}":starts,
                        f"{t}_Starters{s}_Eventcode":starts_event
                    }
                    data_one = dict(**data_one,**data_start)
            player_all.append(data_one)
        df_player2 = pd.DataFrame(player_all)
        df_player2.index = df_player2['Matchtime']
        df_player2.drop('Matchtime',axis=1,inplace=True)
        return df_player2

    def update_player(self,player_event):  
        player = list(player_event['Player_Eventcode'])
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            eventcode = player[event]
            start_parm = {
                "executablePath" : r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "headless" : True,
                "args" : ['--disable-infobars',
                          '-log-level=30',
                          '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
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
            playerevent = eventcode.replace('.html',"")
            url = f"https://www.basketball-reference.com{playerevent}/gamelog/2023"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            html = await page.content()
            data_one = {
                "Eventcode" : playerevent + "/gamelog/2023",
                "html" : html
            }
            data_all.append(data_one)
            #print(html)
            print(eventcode + " web crawler successful!!")
            await browser.close()



        loop = asyncio.get_event_loop()
        data_all = []
        for i in range(0,len(player),5):
            if ((i+5) % len(player)) < 5:
                mi = 5 - ((i+5) - len(player))
            else:
                mi = 5
            tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+mi)]
            loop.run_until_complete(asyncio.wait(tasks))
            if ((i+5) >= len(player)):
                for html in range(len(data_all)):
                    data_html = []
                    eventcode = data_all[html]['Eventcode']
                    html_data = data_all[html]['html']
                    soup = BeautifulSoup(html_data, 'lxml')
                    name = soup.find('div',{"id":"info"}).find("h1").find("span").text.split(" 20")[0]
                    try:
                        tr = soup.find('table',{'id':"pgl_basic"}).find("tbody").find_all("tr")
                        basic = "pgl_basic"
                    except:
                        tr = soup.find('table',{'id':"pgl_basic_playoffs"}).find("tbody").find_all("tr")
                        basic = "pgl_basic_playoffs"
                    for t in range(len(tr)):
                        data_one = {
                            "Eventcode" : eventcode
                        }
                        rk = tr[t].find("th").text
                        td = tr[t].find_all("td")
                        if len(td) > 0:
                            Game = td[0].text
                            Date = td[1].text
                            Game_eventcode = td[1].find("a").get("href")
                            Age = td[2].text.split("-")
                            Age_date = round(float(int(Age[0]) + (int(Age[1]) / 365)),2)
                            Team = td[3].text
                            H_or_A = td[4].text
                            Opponent = td[5].text
                            PointDiff = int(td[6].text.split(' (')[1].replace(")",""))
                            if len(Game) == 0:
                                Game_reason = td[-1].text
                                player_data = {
                                    "RK" : rk,
                                    "Game_reason" : Game_reason,
                                    "Date" : Date,
                                    "Game_eventcode" : Game_eventcode,
                                    "Age" : Age_date,
                                    "Team" : Team,
                                    "H/A" : H_or_A,
                                    "Opponent" : Opponent,
                                    "PointDiff" : PointDiff
                                }
                                data_one = dict(**data_one,**player_data)
                            else:
                                Game_reason = 'play'
                                Game_href = td[0].get("data-endpoint")
                                Game_Start = td[7].text
                                Minutes_r = td[8].text.split(":")
                                Minutes = round(float(int(Minutes_r[0]) + (int(Minutes_r[1]) / 60)),2)
                                FG = td[9].text
                                FGA = td[10].text
                                FG_P = round(float(td[11].text.replace("",'0')),2)
                                P3 = td[12].text
                                P3A = td[13].text
                                P3_P  = round(float(td[14].text.replace("",'0')),2)
                                FT = td[15].text
                                FTA = td[16].text
                                FT_P = round(float(td[17].text.replace("",'0')),2)
                                ORB = td[18].text
                                TRB = td[19].text
                                AST = td[20].text
                                STL = td[21].text
                                BLK = td[22].text
                                TOV = td[23].text
                                PF = td[24].text
                                PTS = td[25].text
                                Game_Score = td[26].text
                                Plus_Minus = td[27].text
                                player_data = {
                                    "RK" : rk,
                                    "Game_reason" : Game_reason,
                                    "Game_href" : Game_href,
                                    "Date" : Date,
                                    "Game_eventcode" : Game_eventcode,
                                    "Age" : Age_date,
                                    "Team" : Team,
                                    "H/A" : H_or_A,
                                    "Opponent" : Opponent,
                                    "PointDiff" : PointDiff,
                                    "Game_Start" : Game_Start,
                                    "Minutes" : Minutes,
                                    "FG" : FG,
                                    "FGA" : FGA,
                                    "FG_P" : FG_P,
                                    "P3" : P3,
                                    "P3A" : P3A,
                                    "P3_P" : P3_P,
                                    "FT" : FT,
                                    "FTA" : FTA,
                                    "FT_P" : FT_P,
                                    "ORB" : ORB,
                                    "TRB" : TRB,
                                    "AST" : AST,
                                    "STL" : STL,
                                    "BLK" : BLK,
                                    "TOV" : TOV,
                                    "PF" : PF,
                                    "PTS" : PTS,
                                    "Game_Score" : Game_Score,
                                    "+/-" : Plus_Minus
                                }
                                data_one = dict(**data_one,**player_data)
                            data_html.append(data_one)
                    print(f'{eventcode} is successful!!')
                    df_all = pd.DataFrame(data_html)
                    df_all.index = df_all['RK']
                    df_all.drop('RK',axis=1,inplace=True)
                    df_all = df_all.sort_values(by=['Date'])
                    exist = os.path.exists(f"C:/Users/walt/Database/play_game/{name}.xlsx")
                    if exist == True:
                        playergame = pd.read_excel(f"C:/Users/walt/Database/play_game/{name}.xlsx",index_col='RK')
                        df_a= pd.concat([playergame,df_all])
                        df_a = df_a.drop_duplicates(subset=['Eventcode','Date'],keep='first')
                        df_a.to_excel(f"C:/Users/walt/Database/play_game/{name}.xlsx")
                    else:
                        df_all.to_excel(f"C:/Users/walt/Database/play_game/{name}.xlsx")

    def change_playerposition(self,df_player):
        player_list = []
        for p in range(len(df_player)):
            matchtime = df_player.index[p]
            away = df_player['Away'].iloc[p]
            home = df_player['Home'].iloc[p]
            Away_confirmed = df_player['Away_confirmed'].iloc[p]
            Home_confirmed = df_player['Home_confirmed'].iloc[p]
            player_data = {
                'Matchtime' : matchtime,
                'Away' : away,
                'Home' : home,
                'Away_confirmed' : Away_confirmed,
                'Home_confirmed' : Home_confirmed
            }
            for t in ['Away','Home']:
                minutes_sort = {'Matchtime' : matchtime}
                for i in range(1,6):
                    player = df_player[f'{t}_Starters{str(i)}'].iloc[p]
                    eventcode = df_player[f'{t}_Starters{str(i)}_Eventcode'].iloc[p]
                    playerdata = pd.read_excel(f"C:/Users/walt/Database/play_game/{player}.xlsx",index_col='RK')
                    playerdata = playerdata[playerdata['Date'] < matchtime.strftime("%Y-%m-%d")]
                    minutes = playerdata[playerdata['Game_reason'] == 'play'][-10:]['Minutes'].mean()
                    minutes_data = {
                        f'{t}_Starters{str(i)}_minutes':minutes
                    }
                    minutes_sort = dict(**minutes_sort,**minutes_data)
                minutes_player = pd.DataFrame([minutes_sort])
                minutes_player.index = minutes_player['Matchtime']
                minutes_player.drop(['Matchtime'],axis=1,inplace=True)
                sort_player = minutes_player.T.sort_values(by=matchtime, ascending=False)
                matchtime = sort_player.columns[0]
                minutes_all = {}
                for sort in range(len(sort_player)):
                    player_position = sort_player.index[sort].replace("_minutes",'')
                    player = df_player[player_position].iloc[p]
                    eventcode = df_player[f'{player_position}_Eventcode'].iloc[p]
                    minutes = sort_player[matchtime].iloc[sort]
                    minutes_data = {
                        f'{t}_Starters{str(sort+1)}' : player,
                        f'{t}_Starters{str(sort+1)}_Eventcode' : eventcode,
                        f'{t}_Starters{str(sort+1)}_minutes':minutes
                    }
                    minutes_all = dict(**minutes_all,**minutes_data)

                player_data = dict(**player_data,**minutes_all)
            player_list.append(player_data)
        df_player = pd.DataFrame(player_list)
        df_player.index = df_player['Matchtime']
        df_player.drop('Matchtime',axis=1,inplace=True)
        df_player.to_excel(f"{self.path}/{self.time}/starts.xlsx")
        return df_player
    
    #先發球員過去10場數據平均
    def player_before(self,odd):
        col = []
        for c in odd.columns:
            if 'Starters' in c or 'starters' in c or 'Eventcode_x' == c or c == 'Home' or c == 'Away':
                col.append(c)
        df_s = odd[col]
        data_all = []
        for i in range(len(df_s)):
            matchtime = df_s.index[i]
            eventcode = df_s['Eventcode_x'].iloc[i]
            data_one = {
                "Matchtime" : matchtime,
                "Eventcode" : eventcode,
            }
            #主隊
            home_team = df_s['Home'].iloc[i]
            home_player1 = df_s['Home_Starters1_Eventcode'].iloc[i]
            home_player1_name = df_s['Home_Starters1'].iloc[i]
            home_player2 = df_s['Home_Starters2_Eventcode'].iloc[i]
            home_player2_name = df_s['Home_Starters2'].iloc[i]
            home_player3 = df_s['Home_Starters3_Eventcode'].iloc[i]
            home_player3_name = df_s['Home_Starters3'].iloc[i]
            home_player4 = df_s['Home_Starters4_Eventcode'].iloc[i]
            home_player4_name = df_s['Home_Starters4'].iloc[i]
            home_player5 = df_s['Home_Starters5_Eventcode'].iloc[i]
            home_player5_name = df_s['Home_Starters5'].iloc[i]


            for player_name_h,count in zip([home_player1_name,home_player2_name,home_player3_name,home_player4_name,home_player5_name],range(1,6)):
                df_player = pd.read_excel(f"C:/Users/walt/Database/play_game/{player_name_h}.xlsx",index_col='Date')
                df_player.index = pd.to_datetime(df_player.index)
                #有上場
                df_match_h = df_player[(df_player.index < matchtime) & (df_player['Game_reason'] == 'play')][-10:]
                df_match_h = df_match_h[['PointDiff', 'Game_Start','Minutes', 'FG', 'FGA', 'FG_P', 'P3', 'P3A', 'P3_P', 'FT', 'FTA',
                                           'FT_P', 'ORB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS','Game_Score', '+/-']]
                df_match_h_sum = df_match_h.sum()
                df_match_h_len = len(df_match_h)
                df_match_h_avg = round(df_match_h_sum / df_match_h_len,2)
                col = []
                for c in df_match_h_avg.index:
                    column = 'Home_starters' + str(count) + "_" + c
                    col.append(column)
                df_match_h_avg.index = col
                data_one = dict(**data_one,**df_match_h_avg)

                #沒上場
                df_match_h = df_player[(df_player.index < matchtime) & (df_player['Game_reason'] != 'play')][-10:]
                df_match_h = df_match_h[['PointDiff']]
                df_match_h_sum = df_match_h.sum()
                df_match_h_len = len(df_match_h)
                df_match_h_avg = round(df_match_h_sum / df_match_h_len,2)
                col = []
                for c in df_match_h_avg.index:
                    column = 'Home_starters' + str(count) + "_noplay_" + c
                    col.append(column)
                df_match_h_avg.index = col
                data_one = dict(**data_one,**df_match_h_avg)
            #客隊
            away_team = df_s['Away'].iloc[i]
            away_player1 = df_s['Away_Starters1_Eventcode'].iloc[i]
            away_player1_name = df_s['Away_Starters1'].iloc[i]
            away_player2 = df_s['Away_Starters2_Eventcode'].iloc[i]
            away_player2_name = df_s['Away_Starters2'].iloc[i]
            away_player3 = df_s['Away_Starters3_Eventcode'].iloc[i]
            away_player3_name = df_s['Away_Starters3'].iloc[i]
            away_player4 = df_s['Away_Starters4_Eventcode'].iloc[i]
            away_player4_name = df_s['Away_Starters4'].iloc[i]
            away_player5 = df_s['Away_Starters5_Eventcode'].iloc[i]
            away_player5_name = df_s['Away_Starters5'].iloc[i]


            for player_name_a,count in zip([away_player1_name,away_player2_name,away_player3_name,away_player4_name,away_player5_name],range(1,6)):
                df_player = pd.read_excel(f"C:/Users/walt/Database/play_game/{player_name_a}.xlsx",index_col='RK')
                df_player.index = pd.to_datetime(df_player.index)
                #有上場
                df_match_a = df_player[(df_player.index < matchtime) & (df_player['Game_reason'] == 'play')][-10:]
                df_match_a = df_match_a[['PointDiff', 'Game_Start','Minutes', 'FG', 'FGA', 'FG_P', 'P3', 'P3A', 'P3_P', 'FT', 'FTA',
                                           'FT_P', 'ORB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS','Game_Score', '+/-']]
                df_match_a_sum = df_match_a.sum()
                df_match_a_len = len(df_match_a)
                df_match_a_avg = round(df_match_a_sum / df_match_a_len,2)
                col = []
                for c in df_match_a_avg.index:
                    column = 'Away_starters' + str(count) + "_" + c
                    col.append(column)
                df_match_a_avg.index = col
                data_one = dict(**data_one,**df_match_a_avg)

                #沒上場
                df_match_a = df_player[(df_player.index < matchtime) & (df_player['Game_reason'] != 'play')][-10:]
                df_match_a = df_match_a[['PointDiff']]
                df_match_a_sum = df_match_a.sum()
                df_match_a_len = len(df_match_a)
                df_match_a_avg = round(df_match_a_sum / df_match_a_len,2)
                col = []
                for c in df_match_a_avg.index:
                    column = 'Away_starters' + str(count) + "_noplay_" + c
                    col.append(column)
                df_match_a_avg.index = col
                data_one = dict(**data_one,**df_match_a_avg)
            data_all.append(data_one)
            print(f'{matchtime} {eventcode} is successful!!')
        df_playerb = pd.DataFrame(data_all)
        df_playerb.index = df_playerb['Matchtime']
        df_playerb.drop(['Matchtime'],axis= 1,inplace=True)
        df_playerb.to_excel(f"{self.path}/{self.time}/basebefore10start.xlsx")
        return df_playerb

    def data_merge(self,odd):
        df_1 = odd[['Home', 'HomeScore', 'Away', 'AwayScore', '讓分', '總分',
                   'Eventcode_x', '主勝(初)', '客勝(初)', '主勝率(初)', '客勝率(初)', '凱利指數(初)',
                   '凱利指數(終)', '主勝(終)', '客勝(終)', '主勝率(終)', '客勝率(終)', 'Away_game',
                   'Away_win', 'Away_lose', 'Away_win_score', 'Away_lose_score',
                   'Away_net_score', 'Away_rank', 'Away_win_rate', 'Away_game_inhome',
                   'Away_win_inhome', 'Away_lose_inhome', 'Away_win_score_inhome',
                   'Away_lose_score_inhome', 'Away_net_score_inhome',
                   'Away_rank_inhome', 'Away_win_rate_inhome', 'Away_game_inaway',
                   'Away_win_inaway', 'Away_lose_inaway', 'Away_win_score_inaway',
                   'Away_lose_score_inaway', 'Away_net_score_inaway',
                   'Away_rank_inaway', 'Away_win_rate_inaway', 'Away_game_insix',
                   'Away_win_insix', 'Away_lose_insix', 'Away_win_score_insix',
                   'Away_lose_score_insix', 'Away_net_score_insix',
                   'Away_win_rate_insix', 'Home_game', 'Home_win', 'Home_lose',
                   'Home_win_score', 'Home_lose_score', 'Home_net_score', 'Home_rank',
                   'Home_win_rate', 'Home_game_inhome', 'Home_win_inhome',
                   'Home_lose_inhome', 'Home_win_score_inhome',
                   'Home_lose_score_inhome', 'Home_net_score_inhome',
                   'Home_rank_inhome', 'Home_win_rate_inhome', 'Home_game_inaway',
                   'Home_win_inaway', 'Home_lose_inaway', 'Home_win_score_inaway',
                   'Home_lose_score_inaway', 'Home_net_score_inaway',
                   'Home_rank_inaway', 'Home_win_rate_inaway', 'Home_game_insix',
                   'Home_win_insix', 'Home_lose_insix', 'Home_win_score_insix',
                   'Home_lose_score_insix', 'Home_net_score_insix',
                   'Home_win_rate_insix', 'Both_battle', 'Away_battle', 'Home_battle']]
        df_2 = pd.read_excel(f"{self.path}/basebefore10.xlsx",index_col='Matchtime')
        df_3 = pd.read_excel(f"{self.path}/{self.time}/basebefore10start.xlsx",index_col='Matchtime')
        df_2 = df_2.rename(columns={"Eventcode":"Eventcode_x"})
        df_3 = df_3.rename(columns={"Eventcode":"Eventcode_x"})
        df_all1 = df_1.merge(df_2,on=['Matchtime','Eventcode_x'])
        df_all2 = df_all1.merge(df_3,on=['Matchtime','Eventcode_x'])
        df_all2.to_excel(f"{self.path}/{self.time}/df_all1.xlsx")
        return df_all2

    def elo(self,df_all2):
            tf = open(f"{self.path}/ELO_aftre.json", "r")
            ELO_first = json.load(tf)
            df_elo = pd.read_excel(f"{self.path}/elo_n.xlsx",index_col='Matchtime')
            #df_elo1 = df_elo[['Eventcode_y','客隊ELO','主隊ELO']]
            df_elo.index = pd.to_datetime(df_elo.index.strftime("%Y-%m-%d"))
            #df_elo = df_elo[['Eventcode_y','客隊ELO','主隊ELO']]
            df_all2.index = pd.to_datetime(df_all2.index.strftime("%Y-%m-%d"))
            elo = []
            for e in range(len(df_all2)):
                eventcode = df_all2['Eventcode_x'][e]
                homeelo = ELO_first[df_all2['Home'][e]]
                awayelo = ELO_first[df_all2['Away'][e]]
                data_one = {
                    "Eventcode_x" : eventcode,
                    "主隊ELO" : homeelo,
                    "客隊ELO" : awayelo
                }
                elo.append(data_one)
            df_elo2 = pd.DataFrame(elo)
            df_elo2.index = df_all2.index
            return df_elo2
    
    def updatedb_starters(self,df_player):
        _server_gamania = 'ecoco-analysis.database.windows.net'  # No TCP
        _database_gamania = 'Analysis' 
        _uid_gamania = 'crawl'
        _pwd_gamania = '@Guess365123!'
        _port = "1433"
        conn_Guess365 = pyodbc.connect('DRIVER={SQL Server};SERVER='+_server_gamania+';Port='+_port+';DATABASE='+_database_gamania+';UID='+_uid_gamania+';PWD='+_pwd_gamania)  # for MSSQL
        cursor = conn_Guess365.cursor()

        df_d = pd.read_excel(f'{self.path}/{self.time}/odds_hand_over.xlsx',index_col = 'Matchtime')[['Home','Away','Eventcode_x']]
        df_o = df_player.copy()
        
        df_o['Away'] = df_o['Away'].replace("PHX",'PHO').replace("BKN",'BRK').replace("CHA",'CHO')
        df_o['Home'] = df_o['Home'].replace("PHX",'PHO').replace("BKN",'BRK').replace("CHA",'CHO')
        df_one = df_d.merge(df_o,on=['Matchtime','Away','Home'])
        #df_one.index = df_one['Matchtime']
        #df_one.drop('Matchtime',axis=1,inplace=True)
        for d in range(len(df_one)):
            Matchtime = df_one.index[d]
            Eventcode = df_one['Eventcode_x'].iloc[d].replace('.htm','')
            Away_confirmed = df_one['Away_confirmed'].iloc[d]
            Home_confirmed = df_one['Away_confirmed'].iloc[d]
            Away = df_one['Away'].iloc[d].replace("PHX",'PHO').replace("BKN",'BRK').replace("CHA",'CHO')
            Home = df_one['Home'].iloc[d].replace("PHX",'PHO').replace("BKN",'BRK').replace("CHA",'CHO')
            Away_Starters1_p = df_one['Away_Starters1'].iloc[d].replace("'",'"')
            Away_Starters2_p = df_one['Away_Starters2'].iloc[d].replace("'",'"')
            Away_Starters3_p = df_one['Away_Starters3'].iloc[d].replace("'",'"')
            Away_Starters4_p = df_one['Away_Starters4'].iloc[d].replace("'",'"')
            Away_Starters5_p = df_one['Away_Starters5'].iloc[d].replace("'",'"')

            Home_Starters1_p = df_one['Home_Starters1'].iloc[d].replace("'",'"')
            Home_Starters2_p = df_one['Home_Starters2'].iloc[d].replace("'",'"')
            Home_Starters3_p = df_one['Home_Starters3'].iloc[d].replace("'",'"')
            Home_Starters4_p = df_one['Home_Starters4'].iloc[d].replace("'",'"')
            Home_Starters5_p = df_one['Home_Starters5'].iloc[d].replace("'",'"')
            if (Away_confirmed == 'Confirmed Lineup') & (Home_confirmed == 'Confirmed Lineup'):
                confirmed = 'Y'
            else:
                confirmed = 'N'
            Insert_SQL = """
                    INSERT INTO NBA_Starters values ('{}','{}','{}','{}','30min','{}','{}','{}','{}','{}','{}',
                    '{}','{}','{}','{}','{}')
            """.format(Matchtime,Eventcode,Home,Away,confirmed,
                    Home_Starters1_p,Home_Starters2_p,Home_Starters3_p,Home_Starters4_p,Home_Starters5_p,
                    Away_Starters1_p,Away_Starters2_p,Away_Starters3_p,Away_Starters4_p,Away_Starters5_p)
            cursor = conn_Guess365.cursor()
            cursor.execute(Insert_SQL)
            cursor.commit()


    def NBA_predict(self):
        if not os.path.isdir(f'{self.path}/{self.time}'):
            os.mkdir(f'{self.path}/{self.time}')
        odds_sch = pd.read_excel(f"{self.path}/odds_sch.xlsx",index_col='Matchtime')
        o_sch_all = pd.read_excel(f"{self.path}/odds_rank.xlsx",index_col='Matchtime')
        print('**********crawler odds start**********')
        odds_all = self.odds(odds_sch)
        print('**********crawler odds end**********')
        print('**********crawler handicap & sum odds start**********')
        odds_all = self.check_odds(odds_all)
        print('**********crawler handicap & sum odds end**********')
        print('**********crawler forcast starts players start**********')
        df_player = self.Lineups()
        print('**********crawler forcast starts players end**********')
        print('**********check players start**********')
        player_event = self.crawler_player(df_player)
        print('**********check players end**********')
        print('**********change players name start**********')
        df_player = self.change_playername(df_player,player_event)
        print('**********change players name end**********')
        print('**********update starts data start**********')
        self.update_player(player_event)
        print('**********update starts data end**********')
        print('**********change players position start**********')
        df_player = self.change_playerposition(df_player)
        print('**********change players position end**********')
        self.updatedb_starters(df_player)
        df_player = df_player[(df_player['Away_confirmed'] == 'Confirmed Lineup') & (df_player['Home_confirmed'] == 'Confirmed Lineup')]
        df = pd.read_excel(f"{self.path}/data_all1.xlsx",index_col='Matchtime')
        df_brfore = pd.read_excel(f"{self.path}/basebefore10.xlsx",index_col='Matchtime')
        df_player = df_player.drop_duplicates(subset='Away',keep='first')
        odd_b = pd.read_excel(f"{self.path}//odds.xlsx",index_col='Matchtime')
        odds_all = pd.read_excel(f"{self.path}/{self.time}/odds_hand_over.xlsx",index_col='Matchtime')
        odd_b.drop(['讓分','總分','主勝(初)','客勝(初)','主勝率(初)','客勝率(初)','凱利指數(初)',
                      '凱利指數(初)','凱利指數(終)','主勝(終)','客勝(終)','主勝率(終)','客勝率(終)'],axis=1,inplace=True)
        odds_all = odd_b.merge(odds_all,on=['Matchtime','Away','AwayScore','Home','HomeScore','Eventcode_x'])
        odds_all.to_excel(f"{self.path}/{self.time}/odd_all2.xlsx")
        odd_eventcode = odds_all[['Away','Home','Eventcode_x']]
        df_player['Away'] = df_player['Away'].replace("BKN","BRK").replace("CHA","CHO").replace('PHX','PHO')
        df_player['Home'] = df_player['Home'].replace("BKN","BRK").replace("CHA","CHO").replace('PHX','PHO')
        df_player = odd_eventcode.merge(df_player,on=['Matchtime','Away','Home'])
        odds_all.drop('Eventcode_x',axis = 1,inplace=True)
        odd = odds_all.merge(df_player,on=['Matchtime','Home','Away'])
        self.player_before(odd)
        df_all2 = self.data_merge(odd)
        df_elo2 = self.elo(df_all2)
        df_all = df_all2.merge(df_elo2,on=['Matchtime','Eventcode_x'])
        col = []
        col2 = []
        for c in df_all.columns:
            if '_+/-' in c:
                if 'Home' in c:
                    col.append(c)
                elif 'Away' in c:
                    col2.append(c)
        h_updown = []
        a_updown = []
        for i in range(len(df_all)):
            home_updown = df_all[col].iloc[i].mean()
            h_updown.append(home_updown)
            away_updown = df_all[col2].iloc[i].mean()
            a_updown.append(away_updown)
        df_all['Home_startersAll_+/-'] = h_updown
        df_all['Away_startersAll_+/-'] = a_updown
        df_all.to_excel(f"{self.path}/{self.time}/predict_data.xlsx")
        col = pd.read_excel(r"C:/Users/walt/Database/20230316predict_col.xlsx",index_col='Matchtime')
        col.drop(['Eventcode_y','win'],axis=1,inplace=True)
        columns =  col.columns.values
        df_all2 = df_all[columns]
        df_x = df_all2.drop(['Home', 'HomeScore', 'Away', 'AwayScore',"Eventcode_x"],axis = 1)
        df_x.to_excel(f"{self.path}/{self.time}/test.xlsx")
        df_x = pd.read_excel(f"{self.path}/{self.time}/test.xlsx",index_col='Matchtime')
        df_x = df_x.fillna(0)
        mixmin_scaler = joblib.load(r"C:/Users/walt/Database/nba_flaml_73%_scaler20230316.model")
        df_x_mm = mixmin_scaler.transform(df_x)
        with open(r'C:/Users/walt/Database\nba_flaml_73%20230316.pkl', 'rb') as f:
            clf = pickle.load(f)
        predicted = clf.predict(df_x_mm).flatten() 
        print(predicted)
        pre = []
        pred = clf.predict_proba(df_x_mm)
        for p in pred:
            pre.append(p[1])
        match = (self.today +timedelta(days=1)).strftime("%Y-%m-%d")
        predlist = []
        data_vs = []
        for i in range(0,len(pre)):
            v = df_all2["Away"][i]
            h = df_all2["Home"][i]
            url = 'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/NBA/any'
            response = requests.get(url,verify=False,auth=HTTPBasicAuth('rick', '123rick456')).text
            j = json.loads(response)
            json_data = j['response']
            have_update = False
            for d in range(len(json_data)):
                team_name_v = json_data[d]["AwayTeam"][1]
                team_name_h = json_data[d]["HomeTeam"][1]
                odd = json_data[d]['odds']
                if team_name_v == self.name2[v] and team_name_h == self.name2[h]:
                    if odd != []:
                        for o in range(len(odd)):
                            if odd[o]["GroupOptionCode"] == "20":
                                if odd[o]["OptionCode"] == '1':
                                    HomeOdds = odd[o]["OptionRate"]
                                elif odd[o]["OptionCode"] == '2':
                                    AwayOdds = odd[o]["OptionRate"]
                    else:
                        print(v + " v.s " + h + " no odds data" )
                        continue
                if team_name_v == self.name2[v] and team_name_h == self.name2[h] and "_" not in json_data[d]["EventCode"] and json_data[d]["MatchTime"].split(" ")[0] == match:
                    have_update = True
                    EventCode = json_data[d]["EventCode"]
                    if pre[i]  > 0.5:
                        homeresult = 'WIN'
                        awayresult = 'LOSE'
                        print(self.name2[v] + " (LOSE) v.s " + self.name2[h] + " (WIN)" )
                        OptionCode = "1"   
                    else:
                        homeresult = 'LOSE'
                        awayresult = 'WIN'
                        print(self.name2[v] + " (WIN) v.s " + self.name2[h] + " (LOSE)" )
                        OptionCode = "2"
                    if (int(round( (1 - pre[i]) * 100,0)) >= 85) or (int(round((pre[i]) * 100,0)) >= 85):
                        main = '1'
                    else:
                        main = '0'

                    if ((pre[i] > 0.5) & (float(HomeOdds) > 1.28)) or ((pre[i] < 0.5) & (float(AwayOdds) > 1.28)): 
                        #url = "https://ecocoapidev1.southeastasia.cloudapp.azure.com/PredictMatchEntry/"
                        data = {'account':"i945win",
                        'password':"adsads2323",
                        'GroupOptionCode':20,
                        'OptionCode':int(OptionCode),
                        'EventCode':EventCode,
                        'predict_type':'Selling',
                        "HomeOdds":float(HomeOdds),
                        "AwayOdds":float(AwayOdds),
                        "HomeConfidence":str(int(round( (pre[i]) * 100,0))) + "%",
                        "AwayConfidence":str(int(round((1-pre[i]) * 100,0))) + "%",
                        "main" : main}
                        predlist.append(data)
                        print(data)
                    vs_one = {
                        "NewModel_Home" : self.name2[h],
                        "NewModel_HomeResult" : homeresult,
                        "NewModel_HomeConfidence":str(int(round( (pre[i]) * 100,0))) + "%",
                        "NewModel_Away" : self.name2[v],
                        "NewModel_AwayResult" : awayresult,
                        "NewModel_AwayConfidence":str(int(round((1-pre[i]) * 100,0))) + "%",
                    }
                    data_vs.append(vs_one)
                    vs = pd.DataFrame(data_vs)
                    vs.to_excel(f"{self.path}/{self.time}/newmodel_pre.xlsx")
        url =f'https://{self.domain_name}/UserMemberSellingPushMessage'
        json_= {"SubscribeLevels":"VIP",
                "predict_winrate":"58.7%",
                "title":"本季準確度 : ",
                "body_data":"2021賽季回測|39050|852過500|58.7%",
                "TournamentText_icon":"https://i.imgur.com/4YeALVb.jpeg",
                "body_image":"https://i.imgur.com/w4MQwdZ.png",
                "predlist":predlist,
                "connect":False,
                "banner":"NBA",
                "check":False}
        response = requests.post(url, json = json_, auth=HTTPBasicAuth('rick', '123rick456'), verify=False).text
        print(response)
        print(predlist)
        
        


if __name__ == '__main__':
    NBAPredict = NBAPredictModel()
    NBAPredict.NBA_predict()

