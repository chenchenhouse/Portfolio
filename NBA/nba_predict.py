import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import numpy as np
import datetime
from time import sleep
from keras.models import load_model
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from keras.models import load_model
import requests
import json
from requests.auth import HTTPBasicAuth
import warnings

warnings.filterwarnings("ignore")

class NBAPredict(object):
    '''
    groupoptioncode: 20強弱盤
    optioncode:1主 2客
    '''
    def __init__(self):
        self.name = {"ATL":"亞特蘭大老鷹","BOS":"波士頓塞爾提克","CHO":"夏洛特黃蜂","CHI":"芝加哥公牛","CLE":"克里夫蘭騎士",
            "DAL":"達拉斯獨行俠","DEN":"丹佛金塊","DET":"底特律活塞","GSW":"金州勇士","HOU":"休士頓火箭",
            "IND":"印第安納溜馬","LAC":"洛杉磯快艇","LAL":"洛杉磯湖人","MEM":"曼斐斯灰熊","MIA":"邁阿密熱火",
            "MIL":"密爾瓦基公鹿","MIN":"明尼蘇達灰狼","BRK":"布魯克林籃網","NOP":"紐奧良鵜鶘","NYK":"紐約尼克",
            "OKC":"奧克拉荷馬市雷霆","ORL":"奧蘭多魔術","PHI":"費城76人","PHO":"鳳凰城太陽","POR":"波特蘭拓荒者",
            "SAC":"沙加緬度國王","SAS":"聖安東尼奧馬刺","TOR":"多倫多暴龍","UTA":"猶他爵士","WAS":"華盛頓巫師"}
        self.path = r"C:\Users\Guess365User\Desktop\nba\123\\"
        self.account = "rick860715"
        self.password = 
        
    def data_update(self):
        '''
        球隊對戰數據更新
        '''
        if self.update == 0:
            print("*********************Update data start*********************")
            try:
                team = ["ATL","BOS","CHO","CHI","CLE","DAL","DEN","DET","GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","BRK","NOP","NYK","OKC",
                    "ORL","PHI","PHO","POR","SAC","SAS","TOR","UTA","WAS"]
                for t in team:
                    if self.date.month >= 10:
                        url = "https://www.basketball-reference.com/teams/" + t +"/" + str(self.date.year+ 1) + "_games.html"
                    else:
                        url = "https://www.basketball-reference.com/teams/" + t +"/" + str(self.date.year) + "_games.html"
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text,"html.parser")
                    body = soup.find_all("tbody")
                    tr = body[0].find_all("tr")
                    tbody = []
                    for i in range(len(tr)):
                        g = tr[i].find("th").text
                        td = tr[i].find_all("td")
                        data = []
                        for j in range(len(td)):
                            td_ = td[j].text
                            data.append(td_)
                        data.insert(0,g)
                        tbody.append(data)
                    df_n = pd.DataFrame(tbody,columns = ["Game","Date","Start","delt","box","V/H","Opponent","result","OT","Tm","Opp","W","L","b_continue","Note"])
                    df_n.index = df_n["Game"]
                    df_n.drop(["Game","Start","delt","box","Note"],axis = 1,inplace = True)
                    df_n.drop(["G"],inplace = True)
                    dateFormatter = "%a, %b %d, %Y"
                    date_ = []
                    for i in range(0,len(df_n["Date"])):
                        d = datetime.datetime.strptime(df_n["Date"][i], dateFormatter)
                        date_.append(d)
                    df_n["Date"] = date_
                    df_n = df_n[df_n["Date"] <= self.date -  datetime.timedelta(days=1)]
                    df_n["V/H"].replace({"@" : 1,"":0},inplace = True)       #1代表客場,0代表主場
                    df_n["OT"].replace({"":0,"OT":1,"2OT":2,"3OT":3,"4OT":4},inplace=True)
                    df_n["b_continue"] = df_n["b_continue"].str.replace("W ","+")
                    df_n["b_continue"] = df_n["b_continue"].str.replace("L ","-")
                    df_n["b_continue"] = df_n["b_continue"].astype(int)
                    df_n["b_continue"] = df_n["b_continue"].shift(1).fillna(0)
                    df_n.to_excel(self.path + "Last Season\\" + t + " total Season.xlsx")
                print("*********************Update data successful!!*********************")
                self.update += 1
            except Exception as e: 
                    print(repr(e))
                    print("最新數據尚未更新!!")
            
    def sch(self):
        '''
        最新賽程表
        '''
        if self.update == 1:
            try:
                name = {"Atlanta Hawks":"ATL","Boston Celtics":"BOS","Charlotte Hornets":"CHO","Chicago Bulls":"CHI",
                "Cleveland Cavaliers":"CLE","Dallas Mavericks":"DAL","Denver Nuggets":"DEN","Detroit Pistons":"DET",
                "Golden State Warriors":"GSW","Houston Rockets":"HOU","Indiana Pacers":"IND","Los Angeles Clippers":"LAC",
                "Los Angeles Lakers":"LAL","Memphis Grizzlies":"MEM","Miami Heat":"MIA","Milwaukee Bucks":"MIL",
                "Minnesota Timberwolves":"MIN","Brooklyn Nets":"BRK","New Orleans Pelicans":"NOP","New York Knicks":"NYK",
                "Oklahoma City Thunder":"OKC","Orlando Magic":"ORL","Philadelphia 76ers":"PHI","Phoenix Suns":"PHO",
                "Portland Trail Blazers":"POR","Sacramento Kings":"SAC","San Antonio Spurs":"SAS","Toronto Raptors":"TOR",
                "Utah Jazz":"UTA","Washington Wizards":"WAS","New Orleans Hornets":"NOP","Charlotte Bobcats":"CHO","New Jersey Nets":"BRK"}
                if self.date.month >= 10:
                    url = "https://www.basketball-reference.com/leagues/NBA_" + str(self.date.year+1) + "_games-april.html"
                else:
                    url = "https://www.basketball-reference.com/leagues/NBA_" + str(self.date.year) + "_games-april.html"
                res = requests.get(url)
                soup = BeautifulSoup(res.text,"html.parser")
                tr = soup.find('table',{"id":"schedule"}).find_all("tr")
                data_all = []
                for i in range(1,len(tr)):
                    date = tr[i].find("th").text
                    dateFormatter = "%a, %b %d, %Y"
                    MatchTime = datetime.datetime.strptime(date,dateFormatter)
                    td = tr[i].find_all("td")
                    away_team = td[1].text
                    away_pts = td[2].text
                    home_team = td[3].text
                    home_pts = td[4].text
                    box = td[5]
                    if box.text != "":
                        evencode = box.find("a").get("href")
                    else:
                        evencode = ""
                    data_one = {
                        "Date":MatchTime,
                        "Visitor":name[away_team],
                        "PTS_V":away_pts,
                        "Home":name[home_team],
                        "PTS_H": home_pts,
                        "Evencode" : evencode
                    }
                    data_all.append(data_one)
                o_sch = pd.DataFrame(data_all)
                o_sch.index = o_sch["Date"]
                o_sch.drop(["Date"],axis = 1,inplace = True)
                next_sch = o_sch[o_sch.index == self.date]
                self.update +=1
                return next_sch
            except Exception as e: 
                print(repr(e))
                print("最新賽程爬取錯誤!!")
    
    def V_WS(self,sch):
        '''
        客隊當家球星數據更新
        '''
        if self.update == 2:
            print("*********************Update Visitor  WS start*********************")
            try:
                v_ws = []
                for s in range(len(sch)):
                    v = sch["Visitor"][s]
                    if v == "CHO":
                        v = "CHA"
                    elif v == "BRK":
                        v = "NJN"
                    elif v == "NOP":
                        v = "NOH"
                    year = sch.index[s].year
                    mon = sch.index[s].month
                    if mon > 10:
                        year = year + 1
                    url = "https://www.basketball-reference.com/teams/" + v +"/"
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text,"html.parser")
                    ws = 2022 - year
                    ws_href = soup.find("tbody").find_all("td")[18 * (ws+1) - 1].find("a").get('href')[:-5]
                    url = "https://www.basketball-reference.com" + ws_href + "/gamelog/" + str(year-1)
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text,"html.parser")
                    if str(soup.find("tbody")) == 'None':
                        pass
                    else:
                        tbody = soup.find("tbody").find_all("tr")
                        season = []
                        for i in range(len(tbody)):
                            if i == 20 or i == 41 or i == 62 or i == 83:
                                continue
                            rk = tbody[i].find("th").text
                            body = tbody[i].find_all("td")
                            if body[0].text == "":
                                continue
                            else:
                                data_all = []
                                for j in range(len(body)):
                                    data = body[j].text
                                    data_all.append(data)
                            data_all.insert(0,rk)
                            season.append(data_all)
                    url = "https://www.basketball-reference.com" + ws_href + "/gamelog/" + str(year)
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text,"html.parser")
                    tbody = soup.find("tbody").find_all("tr")
                    for i in range(len(tbody)):
                        if i == 20 or i == 41 or i == 62 or i == 83:
                            continue
                        rk = tbody[i].find("th").text
                        body = tbody[i].find_all("td")
                        if body[0].text == "":
                            continue
                        else:
                            data_all = []
                            for j in range(len(body)):
                                data = body[j].text
                                data_all.append(data)
                        data_all.insert(0,rk)
                        season.append(data_all)
                    df = pd.DataFrame(season,columns = ["Rk","G","Date","Age","Tm","V/H","Opp","W/L","GS","MP","FG","FGA","FG%","3P",
                                                        "3PA","3P%","FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF","PTS","GmSc","+/-"])
                    df.index = df["Date"]
                    df.drop(["Rk","G","Tm","V/H","Opp","W/L","Date","Age","GS","MP"],axis = 1,inplace = True)
                    df = df.replace("",0)
                    df = pd.DataFrame(df,dtype=np.float)
                    df = df[df.index < str(sch.index[s])]
                    df_m = df.mean().values
                    v_ws.append(df_m)
                v_ws_all = pd.DataFrame(v_ws,columns = ["WS總投籃命中(客)","WS總投籃(客)","WS投籃命中率(客)","WS3分球命中(客)","WS3分球投籃(客)","WS3分球命中率(客)",
                              "WS罰球命中(客)","WS罰球數(客)","WS罰球命中率(客)","WS進攻籃板(客)","WS防守籃板(客)","WS總籃板(客)","WS助攻(客)","WS抄截(客)",
                             "WS火鍋(客)","WS失誤(客)","WS犯規(客)","WS總得分(客)","WS球隊貢獻(客)","WS正負值(客)"])
                v_ws_all.index = sch.index
                print("********************* Update Visitor WS successful!!*********************")
                self.update += 1
                return v_ws_all
            except Exception as e: 
                print(repr(e))
                print(str(sch.index[s]) + " " + v + " Update Visitor WS faill!!")

    def H_WS(self,sch):
        '''
        主隊當家球星數據更新
        '''
        if self.update == 3:
            print("*********************Update Home WS start*********************")
            try:
                h_ws = []
                for s in range(len(sch)):
                    h = sch["Home"][s]
                    if h == "CHO":
                        h = "CHA"
                    elif h == "BRK":
                        h = "NJN"
                    elif h == "NOP":
                        h = "NOH"
                    year = sch.index[s].year
                    mon = sch.index[s].month
                    if mon > 10:
                        year = year + 1
                    url = "https://www.basketball-reference.com/teams/" + h +"/"
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text,"html.parser")
                    ws = 2022 - year
                    ws_href = soup.find("tbody").find_all("td")[18 * (ws+1) - 1].find("a").get('href')[:-5]
                    url = "https://www.basketball-reference.com" + ws_href + "/gamelog/" + str(year-1)
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text,"html.parser")
                    if str(soup.find("tbody")) == 'None':
                        pass
                    else:
                        tbody = soup.find("tbody").find_all("tr")
                        season = []
                        for i in range(len(tbody)):
                            if i == 20 or i == 41 or i == 62 or i == 83:
                                continue
                            rk = tbody[i].find("th").text
                            body = tbody[i].find_all("td")
                            if body[0].text == "":
                                continue
                            else:
                                data_all = []
                                for j in range(len(body)):
                                    data = body[j].text
                                    data_all.append(data)
                            data_all.insert(0,rk)
                            season.append(data_all)
                    url = "https://www.basketball-reference.com" + ws_href + "/gamelog/" + str(year)
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text,"html.parser")
                    tbody = soup.find("tbody").find_all("tr")
                    for i in range(len(tbody)):
                        if i == 20 or i == 41 or i == 62 or i == 83:
                            continue
                        rk = tbody[i].find("th").text
                        body = tbody[i].find_all("td")
                        if body[0].text == "":
                            continue
                        else:
                            data_all = []
                            for j in range(len(body)):
                                data = body[j].text
                                data_all.append(data)
                        data_all.insert(0,rk)
                        season.append(data_all)
                    df = pd.DataFrame(season,columns = ["Rk","G","Date","Age","Tm","V/H","Opp","W/L","GS","MP","FG","FGA","FG%","3P",
                                                        "3PA","3P%","FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF","PTS","GmSc","+/-"])
                    df.index = df["Date"]
                    df.drop(["Rk","G","Tm","V/H","Opp","W/L","Date","Age","GS","MP"],axis = 1,inplace = True)
                    df = df.replace("",0)
                    df = pd.DataFrame(df,dtype=np.float)
                    df = df[df.index < str(sch.index[s])]
                    df_m = df.mean().values
                    h_ws.append(df_m)
                h_ws_all = pd.DataFrame(h_ws,columns = ["WS總投籃命中(主)","WS總投籃(主)","WS投籃命中率(主)","WS3分球命中(主)","WS3分球投籃(主)","WS3分球命中率(主)",
                              "WS罰球命中(主)","WS罰球數(主)","WS罰球命中率(主)","WS進攻籃板(主)","WS防守籃板(主)","WS總籃板(主)","WS助攻(主)","WS抄截(主)",
                             "WS火鍋(主)","WS失誤(主)","WS犯規(主)","WS總得分(主)","WS球隊貢獻(主)","WS正負值(主)"])
                h_ws_all.index = sch.index
                print("*********************Update Home WS successful!!*********************")
                self.update += 1
                return h_ws_all
            except Exception as e: 
                print(repr(e))
                print(str(sch.index[s]) + " " + h + " Update Home WS fail!!")
            
    def Last_W_L(self,data_all):
        '''
        最新賽果更新
        '''
        if self.update == 4:
            print("*********************Update Win or Lose start*********************")
            try:
                last_w_v = []
                last_w_h = []
                for i in range(0,len(data_all)):
                    v = data_all["Visitor"][i]
                    h = data_all["Home"][i]
                    year = data_all.index[i].year
                    mon = data_all.index[i].month
                    if mon < 10:
                        df_v1 = pd.read_excel(self.path + "Season\\" + v +"\\"+ v +" Regular Season " + str(year-1) +".xlsx",index_col="Date")
                        df_v2 = pd.read_excel(self.path + "Last Season\\" + v +" total Season.xlsx",index_col="Date")
                        df_h1 =pd.read_excel(self.path + "Season\\" + h +"\\"+ h +" Regular Season " + str(year-1) +".xlsx",index_col="Date")
                        df_h2 = pd.read_excel(self.path + "Last Season\\" + h+" total Season.xlsx",index_col="Date")
                    else:
                        df_v1 = pd.read_excel(self.path + "Season\\" + v +"\\"+ v +" Regular Season " + str(year) +".xlsx",index_col="Date")
                        df_v2 = pd.read_excel(self.path + "Last Season\\" + v +" total Season.xlsx",index_col="Date")
                        df_h1 = pd.read_excel(self.path + "Season\\" + h +"\\"+ h +" Regular Season " + str(year) +".xlsx",index_col="Date")
                        df_h2 = pd.read_excel(self.path + "Last Season\\" + h+" total Season.xlsx",index_col="Date")
                    df_v1 = df_v1.append(df_v2)
                    df_h1 = df_h1.append(df_h2)
                    v_w = df_v1[df_v1.index < data_all.index[i]]["W"][-1]
                    v_l = df_v1[df_v1.index < data_all.index[i]]["L"][-1]
                    last_w_l = round(v_w / (v_w+ v_l),2)
                    last_w_v.append(last_w_l)
                    h_w = df_h1[df_h1.index < data_all.index[i]]["W"][-1]
                    h_l = df_h1[df_h1.index < data_all.index[i]]["L"][-1]
                    last_w_l_ = round(h_w / (h_w+ h_l),2)
                    last_w_h.append(last_w_l_)
                print("*********************Update Win or Lose successful!!*********************") 
                self.update += 1
                return last_w_v,last_w_h
            except Exception as e: 
                print(repr(e))
                print("*********************Update Win or Lose fail!!*********************") 
        else:
            return "",""
            
    def Odds_rate(self,sch):
        '''
        最新賽程賠率抓取
        '''
        if self.update == 5:
            print("*********************Update Odds rate start*********************") 
            try:
                sch.index = sch.index + datetime.timedelta(days=1)
                year = sch.index[0].year
                month = sch.index[0].month
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--disable-notifications")
                browser = webdriver.Chrome(options=options)
                browser.get("https://nba.win007.com/cn/Normal.aspx?y=" + str(year) + "&m=" + str(month) + "&matchSeason=" + str(year-1) + "-" + str(year) +"&SclassID=1")
                soup = BeautifulSoup(browser.page_source,"lxml")
                tr = soup.find_all("tbody")[2].find_all("tr")
                evencode_all = []
                for t in range(2,len(tr)):
                    if len(tr[t]) > 2:
                        dateFormatter = "%Y%m-%d %H:%M"
                        date = (datetime.datetime.strptime(str(year) + tr[t].find_all("td")[1].text,dateFormatter)).strftime("%Y-%m-%d")
                        if date ==sch.index[0].strftime("%Y-%m-%d"):
                            evencode = tr[t].find_all("td")[7].find("a").get("href").split("/")[2][:-4]
                            evencode_all.append(evencode)
                data_all = []
                for code in evencode_all:
                    browser.get("https://nba.win007.com/1x2/oddslist/" + code +".htm")
                    sleep(1)
                    select = Select(browser.find_element_by_id("sel_showType"))
                    select.select_by_value("1")
                    soup_odd = BeautifulSoup(browser.page_source,"lxml")
                    tr = soup_odd.find("table",{"id":"oddsList_tab"}).find("tbody").find_all("tr")
                    home_team = soup_odd.find("div",{"class":"home"}).text.split("\n")[2]
                    away_team = soup_odd.find("div",{"class":"guest"}).text.split("\n")[2]
                    #不讓分
                    for t in range(len(tr)):
                        company = tr[t].find_all("td")
                        if  "365(英国)" in company[1].text :
                            first_odds_home_win = company[2].text
                            first_odds_away_win = company[3].text
                            next_last = tr[t +1].find_all("td")
                            if  next_last[0].text != '\xa0':
                                last_odds_home_win = next_last[0].text
                                last_odds_away_win = next_last[1].text
                            else:
                                last_odds_home_win = first_odds_home_win
                                last_odds_away_win = first_odds_away_win
                    #過盤
                    browser.get("https://nba.win007.com/odds/OverDown_n.aspx?id=" + code + "&l=0")
                    sleep(1)
                    soup_od = BeautifulSoup(browser.page_source,"lxml")
                    tr = soup_od.find("table",{"id":"odds"}).find("tbody").find_all("tr")
                    for t in range(len(tr)):
                        company = tr[t].find_all("td")
                        if "365" in company[0].text:
                            first_over = company[2].text.split("\n")[1].replace(" ","")
                            first_score = company[3].text.split("\n")[1].replace(" ","")
                            first_under = company[4].text.split("\n")[1].replace(" ","")
                            last_over = company[8].text.split("\n")[2].replace(" ","")
                            last_score = company[9].text.split("\n")[1].replace(" ","")
                            last_under = company[10].text.split("\n")[2].replace(" ","")

                #讓分
                    browser.get("https://nba.win007.com/odds/AsianOdds_n.aspx?id=" + code + "&l=0")
                    sleep(1)
                    soup_o = BeautifulSoup(browser.page_source,"lxml")
                    tr = soup_o.find("table",{"id":"odds"}).find("tbody").find_all("tr")
                    for t in range(len(tr)):
                        company = tr[t].find_all("td")
                        if "365" in company[0].text:
                            first_home = company[2].text.split("\n")[1].replace(" ","")
                            first_handicap = company[3].text.split("\n")[1].replace(" ","")
                            first_away = company[4].text.split("\n")[1].replace(" ","")
                            last_home = company[8].text.split("\n")[2].replace(" ","")
                            last_handicap = company[9].text.split("\n")[1].replace(" ","")
                            last_away = company[10].text.split("\n")[2].replace(" ","")
                    data_one = {
                        "主隊" : home_team,
                        "客隊" : away_team,
                        "主勝(初)" : first_odds_home_win,
                        "客勝(初)" : first_odds_away_win,
                        "主勝(終)" : last_odds_home_win,
                        "客勝(終)" : last_odds_away_win,
                        "過盤(初)" : first_over,
                        "過盤分(初)" :  first_score,
                        "不過盤(初)" : first_under,
                        "過盤(終)" : last_over,
                        "過盤分(終)" :  last_score,
                        "不過盤(終)" : last_under,
                        "讓分主勝(初)" : first_home,
                        "讓分盤口(初)" : first_handicap,
                        "讓分客勝(初)" : first_away,
                        "讓分主勝(終)" : last_home,
                        "讓分盤口(終)" : last_handicap,
                        "讓分客勝(終)" : last_away,
                    }
                    data_all.append(data_one)
                df_all = pd.DataFrame(data_all)
                browser.close()
                print("*********************Update Odds rate successful!!*********************")  
                self.update += 1
                return df_all
            except Exception as e: 
                print(repr(e))
                print(f"{home_team} vs {away_team} 的NBA數據爬取失敗!!")
        
    def odds_win_lose(self,day = 0):
        '''
        NBA賽事預測
        '''
        
        self.date = datetime.datetime.strptime((datetime.datetime.now()- datetime.timedelta(days=day)).strftime("%Y-%m-%d"),"%Y-%m-%d")
        self.update = 0
        self.data_update()
        sch_date = self.sch()
        v_ws = self.V_WS(sch_date)
        h_ws = self.H_WS(sch_date)
        last_w_v,last_w_h = self.Last_W_L(sch_date)
        odds = self.Odds_rate(sch_date)
        if self.update == 6:
            df_all = pd.DataFrame(columns= ["讓分盤口(終)","讓分盤口(初)","主勝(初)","客勝(初)","主勝(終)","客勝(終)","最新勝率(主)","WS正負值(客)","WS正負值(主)","最新勝率(客)"])
            df_all["讓分盤口(終)"] = odds["讓分盤口(終)"].values
            df_all["讓分盤口(初)"] = odds["讓分盤口(初)"].values
            df_all["主勝(初)"] = odds["主勝(初)"].values
            df_all["客勝(初)"] = odds["客勝(初)"].values
            df_all["主勝(終)"] = odds["主勝(終)"].values
            df_all["客勝(終)"] = odds["客勝(終)"].values
            df_all["最新勝率(主)"] = last_w_h
            df_all["WS正負值(客)"] = v_ws["WS正負值(客)"].values
            df_all["WS正負值(主)"] = h_ws["WS正負值(主)"].values
            df_all["最新勝率(客)"] = last_w_v
            df_all = df_all.astype(float)
            df_all["Visitor"] = sch_date["Visitor"].values
            df_all["Home"] = sch_date["Home"].values
            df_x = df_all.drop(["Visitor","Home"],axis = 1)
            model =load_model(self.path + "NBA_w_l_rate_select.h5")
            pre = model.predict(df_x)
            print("*********************NBA Forecast result*********************")   
            for i in range(0,len(pre)):
                v = df_all["Visitor"][i]
                h = df_all["Home"][i]
                url = 'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/NBA/any'
                response = requests.get(url,verify=False,auth=HTTPBasicAuth('rick', 'ri000')).text
                sleep(2)
                j = json.loads(response)
                json_data = j['response']
                have_update = False
                for d in range(len(json_data)):
                    team_name_v = json_data[d]["AwayTeam"][1]
                    team_name_h = json_data[d]["HomeTeam"][1]
                    if team_name_v == self.name[v] and team_name_h == self.name[h] and "_" not in json_data[d]["EventCode"]:
                        have_update = True
                        EventCode = json_data[d]["EventCode"]
                if have_update == False:
                    print(f"無 {self.name[v]} v.s {self.name[h]} 的賽程")
                else:
                    if pre[i]  < 0.5:
                        print(self.name[v] + " (LOSE) v.s " + self.name[h] + " (WIN)" )
                        OptionCode = "1"   
                    else:
                        print(self.name[v] + " (WIN) v.s " + self.name[h] + " (LOSE)" )
                        OptionCode = "2"
                    url = "https://ecocoapidev1.southeastasia.cloudapp.azure.com/PredictMatchEntry/"
                    data = {'account':self.account,
                     'password':self.password,
                     'GroupOptionCode':"20",
                     'OptionCode':OptionCode,
                     'EventCode':EventCode,
                     'PredictType':'Selling'}
                    response_ = requests.post(url,verify=False, data = data, auth=HTTPBasicAuth('rick', 'ri000')).text
                    sleep(2)
                    print(response_)
        
if __name__ == '__main__':
    NBAPredict = NBAPredict()
    NBAPredict.odds_win_lose(1)  
