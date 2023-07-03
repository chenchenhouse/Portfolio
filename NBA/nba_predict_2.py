#!/usr/bin/env python
# coding: utf-8

# In[32]:


import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import numpy as np
import datetime
from keras.models import load_model

class NBAPredict(object):
    '''
    groupoptioncode: 20強弱盤
    optioncode:1主 2客
    '''
    def __init__(self):
        self.path = r"C:\Users\adsad\OneDrive\Desktop\神預(工作)\nba\\"
        self.name  = {"Atlanta Hawks":"ATL","Boston Celtics":"BOS","Charlotte Hornets":"CHO","Chicago Bulls":"CHI",
                "Cleveland Cavaliers":"CLE","Dallas Mavericks":"DAL","Denver Nuggets":"DEN","Detroit Pistons":"DET",
                "Golden State Warriors":"GSW","Houston Rockets":"HOU","Indiana Pacers":"IND","Los Angeles Clippers":"LAC",
                "Los Angeles Lakers":"LAL","Memphis Grizzlies":"MEM","Miami Heat":"MIA","Milwaukee Bucks":"MIL",
                "Minnesota Timberwolves":"MIN","Brooklyn Nets":"BRK","New Orleans Pelicans":"NOP","New York Knicks":"NYK",
                "Oklahoma City Thunder":"OKC","Orlando Magic":"ORL","Philadelphia 76ers":"PHI","Phoenix Suns":"PHO",
                "Portland Trail Blazers":"POR","Sacramento Kings":"SAC","San Antonio Spurs":"SAS","Toronto Raptors":"TOR",
                "Utah Jazz":"UTA","Washington Wizards":"WAS","New Orleans Hornets":"NOP","Charlotte Bobcats":"CHO","New Jersey Nets":"BRK"}
        self.chname = {"ATL":"亞特蘭大老鷹","BOS":"波士頓賽爾提克","CHO":"夏洛特黃蜂","CHI":"芝加哥公牛","CLE":"克里夫蘭騎士",
            "DAL":"達拉斯獨行俠","DEN":"丹佛金塊","DET":"底特律活塞","GSW":"金洲勇士","HOU":"休士頓火箭",
            "IND":"印第安納溜馬","LAC":"洛杉磯快艇","LAL":"洛杉磯湖人","MEM":"曼菲斯灰熊","MIA":"邁阿密熱火",
            "MIL":"密爾瓦基公鹿","MIN":"明尼蘇達灰狼","BRK":"布魯克林籃網","NOP":"新奧爾良鵜鶘","NYK":"紐約尼克",
            "OKC":"奧克拉荷馬市雷霆","ORL":"奧蘭多魔術","PHI":"費城76人","PHO":"鳳凰城太陽","POR":"波特蘭拓荒者",
            "SAC":"沙加緬度國王","SAS":"聖安東尼奧馬刺","TOR":"多倫多暴龍","UTA":"猶他爵士","WAS":"華盛頓巫師"}
    def sch(self):        
        '''
        最新賽程表
        '''
        if self.update == 0:
            print("*********************Update  new Schedule start*********************")
            try:
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
                        "Visitor":self.name[away_team],
                        "PTS_V":away_pts,
                        "Home":self.name[home_team],
                        "PTS_H": home_pts,
                        "Evencode" : evencode
                    }
                    data_all.append(data_one)
                o_sch = pd.DataFrame(data_all)
                o_sch.index = o_sch["Date"]
                o_sch.drop(["Date"],axis = 1,inplace = True)
                next_sch = o_sch[o_sch.index == self.date]
                self.update += 1
                print("*********************Update  new Schedule successful!!*********************")
                return next_sch
            except Exception as e: 
                print(repr(e))
                print("最新賽程爬取錯誤!!")
                
                
    def updata_sch(self):
        '''
        更新最新賽季主客場賽程
        '''
        if self.update == 1:
            print("*********************Update Schedule start*********************")
            try:
                abb_name = ["ATL","BOS","CHO","CHI","CLE","DAL","DEN","DET","GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","BRK","NOP","NYK",
                    "OKC","ORL","PHI","PHO","POR","SAC","SAS","TOR","UTA","WAS"]
                if self.date.month >= 10:
                    year = [self.date.year,self.date.year+1]
                else:
                    year = [self.date.year - 1,self.date.year]
                for n in abb_name:
                    data_all = []
                    for y in year:
                        url = "https://www.basketball-reference.com/teams/" + n +"/" +str(y) + "_games.html"
                        res = requests.get(url)
                        soup = BeautifulSoup(res.text,"html.parser")
                        body = soup.find_all("tbody")
                        if len(body) == 1:
                            body_ = body[0].find_all("tr")
                            for i in range(0,len(body_)):
                                g = body_[i].find("th").text
                                td = body_[i].find_all("td")
                                data_td = []
                                for j in range(0,len(td)):
                                    data = td[j].text
                                    data_td.append(data)
                                data_td.insert(0,g)
                                data_all.append(data_td)
                        else:
                            for t in range(0,len(body)):
                                body_ = body[t].find_all("tr")
                                for i in range(0,len(body_)):
                                    g = body_[i].find("th").text
                                    td = body_[i].find_all("td")
                                    data_td = []
                                    for j in range(0,len(td)):
                                        data = td[j].text
                                        data_td.append(data)
                                    data_td.insert(0,g)
                                    data_all.append(data_td)
                    df = pd.DataFrame(data_all,columns  = ["場次","日期","開始時間", "未知","數據盒","主客場","對手","勝負","OT","自己得分","對手得分","贏(累計)","輸(累計)","連續輸贏","備註"])
                    df.index = df["場次"] 
                    df.drop(["G"],inplace = True)
                    date_all = []
                    dateFormatter = "%a, %b %d, %Y"
                    for d in range(0,len(df)):
                        date = datetime.datetime.strptime(df["日期"][d], dateFormatter)
                        date_all.append(date)
                    df["日期"] = date_all   
                    df["對手"].replace(self.name,inplace = True)
                    df["OT"].replace({"":0,"OT":1,"2OT":2,"3OT":3,"4OT":4},inplace = True)
                    df.drop(["場次","開始時間","未知","數據盒","備註"],axis = 1,inplace = True)
                    v_sch = df[df["主客場"] == "@"]
                    h_sch = df[df["主客場"] == ""]
                    v_sch.to_excel(self.path + "team Schedule\\" + n + " Visitor Schedule.xlsx")
                    h_sch.to_excel(self.path + "team Schedule\\" + n + " Home Schedule.xlsx")
                print("*********************Update Schedule successful!!*********************")
                self.update += 1 
            except Exception as e: 
                print(repr(e))
                print("尚無最新賽季賽程")
                
    def visitor(self,next_sch):
        '''
        客隊前5場客隊狀況
        '''
        if self.update == 2:
            print("*********************Update visitor start*********************")
            try:
                df_vis = pd.DataFrame()
                for s in range(0,len(next_sch)):
                    v_name = next_sch["Visitor"][s]
                    date = next_sch.index[s]
                    v_sch = pd.read_excel(self.path + "team Schedule\\" + v_name + " Visitor Schedule.xlsx",index_col = "場次")
                    v_final = v_sch[v_sch["日期"]< date][-5:]
                    v_f_op = v_final["對手"]
                    v_f_date = v_final["日期"]
                    df_all = []
                    for i in range(0,len(v_final)):
                        year = v_f_date.iloc[i].year
                        mon = v_f_date.iloc[i].month
                        day = v_f_date.iloc[i].day
                        op = v_f_op.iloc[i]
                        ot = v_final["OT"].iloc[i]
                        if mon < 10 and day < 10: 
                            url = "https://www.basketball-reference.com/boxscores/" + str(year) + "0" + str(mon) + "0" + str(day) + "0" + op + ".html"
                        elif mon < 10:
                             url = "https://www.basketball-reference.com/boxscores/" + str(year) + "0" + str(mon) + str(day) + "0" + op + ".html"
                        elif day < 10:
                             url = "https://www.basketball-reference.com/boxscores/" + str(year) + str(mon) + "0" + str(day) + "0" + op + ".html"
                        else:
                            url = "https://www.basketball-reference.com/boxscores/" + str(year) + str(mon) + str(day) + "0" + op + ".html"
                        res = requests.get(url)
                        soup = BeautifulSoup(res.text,"html.parser")
                        if ot == 1:
                            tfoot =[0,8]
                        elif ot == 2:
                             tfoot =[0,9]
                        elif ot == 3:
                            tfoot = [0,10]
                        elif ot == 4:
                            tfoot = [0,11]
                        else:
                            tfoot = [0,7]
                        data = []
                        for t in tfoot:
                            foot = soup.find_all("tfoot")[t].find_all("td")
                            if len(foot) == 15:
                                for j in range(1,len(foot)):
                                    foot_ = foot[j].text
                                    data.append(foot_)
                            else:
                                for j in range(1,len(foot)-1):
                                    foot_ = foot[j].text
                                    data.append(foot_)
                        df_all.append(data)
                    df = pd.DataFrame(df_all,columns = ["總投籃命中(客)","總投籃(客)","投籃命中率(客)","3分球命中(客)","3分球投籃(客)","3分球命中率(客)","罰球命中(客)",
                                                  "罰球數(客)","罰球命中率(客)","進攻籃板(客)","防守籃板(客)","總籃板(客)","助攻(客)","抄截(客)","火鍋(客)","失誤(客)","犯規(客)",
                                                  "總得分(客)","真實命中率(客)","有效命中率(客)","3分球比率(客)","要犯率(客)","進攻籃板率(客)","防守籃板率(客)","總籃板率(客)",
                                                  "助功率(客)","抄截率(客)","火鍋率(客)","失誤率(客)","球權佔有率(客)","進攻評分(客)","防守評分(客)"])
                    df=pd.DataFrame(df,dtype=np.float)
                    df = pd.DataFrame(df.mean())
                    df_t = df.T
                    df_vi = pd.DataFrame()
                    df_vi = df_vi.append(df_t)
                    df_vis = df_vis.append(df_vi)
                print("*********************Update visitor successful!!*********************")
                self.update += 1
                return df_vis
            except Exception as e: 
                print(repr(e))
                print("尚無最新客隊賽程")
            
    def home(self,next_sch):
        '''
        主隊前5場主隊狀況
        '''
        if self.update == 3:
            print("*********************Update home start*********************")
            try:
                df_hom = pd.DataFrame()
                for s in range(0,len(next_sch)):
                    h_name = next_sch["Home"][s]
                    date = next_sch.index[s]
                    h_sch = pd.read_excel(self.path + "team Schedule\\" + h_name + " Home Schedule.xlsx",index_col = "場次")
                    h_final = h_sch[h_sch["日期"]< date][-5:]
                    h_f_op = h_final["對手"]
                    h_f_date = h_final["日期"]
                    df_all = []
                    for i in range(0,len(h_final)):
                        year = h_f_date.iloc[i].year
                        mon = h_f_date.iloc[i].month
                        day = h_f_date.iloc[i].day
                        op = h_f_op.iloc[i]
                        ot = h_final["OT"].iloc[i]
                        if mon < 10 and day < 10: 
                            url = "https://www.basketball-reference.com/boxscores/" + str(year) + "0" + str(mon) + "0" + str(day) + "0" + h_name + ".html"
                        elif mon < 10:
                             url = "https://www.basketball-reference.com/boxscores/" + str(year) + "0" + str(mon) + str(day) + "0" + h_name + ".html"
                        elif day < 10:
                             url = "https://www.basketball-reference.com/boxscores/" + str(year) + str(mon) + "0" + str(day) + "0" + h_name + ".html"
                        else:
                            url = "https://www.basketball-reference.com/boxscores/" + str(year) + str(mon) + str(day) + "0" + h_name + ".html"
                        res = requests.get(url)
                        soup = BeautifulSoup(res.text,"html.parser")
                        if ot == 1:
                            tfoot =[9,17]
                        elif ot == 2:
                             tfoot =[10,19]
                        elif ot == 3:
                            tfoot = [11,21]
                        elif ot == 4:
                            tfoot = [12,23]
                        else:
                            tfoot = [8,15]
                        data = []
                        for t in tfoot:
                            foot = soup.find_all("tfoot")[t].find_all("td")
                            if len(foot) == 15:
                                for j in range(1,len(foot)):
                                    foot_ = foot[j].text
                                    data.append(foot_)
                            else:
                                for j in range(1,len(foot)-1):
                                    foot_ = foot[j].text
                                    data.append(foot_)
                        df_all.append(data)
                    df = pd.DataFrame(df_all,columns = ["總投籃命中(主)","總投籃(主)","投籃命中率(主)","3分球命中(主)","3分球投籃(主)","3分球命中率(主)","罰球命中(主)",
                                                  "罰球數(主)","罰球命中率(主)","進攻籃板(主)","防守籃板(主)","總籃板(主)","助攻(主)","抄截(主)","火鍋(主)","失誤(主)","犯規(主)",
                                                  "總得分(主)","真實命中率(主)","有效命中率(主)","3分球比率(主)","要犯率(主)","進攻籃板率(主)","防守籃板率(主)","總籃板率(主)",
                                                  "助功率(主)","抄截率(主)","火鍋率(主)","失誤率(主)","球權佔有率(主)","進攻評分(主)","防守評分(主)"])
                    df=pd.DataFrame(df,dtype=np.float)
                    df = pd.DataFrame(df.mean())
                    df_t = df.T
                    df_hi = pd.DataFrame()
                    df_hi = df_hi.append(df_t)
                    df_hom = df_hom.append(df_hi)
                print("*********************Update home successful!!*********************")
                self.update += 1 
                return df_hom
            except Exception as e: 
                print(repr(e))
                print("尚無最新主隊賽程")
        
    
    def mean_std(self):
        '''
        紀錄標準化的數值
        '''
        df = pd.read_excel(self.path + "賽季數據.xlsx",index_col = "Date")
        df_train_x = df[['罰球命中率(客)', '真實命中率(客)', '火鍋率(客)', '進攻評分(客)', '防守評分(客)', '罰球命中率(主)',
           '總籃板率(主)', '失誤率(主)', '進攻評分(主)', '防守評分(主)']]
        mean = df_train_x.mean()
        std = df_train_x.std()
        return mean,std

    def test_W_L(self,day=0):
        self.update = 0
        self.date = datetime.datetime.strptime((datetime.datetime.now()- datetime.timedelta(days=day)).strftime("%Y-%m-%d"),"%Y-%m-%d")
        next_sch = self.sch()
        self.updata_sch()
        df_vis = self.visitor(next_sch)
        df_hom = self.home(next_sch)
        if self.update == 4:
            df_vis.index = next_sch.index
            df_hom.index = next_sch.index
            data_all = pd.concat([next_sch,df_vis,df_hom],axis = 1)
            mean,std = self.mean_std()
            df_x = data_all[['罰球命中率(客)', '真實命中率(客)', '火鍋率(客)', '進攻評分(客)', '防守評分(客)', '罰球命中率(主)',
               '總籃板率(主)', '失誤率(主)', '進攻評分(主)', '防守評分(主)']]
            df_x_z = (df_x - mean) / std
            model = load_model(self.path + "NBA_predict_z_score.h5")
            pre = model.predict_classes(df_x_z)
            for i in range(0,len(pre)):
                v = data_all["Visitor"][i]
                h = data_all["Home"][i]
                if pre[i] == 0:
                    print(self.chname[v] + " (LOSE) v.s " + self.chname[h] + " (WIN)" )
                else:
                    print(self.chname[v] + " (WIN) v.s " + self.chname[h] + " (LOSE)" )

    
if __name__ == '__main__':
    NBAPredict = NBAPredict()
    NBAPredict.test_W_L()


# In[ ]:




