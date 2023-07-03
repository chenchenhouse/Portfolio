#非同步爬蟲
import nest_asyncio
import asyncio
from pyppeteer import launch,launcher
#html解析
from bs4 import BeautifulSoup
#xml解析
from lxml import etree
from pyquery import PyQuery as pq
#動態爬蟲
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
#時間處理
from datetime import datetime,timedelta,timezone
from time import sleep
#http基本認證
from requests.auth import HTTPBasicAuth

#數據處理
import pandas as pd
#發送http請求
import requests
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

nest_asyncio.apply()
launcher.DEFAULT_ARGS.remove("--enable-automation")

class NBAUpdate(object):
    '''
    groupoptioncode: 20強弱盤
    optioncode:1主 2客
    '''
    def __init__(self):
        self.matchdate = datetime.now() + timedelta(days=0)
        self.today = (self.matchdate + timedelta(days=1)).strftime("%Y%m%d")
        self.path = f'C:/Users/user/NBA預測/20221217/database/{self.today}'
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
        self.path_b = r'C:/Users/user/NBA預測/20221217/database/' + str((self.matchdate).strftime("%Y%m%d"))
        self.domain_name = '776f-220-130-85-186.jp.ngrok.io'
    #賽程爬蟲
    def schedule(self):      
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            start_parm = {
                "executablePath" : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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
            month = filter_[event].get('href')
            url = f"https://www.basketball-reference.com{month}"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            html = await page.content()
            data_one = {
                "html" : html
            }
            data_all.append(data_one)
            print(month + " web crawler successful!!")
            await browser.close()



        if __name__ == '__main__':
            data_all = []
            year = self.matchdate.year 
            month = self.matchdate.month
            if month >= 10:
                season = year + 1
            else:
                season = year
            options = Options()
            options.add_argument('--headless') 
            browser = webdriver.Chrome(options=options)
            browser.get(f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html")
            sleep(1)
            soup = BeautifulSoup(browser.page_source,"lxml")
            filter_ = soup.find("div",{'class':'filter'}).find_all("a")
            browser.close()
            loop = asyncio.get_event_loop()
            count = 1
            for i in range(0,len(filter_),5):
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+5)]
                loop.run_until_complete(asyncio.wait(tasks))
                if (i+5) >= len(filter_):
                    data_html = []
                    for html in range(len(data_all)):
                        html_data = data_all[html]['html']
                        soup = BeautifulSoup(html_data,"lxml")
                        tr = soup.find("table",{"id":"schedule"}).find("tbody").find_all('tr')
                        for t in range(len(tr)):
                            date = tr[t].find("th").text
                            if date not in ['Date','Playoffs']:
                                dateFormatter = "%a, %b %d, %Y %I:%M%p"
                                time = datetime.strptime(tr[t].find("th").text + " " + tr[t].find("td").text + 'm',dateFormatter)
                                if (time.year == 2020 and time.month == 12) or (time.year == 2021 and time.month in (1,2,3,4,5,6,7)):
                                    matchtime  = time + timedelta(hours=13)
                                else:
                                    matchtime  = time + timedelta(hours=12)
                                td = tr[t].find_all("td")
                                away_team = td[1].text
                                away_pts = td[2].text
                                home_team = td[3].text
                                home_pts = td[4].text
                                box = td[5]
                                if box.text != "":
                                    evencode = box.find("a").get("href")
                                else:
                                    evencode = ""
                                ot = td[6].text
                                if ot == '':
                                    ot = 0
                                elif ot == 'OT':
                                    ot = 1
                                else:
                                    ot = int(ot.replace('OT',''))
                                data_one = {
                                    "Matchtime":matchtime,
                                    "Eventcode" : evencode,
                                    "Away":away_team,
                                    "AwayScore":away_pts,
                                    "Home":home_team,
                                    "HomeScore": home_pts,
                                    "OT" : ot,
                                }
                                data_html.append(data_one)
        o_sch = pd.DataFrame(data_html)
        o_sch.index = o_sch["Matchtime"]
        o_sch.drop(["Matchtime"],axis = 1,inplace = True)
        o_sch = o_sch.sort_index()
        o_sch.to_excel(f"{self.path}/sch.xlsx")
        df_b = o_sch[(o_sch.index >  (self.matchdate).strftime("%Y-%m-%d")) & (o_sch.index < (self.matchdate + timedelta(days=1)).strftime("%Y-%m-%d"))]
        df_n = o_sch[(o_sch.index > (self.matchdate + timedelta(days=1)).strftime("%Y-%m-%d")) & (o_sch.index < (self.matchdate + timedelta(days=2)).strftime("%Y-%m-%d"))]
        print('sch is successful!!')
        return df_b,df_n

    #賽事基本資料
    def linepoint(self,df_b): 
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            matchtime = df_b.index[event]
            eventcode = df_b['Eventcode'].iloc[event]
            start_parm = {
                "executablePath" : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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
            url = f"https://www.basketball-reference.com{eventcode}"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            html = await page.content()
            data_one = {
                "Matchtime" : matchtime,
                "Eventcode" : eventcode,
                "html" : html
            }
            data_all.append(data_one)
            print(eventcode + " web crawler successful!!")
            await browser.close()



        if __name__ == '__main__':
            data_all = []
            loop = asyncio.get_event_loop()
            for i in range(0,len(df_b),5):
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+5)]
                loop.run_until_complete(asyncio.wait(tasks))
                if (i+5) >= len(df_b):
                    data_html = []
                    for html in range(len(data_all)):
                        matchtime = data_all[html]['Matchtime']
                        eventcode = data_all[html]['Eventcode']
                        html_data = data_all[html]['html']
                        data_one = {
                            "Matchtime" : matchtime,
                            "Eventcode" : eventcode
                        }
                        soup = BeautifulSoup(html_data, 'lxml')
                        #單節得分
                        tr = soup.find("table",{'id':"line_score"}).find("tbody").find_all('tr')
                        away_team = tr[0].find('th',{"data-stat":"team"}).find("a").text
                        #客
                        away_line1 = tr[0].find("td",{"data-stat":"1"}).text
                        away_line2 = tr[0].find("td",{"data-stat":"2"}).text
                        away_line3 = tr[0].find("td",{"data-stat":"3"}).text
                        away_line4 = tr[0].find("td",{"data-stat":"4"}).text
                        #主
                        home_team = tr[1].find('th',{"data-stat":"team"}).find("a").text
                        home_line1 = tr[1].find("td",{"data-stat":"1"}).text
                        home_line2 = tr[1].find("td",{"data-stat":"2"}).text
                        home_line3 = tr[1].find("td",{"data-stat":"3"}).text
                        home_line4 = tr[1].find("td",{"data-stat":"4"}).text
                        data_linescore = {
                            "Away_Line1" : away_line1,
                            "Away_Line2" : away_line2,
                            "Away_Line3" : away_line3,
                            "Away_Line4" : away_line4,
                            "Home_Line1" : home_line1,
                            "Home_Line2" : home_line2,
                            "Home_Line3" : home_line3,
                            "Home_Line4" : home_line4,
                        }
                        data_one = dict(**data_one,**data_linescore)
                        #4個重要因子
                        tr = soup.find("table",{'id':"four_factors"}).find("tbody").find_all('tr')
                        #客"
                        away_pace = tr[0].find('td',{'data-stat':"pace"}).text
                        away_ft_rate = tr[0].find('td',{'data-stat':"ft_rate"}).text
                        #主
                        home_pace = tr[1].find('td',{'data-stat':"pace"}).text
                        home_ft_rate = tr[1].find('td',{'data-stat':"ft_rate"}).text
                        data_factors = {
                            "Away_Pace" : away_pace,
                            "Away_FTrate" : away_ft_rate,
                            "Home_Pace" : home_pace,
                            "Home_FTrate" : home_ft_rate,
                        }
                        data_one = dict(**data_one,**data_factors)
                        #basic & advanced stats
                        data_basicstat = ['mp','fg','fga','fg_pct','fg3','fg3a','fg3_pct','ft','fta','ft_pct','orb',
                                    'drb','trb','ast','stl','blk','tov','pf','pts','plus_minus']
                        data_basicname = ['MP','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TBR',
                                    'AST','STL','BLK','TOV','PF','PTS','+/-']
                        data_advancedstat = ['ts_pct','efg_pct','fg3a_per_fga_pct','fta_per_fga_pct','orb_pct',
                                            'drb_pct','trb_pct','ast_pct','stl_pct','blk_pct','tov_pct','usg_pct',
                                            'off_rtg','def_rtg','bpm']
                        data_advancedname = ['TS%','eFG%','3PAr','FTr','ORB%','DRB%','TRB%','AST%','STL%','BLK%',
                                            'TOV%','USG%','ORtg','DRtg','BPM']
                        #客
                        #one
                        tr_basicbody = soup.find('table',{'id':f"box-{away_team}-game-basic"}).find('tbody').find_all('tr')[:5]
                        tr_advancedbody = soup.find('table',{'id':f"box-{away_team}-game-advanced"}).find('tbody').find_all('tr')[:5]
                        for t in range(len(tr_basicbody)):
                            starters = tr_basicbody[t].find('th',{'data-stat':"player"}).find("a")
                            starters_name = starters.text
                            starters_eventcode = starters.get("href")
                            data_starter = {
                                f"Away_Starters{t+1}" : starters_name,
                                f"Away_Starters{t+1}_Eventcode" : starters_eventcode
                            }
                            data_one = dict(**data_one,**data_starter)

                            for d in range(len(data_basicstat)):
                                try:
                                    data = tr_basicbody[t].find('td',{'data-stat': data_basicstat[d]}).text
                                except:
                                    data = None
                                data_s = {
                                    f"Away_starters{t+1}_{data_basicname[d]}" : data
                                }
                                data_one = dict(**data_one,**data_s)

                            for d in range(len(data_advancedstat)):
                                try:
                                    data = tr_advancedbody[t].find('td',{'data-stat': data_advancedstat[d]}).text
                                except:
                                    data = None
                                data_s = {
                                    f"Away_starters{t+1}_{data_advancedname[d]}" : data
                                }
                                data_one = dict(**data_one,**data_s)

                        #total
                        tr_basicfoot = soup.find('table',{'id':f"box-{away_team}-game-basic"}).find('tfoot').find('tr') 
                        tr_advancedfoot = soup.find('table',{'id':f"box-{away_team}-game-advanced"}).find('tfoot').find('tr')
                        for d in range(len(data_basicstat)):
                            try:
                                data = tr_basicfoot.find('td',{'data-stat': data_basicstat[d]}).text
                            except:
                                data = None
                            data_t = {
                                f"Away_Total_{data_basicname[d]}" : data
                            }
                            data_one = dict(**data_one,**data_t)
                        for d in range(len(data_advancedstat)):
                            try:
                                data = tr_advancedfoot.find('td',{'data-stat': data_advancedstat[d]}).text
                            except:
                                    data = None
                            data_t = {
                                f"Away_Total_{data_advancedname[d]}" : data
                            }
                            data_one = dict(**data_one,**data_t)

                        #主
                        #one
                        tr_basicbody = soup.find('table',{'id':f"box-{home_team}-game-basic"}).find('tbody').find_all('tr')[:5]
                        tr_advancedbody = soup.find('table',{'id':f"box-{home_team}-game-advanced"}).find('tbody').find_all('tr')[:5]
                        for t in range(len(tr_basicbody)):
                            starters = tr_basicbody[t].find('th',{'data-stat':"player"}).find("a")
                            starters_name = starters.text
                            starters_eventcode = starters.get("href")
                            data_starter = {
                                f"Home_Starters{t+1}" : starters_name,
                                f"Home_Starters{t+1}_Eventcode" : starters_eventcode
                            }
                            data_one = dict(**data_one,**data_starter)

                            for d in range(len(data_basicstat)):
                                try:
                                    data = tr_basicbody[t].find('td',{'data-stat': data_basicstat[d]}).text
                                except:
                                    data = None
                                data_s = {
                                    f"Home_starters{t+1}_{data_basicname[d]}" : data
                                }
                                data_one = dict(**data_one,**data_s)

                            for d in range(len(data_advancedstat)):
                                try:
                                    data = tr_advancedbody[t].find('td',{'data-stat': data_advancedstat[d]}).text
                                except:
                                    data = None
                                data_s = {
                                    f"Home_starters{t+1}_{data_advancedname[d]}" : data
                                }
                                data_one = dict(**data_one,**data_s)

                        #total
                        tr_basicfoot = soup.find('table',{'id':f"box-{home_team}-game-basic"}).find('tfoot').find('tr') 
                        tr_advancedfoot = soup.find('table',{'id':f"box-{home_team}-game-advanced"}).find('tfoot').find('tr')
                        for d in range(len(data_basicstat)):
                            try:
                                data = tr_basicfoot.find('td',{'data-stat': data_basicstat[d]}).text
                            except:
                                data = None
                            data_t = {
                                f"Home_Total_{data_basicname[d]}" : data
                            }
                            data_one = dict(**data_one,**data_t)
                        for d in range(len(data_advancedstat)):
                            try:
                                data = tr_advancedfoot.find('td',{'data-stat': data_advancedstat[d]}).text
                            except:
                                data = None
                            data_t = {
                                f"Home_Total_{data_advancedname[d]}" : data
                            }
                            data_one = dict(**data_one,**data_t)
                        data_html.append(data_one)
                        print(eventcode + " insert data successful!!")
                    df_all = pd.DataFrame(data_html)
                    df_all.index = df_all['Matchtime']
                    df_all = df_all.sort_index()
                    df_all.drop('Matchtime',axis=1,inplace=True)
                    df_all.to_excel(f"{self.path}/boxscore_all.xlsx")
                    df_merge = df_b.merge(df_all,on=['Matchtime','Eventcode'])
                    linepoint = df_merge.drop_duplicates(keep='first')
                    linepoint = linepoint.sort_index()
                    linepoint['Home'] = linepoint['Home'].replace(self.name_n)
                    linepoint['Away'] = linepoint['Away'].replace(self.name_n)
                    linepoint = pd.read_excel(f"{self.path}/boxscore_all.xlsx",index_col='Matchtime')
                    return linepoint
            
    #得分狀況
    def scorechange(self,df_b):      
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            matchtime = df_b.index[event]
            eventcode = df_b['Eventcode'].iloc[event]
            start_parm = {
                "executablePath" : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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
            splitevent = eventcode.split('/')
            url = f"https://www.basketball-reference.com/{splitevent[1]}/pbp/{splitevent[2]}"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            html = await page.content()
            data_one = {
                "Matchtime" : matchtime,
                "Eventcode" : eventcode,
                "html" : html
            }
            data_all.append(data_one)
            print(eventcode + " web crawler successful!!")
            await browser.close()



        if __name__ == '__main__':
            data_all = []
            loop = asyncio.get_event_loop()
            for i in range(0,len(df_b),5):
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+5)]
                loop.run_until_complete(asyncio.wait(tasks))
                if (i+5) >= len(df_b):
                    data_html = []
                    for html in range(len(data_all)):
                        matchtime = data_all[html]['Matchtime']
                        eventcode = data_all[html]['Eventcode']
                        html_data = data_all[html]['html']
                        data_one = {
                            "Matchtime" : matchtime,
                            "Eventcode" : eventcode
                        }
                        soup = BeautifulSoup(html_data, 'lxml')
                        #Ties & Lead Changes
                        tr = soup.find('table',{'id': "st_0"}).find('tbody').find_all('tr')
                        tie = tr[1].find('td').text
                        leadchanges = tr[2].find('td').text
                        gametie = tr[3].find('td').text
                        awayled = tr[4].find('td').text.split(':')
                        awayled_s = (int(awayled[0])*60) + float(awayled[1])
                        homeled = tr[5].find('td').text.split(':')
                        homeled_s = (int(homeled[0])*60) + float(homeled[1])
                        #Most Consecutive Points
                        tr = soup.find('table',{'id': "st_1"}).find('tbody').find_all('tr')
                        away_MCpoints = tr[1].find('td').text
                        home_MCpoints = tr[2].find('td').text
                        #Longest Scoring Drought
                        tr = soup.find('table',{'id': "st_2"}).find('tbody').find_all('tr')
                        away_LSdrought = tr[1].find('td').text.split(':')
                        away_LSdrought_s = (int(away_LSdrought[0])*60) + float(away_LSdrought[1])
                        home_LSdrought = tr[2].find('td').text.split(':')
                        home_LSdrought_s = (int(home_LSdrought[0])*60) + float(home_LSdrought[1])
                        data_summary = {
                            "Ties" : tie,
                            "LeadChanges" : leadchanges,
                            "GameTied" : gametie,
                            "AwayLed" : awayled_s,
                            "HomeLed" : homeled_s,
                            "Away_MCpoints" : away_MCpoints,
                            "Home_MCpoints" : home_MCpoints,
                            "Away_LSdrought" : away_LSdrought_s,
                            "Home_LSdrought" : home_LSdrought_s,
                        }
                        data_one = dict(**data_one,**data_summary)
                        data_html.append(data_one)
                        print(f'{eventcode} is successful!!')
                    df_all = pd.DataFrame(data_html)
                    df_all.index = df_all['Matchtime']
                    df_all = df_all.sort_index()
                    df_all.drop('Matchtime',axis=1,inplace=True)
                    df_merge = df_b.merge(df_all,on=['Matchtime','Eventcode'])
                    scorechange = df_merge.drop_duplicates(keep='first')
                    scorechange['Home'] = scorechange['Home'].replace(self.name_n)
                    scorechange['Away'] = scorechange['Away'].replace(self.name_n)
                    scorechange.to_excel(f"{self.path}/all_game.xlsx")
                    scorechange = pd.read_excel(f"{self.path}/all_game.xlsx",index_col='Matchtime')
                    return scorechange

    #賠率賽程
    def odds_sch(self):
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            start_parm = {
                "executablePath" : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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
            year = self.matchdate.year 
            mon  = self.matchdate.month
            month = [10,11,12,1,2,3,4,5,6]
            m = month[event]
            if mon < 10:
                if m < 10 :
                    y = year
                    url = "https://nba.titan007.com/cn/Normal.aspx?y=" + str(year) +"&m=" +str(m) +"&matchSeason=" + str(year-1) + "-"+ str(year) + "&SclassID=1"
                else:
                    y = year-1
                    url = "https://nba.titan007.com/cn/Normal.aspx?y=" + str(year-1) +"&m=" +str(m) +"&matchSeason=" + str(year-1) + "-"+ str(year) + "&SclassID=1"
            else:

                if m < 10 :
                    y = year+1
                    url = "https://nba.titan007.com/cn/Normal.aspx?y=" + str(year+1) +"&m=" +str(m) +"&matchSeason=" + str(year) + "-"+ str(year+1) + "&SclassID=1"
                else:
                    y = year
                    url = "https://nba.titan007.com/cn/Normal.aspx?y=" + str(year) +"&m=" +str(m) +"&matchSeason=" + str(year) + "-"+ str(year+1) + "&SclassID=1"
            print(url)
            options = {"waitUntil": 'load', "timeout": 0}
            await page.goto(url,options = options )
            html = await page.content()
            data_one = {
                "year": y,
                "month":m,
                "html" : html
            }
            data_all.append(data_one)
            print(str(m) + " web crawler successful!!")
            await browser.close()



        if __name__ == '__main__':
            data_all = []
            loop = asyncio.get_event_loop()
            month = [10,11,12,1,2,3,4,5,6]
            for i in range(0,len(month),5):
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+5)]
                loop.run_until_complete(asyncio.wait(tasks))
                if (i+5) >= len(month):
                    data_html = []
                    for html in range(len(data_all)):
                        year = data_all[html]['year']
                        month = data_all[html]['month']
                        html_data = data_all[html]['html']
                        soup = BeautifulSoup(html_data, 'lxml')
                        if len(soup.find_all("table",{"id":"scheTab"})) > 0:
                            tr = soup.find("table",{"id":"scheTab"}).find("tbody").find_all("tr",{"align":"center"})
                            for t in range(len(tr)):
                                td = tr[t].find_all("td")
                                dateFormatter = "%Y%m-%d %H:%M"
                                matchtime = datetime.strptime(str(year) + td[1].text,dateFormatter)
                                hometeam = td[2].text
                                awayteam = td[4].text
                                if td[5].text != "" or matchtime < ((self.matchdate) + timedelta(days=1)):
                                    try:
                                        score = td[3].find("a").find_all("b")
                                        homescore = score[0].text
                                        awayscore = score[1].text
                                    except:
                                        score = None
                                        homescore = None
                                        awayscore = None
                                    handicap = td[5].text
                                    sumscore = td[6].text
                                    eventcode = td[7].find("a").get("href").split("/")[2]
                                    data_one = {
                                        "Matchtime" : matchtime,
                                        "Eventcode_x" : eventcode,
                                        "Home" : hometeam,
                                        "HomeScore" : homescore,
                                        "Away" : awayteam,
                                        "AwayScore" : awayscore,
                                        "讓分" : handicap,
                                        "總分" : sumscore
                                    }
                                    data_html.append(data_one)
                                    print(f"{matchtime} {eventcode} successful!!")
                    df_all = pd.DataFrame(data_html)
                    df_all.index = df_all['Matchtime']
                    df_all = df_all.sort_index()
                    df_all.drop('Matchtime',axis=1,inplace=True)
                    odds_sch = df_all[df_all.index > (self.matchdate).strftime("%Y-%m-%d")]
                    odds_sch.to_excel(f"{self.path}/odds_sch.xlsx")
                    odds_sch = pd.read_excel(f"{self.path}/odds_sch.xlsx",index_col='Matchtime')
                    return odds_sch
    
    #雙方對戰狀況
    def battlegame(self,odds_sch):
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
                "executablePath" : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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
            url = f"http://nba.titan007.com/analysis/{eventcode}"
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



        if __name__ == '__main__':
            data_all= []
            loop = asyncio.get_event_loop()
            for i in range(0,len(odds_sch),5):
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+5)]
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
                        #主隊
                        tr = soup.find("div",{'id': 'porlet_1'}).find("div",{"id":"e"}).find_all("tr",{'align':"center"})
                        for t in range(0,4):
                            td = tr[t].find_all("td")
                            type_ = td[0].text
                            Home_game = td[1].text
                            Home_win = td[2].text
                            Home_lose = td[3].text
                            Home_win_score = td[4].text
                            Home_lose_score = td[5].text
                            Home_net_score = td[6].text
                            Home_rank = td[7].text.replace("东",'+').replace("西",'-')
                            Home_win_rate = td[8].text.replace("%","")
                            if Home_win_rate == '':
                                Home_win_rate = 0
                            if type_ == '总':
                                  type_name = '' 
                            elif type_ == '主':
                                type_name = '_inhome'
                            elif type_ == '客':
                                type_name = '_inaway'
                            elif type_ == '近6场':
                                type_name = '_insix'
                            data_homerank  = {
                                    f"Away_game{type_name}" : Home_game,
                                    f"Away_win{type_name}" : Home_win,
                                    f"Away_lose{type_name}" : Home_lose,
                                    f"Away_win_score{type_name}" : Home_win_score,
                                    f"Away_lose_score{type_name}" : Home_lose_score,
                                    f"Away_net_score{type_name}" : Home_net_score,
                                    f"Away_rank{type_name}" : Home_rank,
                                    f"Away_win_rate{type_name}" : Home_win_rate
                                }
                            data_one = dict(**data_one,**data_homerank)

                        #客隊
                        tr = soup.find("div",{'id': 'porlet_1'}).find("div",{"id":"f"}).find_all("tr",{'align':"center"})
                        for t in range(0,4):
                            td = tr[t].find_all("td")
                            type_ = td[0].text
                            Away_game = td[1].text
                            Away_win = td[2].text
                            Away_lose = td[3].text
                            Away_win_score = td[4].text
                            Away_lose_score = td[5].text
                            Away_net_score = td[6].text
                            Away_rank = td[7].text.replace("东",'+').replace("西",'-')
                            Away_win_rate = td[8].text.replace("%","")
                            if Away_win_rate == '':
                                Away_win_rate = 0

                            if type_ == '总':
                                  type_name = '' 
                            elif type_ == '主':
                                type_name = '_inhome'
                            elif type_ == '客':
                                type_name = '_inaway'
                            elif type_ == '近6场':
                                type_name = '_insix'

                            data_awayrank  = {
                                    f"Home_game{type_name}" : Away_game,
                                    f"Home_win{type_name}" : Away_win,
                                    f"Home_lose{type_name}" : Away_lose,
                                    f"Home_win_score{type_name}" : Away_win_score,
                                    f"Home_lose_score{type_name}" : Away_lose_score,
                                    f"Home_net_score{type_name}" : Away_net_score,
                                    f"Home_rank{type_name}" : Away_rank,
                                    f"Home_win_rate{type_name}" : Away_win_rate
                                }
                            data_one = dict(**data_one,**data_awayrank)

                        #both battle
                        tr = soup.find("div",{'id': 'porlet_2'}).find("div",{"id":"v"}).find_all("tr",{'align':"center"})[-1]
                        both_battle = tr.find("td").find_all("font")[2].text.replace("%","")
                        data_bothbattle  = {
                                f"Both_battle" : both_battle
                            }
                        data_one = dict(**data_one,**data_bothbattle)

                        #Home battle
                        tr = soup.find("div",{'id': 'porlet_3'}).find("div",{"id":"h"}).find_all("tr",{'align':"center"})[-1]
                        away_battle = tr.find("td").find_all("font")[2].text.replace("%","")
                        data_awaybattle  = {
                                f"Away_battle" : away_battle
                            }
                        data_one = dict(**data_one,**data_awaybattle)

                        #Away battle
                        tr = soup.find("div",{'id': 'porlet_3'}).find("div",{"id":"a"}).find_all("tr",{'align':"center"})[-1]
                        home_battle = tr.find("td").find_all("font")[2].text.replace("%","")
                        data_homebattle  = {
                                f"Home_battle" : home_battle
                            }
                        data_one = dict(**data_one,**data_homebattle)

                        data_html.append(data_one)
                        print(eventcode + " rank data successful!!")
                    df_all = pd.DataFrame(data_html)
                    df_all.index = df_all['Matchtime']
                    df_all = df_all.sort_index()
                    df_all.drop('Matchtime',axis=1,inplace=True)
        o_sch_all = odds_sch.merge(df_all,on=['Matchtime','Eventcode_x'])
        o_sch_all = o_sch_all.drop_duplicates(subset='Eventcode_x',keep='first')
        o_sch_all['Home'] = o_sch_all['Home'].replace(self.name)
        o_sch_all['Away'] = o_sch_all['Away'].replace(self.name)
        o_sch_all.to_excel(f"{self.path}/odds_rank.xlsx")
        o_sch_all = pd.read_excel(f"{self.path}/odds_rank.xlsx",index_col='Matchtime')
        return o_sch_all
    
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
                "executablePath" : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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



        if __name__ == '__main__':
            data_all= []
            loop = asyncio.get_event_loop()
            for i in range(0,len(odds_sch),5):
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+5)]
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
                    df_all.to_excel(f"{self.path}/odds.xlsx")
        odds_all = odds_sch.merge(df_all,on=['Matchtime','Eventcode_x'])
        odds_all['Home'] = odds_all['Home'].replace(self.name)
        odds_all['Away'] = odds_all['Away'].replace(self.name)
        odds_all.to_excel(f"{self.path}/odds_all.xlsx")
        odds_all = pd.read_excel(f"{self.path}/odds_all.xlsx",index_col='Matchtime')
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
                "executablePath" : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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



        if __name__ == '__main__':
            data_all= []
            loop = asyncio.get_event_loop()
            for i in range(0,len(odds_all),5):
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+5)]
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
                    df_all.to_excel(f"{self.path}/odds.xlsx")
        odds_all.drop(['讓分','總分'],axis=1,inplace=True)
        odds_all2 = odds_all.merge(df_all,on=['Matchtime','Eventcode_x'])
        odds_all2['Home'] = odds_all2['Home'].replace(self.name)
        odds_all2['Away'] = odds_all2['Away'].replace(self.name)
        odds_all2.to_excel(f"{self.path}/odds_hand_over.xlsx")
        odds_all2 = pd.read_excel(f"{self.path}/odds_hand_over.xlsx",index_col='Matchtime')
        return odds_all2
    
    def before_data(self,df,o_sch_all,odds_all):
        df_b = pd.read_excel(f"{self.path_b}/beforedata_new.xlsx",index_col='Matchtime')
        df_a= pd.concat([df_b,df])
        df_a = df_a[df_b.columns]
        df_a.to_excel(f"{self.path}/beforedata_new.xlsx")
        col = []
        for i in df_a.columns:
            if 'Home'== i or 'Away' == i or 'Eventcode_y' == i  or 'Line' in i or 'Pace' in i or 'Total' in i  or i == 'OT' or i =='Ties' or i == 'LeadChanges' or i == 'GameTied' or i == 'AwayLed' or i == 'HomeLed' or i == 'Away_MCpoints' or i == 'Home_MCpoints' or i == 'Away_LSdrought' or i == 'Home_LSdrought':
                col.append(i)
        df_s = df_a[col]
        o_sch_all_n = o_sch_all[o_sch_all.index > (self.matchdate)]
        odds_all.index = odds_all['Matchtime']
        odds_all.drop('Matchtime',axis=1,inplace=True)
        odds_all_n = odds_all[odds_all.index > (self.matchdate)]
        print(odds_all_n)
        print(o_sch_all_n)
        #o_sch_all_n.merge(odds_all_n,on=['Matchtime','Eventcode_x','Home','HomeScore','Away','AwayScore','讓分','總分'])
        df_s2 = odds_all_n.merge(o_sch_all_n,on=['Matchtime','Eventcode_x','Home','HomeScore','Away','AwayScore','讓分','總分'])
        df_s2.to_excel(f"{self.path}/odds.xlsx")
        data_all = []
        for i in range(len(o_sch_all_n)):
            matchtime = o_sch_all_n.index[i]
            eventcode = o_sch_all_n['Eventcode_x'].iloc[i]
            data_one = {
                "Matchtime" : matchtime,
                "Eventcode" : eventcode,
            }
            #主隊
            home_team = o_sch_all_n['Home'].iloc[i]
            home_data = df_s[((df_s['Home'] == home_team) | (df_s['Away'] == home_team)) & (df_s.index < o_sch_all_n.index[i])]
            #主in主前10場戰績
            home_data_inhome = home_data[home_data['Home'] == home_team][-10:]
            col = []
            for c in home_data_inhome.columns:
                 if c != 'Home' and "Away_" not in c and ('Home' in c or 'Total' in c or 'OT'== c or 'Ties' == c or c == 'LeadChanges' or c == 'GameTied' or c == 'HomeLed' or c == 'Home_MCpoints' or c == 'Home_LSdrought'):
                    col.append(c)
            home_inhome = home_data_inhome[col]
            home_inhome_sum = home_inhome.sum()
            col = []
            for c in home_inhome_sum.index:
                c = c.replace("Home_","").replace("Home","")
                col.append(c)
            home_inhome_sum.index = col
            home_inhome_len = len(home_inhome)
            print(home_inhome_sum)
            home_inhome_avg = round(home_inhome_sum / home_inhome_len,2)
            col = []
            for c in home_inhome_avg.index:
                columns = "Home_" + c + "_inHome"
                col.append(columns)
            home_inhome_avg.index = col
            data_one = dict(**data_one,**home_inhome_avg)

            #主in客前10場戰績
            home_data_inaway = home_data[home_data['Away'] == home_team][-10:]
            col = []
            for c in home_data_inaway.columns:
                 if c != 'Away' and "Home_" not in c and ('Away' in c or 'Total' in c or 'OT'== c or 'Ties' == c or c == 'LeadChanges' or c == 'GameTied' or c == 'AwayLed' or c == 'Away_MCpoints'  or c == 'Away_LSdrought'):
                    col.append(c)
            home_inaway = home_data_inaway[col]
            home_inaway_sum = home_inaway.sum()
            col = []
            for c in home_inaway_sum.index:
                c = c.replace("Away_","").replace("Away","")
                col.append(c)
            home_inaway_sum.index = col
            home_inaway_len = len(home_inaway)
            home_inaway_avg = round(home_inaway_sum / home_inaway_len,2)
            col = []
            for c in home_inaway_avg.index:
                columns = "Home_" +  c + "_inAway"
                col.append(columns)
            home_inaway_avg.index = col
            data_one = dict(**data_one,**home_inaway_avg)

            #主_total
            home_data_after10 = home_data[-10:]
            home_data_totalinhome = home_data_after10[home_data_after10['Home'] == home_team]
            col = []
            for c in home_data_totalinhome.columns:
                 if c != 'Home' and "Away_" not in c and ('Home' in c or 'Total' in c or 'OT'== c or 'Ties' == c or c == 'LeadChanges' or c == 'GameTied' or c == 'HomeLed' or c == 'Home_MCpoints' or c == 'Home_LSdrought'):
                    col.append(c)
            home_totalinhome = home_data_totalinhome[col]
            home_totalinhome_sum = home_totalinhome.sum()
            col = []
            for c in home_totalinhome_sum.index:
                c = c.replace("Home_","").replace("Home","")
                col.append(c)
            home_totalinhome_sum.index = col
            home_totalinhome_len = len(home_totalinhome)

            home_data_totalinaway = home_data_after10[home_data_after10['Away'] == home_team]
            col = []
            for c in home_data_totalinaway.columns:
                 if c != 'Away' and "Home_" not in c and ('Away' in c or 'Total' in c or 'OT'== c or 'Ties' == c or c == 'LeadChanges' or c == 'GameTied' or c == 'AwayLed' or c == 'Away_MCpoints'  or c == 'Away_LSdrought'):
                    col.append(c)
            home_totalinaway = home_data_totalinaway[col]
            home_totalinaway_sum = home_totalinaway.sum()
            col = []
            for c in home_totalinaway_sum.index:
                c = c.replace("Away_","").replace("Away","")
                col.append(c)
            home_totalinaway_sum.index = col
            home_totalinaway_len = len(home_totalinaway)

            home_total_avg = (home_totalinhome_sum + home_totalinaway_sum) / (home_totalinhome_len + home_totalinaway_len)
            col = []
            for c in home_total_avg.index:
                columns = "Home_" + c + "_Total"
                col.append(columns)
            home_total_avg.index = col
            data_one = dict(**data_one,**home_total_avg)

             #客隊
            away_team = o_sch_all_n['Away'].iloc[i]
            away_data = df_s[((df_s['Home'] == away_team) | (df_s['Away'] == away_team)) & (df_s.index < o_sch_all_n.index[i])]
            #客in主前10場戰績
            away_data_inhome = away_data[away_data['Home'] == away_team][-10:]
            col = []
            for c in away_data_inhome.columns:
                 if c != 'Home' and "Away_" not in c and ('Home' in c or 'Total' in c or 'OT'== c or 'Ties' == c or c == 'LeadChanges' or c == 'GameTied' or c == 'HomeLed' or c == 'Home_MCpoints' or c == 'Home_LSdrought'):
                    col.append(c)
            away_inhome = away_data_inhome[col]
            away_inhome_sum = away_inhome.sum()
            col = []
            for c in away_inhome_sum.index:
                c = c.replace("Home_","").replace("Home","")
                col.append(c)
            away_inhome_sum.index = col
            away_inhome_len = len(away_inhome)
            away_inhome_avg = round(away_inhome_sum / away_inhome_len,2)
            col = []
            for c in away_inhome_avg.index:
                columns = "Away_" + c + "_inHome"
                col.append(columns)
            away_inhome_avg.index = col
            data_one = dict(**data_one,**away_inhome_avg)

            #客in客前10場戰績
            away_data_inaway = away_data[away_data['Away'] == away_team][-10:]
            col = []
            for c in away_data_inaway.columns:
                 if c != 'Away' and "Home_" not in c and 'tarters' not in c and ('Away' in c or 'Total' in c or 'OT'== c or 'Ties' == c or c == 'LeadChanges' or c == 'GameTied' or c == 'AwayLed' or c == 'Away_MCpoints' or c == 'Away_LSdrought'):
                    col.append(c)
            away_inaway = away_data_inaway[col]
            away_inaway_sum = away_inaway.sum()
            col = []
            for c in away_inaway_sum.index:
                c = c.replace("Away_","").replace("Away","")
                col.append(c)
            away_inaway_sum.index = col
            away_inaway_len = len(away_inaway)
            away_inaway_avg = round(away_inaway_sum / away_inaway_len,2)
            col = []
            for c in away_inaway_avg.index:
                columns = "Away_" +  c + "_inAway"
                col.append(columns)
            away_inaway_avg.index = col
            data_one = dict(**data_one,**away_inaway_avg)

            #客_total
            away_data_after10 = away_data[-10:]
            away_data_totalinhome = away_data_after10[away_data_after10['Home'] == away_team]
            col = []
            for c in away_data_totalinhome.columns:
                 if c != 'Home' and "Away_" not in c and ('Home' in c or 'Total' in c or 'OT'== c or 'Ties' == c or c == 'LeadChanges' or c == 'GameTied' or c == 'HomeLed' or c == 'Home_MCpoints' or c == 'Home_LSdrought'):
                    col.append(c)
            away_totalinhome = away_data_totalinhome[col]
            away_totalinhome_sum = away_totalinhome.sum()
            col = []
            for c in away_totalinhome_sum.index:
                c = c.replace("Home_","").replace("Home","")
                col.append(c)
            away_totalinhome_sum.index = col
            away_totalinhome_len = len(away_totalinhome)

            away_data_totalinaway = away_data_after10[away_data_after10['Away'] == away_team]
            col = []
            for c in away_data_totalinaway.columns:
                 if c != 'Away' and "Home_" not in c and ('Away' in c or 'Total' in c or 'OT'== c or 'Ties' == c or c == 'LeadChanges' or c == 'GameTied' or c == 'AwayLed' or c == 'Away_MCpoints'  or c == 'Away_LSdrought'):
                    col.append(c)
            away_totalinaway = away_data_totalinaway[col]
            away_totalinaway_sum = away_totalinaway.sum()
            col = []
            for c in away_totalinaway_sum.index:
                c = c.replace("Away_","").replace("Away","")
                col.append(c)
            away_totalinaway_sum.index = col
            away_totalinaway_len = len(away_totalinaway)

            away_total_avg = (away_totalinhome_sum + away_totalinaway_sum) / (away_totalinhome_len + away_totalinaway_len)
            col = []
            for c in away_total_avg.index:
                columns = "Away_" + c + "_Total"
                col.append(columns)
            away_total_avg.index = col
            data_one = dict(**data_one,**away_total_avg)

            data_all.append(data_one)
            print(f'{matchtime} {eventcode} is successful!!')
        df_all_b = pd.DataFrame(data_all)
        df_all_b.index = df_all_b['Matchtime']
        df_all_b.drop(['Matchtime'],axis= 1,inplace=True)
        df_all_b = df_all_b.dropna()
        df_all_b.to_excel(f"{self.path}/basebefore10.xlsx")
        return df_s2,df_all_b

    #抓取最新賽事預估先發球員
    def Lineups(self):
        res = requests.get('https://www.rotowire.com/basketball/nba-lineups.php')
        soup = BeautifulSoup(res.text,'lxml')
        game = soup.find("main",{"data-sportfull":"basketball"}).find_all("div",{"class":"lineup is-nba"})
        if len(game) == 0:
            game = soup.find("main",{"data-sportfull":"basketball"}).find_all("div",{"class":"lineup is-nba has-started"})
        data_all = []
        for g in range(len(game)):
            time_g = (self.matchdate.strftime("%Y-%m-%d")) + " " + game[g].find("div",{"class":"lineup__meta flex-row"}).find('div').text.replace(" ET","")
            matchtime = (datetime.strptime(time_g, "%Y-%m-%d %I:%M %p") + timedelta(hours = 13))
            away = game[g].find("a",{"class":"lineup__team is-visit"}).find("div").text
            home = game[g].find("a",{"class":"lineup__team is-home"}).find("div").text
            situation_a = game[g].find("ul",{"class":"lineup__list is-visit"}).find_all("li")[0]
            situation_h = game[g].find("ul",{"class":"lineup__list is-home"}).find_all("li")[0]
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
        df_player.to_excel(f"{self.path}/players.xlsx")
        return df_player 
    
    def crawler_player(self,df_player):
        player_list = list()
        for t in ['Away','Home']:
            for i in range(1,6):
                player = list(df_player[f'{t}_Starters{str(i)}'])
                player_list += player
        async def create_page():
            browser = await launch(headless=True)
            page = await browser.newPage()
            return browser,page

        async def close_page(browser):
            await browser.close()

        async def callurl_and_getdata(event):
            name = player_list[event].replace('.','')
            name_rotowire_f = name.split(' ')[0]
            name_rotowire_l = name.split(' ')[1]
            start_parm = {
                "executablePath" : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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
                "name" : player_list[event],
                "html" : html
            }
            data_all.append(data_one)
            #print(html)
            print(name + " web crawler successful!!")
            await browser.close()
        
        if __name__ == '__main__':
            fail_data = []
            data_all = []
            loop = asyncio.get_event_loop()
            for i in range(0,len(player_list),5):
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+5)]
                loop.run_until_complete(asyncio.wait(tasks))
                if (i+5) >= len(player_list):
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
                    player_event = pd.DataFrame(data_html)
                    player_event.index = player_event['ROTOWIRE_name']
                    player_event.drop('ROTOWIRE_name',axis=1,inplace=True)
                    player_event.to_excel(f"{self.path}/playername.xlsx")
                    player_event = pd.read_excel(f"{self.path}/playername.xlsx",index_col='ROTOWIRE_name')
                    return player_event
     
    def change_playername(self,df_player,player_event):
        player_all = []
        for i in range(len(df_player)):
            matchtime = df_player.index[i]
            away = df_player['Away'].iloc[i]
            home = df_player['Home'].iloc[i]
            data_one = {
                "Matchtime" : matchtime,    
                "Away" : away,
                "Home" : home}
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
                "executablePath" : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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



        if __name__ == '__main__':
            loop = asyncio.get_event_loop()
            data_all = []
            for i in range(0,len(player),5):
                tasks = [asyncio.ensure_future(callurl_and_getdata(event)) for event in range(i,i+5)]
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
                        exist = os.path.exists(f"C:/Users/user/NBA預測/20221217/2023/player/play_game/{name}.xlsx")
                        if exist == True:
                            playergame = pd.read_excel(f"C:/Users/user/NBA預測/20221217/database/player/play_game/{name}.xlsx",index_col='RK')
                            df_a= pd.concat([playergame,df_all])
                            df_a = df_a.drop_duplicates(subset=['Eventcode','Date'],keep='first')
                            df_a.to_excel(f"C:/Users/user/NBA預測/20221217/database/player/play_game/{name}.xlsx")
                        else:
                            df_all.to_excel(f"C:/Users/user/NBA預測/20221217/database/player/play_game/{name}.xlsx")
                    data_all = []
    
    def change_playerposition(self,df_player):
        player_list = []
        for p in range(len(df_player)):
            matchtime = df_player.index[p]
            away = df_player['Away'].iloc[p]
            home = df_player['Home'].iloc[p]
            player_data = {'Matchtime' : matchtime,
                              'Away' : away,
                              'Home' : home}
            for t in ['Away','Home']:
                minutes_sort = {'Matchtime' : matchtime}
                for i in range(1,6):
                    player = df_player[f'{t}_Starters{str(i)}'].iloc[p]
                    eventcode = df_player[f'{t}_Starters{str(i)}_Eventcode'].iloc[p]
                    playerdata = pd.read_excel(f"C:/Users/user/NBA預測/20221217/database/player/play_game/{player}.xlsx",index_col='RK')
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
        df_player.to_excel(f"{self.path}/starts.xlsx")
    
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
                df_player = pd.read_excel(f"C:/Users/user/NBA預測/20221217/database/player/play_game/{player_name_h}.xlsx",index_col='Date')
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
                df_player = pd.read_excel(f"C:/Users/user/NBA預測/20221217/database/player/play_game/{player_name_a}.xlsx",index_col='RK')
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
        df_playerb.to_excel(f"{self.path}/basebefore10start.xlsx")
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
        df_3 = pd.read_excel(f"{self.path}/basebefore10start.xlsx",index_col='Matchtime')
        df_2 = df_2.rename(columns={"Eventcode":"Eventcode_x"})
        df_3 = df_3.rename(columns={"Eventcode":"Eventcode_x"})
        df_all1 = df_1.merge(df_2,on=['Matchtime','Eventcode_x'])
        df_all2 = df_all1.merge(df_3,on=['Matchtime','Eventcode_x'])
        df_all2.to_excel(f"{self.path}/df_all1.xlsx")
        return df_all2
    
    #更新最新的elo
    def update_elo(self,df):
        df_b = df[(df.index >  (self.matchdate).strftime("%Y-%m-%d")) & (df.index < (self.matchdate + timedelta(days=1)).strftime("%Y-%m-%d"))]
        df_elo = df_b.copy()
        df_elo['W/L'] = (df_elo['HomeScore'] > df_elo['AwayScore'])*1
        df_elo['Away'] = df_elo['Away'].replace(self.name)
        df_elo['Home'] = df_elo['Home'].replace(self.name)
        tf = open(f"{self.path_b}/ELO_aftre.json", "r")
        ELO_first = json.load(tf)
        ELO_all = []
        for i in range(0,len(df_elo)):
            away_team = df_elo["Away"][i]
            home_team = df_elo["Home"][i]
            df_eventcode = df_elo['Eventcode_x'][i]
            y = df_elo.index[i]
            if str(y) in ['2005-11-02 07:00:00','2006-11-01 08:00:00','2007-10-31 08:00:00','2008-10-29 08:00:00','2009-10-28 07:30:00',
                         '2010-10-27 07:30:00','2011-12-26 00:00:00','2012-10-31 07:00:00','2013-10-30 07:00:00',
                          '2014-10-29 08:00:00','2015-10-28 08:00:00','2016-10-26 07:30:00','2017-10-18 08:01:00',
                         '2018-10-17 08:00:00','2019-10-23 08:00:00','2020-12-23 08:00:00','2021-10-20 07:30:00','2022-10-19 07:30:00']:
                if df_eventcode in ['/boxscores/201410280SAS.html','/boxscores/201510270ATL.html']:
                    pass
                else:
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
            Sa = df_elo["W/L"][i]
            ELO_one = {
                "客隊ELO" : round(ELO_first[away_team],4),
                "主隊ELO" : round(ELO_first[home_team],4)
            }
            ELO_all.append(ELO_one)
            if Sa == 0:
                ELO_first[away_team] +=  (k_a * (1 - Ea))
                ELO_first[home_team] += -(k_h * (1 - Ea))
            elif Sa == 1:
                ELO_first[away_team] += -(k_a * (1 - Ea))
                ELO_first[home_team] +=  (k_h * (1 - Ea))
            print(f"{df_elo.index[i]} {away_team} vs {home_team} 結果為 客隊:{round(ELO_first[away_team],4)} 主隊:{round(ELO_first[home_team],4)}")
        elo_a = pd.DataFrame(ELO_all)
        elo_a.index = df_elo.index
        df_elo["客隊ELO"] = elo_a["客隊ELO"]
        df_elo["主隊ELO"] = elo_a["主隊ELO"]
        df_elo =  df_elo.rename(columns={"Eventcode":"Eventcode_y"})
        df_elo.to_excel(f"{self.path}/elo_n.xlsx")
        return ELO_first,df_elo
        
        
    def elo(self,ELO_first,df_elo,df_all2):
        tf = open(f"{self.path}/ELO_aftre.json", "w")
        json.dump(ELO_first,tf)
        tf.close()
        df_elo1 = df_elo[['Eventcode_y','客隊ELO','主隊ELO']]
        df_elo.index = pd.to_datetime(df_elo.index.strftime("%Y-%m-%d"))
        df_elo = df_elo[['Eventcode_y','客隊ELO','主隊ELO']]
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
    
    def Update_match(self):
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        print('**********賽程爬蟲 爬取開始**********')
        df_b,df_n = self.schedule()
        print('**********賽程爬蟲 爬取結束**********')
        print('**********賽事基本資料 爬取開始**********')
        linepoint = self.linepoint(df_b)
        print('**********賽事基本資料 爬取結束**********')
        print('**********得分狀況 爬取開始**********')
        scorechange = self.scorechange(df_b)
        print('**********得分狀況 爬取結束**********')
        print('**********賠率賽程 爬取開始**********')
        odds_sch = self.odds_sch()
        print('**********雙方對戰狀況 爬取開始**********')
        o_sch_all = self.battlegame(odds_sch)
        print('**********雙方對戰狀況 爬取結束**********')
        print('**********不讓分賠率 爬取開始**********')
        odds_all = self.odds(odds_sch)
        print('**********不讓分賠率抓取 爬取結束**********')
        print('**********讓分與總分 爬取開始**********')
        odds_all = self.check_odds(odds_all)
        print('**********讓分與總分賠率 爬取結束**********')
        print('**********預估先發球員 爬取開始**********')
        df_player = self.Lineups()
        print('**********預估先發球員 爬取結束**********')
        print('**********球員比對 爬取開始**********')
        player_event = self.crawler_player(df_player)
        print('**********球員比對 爬取結束**********')
        print('**********球員名稱 變更開始**********')
        df_player = self.change_playername(df_player,player_event)
        print('**********球員名稱 變更結束**********')
        print('**********球員數據 更新開始**********')
        self.update_player(player_event)
        print('**********球員數據 更新結束**********')
        print('**********球員位置 變更開始**********')
        df_player = self.change_playerposition(df_player)
        print('**********球員位置 變更結束**********')
        df_alldata = scorechange.merge(linepoint,on=['Matchtime','Eventcode'])
        df_alldata = df_alldata.rename(columns={"Eventcode":"Eventcode_y"})
        odds_all = odds_all.reset_index()
        df_m = odds_all.merge(df_alldata,on=['Away','AwayScore','Home','HomeScore'])
        df_m = df_m.drop_duplicates(subset='Eventcode_x',keep='first')
        df_m.index = df_m['Matchtime']
        df_m.drop(['Matchtime'],axis=1,inplace=True)
        df_m.to_excel(f"{self.path}/data_all.xlsx")
        df_m = pd.read_excel(f"{self.path}/data_all.xlsx",index_col='Matchtime')
        df = df_m.merge(o_sch_all,on=['Matchtime','Eventcode_x','Home','HomeScore','Away','AwayScore','讓分','總分'])
        df['GameTied'] = df['GameTied'].apply(lambda x : int(x.split(":")[0])*60 + float(x.split(":")[1]))
        df.to_excel(f"{self.path}/data_all1.xlsx")
        df_s2,df_brfore = self.before_data(df,o_sch_all,odds_all)
        df_player = df_player.drop_duplicates(subset='Away',keep='first')
        odds_all = pd.read_excel(f"{self.path}/odds.xlsx",index_col='Matchtime')
        odd_eventcode = odds_all[['Away','Home','Eventcode_x']]
        df_player['Away'] = df_player['Away'].replace("BKN","BRK").replace("CHA","CHO").replace('PHX','PHO')
        df_player['Home'] = df_player['Home'].replace("BKN","BRK").replace("CHA","CHO").replace('PHX','PHO')
        df_player = odd_eventcode.merge(df_player,on=['Matchtime','Away','Home'])
        odd = df_s2.merge(df_player,on=['Matchtime','Home','Away','Eventcode_x'])
        self.player_before(odd)
        ELO_first,df_elo = self.update_elo(df)
        df_all2 = self.data_merge(odd)
        df_elo2 = self.elo(ELO_first,df_elo,df_all2)
        df_all = df_all2.merge(df_elo2,on=['Matchtime','Eventcode_x'])
        df_all.to_excel(f"{self.path}/predict_data.xlsx")
        col = pd.read_excel(r"C:/Users/user/NBA預測/20221217/predictdata2.xlsx",index_col='Matchtime')
        col.drop(['Eventcode_y','win'],axis=1,inplace=True)
        columns =  col.columns.values
        df_all2 = df_all[columns]
        df_x = df_all2.drop(['Home', 'HomeScore', 'Away', 'AwayScore',"Eventcode_x"],axis = 1)
        df_x.to_excel(f"{self.path}/test.xlsx")
        df_x = pd.read_excel(f"{self.path}/test.xlsx",index_col='Matchtime')
        df_x = df_x.fillna(0)
        mixmin_scaler = joblib.load(r"C:\Users\user\NBA預測\20221217\20230112\nba_flaml_74%_scaler2.model")
        df_x_mm = mixmin_scaler.fit_transform(df_x)
        with open(r'C:\Users\user\NBA預測\20221217\20230112\nba_flaml_74%2.pkl', 'rb') as f:
            clf = pickle.load(f)
        predicted = clf.predict(df_x_mm).flatten() 
        print(predicted)
        pre = []
        pred = clf.predict_proba(df_x_mm)
        for p in pred:
            pre.append(p[1])
        match = (self.matchdate + timedelta(days=1)).strftime("%Y-%m-%d")
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
                        print(v + " v.s " + h + "無賠率" )
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
                    #url = "https://ecocoapidev1.southeastasia.cloudapp.azure.com/PredictMatchEntry/"
                    data = {'account':"winwin666",
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
                        "NewModel_HHomeResult" : homeresult,
                        "NewModel_HHomeConfidence":str(int(round( (pre[i]) * 100,0))) + "%",
                        "NewModel_HAway" : self.xlsx"name2[v],
                        "NewModel_HAwayResult" : awayresult,
                        "NewModel_HAwayConfidence":str(int(round((1-pre[i]) * 100,0))) + "%",
                    }
                    data_vs.append(vs_one)
        vs = pd.DataFrame(data_vs)
        vs.to_excel(f"{self.path}/newmodel_pre.xlsx")
        '''
        url =f'https://{self.dmain_name}/UserMemberSellingPushMessage'
        json_= {"SubscribeLevels":"free/NBA",
                "predict_winrate":"58.7%",
                "title":"本季準確度 : ",
                "body_data":"2021賽季回測|39050|852過500|58.7%",
                "TournamentText_icon":"https://i.imgur.com/4YeALVb.jpeg",
                "body_image":"https://i.imgur.com/w4MQwdZ.png",
                "predlist":predlist,
               "connect":False,
                "banner":"NBA"}
        response = requests.post(url, json = json_, auth=HTTPBasicAuth('rick', '123rick456'), verify=False).text
        print(response)
        print(predlist)
        '''
        
        
if __name__ == '__main__':
    NBAUpdate = NBAUpdate()
    NBAUpdate.Update_match()
