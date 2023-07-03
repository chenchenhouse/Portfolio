#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
import datetime
import pymssql
import datetime
import email
import smtplib
from email.mime.text import MIMEText #導入MIMEText 類
from email.mime.multipart import MIMEMultipart   #導入MIMEMultipart類
from email.mime.image import MIMEImage    #導入MIMEImage類
from email.mime.base import MIMEBase   # MIME子類的基類
from email import encoders    #導入編碼器
import warnings

warnings.filterwarnings("ignore")

class MemberEmail(object):
    
    def __init__(self):
        self.server = 'gh.ecocoshiny.com'
        self.database = 'GoHit' 
        self.username = 'userLC' 
        self.password = '246246Winwin'
        
    
    def day_range(self,day=7):
        date = (datetime.datetime.now() - datetime.timedelta(days=day)).replace(hour = 0,minute = 0,second=0).strftime("%Y-%m-%d %H:%M:%S.000")
        return date
    
    def get_ConnectionFromDB(self):
        '''
        開啟DB
        '''
        db = pymssql.connect(self.server,self.username,self.password,self.database)
        self.cursor = db.cursor()
        
        
    def Member_profit(self,day):
        '''
        賽事虛擬獲利
        '''
        date = self.day_range(day)
        sql = f'''
            Select A.UserId,A.TournamentText,sum(case  B.Results when 'Y' then Profit else -1000 end) as profit,sum(case B.Results when 'Y' then 1 else 0 end) as win ,sum(case B.Results when 'Y' then 0 else 1 end) as LOS
            From PredictMatch  as A
            INNER join PredictResults AS B on B.Predict_id = A.id
            INNER join MatchEntry  AS C on A.EventCode = C.EventCode
            INNER join UserMember  AS D on A.UserId = D.UserId
            where C.MatchTime >= '{date}' AND gameType = 'Forecast' AND D.Email IS NOT NULL 
            Group by A.UserId,A.TournamentText
        '''
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        df_usermember = pd.DataFrame(results,columns = ["UserId","TournamentText","profit","win","lose"])
        win_rate = round((df_usermember["win"] / (df_usermember["win"] + df_usermember["lose"]))*100,2)
        win_rate = win_rate.astype("str") + "%"
        df_usermember["win rate"] = win_rate
        return df_usermember
    
    
    def Member_benefit(self,userid,game,day):
        '''
        個別賽事分潤
        '''
        date = self.day_range(day)
        sql =f'''
        SELECT A.Userid,SUM(CAST(A.benefit AS FLOAT)) AS Benefit,COUNT(A.from_UserId) AS SELL_COUNT,A.Game_id
        FROM [GoHit].[dbo].[UserBenefit_hit] AS A
        INNER join Games AS B on A.Game_id = B.id
        WHERE sell_datetime >= '{date}'  AND A.UserId = '{userid}' AND B.game = '{game}'
        GROUP BY A.Userid,A.Game_id
        '''
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if results != []:
            benefit = results[0][1]
            sell_count = results[0][2]
        else:
            benefit = 0
            sell_count = 0
        return benefit,sell_count

    
    def Member_thumbsup(self,userid,day):
        '''
        按讚數
        '''
        date = self.day_range(day)
        sql =f'''
        SELECT A.CreatedBy,COUNT(B.CreatedBy) AS thumbsup
        FROM Discussion as A
        FULL OUTER JOIN DiscussionFavorite AS B ON  A.Id = B.DiscussionId 
        WHERE A.IsActive = '1' AND (B.IsActive = '1' OR B.IsActive IS NULL) AND B.CreatedOn >= '{date}' AND B.CreatedBy = '{userid}'
        GROUP BY A.CreatedBy'''
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if results != []:
            thumbsup = results[0][1]
        else:
            thumbsup = 0
        return thumbsup
    
    def Member_name(self,userid):
        '''
        總G幣跟總分潤
        '''
        sql =f'''  
         SELECT A.UserId,A.member,A.Email,B.Money,C.Benefit
         FROM UserMember AS A
         FULL OUTER JOIN UserMoney AS B ON A.UserId = B.UserId
         FULL OUTER JOIN UserBenefit AS C ON A.UserId = C.UserId
         WHERE A.UserId =  '{userid}'
        '''
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        df_usermember = pd.DataFrame(results,columns = ["UserId","Member","Email","Money","Benefit"])
        if df_usermember["Money"][0] == None:
            df_usermember["Money"][0] = 0
        if df_usermember["Benefit"][0] == None:
            df_usermember["Benefit"][0] = 0    
        return df_usermember
    
    def send_email_Member(self,day=7):
        self.day = day
        self.get_ConnectionFromDB()
        #賽事虛擬獲利
        user_profit = self.Member_profit(day)

        #個別賽事分潤
        benefit_all = []
        sell_count_all = []
        thumbsup_all = []
        for user in range(len(user_profit)):
            userid = user_profit["UserId"].iloc[user]
            game =  user_profit["TournamentText"].iloc[user]
            benefit,sell_count = self.Member_benefit(userid,game,day)
            benefit_all.append(benefit)
            sell_count_all.append(sell_count)
        user_profit["benefit"] = benefit_all
        user_profit["sell_count"] = sell_count_all

        group_user = user_profit.groupby("UserId")
        have_email_user = group_user.sum().index
        for i in have_email_user:
            member = self.Member_name(i)
            user_id = member["UserId"].iloc[0]
            name = member["Member"].iloc[0]
            email_ = member["Email"].iloc[0]
            if name == "ccc":
                money = str(member["Money"].iloc[0])
                Benefit = member["Benefit"].iloc[0]
                member_profit = user_profit[user_profit["UserId"] == i]
                thumbsup = self.Member_thumbsup(i,day)  #按讚數
                member_data ={
                    "會員" : name,
                    "信箱" : email_,
                    "總G幣" : money,
                    "總分潤" : Benefit,
                    "被按讚數" : thumbsup
                } 
                game_all = {}
                for m in range(len(member_profit)):
                    tournament = member_profit["TournamentText"].iloc[m]
                    profit = str(member_profit["profit"].iloc[m])
                    count = str(member_profit["sell_count"].iloc[m])
                    win = member_profit["win"].iloc[m]
                    lose = member_profit["lose"].iloc[m]
                    win_rate = member_profit["win rate"].iloc[m]
                    benefit_one_game = member_profit["benefit"].iloc[m]
                    game_all.setdefault("賽事",[]).append(tournament)
                    game_all.setdefault("虛擬獲利",[]).append(profit)
                    game_all.setdefault("賣牌數",[]).append(count)
                    game_all.setdefault("準",[]).append(win)
                    game_all.setdefault("惜",[]).append(lose)
                    game_all.setdefault("勝率",[]).append(win_rate)
                    game_all.setdefault("單一賽事賣牌獲利",[]).append(benefit_one_game)
                member_all = {**member_data,**game_all}

                game_all = ""
                for p in range(len(member_all["賽事"])):
                    game = member_all["賽事"][p]
                    profit = member_all["虛擬獲利"][p]
                    s_count = member_all["賣牌數"][p]
                    win = member_all["準"][p]
                    lose = member_all["惜"][p]
                    win_rate = member_all["勝率"][p]
                    one_profit = member_all["單一賽事賣牌獲利"][p]
                    game_one = f'''<tr>
                    <td >{game}</td>
                    <td >{win_rate}</td>
                    <td >{win}-{lose}</td>
                    <td >{profit}</td>
                    <td >{s_count}</td>
                    <td >{one_profit}</td>
                    </tr>'''
                    game_all += game_one
                date_week = (datetime.datetime.now() - datetime.timedelta(days=day)).strftime("%Y-%m-%d")
                date_today = datetime.datetime.now().strftime("%Y-%m-%d")
                msg=email.message.EmailMessage()
                from_a="adsads023023@gmail.com"
                to_b="ring860112@gmail.com"
                msg["From"]=from_a
                msg["To"]=to_b
                msg["Subject"]="[GUESS365] 您的個人預測績效及買賣概況"
                with open(r"C:\Users\Guess365User\Desktop\EMAIL寄信\mail html\mail html\css\main.css", "r+", encoding='utf-8') as f:
                    text= f.read()
                    f.close()
                with open(r"C:\Users\Guess365User\Desktop\EMAIL寄信\mail html\mail html\css\normalize.css", "r+", encoding='utf-8') as f:
                    text2 = f.read()
                    f.close()   
                msg.add_alternative(f'''
                    <!DOCTYPE html>
                    <html lang="en">

                    <head>
                      <style type="text/css" nonce>
                      {text}
                      {text2}
                      </style>
                      <meta charset="UTF-8">
                      <meta name="viewport" content="width=device-width, initial-scale=1">
                      <title>Guess365 Mail</title>
                    </head>

                    <body>
                      <header>
                        <div class="logo-panel">
                          <a href="https://guess365.cc/" class="logo" target="_blank" >
                            <img src="https://github.com/chenchenhouse/email/blob/main/images/logo.png?raw=true" alt="Guess365">
                          </a>
                        </div>
                        <div class="user-content">
                          <div class="name">Hi <b>{member_all["會員"]}</b></div>
                          <p>我們統計了您這段期間在 GUESS365 的達標成就，固定時間寄發統計資訊至您的信箱：</p>
                          <div class="time">計算區間：<span>{date_week} ~ {date_today}</span></div>
                        </div>
                      </header>
                      
                        <div class="wrapper" style="padding-bottom: 0px">
                          <div class="panel panel-topic" >
                            <div class="main-title" style="float:left;margin-right: 0rem;">
                                  <div class="title" >
                                    <img src="https://github.com/chenchenhouse/email/blob/main/images/icon-money.png?raw=true" alt="coin">
                                    <b>G幣餘額&分潤點數</b>
                                 </div>
                                 <div class="description" >
                                    2022/12/31前，完成儲值<b class="point">1688G幣</b>，可額外獲得<b class="point">68G幣</b>
                                 </div>
                             </div> 
                             <div class="point-block" style="float: right;">
                                  <div class="list" style="line-height: 25px;">
                                    <span>目前點數：</span>
                                    <b class="point">{member_all["總G幣"]} G幣 </b>
                                    <br> 
                                    <span>分潤點數：</span>
                                     <b class="point">{member_all["總分潤"]} 點</b>
                                  </div>
                                        

                             </div>
                           </div>
                          <div class="panel" >
                            <div class="main-title">
                              <div class="title">
                                <img src="https://github.com/chenchenhouse/email/blob/main/images/icon-money.png?raw=true" alt="coin">
                                <b>本期表現</b>
                              </div>
                              <div class="scoll-table">
                                <table class='table1'>
                                  <thead>
                                    <tr>
                                      <th>聯盟</th>
                                      <th>勝率</th>
                                      <th>神-惜</th>
                                      <th>虛擬獲利</th>
                                      <th>賣牌數</th>
                                      <th>賣牌分潤</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {game_all}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          </div>
                          <div class="panel panel-topic">
                            <div class="main-title" >
                              <div class="title" style="float: left;">
                                <img src="https://github.com/chenchenhouse/email/blob/main/images/icon-money.png?raw=true" alt="coin">
                                <b>文章被按讚數</b>
                              </div>
                            </div>
                            <div class="point-block" style="float:right;padding-left:10rem;display: inline-flex;">  
                                <div class="list" style="width: 8rem;display:inline-block">
                                    <span style="margin-top: 1.3rem;display: inline-block;">文章被按讚數：</span>
                                    <b class="point">{member_all["被按讚數"]}</b>
                                </div>
                                    <a style="margin-top: 1rem;float: right;padding: 5px 12px;text-align:center;font-size: 0.875rem;margin-bottom:8px;min-width: 40%;line-height:1.471;border-radius:3px;color:#fff;background-color: #D9168E;border: 1px solid #D9168E;display:inline-block;text-decoration:none";font-weight: bold; href="https://guess365.cc/Discussion/UserTrackList/229?userId=6a7ac1ac-7b23-4c45-8e93-de1cce9d40f0" target="_blank" data-saferedirecturl="https://guess365.cc/Discussion/UserTrackList/229?userId=6a7ac1ac-7b23-4c45-8e93-de1cce9d40f0">前往文章</a>
                                </div>
                           </div>
                           <div class="panel">
                            <div class="main-title">
                              <div class="title">
                                <img src="https://github.com/chenchenhouse/email/blob/main/images/icon-news.png?raw=true" alt="news">
                                <b>最新消息</b>
                              </div>
                            </div>
                           <div style="width:42rem;height:290px;margin:0 auto">  
                            <a href="https://page.line.me/?accountId=031pakqd">
                                <img src="https://github.com/chenchenhouse/email/blob/main/images/%E6%9C%80%E6%96%B0%E6%B6%88%E6%81%AF.png?raw=true" alt="news">
                            </a>
                            </div>  
                         </div>
                      </body>
                      <div class="foot">
                        <div class="foot foot-top">
                          <div class="info" style="float: left;">
                            <p style="margin-top: 10px;">週一至週日 09:00-20:00</p>
                            <p style="margin-top: 10px;">客服電話：<a href="tel:+886-06-2099558">06-2099558</a></p>
                          </div>
                          <div class="social" style="float: right;">
                            <a href="https://www.facebook.com/guess365.cc">
                              <img src="https://github.com/chenchenhouse/email/blob/main/images/icon-fb.png?raw=true" alt="FB" style="width: 30px;">
                            </a>
                            <a href="https://page.line.me/?accountId=031pakqd">
                              <img src="https://github.com/chenchenhouse/email/blob/main/images/icon-line.png?raw=true" alt="LINE" style="width: 30px;">
                            </a>
                            <a href="https://www.instagram.com/guess365.cc/">
                              <img src="https://github.com/chenchenhouse/email/blob/main/images/icon-ig.png?raw=true" alt="IG" style="width: 30px;">
                            </a>
                          </div>
                        </div>
                        <div class="foot foot-btm">
                          CopyRight @ 2022 Guess365 Co.Ltd All Rights Reserved.
                        </div>
                      </div>
                   
                    
                    
                    </html>
                    
                    ''',subtype="html") #HTML信件內容
               
                acc="adsads023023@gmail.com"
                password="gkfjngdawmwuwmjm"

                server=smtplib.SMTP_SSL("smtp.gmail.com",465) #建立gmail連驗
                server.login(acc,password)
                server.send_message(msg)
                print(f''' 會員:{member_all["會員"]} 
                Email: {member_all["信箱"]}
                寄件成功!!''')
        
if __name__ == '__main__':
    MemberEmail = MemberEmail()
    MemberEmail.send_email_Member(day=200)
                                  


# In[ ]:




