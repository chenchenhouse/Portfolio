#20220524
#寄送特定人
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
import pygsheets


warnings.filterwarnings("ignore")

class MemberEmail_welcome(object):
    
    def __init__(self):
        self.server = 'guess365.database.windows.net'
        self.database = 'Guess365' 
        self.username = "readonly"
        self.password = "superSafe!"
        self.name = ["bear1224","wenchance","MrQN","arenas0428","chen338",  
                     "meater365","Deanderell","domomo","qaz29278","zx8908919","voc497810","grant033","dyco84","e1p3m06","kc6115",
                     "hoho26711","v9992789","A26237179","ryan91422","Ringoyu","Abai","joe1106","love170523","Hong3q3q","Ass1115",   
                     "AlvinHuang","max920127","ricthie1","Luke030322","ge860303","tiyb355053","Fighter","sky1213","lur","huan5138"]
        self.from = "寄件人Email"
        self.password = "寄信密碼"
        
    
    def get_ConnectionFromDB(self):
        '''
        開啟DB
        '''
        db = pymssql.connect(self.server,self.username,self.password,self.database)
        self.cursor = db.cursor()
        
    def Member_list(self):
        '''
        所有user資料
        '''
        sql = f'''
            SELECT UserId,member,nickname,Email,dd
              FROM UserMember
        '''
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        df_user = pd.DataFrame(results,columns = ["UserId","Member","Nickname","Email","dd"])
        return df_user
    
    
    def Analyze_push(self,ID1=260,ID2=260):
        '''
        分析文章推播
        '''
        sql =f'''
            SELECT A.Id,A.ViewsCount,A.Title,B.member,C.Id
              FROM Discussion AS A
              INNER JOIN UserMember AS B ON A.CreatedBy = B.UserId
              OUTER APPLY (SELECT TOP (1) ID FROM UserMember_Pic AS C WHERE C.UserId = A.CreatedBy  ORDER BY dd DESC ) AS C
              WHERE A.ID = {ID1}'''
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        analyze1 = pd.DataFrame(results,columns= ["user_id","viewscount","title","member","pic_id"])
        sql =f'''
            SELECT A.Id,A.ViewsCount,A.Title,B.member,C.Id
              FROM Discussion AS A
              INNER JOIN UserMember AS B ON A.CreatedBy = B.UserId
              OUTER APPLY (SELECT TOP (1) ID FROM UserMember_Pic AS C WHERE C.UserId = A.CreatedBy  ORDER BY dd DESC ) AS C
              WHERE A.ID = {ID2}'''
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        analyze2 = pd.DataFrame(results,columns= ["user_id","viewscount","title","member","pic_id"])
        return analyze1,analyze2
    
        
        
    
    def send_email_Member(self,day_=14,ID1=260,ID2=260):
        self.get_ConnectionFromDB()
        df_user = self.Member_list()
        date_today = datetime.datetime.now().strftime("%Y-%m-%d")
        for d in range(len(df_user)):
            user_id = df_user["UserId"].iloc[d]
            name = df_user["Member"].iloc[d]
            email_ = df_user["Email"].iloc[d]
            if name in self.name:
                member_data ={
                    "會員" : name,
                    "信箱" : email_,
                } 
                if email_ != "":
                    #分析文章推播
                    analyze1,analyze2 = self.Analyze_push(ID1,ID2)

                    msg=email.message.EmailMessage()
                    from_a= self.from
                    to_b= email_
                    msg["From"]=from_a
                    msg["To"]=to_b
                    msg["Subject"]="[GUESS365] 歡迎您註冊成為GUESS365的一員"
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
                            <header style="padding: 30px;padding-bottom:10px;padding-top:20px;">
                                <div class="logo-panel">
                                  <a href="https://guess365.cc/" class="logo" target="_blank" >
                                    <img src="https://github.com/chenchenhouse/email/blob/main/images/logo.png?raw=true" alt="Guess365" style="width: 23rem;">
                                  </a>
                                </div>
                                <div class="user-content">
                                  <div class="name">Hi <b>{member_data["會員"]}</b>:</div>
                                  <p style="text-align:justify;margin-left: 29px;">歡迎您加入【Guess365神連莊】運動賽事預測平台。</p>
                                </div>
                              </header>

                                <div class="wrapper" style="padding:30px;padding-bottom:0px;padding-top:20px;">
                                    <div class="panel panel-topic" style="padding: 0px;">
                                        <div class="main-title" style="float:left;margin-right: 0rem;">
                                          <div class="title" style="margin-bottom: 15px;">
                                            <img src="https://www.mainz.com.tw/wp-content/uploads/2016/07/%E4%BF%A1%E4%BB%B6%E9%A0%90%E7%B4%84.jpg" alt="ai">
                                            <b>您的專屬情報：</b>
                                          </div>
                                          <div style="border-radius:6px;margin-bottom:32px;margin-right:30px;">
                                               <ol style="font-size: 15px;line-height: 30px;">
                                                   <li style="list-style-type:'🔔 ';margin-left: 40px;">
                                                       每兩週寄送平台<b class="point">雙週報</b>，統計您的G幣餘額、分潤點數及當期表現
                                                   </li>
                                                   <li style="list-style-type:'🔔 ';margin-left: 40px;">
                                                       如有<b class="point">最新消息</b>或<b class="point">活動</b>，也將透過Email傳達
                                                   </li>
                                                   <li style="list-style-type:'🔔 ';margin-left: 40px;">
                                                       避免信箱誤認為垃圾信件，導致無法接收平台訊息，記得將信件設為<b class="point">重要信件</b>
                                                   </li>
                                               </ol>
                                           </div> 
                                        </div>
                                   </div>
                                   <div class="panel">
                                      <div class="main-title">
                                          <div class="title" style="margin-bottom: 15px;">
                                            <img src="https://cdn-icons-png.flaticon.com/512/1486/1486459.png" alt="ai">
                                            <b>您也許會想了解：</b>
                                          </div>
                                          <div style="border:1px solid #cbc3c2;border-radius:6px;padding:10px 10px;margin-bottom:32px;margin-left:15px">
                                            <ol style="font-size: 15px;line-height: 30px;margin-left: 25px;"> 
                                                <li  style="border-bottom:0px solid #ddd;padding-bottom:5px;margin:5px 0;">
                                                   Guess365是什麼平台?
                                                    <a href="https://guess365.cc/" title="點此了解詳情" style="color:#24a0c2;margin-left: 10px;" target="_blank" data-saferedirecturl= "https://guess365.cc/Introduction/Index">➤ 點此了解詳情</a>
                                                </li>
                                                <li  style="border-bottom:0px solid #ddd;padding-bottom:5px;margin:5px 0;">
                                                   我該如何儲值G幣?
                                                    <a href="https://guess365.cc/deposit" title="點此了解詳情" style="color:#24a0c2;margin-left: 10px;" target="_blank" data-saferedirecturl= "https://guess365.cc/deposit">➤ 點此了解詳情</a>
                                                </li>
                                                <li  style="border-bottom:0px solid #ddd;padding-bottom:5px;margin:5px 0;">
                                                   如何尋找預測高手?
                                                    <a href="https://guess365.cc/buy" title="點此了解詳情" style="color:#24a0c2;margin-left: 10px;" target="_blank" data-saferedirecturl= "https://guess365.cc/Introduction/sell_rules">➤ 點此了解詳情</a>
                                                </li>
                                                <li  style="border-bottom:0px solid #ddd;padding-bottom:5px;margin:5px 0;">
                                                   如何預測賽事?
                                                    <a href="https://guess365.cc/guessing" title="點此了解詳情" style="color:#24a0c2;margin-left: 10px;" target="_blank" data-saferedirecturl= "https://guess365.cc/Introduction/member_level">➤ 點此了解詳情</a>
                                                </li>
                                            </ol>
                                          </div>
                                      </div>
                                    </div>
                                  <div class="panel" style="min-width: 502px;">
                                  <div class="main-title">
                                      <div class="title" style="margin-bottom: 15px;">
                                        <img src="https://github.com/chenchenhouse/email/blob/main/images/icon-ai.png?raw=true" alt="ai">
                                        <b>分析好文推薦</b>
                                      </div>
                                  </div>
                                  <table  class="table2" style="display: inline-block;">
                                      <tbody style="vertical-align:top;text-align:left;display: -webkit-box;">
                                        <tr style="display: inline-block;width: 645px;">
                                          <td style="padding: 8px;float:left;width:50%;max-width:100rem;border-right:2px solid #ebebeb;padding-right:12px">
                                           <ul style="margin-left: 15px;">
                                            <li style="padding-inline-start: 0.5ch;margin-left: 15px;">
                                              <a href="https://ecocoapidev1.southeastasia.cloudapp.azure.com/gmail?article={analyze1["user_id"][0]}&user={name}&senddate={date_today}" style="height:25px;color:#4867ff;text-decoration:underline;font-size: 1rem;font-weight:600;word-break:break-all;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;" target="_blank" data-saferedirecturl="https://ecocoapidev1.southeastasia.cloudapp.azure.com/gmail?article={analyze1["user_id"][0]}&user={name}&senddate={date_today}">{analyze1["title"][0]}</a>
                                               <div style="display:flex;margin-top:10px">
                                                   <img style="margin-right:8px;border-radius:50%;width: 9%;" src="https://guess365.cc/api/pic/UserMember_Pic/{analyze1["pic_id"][0]}" width="24px" height="24px">
                                                   <span style="font-size:14px">
                                                     本文作者：{analyze1["member"][0]}
                                                   </span>
                                               </div>
                                               <div style="display:inline-block;margin-top:10px;float:right;min-width: 170px;"> 
                                                <span style="font-size:14px;float:left;margin-top:20px;padding-right: 0.5vw;">
                                                    文章人氣 : <b style="color:#ff485a;padding-right: 3px;">{analyze1["viewscount"][0]}</b>
                                                </span>

                                                <a style="margin-top: 1rem;float: right;padding: 5px 12px;text-align:center;font-size: 0.875rem;margin-bottom:8px;min-width: 40%;line-height:1.471;border-radius:3px;color:#fff;background-color: #D9168E;border: 1px solid #D9168E;display:inline-block;text-decoration:none";font-weight: bold; href="https://ecocoapidev1.southeastasia.cloudapp.azure.com/gmail?article={analyze1["user_id"][0]}&user={name}&senddate={date_today}" target="_blank" data-saferedirecturl="https://ecocoapidev1.southeastasia.cloudapp.azure.com/gmail?article={analyze1["user_id"][0]}&user={name}&senddate={date_today}">前往文章</a>
                                              </div>
                                          </li>
                                          </ul>
                                         </td>
                                         <td style="float: left;width: 50%;max-width: 100rem;">
                                           <ul style="margin-left: 15px;">
                                            <li style=" padding-inline-start:0.5ch;margin-left: 15px;">
                                              <a href="https://ecocoapidev1.southeastasia.cloudapp.azure.com/gmail?article={analyze2["user_id"][0]}&user={name}&senddate={date_today}" style="height:25px;color:#4867ff;text-decoration:underline;font-size:1rem;font-weight:600;word-break:break-all;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;" target="_blank" data-saferedirecturl="https://ecocoapidev1.southeastasia.cloudapp.azure.com/gmail?article={analyze2["user_id"][0]}&user={name}&senddate={date_today}">{analyze2["title"][0]}</a>
                                              <div>
                                                  <div style="display:flex;margin-top:10px">
                                                    <img style="margin-right:8px;border-radius:50%;width: 9%;" src="https://guess365.cc/api/pic/UserMember_Pic/{analyze2["pic_id"][0]}" width="24px" height="24px">
                                                    <span style="font-size:14px;">
                                                        本文作者：{analyze2["member"][0]}
                                                    </span>
                                                  </div>
                                                  <div style="display: inline-block;margin-top:10px;float:right;min-width: 170px"> 
                                                    <span style="font-size:14px;float: left;margin-top: 20px;padding-right: 0.5vw;">
                                                        文章人氣 : <b style="color:#ff485a;padding-right: 3px;">{analyze2["viewscount"][0]}</b>
                                                    </span>

                                                    <a style="margin-top: 1rem;float: right;padding: 5px 12px;text-align:center;font-size: 0.875rem;margin-bottom:8px;min-width: 40%;line-height:1.471;border-radius:3px;color:#fff;background-color: #D9168E;border: 1px solid #D9168E;display:inline-block;text-decoration:none";font-weight: bold; href="https://ecocoapidev1.southeastasia.cloudapp.azure.com/gmail?article={analyze2["user_id"][0]}&user={name}&senddate={date_today}" target="_blank" data-saferedirecturl="https://ecocoapidev1.southeastasia.cloudapp.azure.com/gmail?article={analyze2["user_id"][0]}&user={name}&senddate={date_today}">前往文章</a>
                                                  </div>
                                               </div>
                                              </li>
                                            </ul>
                                          </td>
                                        </tr>
                                      </tbody>
                                  </table>
                              </div>
                               <div class="panel">
                            <div class="main-title">
                              <div class="title">
                                <img src="https://github.com/chenchenhouse/email/blob/main/images/icon-news.png?raw=true" alt="news">
                                <b>最新消息</b>
                              </div>
                            </div>
                           <div style="min-width:42rem;height:290px;margin:0 auto">  
                            <a href="https://ecocoapidev1.southeastasia.cloudapp.azure.com/gmail?article=line&user={name}&senddate={date_today}">
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
                          Copyright© 2022 Guess365 Co.Ltd All Rights Reserved.
                        </div>
                      </div>



                    </html>

                        ''' ,subtype="html")#HTML信件內容
                    acc=self.from
                    password= self.password

                    server=smtplib.SMTP_SSL("smtp.gmail.com",465) #建立gmail連驗
                    server.login(acc,password)
                    server.send_message(msg)
                    print(f'''會員:{df_user["Member"].iloc[d]} \nEmail: {df_user["Email"].iloc[d]} \n寄件成功!!''')
            
if __name__ == '__main__':
    MemberEmail_welcome = MemberEmail_welcome()
    MemberEmail_welcome.send_email_Member(day_=14,ID1='192',ID2='284')

