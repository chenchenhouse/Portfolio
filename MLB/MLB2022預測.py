#!/usr/bin/env python
# coding: utf-8

# In[3]:


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
import json
from requests.auth import HTTPBasicAuth
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras.models import load_model
from keras.layers import Dense , Dropout
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve,auc
from sklearn.metrics import confusion_matrix
import re
import sys 




class MLBPredict(object):
    def __init__(self):
        self.date = datetime.datetime.now() 
        self.name = {"Philadelphia Phillies":"PHI","New York Yankees":"NYY","Detroit Tigers":"DET","Baltimore Orioles":"BAL",
                             "Toronto Blue Jays":"TOR","Pittsburgh Pirates":"PIT","Cincinnati Reds":"CIN","Cleveland Guardians":"CLE",
                             "Cleveland Indians" : "CLE","Oakland Athletics":"OAK","San Francisco Giants":"SFG","Atlanta Braves":"ATL",
                             "New York Mets":"NYM","Seattle Mariners":"SEA","San Diego Padres":"SDP","Chicago White Sox":"CHW",
                             "Texas Rangers":"TEX","Kansas City Royals":"KCR","Colorado Rockies":"COL","Arizona Diamondbacks":"ARI",
                             "Arizona D'Backs" : "ARI","Tampa Bay Rays":"TBR","Miami Marlins":"MIA","St. Louis Cardinals":"STL",
                             "Houston Astros":"HOU","Los Angeles Angels":"LAA","Los Angeles Dodgers" : "LAD","Milwaukee Brewers":"MIL",
                             "Chicago Cubs":"CHC","Washington Nationals":"WSN","Boston Red Sox":"BOS","Minnesota Twins":"MIN"}
        self.name_2 = {"費城人":"PHI","紐約洋基":"NYY","底特律老虎":"DET","巴爾的摩黃鸝":"BAL","多倫多藍鳥":"TOR","匹茲堡海盜":"PIT",
                "辛辛那提紅人":"CIN","波士頓紅襪":"BOS","奧克蘭運動家":"OAK","三藩市巨人":"SFG","明尼蘇達雙城":"MIN","華盛頓國民":"WSN",
                "亞特蘭大勇士":"ATL","紐約大都會":"NYM","德州游騎兵":"TEX","堪薩斯城皇家":"KCR","洛杉磯道奇":"LAD","芝加哥白襪":"CHW",
                "西雅圖水手":"SEA","聖地亞哥教士":"SDP","科羅拉多洛基":"COL","亞利桑那響尾蛇":"ARI","坦帕湾魔鬼鱼":"TBR","迈亚密馬林魚":"MIA",
                "聖路易斯紅雀":"STL","克里夫蘭守護者":"CLE","休斯頓太空人":"HOU","密爾沃基釀酒人":"MIL","芝加哥小熊":"CHC","克里夫蘭印第安人" : "CLE",
                "洛杉磯天使":"LAA"}
        self.name_3 = {"PHI":"費城費城人","NYY":"紐約洋基","DET":"底特律老虎","BAL":"巴爾地摩金鶯","TOR":"多倫多藍鳥",
                               "PIT":"匹茲堡海盜","CIN":"辛辛那堤紅人","BOS": "波士頓紅襪","OAK":"奧克蘭運動家","SFG": "舊金山巨人",
                               "MIN":"明尼蘇達雙城","WSN":"華盛頓國民","ATL":"亞特蘭大勇士","NYM":"紐約大都會","TEX":"德州遊騎兵",
                               "KCR":"堪薩斯皇家","LAD":"洛杉磯道奇","CHW":"芝加哥白襪","SEA":"西雅圖水手","SDP":"聖地牙哥教士",
                               "COL":"科羅拉多落磯山","ARI":"亞歷桑那響尾蛇","TBR":"坦帕灣光芒","MIA":"邁阿密馬林魚","STL":"聖路易紅雀",
                               "CLE":"克里夫蘭守護者","HOU":"休士頓太空人","MIL":"密爾瓦基釀酒人","CHC":"芝加哥小熊","LAA":"洛杉磯天使"}
        self.path = r"C:\Users\adsad\OneDrive\Desktop\神預(工作)\MLB\schedule\\"
        
    def reference_sch(self):
        '''
        爬取MLB reference的賽程
        '''
        print("*************************爬取reference賽程 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_all = []
            year = self.date.year
            browser.get(f"https://www.baseball-reference.com/leagues/majors/{str(year)}-schedule.shtml")
            soup = BeautifulSoup(browser.page_source,"lxml")
            soup.find("div",{"class":"section_content"})
            div = soup.find("div",{"class":"section_content"}).find_all("div")
            for d in range(len(div)):
                dateFormatter = "%A, %B %d, %Y"
                date_game = div[d].find("h3").text
                date_re = (self.date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                date_start = (self.date - datetime.timedelta(days=4)).strftime("%Y-%m-%d")
                if date_game != "Today's Games": 
                    MatchTime = datetime.datetime.strptime(date_game,dateFormatter).strftime("%Y-%m-%d")
                    find_p = div[d].find_all("p")
                    if MatchTime <= date_re and  MatchTime >= date_start and find_p[0].find_all("a")[2].text == "Boxscore":
                        for p in range(len(find_p)-1):
                            home_name = find_p[p].find_all("a")[1].text
                            away_name = find_p[p].find_all("a")[0].text
                            home_score =re.sub("\D","",find_p[p].text.split("\n")[2])
                            away_score = re.sub("\D","",find_p[p].text.split("\n")[5])
                            evencode = find_p[p].find_all("a")[2].get("href")
                            data_one = {
                                "Date" : MatchTime,
                                "主隊" : home_name,
                                "主隊得分" : home_score,
                                "客隊" : away_name,
                                "客隊得分" : away_score,
                                "Evencode" : evencode
                            }
                            data_all.append(data_one)
                            print(f"{str(MatchTime)} {home_name} vs {away_name} successful!!")
            data_all_n = pd.DataFrame(data_all)
            data_all_n.index = data_all_n["Date"]
            data_all_n.drop(["Date"],axis =1,inplace=True)
            print("*************************爬取reference賽程 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取reference賽程 fail!! ************************************") 
            sys.exit()
        browser.close()
        return data_all_n
    
    def reference_boxscore(self,data_all_n):
        print("*************************爬取reference boxscore start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            df_all = pd.DataFrame()
            for i in range(len(data_all_n)):
                date = data_all_n.index[i]
                evencode = data_all_n["Evencode"][i]
                browser.get(f"https://www.baseball-reference.com{evencode}")
                soup = BeautifulSoup(browser.page_source,"lxml")
                away_name = soup.find("div",{"class":"scorebox"}).find_all("strong")[0].find("a").text.replace(" ","").replace(".","")
                home_name = soup.find("div",{"class":"scorebox"}).find_all("strong")[1].find("a").text.replace(" ","").replace(".","")
                columns_all = []
                columns_ab = soup.find("table",{"id" :away_name + "batting"}).find("tr").find_all("th")
                for c in range(len(columns_ab[:-1])-1):
                    col = "Away_Batting_" + columns_ab[c+1].text
                    columns_all.append(col)
                columns_hb = soup.find("table",{"id" :home_name + "batting"}).find("tr").find_all("th")
                for c in range(len(columns_hb[:-1])-1):
                    col = "Home_Batting_" + columns_hb[c+1].text
                    columns_all.append(col)
                columns_ap = soup.find("table",{"id" :away_name + "pitching"}).find("tr").find_all("th")
                for c in range(len(columns_ap[:-1])):
                    col = "Away_Pitching_" + columns_ap[c+1].text
                    columns_all.append(col)
                columns_hp = soup.find("table",{"id" :home_name + "pitching"}).find("tr").find_all("th")
                for c in range(len(columns_hp[:-1])):
                    col = "Home_Pitching_" + columns_hp[c+1].text
                    columns_all.append(col)

                data_all = []
                data_ab = soup.find("table",{"id" :away_name + "batting"}).find("tfoot").find_all("td")[:-1]
                for d in range(len(data_ab)):
                    data = data_ab[d].text
                    data_all.append(data)
                data_hb = soup.find("table",{"id" :home_name + "batting"}).find("tfoot").find_all("td")[:-1]
                for d in range(len(data_hb)):
                    data = data_hb[d].text
                    data_all.append(data)
                data_ap = soup.find("table",{"id" :away_name + "pitching"}).find("tfoot").find_all("td")
                for d in range(len(data_ap)):
                    data = data_ap[d].text
                    data_all.append(data)
                data_hp = soup.find("table",{"id" :home_name + "pitching"}).find("tfoot").find_all("td")
                for d in range(len(data_hp)):
                    data = data_hp[d].text
                    data_all.append(data)
                df = pd.DataFrame(data_all).T
                df.columns = columns_all
                df_all = df_all.append(df)
                print(f"{str(date)} {evencode} successful!!")
            df_all.index = data_all_n.index
            data_all_n1 = pd.concat([data_all_n,df_all],axis = 1)
            data_all_n1.index = pd.to_datetime(data_all_n1.index)
            print("*************************爬取reference boxscore successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取reference boxscore fail!! ************************************")    
            sys.exit()
        browser.close()
        return data_all_n1
    
    def reference_data(self,data_all_n1):
        '''
        reference先發名單
        '''
        print("*************************爬取 reference先發名單 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)

            data_fpitcher = []
            for i in range(len(data_all_n1)):
                date = data_all_n1.index[i]
                evencode = data_all_n1["Evencode"][i]
                browser.get(f"https://www.baseball-reference.com{evencode}")
                soup = BeautifulSoup(browser.page_source,"lxml")
                away_name = soup.find("div",{"class":"scorebox"}).find_all("strong")[0].find("a").text.replace(" ","").replace(".","")
                home_name = soup.find("div",{"class":"scorebox"}).find_all("strong")[1].find("a").text.replace(" ","").replace(".","")
                data_ap = soup.find("table",{"id" :away_name + "pitching"}).find("tbody").find("tr")
                away_pitcher_name = data_ap.find("a").text
                away_pitcher_evencode = data_ap.find("a").get("href")
                data_hp = soup.find("table",{"id" :home_name + "pitching"}).find("tbody").find("tr")
                home_pitcher_name = data_hp.find("a").text
                home_pitcher_evencode = data_hp.find("a").get("href")
                data_one = {
                    'Away_FPitching_name' : away_pitcher_name,
                    'Away_FPitching_Evencode': away_pitcher_evencode,
                    'Home_FPitching_name' : home_pitcher_name,
                    'Home_FPitching_Evencode' : home_pitcher_evencode
                }
                data_fpitcher.append(data_one)
                print(f"{str(date)} {evencode} successful!!")
            df_fpitcher = pd.DataFrame(data_fpitcher)
            df_fpitcher.index = data_all_n1.index
            print("*************************爬取 reference先發名單 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取 reference先發名單 fail!! ************************************")  
            sys.exit()
        browser.close()

        '''
        reference away先發數據
        '''
        print("*************************爬取reference away先發數據 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_afpitcher = []
            for d in range(len(df_fpitcher)):
                data_one = []
                date = df_fpitcher.index[d]
                away = df_fpitcher["Away_FPitching_Evencode"][d].split("/")[-1].replace(".shtml","")
                away_name = df_fpitcher["Away_FPitching_name"][d]
                data_one.append(away_name)
                browser.get(f"https://www.baseball-reference.com/players/gl.fcgi?id={away}&t=p&year={str(date.year)}")
                soup = BeautifulSoup(browser.page_source,"lxml")
                tr = soup.find("table",{"id":"pitching_gamelogs"}).find("tbody").find_all("tr")
                for t in range(len(tr)):
                    td = tr[t].find_all("td")
                    if len(td) != 0:
                        game_time = td[2].get("csk").split(".")[0]
                        matchtime = df_fpitcher.index[d].strftime("%Y-%m-%d")
                        if matchtime == game_time:
                            for j in range(len(td)):
                                if j == 0:
                                    Gcar = td[j].get("data-endpoint")
                                    data_one.append(Gcar)
                                elif j == 1:
                                    Gtm = td[j].get("data-endpoint")
                                    data_one.append(Gtm)
                                elif j == 2:
                                    time = td[j].get("csk").split(".")[0]
                                    data_one.append(time)
                                else:
                                    data = td[j].text
                                    data_one.append(data)
                            data_afpitcher.append(data_one)
                            print(f"{game_time} {away_name} successful!!")
            col = ["Name","Box_Gcar","Box_Gtm","Date","Tm","H/V","Opp","Rslt","Inngs","Dec","DR","IP","H","R","ER","BB","SO","HR",
           "HBP","ERA","FIP","BF","Pit","Str","StL","StS","GB","FB","LD","PU","Unk","GSc","IR","IS","SB","CS","PO","AB","2B","3B",
           "IBB","GDP","SF","ROE","aLI","WPA","acLI","cWPA","RE24","DFS(DK)","DFS(FD)","Entered","Exited"]
            df_afpitcher = pd.DataFrame(data_afpitcher)
            df_afpitcher.index = data_all_n1.index
            df_afpitcher.columns = col
            df_afpitcher.columns = "Away_FPitching_" + df_afpitcher.columns
            df_afpitcher.drop(["Away_FPitching_DFS(DK)","Away_FPitching_DFS(FD)","Away_FPitching_Entered","Away_FPitching_Exited"],axis =1,inplace=True)
            print("*************************爬取 reference away先發數據 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取 reference away先發數據 fail!! ************************************")  
            sys.exit()
        browser.close()

        '''
        reference home先發數據
        '''
        print("*************************爬取 reference home先發數據 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_hfpitcher = []
            for d in range(len(df_fpitcher)):
                data_one = []
                date = df_fpitcher.index[d]
                home = df_fpitcher["Home_FPitching_Evencode"][d].split("/")[-1].replace(".shtml","")
                home_name = df_fpitcher["Home_FPitching_name"][d]
                data_one.append(home_name)
                browser.get(f"https://www.baseball-reference.com/players/gl.fcgi?id={home}&t=p&year={str(date.year)}")
                soup = BeautifulSoup(browser.page_source,"lxml")
                tr = soup.find("table",{"id":"pitching_gamelogs"}).find("tbody").find_all("tr")
                for t in range(len(tr)):
                    td = tr[t].find_all("td")
                    if len(td) != 0:
                        game_time = td[2].get("csk").split(".")[0]
                        matchtime = df_fpitcher.index[d].strftime("%Y-%m-%d")
                        if matchtime == game_time:
                            for j in range(len(td)):
                                if j == 0:
                                    Gcar = td[j].get("data-endpoint")
                                    data_one.append(Gcar)
                                elif j == 1:
                                    Gtm = td[j].get("data-endpoint")
                                    data_one.append(Gtm)
                                elif j == 2:
                                    time = td[j].get("csk").split(".")[0]
                                    data_one.append(time)
                                else:
                                    data = td[j].text
                                    data_one.append(data)
                            data_hfpitcher.append(data_one)
                            print(f"{game_time} {home_name} successful!!")
            df_hfpitcher = pd.DataFrame(data_hfpitcher)
            df_hfpitcher.index = data_all_n1.index
            df_hfpitcher.columns = col
            df_hfpitcher.columns = "Home_FPitching_" + df_hfpitcher.columns
            df_hfpitcher.drop(["Home_FPitching_DFS(DK)","Home_FPitching_DFS(FD)","Home_FPitching_Entered","Home_FPitching_Exited"],axis =1,inplace=True)
            print("*************************爬取 reference home先發數據 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取 reference home先發數據 fail!! ************************************")  
            sys.exit()
        browser.close()

        '''
        reference away先發本季數據
        '''
        print("*************************爬取 reference away先發本季數據 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_Gtm_a = []
            for i in range(len(df_afpitcher)):
                data_one = []
                browser.get(f"https://www.baseball-reference.com" + df_afpitcher["Away_FPitching_Box_Gtm"][i])
                soup = BeautifulSoup(browser.page_source,"lxml")
                name = soup.find("h2").text.split(" Cumulative")[0]
                data_one.append(name)
                win = soup.find("tbody").find("th").text
                data_one.append(win)
                td = soup.find("tbody").find_all("td")
                for t in range(len(td)):
                    data = td[t].text
                    data_one.append(data)
                data_Gtm_a.append(data_one)
                print(f"{name} successful!!")
            col = ["name","W","L","G","GS","CG","SHO","GF","SV","IP","H","R","ER","BB","SO","HR","ERA","HBP","WP","BK",
                   "Pit","Str","GSc","IR","IS","2B","3B","SB","CS"]
            data_Gtm_a = pd.DataFrame(data_Gtm_a,columns = col)
            data_Gtm_a.columns = "Away_Gtm_" + data_Gtm_a.columns
            data_Gtm_a.index = data_all_n1.index
            print("*************************爬取 reference away先發本季數據 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取 reference away先發本季數據 fail!! ************************************")  
            sys.exit()
        browser.close()

        '''
        reference home先發本季數據
        '''
        print("*************************爬取reference home先發本季數據 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_Gtm_h = []
            for i in range(len(df_hfpitcher)):
                data_one = []
                browser.get(f"https://www.baseball-reference.com" + df_hfpitcher["Home_FPitching_Box_Gtm"][i])
                soup = BeautifulSoup(browser.page_source,"lxml")
                name = soup.find("h2").text.split(" Cumulative")[0]
                data_one.append(name)
                win = soup.find("tbody").find("th").text
                data_one.append(win)
                td = soup.find("tbody").find_all("td")
                for t in range(len(td)):
                    data = td[t].text
                    data_one.append(data)
                data_Gtm_h.append(data_one)
                print(f"{name} successful!!")
            col = ["name","W","L","G","GS","CG","SHO","GF","SV","IP","H","R","ER","BB","SO","HR","ERA","HBP","WP","BK",
                   "Pit","Str","GSc","IR","IS","2B","3B","SB","CS"]
            data_Gtm_h = pd.DataFrame(data_Gtm_h,columns = col)
            data_Gtm_h.columns = "Home_Gtm_" + data_Gtm_h.columns
            data_Gtm_h.index = data_all_n1.index
            print("*************************爬取 reference home先發本季數據 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取 reference home先發本季數據 fail!! ************************************")  
            sys.exit()
        browser.close()

        '''
        reference away先發歷年數據
        '''
        print("*************************爬取reference away先發歷年數據 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_Gcar_a = []
            for i in range(len(df_afpitcher)):
                data_one = []
                browser.get(f"https://www.baseball-reference.com" + df_afpitcher["Away_FPitching_Box_Gcar"][i])
                soup = BeautifulSoup(browser.page_source,"lxml")
                name = soup.find("h2").text.split(" Cumulative")[0]
                data_one.append(name)
                win = soup.find("tbody").find("th").text
                data_one.append(win)
                td = soup.find("tbody").find_all("td")
                for t in range(len(td)):
                    data = td[t].text
                    data_one.append(data)
                data_Gcar_a.append(data_one)
                print(f"{name} successful!!")
            col = ["name","W","L","G","GS","CG","SHO","GF","SV","IP","H","R","ER","BB","SO","HR","ERA","HBP","WP","BK"]
            data_Gcar_a = pd.DataFrame(data_Gcar_a,columns = col)
            data_Gcar_a.columns = "Away_Gcar_" + data_Gcar_a.columns
            data_Gcar_a.index = data_all_n1.index
            print("*************************爬取 reference away先發歷年數據 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取 reference away先發歷年數據 fail!! ************************************") 
            sys.exit()
        browser.close()

        '''
        reference home先發歷年數據
        '''
        print("*************************爬取reference home先發歷年數據 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_Gcar_h = []
            for i in range(len(df_hfpitcher)):
                data_one = []
                browser.get(f"https://www.baseball-reference.com" + df_hfpitcher["Home_FPitching_Box_Gcar"][i])
                soup = BeautifulSoup(browser.page_source,"lxml")
                name = soup.find("h2").text.split(" Cumulative")[0]
                data_one.append(name)
                win = soup.find("tbody").find("th").text
                data_one.append(win)
                td = soup.find("tbody").find_all("td")
                for t in range(len(td)):
                    data = td[t].text
                    data_one.append(data)
                data_Gcar_h.append(data_one)
                print(f"{name} successful!!")
            col = ["name","W","L","G","GS","CG","SHO","GF","SV","IP","H","R","ER","BB","SO","HR","ERA","HBP","WP","BK"]
            data_Gcar_h = pd.DataFrame(data_Gcar_h,columns = col)
            data_Gcar_h.columns = "home_Gcar_" + data_Gcar_h.columns
            data_Gcar_h.index = data_all_n1.index
            print("*************************爬取 reference home先發歷年數據 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            printint("*************************爬取 reference home先發歷年數據 fail!! ************************************")  
            sys.exit()
        browser.close()

        '''
        merge
        '''
        print("*************************數據merge start!! ************************************")
        try:
            data_Gcar_a_1 = data_Gcar_a[data_Gcar_a.columns[1:]]
            data_Gcar_h_1 = data_Gcar_h[data_Gcar_h.columns[1:]]
            data_Gtm_a_1 = data_Gtm_a[data_Gtm_a.columns[1:]]
            data_Gtm_h_1 = data_Gtm_h[data_Gtm_h.columns[1:]]
            df_feature = pd.concat([data_Gcar_a_1,data_Gcar_h_1,data_Gtm_a_1,data_Gtm_h_1],axis = 1)
            data_all_n2 = pd.concat([data_all_n1,df_feature],axis = 1)
            data_all_n2["主隊"]  = data_all_n2["主隊"].replace(name)
            data_all_n2["客隊"]  = data_all_n2["客隊"].replace(name)
            w_all = []
            for i in range(len(data_all_n2)):
                if data_all_n2["主隊得分"][i] < data_all_n2["客隊得分"][i]:
                    w = 0
                else:
                    w = 1
                w_all.append(w)
            data_all_n2["W/L"] = w_all
            data_all_n2["客隊"]  = data_all_n2["客隊"].replace(self.name)
            data_all_n2["主隊"]  = data_all_n2["主隊"].replace(self.name)
            print("*************************數據merge successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************數據merge fail!! ************************************") 
            sys.exit()
        return data_all_n2
    
    def titan_sch(self):
        '''
        爬取球探網賽程
        '''
        print("*************************爬取 球探網賽程 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_sch_all = []
            date = (self.date + datetime.timedelta(days=1))
            date_start = (self.date - datetime.timedelta(days=4)).strftime("%Y-%m-%d")
            if date.day <= 3:
                for i in [date.month-1,date.month]:
                    browser.get(f"http://sports.titan007.com/big/infoData/baseball/Normal.aspx?y=2022&m={i}&matchSeason=2022&SclassID=1")
                    soup = BeautifulSoup(browser.page_source,"lxml")
                    tr = soup.find("table",{"id":"scheTab"}).find_all("tr")
                    for t in range(1,len(tr)):
                        td = tr[t].find_all("td")
                        if len(td) == 8:
                            date_game = "2022" + td[1].text
                            dateFormatter = "%Y%m-%d%H:%M"
                            MatchTime = datetime.datetime.strptime(date_game,dateFormatter).strftime("%Y-%m-%d")
                            if MatchTime <= self.date.strftime("%Y-%m-%d") and MatchTime > date_start:
                                home = tr[t].find_all("td")[2].text
                                away = tr[t].find_all("td")[4].text
                                evencode = re.sub("\D","",tr[t].find_all("td")[7].find("a").get("href"))
                                data_sch_one = {
                                    "Date" : MatchTime,
                                    "主隊" : home,
                                    "客隊" : away,
                                    "Evencode_odd" : evencode
                                }
                                data_sch_all.append(data_sch_one)
                                print(f"{str(MatchTime)} {home} vs {away} successful!!")
            else:
                browser.get(f"http://sports.titan007.com/big/infoData/baseball/Normal.aspx?y=2022&m={self.date.month}&matchSeason=2022&SclassID=1")
                soup = BeautifulSoup(browser.page_source,"lxml")
                tr = soup.find("table",{"id":"scheTab"}).find_all("tr")
                for t in range(1,len(tr)):
                    td = tr[t].find_all("td")
                    if len(td) == 8:
                        date_game = "2022" + td[1].text
                        dateFormatter = "%Y%m-%d%H:%M"
                        MatchTime = datetime.datetime.strptime(date_game,dateFormatter).strftime("%Y-%m-%d")
                        if MatchTime <= self.date.strftime("%Y-%m-%d") and MatchTime > date_start:
                            home = tr[t].find_all("td")[2].text
                            away = tr[t].find_all("td")[4].text
                            evencode = re.sub("\D","",tr[t].find_all("td")[7].find("a").get("href"))
                            data_sch_one = {
                                "Date" : MatchTime,
                                "主隊" : home,
                                "客隊" : away,
                                "Evencode_odd" : evencode
                            }
                            data_sch_all.append(data_sch_one)
                            print(f"{str(MatchTime)} {home} vs {away} successful!!")
            df_sch_all = pd.DataFrame(data_sch_all)
            df_sch_all.index = df_sch_all["Date"]
            df_sch_all.drop(["Date"],axis = 1,inplace=True)
            df_sch_all.index = pd.to_datetime(df_sch_all.index)
            df_sch_all.index = df_sch_all.index - datetime.timedelta(days=1)
            print("*************************爬取 球探網賽程 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取 球探網賽程 fail!! ************************************")  
        browser.close()
        return df_sch_all
    
    def titan_odds(self,df_sch_all):
        '''
        爬取球探網賠率
        '''
        print("*************************爬取 賠率 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_all = []
            for i in range(len(df_sch_all)): 
                browser.get("http://sports.titan007.com/oddslist/baseball/" + str(df_sch_all["Evencode_odd"][i]) + ".htm")
                #sleep(1)
                soup = BeautifulSoup(browser.page_source,"lxml")
                if str(soup.find_all("tbody")) != '[]' and len(soup.find_all("tbody")) >= 5:
                    tr = soup.find_all("tbody")[4].find_all("tr")
                    for t in range(len(tr)):
                        td = tr[t].find_all("td")
                        if "初盘平均值" in td[0].text:
                            home_win_first = td[1].text
                            away_win_first = td[2].text
                            home_win_rate_first = td[3].text[:-1]
                            away_win_rate_first = td[4].text[:-1]
                            payout_first = td[5].text[:-1]
                            td_last = tr[t+1].find_all("td")
                            if td_last[0].text == "即时平均值":
                                home_win_last = td_last[1].text
                                away_win_last = td_last[2].text
                                home_win_rate_last = td_last[3].text[:-1]
                                away_win_rate_last = td_last[4].text[:-1]
                                payout_last = td_last[5].text[:-1]
                            else:
                                home_win_last = home_win_first
                                away_win_last = away_win_first
                                home_win_rate_last = home_win_rate_first
                                away_win_rate_last = away_win_rate_first
                                payout_last = payout_first
                            data_one = {
                                "Date" : df_sch_all.index[i],
                                "主隊" : df_sch_all["主隊"][i],
                                "客隊" :  df_sch_all["客隊"][i],
                                "Evencode_odd" : df_sch_all["Evencode_odd"][i],
                                "主勝(初)" : home_win_first,
                                "客勝(初)" : away_win_first,
                                "主勝率(初)" : home_win_rate_first,
                                "客勝率(初)" : away_win_rate_first,
                                "返還率(初)" : payout_first,
                                "主勝(終)" : home_win_last,
                                "客勝(終)" : away_win_last,
                                "主勝率(終)" : home_win_rate_last,
                                "客勝率(終)" : away_win_rate_last,
                                "返還率(終)" : payout_last,
                            }
                            data_all.append(data_one)
                            print(f'{df_sch_all.index[i]} {df_sch_all["主隊"][i]} vs {df_sch_all["客隊"][i]} 主勝(初): {home_win_first} 主勝(終): {home_win_last} successful!!')
                else:
                    data_one = {
                                "Date" : df_sch_all.index[i],
                                "主隊" : df_sch_all["主隊"][i],
                                "客隊" :  df_sch_all["客隊"][i],
                                "Evencode_odd" : df_sch_all["Evencode_odd"][i],
                                "主勝(初)" : "",
                                "客勝(初)" : "",
                                "主勝率(初)" : "",
                                "客勝率(初)" : "",
                                "返還率(初)" : "",
                                "主勝(終)" : "",
                                "客勝(終)" : "",
                                "主勝率(終)" : "",
                                "客勝率(終)" : "",
                                "返還率(終)" : "",
                            }
                    data_all.append(data_one)
                    print(f'{df_sch_all.index[i]} {df_sch_all["主隊"][i]} vs {df_sch_all["客隊"][i]} 沒資料!!')
            df_odd_all = pd.DataFrame(data_all)
            df_odd_all.index = df_odd_all["Date"]
            df_odd_all.drop(["Date"],axis = 1,inplace=True)
            df_odd = pd.merge(df_sch_all,df_odd_all,on=["Date","主隊","客隊","Evencode_odd"])
            df_odd = df_odd[df_odd["主勝(初)"] != '']
            df_odd1 = df_odd[df_odd.columns[3:]].astype("float")
            df_odd["客勝率(初)"] = df_odd1["主勝(初)"] / (df_odd1["主勝(初)"] + df_odd1["客勝(初)"])
            df_odd["主勝率(初)"] = df_odd1["客勝(初)"] / (df_odd1["主勝(初)"] + df_odd1["客勝(初)"])
            df_odd["客勝率(終)"] = df_odd1["主勝(終)"] / (df_odd1["主勝(終)"] + df_odd1["客勝(終)"])
            df_odd["主勝率(終)"] = df_odd1["客勝(終)"] / (df_odd1["主勝(終)"] + df_odd1["客勝(終)"])
            print("*************************爬取 賠率 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取 賠率 fail!! ************************************")  
        browser.close()
        return df_odd
    
    def titan_rate(self,df_odd):
        '''
        爬取球探網近10場勝率
        '''
        print("*************************爬取 近10場勝率 start!! ************************************")
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            data_all = []
            for i in range(len(df_odd)):
                date = df_odd.index[i]
                evencode = df_odd["Evencode_odd"][i]
                browser.get(f"http://sports.titan007.com/analysis/baseball/{evencode}cn.htm")
                sleep(1)
                soup = BeautifulSoup(browser.page_source,"lxml")
                if soup.text != "":
                    both_rate = float(soup.find("td",{"colspan":"13"}).find_all("font")[2].text.replace("%",""))
                    home_rate =float( soup.find_all("td",{"colspan":"9"})[0].find_all("font")[1].text.replace("%",""))
                    away_rate = float(soup.find_all("td",{"colspan":"9"})[1].find_all("font")[1].text.replace("%",""))
                    data_one = {
                        "Date" : date,
                        "Evencode_odd" : evencode,
                        "雙方對戰(主隊)" : both_rate,
                        "雙方對戰(客隊)" : 100 - both_rate,
                        "主隊勝率" : home_rate,
                        "客隊勝率" : away_rate,
                    }
                    data_all.append(data_one)
                    print(f"{date} {evencode} successful!!")
                df_a = pd.DataFrame(data_all)
                df_a.index = df_a["Date"]
                df_a.drop(["Date"],axis=1,inplace=True)
                df_all = pd.merge(df_odd,df_a,on=["Date","Evencode_odd"])
                columns = []
                for i in  df_all.columns:
                    if "away" in i:
                        s = i.replace("away","Away")
                    elif "home" in i:
                        s = i.replace("home","Home")
                    else:
                        s = i
                    columns.append(s)
            df_all.columns = columns
            df_all["主隊"]  = df_all["主隊"].replace(self.name_2)
            df_all["客隊"]  = df_all["客隊"].replace(self.name_2)
            print("*************************爬取 近10場勝率 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************爬取 近10場勝率 fail!! ************************************")  
        browser.close()
        return df_all
    
    def ELO(self,df_all_n,df_all):
        '''
        計算ELO
        '''
        print("*************************計算ELO start!! ************************************")
        try:
            df_n = pd.read_excel(self.path + "2022_feature.xlsx",index_col="Date")
            date_start = (self.date - datetime.timedelta(days=4)).strftime("%Y-%m-%d")
            df_n = df_n[df_n.index < date_start]
            elo_new = df_n.append(df_all_n)
            tf = open(self.path + "ELO.npy", "r")
            ELO_first = json.load(tf)
            ELO_all = []
            for i in range(len(elo_new)):
                away_team = elo_new["客隊"][i]
                home_team = elo_new["主隊"][i]
                y = elo_new.index[i]
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
                Sa = elo_new["W/L"][i]
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
                print(f"{elo_new.index[i]} {away_team} vs {home_team} 結果為 客隊:{round(ELO_first[away_team],4)} 主隊:{round(ELO_first[home_team],4)}")
            df_elo = pd.DataFrame(ELO_all)
            df_elo.index = elo_new.index
            elo_new["主隊ELO"] = df_elo["主隊ELO"]
            elo_new["客隊ELO"] = df_elo["客隊ELO"]
            print("*************************計算ELO successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************計算ELO fail!! ************************************")  
            sys.exit()
        df_all_now = df_all[df_all.index == self.date.strftime("%Y-%m-%d")]
        ELO_home = []
        ELO_away = []
        for i in range(len(df_all_now)):
            ELO_h = ELO_first[df_all_now["主隊"][i]]
            ELO_a = ELO_first[df_all_now["客隊"][i]]
            ELO_home.append(ELO_h)
            ELO_away.append(ELO_a)
        df_all_now["主隊ELO"] = ELO_home
        df_all_now["客隊ELO"] = ELO_away
        df_all_now = df_all_now.dropna()
        print(df_all_now)
        return df_all_now,elo_new
    
    def updata_reference(self,elo_new):
        '''
        更新數據
        '''
        print("*************************更新最新各球隊數據 start!! ************************************")
        try:
            team_name = ["STL","CHC","SFG","ARI","PIT","CIN","MIN","DET","CLE","HOU","CHW","KCR","SDP","LAD","ATL","MIA","COL","MIL","TOR",
              "NYY","TEX","OAK","BOS","PHI","LAA","SEA","BAL","TBR","NYM","WSN"]
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            browser = webdriver.Chrome(options=options)
            for team in team_name:
                browser.get(f"https://www.baseball-reference.com/teams/{team}/{self.date.year}-schedule-scores.shtml")
                soup = BeautifulSoup(browser.page_source,"lxml")
                tr = soup.find("table",{"id":"team_schedule"}).find("tbody").find_all("tr")
                data_team_all = []
                for t in range(len(tr)):
                    td = tr[t].find_all("td")
                    if td != []:
                        matchtime = td[0].get("csk")
                        if matchtime <= (self.date-datetime.timedelta(days=1)).strftime("%Y-%m-%d"):
                            evenhref = td[1].find("a").get("href")
                            team = td[2].text
                            h_v = td[3].text
                            away = td[4].text
                            w_l = td[5].text
                            w_l_count = td[9].text
                            win_pitcher = td[12].text
                            loss_pitcher = td[13].text
                            save_pitcher = td[14].text
                            streak = len(td[19].text)
                            if td[19].text[0] == "-":
                                streak = int("-" + str(streak))
                            data_team_one = {
                                "Date" : matchtime,
                                "box" : evenhref,
                                "Tm" : team,
                                "V/H" : h_v,
                                "Opp" : away,
                                "W/L" : w_l,
                                "W-L" : w_l_count,
                                "Win" : win_pitcher,
                                "Loss" : loss_pitcher,
                                "Save" : save_pitcher,
                                "Streak" : streak
                            }
                            data_team_all.append(data_team_one)
                        else:
                            break
                teamdata = pd.DataFrame(data_team_all)
                teamdata.to_excel(self.path + team + str(self.date.year) + " schedule.xlsx",index = False)
                print(f"{team} successful!!")
            print("*************************更新最新各球隊數據 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************更新最新各球隊數據 fail!! ************************************")  
            sys.exit()
        browser.close()
        
        print("*************************更新今年勝率 start!! ************************************")
        try:
            df_all_a = []
            df_all_h = []
            for i in range(len(elo_new)):
                date = elo_new.index[i]
                evencode = elo_new["Evencode"][i]
                away_team = elo_new["客隊"][i]
                home_team = elo_new["主隊"][i]
                #客隊
                wl_a = pd.read_excel(f"{self.path}{away_team}2022 schedule.xlsx",index_col="Date")
                a_match = wl_a[wl_a["box"] == evencode]
                if  "W" in a_match["W/L"][0]:
                    w = int(a_match["W-L"][0].split("-")[0]) - 1
                    l = int(a_match["W-L"][0].split("-")[1])
                else:
                    w = int(a_match["W-L"][0].split("-")[0])
                    l = int(a_match["W-L"][0].split("-")[1]) - 1
                if (w+l) == 0:
                    match_wl_a = 0
                    df_all_a.append(match_wl_a)
                else:
                    match_wl_a = w / (w+l)
                    df_all_a.append(match_wl_a)
                #主隊
                wl_h = pd.read_excel(f"{self.path}{home_team}2022 schedule.xlsx",index_col="Date")
                h_match = wl_h[wl_h["box"] == evencode]
                if  "W" in h_match["W/L"][0]:
                    w = int(h_match["W-L"][0].split("-")[0]) - 1
                    l = int(h_match["W-L"][0].split("-")[1])
                else:
                    w = int(h_match["W-L"][0].split("-")[0])
                    l = int(h_match["W-L"][0].split("-")[1]) - 1
                if (w+l) == 0:
                    match_wl_h = 0
                    df_all_h.append(match_wl_h)
                else:
                    match_wl_h = w / (w+l)
                    df_all_h.append(match_wl_h)
            elo_new["Away_W-L"] = df_all_a
            elo_new["Home_W-L"] = df_all_h
            elo_new.to_excel(self.path + "2022_feature.xlsx")
            elo_new = pd.read_excel(self.path + "2022_feature.xlsx",index_col="Date")
            print("*************************更新今年勝率 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************更新今年勝率 fail!! ************************************")  
            sys.exit()
        return elo_new
    
    def updata_rate_last(self,df_all_now):
        '''
        更新最新賽事勝率
        '''
        print("*************************更新最新勝率 start!! ************************************")
        try:
            df_all_a = []
            df_all_h = []
            for i in range(len(df_all_now)):
                date = df_all_now.index[i]
                #evencode = elo_new1["Evencode"][i]
                away_team = df_all_now["客隊"][i]
                home_team = df_all_now["主隊"][i]
                #客隊
                wl_a = pd.read_excel(f"{self.path}{away_team}2022 schedule.xlsx",index_col="Date")
                #a_match = wl_a[wl_a["box"] == evencode]
                a_match = wl_a.iloc[-1]
                w = int(a_match["W-L"].split("-")[0])
                l = int(a_match["W-L"].split("-")[1])
                if (w+l) == 0:
                    match_wl_a = 0
                    df_all_a.append(match_wl_a)
                else:
                    match_wl_a = w / (w+l)
                    df_all_a.append(match_wl_a)
                #主隊
                wl_h = pd.read_excel(f"{self.path}{home_team}2022 schedule.xlsx",index_col="Date")
                #h_match = wl_h[wl_h["box"] == evencode]
                h_match = wl_h.iloc[-1]
                w = int(h_match["W-L"].split("-")[0])
                l = int(h_match["W-L"].split("-")[1])
                if (w+l) == 0:
                    match_wl_h = 0
                    df_all_h.append(match_wl_h)
                else:
                    match_wl_h = w / (w+l)
                    df_all_h.append(match_wl_h)
            df_all_now["Away_W-L"] = df_all_a
            df_all_now["Home_W-L"] = df_all_h
            print("*************************更新最新勝率 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************更新最新勝率 fail!! ************************************")  
            sys.exit()
        return  df_all_now
    
    def calculate_sum_avg(self,df_all_now):
        print("*************************計算特徵值加總與平均 start!! ************************************")
        try:
            data_all_n2 = pd.read_excel(self.path + "2022_feature.xlsx",index_col="Date")
            df_before = pd.read_excel(self.path + "add_odd.xlsx",index_col="Date")
            columns = []
            for i in  df_before.columns:
                if "away" in i:
                    s = i.replace("away","Away")
                elif "home" in i:
                    s = i.replace("home","Home")
                else:
                    s = i
                columns.append(s)
            df_before.columns = columns
            columns = []
            for i in  data_all_n2.columns:
                if "away" in i:
                    s = i.replace("away","Away")
                elif "home" in i:
                    s = i.replace("home","Home")
                else:
                    s = i
                columns.append(s)
            data_all_n2.columns = columns
            df_all_data = df_before.append(data_all_n2)
            df_1 = df_all_data.drop(["Away_Batting_WPA-","Away_Batting_cWPA","Home_Batting_WPA-","Home_Batting_cWPA","Away_Pitching_cWPA","Home_Pitching_cWPA","Away_W-L","Home_W-L",'主勝(初)', '客勝(初)', '主勝率(初)',
           '客勝率(初)', '返還率(初)', '主勝(終)', '客勝(終)', '主勝率(終)', '客勝率(終)', '返還率(終)',"Away_Gcar_name","Away_Gtm_name","Home_Gcar_name","Home_Gtm_name",
            'W/L','主隊ELO', '客隊ELO',"Home_Gtm_IR","Home_Gtm_IS"],axis = 1)
            df_11 = df_1[str(self.date.year-1):str(self.date.year)]
            away_col = df_11.columns[5:25].append(df_11.columns[45:70]).append(df_11.columns[95:142])
            home_col = df_11.columns[25:45].append(df_11.columns[70:95]).append(df_11.columns[142:187])
            w_all = []
            #客對加總
            for i in range(len(df_all_now)):
                date = df_all_now.index[i]
                away = df_all_now["客隊"][i]
                wh_a = df_11[(df_11["客隊"] == away) | (df_11["主隊"] == away)]
                wh_aa = wh_a[wh_a["客隊"] == away][away_col]
                wh_aa = wh_aa.fillna(0)
                wh_aa = wh_aa.replace("",0)
                wh_aa = wh_aa.astype("float")
                wh_aa_bn = wh_aa[str(date.year-1):str(date.year)]
                wh_aa_b = wh_aa_bn[wh_aa_bn.index < date]
                wh_aa_sum  =wh_aa_b.sum()
                w_aa_len = len(wh_aa_b)
                col_all = []
                for c in wh_aa_sum.index:
                    col_a = c.replace("Away_","").replace("away_","")
                    col_all.append(col_a)
                wh_aa_sum.index = col_all
                wh_h = df_11[(df_11["客隊"] == away) | (df_11["主隊"] == away)]
                wh_ah = wh_h[wh_h["主隊"] == away][home_col]
                wh_ah = wh_ah.fillna(0)
                wh_ah = wh_ah.replace("",0)
                wh_ah = wh_ah.astype("float")
                wh_ah_bn = wh_ah[str(date.year-1):str(date.year)]
                wh_ah_b = wh_ah_bn[wh_ah_bn.index < date]
                wh_ah_sum  =wh_ah_b.sum()
                w_ah_len = len(wh_ah_b)
                col_all = []
                for c in wh_ah_sum.index:
                    col_h = c.replace("Home_","").replace("home_","")
                    col_all.append(col_h)
                wh_ah_sum.index = col_all
                w_one = (wh_aa_sum + wh_ah_sum)
                w_all.append(w_one)
            df_a = pd.DataFrame(w_all)
            col_all = []
            for c in df_a.columns:
                col_a = "Away_" + c
                col_all.append(col_a)
            df_a.columns = col_all
            df_a.index = df_all_now.index
            df_a["客隊"] = df_all_now["客隊"]
            #df_a["客隊得分"] = df_all["客隊得分"]
            df_a["主隊"] = df_all_now["主隊"]
            #df_a["主隊得分"] = df_all["主隊得分"]
            df_a["Evencode_odd"] = df_all_now["Evencode_odd"]

            #主隊加總
            w_all_h = []
            for i in range(len(df_all_now)):
                date = df_all_now.index[i]
                away = df_all_now["主隊"][i]
                wh_a = df_11[(df_11["客隊"] == away) | (df_11["主隊"] == away)]
                wh_aa = wh_a[wh_a["客隊"] == away][away_col]
                wh_aa = wh_aa.fillna(0)
                wh_aa = wh_aa.replace("",0)
                wh_aa = wh_aa.astype("float")
                wh_aa_bn = wh_aa[str(date.year-1):str(date.year)]
                wh_aa_b = wh_aa_bn[wh_aa_bn.index < date]
                wh_aa_sum  =wh_aa_b.sum()
                w_aa_len = len(wh_aa_b)
                col_all = []
                for c in wh_aa_sum.index:
                    col_a = c.replace("Away_","").replace("away_","")
                    col_all.append(col_a)
                wh_aa_sum.index = col_all
                wh_h = df_11[(df_11["客隊"] == away) | (df_11["主隊"] == away)]
                wh_ah = wh_h[wh_h["主隊"] == away][home_col]
                wh_ah = wh_ah.fillna(0)
                wh_ah = wh_ah.replace("",0)
                wh_ah = wh_ah.astype("float")
                wh_ah_bn = wh_ah[str(date.year-1):str(date.year)]
                wh_ah_b = wh_ah_bn[wh_ah_bn.index < date]
                wh_ah_sum  =wh_ah_b.sum()
                w_ah_len = len(wh_ah_b)
                col_all = []
                for c in wh_ah_sum.index:
                    col_h = c.replace("Home_","").replace("home_","")
                    col_all.append(col_h)
                wh_ah_sum.index = col_all
                w_one = (wh_aa_sum + wh_ah_sum) 
                w_all_h.append(w_one)
            df_h = pd.DataFrame(w_all_h)
            col_all = []
            for c in df_h.columns:
                col_a = "Home_" + c
                col_all.append(col_a)
            df_h.columns = col_all
            df_h.index = df_all_now.index
            df_h["客隊"] = df_all_now["客隊"]
            #df_h["客隊得分"] = df_11["客隊得分"]
            df_h["主隊"] = df_all_now["主隊"]
            #df_h["主隊得分"] = df_11["主隊得分"]
            df_h["Evencode_odd"] = df_all_now["Evencode_odd"] 

            df_2 = df_all_data[["客隊","客隊得分","主隊","主隊得分","Evencode","Away_Batting_WPA-","Away_Batting_cWPA","Home_Batting_WPA-","Home_Batting_cWPA","Away_Pitching_cWPA","Home_Pitching_cWPA"]]
            df_22 = df_2[str(self.date.year-1):str(self.date.year)]
            col = ["Away_Batting_WPA-","Away_Batting_cWPA","Home_Batting_WPA-","Home_Batting_cWPA","Away_Pitching_cWPA","Home_Pitching_cWPA"]
            for i in col:
                df_22[i] = df_22[i].apply(lambda x:str(x).replace("%","")).astype("float")
            away_col = df_22.columns[5:7].append(df_22.columns[9:10])
            home_col = df_22.columns[7:9].append(df_22.columns[10:11])
            #客隊平均
            w_all_av = []
            for i in range(len(df_all_now)):
                date = df_all_now.index[i]
                away = df_all_now["客隊"][i]
                wh_a = df_22[(df_22["客隊"] == away) | (df_22["主隊"] == away)]
                wh_aa = wh_a[wh_a["客隊"] == away][away_col]
                wh_aa = wh_aa.fillna(0)
                wh_aa = wh_aa.replace("",0)
                wh_aa = wh_aa.astype("float")
                wh_aa_bn = wh_aa[str(date.year-1):str(date.year)]
                wh_aa_b = wh_aa_bn[wh_aa_bn.index < date]
                wh_aa_sum  =wh_aa_b.mean()
                w_aa_len = len(wh_aa_b)
                col_all = []
                for c in wh_aa_sum.index:
                    col_a = c.replace("Away_","").replace("away_","")
                    col_all.append(col_a)
                wh_aa_sum.index = col_all
                wh_h = df_22[(df_22["客隊"] == away) | (df_22["主隊"] == away)]
                wh_ah = wh_h[wh_h["主隊"] == away][home_col]
                wh_ah = wh_ah.fillna(0)
                wh_ah = wh_ah.replace("",0)
                wh_ah = wh_ah.astype("float")
                wh_ah_bn = wh_ah[str(date.year-1):str(date.year)]
                wh_ah_b = wh_ah_bn[wh_ah_bn.index < date]
                wh_ah_sum  =wh_ah_b.mean()
                w_ah_len = len(wh_ah_b)
                col_all = []
                for c in wh_ah_sum.index:
                    col_h = c.replace("Home_","").replace("home_","")
                    col_all.append(col_h)
                wh_ah_sum.index = col_all
                w_one = (wh_aa_sum + wh_ah_sum)/2
                w_all_av.append(w_one)
            df_av= pd.DataFrame(w_all_av)
            col_all = []
            for c in df_av.columns:
                col_a = "Away_" + c
                col_all.append(col_a)
            df_av.columns = col_all
            df_av.index = df_all_now.index
            df_av["客隊"] = df_all_now["客隊"]
            #df_av["客隊得分"] = df_22["客隊得分"]
            df_av["主隊"] = df_all_now["主隊"]
            #df_av["主隊得分"] = df_22["主隊得分"]
            df_av["Evencode_odd"] = df_all_now["Evencode_odd"]
            df_a_all = pd.merge(df_a,df_av,on=["Date","客隊","主隊","Evencode_odd"])

            #主隊平均
            w_all_h_av = []
            for i in range(len(df_all_now)):
                date = df_all_now.index[i]
                away = df_all_now["主隊"][i]
                wh_a = df_22[(df_22["客隊"] == away) | (df_22["主隊"] == away)]
                wh_aa = wh_a[wh_a["客隊"] == away][away_col]
                wh_aa = wh_aa.fillna(0)
                wh_aa = wh_aa.replace("",0)
                wh_aa = wh_aa.astype("float")
                wh_aa_bn = wh_aa[str(date.year-1):str(date.year)]
                wh_aa_b = wh_aa_bn[wh_aa_bn.index < date]
                wh_aa_sum  =wh_aa_b.mean()
                w_aa_len = len(wh_aa_b)
                col_all = []
                for c in wh_aa_sum.index:
                    col_a = c.replace("Away_","").replace("away_","")
                    col_all.append(col_a)
                wh_aa_sum.index = col_all
                wh_h = df_22[(df_22["客隊"] == away) | (df_22["主隊"] == away)]
                wh_ah = wh_h[wh_h["主隊"] == away][home_col]
                wh_ah = wh_ah.fillna(0)
                wh_ah = wh_ah.replace("",0)
                wh_ah = wh_ah.astype("float")
                wh_ah_bn = wh_ah[str(date.year-1):str(date.year)]
                wh_ah_b = wh_ah_bn[wh_ah_bn.index < date]
                wh_ah_sum  =wh_ah_b.mean()
                w_ah_len = len(wh_ah_b)
                col_all = []
                for c in wh_ah_sum.index:
                    col_h = c.replace("Home_","").replace("home_","")
                    col_all.append(col_h)
                wh_ah_sum.index = col_all
                w_one = (wh_aa_sum + wh_ah_sum) /2
                w_all_h_av.append(w_one)
            df_h_av = pd.DataFrame(w_all_h_av)
            col_all = []
            for c in df_h_av.columns:
                col_a = "Home_" + c
                col_all.append(col_a)
            df_h_av.columns = col_all
            df_h_av.index = df_all_now.index
            df_h_av["客隊"] = df_all_now["客隊"]
            #df_h_av["客隊得分"] = df_22["客隊得分"]
            df_h_av["主隊"] = df_all_now["主隊"]
            #df_h_av["主隊得分"] = df_22["主隊得分"]
            df_h_av["Evencode_odd"] = df_all_now["Evencode_odd"]
            df_h_all = pd.merge(df_h,df_h_av,on=["Date","客隊","主隊","Evencode_odd"])
            df_be = pd.merge(df_a_all,df_h_all,on=["Date","主隊","客隊","Evencode_odd"])
            df_be_2022 = df_be[str(self.date.year)]
            df_be_2022["主隊"] = df_all_now["主隊"]
            df_be_2022["客隊"] = df_all_now["客隊"]
            df_be_2022["Evencode_odd"] = df_all_now["Evencode_odd"]
            df_all_f = pd.merge(df_be_2022,df_all_now,on=["Date","客隊","主隊","Evencode_odd"])
            df_all_f = df_all_f.drop(["客隊","主隊","Evencode_odd"],axis = 1)
            df_all_f = df_all_f.fillna(0)

            print("*************************計算特徵值加總與平均 successful!! ************************************")
        except Exception as e: 
            print(repr(e))
            print("*************************計算特徵值加總與平均 fail!! ************************************")  
            sys.exit()
        return df_all_f 
        
    def data_sub(self,df_all_f):
        '''
        主客隊數據相減
        '''
        print("*************************計算主客隊相減 start!! ************************************")
        away_c = []
        df_all_f = df_all_f.astype("float")
        for i in df_all_f.columns:
            if "Away" in i or "客" in i:
                away_c.append(i)
        df_a_data = df_all_f[away_c]
        print(df_a_f)
        col_all = []
        for i in range(0,103):
            col = df_a_data.columns[i].replace("Away_","").replace("away_","").replace("客","")
            col_all.append(col)
        df_a_data.columns = col_all
        home_c = []
        for i in df_all_f.columns:
            if "Home" in i or "主" in i:
                home_c.append(i)
        df_h_data = df_all_f[home_c]
        col_all = []
        for i in range(0,103):
            col = df_h_data.columns[i].replace("Home_","").replace("home_","").replace("主","")
            col_all.append(col)
        df_h_data.columns = col_all
        df_sub = df_h_data - df_a_data
        df_sub["返還率(差)"]= df_all_f['返還率(終)'] - df_all_f['返還率(初)']
        df_sub["主勝(差)"] = df_all_f['主勝(終)'] - df_all_f['主勝(初)']
        df_sub["客勝(差)"] = df_all_f['客勝(終)'] - df_all_f['客勝(初)']
        df_sub["主勝率(差)"] = df_all_f["主勝率(終)"] - df_all_f["主勝率(初)"]
        df_sub["客勝率(差)"] = df_all_f["客勝率(終)"] - df_all_f["客勝率(初)"]
        tf_all = []
        for i in range(len(df_sub)):
            tf = df_sub.index[i].strftime("%Y-%m-%d")  < str(df_sub.index[i].year) + "-08-31"
            tf_all.append(tf*1)
        df_sub["831"] = tf_all
        return df_sub
    
    def before_std(self,df_sub):
        '''
        計算模型的標準差
        '''
        df_sub_2022 = df_sub.copy()
        df_h = pd.read_excel(self.path + "feature_h.xlsx",index_col="Date")
        df_h_data = df_h.drop(["客隊","客隊得分","主隊","主隊得分","Evencode_odd","Evencode","W/L"],axis = 1)
        col_all = []
        for i in range(0,103):
            col = df_h_data.columns[i].replace("Home_","").replace("home_","").replace("主","")
            col_all.append(col)
        df_h_data.columns = col_all   
        df_a = pd.read_excel(self.path + "feature_a.xlsx",index_col="Date")
        df_a_data = df_a.drop(["客隊","客隊得分","主隊","主隊得分","Evencode_odd","Evencode","W/L"],axis = 1)
        col_all = []
        for i in range(0,103):
            col = df_a_data.columns[i].replace("Away_","").replace("away_","").replace("客","")
            col_all.append(col)
        df_a_data.columns = col_all
        df_sub = df_h_data - df_a_data
        df = pd.read_excel(self.path + "feature_odd_all.xlsx",index_col="Date")
        df_sub["返還率(差)"]= df['返還率(終)'] - df['返還率(初)']
        df_sub["主勝(差)"] = df['主勝(終)'] - df['主勝(初)']
        df_sub["客勝(差)"] = df['客勝(終)'] - df['客勝(初)']
        df_sub["主勝率(差)"] = df["主勝率(終)"] - df["主勝率(初)"]
        df_sub["客勝率(差)"] = df["客勝率(終)"] - df["客勝率(初)"]
        result = pd.read_excel(self.path + "feature_odd_all.xlsx",index_col="Date")
        result = result.dropna()
        result = result[["客隊","客隊得分","主隊","主隊得分","Evencode_odd","Evencode","主勝(初)","客勝(初)","主勝率(初)",
                         "客勝率(初)","返還率(初)","主勝(終)","客勝(終)","主勝率(終)","客勝率(終)","返還率(終)","W/L"]]
        df_x =df_sub.dropna()
        df_y = result.dropna()["W/L"]
        tf_all = []
        for i in range(len(df_x)):
            tf = df_x.index[i].strftime("%Y-%m-%d")  < str(df_x.index[i].year) + "-08-31"
            tf_all.append(tf*1)
        df_x["831"] = tf_all
        df_x_train = df_x[:"2021-01-01"]
        x_test = df_x["2021-01-01":]
        df_y_train = df_y[:"2021-01-01"]
        y_test = df_y["2021-01-01":]
        x_train, x_val, y_train, y_val = train_test_split(df_x_train, df_y_train, test_size = 0.3, random_state = 666)
        x_train_10 = x_train.copy() 
        scl = StandardScaler()
        x_train_sd = scl.fit_transform(x_train_10)
        df_sub = df_sub_2022[df_x_train.columns]
        x_2022_sd =  scl.transform(df_sub)
        return x_2022_sd
        
        
        
        
    def odd_win_lose(self):
        '''
        MLB賽事預測
        '''
        data_all_n = self.reference_sch()
        data_all_n1 = self.reference_boxscore(data_all_n)
        data_all_n2 = self.reference_data(data_all_n1)
        df_sch_all = self.titan_sch()
        df_odd = self.titan_odds(df_sch_all)
        df_all = self.titan_rate(df_odd)
        df_all_n = pd.merge(data_all_n2,df_all,on=["Date","主隊","客隊"])
        df_all_now,elo_new = self.ELO(df_all_n,df_all)
        elo_new = self.updata_reference(elo_new)
        df_all_now = self.updata_rate_last(df_all_now)
        df_all_f = self.calculate_sum_avg(df_all_now)
        df_sub = self.data_sub(df_all_f)
        x_2022_sd = self.before_std(df_sub)
        model = load_model(self.path + "mlb59_65%_add_2.h5")
        pre = (model.predict(x_2022_sd))
        #winwin666
        predlist = []
        for i in range(0,len(pre)):
            v = df_all_1["客隊"][i]
            h = df_all_1["主隊"][i]
            home_rate = df_all_f["主勝率(終)"][i]
            away_rate = df_all_f["客勝率(終)"][i]
            url = 'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/MLB/any'
            response = requests.get(url,verify=False,auth=HTTPBasicAuth('rick', 'rick000')).text
            j = json.loads(response)
            json_data = j['response']
            have_update = False
            for d in range(len(json_data)):
                team_name_v = json_data[d]["AwayTeam"][1]
                team_name_h = json_data[d]["HomeTeam"][1]
                odd = json_data[d]["odds"]
                if team_name_v == name_3[v] and team_name_h == name_3[h]  and "_" not in json_data[d]["EventCode"]:
                    if odd != []:
                        have_update = True
                        for o in range(len(odd)):
                            if odd[o]["GroupOptionCode"] == "20":
                                if odd[o]["OptionCode"] == '1':
                                    HomeOdds = odd[o]["OptionRate"]
                                elif odd[o]["OptionCode"] == '2':
                                    AwayOdds = odd[o]["OptionRate"]
                        EventCode = json_data[d]["EventCode"]
                        if  have_update == True:
                            if pre[i] > 0.6:
                                print(name_3[v] + " (LOSE) v.s " + name_3[h] + " (WIN)" )
                                OptionCode = "1"   
                            elif pre[i] < 0.4 :
                                print(name_3[v] + " (WIN) v.s " + name_3[h] + " (LOSE)" )
                                OptionCode = "2"
                            else:
                                print(name_3[v] + " v.s " + name_3[h] + "信性度不夠" )
                                continue
                            data = {'account':"winwin666",
                             'password':"adsads2323",
                             'GroupOptionCode':"20",
                             'OptionCode':OptionCode,
                             'EventCode':EventCode,
                             'predict_type':'Selling',
                             "HomeOdds":HomeOdds,
                             "AwayOdds":AwayOdds,
                             "HomeConfidence":str(int(round(pre[i][0] * 100,0))) + "%",
                             "AwayConfidence":str(int(round( (1 - pre[i][0]) * 100,0))) + "%",}
                            predlist.append(data)
                            print(data)
                    else:
                        print(name_3[v] + " v.s " + name_3[h] + "無賠率" )
        url = 'https://81f5-220-130-85-186.ngrok.io/UserMemberSellingPushMessage'
        json= {"SubscribeLevels":"free/gold/platinum",
                "predict_winrate":"70%",
                "title":"本季準確度:",
                "body_data":"2021賽季回測|20530|288過251|87.2",
                "TournamentText_icon":"https://upload.wikimedia.org/wikipedia/zh/thumb/2/2a/Major_League_Baseball.svg/1200px-Major_League_Baseball.svg.png",
                "body_image":"https://i.imgur.com/R3eCxgt.png",
                "predlist":predlist}
        response = requests.post(url, json = json, auth=HTTPBasicAuth('jake', '000jk'), verify=False).text
        print(response)
        #bestwin
        predlist = []
        for i in range(0,len(pre)):
            v = df_all_1["客隊"][i]
            h = df_all_1["主隊"][i]
            home_rate = df_all_f["主勝率(終)"][i]
            away_rate = df_all_f["客勝率(終)"][i]
            url = 'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/MLB/any'
            response = requests.get(url,verify=False,auth=HTTPBasicAuth('rick', 'rick000')).text
            j = json.loads(response)
            json_data = j['response']
            have_update = False
            for d in range(len(json_data)):
                team_name_v = json_data[d]["AwayTeam"][1]
                team_name_h = json_data[d]["HomeTeam"][1]
                odd = json_data[d]["odds"]
                if team_name_v == name_3[v] and team_name_h == name_3[h]  and "_" not in json_data[d]["EventCode"]:
                    if odd != []:
                        have_update = True
                        for o in range(len(odd)):
                            if odd[o]["GroupOptionCode"] == "20":
                                if odd[o]["OptionCode"] == '1':
                                    HomeOdds = odd[o]["OptionRate"]
                                elif odd[o]["OptionCode"] == '2':
                                    AwayOdds = odd[o]["OptionRate"]
                        EventCode = json_data[d]["EventCode"]
                        if  have_update == True:
                            if pre[i] > 0.5 and pre[i] > home_rate:
                                print(name_3[v] + " (LOSE) v.s " + name_3[h] + " (WIN)" )
                                OptionCode = "1"   
                            elif pre[i] < 0.5  and pre[i] < home_rate :
                                print(name_3[v] + " (WIN) v.s " + name_3[h] + " (LOSE)" )
                                OptionCode = "2"
                            else:
                                print(name_3[v] + " v.s " + name_3[h] + "信性度不夠" )
                                continue
                            url = "https://ecocoapidev1.southeastasia.cloudapp.azure.com/PredictMatchEntry/"
                            data = {'account':"bestwin",
                             'password':"adsads2323",
                             'GroupOptionCode':"20",
                             'OptionCode':OptionCode,
                             'EventCode':EventCode,
                             'PredictType':'Selling'}
                            print(data)
                            response_ = requests.post(url,verify=False, data = data, auth=HTTPBasicAuth('rick', 'rick000')).text
                            print(response_)
                        else:
                             print(name_3[v] + " v.s " + name_3[h] + " 無賽事" )
        #i945win
        for i in range(0,len(pre)):
            v = df_all_1["客隊"][i]
            h = df_all_1["主隊"][i]
            url = 'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/MLB/any'
            response = requests.get(url,verify=False,auth=HTTPBasicAuth('rick', 'rick000')).text
            j = json.loads(response)
            json_data = j['response']
            have_update = False
            for d in range(len(json_data)):
                team_name_v = json_data[d]["AwayTeam"][1]
                team_name_h = json_data[d]["HomeTeam"][1]
                if team_name_v == name_3[v] and team_name_h == name_3[h] and "_" not in json_data[d]["EventCode"]:
                    have_update = True
                    EventCode = json_data[d]["EventCode"]
            if  have_update== True:
                if pre[i] > 0.5:
                    print(name_3[v] + " (LOSE) v.s " + name_3[h] + " (WIN)" )
                    OptionCode = "1"   
                else :
                    print(name_3[v] + " (WIN) v.s " + name_3[h] + " (LOSE)" )
                    OptionCode = "2"
                url = "https://ecocoapidev1.southeastasia.cloudapp.azure.com/PredictMatchEntry/"
                data = {'account':"i945win",
                 'password':"adsads2323",
                 'GroupOptionCode':"20",
                 'OptionCode':OptionCode,
                 'EventCode':EventCode,
                 'PredictType':'Selling'}
                print(data)
                response_ = requests.post(url,verify=False, data = data, auth=HTTPBasicAuth('rick', 'rick000')).text
                print(response_)
            else:
                 print(name_3[v] + " v.s " + name_3[h] + " 無賽事" )
        
if __name__ == '__main__':
    MLBPredict = MLBPredict()
    MLBPredict.odd_win_lose() 


# In[ ]:




