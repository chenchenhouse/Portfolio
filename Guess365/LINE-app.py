from collections import defaultdict
from datetime import datetime, timedelta, timezone
from flask import abort,Flask,flash,g,jsonify,render_template,request,redirect,url_for,Markup,Response
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from io import BytesIO
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from matplotlib import dates as mdates
from matplotlib.gridspec import GridSpec
from PIL import Image, ImageDraw,ImageFilter
from requests.auth import HTTPBasicAuth as HBA
from sqlalchemy import create_engine
from scipy.interpolate import make_interp_spline
from time import sleep
from urllib.parse import parse_qsl,quote
from werkzeug.security import generate_password_hash, check_password_hash

import base64
import copy
import hashlib
import hmac
import json
import numpy as np
import pandas as pd
import pyodbc
import pytz
import traceback
import uuid
import requests
import random
import time
import warnings
import string
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



import web_config
import auto_match_pk as match_pk

warnings.filterwarnings('ignore')
utc = pytz.UTC

app = Flask(__name__)

'''
[1] LINE參數
'''

'''
#測試區
line_bot_api = LineBotApi(web_config.line_test().line_bot_api)

handler = WebhookHandler(web_config.line_test().handler)
liffid = web_config.line_test().liffid
linepay_liffid = web_config.line_test().linepay_liffid
linepay_check = web_config.line_test().linepay_check
'''
#正式區
line_bot_api = LineBotApi(web_config.line_district().line_bot_api)

handler = WebhookHandler(web_config.line_district().handler)
liffid = web_config.line_district().liffid
linepay_liffid = web_config.line_district().linepay_liffid
linepay_check = web_config.line_district().linepay_check

#Domain Name
domain_name = web_config.domain().domain_name
branch = web_config.domain().branch

'''
[2]LINE PAY
'''
channel_id = web_config.Line_pay().channel_id
channel_secret = web_config.Line_pay().channel_secret
uri = web_config.Line_pay().uri
transaction_id = web_config.Line_pay().transaction_id 



'''
[3]全域參數
'''
auth = HTTPBasicAuth()
@app.before_request
def before_request():
    '''
    #linux
    g.conn_Guess365 = pyodbc.connect(server=web_config.production().server,
                                    database=web_config.production().database,
                                    user=web_config.production().username,
                                    password=web_config.production().password, 
                                    tds_version = '7.3',
                                    port = web_config.production().port,
                                    driver = '/home/linuxbrew/.linuxbrew/lib/libtdsodbc.so') 
    cursor = g.conn_Guess365.cursor()

    #測試區
    _server_gamania = web_config.testing().server  # No TCP
    _database_gamania = web_config.testing().database
    _uid_gamania = web_config.testing().username
    _pwd_gamania = quote(web_config.testing().password)
    _port = "1433"
    '''
    #正式區
    _server_gamania = web_config.production().server  # No TCP
    _database_gamania = web_config.production().database
    _uid_gamania = web_config.production().username
    _pwd_gamania = web_config.production().password
    _port = "1433"
    
    g.conn_Guess365 = pyodbc.connect('DRIVER={SQL Server};SERVER='+_server_gamania+';Port='+_port+';DATABASE='+_database_gamania+';UID='+_uid_gamania+';PWD='+_pwd_gamania)  # for MSSQL
    g.cursor = g.conn_Guess365.cursor()
    
    #LINE PAY
    #nonce = str(uuid.uuid4())
    g.nonce = str(round(time.time() * 1000))  
    g.headers = {
        'Content-Type': 'application/json',
        'X-LINE-ChannelId': channel_id,
        'X-LINE-Authorization-Nonce': g.nonce,
    }

    #隨機時間戳(解決快取問題)
    g.timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
'''
[4]安全性設定
'''
users = [
    {'username': web_config.user().username,'password': generate_password_hash(web_config.user().password), 'password_2': web_config.user().password}
]
@auth.verify_password
def verify_password(username, password):
    for user in users:
        if user['username'] == username:
            if check_password_hash(user['password'], password):
                return True
    return False


'''
[5]加入紀錄
1.加LINE後跳出登入或註冊的操作圖示，點擊進行登入或註冊
2.加入LINE後直接給於隨機帳密，直接進行註冊
'''

"""
#狀況1
@handler.add(FollowEvent)
def handle_follow(event):
    newLineUniqueID = event.source.user_id
    profile = line_bot_api.get_profile(newLineUniqueID)
    headshot = profile.picture_url
    membername = profile.display_name
    results_lineuser = SearchLineUser(newLineUniqueID)
    if newLineUniqueID in results_lineuser['LineUniqueID'].values:
        User = results_lineuser[results_lineuser['LineUniqueID'] == newLineUniqueID]
        if User['UserId'].values[0] == None:
            alreadylogupLine(headshot,'join',newLineUniqueID)
            
            image_message = ImagemapSendMessage(
                base_url=f'https://{domain_name}/static/welcome.png#1040',
                alt_text='歡迎加入Guess365',
                base_size=BaseSize(height=2080, width=1040),
                actions=[
                 URIImagemapAction(# 超連結
                     link_uri=f'https://liff.line.me/{liffid}',
                     area=ImagemapArea(
                         x=0, y=0, width=1040, height=2080
                     )
                 )
                ]
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        else:
            alreadylogupLine(headshot,'connect',newLineUniqueID)
            yzmdata = requests.get(headshot)
            tempIm = BytesIO(yzmdata.content)
            markImg = Image.open(tempIm)
            thumb_width = 150
            im_square = crop_max_square(markImg).resize((thumb_width,thumb_width),Image.LANCZOS)
            im_thumb = mask_circle_transparent(im_square,0)
            im_thumb.save(f"static/memberlogo/{User['UserId'].values[0]}.png")
            
            image_message = ImagemapSendMessage(
                base_url=f'https://{domain_name}/static/welcome.png#1040',
                alt_text='歡迎加入Guess365',
                base_size=BaseSize(height=2080, width=1040),
                actions=[
                 URIImagemapAction(# 超連結
                     link_uri=f'https://mobile.guess365.cc/',
                     area=ImagemapArea(
                         x=0, y=0, width=1040, height=2080
                     )
                 )
                ]
            )
            line_bot_api.reply_message(event.reply_token, image_message)
            
    else:
        Insert_SQL = '''
            INSERT INTO [dbo].[LineUserMember] (LineUniqueID,[Level],HeadShot,LineName,CreatedTime,Situate,Register) VALUES 
            ('{}','0','{}',N'{}','{}','join','Line')    
        '''.format(newLineUniqueID,
                   headshot,
                   membername,datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
        
        image_message = ImagemapSendMessage(
            base_url=f'https://{domain_name}/static/welcome.png#1040',
            alt_text='歡迎加入Guess365',
            base_size=BaseSize(height=2080, width=1040),
            actions=[
             URIImagemapAction(# 超連結
                 link_uri=f'https://liff.line.me/{liffid}',
                 area=ImagemapArea(
                     x=0, y=0, width=1040, height=2080
                 )
             )
            ]
        )
        line_bot_api.reply_message(event.reply_token, image_message)

    cursor = g.conn_Guess365.cursor()
    cursor.execute(Insert_SQL)
    cursor.commit() 
"""
@handler.add(FollowEvent)
#狀況2
def handle_follow(event):
    newLineUniqueID = event.source.user_id
    profile = line_bot_api.get_profile(newLineUniqueID)
    headshot = profile.picture_url
    membername = profile.display_name
    results_lineuser = SearchLineUser(newLineUniqueID)
    
    if len(results_lineuser) > 0:
        User = results_lineuser[results_lineuser['LineUniqueID'] == newLineUniqueID]
        Userid = User['UserId'].values[0]
        if Userid == None:
            alreadylogupLine(headshot,'join',newLineUniqueID)
        else:
            alreadylogupLine(headshot,'connect',newLineUniqueID)
            SaveHeadshot(headshot,Userid)
    else:
        ip = request.headers['X-Forwarded-For'] 
        account,password = RandomAccont()
        url = f'http://https://ecocoapidev1.southeastasia.cloudapp.azure.com/Register/'
        data = {
            'member' : account,
            'password' : password,
            'nickname' : membername,
            'ip' : ip
        }
        response_ = requests.post(url,verify=False, data = data, auth=HBA('rick', '123rick456')).text
        if response_ != 'Account has exist' and 'Error Info' not in response_:
            #查詢userid
            UserId = json.loads(response_)['response'][0]['Success Info']
            logupandfree(newLineUniqueID,UserId,membername,headshot)
            SaveHeadshot(headshot,UserId)
    UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
    FlexMessage = set_UserMemberInfo(event, UserMemberInfo) 
    image_message = ImageSendMessage(
            alt_text='歡迎加入Guess365',
            original_content_url=f'https://{domain_name}/static/banner/recommend.jpg#1040',
            preview_image_url=f'https://{domain_name}/static/banner/recommend.jpg#1040',
        )
    line_bot_api.reply_message(event.reply_token, [FlexSendMessage('關於我', FlexMessage),image_message])


'''
[4]推播功能
1.API自動推播
2.手動WEB推播
'''
#狀況1
@app.route("/UserMemberSellingPushMessage", methods=['POST'])
@auth.login_required
def send_UserMemberSellingPushMessage():
    try:
        # 取得會員輸入資料
        data = request.get_json()
        auth_username = auth.username()
        connect = data['connect']
        SubscribeLevels = data['SubscribeLevels']
        banner = data['banner']
        check = data['check']
        if connect:
            header=dict(
            predict_winrate = data['predict_winrate'],
            title = data['title'],
            TournamentText_icon = data['TournamentText_icon'],
            body_data=data['body_data'],
            body_image = data['body_image'])
        else:
            header=False
            
        #判斷會員是否已到期
        for maturity in [False,True]:
            LineBotAutoPredictionLogs = get_LineBotAutoPredictionLog(SubscribeLevels=SubscribeLevels.split('/'),maturity = maturity)
            if LineBotAutoPredictionLogs.shape[0] > 0:
                if maturity == True:
                    predlist_match = []
                    for i in range(len(predlist)):
                        if predlist[i]['OptionCode'] == 1:
                            confidence = int(predlist[i]['HomeConfidence'].replace("%",""))
                        elif predlist[i]['OptionCode'] == 2:
                            confidence = int(predlist[i]['AwayConfidence'].replace("%",""))
                        else:
                            confidence = int(predlist[i]['TieConfidence'].replace("%",""))

                        if len(predlist_match) == 0:
                            predlist_match.append(predlist[i])
                        else:
                            if predlist_match[0]['OptionCode'] == 1:
                                confidence_m = int(predlist_match[0]['HomeConfidence'].replace("%",""))
                            elif predlist_match[0]['OptionCode'] == 2:
                                confidence_m = int(predlist_match[0]['AwayConfidence'].replace("%",""))
                            else:
                                confidence_m = int(predlist_match[0]['TieConfidence'].replace("%",""))  
                            if confidence > confidence_m:
                                predlist_match[0] = predlist[i]
                else:
                    predlist_match = data['predlist']
                data['predlist'] = predlist_match
                LineUniqueIDs = list(set(LineBotAutoPredictionLogs['LineUniqueID']))
                searchpush = searchalreadlypush()
                havewrite = False
                pushmessage = defaultdict(lambda: defaultdict(dict))
                for lineid in LineUniqueIDs:
                    checkdata = copy.deepcopy(data)
                    if check == True:
                        alreadypushid = searchpush[searchpush['LineUniqueID'] == lineid]['id']
                        for pre in predlist_match:
                            eventcode = pre['EventCode']
                            groupoptioncode = pre['GroupOptionCode']
                            matchpushid = searchpush[(searchpush['EventCode'] == eventcode) & (searchpush['GroupOptionCode'] == str(groupoptioncode))]['id']
                            havepush = []  
                            for match in matchpushid:
                                push = match in list(alreadypushid)
                                havepush.append(push)
                            if True in havepush:
                                checkdata['predlist'].remove(pre)

                    #要推播的賽事寫入資料庫
                    if havewrite == False:
                        all_linepushmessage = ''
                        for pre in data['predlist']:  
                            try:
                                tieodds = pre['Tieodds']
                                tie = True
                            except:
                                tie = False
                            linepushmessage = write_linepushmessage(pre,tie)
                            if linepushmessage != "game had start!!" :
                                all_linepushmessage += linepushmessage
                            else:
                                checkdata['predlist'].remove(pre)
                        if all_linepushmessage == '':
                            return "All game had start!!"
                        cursor = g.conn_Guess365.cursor()
                        cursor.execute(all_linepushmessage)
                        cursor.commit()
                        havewrite = True

                    # 傳送預測請求
                    response = requests.post(f'{branch}/PredictMatchEntrys/',json=checkdata, auth=(users[0]['username'],users[0]['password_2']),verify=False).text
                    response = json.loads(response)
    
                    print(response)
                    # 判斷請求是否成功，成功代表資料無誤
                    if 'PredictSQL' in response.keys():
                        content = f"{response['PredictSQL']}"
                        contents = content.split('------------------')[:-1]
                        if maturity == False:
                            if len(contents) <= 6:
                                Message1 = set_FlexTemplateMessage(contents, header,connect,banner)
                                Flex_Message = [Message1]
                            elif len(contents) <= 12:
                                Message1 = set_FlexTemplateMessage(contents[:6], header,connect,banner)
                                Message2 = set_FlexTemplateMessage(contents[6:], header,connect,banner)
                                Flex_Message = [Message1,Message2]
                            else:
                                Message1 = set_FlexTemplateMessage(contents[:6], header,connect,banner)
                                Message2 = set_FlexTemplateMessage(contents[6:12], header,connect,banner)
                                Message3 = set_FlexTemplateMessage(contents[12:], header,connect,banner)
                                Flex_Message = [Message1,Message2,Message3]
                        else:
                            Message1 = set_FlexTemplateMaturity(contents,banner)
                            Flex_Message = [Message1]
                        pushlist = len(pushmessage)
                        if pushlist != 0:
                            samemessage = False
                            for push in range(len(pushmessage)):
                                if Flex_Message == pushmessage[push]['FlexMessage']:
                                    samemessage = True
                                    break
                            if samemessage == True:
                                pushmessage[push]['PushMember'].append(lineid)
                            else:
                                pushmessage[pushlist] = {'PushMember' : [lineid],'FlexMessage' : Flex_Message,"Predlist" : checkdata['predlist']}
                        else:
                            pushmessage[0] = {'PushMember' : [lineid],'FlexMessage' : Flex_Message,"Predlist" : checkdata['predlist']}
                    else:
                        pass
                
                for push in range(len(pushmessage)):
                    pushmember = pushmessage[push]['PushMember']
                    flexmessage = pushmessage[push]['FlexMessage']
                    predlist = pushmessage[push]['Predlist']
                    pushamount = len(pushmember) // 500
                    if pushamount > 0:
                        for amount in range(pushamount): 
                            pushlistone = pushmember[500*amount:500*(amount+1)]
                            for message in flexmessage:
                                line_bot_api.multicast(pushlistone, FlexSendMessage('本日預測', message))
                    else:
                        for message in flexmessage:
                            line_bot_api.multicast(pushmember, FlexSendMessage('本日預測', message))
                    for pre in predlist: 
                        all_insert = ''
                        pushid = maxid(pre)
                        for member in pushmember:
                            insert_sql = write_linepushmember(member,pushid) 
                            all_insert += insert_sql
                        cursor = g.conn_Guess365.cursor()
                        cursor.execute(all_insert)
                        cursor.commit()    
                try:
                    write_LineBotPushMessage('linebot', auth_username, content, SubscribeLevels)
                except:
                    if maturity == True:
                        return jsonify({'response': f'No {SubscribeLevels} members need to push.'})
                if maturity == True:
                    return jsonify({'response': f'Successfully pushed to {SubscribeLevels} members.'})

            else:
                if maturity == False:
                    print("no unexpired matching members need to push.")
                else:
                    return jsonify({'response': 'Successfully pushed, but no matching members.'}) 
    except:
        return Response(jsonify({'response': [{'Error Info': traceback.format_exc()}]}),status=400)

#狀況2
@app.route("/PredictMatchPushMessage", methods=['GET','POST'])
@auth.login_required
def send_PredicMatchPushMessage():
    auth_username = auth.username()
    LineUserMembers = get_LineUserMember()
    if request.method == 'GET': 
        Tournamentlist = Markup(list(sql_SearchLastGame(day=0,scope=10)['TournamentText'].values))
        MatchEntrys = requests.get(f'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/All/any',verify=False, auth=(users[0]['username'],users[0]['password_2'])).text
        MatchEntrys = json.loads(MatchEntrys)['response']
        if len(MatchEntrys) <2:
            MatchEntrys = requests.get(f'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/All/any',verify=False, auth=(users[0]['username'],users[0]['password_2'])).text
            MatchEntrys = json.loads(MatchEntrys)['response']
        MatchEntrys = Markup(MatchEntrys)
        return render_template('Predictpush.html',**locals())
    
    elif request.method == 'POST':
        alliances = request.form.getlist('alliance_table')
        game = request.form.getlist('game_table')
        odds = request.form.getlist('odds_table')
        subscribe = request.form.getlist('subscribelevels')
        subscribelevels = ""
        account,password = "adsads2323","s9212598"
        for sub in range(len(subscribe)):
            subscribelevels += subscribe[sub]
            if sub < len(subscribe)-1:
                subscribelevels += "/"
        all_option = Searchoption(search_all=True)
        for alliance in set(alliances):
            predlist = []
            for g in range(len(game)):
                if alliances[g] == alliance:
                    eventcode = game[g].split(" ")[-1]
                    groupoption = odds[g].split("-")[0]
                    optionteam = odds[g].split("-")[1]
                    option_one = all_option[(all_option['Type_cname'] == groupoption) & (all_option['TournamentText'] == alliance)]
                    option = []
                    for i in range(len(option_one)):
                        option.appendnd(option_one['OptionCode'][i])
                    groupoptioncode = option_one['GroupOptionCode'][0]
                    if optionteam == '主':
                        OptionCode = '1'
                    elif optionteam == '客':
                        OptionCode = '2'
                    elif optionteam == '平':
                        OptionCode = 'X'
                    elif optionteam == '大':
                        OptionCode = 'Over'
                    elif optionteam == '小':
                        OptionCode = 'Under'   
                    manualpush = manualpushsearch(eventcode,option,groupoptioncode)
                    HomeConfidence = round((float(manualpush['Awayodds'][0]) / (float(manualpush['Awayodds'][0])+float(manualpush['Homeodds'][0])))*100,0)
                    AwayConfidence = round((float(manualpush['Homeodds'][0]) / (float(manualpush['Awayodds'][0])+float(manualpush['Homeodds'][0])))*100,0)
                    prdict = {
                        "account":account,
                        "password":password,
                        "GroupOptionCode":groupoptioncode,
                        "OptionCode":OptionCode,
                        "EventCode":eventcode,                                                                                                                                                                                                                                                                                                         
                        "predict_type":"OnlyPush",
                        "HomeOdds":manualpush['Homeodds'][0],
                        "AwayOdds":manualpush['Awayodds'][0],
                        "HomeConfidence":f"{int(HomeConfidence)}%",
                        "AwayConfidence":f"{int(AwayConfidence)}%"
                    }
                    predlist.append(prdict)
            url = f"https://{domain_name}/UserMemberSellingPushMessage"
            banner = manualpush['SportText'][0]
            if alliance == 'NPB':
                json_= {"SubscribeLevels":subscribelevels,
                        "predict_winrate":"58.7%",
                        "title":"本季準確度 : ",
                        "body_data":"2021賽季回測|39050|852過500|58.7%",
                        "TournamentText_icon":"https://i.imgur.com/4YeALVb.jpeg",
                        "body_image":"https://i.imgur.com/w4MQwdZ.png",
                        "predlist":predlist,
                        "connect" : True,
                        "banner" : banner}
            elif alliance == 'MLB':
                json_= {"SubscribeLevels":subscribelevels,
                        "predict_winrate":"70%",
                        "title":"本季準確度:",
                        "body_data":"2021賽季回測|20530|288過251|87.2",
                        "TournamentText_icon":"https://upload.wikimedia.org/wikipedia/zh/thumb/2/2a/Major_League_Baseball.svg/1200px-Major_League_Baseball.svg.png",
                        "body_image":"https://i.imgur.com/R3eCxgt.png",
                        "predlist":predlist,
                        "connect" : True,
                        "banner" : banner}
            else:
                json_= {"SubscribeLevels":subscribelevels,
                        "predlist":predlist,
                        "connect" : False,
                        "banner" : banner}
            response = requests.post(url, json = json_, auth=HBA('rick', '123rick456'), verify=False).text
            all_linepushmessage = ''
            for pre in predlist:
                linepushmessage = write_linepushmessage(pre)
                all_linepushmessage += linepushmessage
            cursor = g.conn_Guess365.cursor()
            cursor.execute(all_linepushmessage)
            cursor.commit()

        return redirect(url_for('send_PredicMatchPushMessage'))

'''
@app.route("/UserMemberPushMessage", methods=['GET','POST'])
@auth.login_required
def send_UserMemberPushMessage():
    auth_username = auth.username()
    user_select = get_LineUserMember()
    if request.method == 'POST':
        content = request.form['content']
        user_select = request.form['user_select']
        selected_icon_text = request.form['selected-text']
        if content != '' and selected_icon_text != '-1':
            if user_select == '所有人':
                user_select = list(user_select['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, [TextSendMessage(text=content),
                                                         ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                          preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg')])
                    write_LineBotPushMessage('manual', auth_username, content ,'all')
                    flash('傳送成功(文字+貼圖)')
                else:
                    flash('沒有用戶')
            elif user_select == 'Level-1用戶':
                user_select = list(user_select[user_select['Level']==1]['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, [TextSendMessage(text=content),
                                                         ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                          preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg')])
                    write_LineBotPushMessage('manual', auth_username, content,'Level-1')
                    flash('傳送成功(文字+貼圖)')
                else:
                    flash('沒有用戶')
            else:
                user_select = json.loads(user_select.replace('\'','\"'))['LineUniqueID']
                line_bot_api.multicast([user_select], [TextSendMessage(text=content),
                                                       ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                        preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg')])
                write_LineBotPushMessage('manual', auth_username, content,user_select)
                flash('傳送成功(文字+貼圖)')
        elif content != '' and selected_icon_text == '-1':
            if user_select == '所有人':
                user_select = list(user_select['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, TextSendMessage(text=content))
                    write_LineBotPushMessage('manual', auth_username, content,'all')
                    flash('傳送成功(文字)')
                else:
                    flash('沒有用戶')
            elif user_select == 'Level-1用戶':
                user_select = list(user_select[user_select['Level']==1]['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, TextSendMessage(text=content))
                    write_LineBotPushMessage('manual', auth_username, content,'Level-1')
                    flash('傳送成功(文字)')
                else:
                    flash('沒有用戶')
            else:
                user_select = json.loads(user_select.replace('\'','\"'))['LineUniqueID']
                line_bot_api.multicast([user_select], TextSendMessage(text=content))
                write_LineBotPushMessage('manual', auth_username, content,user_select)
                flash('傳送成功(文字)')
        elif content == '' and selected_icon_text != '-1':
            if user_select == '所有人':
                user_select = list(user_select['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                         preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg'))
                    write_LineBotPushMessage('manual', auth_username, content,'all')
                    flash('傳送成功(貼圖)')
                else:
                    flash('沒有用戶')
            elif user_select == 'Level-1用戶':
                user_select = list(user_select[user_select['Level']==1]['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                         preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg'))
                    write_LineBotPushMessage('manual', auth_username, content,'Level-1')
                    flash('傳送成功(貼圖)')
                else:
                    flash('沒有用戶')
            else:
                user_select = json.loads(user_select.replace('\'','\"'))['LineUniqueID']
                line_bot_api.multicast([user_select], ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                        preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg'))
                write_LineBotPushMessage('manual', auth_username, content,user_select)
                flash('傳送成功(貼圖)')
        else:
            flash('傳送失敗，請填寫文字或貼圖')
        return render_template('Sellings.html',**locals())
    return render_template('Sellings.html',**locals())
'''

'''
[5]自動賽果推播
'''
#@app.route("/immediatePredictResultsPush/DateBetween=<DateBetween>", methods=['GET'])
@app.route("/immediatePredictResultsPush/UserId=<UserId>", methods=['GET'])
@app.route("/immediatePredictResultsPush", methods=['GET'])
@auth.login_required
def immediate_PredictResultsPushMessage(DateBetween = None,UserId = None):
    # 取得驗證帳戶、LineId
    auth_username = auth.username()
    DateBetween = request.args.get('DateBetween')
    UserId = request.args.get('UserId')
    if request.method == 'GET':
        try:
            if DateBetween:
                DatetimeTop, DatetimeBottom = DateBetween.split('~')[0].strip() + ' 00:00:00.000', DateBetween.split('~')[1].strip() + ' 23:59:59.000'
            else:
                DatetimeTop, DatetimeBottom = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), (datetime.now() - timedelta(
                days=1)).replace(hour=23, minute=59, second=59).astimezone(timezone(timedelta(hours=12))).strftime('%Y-%m-%d %H:%M:%S.000')
            SQL = '''SELECT distinct a.EventCode,a.TournamentText,a.GroupOptionCode,e.Type_cname,a.PredictTeam,a.OptionCode,a.SpecialBetValue,
                b.MatchTime,b.HomeTeam,f.name as Home_CTeam,b.AwayTeam,g.name as Away_CTeam,b.HomeScore,b.AwayScore,a.SportCode,d.Profit,a.main,
                ROW_NUMBER() over (partition BY a.EventCode order by a.CreatedTime) sn
                    FROM [dbo].[LINEPushMatch] as a
                    inner join MatchResults as b on a.EventCode = b.EventCode
                    inner join PredictMatch as c on a.EventCode = c.EventCode and a.UserId = c.UserId
                    inner join PredictResults as d on c.id = d.Predict_id
                    inner join GroupOptionCode as e on a.GroupOptionCode = e.GroupOptionCode1
                    inner join teams as f on b.HomeTeam = f.team
                    inner join teams as g on b.AwayTeam = g.team
                    where b.MatchTime >= '{}' and b.MatchTime <= '{}' and b.time_status = 'Ended'
                    order by a.TournamentText
                    '''.format(DatetimeTop,DatetimeBottom)
            PredictResults = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
            PredictResults.index = PredictResults['MatchTime']
            PredictResults = PredictResults[PredictResults['sn'] == 1]
            if len(PredictResults)>0:
                TournamentTexts = list(set(PredictResults['TournamentText']))
                TournamentTexts.sort(key = list(PredictResults['TournamentText']).index)
                matchtime = []
                for i in range(len(PredictResults)):
                    if PredictResults['TournamentText'].iloc[i] == 'World Cup 2022':
                        time = (PredictResults.index[i].tz_localize('UTC').tz_convert('America/Resolute')).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        time = PredictResults.index[i]
                    matchtime.append(time)
                PredictResults.index = matchtime
                PredictResults.index = pd.to_datetime(PredictResults.index)
                
                PredictResults = PredictResults[(PredictResults.index >= DatetimeTop) & (PredictResults.index <=(datetime.now() - timedelta(days=1)).replace(hour=23, minute=59, second=59).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))]
                Times = sorted(list(set(PredictResults.index)))
                MatchTimes = pd.to_datetime(Times,format='%Y-%m-%d').strftime("%Y-%m-%d").unique()
                alliance = []
                for MatchTime in MatchTimes:
                    for TournamentText in TournamentTexts:
                        message_1x2 = {
                            "type":'全場獲勝'
                        } 
                        message_1x2_main = ''
                        message_1x2_other = ''
                        message_handicap = {
                            "type":'全場讓分'
                        }
                        message_handicap_main = ''
                        message_handicap_other = ''
                        message_total = {
                            "type":'全場大小'
                        }
                        message_total_main = ''
                        message_total_other = ''
                        if TournamentText == 'NPB':
                            PredictResults = PredictResults[PredictResults['HomeScore'] != PredictResults['AwayScore']]
                        for P in range(len(PredictResults)):
                            matchtime_one = PredictResults.index[P].strftime('%Y-%m-%d')
                            if PredictResults['TournamentText'].iloc[P] == TournamentText and matchtime_one == MatchTime:
                                sport_type = PredictResults['Type_cname'].iloc[P]
                                HomeTeam = PredictResults['Home_CTeam'].iloc[P]
                                AwayTeam = PredictResults['Away_CTeam'].iloc[P]
                                homescore = int(PredictResults['HomeScore'].iloc[P])
                                awayscore = int(PredictResults['AwayScore'].iloc[P])
                                option = PredictResults['OptionCode'].iloc[P] 
                                main = PredictResults['main'].iloc[P] 
                                
                                if sport_type == '全場獲勝':
                                    if PredictResults['GroupOptionCode'].iloc[P] == '10':
                                        if option == "1":
                                            if homescore > awayscore:
                                                game_result = '✔️' 
                                            elif homescore < awayscore:
                                                game_result = '❌'
                                            else:
                                                game_result = '❌'
                                        elif option == "2":
                                            if homescore > awayscore:
                                                game_result = '❌' 
                                            elif homescore < awayscore:
                                                game_result = '✔️'
                                            else:
                                                game_result = '❌'
                                        else:
                                            if homescore > awayscore:
                                                game_result = '❌' 
                                            elif homescore < awayscore:
                                                game_result = '❌'
                                            else:
                                                game_result = '✔️'
                                    else:
                                        if option == "1":
                                            if homescore > awayscore:
                                                game_result = '✔️' 
                                            elif homescore < awayscore:
                                                game_result = '❌'
                                            else:
                                                game_result = '❕'
                                        else:
                                            if homescore > awayscore:
                                                game_result = '❌' 
                                            elif homescore < awayscore:
                                                game_result = '✔️'
                                            else:
                                                game_result = '❕'
                                    if main == 1:
                                        message_1x2_main+=f"{game_result}"\
                                                          f"|{HomeTeam}|{homescore} : {awayscore}|{AwayTeam}"\
                                                          f"|{Mapping_OptionCode(PredictResults['OptionCode'].iloc[P],PredictResults['SportCode'].iloc[P],PredictResults['GroupOptionCode'].iloc[P],HomeTeam,AwayTeam)}\n"
                                    else:
                                        message_1x2_other+=f"{game_result}"\
                                                          f"|{HomeTeam}|{homescore} : {awayscore}|{AwayTeam}"\
                                                          f"|{Mapping_OptionCode(PredictResults['OptionCode'].iloc[P],PredictResults['SportCode'].iloc[P],PredictResults['GroupOptionCode'].iloc[P],HomeTeam,AwayTeam)}\n"
                                elif sprot_type == '全場讓分':
                                    SpecialBetValue = float(PredictResults['SpecialBetValue'].iloc[P])
                                    if option == "1":
                                        if homescore + SpecialBetValue > awayscore:
                                            game_result = '✔️' 
                                        elif homescore + SpecialBetValue < awayscore:
                                            game_result = '❌'
                                        else:
                                            game_result = '❕'
                                    else:
                                        if homescore + SpecialBetValue  > awayscore:
                                            game_result = '❌' 
                                        elif homescore + SpecialBetValue  < awayscore:
                                            game_result = '✔️'
                                        else:
                                            game_result = '❕'
                                    if main == 1:
                                        message_handicap_main+=f"{game_result}"\
                                                               f"|{HomeTeam}|{homescore} : {awayscore}|{AwayTeam}"\
                                                               f"|{Mapping_OptionCode(PredictResults['OptionCode'].iloc[P],PredictResults['SportCode'].iloc[P],PredictResults['GroupOptionCode'].iloc[P],HomeTeam,AwayTeam)}\n"
                                    else:
                                        message_handicap_other+=f"{game_result}"\
                                                               f"|{HomeTeam}|{homescore} : {awayscore}|{AwayTeam}"\
                                                               f"|{Mapping_OptionCode(PredictResults['OptionCode'].iloc[P],PredictResults['SportCode'].iloc[P],PredictResults['GroupOptionCode'].iloc[P],HomeTeam,AwayTeam)}\n"
                                elif sprot_type == '全場大小':
                                    SpecialBetValue = float(PredictResults['SpecialBetValue'].iloc[P])
                                    if option == 'Over':
                                        if homescore + awayscore > SpecialBetValue:
                                            game_result = '✔️' 
                                        elif homescore + awayscore < SpecialBetValue:
                                            game_result = '❌'
                                        else:
                                            game_result = '❕'
                                    else:
                                        if homescore + awayscore > SpecialBetValue:
                                            game_result = '❌' 
                                        elif homescore + awayscore < SpecialBetValue:
                                            game_result = '✔️'
                                        else:
                                            game_result = '❕'
                                    if main == 1:
                                        message_total_main+=f"{game_result}"\
                                                            f"|{HomeTeam}|{homescore} : {awayscore}|{AwayTeam}"\
                                                            f"|{Mapping_OptionCode(PredictResults['OptionCode'].iloc[P],PredictResults['SportCode'].iloc[P],PredictResults['GroupOptionCode'].iloc[P],HomeTeam,AwayTeam)}\n"
                                    else:
                                        message_total_other+=f"{game_result}"\
                                                            f"|{HomeTeam}|{homescore} : {awayscore}|{AwayTeam}"\
                                                            f"|{Mapping_OptionCode(PredictResults['OptionCode'].iloc[P],PredictResults['SportCode'].iloc[P],PredictResults['GroupOptionCode'].iloc[P],HomeTeam,AwayTeam)}\n"

                        message_1x2["maingame"] = message_1x2_main
                        message_handicap["maingame"] = message_handicap_main
                        message_total["maingame"] = message_total_main
                        message_1x2["othergame"] = message_1x2_other
                        message_handicap["othergame"] = message_handicap_other
                        message_total["othergame"] = message_total_other
                        PredictResults.index = pd.to_datetime(PredictResults.index.strftime('%Y-%m-%d'))
                        for sport_t in ['全場獲勝','全場讓分','全場大小']:
                            tournamegame = PredictResults[(PredictResults['TournamentText'] == TournamentText) & (PredictResults['Type_cname'] == sport_t) & (PredictResults.index == MatchTime)]
                            total_return = tournamegame['Profit'].sum() - (len(tournamegame[tournamegame['Profit']== 0])*1000) 
                            if sport_t == '全場獲勝':
                                message_1x2["profit"] = total_return
                            elif sport_t == '全場讓分':
                                message_handicap["profit"] = total_return
                            elif sport_t == '全場大小':
                                message_total["profit"] = total_return
                        tournamegame = PredictResults[(PredictResults['TournamentText'] == TournamentText) & (PredictResults.index == MatchTime)]
                        total_return = tournamegame['Profit'].sum() - (len(tournamegame[tournamegame['Profit']== 0])*1000) 
                        message_one ={
                            "date" : MatchTime,
                            "sport":TournamentText,
                            "predictresult" : [message_1x2,message_handicap,message_total],
                            "total_profit" : total_return
                            }
                        alliance.append(message_one)

                if UserId:
                    line_bot_api.push_message(UserId,FlexSendMessage("預測戰績報告",set_PredictResultsFlex(alliance)))
                    return jsonify({'response':f'Successfully pushed {DatetimeTop}~{DatetimeBottom} to {UserId}'})
                else:
                    for m in [False,True]:
                        user_select = get_LineUserMember(maturity = m)
                        if (m == True) and (alliance[0]['total_profit'] <= 0):
                            pass
                        else:
                            pushmember = list(user_select['LineUniqueID'])
                            pushamount = len(pushmember) // 500
                            if pushamount > 0:
                                for amount in range(pushamount): 
                                    pushlistone = pushmember[500*amount:500*(amount+1)]
                                    line_bot_api.multicast(pushlistone,FlexSendMessage("預測戰績報告",set_PredictResultsFlex(alliance)))
                            else:
                                line_bot_api.multicast(pushmember, FlexSendMessage('預測戰績報告', set_PredictResultsFlex(alliance)))
                            
                                
                    return jsonify({'response':f'Successfully pushed {DatetimeTop}~{DatetimeBottom} to all member.'})
            else:
                return jsonify({'response':'No Results need to push.'})
        except Exception as e:
            print(e)  
            return Response(jsonify({'response': [{'Error Info': traceback.format_exc()}]}),status=400)
 
'''
[6]群體或特定會員推播訊息
'''
@app.route("/PushMessage", methods=['GET','POST'])
@auth.login_required
def send_pushmessage():
    auth_username = auth.username()
    if request.method == 'POST':
        member = request.form["member"]
        type_ = request.form["type"]
        content = request.form["content"]
        if member == 'specific':
            member = [request.form["id_"]][0].split("(")[0]
            nickname = [request.form["id_"]][0].split("(")[1].replace(")","")
            SQL = '''
                  SELECT *
                    FROM UserMember as a 
                    inner join LineUserMember as b on a.UserId = b.UserId
                    where member = '{}' and nickname = N'{}'
            '''.format(member,nickname)
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            id_ = list(result['LineUniqueID'])
        else:
            SQL = '''
                SELECT *
                  FROM [dbo].[LineUserMember]
                  where situate != 'ban'
            '''
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            id_ = list(result['LineUniqueID'])
        if type_ == 'text':
            message = TextSendMessage(text = content)
        else:
            json_content = json.loads(content)
            message = FlexSendMessage('Guess365好康報報',json_content)
        pushamount = len(id_) // 500
        if pushamount > 0:
            for amount in range(pushamount): 
                pushlistone = id_[500*amount:500*(amount+1)]
                line_bot_api.multicast(pushlistone, message)
        elif len(id_) == 1:
            line_bot_api.push_message(id_[0], message)
        else:
            line_bot_api.multicast(id_, message)
        return redirect(url_for('send_pushmessage'))
    else:
        SQL = '''
            SELECT member,LineName
            FROM [dbo].[LineUserMember] as a 
            inner join UserMember as b on a.UserId = b.UserId
            where situate != 'ban'
        '''
        result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
        return render_template('pushmessage.html',result = result)
'''
@app.route("/PredictResultsPushMessage", methods=['GET','POST'])
@auth.login_required
def send_PredictResultsPushMessage():
    # 取得驗證帳戶、LineId
    auth_username = auth.username()
    user_select = get_LineUserMember()
    if request.method == 'GET':
        # 檢查是否有填寫參數
        accounts = request.values.get('member')
        DateBetween = request.values.get('DateBetween')
        # 沒填寫accounts，則賦予預設值
        if accounts == None:
            accounts = 'winwin666,adsads2323'
        # DateBetween，則使用無指定路由
        if DateBetween == None:
            PredictResults = requests.get(f'{branch}/PredictResults/{accounts}', auth=(users[0]['username'],users[0]['password_2']),verify=False).text
            PredictResults = json.loads(PredictResults)['responese']
            DateBetween = (datetime.now()- timedelta(days=1)).strftime("%Y-%m-%d")        
        else:
            PredictResults = requests.get(f'{branch}/PredictResults/{accounts}/{DateBetween}', auth=(users[0]['username'],users[0]['password_2']),verify=False).text
            PredictResults = json.loads(PredictResults)['responese']
        return render_template('Predict.html', **locals())

    elif request.method == 'POST':
        content = request.form['content']
        user_select = request.form['user_select']
        selected_icon_text = request.form['selected-text']
        predict_content = request.form['predict_content']
        if content != '' and selected_icon_text != '-1':
            if user_select == '所有人':
                user_select = list(user_select['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, [TextSendMessage(text=content),
                                                         ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                          preview_image_url=f'https://liff.line.me/{domain_name}/static/sticker/{selected_icon_text}.jpg'),
                                                         FlexSendMessage(f'{content}',set_PredictResultsFlex(predict_content))])
                    write_LineBotPushMessage('manual', auth_username, content ,'all')
                    flash('傳送成功(文字+貼圖)')
                else:
                    flash('沒有用戶')
            elif user_select == 'Level-1用戶':
                user_select = list(user_select[user_select['Level']==1]['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, [TextSendMessage(text=content),
                                                         ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                          preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg'),
                                                         FlexSendMessage(f'{content}',set_PredictResultsFlex(predict_content))])
                    write_LineBotPushMessage('manual', auth_username, content,'Level-1')
                    flash('傳送成功(文字+貼圖)')
                else:
                    flash('沒有用戶')
            else:
                user_select = json.loads(user_select.replace('\'','\"'))['LineUniqueID']
                line_bot_api.multicast([user_select], [TextSendMessage(text=content),
                                                       ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                        preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg'),
                                                       FlexSendMessage(f'{content}',set_PredictResultsFlex(predict_content))])
                write_LineBotPushMessage('manual', auth_username, content,user_select)
                flash('傳送成功(文字+貼圖)')
        elif content != '' and selected_icon_text == '-1':
            if user_select == '所有人':
                user_select = list(user_select['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, [TextSendMessage(text=content),
                                                         FlexSendMessage(f'{content}',set_PredictResultsFlex(predict_content))])
                    write_LineBotPushMessage('manual', auth_username, content,'all')
                    flash('傳送成功(文字)')
                else:
                    flash('沒有用戶')
            elif user_select == 'Level-1用戶':
                user_select = list(user_select[user_select['Level']==1]['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, [TextSendMessage(text=content),
                                                         FlexSendMessage(f'{content}',set_PredictResultsFlex(predict_content))])
                    write_LineBotPushMessage('manual', auth_username, content,'Level-1')
                    flash('傳送成功(文字)')
                else:
                    flash('沒有用戶')
            else:
                user_select = json.loads(user_select.replace('\'','\"'))['LineUniqueID']
                line_bot_api.multicast([user_select], [TextSendMessage(text=content),
                                                     FlexSendMessage(f'{content}',set_PredictResultsFlex(predict_content))])
                write_LineBotPushMessage('manual', auth_username, content,user_select)
                flash('傳送成功(文字)')
        elif content == '' and selected_icon_text != '-1':
            if user_select == '所有人':
                user_select = list(user_select['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, [ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                            preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg'),
                                                         FlexSendMessage(f'{content}',set_PredictResultsFlex(predict_content))])
                    flash('傳送成功(貼圖)')
                else:
                    flash('沒有用戶')
            elif user_select == 'Level-1用戶':

                user_select = list(user_select[user_select['Level']==1]['LineUniqueID'])
                if len(user_select) > 0:
                    line_bot_api.multicast(user_select, [ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                            preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg'),
                                                         FlexSendMessage(f'{content}',set_PredictResultsFlex(predict_content))])
                    write_LineBotPushMessage('manual', auth_username, content,'Level-1')
                    flash('傳送成功(貼圖)')
                else:
                    flash('沒有用戶')
            else:
                user_select = json.loads(user_select.replace('\'','\"'))['LineUniqueID']
                line_bot_api.multicast([user_select], [ImageSendMessage(original_content_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg',
                                                                            preview_image_url=f'https://{domain_name}/static/sticker/{selected_icon_text}.jpg'),
                                                       FlexSendMessage(f'{content}',set_PredictResultsFlex(predict_content))])
                write_LineBotPushMessage('manual', auth_username, content,user_select)
                flash('傳送成功(貼圖)')
        else:

            flash('傳送失敗，請填寫文字或貼圖')

        return redirect(url_for('send_PredictResultsPushMessage')+request.form['parameter'])
'''

    

'''
[7]封鎖紀錄
'''
@handler.default()
def default(event):
    newLineUniqueID = event.source.user_id
    update_SQL = '''
        UPDATE [dbo].[LineUserMember] 
            SET ModifyTime = '{0}',Situate = 'ban',banned = 'Yes',banTime = '{0}'
            where LineUniqueID = '{1}'
    '''.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
               newLineUniqueID)
    cursor = g.conn_Guess365.cursor()
    cursor.execute(update_SQL)
    cursor.commit() 
'''
[8]登入功能
'''
#LIFF靜態頁面
@app.route('/page')
def page():
    auth_username = users[0]['username']
    auth_password = users[0]['password_2']
    return render_template('index.html',liffid = liffid, domain_name=domain_name, username=auth_username,  password=auth_password)

@app.route('/login', methods=['POST'])
@auth.login_required
def Login():
    data = request.get_json()
    text = data.get('text')
    response = manageForm(text)
    return jsonify({'response':response})

'''
'''
@app.route('/addlinebot', methods=['GET'])
def lineadd():
    state = request.values.get('liff.state')
    return redirect('https://liff.line.me/1645278921-kWRPP32q/?accountId=206owzmt')

'''
[9] LINE PAY LIFF
'''
@app.route('/linepay', methods=['GET'])
def redirect_to_linepay():
    state = request.values.get('liff.state')[1:].split('&')
    url = do_request_payment(state)
    if url == '您已加值過該方案':
        return '您已加值過該方案'
    return redirect(url)

def get_auth_signature (secret, uri, body, nonce):
    """
    用於製作密鑰
    :param secret: your channel secret
    :param uri: uri
    :param body: request body
    :param nonce: uuid or timestamp(時間戳)
    :return:
    """
    str_sign = secret + uri + body + nonce
    return base64.b64encode(hmac.new(str.encode(secret), str.encode(str_sign), digestmod=hashlib.sha256).digest()).decode("utf-8")

def do_request_payment(state):
    userid = state[0]
    name = state[1]
    price = str(int(float(state[2])))
    days = str(int(float(state[3])))
    '''僅使用文檔中必填的資料'''
    request_options = {
        "amount": price,
        "currency": 'TWD',
        "orderId": g.nonce,
        "packages": [{
            "id": 'NBA202223',
            "amount": price,
            "name": f'{name}大數據預測機器人',
            "products": [{
                "name": f'{name}大數據預測機器人',
                "quantity": 1,
                "price": price,
                "imageUrl" : f'https://{domain_name}/static/banner/{name}.png?timestamp={g.timestamp}'
            }]
        }],
        "redirectUrls": {
            "confirmUrl": f'https://liff.line.me/{linepay_check}',
            "cancelUrl": 'https://guess365.cc/linebot'
        }
    }
    json_body = json.dumps(request_options)

    g.headers['X-LINE-Authorization-Nonce'] = g.nonce
    g.headers['X-LINE-Authorization'] = get_auth_signature(channel_secret, uri, json_body,g.nonce)
    response = requests.post("https://sandbox-api-pay.line.me"+uri, headers=g.headers, data=json_body)
    dict_response = json.loads(response.text)
    if dict_response.get('returnCode') == "0000":
        info = dict_response.get('info')
        web_url = info.get('paymentUrl').get('web')
        transaction_id = str(info.get('transactionId'))
        print(f"付款web_url:{web_url}")
        print(f"交易序號:{transaction_id}")
        
        SQL = '''
            SELECT *,ROW_NUMBER() over (partition BY subscribeLevel order by SubscribeStart_dd desc) sn
            FROM [dbo].[LineSubscription] as a
            where UesrId = '{}' and SubscribeLevel = '{}'
            ORDER BY SubscribeStart_dd DESC
        '''.format(UserId,name)
        result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
        result = result[result['sn'] == 1]
        if len(result) > 0:
            if result['isPayment'].iloc[0] == 'No':
                if result['SubscribeStart_dd'].iloc[0].strftimetime("%Y-%m-%d") == datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'):
                    Insert_SQL = '''
                        update LineSubscription set SubscribeStart_dd = '{}' where id = '{}'
                    '''.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                          result['id'].iloc[0])
                else:
                    Insert_SQL = """
                        INSERT INTO LineSubscription (SubscribeLevel,SubscribeStart_dd,isPayment,UesrId,transactionId,orderId) 
                            values ('{}','{}','No','{}','{}','{}')
                    """.format(name,
                               datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                               userid,
                               transaction_id,
                               request_options['orderId'])
            else:
                return '您已加值過該方案'
        else:
            Insert_SQL = """
                INSERT INTO LineSubscription (SubscribeLevel,SubscribeStart_dd,isPayment,UesrId,transactionId,orderId) 
                    values ('{}','{}','No','{}','{}','{}')
            """.format(name,
                       datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                       userid,
                       transaction_id,
                       request_options['orderId'])
        cursor = g.conn_Guess365.cursor()
        cursor.execute(Insert_SQL)
        cursor.commit()
        return web_url
    
    
'''
[10] LINE PAY CHECK LIFF
'''
@app.route('/linepaycheck')
def redirect_to_linepaycheck():
    auth_username = users[0]['username']
    auth_password = users[0]['password_2']
    return render_template('付款完成.html',liffid = linepay_check, domain_name=domain_name, username=auth_username,  password=auth_password)


@app.route('/trackorder', methods=['POST'])
@auth.login_required
def trackorder():
    data = request.get_json()
    text = data.get('text').split("/")
    transactionid = text[0]
    orderid = text[1]
    lineuserid = text[2]
    UserId = get_UserMemberInfo(lineuserid)['UserId']
    SQL = '''
    SELECT *
       FROM [dbo].[LineSubscription] as a
       inner join LineSubscriptionDisplayParameters as b on a.SubscribeLevel = b.code
      where transactionId = '{}' and orderId = '{}' and UesrId = '{}'
    '''.format(transactionid,orderid,UserId)
    result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    if len(result) != 0:
        price = int(float(result['price'].iloc[0]))
        status = do_checkout(transactionid,price)  # 檢查訂單狀態
        if status == True:
            confirm = do_confirm(transactionid,price)  # 確認訂單
            if confirm == True:
                day = result['days']
                update_SQL = """
                     update LineSubscription set SubscribeStart_dd = '{0}'SubscribeEnd_dd = '{1}',isPayment = 'Yes',Payment_dd = '{1}' 
                         where UesrId = '{1}' and transactionId = '{2}' and orderId = '{3}'
                """.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                           
                           UserId,
                           transactionid,
                           orderid)
                cursor = g.conn_Guess365.cursor()
                cursor.execute(update_SQL)
                cursor.commit()
                
                return "success"
            else:
                return "error1"
        else:
            return "error2"
    else:
        return "error3"

def do_checkout(transaction_id,price):
    conf_data = '''{}"amount": {}, "currency": "TWD"{}'''.format('{',price,'}')
    checkout_url = f"/v3/payments/requests/{transaction_id}/check"
    g.headers['X-LINE-Authorization'] = get_auth_signature(channel_secret, checkout_url, conf_data, g.nonce)
    response = requests.get("https://sandbox-api-pay.line.me"+checkout_url, headers=g.headers, data=conf_data)
    response = json.loads(response.text)
    if str(response.get('returnCode')) == "0110":
        return True
    return False

def do_confirm(transaction_id,price):

    con_url = f"/v3/payments/{transaction_id}/confirm"
    conf_data = '''{}"amount": {}, "currency": "TWD"{}'''.format('{',price,'}')
    g.headers['X-LINE-Authorization'] = get_auth_signature(channel_secret, con_url, conf_data, g.nonce)
    response = requests.post("https://sandbox-api-pay.line.me"+con_url, headers=g.headers, data=conf_data)

    response = json.loads(response.text)
    if str(response.get('returnCode')) == "0000":
        return True
    return False

'''
[11]訂閱信箱
'''
#LIFF靜態頁面
@app.route('/SubcribeEmail')
def SubcribeEmail():
    auth_username = users[0]['username']
    auth_password = users[0]['password_2']
    return render_template('Linemail.html',liffid = '1657119443-MgX9BxBA', domain_name=domain_name, username=auth_username,  password=auth_password)

@app.route('/checkemail', methods=['POST'])
@auth.login_required
def checkemail():
    data = request.get_json()
    text = data.get('text')
    flist = text.split('/')
    email = flist[0]
    newLineUniqueID = flist[1]
    SQL = '''
         SELECT a.UserId,a.member,a.nickname,a.Email,b.LineUniqueID,b.LineName,c.SubscribeLevel,c.SubscribeStart_dd,c.SubscribeEnd_dd,c.Payment_dd,c.isPayment,d.Email_subscription
          FROM Line_config as d,[dbo].[UserMember] as a
          full outer join LineUserMember as b on a.UserId = b.userid
          inner join LineSubscription as c on a.UserId = c.UesrId
          ORDER by CreatedTime desc
    '''
    result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    if email not in set(result['Email']):
        member = result[(result['LineUniqueID'] == newLineUniqueID)]
        #判斷信箱是否被綁定過
        if list(set(member['Email']))[0] is None:
            update_SQL1 = '''
                update UserMember set Email='{}' where UserId = '{}'    
            '''.format(email,member['UserId'].iloc[0])
            #贈於7天免費接收預測
            email_subscription = list(set(result['Email_subscription']))[0]
            insubscription = member[(member['SubscribeLevel'] == email_subscription) &(member['SubscribeEnd_dd'] > datetime.now()) & (member['isPayment'] == 'Yes')]
            if len(insubscription) > 0:
                subscribe_end = insubscription['SubscribeEnd_dd'].iloc[0]
                subscribedate = (subscribe_end+timedelta(7)).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999')
                update_SQL2 = '''  
                    update LineSubscription set SubscribeEnd_dd = '{}' where UesrId = '{}' and SubscribeLevel = '{}'
                '''.format(subscribedate,
                    member['UserId'].iloc[0],
                    email_subscription)
            else:
                subscribe_free = member[(member['SubscribeLevel'] == 'free')]
                if len(subscribe_free) == 0:
                    update_SQL2 ='''
                        insert into LineSubscription (SubscribeLevel,SubscribeStart_dd,SubscribeEnd_dd,isPayment,Payment_dd,UesrId) values 
                            ('free','{0}','{1}','Yes','{0}','{2}')
                    '''.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                              (datetime.now()+timedelta(7)).astimezone(timezone(timedelta(hours=8))).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999'),
                              member['UserId'].iloc[0])
                else:
                    subscribe_end = subscribe_free['SubscribeEnd_dd'].iloc[0]
                    if subscribe_end > datetime.now():
                        subscribedate = (subscribe_end+timedelta(7)).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999')
                    else:
                        subscribedate = (datetime.now()+timedelta(7)).astimezone(timezone(timedelta(hours=8))).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999')
                    update_SQL2 = '''  
                        update LineSubscription set SubscribeEnd_dd = '{}' where UesrId = '{}' and SubscribeLevel = 'free'
                    '''.format(subscribedate,
                        member['UserId'].iloc[0])
            update_SQL = update_SQL1 + "\n" + update_SQL2
            cursor = g.conn_Guess365.cursor()
            cursor.execute(update_SQL)
            cursor.commit() 
            response = 'success'
        else:
            response = 'error2'
    else:
        response = 'error1'
    print(response)
    return jsonify({'response':response})

'''
[12]寄送資訊
'''
#LIFF靜態頁面
@app.route('/send_info', methods=['GET'])
def sendinfo():
    orderId = request.values.get('orderId')
    auth_username = users[0]['username']
    auth_password = users[0]['password_2']
    return render_template('send_information.html',liffid = '1657119443-26AdkxkG', domain_name=domain_name,orderId=orderId, username=auth_username,  password=auth_password)

@app.route('/send_check', methods=['POST'])
@auth.login_required
def sendcheck():
    data = request.get_json()
    text = data.get('text').split("/")
    orderid = text[0]
    username = text[1]
    address = text[2]
    phone = text[3]
    lineuniqueId = text[4]
    SQL = '''
        SELECT * FROM  GPlusStore_buyer where id = '{}'
    '''.format(orderid)
    result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    if result['Delivery_Status'].iloc[0] == 2:
        response = 'error4'
    elif username == '':
        response = 'error1'
    elif address == '':
        response = 'error2'
    elif phone == '':
        response = 'error3'
    else:
        update_sql = '''
                    update GPlusStore_buyer set 
                        Delivery_Status = '2' ,Name = N'{}',Address = N'{}',phone = '{}',FormDate = '{}'
                        where id = '{}'
                '''.format(username,
                           address,
                           phone,
                           datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                           orderid 
                          )
        print(update_sql)
        cursor = g.conn_Guess365.cursor()
        cursor.execute(update_sql)
        cursor.commit()
        response = 'success'
    return jsonify({'response':response})

'''
[13]LineBot訊息回覆設定
'''
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    newLineUniqueID = event.source.user_id
    mtext = event.message.text

    if mtext == '@登入會員':
        try:
            newLineUniqueID, UserId,situate = get_LineUserMember(LineUniqueID=newLineUniqueID)
            if newLineUniqueID != None and UserId == None and situate == 'join' :
                flex_message = TextSendMessage(text="請選擇要查詢的會員資訊", 
                                            quick_reply=QuickReply(items=[ 
                                                QuickReplyButton(action=URIAction(label="會員登入", uri=f'https://liff.line.me/{liffid}')),
                                                QuickReplyButton(action=PostbackAction(label="玩法規則", data="@登入會員=已經登入")),
                                                QuickReplyButton(action=URIAction(label="FB粉絲專頁", uri=f'https://liff.line.me/1657119443-A6P8papON')),
                                            ]))
                
            else:
                flex_message = TextSendMessage(text="請選擇要查詢的會員資訊", 
                                            quick_reply=QuickReply(items=[ 
                                                QuickReplyButton(action=PostbackAction(label="會員中心", data="@登入會員=關於我")),
                                                QuickReplyButton(action=PostbackAction(label="玩法規則", data="@登入會員=已經登入")),
                                                QuickReplyButton(action=URIAction(label="FB粉絲專頁", uri=f'https://liff.line.me/1657119443-A6P8papO')),
                                            ]))
            line_bot_api.reply_message(event.reply_token, flex_message)
            
        except Exception as e: 
            print(e)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif mtext == '@好手PK':
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            try:
                flex_message = TextSendMessage(text="請選擇要執行的項目", 
                                                quick_reply=QuickReply(items=[ 
                                                    QuickReplyButton(action=PostbackAction(label="PK商城", data = "@好手PK=PK商城")),
                                                    QuickReplyButton(action=PostbackAction(label="我要PK", data="@好手PK=我要PK")),
                                                    QuickReplyButton(action=PostbackAction(label="PK戰績", data = "@好手PK=查詢戰績")),
                                                    QuickReplyButton(action=PostbackAction(label="兌換查詢", data='@好手PK=兌換查詢')),    
                                                ]))
                line_bot_api.reply_message(event.reply_token, flex_message)
            except:

                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif mtext == '@我要PK':
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            plays = get_PlayerPKGame()
            set_PlayerPKFlexTemplateMessage(event=event,plays=plays) 
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請先登入！'))
        
    elif mtext == '@賽事查詢':
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            flex_message = TextSendMessage(text="請選擇要查詢的時間", 
                                            quick_reply=QuickReply(items=[ 
                                                QuickReplyButton(action=PostbackAction(label="昨日賽果", data="@賽事時間=昨日")),
                                                QuickReplyButton(action=PostbackAction(label="今日賽事", data = "@賽事時間=今日")),
                                                QuickReplyButton(action=PostbackAction(label="明日賽事", data = "@賽事時間=明日")),
                                            ]))
            line_bot_api.reply_message(event.reply_token, flex_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif mtext == '@關於我':
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            FlexMessage = set_UserMemberInfo(event, UserMemberInfo)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('關於我', FlexMessage))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif mtext == '@pay':
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            FlexMessage = subscriptionlist(UserMemberInfo)
            if FlexMessage['contents'] == 'nogame':
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='恭喜你已購買所有方案，如有最新方案將即時通知您'))
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('LINE PAY', FlexMessage))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif mtext == '@LINEBOT戰績查詢':
        flex_message = TextSendMessage(text="請選擇要查詢的賽事戰績", 
                                            quick_reply=QuickReply(items=[ 
                                                QuickReplyButton(action=PostbackAction(label="NBA", data="@AI機器人=NBA")),
                                                QuickReplyButton(action=MessageAction(label="敬請期待", text = "敬請期待，目前團隊正在開發歐足、MLB、NPB等賽事之預測機器人，如有更多想了解之問題或賽事，皆可直接詢問小編唷!!")),
                                            ]))
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif mtext == '@訂閱資訊':
        flex_message = TextSendMessage(text="請選擇要訂閱的聯盟", 
                                            quick_reply=QuickReply(items=[ 
                                                QuickReplyButton(action=PostbackAction(label="NBA", data="@cycle=NBA")),
                                                QuickReplyButton(action=PostbackAction(label="NPB", data = "@cycle=NPB")),
                                            ]))
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif mtext == '@訂閱Email':
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            if UserMemberInfo['email'] is None:
                email_flex= subscribe_email()
                line_bot_api.reply_message(event.reply_token, FlexSendMessage('限時綁定電子報', email_flex))
            else:
                SQL = '''
                     SELECT * FROM Line_config 
                '''
                result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
                email_subscription = result['Email_subscription'].iloc[0]
                if email_subscription in list(UserMemberInfo['SubscribeLevel']):
                    index = list(UserMemberInfo['SubscribeLevel']).index(email_subscription)
                    SubscribeEnd_dd = UserMemberInfo['SubscribeEnd_dd'].iloc[index]
                    ispayment = UserMemberInfo['isPayment'].iloc[index]
                    if (SubscribeEnd_dd > datetime.now()) & (ispayment == 'Yes'):
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='您已填寫過Email囉，感謝您的支持!!'))
                    else:
                        Flex_remit = json.load(open('static/remit.json', 'r', encoding='utf-8'))
                        Flex_remit['hero']['contents'][0]['url'] = f"https://{domain_name}/static/banner/remit_have_email.png"
                        line_bot_api.reply_message(event.reply_token,FlexSendMessage('訂閱資訊', Flex_remit))
                else:
                    Flex_remit = json.load(open('static/remit.json', 'r', encoding='utf-8'))
                    Flex_remit['hero']['contents'][0]['url'] = f"https://{domain_name}/static/banner/remit_email.png"
                    line_bot_api.reply_message(event.reply_token,FlexSendMessage('訂閱資訊', Flex_remit))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif mtext == '@成功訂閱電子報':
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            FlexMessage = set_UserMemberInfo(event, UserMemberInfo)
            Flex_remit = json.load(open('static/remit.json', 'r', encoding='utf-8'))
            Flex_remit['hero']['contents'][0]['url'] = f"https://{domain_name}/static/banner/remit_email.png"
            line_bot_api.reply_message(event.reply_token, [FlexSendMessage('關於我', FlexMessage),FlexSendMessage('訂閱資訊', Flex_remit)])
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif mtext == '@使用教學':
        Flex_instruction = json.load(open('static/instruction.json', 'r', encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token,FlexSendMessage('使用教學', Flex_instruction))
    elif 'https://liff.line.me/1645278921-kWRPP32q/?accountId=206owzmt' in mtext:
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        createdtime = UserMemberInfo['CreatedTime']
        recommender = UserMemberInfo['recommender']
        member = UserMemberInfo['member']
        if UserMemberInfo['UserId'] != None:
            if recommender == None:
                recommender = mtext.split("(")[1].split(")")[0]
                SQL = '''
                     SELECT b.*
                      FROM [dbo].[UserMember] as a
                      inner join LineUserMember as b on a.UserId = b.UserId
                      where member = '{}' and a.dd < '{}'
                '''.format(recommender,createdtime)
                result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
                if recommender != member:
                    if len(result) != 0:
                        recommender_userid = result['UserId'].iloc[0]
                        recommender_lineid = result['LineUniqueID'].iloc[0]
                        update_SQL = '''  
                            UPDATE LineUserMember SET recommender = '{}' where UserId = '{}' 
                        '''.format(recommender_userid,
                            UserMemberInfo['UserId'])
                        cursor = g.conn_Guess365.cursor()
                        cursor.execute(update_SQL)
                        cursor.commit() 
                        text_berecommender = '''Hi~我們收到您的回傳囉\U0001F60A，待試用滿10天，即可獲得一張35元 7-11咖啡提貨券！屆時將由客服將獎品以URL連結方式傳送給您的Line帳號，記得幫我們打開通知，才不會錯過唷!'''
                        text_recommender = '''Hi~我們收到{}將您設為推薦人囉\U0001F60A，待其試用滿10天，您即可獲得一張50元 7-11禮券！屆時將由客服將獎品以URL連結方式傳送給您的Line帳號，記得幫我們打開通知，才不會錯過唷！'''.format(member)
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text_berecommender))
                        line_bot_api.push_message(recommender_lineid,TextSendMessage(text=text_recommender))
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='您填寫之會員帳號不存在，或其晚於您加入會員，請再次確認！'))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='推薦人不可以填寫自己唷!!'))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='您已填寫過推薦人'))
                
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif mtext == '@GPlus商城':
        image_message = ImagemapSendMessage(
            base_url=f'https://{domain_name}/static/banner/gplus_store.jpg#1040',
            alt_text='PK商城',
            base_size=BaseSize(height=1040, width=1040),
            actions=[
                MessageImagemapAction(
                    text='確定要兌換「Nintendo Switch」?',
                    area=ImagemapArea(
                        x=0, y=0, width=520, height=520
                    )
                ),
                MessageImagemapAction(
                    text='確定要兌換「AirPods 3代」?',
                    area=ImagemapArea(
                        x=520, y=0, width=520, height=520
                    )
                ),
                MessageImagemapAction(
                    text='確定要兌換「Linebot賽事預測」?',
                    area=ImagemapArea(
                        x=0, y=520, width=520, height=520
                    )
                ),
                MessageImagemapAction(
                    text='確定要兌換「國賓電影票」?',
                    area=ImagemapArea(
                        x=520, y=520, width=520, height=520
                    )
                )
              ]
        )
        line_bot_api.reply_message(event.reply_token, image_message)
    elif '確定要兌換' in mtext:
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            merchandise = mtext[6:].replace("」?","")
            SQL = '''
                SELECT a.*,b.id as orderId,b.UserId,b.Delivery_Status
                  FROM [dbo].[GPlusStore] AS A
                  FULL OUTER JOIN GPlusStore_buyer as b on a.id = b.merchandise_id
                  where merchandise = N'{}'
            '''.format(merchandise)
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            successfulexchange = len(result[result['Delivery_Status'] != 0])
            merchandise_gplus = result['GPlus'].iloc[0]
            if UserMemberInfo['gplus'] < merchandise_gplus:
                gplusdiff = merchandise_gplus - UserMemberInfo['gplus']
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'抱歉，您的GPlus幣不足{gplusdiff}元，請選擇其它商品進行兌換\U0001F60A'))
            elif (result['UserId'].iloc[0] != None) & (successfulexchange >= result['inventory'].iloc[0]):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='抱歉，該商品已被兌換完畢，將盡快上架新貨，敬請期待!!'))
            else:
                insert_sql = '''
                    insert into GPlusStore_buyer 
                  (UserId,CreatedTime,Delivery_Status,merchandise_id)
                  OUTPUT Inserted.id
                  values 
                  ('{}','{}','0','{}')   
                '''.format(UserMemberInfo['UserId'],
                          datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                          result['Id'].iloc[0])
                print(insert_sql)
                cursor = g.conn_Guess365.cursor()
                cursor.execute(insert_sql)
                cursor.commit()
                orderId = pd.read_sql(sql=insert_sql,con=g.conn_Guess365,coerce_float=True)['id'].iloc[0] -1
                print(orderId)
                exchangecheck_flex = exchangecheck(result['merchandise'].iloc[0],result['price'].iloc[0],result['GPlus'].iloc[0],orderId)
                print(exchangecheck_flex)
                line_bot_api.reply_message(event.reply_token,FlexSendMessage(f'確認兌換{merchandise}?', exchangecheck_flex))
                
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif mtext == '@查詢即時比分':
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            tournametext = sql_SearchLastGame(day=0)
            QRButton = []
            for game in range(len(tournametext)):
                QuickR = [QuickReplyButton(action=PostbackAction(label=tournametext['CName'][game], data=f"@賽事進行中={tournametext['TournamentText'][game]}|{tournametext['CName'][game]}"))]
                QRButton += QuickR
            flex_message = TextSendMessage(text="請選擇要查詢的賽事聯盟",
                                        quick_reply=QuickReply(items=QRButton))
            line_bot_api.reply_message(event.reply_token, flex_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    
    elif (('@成功填寫' in mtext) or ('@已填寫過' in mtext)) and ('寄送資訊' in mtext):
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            orderId = mtext.split(":")[1].replace('的寄送資訊','')
            merchandise_status_flex = merchandise_status(UserMemberInfo['UserId'],orderId)
            line_bot_api.reply_message(event.reply_token,FlexSendMessage(f'兌換商品狀況', merchandise_status_flex))
            message = '{}({})已成功填寫PK商城商品(編號:{})寄送資訊，請儘速確認!!'.format(UserMemberInfo['nickname'],UserMemberInfo['UserId'],orderId)
            line_bot_api.multicast(['U5eeaccf2a166d213fa1f693bad471c7d','U7e526688657cc2479ffec97f86a14a1d'], TextSendMessage(text=message))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif '@訂單查詢' in mtext:
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            orderId = mtext.split(":")[1]
            merchandise_status_flex = merchandise_status(UserMemberInfo['UserId'],orderId)
            line_bot_api.reply_message(event.reply_token,FlexSendMessage(f'兌換商品狀況', merchandise_status_flex))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    else:
        write_ReplyMessage(mtext, newLineUniqueID)
        
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    pass

@handler.add(MessageEvent, message=VideoMessage)
def handle_message(event):
    pass

@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):
    pass

@handler.add(MessageEvent, message=StickerMessage)
def handle_message(event):
    pass

@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    pass

@handler.add(PostbackEvent)
def handle_postback(event):
    newLineUniqueID = event.source.user_id
    backdata = dict(parse_qsl(event.postback.data))
    alreadylogin = backdata.get('@登入會員')
    pk = backdata.get('@好手PK')
    payment = backdata.get('@加值套餐')
    pkselect = backdata.get('@PK選擇')
    pkinviteselect = backdata.get('@PK邀請選擇')
    searchother = backdata.get('@查詢他人戰績')
    selecttime = backdata.get('@賽事時間')
    selectalliance = backdata.get('@聯盟選擇')
    selectgroup = backdata.get('@盤口選擇')
    selecttoday= backdata.get('@今日選擇')
    aboutAI = backdata.get('@獲利績效') 
    remit_cycle = backdata.get('@cycle')
    remit = backdata.get('@remit')
    playing_match = backdata.get('@賽事進行中')
    exchange = backdata.get('@exchange')
    successorder = backdata.get('@完成訂單')
    exchangeId = backdata.get('@兌換ID')
    exchangeStatus = backdata.get('@兌換狀況')
    invitefriend = backdata.get('@邀請好友加入')

    
    if payment:
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            add_LineBotAutoPrediction(UserMemberInfo['UserId'],payment)
            combo = {"free":"免費" , "gold" : "黃金" , "platinum" : "鑽石"}
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'成功購買「{combo[payment]}」方案！'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif pkselect:
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            data = json.loads(pkselect.replace('[','{').replace(']','}').replace('\'','\"'))
            isSuccess,pkid = add_LinePlayerPK(UserMemberInfo['UserId'],data,event)
            if isSuccess:
                profile = line_bot_api.get_profile(newLineUniqueID)
                headshot = profile.picture_url
                user = UserMemberInfo['UserId']
                SaveHeadshot(headshot,user)
                FlexMessage = set_CheckFlex(data,pkid)
                line_bot_api.reply_message(event.reply_token, FlexSendMessage('確認PK挑選',FlexMessage))
                Match_PK = match_pk.Match_PK(g.conn_Guess365)
                Match_PK.comply_match()
                
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif alreadylogin:
        if alreadylogin == '已經登入':
            FlexMessage = json.load(open('static/alreadyconnect.json', 'r', encoding='utf-8'))
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(f'Guess365 Linebot遊戲規則', FlexMessage))
        elif alreadylogin == '關於我':
            UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
            if UserMemberInfo['UserId'] != None:
                FlexMessage = set_UserMemberInfo(event, UserMemberInfo )
                line_bot_api.reply_message(event.reply_token, FlexSendMessage('關於我', FlexMessage))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
        elif alreadylogin == '請先登入':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif pk:
        if pk == '我要PK':
            plays = get_PlayerPKGame()
            set_PlayerPKFlexTemplateMessage(event=event,plays=plays)
        elif pk == '查詢戰績':
            UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
            get_PlayerPKStandings(UserMemberInfo['UserId'], event,UserMemberInfo)
        elif pk == 'PK商城':
            image_message = ImagemapSendMessage(
            base_url=f'https://{domain_name}/static/banner/gplus_store.jpg#1040',
            alt_text='PK商城',
            base_size=BaseSize(height=1040, width=1040),
            actions=[
                MessageImagemapAction(
                    text='確定要兌換「Nintendo Switch」?',
                    area=ImagemapArea(
                        x=0, y=0, width=520, height=520
                    )
                ),
                MessageImagemapAction(
                    text='確定要兌換「AirPods 3代」?',
                    area=ImagemapArea(
                        x=520, y=0, width=520, height=520
                    )
                ),
                MessageImagemapAction(
                    text='確定要兌換「Linebot賽事預測」?',
                    area=ImagemapArea(
                        x=0, y=520, width=520, height=520
                    )
                ),
                MessageImagemapAction(
                    text='確定要兌換「國賓電影票」?',
                    area=ImagemapArea(
                        x=520, y=520, width=520, height=520
                    )
                )
              ]
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        elif pk == '兌換查詢':
            UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
            delivering,successful,cancel = search_orderId(UserMemberInfo['UserId'])
            QRButton = []
            for listId,title in zip([delivering,successful,cancel],['進行中','已完成','不成立']):  
                if len(listId) > 0:
                    QuickR = [QuickReplyButton(action=PostbackAction(label=title, data=f"@兌換ID={UserMemberInfo['UserId']}|{listId}"))]
                    QRButton += QuickR
            if (len(delivering) == 0) & (len(successful) == 0) & (len(cancel) == 0):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='目前無任何兌換紀錄，多多參加「我要PK」換好禮吧!!'))
            else:
                flex_message = TextSendMessage(text="請選擇要查詢的訂單狀況",quick_reply=QuickReply(items=QRButton))
                line_bot_api.reply_message(event.reply_token, flex_message)
            
    elif exchangeId:
        userid = exchangeId.split("|")[0]
        orderid = eval(exchangeId.split("|")[1])
        QRButton = []
        for i in orderid:  
            QuickR = [QuickReplyButton(action=PostbackAction(label=f'訂單編號:{i}', data=f"@兌換狀況={userid}|{i}"))]
            QRButton += QuickR
        flex_message = TextSendMessage(text="請選擇要查詢的訂單ID",
                                    quick_reply=QuickReply(items=QRButton))
        line_bot_api.reply_message(event.reply_token, flex_message)
    
    elif exchangeStatus:
        userId = exchangeStatus.split("|")[0]
        orderId = exchangeStatus.split("|")[1]
        merchandise_status_flex = merchandise_status(userId,orderId)
        line_bot_api.reply_message(event.reply_token,FlexSendMessage(f'兌換商品狀況', merchandise_status_flex))
    elif pkinviteselect:
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            data = json.loads(pkinviteselect.replace('[','{').replace(']','}').replace('\'','\"'))
            isSuccess = update_invite_LinePlayerPK(UserMemberInfo['UserId'],data,event)
            if isSuccess:
                PKMatchFlex = set_PKMatchFlex(UserMemberInfo['UserId'],data,ToUser=2)
                Match_PK = match_pk.Match_PK(g.conn_Guess365)
                Match_PK.matchPK(data,UserMemberInfo['UserId'])
                all_member = get_member()
                member = all_member[all_member['UserId'] == data['UserId1']]['member'].iloc[0]
                line_bot_api.reply_message(event.reply_token, FlexSendMessage( f"您成功接受{member}挑戰", PKMatchFlex))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif searchother:
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        if UserMemberInfo['UserId'] != None:
            data = json.loads(searchother.replace('[','{').replace(']','}').replace('\'','\"'))
            get_PlayerPKStandings(data['UserId'],event,UserMemberInfo,other = True)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
    elif selecttime:
        if  selecttime == '昨日':
            search_day = -1
            tournametext = sql_SearchLastGame(day=search_day)
        elif selecttime == '今日':
            search_day = 0
            tournametext = sql_SearchLastGame(day=search_day)
        elif selecttime == '明日':
            search_day = 1
            tournametext = sql_SearchLastGame(day=search_day)
        QRButton = []
        for game in range(len(tournametext)):
            QuickR = [QuickReplyButton(action=PostbackAction(label=tournametext['CName'][game], data=f"@聯盟選擇={search_day}|{tournametext['TournamentText'][game]}|{tournametext['CName'][game]}"))]
            QRButton += QuickR
        flex_message = TextSendMessage(text="請選擇要查詢的賽事聯盟",
                                    quick_reply=QuickReply(items=QRButton))
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif selectalliance:
        day = selectalliance.split("|")[0]
        sport = selectalliance.split("|")[1]
        cname = selectalliance.split("|")[2]
        if int(day) == -1:
            ResultFlex = SearchMatchResult(int(day),sport)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage( f"查詢{cname}最新賽果", ResultFlex))
        elif int(day) == 0: 
            all_match = search_match(sport)
            #已完賽
            match_over = all_match[(all_match.index <= datetime.now()) & (all_match['HomeScore'] != 'None') & (all_match['AwayScore'] != 'None')]
            #未開賽
            match_notstart = all_match[all_match.index > datetime.now()]
            if (len(match_over) == 0) & (len(match_notstart) == 0):
                flex_message = TextSendMessage(text="本日賽事皆開賽且尚未有任何賽果，請稍後再查詢")
            elif len(match_over) == 0:
                QuickR = [QuickReplyButton(action=PostbackAction(label="未開賽", data=f"@今日選擇={selectalliance}|未開賽事"))]
                flex_message = TextSendMessage(text="請選擇要查詢的部分",
                                        quick_reply=QuickReply(items=QuickR))
            elif len(match_notstart) == 0:
                QuickR = [QuickReplyButton(action=PostbackAction(label="已完賽", data=f"@今日選擇={selectalliance}|已開賽事"))]
                flex_message = TextSendMessage(text="請選擇要查詢的部分",
                                        quick_reply=QuickReply(items=QuickR))
            else:
                QuickR = [QuickReplyButton(action=PostbackAction(label="未開賽", data=f"@今日選擇={selectalliance}|未開賽事")),
                          QuickReplyButton(action=PostbackAction(label="已完賽", data=f"@今日選擇={selectalliance}|已開賽事"))]
                flex_message = TextSendMessage(text="請選擇要查詢的部分",
                                        quick_reply=QuickReply(items=QuickR))
 
            line_bot_api.reply_message(event.reply_token, flex_message)
        
        else:
            groupoption = search_groupoption(sport,day)
            QRButton = []
            for group in groupoption['Type_cname']:  
                QuickR = [QuickReplyButton(action=PostbackAction(label=group, data=f"@盤口選擇={selectalliance}|{group}"))]
                QRButton += QuickR
            flex_message = TextSendMessage(text="請選擇要查詢的盤口",
                                        quick_reply=QuickReply(items=QRButton))
            line_bot_api.reply_message(event.reply_token, flex_message)
    elif selectgroup:
        day = selectgroup.split("|")[0]
        sport = selectgroup.split("|")[1]
        cname = selectgroup.split("|")[2]
        groupoption = selectgroup.split("|")[3]
        option,groupoptioncode = Searchoption(sport,groupoption)
        SearchMatch = SearchMatchEntry(day,sport,option,groupoptioncode)
        MatchEntry_Flex = MatchEntryFlex(day,sport,cname,option,groupoption,groupoptioncode,SearchMatch)    
        return line_bot_api.reply_message(event.reply_token, FlexSendMessage( f"查詢{cname}最新賽事", MatchEntry_Flex))
    elif selecttoday:
        try:
            day = selecttoday.split("|")[0]
            sport = selecttoday.split("|")[1]
            cname = selecttoday.split("|")[2]
            option = selecttoday.split("|")[3]
            if option == '已開賽事':
                ResultFlex = SearchMatchResult(0,sport)
                line_bot_api.reply_message(event.reply_token, FlexSendMessage( f"查詢{cname}最新賽果", ResultFlex))
            else:
                groupoption = search_groupoption(sport,day)
                QRButton = []
                for group in groupoption['Type_cname']:  
                    QuickR = [QuickReplyButton(action=PostbackAction(label=group, data=f"@盤口選擇={day}|{sport}|{cname}|{group}"))]
                    QRButton += QuickR
                flex_message = TextSendMessage(text="請選擇要查詢的盤口",
                                            quick_reply=QuickReply(items=QRButton))
                line_bot_api.reply_message(event.reply_token, flex_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請重新查詢！'))
    elif aboutAI:
        aboutaibanner_Flex = json.load(open('static/about_aibanner.json', 'r', encoding='utf-8'))
        for sport in ['NPB','NBA']:
            aboutlinebot = about_linebot(sport)
            aboutaibanner_Flex['contents'].insert(0,aboutlinebot)
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(f'AI機器人戰績查詢', aboutaibanner_Flex))
    elif remit_cycle:
        flex_message = TextSendMessage(text="請選擇要支付的方式", 
            quick_reply=QuickReply(items=[ 
                QuickReplyButton(action=PostbackAction(label=f"匯款", data=f"@remit={remit_cycle}|remittance")),
                QuickReplyButton(action=PostbackAction(label=f"一卡通Money", data=f"@remit={remit_cycle}|linemoney"))
            ]))
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif remit:
        FlexMessage = json.load(open('static/remit.json', 'r', encoding='utf-8'))
        sport = remit.split("|")[0]
        pay = remit.split("|")[1]
        if pay == 'remittance':
            FlexMessage['hero']['contents'][0]['url'] = f"https://{domain_name}/static/banner/remit_{sport}_{pay}.png?timestamp={g.timestamp}"
            FlexMessage['hero']['contents'][0]['action']['data'] = f'@AI機器人={sport}'
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('訂閱資訊', FlexMessage))
        else:
            # 設定圖片的URL和大小
            image_url = f"https://{domain_name}/static/banner/linepaymoney.png#700"

            # 創建ImageSendMessage物件
            image_message = ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url,
            )
            directions_flex = FlexSendMessage(
                '一卡通Money轉帳說明',json.load(open('static/linepaymoney.json', 'r', encoding='utf-8'))
            )
            line_bot_api.reply_message(event.reply_token, [image_message,directions_flex])
    elif playing_match:
        print(time.ctime())
        sport = playing_match.split("|")[0]
        cname = playing_match.split("|")[1]       
        #all_match = search_match(sport)
        ResultFlex = SearchPlayingMatch(sport)
        print(time.ctime())
        line_bot_api.reply_message(event.reply_token, FlexSendMessage( f"查詢{cname}即時比分", ResultFlex))  
    elif exchange:
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        info = exchange.split("|")
        merchandise = info[0]
        orderId = info[1]
        if UserMemberInfo['UserId'] != None:
            SQL = '''
                SELECT a.*,b.id as orderId,b.UserId,b.Delivery_Status
                  FROM [dbo].[GPlusStore] AS A
                  FULL OUTER JOIN GPlusStore_buyer as b on a.id = b.merchandise_id
                  where merchandise = N'{}'
            '''.format(merchandise)
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            successfulexchange = result[result['Delivery_Status'] != 0]
            merchandise_gplus = result['GPlus'].iloc[0]
            if int(orderId) in successfulexchange['orderId'].values:
                message = '您已確認過兌換，請查看目前訂單狀況'
                merchandise_status_flex = merchandise_status(UserMemberInfo['UserId'],orderId)
                line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=message),FlexSendMessage(f'訂單{orderId}兌換狀況', merchandise_status_flex)])
           
            elif UserMemberInfo['gplus'] < merchandise_gplus:
                gplusdiff = merchandise_gplus - UserMemberInfo['gplus']
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'抱歉，您的GPlus幣不足{gplusdiff}，請選擇其它商品進行兌換\U0001F60A'))
            elif (result['UserId'].iloc[0] != None) & (len(successfulexchange) >= result['inventory'].iloc[0]):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='抱歉，該商品已被兌換完畢，將盡快上架新貨，敬請期待!!'))
            else:
                #status: 1 → 商品兌換成功，但尚未填寫寄送資訊
                update_sql1 = '''
                  update GPlusStore_buyer set Delivery_Status = 1,ExchangeDate = '{}',ExpirationDate = '{}'
                      where id = '{}'                   
                '''.format(
                          datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                          (datetime.now()+timedelta(7)).astimezone(timezone(timedelta(hours=8))).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999'),
                          orderId)
                gplus = UserMemberInfo['gplus'] - merchandise_gplus
                update_sql2 = '''
                    update UserGPlus set GPlus = '{}',Modify_dd = '{}' where userid = '{}'
                '''.format(gplus,
                          datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                          UserMemberInfo['UserId'])
                update_sql = update_sql1 + '\n' + update_sql2 
                cursor = g.conn_Guess365.cursor()
                cursor.execute(update_sql)
                cursor.commit()
                merchandise_status_flex = merchandise_status(UserMemberInfo['UserId'],orderId)
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(f'GPlus商城編號:{orderId}兌換狀況', merchandise_status_flex))
    elif successorder:
        SQL = '''
            SELECT * FROM  GPlusStore_buyer where id = '{}'
        '''.format(successorder)
        result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
        if result['Delivery_Status'].iloc[0] == 3:
            update_sql = '''
              update GPlusStore_buyer set Delivery_Status = 4,completeDate = '{}'
                  where id = '{}'                
            '''.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                       successorder)
            cursor = g.conn_Guess365.cursor()
            cursor.execute(update_sql)
            cursor.commit()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='恭喜您完成本次兌換，繼續參加PK贏得更多G⁺幣吧!!'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='您已完成訂單，如有問題請洽客服。'))
    elif invitefriend:
        UserMemberInfo = get_UserMemberInfo(newLineUniqueID)
        member = UserMemberInfo['member']
        nickname = UserMemberInfo['nickname']
        if UserMemberInfo['UserId'] != None:
            FlexMessage = json.load(open('static/invite.json', 'r', encoding='utf-8'))
            encoded_text = quote('您的好友{}({})邀請您加入Guess365 LINEBOT好友，您將可獲得35元7-11咖啡券一張\n'.format(nickname,member))
            return_text = quote(' \n【請複製此訊息，加入並回傳】')
            FlexMessage['body']['contents'][3]['contents'][0]['action']['uri'] = \
                'line://msg/text/?{}https://liff.line.me/1645278921-kWRPP32q/?accountId=206owzmt{}'.format(encoded_text,return_text)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(f'推薦好友加LINE拿禮券', FlexMessage))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='資訊有誤，請先封鎖我再重新加入！'))
def set_UserMemberInfo(event,UserMemberInfo):
    
    #會員資訊-會員中心的FlexMessage製作
    FlexMessage = json.load(open('static/Flex.json', 'r', encoding='utf-8'))
    # koer3741(kobe廟報明牌)
    FlexMessage['body']['contents'][0]['contents'][0]['contents'][0]['text'] = f"會員 : {UserMemberInfo['member']}({UserMemberInfo['nickname']})"
    #密碼
    FlexMessage['body']['contents'][0]['contents'][0]['contents'][2]['text'] = f"密碼 : {UserMemberInfo['password']}"
    if UserMemberInfo['email'] != None:
        FlexMessage['body']['contents'][0]['contents'][0]['contents'][3]['text'] = f"信箱 : {UserMemberInfo['email']}"
    else:
        FlexMessage['body']['contents'][0]['contents'][0]['contents'][3]['text'] = '信箱 : 尚未綁定'
    #G幣
    if UserMemberInfo['gmoney'] != None:
        FlexMessage['body']['contents'][0]['contents'][0]['contents'][4]['text'] = f"G幣 : {UserMemberInfo['gmoney']}"
    else:
        FlexMessage['body']['contents'][0]['contents'][0]['contents'][4]['text'] = 'G幣 : 0'
    #G⁺幣
    gplus_max = max(int(UserMemberInfo['gplus']),0)
    FlexMessage['body']['contents'][0]['contents'][0]['contents'][5]['text'] = f"G Plus幣 : {gplus_max}"
    # 訂閱等級 : 鑽石
    SubscribeLevel = UserMemberInfo['SubscribeLevel']
    SubscribeLevel_contents = FlexMessage['body']['contents'][0]['contents'][0]['contents'][6]['contents']
    if SubscribeLevel[0] != None:
        for i in range(len(SubscribeLevel)):
            pay = {"Yes" : "已付款", "No" : "未付款"}
            isPayment = UserMemberInfo['isPayment'].iloc[i]
            SubscribeFlex = json.load(open('static/Flex-subscribe.json', 'r', encoding='utf-8'))
            # 訂閱時間:2022/5/10~2022/8/10
            if pd.isnull(UserMemberInfo['SubscribeEnd_dd'].iloc[i]):
                SubscribeFlex[1]['text'] = f"訂閱項目 : {SubscribeLevel.iloc[i]}"
                SubscribeFlex[2]['text'] = f"訂閱期限 : 無"
                SubscribeFlex[3]['text'] = f"是否付款 : {pay[isPayment]}"
            else:
                SubscribeFlex[2]['text'] = f"訂閱期限 : {UserMemberInfo['SubscribeEnd_dd'].iloc[i].strftime('%Y-%m-%d %H:%M:%S.f')[:-5]}"
                # 已付款(2022/8/5)
                if SubscribeLevel.iloc[i] == 'free':
                    SubscribeFlex[1]['text'] = f"訂閱項目 : 限時免費"
                    SubscribeFlex[3]['text'] = f"是否付款 : 免費 ({UserMemberInfo['Payment_dd'].iloc[i].strftime('%Y-%m-%d %H:%M:%S.f')[:-5]})"
                else:
                    SubscribeFlex[1]['text'] = f"訂閱項目 : {SubscribeLevel.iloc[i]}"
                    SubscribeFlex[3]['text'] = f"是否付款 : {pay[isPayment]} ({UserMemberInfo['Payment_dd'].iloc[i].strftime('%Y-%m-%d %H:%M:%S.f')[:-5]})"
            SubscribeLevel_contents += SubscribeFlex
    else:
        SubscribeFlex = json.load(open('static/Flex-subscribe.json', 'r', encoding='utf-8'))
        SubscribeFlex[1]['text'] = f"訂閱等級 : 無"
        # 訂閱時間:2022/5/10~2022/8/10
        SubscribeFlex[2]['text'] = f"訂閱期限 : 無"
        # 已付款(2022/8/5)
        SubscribeFlex[3]['text'] = f"想收到AI預測推薦，就到官網訂閱吧!!"
        SubscribeLevel_contents += SubscribeFlex
    SQL = '''
        SELECT *
          FROM [dbo].[Line_config]
    '''
    result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    FlexMessage['footer']['contents'][0]['contents'][0]['contents'][0]['action']['label'] = result['aboutme_buttom1'].iloc[0]
    FlexMessage['footer']['contents'][0]['contents'][1]['contents'][0]['action']['label'] = result['aboutme_buttom2'].iloc[0]
    return FlexMessage

#判斷是否已是會員
def SearchLineUser(newLineUniqueID):
    SQL = '''
        SELECT * FROM [dbo].[LineUserMember]
            where LineUniqueID = '{}'
    '''.format(newLineUniqueID)
    results_lineuser = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    return results_lineuser

#更新解封鎖會員的狀態
def alreadylogupLine(headshot,situate,newLineUniqueID):
    Insert_SQL = '''
        UPDATE [dbo].[LineUserMember] 
            SET ModifyTime = '{}',Situate = '{}',HeadShot = '{}'
            where LineUniqueID = '{}'
    '''.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
               situate,
               headshot,
               newLineUniqueID)
    cursor = g.conn_Guess365.cursor()
    cursor.execute(Insert_SQL)
    cursor.commit() 
    
#大頭照
def SaveHeadshot(headshot,UserId):
    yzmdata = requests.get(headshot)
    tempIm = BytesIO(yzmdata.content)
    markImg = Image.open(tempIm)
    thumb_width = 150
    im_square = crop_max_square(markImg).resize((thumb_width,thumb_width),Image.LANCZOS)
    im_thumb = mask_circle_transparent(im_square,0)
    im_thumb.save(f"static/memberlogo/{UserId}.png")
    update_SQL = """
         update LineUserMember set HeadShot = '{}' where UserId = '{}'
    """.format(headshot,UserId)
    cursor = g.conn_Guess365.cursor()
    cursor.execute(update_SQL)
    cursor.commit()
    
#隨機創建帳密
def RandomAccont():
    length = random.randint(6,10)
    account = gen_random_string(length)
    password = gen_random_string(length)
    SQL = "select * from UserMember"
    result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    while account in result['member']:
        account = gen_random_string(length)
    return account,password

#隨機長度
def gen_random_string(length):
    numcount = random.randint(1,length - 1)
    lettercount = length - numcount
    numlist = [random.choice(string.digits) for i in range(numcount)]
    letterlist = [random.choice(string.ascii_letters) for i in range(lettercount)]
    allist = letterlist + numlist
    result = ''.join([i for i in allist])
    return result

#將新會員寫入DB且送10天免費訂閱
def logupandfree(newLineUniqueID,UserId,membername,headshot):
    #lineusermember
    Insert_SQL1 = '''
        INSERT INTO [dbo].[LineUserMember] (LineUniqueID,[Level],UserId,HeadShot,LineName,CreatedTime,Situate) VALUES 
        ('{}','0','{}','{}',N'{}','{}','connect')    
    '''.format(newLineUniqueID,
               UserId,
               headshot,
               membername,
               datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))    
    #贈於10天免費接收預測
    Insert_SQL2 = '''  
      INSERT INTO LineSubscription (SubscribeLevel,SubscribeStart_dd,SubscribeEnd_dd,isPayment,Payment_dd,UesrId) 
          VALUES ('free','{}','{}','Yes','{}','{}')
    '''.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
        (datetime.now()+timedelta(10)).astimezone(timezone(timedelta(hours=8))).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999'),
        datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
        UserId)
    Insert_SQL = Insert_SQL1 + "\n" + Insert_SQL2
    cursor = g.conn_Guess365.cursor()
    cursor.execute(Insert_SQL)
    cursor.commit() 
    
    
    
    
#處理透過Web註冊或登入的會員
def manageForm(mtext):
    try:
        flist = mtext.split('/')
        sign = flist[0]
        account = flist[1]
        password = flist[2]
        ip = flist[3]
        newLineUniqueID = flist[4]
        profile = line_bot_api.get_profile(newLineUniqueID)
        nickname = profile.display_name
        headshot = profile.picture_url
        if sign == 'signin':
            UserId = get_UserMember(account, password)
            if UserId:
                LineUniqueID_1 = get_LineUserMember(UserId=UserId)[0]

                LineUniqueID_2 = get_LineUserMember(LineUniqueID=newLineUniqueID)
                # 用戶登入後，將LineID與帳號綁定，並寫入LineUserMember
                if UserId and LineUniqueID_1 == None and LineUniqueID_2[1] == None and LineUniqueID_2[0] != None:
                    add_LineUserMember(UserId, newLineUniqueID,headshot,sign)
                    #贈於15天免費接收預測
                    add_freeSubscription(UserId)
                    SaveHeadshot(headshot,UserId)
                    return "success_2"
                elif UserId and LineUniqueID_1 == newLineUniqueID and LineUniqueID_2[1] == UserId:
                    return "error_1"
                elif UserId and LineUniqueID_1 != None and LineUniqueID_1 != newLineUniqueID :
                    return "error_2"
            else:
                return "error_3"
        elif sign == 'signup':
            LineUniqueID_2 = get_LineUserMember(LineUniqueID=newLineUniqueID)
            if LineUniqueID_2[1] == None and LineUniqueID_2[0] != None:
                SQL = "select * from UserMember where member = '{}'".format(account)
                result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
                if len(result) == 0:
                    url = 'http://https://ecocoapidev1.southeastasia.cloudapp.azure.com/Register/'
                    data = {
                        'member' : account,
                        'password' : password,
                        'nickname' : nickname,
                        'ip' : ip
                    }
                    response_ = requests.post(url,verify=False, data = data, auth=HBA('rick', '123rick456')).text
                    if response_ != 'Account has exist' and 'Error Info' not in response_:
                        #查詢userid
                        UserId = json.loads(response_)['response'][0]['Success Info']
                        #添加到LineUserMember
                        add_LineUserMember(UserId, newLineUniqueID,headshot,sign)
                        #贈於15天免費接收預測
                        add_freeSubscription(UserId)
                        SaveHeadshot(headshot,UserId)
                        return "success_1"
                    else:
                        return "error_5"
                else:
                    return "error_5"
            else:
                return "error_6"
    except Exception as e:
        print(e)
        return "error_4"
    
'''
[6]資料庫存取
'''
# 檢查是否有會員,存在則回傳UserId，反之回傳None
def get_UserMember( account=None, password=None, UserId=None):
    try:
        if account != None and password != None:
            SQL = "select * from UserMember where member = '{}' and Password = '{}' ".format(account,password)
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            return result['UserId'].iloc[0]
        elif UserId != None:
            SQL = """
            select * from UserMember AS A 
                FULL OUTER JOIN UserMoney AS B 
                ON A.UserId = B.UserId 
                where A.UserId = '{}' 
            """.format(UserId)
            result_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            return result['UserId'].iloc[0]
    except Exception as e:
        print(e)
        return None

# 取得會員的相關資料
def get_LineUserMember(UserId=None,LineUniqueID=None,situate=None,member=False,maturity=False):
    if LineUniqueID and member:
        SQL = """
            select a.LineUniqueID,a.UserId,b.[Password],b.nickname,a.situate,a.CreatedTime,a.recommender,b.member,b.Email,c.Money,d.GPlus,e.SubscribeLevel,e.SubscribeStart_dd,e.SubscribeEnd_dd,e.isPayment,e.Payment_dd,ROW_NUMBER() over (partition BY subscribeLevel order by SubscribeStart_dd desc) sn
            from LineUserMember  AS a
            inner join UserMember AS b on a.UserId = b.UserId
            FULL OUTER JOIN UserMoney AS c ON c.UserId = b.UserId
            FULL OUTER JOIN UserGPlus AS d ON A.UserId = d.UserId
            FULL OUTER join LineSubscription as e on a.UserId = e.UesrId and e.SubscribeStart_dd < '{}' and (e.SubscribeEnd_dd > '{}' or e.SubscribeEnd_dd is null)
            where a.LineUniqueID= '{}'
            GROUP by a.LineUniqueID,a.UserId,b.[Password],b.nickname,a.situate,a.CreatedTime,a.recommender,b.member,c.Money,d.GPlus,e.SubscribeLevel,e.SubscribeStart_dd,b.Email,e.SubscribeEnd_dd,e.isPayment,e.Payment_dd
            order by SubscribeStart_dd desc
        """.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),LineUniqueID)
        result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
        result = result[result['sn'] == 1]
        return result
            
    if UserId:
        try:
            SQL = "select * from LineUserMember where UserId = '{}'".format(UserId)
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            return result['LineUniqueID'].iloc[0],result['UserId'].iloc[0],result['situate'].iloc[0]
        except Exception as e:
            print(e)
            return [None,None,None]
    elif LineUniqueID:
        try:
            SQL = "select * from LineUserMember where LineUniqueID = '{}'".format(LineUniqueID)
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            return result['LineUniqueID'].iloc[0],result['UserId'].iloc[0],result['situate'].iloc[0]
        except Exception as e:
            print(e)
            return [None,None,None]
    elif maturity:
        try:
            SQL = """SELECT DISTINCT LineUniqueID,SubscribeLevel,SubscribeEnd_dd
                FROM (
                    SELECT *,ROW_NUMBER() over (partition BY uesrid  order by SubscribeStart_dd desc) sn
                    FROM LineSubscription) S
                inner join LineUserMember on  S.UesrId = LineUserMember.UserId
                where SubscribeEnd_dd < '{}' and situate != 'ban' and S.sn = 1
                order by SubscribeEnd_dd desc
            """.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            return result
        except Exception as e:
            print(e)
    elif maturity == False:
        try:
            SQL = """SELECT　SubscribeLevel, LineUniqueID FROM LineSubscription
                inner join LineUserMember on  LineSubscription.UesrId = LineUserMember.UserId
                where isPayment = 'Yes' and SubscribeEnd_dd > '{}' and situate != 'ban'
                order by Payment_dd desc
            """.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            return result
        except Exception as e:
            print(e)

    else:
        try:
            SQL = f"select * from LineUserMember "
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            return result
        except Exception as e:
            print(e)
            return []

#更新加入會員的狀態
def add_LineUserMember(UserId, newLineUniqueID,headshot,sign):
    if sign == 'signin':
        register = 'NULL'
    elif sign == 'signup':
        register = 'Line'
    Insert_SQL = """
        UPDATE LineUserMember SET UserId='{}',ModifyTime='{}',Situate='connect' ,HeadShot='{}',Register='{}'
            where LineUniqueID='{}'
    """.format(UserId,
               datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
               headshot,
               register,
               newLineUniqueID)
    cursor = g.conn_Guess365.cursor()
    cursor.execute(Insert_SQL)
    cursor.commit()

#贈送10天免費訂閱
def add_freeSubscription(UserId):
    Insert_SQL = '''  
      INSERT INTO LineSubscription (SubscribeLevel,SubscribeStart_dd,SubscribeEnd_dd,isPayment,Payment_dd,UesrId) 
          VALUES ('free','{}','{}','Yes','{}','{}')
    '''.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
        (datetime.now()+timedelta(10)).astimezone(timezone(timedelta(hours=8))).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999'),
        datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
        UserId)
    cursor = g.conn_Guess365.cursor()
    cursor.execute(Insert_SQL)
    cursor.commit()

#查詢會員訂閱狀態
def get_LineBotAutoPredictionLog(UserId=None, SubscribeLevels=[],maturity=False, all = 0):
    if UserId!= None and all == 0:
        try:
            SQL = "select Top 1 * from LineSubscription where [UesrId] = '{}' order by SubscribeStart_dd desc".format(UserId)
            result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            return result['UesrId'].iloc[0], result['SubscribeLevel'].iloc[0], result['SubscribeStart_dd'].iloc[0], result['SubscribeEnd_dd'].iloc[0], result['isPayment'].iloc[0], result['Payment_dd'].iloc[0]
        except Exception as e:
            print(e)
            return [None, None, None, None, None, None]
    elif SubscribeLevels!=[]:
        if maturity == False:
            try:
                SQL = ''' SELECT　SubscribeLevel, LineUniqueID FROM LineSubscription
                           inner join LineUserMember on  LineSubscription.UesrId = LineUserMember.UserId
                           where SubscribeLevel　in ({}) and isPayment = 'Yes' and SubscribeEnd_dd > '{}' and situate != 'ban'
                           order by Payment_dd desc
                        '''.format(str(SubscribeLevels).replace('[','').replace(']',''),
                                   datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
                results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
                return results
            except Exception as e:
                print(e)
                return []
        else:
            try:
                SQL = ''' SELECT DISTINCT LineUniqueID,SubscribeLevel,SubscribeEnd_dd
                            FROM (
                                SELECT *,ROW_NUMBER() over (partition BY uesrid  order by SubscribeStart_dd desc) sn
                                FROM LineSubscription where SubscribeLevel　in ({0})) S
                            inner join LineUserMember on  S.UesrId = LineUserMember.UserId
                            where SubscribeLevel　in ({0}) and SubscribeEnd_dd < '{1}' and situate != 'ban' and S.sn = 1
                            order by SubscribeEnd_dd desc
                        '''.format(str(SubscribeLevels).replace('[','').replace(']',''),
                                   datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))

                results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
                return results
            except Exception as e:
                print(e)
                return []
    elif UserId!= None and all == 1:
        try:
            SQL = """select * from LineSubscription 
                    where [UesrId] = '{}' and isPayment='Yes' 
                    order by SubscribeStart_dd desc""".format(UserId)
            results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
            return results
        except Exception as e:
            print(e)
            return []
        
#查詢會員GPlus幣    
def get_GPlus(UserId):

    try:
        SQL = """
            select b.GPlus from UserMember AS A
            INNER JOIN UserGPlus AS B ON A.UserId = B.UserId
            where A.UserId = '{}'
        """.format(UserId)
        results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
        if len(results) > 0:
            return results['GPlus'].iloc[0]
        else:
            return []
    except Exception as e:
        print(e)
        return []

#查詢會員相關資訊
def get_UserMemberInfo(LineUniqueID):
    memberinfo = get_LineUserMember(LineUniqueID=LineUniqueID,member=True)
    newLineUniqueID = memberinfo['LineUniqueID'].iloc[0]
    UserId = memberinfo['UserId'].iloc[0]
    situate = memberinfo['situate'].iloc[0]
    CreatedTime = memberinfo['CreatedTime'].iloc[0]
    recommender = memberinfo['recommender'].iloc[0]
    UserMember = memberinfo['member'].iloc[0]
    Password = memberinfo['Password'].iloc[0]
    Nickname = memberinfo['nickname'].iloc[0]
    Gmoney = memberinfo['Money'].iloc[0]
    GPlus = memberinfo['GPlus'].iloc[0]
    subscribeLevel = memberinfo['SubscribeLevel']
    subscribeStart_dd = memberinfo['SubscribeStart_dd']
    subscribeEnd_dd = memberinfo['SubscribeEnd_dd']
    ispayment = memberinfo['isPayment']
    payment_dd = memberinfo['Payment_dd']
    email = memberinfo['Email'].iloc[0]

    
    
    
    
    # 若newLineUniqueID,UserId都存在，代表已經登入
    if newLineUniqueID and UserId and situate == 'connect':
        if GPlus == None:
            GPlus = 0
        return dict(LineUniqueID=newLineUniqueID,
             UserId = UserId,
             member = UserMember,
             password = Password,
             nickname=Nickname,
             gmoney = Gmoney,
             gplus = GPlus,
             CreatedTime = CreatedTime,
             recommender = recommender,
             SubscribeLevel=subscribeLevel,
             SubscribeStart_dd=subscribeStart_dd,
             SubscribeEnd_dd=subscribeEnd_dd,
             isPayment=ispayment,
             Payment_dd=payment_dd,
             email = email)
    else:
        return dict(LineUniqueID=None,
             UserId=None,
             member=None,
             password=None,
             nickname=None,
             gmoney =None,
             gplus =None,
             CreatedTime =None,
             recommender = None,
             SubscribeLevel=None,
             SubscribeStart_dd=None,
             SubscribeEnd_dd=None,
             isPayment=None,
             Payment_dd=None,
             email=None)

def add_LineBotAutoPrediction(UesrId,SubscribeLevel):
    SubscribeStart_dd = datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000')
    SubscribeEnd_dd = (datetime.now().astimezone(timezone(timedelta(hours=8)))+timedelta(days=30)).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.000')
    Payment_dd = SubscribeStart_dd
    isPayment = 'Yes'
    # 檢查當前付費紀錄，如果有則把Payment設成No
    if len(get_LineBotAutoPredictionLog(UserId=UesrId, all=1))>0:
        Update_SQL = '''UPDATE  [dbo].[LineSubscription] SET [isPayment]='No' WHERE UesrId = '{}' '''.format(UesrId)
        cursor = g.conn_Guess365.cursor()
        cursor.execute(Update_SQL)
        cursor.commit()
    Insert_SQL = '''INSERT INTO [dbo].[LineSubscription] ([SubscribeLevel],[SubscribeStart_dd],[SubscribeEnd_dd],[isPayment],[Payment_dd],[UesrId]) 
        VALUES(N'{}','{}','{}','{isPayment}','{}','{}') 
    '''.format(SubscribeLevel,SubscribeStart_dd,SubscribeEnd_dd,Payment_dd,UesrId)
    cursor = g.conn_Guess365.cursor()
    cursor.execute(Update_SQL)
    cursor.commit()

#將非關鍵字的文字訊息寫到db中
def write_ReplyMessage(content, LineUniqueID):
    content = r"%s"%content
    Insert_SQL = """INSERT INTO [dbo].[LineUserMemberReplyMessage] ([Content],[dd],[LineUniqueID]) 
        VALUES(N'{}','{}','{}')
        """.format(content,datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),LineUniqueID)
    cursor = g.conn_Guess365.cursor()
    cursor.execute(Insert_SQL)
    cursor.commit()

def write_LineBotPushMessage(type_,from_account,content,target_users):
    content = r"%s"%content
    content = content.replace('\'', '\"')
    Insert_SQL = """INSERT INTO [dbo].[LineBotPushMessage] ([Content],[type],[from_account],[target_users],[dd]) 
        VALUES(N'{}','{}','{}','{}','{}')
    """.format(content,type_,from_account,target_users,datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
    cursor = g.conn_Guess365.cursor()
    cursor.execute(Insert_SQL)
    cursor.commit()

#未訂閱者賽事預測的FlexMessage
def set_FlexTemplateMaturity(contents,banner):
    PredictCarouselFlex = json.load(open('static/Predictmaturity.json', 'r', encoding='utf-8'))
    sql =  """
        SELECT *
          FROM [dbo].[teams]
     """
    teamlogos = pd.read_sql(sql=sql,con=g.conn_Guess365,coerce_float=True)
    
    sql = """
        SELECT *
         FROM [dbo].[Line_config]
     """
    predict_profit = pd.read_sql(sql=sql,con=g.conn_Guess365,coerce_float=True)['Predict_Profit'].iloc[0]
    before = predict_profit.split(" ")[0]
    after = predict_profit.split(" ")[1]
    PredictCarouselFlex['contents'][0]['body']['contents'][1]['contents'][0]['contents'][0]['contents'][0]['text'] = before
    PredictCarouselFlex['contents'][0]['body']['contents'][1]['contents'][0]['contents'][1]['contents'][0]['text'] = after
    
    '''
    編輯預測頁
    '''
    PredictFlexs = []
    predictlist_m = []
    mainpredict = []
    otherpredict = []
    notmain = []
    for subtext in range(len(contents)):
        s = contents[subtext].find('{')
        e = contents[subtext].find('}')
        pred = json.loads(contents[subtext][s:e+1].replace('\'','\"'))
        homeconfidence = int(pred['Confidence'][0].replace("%",""))
        awayconfidence = int(pred['Confidence'][1].replace("%",""))
        if len(pred['Odds']) == 2:
            PredictFlex = json.load(open('static/PredictFlex_2result_maturity.json', 'r', encoding='utf-8')) 
            # 客隊賠率
            PredictFlex['body']['contents'][4]['contents'][1]['contents'][1]['contents'][0]['text'] = str(round(float(pred['Odds'][1]),2))
            # 客隊勝率
            PredictFlex['body']['contents'][4]['contents'][3]['contents'][1]['contents'][0]['text'] = pred['Confidence'][1]
            # 信心度條
            PredictFlex['body']['contents'][4]['contents'][2]['contents'][0]['width'] = pred['Confidence'][0]
            # 預測
            PredictFlex['body']['contents'][7]['contents'][0]['text'] = pred['OptionCode'].strip()
        else:
            PredictFlex = json.load(open('static/PredictFlex_3result_maturity.json', 'r', encoding='utf-8')) 
            # 客隊賠率
            PredictFlex['body']['contents'][4]['contents'][1]['contents'][2]['contents'][0]['text'] = str(round(float(pred['Odds'][1]),2))
            # 客隊勝率
            PredictFlex['body']['contents'][4]['contents'][3]['contents'][2]['contents'][0]['text'] = pred['Confidence'][1]
             # 平手賠率
            PredictFlex['body']['contents'][4]['contents'][1]['contents'][1]['contents'][0]['text'] = str(round(float(pred['Odds'][2]),2))
            # 平手勝率
            PredictFlex['body']['contents'][4]['contents'][3]['contents'][1]['contents'][0]['text'] = pred['Confidence'][2]
            #信心度條
            tieconfidence = str(int(pred['Confidence'][0].replace("%","")) + int(pred['Confidence'][2].replace("%",""))) + "%"
            #平手信心
            PredictFlex['body']['contents'][4]['contents'][2]['contents'][0]['width'] = tieconfidence
            #主隊信心
            PredictFlex['body']['contents'][4]['contents'][2]['contents'][1]['width'] = pred['Confidence'][0]
            # 預測
            PredictFlex['body']['contents'][5]['contents'][0]['text'] = pred['OptionCode'].strip()
        #Banner
        PredictFlex['hero']['url'] = f"https://{domain_name}/static/banner/{banner}.png"
        # 開賽時間
        PredictFlex['body']['contents'][0]['contents'][0]['contents'][0]['text'] ='開賽時間：'+pred['MatchTime']
        # 盤口
        PredictFlex['body']['contents'][1]['contents'][0]['text'] = pred['GroupOptionName'].strip()
        # 主隊LOGO
        PredictFlex['body']['contents'][2]['contents'][0]['contents'][0]['url'] = check_photo(teamlogos,pred['HomeTeam'],"Home")
        # 主隊名稱
        PredictFlex['body']['contents'][3]['contents'][0]['contents'][0]['text'] = pred['HomeTeam']
        # 客隊LOGO
        PredictFlex['body']['contents'][2]['contents'][2]['contents'][0]['url'] = check_photo(teamlogos,pred['AwayTeam'],"Away")
        # 客隊名稱
        PredictFlex['body']['contents'][3]['contents'][1]['contents'][0]['text']= pred['AwayTeam']
        # 主隊賠率
        PredictFlex['body']['contents'][4]['contents'][1]['contents'][0]['contents'][0]['text'] = str(round(float(pred['Odds'][0]),2))
        # 主隊勝率
        PredictFlex['body']['contents'][4]['contents'][3]['contents'][0]['contents'][0]['text'] = pred['Confidence'][0]
        
        PredictCarouselFlex['contents'] += [PredictFlex]
        return PredictCarouselFlex    

#訂閱者賽事預測的FlexMessage
def set_FlexTemplateMessage(contents,header,connect,banner):
    PredictCarouselFlex = json.load(open('static/PredictCarouselFlex.json', 'r', encoding='utf-8'))
    sql =  """
        SELECT *
          FROM [dbo].[teams]
     """
    teamlogos = pd.read_sql(sql=sql,con=g.conn_Guess365,coerce_float=True)
    
    if header != False:
        '''
        編輯尾頁
        '''
        # LOGO
        PredictCarouselFlex['body']['contents'][0]['contents'][0]['url']=header['TournamentText_icon']
        # 準確度標題-1
        PredictCarouselFlex['body']['contents'][1]['contents'][0]['contents'][0]['text']=header['title']
        # 準確度標題-2
        PredictCarouselFlex['body']['contents'][1]['contents'][1]['contents'][0]['text']=header['predict_winrate']
        # 準確度值
        PredictCarouselFlex['body']['contents'][2]['contents'][0]['width']=header['predict_winrate']
        # 4個值
        body_data = header['body_data'].split("|")
        PredictCarouselFlex['body']['contents'][3]['contents'][0]['text']=body_data[0]
        PredictCarouselFlex['body']['contents'][3]['contents'][1]['contents'][0]['contents'][1]['text']=body_data[1]
        PredictCarouselFlex['body']['contents'][3]['contents'][2]['contents'][0]['contents'][1]['text']=body_data[2]
        PredictCarouselFlex['body']['contents'][3]['contents'][3]['contents'][0]['contents'][1]['text']=body_data[3]
        # 回測圖
        PredictCarouselFlex['body']['contents'][4]['contents'][0]['url']=header['body_image']
        
    '''
    編輯首頁
    '''
    PredictResultsFlex_list = json.load(open('static/predict_list_main.json', 'r', encoding='utf-8'))
    PredictResultsFlex_list['hero']['url'] = f"https://{domain_name}/static/banner/predict_banner/{banner}.png"
    '''
    編輯預測頁
    '''
    PredictFlexs = []
    predictlist_m = []
    short_name  = pd.read_excel("static/Team Name.xlsx",index_col = '全名',engine='openpyxl')
    mainpredict = []
    otherpredict = []
    notmain = []
    for subtext in range(len(contents)):
        s = contents[subtext].find('{')
        e = contents[subtext].find('}')
        pred = json.loads(contents[subtext][s:e+1].replace('\'','\"'))
        homeconfidence = int(pred['Confidence'][0].replace("%",""))
        awayconfidence = int(pred['Confidence'][1].replace("%",""))
        main = pred['Main']
        if len(pred['Odds']) == 3:
            # 平手勝率
            tieconfidence = int(pred['Confidence'][2].replace("%",""))
        if main == '1':
            mainpredict.append(pred)
        else:
            otherpredict.append(pred)
    all_predict = mainpredict + otherpredict        
    backgroundblack = 0
    for p in range(len(all_predict)):
        pred = all_predict[p]
        if p == 0:
            #開賽日期
            PredictResultsFlex_list['body']['contents'][0]['contents'][2]['contents'][0]['text'] = \
                (datetime.now().astimezone(timezone(timedelta(hours=8)))+timedelta(days=1)).strftime('%Y') + '-' + (pred['MatchTime'].split(" ")[0]) + ' 預測清單'
            #盤口
            #PredictResultsFlex_list['body']['contents'][1]['contents'][0]['text'] = pred['GroupOptionName'].strip()   
        if pred in mainpredict:
            predictmatch = json.load(open('static/predict_match_mortmain.json', 'r', encoding='utf-8'))
            #主隊logo
            predictmatch['contents'][0]['contents'][2]['contents'][0]['url'] = check_photo(teamlogos,pred['HomeTeam'],"Home")
            #客隊logo
            predictmatch['contents'][2]['contents'][0]['contents'][0]['url'] = check_photo(teamlogos,pred['AwayTeam'],"Away")
            if pred['HomeTeam'] == pred['OptionCode'].strip():
                #主勝icon
                predictmatch['contents'][0]['contents'][0]['contents'][0]['url'] = \
                    'https://i.imgur.com/YDfzHVg.png'
                #主隊名稱粗體
                predictmatch['contents'][0]['contents'][1]['contents'][0]['weight'] = 'bold'
                #客輸要透明
                predictmatch['contents'][2]['contents'][2]['contents'][0]['url'] = \
                    f'https://colorate.azurewebsites.net/SwatchColor/ffffff'
            elif pred['AwayTeam'] == pred['OptionCode'].strip():
                #主輸要透明
                predictmatch['contents'][0]['contents'][0]['contents'][0]['url'] = \
                     f'https://colorate.azurewebsites.net/SwatchColor/ffffff'
                #客隊名稱粗體
                predictmatch['contents'][2]['contents'][1]['contents'][0]['weight'] = 'bold'
                #客勝icon
                predictmatch['contents'][2]['contents'][2]['contents'][0]['url'] = \
                    'https://i.imgur.com/YDfzHVg.png'
            else:
                #主輸要透明
                predictmatch['contents'][0]['contents'][0]['contents'][0]['url'] = \
                     f'https://colorate.azurewebsites.net/SwatchColor/ffffff'
                #客輸要透明
                predictmatch['contents'][2]['contents'][2]['contents'][0]['url'] = \
                    f'https://colorate.azurewebsites.net/SwatchColor/ffffff'
                #平的背景顏色
                predictmatch['contents'][1]['backgroundColor'] = '#d9168e'
                 #平的字顏色
                predictmatch['contents'][1]['contents'][0]['color'] = '#ffffff'
                #平的字樣
                predictmatch['contents'][1]['contents'][0]['text'] = '平'
                #平的大小
                predictmatch['contents'][1]['contents'][0]['size'] = '16px'
                #平的型態
                predictmatch['contents'][1]['contents'][0]['style'] = 'normal'
                #平的粗體
                predictmatch['contents'][1]['contents'][0]['weight'] = 'bold'
            #主隊名稱
            if pred['HomeTeam'] in short_name.index:
                predictmatch['contents'][0]['contents'][1]['contents'][0]['text'] = \
                    short_name[short_name.index == pred['HomeTeam']]['縮寫'].iloc[0]
            else:
                 predictmatch['contents'][0]['contents'][1]['contents'][0]['text'] = pred['HomeTeam']
            #客隊名稱
            if pred['AwayTeam'] in short_name.index:
                predictmatch['contents'][2]['contents'][1]['contents'][0]['text'] =\
                    short_name[short_name.index == pred['AwayTeam']]['縮寫'].iloc[0]
            else:
                 predictmatch['contents'][2]['contents'][1]['contents'][0]['text'] = pred['AwayTeam']
            predictlist_m.append(predictmatch)    
        else:  
            predictmatch = json.load(open('static/predict_match_other.json', 'r', encoding='utf-8'))
            #獲勝icon
            if backgroundblack in [0,2,4]:
                background = 'f5f5f5'
            else:
                background = 'ffffff'
            backgroundblack += 1
            if pred['HomeTeam'] == pred['OptionCode'].strip():
                #主勝icon
                predictmatch['contents'][0]['contents'][0]['contents'][0]['url'] = \
                    'https://i.imgur.com/YDfzHVg.png'
                #主隊名稱顏色
                predictmatch['contents'][0]['contents'][1]['contents'][0]['color'] = '#000000'
                #主隊名稱粗體
                predictmatch['contents'][0]['contents'][1]['contents'][0]['weight'] = 'bold'
                #vs的背景顏色
                predictmatch['contents'][1]['backgroundColor'] ="#" +  background 
                #客輸要透明
                predictmatch['contents'][2]['contents'][2]['contents'][0]['url'] = \
                  f'https://colorate.azurewebsites.net/SwatchColor/{background}'
            elif pred['AwayTeam'] == pred['OptionCode'].strip():
                #主輸要透明
                predictmatch['contents'][0]['contents'][0]['contents'][0]['url'] = \
                    f'https://colorate.azurewebsites.net/SwatchColor/{background}'
                #主隊名稱顏色
                predictmatch['contents'][0]['contents'][1]['contents'][0]['color'] = '#000000'
                #主隊名稱不粗體
                predictmatch['contents'][0]['contents'][1]['contents'][0]['weight'] = 'regular'
                #vs的背景顏色
                predictmatch['contents'][1]['backgroundColor'] = "#" + background 
                #客隊名稱的顏色
                predictmatch['contents'][2]['contents'][1]['contents'][0]['color'] = '#000000'
                #客隊名稱粗體
                predictmatch['contents'][2]['contents'][1]['contents'][0]['weight'] = 'bold'
                #客勝icon
                predictmatch['contents'][2]['contents'][2]['contents'][0]['url'] = \
                    'https://i.imgur.com/YDfzHVg.png'
            else:
                #主輸要透明
                predictmatch['contents'][0]['contents'][0]['contents'][0]['url'] = \
                    f'https://colorate.azurewebsites.net/SwatchColor/{background}'
                #平的背景顏色
                predictmatch['contents'][1]['backgroundColor'] = '#d9168e'  
                #平的字顏色
                predictmatch['contents'][1]['contents'][0]['color'] = '#ffffff'
                #平的字樣
                predictmatch['contents'][1]['contents'][0]['text'] = '平'
                #客輸要透明
                predictmatch['contents'][2]['contents'][2]['contents'][0]['url'] = \
                   f'https://colorate.azurewebsites.net/SwatchColor/{background}'
                #主隊名稱顏色
                predictmatch['contents'][0]['contents'][1]['contents'][0]['color'] = '#000000'
                #主隊名稱不粗體
                predictmatch['contents'][0]['contents'][1]['contents'][0]['weight'] = 'regular'
            #主隊名稱
            if pred['HomeTeam'] in short_name.index:
                predictmatch['contents'][0]['contents'][1]['contents'][0]['text'] = \
                    short_name[short_name.index == pred['HomeTeam']]['縮寫'].iloc[0]
            else:
                 predictmatch['contents'][0]['contents'][1]['contents'][0]['text'] = pred['HomeTeam']
            #客隊名稱
            if pred['AwayTeam'] in short_name.index:
                predictmatch['contents'][2]['contents'][1]['contents'][0]['text'] =\
                    short_name[short_name.index == pred['AwayTeam']]['縮寫'].iloc[0]
            else:
                 predictmatch['contents'][2]['contents'][1]['contents'][0]['text'] = pred['AwayTeam']
            #主隊logo
            predictmatch['contents'][0]['contents'][2]['contents'][0]['url'] =  check_photo(teamlogos,pred['HomeTeam'],"Home")
            #客隊logo
            predictmatch['contents'][2]['contents'][0]['contents'][0]['url'] = check_photo(teamlogos,pred['AwayTeam'],"Away")
            notmain.append(predictmatch)
        if len(pred['Odds']) == 2:
            PredictFlex = json.load(open('static/PredictFlex_2result.json', 'r', encoding='utf-8')) 
            # 客隊賠率
            PredictFlex['body']['contents'][4]['contents'][1]['contents'][1]['contents'][0]['text'] = str(round(float(pred['Odds'][1]),2))
            # 客隊勝率
            PredictFlex['body']['contents'][4]['contents'][3]['contents'][1]['contents'][0]['text'] = pred['Confidence'][1]
            # 信心度條
            PredictFlex['body']['contents'][4]['contents'][2]['contents'][0]['width'] = pred['Confidence'][0]
            # 預測
            PredictFlex['body']['contents'][7]['contents'][0]['text'] = pred['OptionCode'].strip()
        else:
            PredictFlex = json.load(open('static/PredictFlex_3result.json', 'r', encoding='utf-8')) 
            # 客隊賠率
            PredictFlex['body']['contents'][4]['contents'][1]['contents'][2]['contents'][0]['text'] = str(round(float(pred['Odds'][1]),2))
            # 客隊勝率
            PredictFlex['body']['contents'][4]['contents'][3]['contents'][2]['contents'][0]['text'] = pred['Confidence'][1]
             # 平手賠率
            PredictFlex['body']['contents'][4]['contents'][1]['contents'][1]['contents'][0]['text'] = str(round(float(pred['Odds'][2]),2))
            # 平手勝率
            PredictFlex['body']['contents'][4]['contents'][3]['contents'][1]['contents'][0]['text'] = pred['Confidence'][2]
            #信心度條
            tieconfidence = str(int(pred['Confidence'][0].replace("%","")) + int(pred['Confidence'][2].replace("%",""))) + "%"
            #平手信心
            PredictFlex['body']['contents'][4]['contents'][2]['contents'][0]['width'] = tieconfidence
            #主隊信心
            PredictFlex['body']['contents'][4]['contents'][2]['contents'][1]['width'] = pred['Confidence'][0]
            # 預測
            PredictFlex['body']['contents'][5]['contents'][0]['text'] = pred['OptionCode'].strip()
        #Banner
        PredictFlex['hero']['url'] = f"https://{domain_name}/static/banner/predict_banner/{banner}.png"
        # 開賽時間
        PredictFlex['body']['contents'][0]['contents'][0]['contents'][0]['text'] ='開賽時間：'+pred['MatchTime']
        # 盤口
        PredictFlex['body']['contents'][1]['contents'][0]['text'] = pred['GroupOptionName'].strip()
        # 主隊LOGO
        PredictFlex['body']['contents'][2]['contents'][0]['contents'][0]['url'] = check_photo(teamlogos,pred['HomeTeam'],"Home")
        # 主隊名稱
        PredictFlex['body']['contents'][3]['contents'][0]['contents'][0]['text'] = pred['HomeTeam']
        # 客隊LOGO
        PredictFlex['body']['contents'][2]['contents'][2]['contents'][0]['url'] = check_photo(teamlogos,pred['AwayTeam'],"Away")
        # 客隊名稱
        PredictFlex['body']['contents'][3]['contents'][1]['contents'][0]['text']= pred['AwayTeam']
        # 主隊賠率
        PredictFlex['body']['contents'][4]['contents'][1]['contents'][0]['contents'][0]['text'] = str(round(float(pred['Odds'][0]),2))
        # 主隊勝率
        PredictFlex['body']['contents'][4]['contents'][3]['contents'][0]['contents'][0]['text'] = pred['Confidence'][0]
        PredictFlexs.append(PredictFlex)
    if connect:
        '''
        串接
        '''
        PredictFlexs.append(PredictCarouselFlex)
    if len(notmain) > 0:
        PredictResultsFlex_list['body']['contents'][3]['contents'][5]['contents'][0]['contents'][0]['contents'] += notmain
    else:
        PredictResultsFlex_list['body']['contents'][3]['contents'][5]['contents'][0]['contents'][0]['contents'][0]['contents'][0]['contents'][0]['color'] = '#ffffff'
    if len(predictlist_m) > 0:  
        
        PredictResultsFlex_list['body']['contents'][2]['contents'] += predictlist_m
    else:
        text = [{
            "type": "text",
            "text": "本日無主推",
            "color": "#FFFFFF",
            "weight": "bold",
            "size": "22px"
          }]
        PredictResultsFlex_list['body']['contents'][2]['contents'] += text
    PredictFlexs.insert(0,PredictResultsFlex_list)

    Carousel = {
      "type": "carousel",
      "contents":PredictFlexs
    }
    return Carousel

#查詢DB中的下狠話
def get_Quotations():
    SQL = "SELECT * From [dbo].[LinePKQuotations]"
    results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    return list(results['Quotation'])

#檢查隊徽是否存在
def check_photo(teamlogos,play,team):
    teamlogo = 'https://i.imgur.com/x31phAh.jpeg'
    '''
    檢查隊徽圖片是否存在
    '''
    if team == "Home":
        if len(teamlogos[teamlogos['name']== play])>0:
            team = teamlogos[teamlogos['name']==play]['image'].iloc[0]
            if team is not None:
                teamlogo = ("https://guess365.cc" + team).replace(" ","%20")
    elif team == "Away":
        if len(teamlogos[teamlogos['name']==play])>0:
            team = teamlogos[teamlogos['name']==play]['image'].iloc[0]
            if team is not None:
                teamlogo = ("https://guess365.cc" + team).replace(" ","%20")
    return teamlogo

#PK賽事的FlexMessage
def set_PlayerPKFlexTemplateMessage(event,plays):
    
    try:
        corpus = get_Quotations()

        sql =  """
                SELECT *
                  FROM [dbo].[teams]
                """
        teamlogos = pd.read_sql(sql=sql,con=g.conn_Guess365,coerce_float=True)
        Carousel = {
          "type": "carousel",
          "contents": [
            {
              "type": "bubble",
              "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "image",
                    "url": f"https://{domain_name}/static/banner/pkbanner.png",
                    "aspectMode": "cover",
                    "size": "300px",
                    "aspectRatio": "1:1.7",
                    "offsetBottom": "20px"
                  }
                ],
                "paddingAll": "0px",
                "height": "430px",
                "width": "300px"
              }
            }
          ]
        }
        for play in plays:
            LinePlayerPKFlex_self = json.load(open('static/LinePlayerPKFlex_self_v2.json', 'r', encoding='utf-8'))
            # 比賽時間
            LinePlayerPKFlex_self['body']['contents'][0]['contents'][0]['contents'][0]['text'] = f"賽事時間 : {play['MatchTime'][5:-7]}"
            #賽事
            LinePlayerPKFlex_self['body']['contents'][1]['contents'][0]['contents'][0]['text'] = play['TournamentText']
            # 主隊名稱
            if play['HomeTeam'][1] == None:
                hometeam = play['HomeTeam'][0]
            else:
                hometeam = play['HomeTeam'][1]
            LinePlayerPKFlex_self['body']['contents'][1]['contents'][0]['contents'][2]['contents'][0]['contents'][0]['text'] = hometeam
            # 主隊徽
            LinePlayerPKFlex_self['body']['contents'][1]['contents'][0]['contents'][1]['contents'][0]['contents'][0]['url'] = \
                check_photo(teamlogos,hometeam,'Home')
            # 客隊名稱
            if play['AwayTeam'][1] == None:
                awayteam = play['AwayTeam'][0]
            else:
                awayteam = play['AwayTeam'][1]
            LinePlayerPKFlex_self['body']['contents'][1]['contents'][0]['contents'][2]['contents'][1]['contents'][0]['text'] = awayteam
            # 客隊徽
            LinePlayerPKFlex_self['body']['contents'][1]['contents'][0]['contents'][1]['contents'][2]['contents'][0]['url'] = \
                check_photo(teamlogos,awayteam,'Away')
            # 盤口
            optionCode = play['odds'][0]['Type_cname']
            LinePlayerPKFlex_self['body']['contents'][2]['contents'][1]['contents'][0]['text'] = \
                optionCode
            # 賠率
            if play['odds'][0]['GroupOptionCode'] == "20":
                option1 = "主隊"
                option2 = "客隊"
                LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][0]['contents'][1]['contents'][0]['text']  = \
                    f"賠率{play['odds'][0]['OptionRate']}" # 主
                LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][1]['contents'][1]['contents'][0]['text']  = \
                    f"賠率{play['odds'][1]['OptionRate']}" # 客
            elif play['odds'][0]['GroupOptionCode'] in ["60","52"]:
                specialBetValue = play['odds'][0]['SpecialBetValue']
                if specialBetValue.split(".")[1] == "0":
                    specialBetValue = specialBetValue[:-2]
                option1 = f"大於{specialBetValue}"
                option2 = f"小於{specialBetValue}"
                LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][0]['contents'][1]['contents'][0]['text']  = \
                    f"賠率{play['odds'][0]['OptionRate']}" # 大分
                LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][1]['contents'][1]['contents'][0]['text']  = \
                    f"賠率{play['odds'][1]['OptionRate']}" # 小分
            elif play['odds'][0]['GroupOptionCode'] in ["228","51"]:
                specialBetValue = play['odds'][0]['SpecialBetValue']
                if specialBetValue.split(".")[1] == "0":
                    specialBetValue = specialBetValue[:-2]
                if float(specialBetValue) > 0:
                    specialBetValue = specialBetValue[1:]
                    option1 = f"主+{specialBetValue}"
                    option2 = f"客-{specialBetValue}"
                elif float(specialBetValue) < 0:
                    specialBetValue = specialBetValue[1:]
                    option1 = f"主-{specialBetValue}"
                    option2 = f"客+{specialBetValue}"
                LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][0]['contents'][1]['contents'][0]['text']  = \
                    f"賠率{play['odds'][0]['OptionRate']}" # 主
                LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][1]['contents'][1]['contents'][0]['text']  = \
                    f"賠率{play['odds'][1]['OptionRate']}" # 客
            # 下狠話
            #LinePlayerPKFlex_self['body']['contents'][4]['contents'][1]['contents'][0]['text'] = corpus[random.randint(0,len(corpus)-1)].strip()
            # LABEL
            LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][0]['contents'][0]['action']['label']  = option1
            LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][1]['contents'][0]['action']['label']  = option2
            # ACTION
            LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][0]['contents'][0]['action']['data']  = \
                f'''@PK選擇=['EventCode':'{play['EventCode']}','MatchTime':'{play['MatchTime'][5:-7]}','HomeTeam':'{hometeam}','AwayTeam':'{awayteam}','OptionCode':'{play['odds'][0]['OptionCode']}','GroupOptionCode':'{play['odds'][0]['GroupOptionCode']}','HomeOdds':'{play['odds'][0]['OptionRate']}','AwayOdds':'{play['odds'][1]['OptionRate']}','SpecialBetValue':'{play['odds'][0]['SpecialBetValue']}','SportCode':'{play['SportCode']}']''' # 主
            LinePlayerPKFlex_self['body']['contents'][2]['contents'][2]['contents'][0]['contents'][1]['contents'][0]['action']['data']  = \
                f'''@PK選擇=['EventCode':'{play['EventCode']}','MatchTime':'{play['MatchTime'][5:-7]}','HomeTeam':'{hometeam}','AwayTeam':'{awayteam}','OptionCode':'{play['odds'][1]['OptionCode']}','GroupOptionCode':'{play['odds'][0]['GroupOptionCode']}','HomeOdds':'{play['odds'][0]['OptionRate']}','AwayOdds':'{play['odds'][1]['OptionRate']}','SpecialBetValue':'{play['odds'][0]['SpecialBetValue']}','SportCode':'{play['SportCode']}']''' # 客
            Carousel["contents"] += [LinePlayerPKFlex_self]
        if len(plays)>0:
            line_bot_api.reply_message(event.reply_token, FlexSendMessage("我要PK",Carousel))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("目前沒有提供PK項目"))
    except Exception as e:
        print(e)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

#統計PK的戰績
def get_PlayerPKStandings(UserId, event,UserMemberInfo,other= False):
    Standings = {'勝': 0, '敗': 0, '未開賽': 0,'場數': 0 }

    SQL = ''' 
        SELECT Result,UserId1,UserId2,id,GPlus from LinePlayerPK
            where (UserId1 = '{0}' or UserId2 = '{0}')
            ORDER BY id desc
    '''.format(UserId)
    results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    for result in range(len(results)):
        if results['UserId1'][result] == UserId:
            if results['Result'][result] == 'UserId1':
                Standings['勝'] +=1
                Standings['場數'] +=1
            elif results['Result'][result] == 'UserId2':
                Standings['敗'] +=1
                Standings['場數'] +=1
            elif results['Result'][result] == None:
                Standings['未開賽'] +=1
        else:
            if results['Result'][result] == 'UserId2':
                Standings['勝'] +=1
                Standings['場數'] +=1
            elif results['Result'][result] == 'UserId1':
                Standings['敗'] +=1
                Standings['場數'] +=1
            elif results['Result'][result] == None:
                Standings['未開賽'] +=1
            
    pd_results = pd.DataFrame(results)
    pd_results = pd_results.dropna(subset=['GPlus'])
    pd_results.reset_index(inplace=True, drop=True)
    SearchPK = SearchPKResult(event,Standings,pd_results,UserMemberInfo,other)
    return line_bot_api.reply_message(event.reply_token, FlexSendMessage("PK戰況查詢",SearchPK))

#PK戰績的FlexMessage
def SearchPKResult(event,Standings,pd_results,UserMemberInfo,other):
    profile = line_bot_api.get_profile(UserMemberInfo['LineUniqueID'])
    headshot = profile.picture_url
    SaveHeadshot(headshot,UserMemberInfo['UserId'])
    PKStandingsFlex = json.load(open('static/SearchPK_戰績.json', 'r', encoding='utf-8'))
    #會員大頭照
    PKStandingsFlex['body']['contents'][0]['contents'][0]['url'] = f"https://{domain_name}/static/memberlogo/{UserMemberInfo['UserId']}.png?timestamp={g.timestamp}"
    #取消他人會員連結(關於我)
    if other == True:
        PKStandingsFlex['body']['contents'][0]['contents'][0]['action'] = []
        PKStandingsFlex['body']['contents'][0]['contents'][1]['action'] = []
    #會員名稱(暱稱)
    PKStandingsFlex['body']['contents'][0]['contents'][1]['text'] = f"{UserMemberInfo['member']}({UserMemberInfo['nickname']})"
    #戰績
    PKStandingsFlex['body']['contents'][3]['contents'][0]['contents'][0]['text'] = f"{Standings['勝']}勝{Standings['敗']}敗"
    #PK場數
    PKStandingsFlex['body']['contents'][3]['contents'][1]['contents'][0]['text'] = f"{Standings['場數']}場"
    #勝率
    if Standings['場數'] != 0:
        win_rate = round((int(Standings['勝']) / (Standings['場數']))*100,1)
    else:
        win_rate = 0
    PKStandingsFlex['body']['contents'][3]['contents'][2]['contents'][0]['text'] = f"{win_rate}%"
    #總GPlus幣
    PKStandingsFlex['body']['contents'][7]['contents'][1]['text'] = '總G⁺幣 : {} G⁺'.format(UserMemberInfo['gplus'])
    #近期戰況
    if len(pd_results) > 5:
        count = 5
    else:
        count = len(pd_results)
    all_member = get_member()
    for r in range(0,count):
        PKScurrentFlex = json.load(open('static/SearchPK_近期戰況.json', 'r', encoding='utf-8'))
        if pd_results['UserId1'][r] == UserMemberInfo['UserId']:
            if pd_results['Result'][r] == 'UserId1':
                #輸贏logo
                PKScurrentFlex['contents'][0]['contents'][0]['url'] = 'https://i.imgur.com/3m8eb4Q.png'
                #GPlus幣
                PKScurrentFlex['contents'][3]['contents'][0]['text'] = f"+{int(pd_results['GPlus'][r])}"
                PKScurrentFlex['contents'][3]['contents'][0]['color'] = '#e32b79'
            elif pd_results['Result'][r] == 'UserId2':
                PKScurrentFlex['contents'][0]['contents'][0]['url'] = 'https://i.imgur.com/elT6px5.png'
                PKScurrentFlex['contents'][3]['contents'][0]['text'] = "0"
                PKScurrentFlex['contents'][3]['contents'][0]['color'] = '#32CD32'
            else:
                PKScurrentFlex['contents'][0]['contents'][0]['url'] = 'https://i.imgur.com/a9uDWYK.png'
                PKScurrentFlex['contents'][3]['contents'][0]['text'] = "0"
                PKScurrentFlex['contents'][3]['contents'][0]['color'] ='#000000'
            #對手
            PKScurrentFlex['contents'][2]['contents'][0]['text'] = all_member[all_member['UserId'] == pd_results['UserId2'][r]]['member'].iloc[0]
            
            
        elif pd_results['UserId2'][r] == UserMemberInfo['UserId']:
            if pd_results['Result'][r] == 'UserId2':
                #輸贏logo
                PKScurrentFlex['contents'][0]['contents'][0]['url'] = 'https://i.imgur.com/3m8eb4Q.png'
                #GPlus幣
                PKScurrentFlex['contents'][3]['contents'][0]['text'] = f"+{int(pd_results['GPlus'][r])}"
                PKScurrentFlex['contents'][3]['contents'][0]['color'] = '#e32b79'
            elif pd_results['Result'][r] == 'UserId1':
                PKScurrentFlex['contents'][0]['contents'][0]['url'] = 'https://i.imgur.com/elT6px5.png'
                PKScurrentFlex['contents'][3]['contents'][0]['text'] = "0"
                PKScurrentFlex['contents'][3]['contents'][0]['color'] = '#32CD32'
            else:
                PKScurrentFlex['contents'][0]['contents'][0]['url'] = 'https://i.imgur.com/a9uDWYK.png'
                PKScurrentFlex['contents'][3]['contents'][0]['text'] = "0"
                PKScurrentFlex['contents'][3]['contents'][0]['color'] ='#000000'
            #對手
            PKScurrentFlex['contents'][2]['contents'][0]['text'] = all_member[all_member['UserId'] == pd_results['UserId1'][r]]['member'].iloc[0]
        #PKID
        PKScurrentFlex['contents'][1]['contents'][0]['text'] = str(pd_results['id'][r])
        
        PKStandingsFlex['body']['contents'][5]['contents'][1]['contents'].append(PKScurrentFlex)
    return PKStandingsFlex

#隨機4場PK賽事
def get_PlayerPKGame():
    try:
        # https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/NBA/any
        MatchEntrys = requests.get(f'{branch}/MatchEntryInfo/DateBetween/All/any',verify=False, auth=(users[0]['username'],users[0]['password_2'])).text
        MatchEntrys = json.loads(MatchEntrys)['response']
        play_num = len(MatchEntrys)
        if play_num == 0:
            MatchEntrys = requests.get(f'{branch}/MatchEntryInfo/DateBetween/All/any',verify=False, auth=(users[0]['username'],users[0]['password_2'])).text
            MatchEntrys = json.loads(MatchEntrys)['response']
            play_num = len(MatchEntrys)
        random.shuffle(MatchEntrys)
        plays = []
        c = 0
        for idx in range(0,play_num):
            tournametext = MatchEntrys[idx]['TournamentText']
            GroupOptionCodeList = ['20','52','51','228','60']
            random.shuffle(GroupOptionCodeList)
            odds_list = []
            for odds in MatchEntrys[idx]['odds']:
                if odds != [] and str(odds['GroupOptionCode']) == str(GroupOptionCodeList[0]):
                    odds_list += [odds]
            if 4>c and odds_list != []:
                temp = MatchEntrys[idx].copy()
                temp['odds'] = odds_list
                plays.append(temp)
                c+=1
            elif odds_list == []:
                continue
            elif c == 4:
                break
        return plays
    except Exception as e:
        print(e)
        return []

#查詢所有盤口
def get_all_TypeCname():
    SQL = '''SELECT [SportCode],[Type],[Type_cname],[Play_Name],[GroupOptionCode1] 
        FROM [dbo].[GroupOptionCode] '''
    results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    return results

#查詢指定的賽事盤口
def get_TypeCname(SportCode = None,GroupOptionCode = None):
    if SportCode and GroupOptionCode:
        SQL = '''SELECT [SportCode],[Type],[Type_cname],[Play_Name],[GroupOptionCode1] FROM [dbo].[GroupOptionCode] 
                    where [SportCode]='{}' and  GroupOptionCode1='{}' '''.format(SportCode,GroupOptionCode)
        results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
        if len(results)>0:
            return results['Type_cname'].iloc[0]
        else:
            return None
    elif SportCode == None and GroupOptionCode == None:
        SQL = '''SELECT [SportCode],[Type],[Type_cname],[Play_Name],[GroupOptionCode1] 
            FROM [dbo].[GroupOptionCode]'''
        results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
        return results
    
#轉換DB中下注選項的名稱
def Mapping_OptionCode(OptionCode,SportCode,GroupOptionCode,HomeTeam,AwayTeam):
    if SportCode == '1' and GroupOptionCode in ('55'):
        texts = [OptionCode.split('/')[0].strip(), OptionCode.split('/')[1].strip()]
        if not texts[0] == 'Draw' and not texts[1] == 'Draw':
            return '平手'
        elif not texts[0] == 'Draw' and texts[1] == 'Draw':
            return HomeTeam+'/平手'
        elif texts[0] == 'Draw' and not texts[1] == 'Draw':
            return '平手/'+AwayTeam
    else:
        if OptionCode == '1':
            return HomeTeam
        elif OptionCode == '2':
            return AwayTeam
        elif OptionCode == 'X':
            return '平手'
        elif OptionCode == 'Over':
            return '大分'
        elif OptionCode == 'Under':
            return '小分'

    return None

#添加PK賽事到DB(每日一人最多3場)
def add_LinePlayerPK(UserId, data, event):
    try:
        SQL = """SELECT count(id) as count FROM [dbo].[LinePlayerPK] where UserId1='{}'
              and created_dd >= '{}'
              and created_dd <= '{}'
            """.format(UserId,datetime.now().astimezone(timezone(timedelta(hours=8))).replace(hour=0,minute=0,second=0).strftime('%Y-%m-%d %H:%M:%S.000'),datetime.now().astimezone(timezone(timedelta(hours=8))).replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S.000'))
        results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
        
        if results['count'].iloc[0] < 3:
            Insert_SQL = """INSERT INTO [dbo].[LinePlayerPK] ([UserId1],[EventCode],[Option1],[GroupOptionCode],[isAutoMatch],[isPushed],[created_dd],[HomeOdds],[AwayOdds],[SpecialBetValue]) 
                         VALUES(N'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')
                    """.format(UserId,data['EventCode'],data['OptionCode'],data['GroupOptionCode'],False,False,datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),data['HomeOdds'],data['AwayOdds'],data['SpecialBetValue'])
            cursor = g.conn_Guess365.cursor()
            cursor.execute(Insert_SQL)
            cursor.commit()
            search_SQL = """
                SELECT *FROM [dbo].[LinePlayerPK]
                WHERE UserId1 = N'{}' and EventCode = '{}' and Option1 = '{}' and GroupOptionCode = '{}'
            """.format(UserId,data['EventCode'],data['OptionCode'],data['GroupOptionCode'])
            results = pd.read_sql(sql=search_SQL,con=g.conn_Guess365,coerce_float=True)  
            return True,results['id'].iloc[0]
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已達上限，單日最多PK「3場」'))
            return False,False
    except Exception as e:
        print(e)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已經重複選擇！'))
        return False,False

#賽事配對成功，將資料更新到DB中
def update_invite_LinePlayerPK(UserId, data, event):
    try:
        SQL = """SELECT * FROM [dbo].[LinePlayerPK]
              inner join MatchEntry on LinePlayerPK.EventCode = MatchEntry.EventCode
              where id = {} """.format(data['id'])
        result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
        
        if result['Option2'].iloc[0] == None and result['UserId2'].iloc[0] != None and result['MatchTime'].iloc[0].replace(tzinfo=utc) >= datetime.now().astimezone(timezone(timedelta(hours=8))).replace(tzinfo=utc):
            SQL = """UPDATE [dbo].[LinePlayerPK] SET Option2 = '{}' 
            where id = {} """.format(data['Option2Code'],data['id'])
            cursor = g.conn_Guess365.cursor()
            cursor.execute(SQL)
            cursor.commit()
        
            PKMatchFlex = set_PKMatchFlex(UserId,data)
            all_member = get_member()
            member = all_member[all_member['UserId'] == UserId]['member'].iloc[0]
            line_bot_api.push_message(data['LineUniqueID'],FlexSendMessage(f"{member}已接受您的挑戰",PKMatchFlex))
            return PKMatchFlex
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'您已經點選或比賽已開始'))
            return False
    except Exception as e:
        print(e)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'Id{data["id"]}錯誤！'))
        return False

#查詢DB中的所有會員資料
def get_member():
    SQL = f"select * from UserMember"
    results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    return results
   
#PK賽事確認訊息的FlexMessage
def set_CheckFlex(data,pkid):
    GroupOptionCode = get_TypeCname(data['SportCode'], data['GroupOptionCode'])
    checkFlex= json.load(open('static/check.json', 'r', encoding='utf-8'))
    #開賽時間
    checkFlex['body']['contents'][0]['contents'][0]['text'] = f"開賽時間 : {data['MatchTime']}"
    #PK場號
    checkFlex['body']['contents'][2]['contents'][1]['contents'][0]['text'] = f"PK場號 : {pkid}"
    #盤口
    checkFlex['body']['contents'][2]['contents'][1]['contents'][1]['text'] = GroupOptionCode
    #主隊
    checkFlex['body']['contents'][2]['contents'][1]['contents'][2]['contents'][0]['contents'][0]['text'] = data['HomeTeam']
    #客隊
    checkFlex['body']['contents'][2]['contents'][1]['contents'][2]['contents'][2]['contents'][0]['text'] = data['AwayTeam']
    #選擇
    if data['GroupOptionCode'] == '20':
        if data['OptionCode'] == "1":
            checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = data['HomeTeam']
        else:
            checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = data['AwayTeam']
    elif data['GroupOptionCode'] in ['60','52']:
        specialBetValue = data['SpecialBetValue']
        if specialBetValue.split(".")[1] == "0":
            specialBetValue = specialBetValue[:-2]
        if data['OptionCode'] == "Over":
            checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = \
            f"大於{specialBetValue}"
        else:
            checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = \
            f"小於{specialBetValue}" 
    elif data['GroupOptionCode'] in ['228','51']:
        specialBetValue = data['SpecialBetValue']
        if specialBetValue.split(".")[1] == "0":
            specialBetValue = specialBetValue[:-2]
        if float(data['SpecialBetValue']) > 0:
            if data['OptionCode'] == "1":
                checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = \
                f"主+{data['SpecialBetValue']}"

            else:
                checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = \
                f"客-{data['SpecialBetValue']}" 
        else:
            SpecialBetValue = data['SpecialBetValue'][1:]
            if data['OptionCode'] == "1":
                checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = \
                f"主-{SpecialBetValue}"

            else:
                checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = \
                f"客+{SpecialBetValue}" 
    elif data['GroupOptionCode'] == '10':
        if data['OptionCode'] == "1":
            checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = data['HomeTeam']
        elif database['OptionCode'] == '2':
            checkFlex['body']['contents'][2]['contents'][1]['contents'][3]['contents'][0]['text'] = data['AwayTeam']
        else:
            database
    return checkFlex

#賽果推播的FlexMessage
def set_PredictResultsFlex(contents):
    try:
        predictresult_text = []
        contents = str(contents).replace("'",'"')
        contents = json.loads(contents)
        teamname = pd.read_excel("static/Team Name.xlsx",index_col='全名',engine='openpyxl')
        for c in range(0,len(contents)):
            date  = contents[c]['date']
            sport = contents[c]['sport']
            PredictResults = contents[c]['predictresult']
            for predict in range(0,len(PredictResults)):
                maingame = PredictResults[predict]['maingame']
                othergame = PredictResults[predict]['othergame']
                if (maingame != '') or (othergame != ''):  
                    PredictResultsFlex_sport = json.load(open('static/PredictResultsFlex - 聯盟.json', 'r', encoding='utf-8'))
                    type_ = PredictResults[predict]['type']
                    profit = int(PredictResults[predict]['profit'])
                    PredictResultsFlex_sport['hero']['url'] = f'https://{domain_name}/static/banner/result_banner/{sport}.png'
                    
                    #比賽日期
                    PredictResultsFlex_sport['body']['contents'][0]['contents'][2]['contents'][0]['text'] = date
                    if maingame != '':
                        result_m = maingame.split("\n")
                        for r in range(0,len(result_m)-1):
                            PredictResultsFlex_maingame = json.load(open('static/PredictResultsFlex_main.json', 'r', encoding='utf-8'))
                            result_main = result_m[r].split("|")
                            #預測結果
                            if result_main[0] == '✔️':
                                PredictResultsFlex_maingame['contents'][0]['contents'][0]['url'] = "https://i.imgur.com/hhLGaWs.png"
                            elif result_main[0] == '❌':
                                PredictResultsFlex_maingame['contents'][0]['contents'][0]['url'] = "https://i.imgur.com/us09Xz2.png"
                            else:
                                PredictResultsFlex_maingame['contents'][0]['contents'][0]['url'] = "https://i.imgur.com/iLaFnYQ.png"
                            #隊伍名稱
                            if result_main[1] in teamname.index:
                                home = teamname[teamname.index == result_main[1]]['縮寫'].iloc[0]
                            else:
                                home = result_main[1]
                            if result_main[3] in teamname.index:
                                away = teamname[teamname.index == result_main[3]]['縮寫'].iloc[0]
                            else:
                                away = result_main[3]
                            #主隊名稱
                            PredictResultsFlex_maingame['contents'][1]['contents'][0]['contents'][0]['text'] = home
                            #客隊名稱
                            PredictResultsFlex_maingame['contents'][1]['contents'][2]['contents'][0]['text'] = away
                            #比分
                            point = result_main[2].split(' ')
                            #主隊分數
                            PredictResultsFlex_maingame['contents'][1]['contents'][1]['contents'][0]['contents'][0]['text'] = point[0]
                            #客隊分數
                            PredictResultsFlex_maingame['contents'][1]['contents'][1]['contents'][2]['contents'][0]['text'] = point[2]
                            #主推賽事
                            PredictResultsFlex_sport['body']['contents'][2]['contents'] += [PredictResultsFlex_maingame]
                    else:
                        result_m = ['1']
                        message = [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                              {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": "無主推賽事",
                                    "weight": "bold",
                                    "size": "20px"
                                  }
                                ],
                                "alignItems": "center"
                              }
                            ],
                            "justifyContent": "center",
                            "spacing": "5px",
                            "backgroundColor": "#ffffff",
                            "margin": "5px",
                            "width": "98%",
                            "height": "40px",
                            "cornerRadius": "md",
                            "alignItems": "center",
                            "offsetBottom": "4px"
                          }
                        ]
                        #無主推賽事
                        PredictResultsFlex_sport['body']['contents'][2]['contents'] += message

                    if othergame != '':
                        result_o = othergame.split("\n")
                        for r in range(0,len(result_o)-1):
                            PredictResultsFlex_othergame = json.load(open('static/PredictResultsFlex_other.json', 'r', encoding='utf-8'))
                            result_other = result_o[r].split("|")
                            #預測結果
                            if result_other[0] == '✔️':
                                PredictResultsFlex_othergame['contents'][0]['contents'][0]['url'] = "https://i.imgur.com/hhLGaWs.png"
                            elif result_other[0] == '❌':
                                PredictResultsFlex_othergame['contents'][0]['contents'][0]['url'] = "https://i.imgur.com/us09Xz2.png"
                            else:
                                PredictResultsFlex_othergame['contents'][0]['contents'][0]['url'] = "https://i.imgur.com/iLaFnYQ.png"
                            #隊伍名稱
                            if (result_other[1] in teamname.index) and (result_other[3] in teamname.index):
                                home = teamname[teamname.index == result_other[1]]['縮寫'].iloc[0]
                                away = teamname[teamname.index == result_other[3]]['縮寫'].iloc[0]
                            else:
                                home = result_other[1]
                                away = result_other[3]
                            #主隊名稱
                            PredictResultsFlex_othergame['contents'][1]['contents'][0]['contents'][0]['text'] = home
                            #客隊名稱
                            PredictResultsFlex_othergame['contents'][1]['contents'][2]['contents'][0]['text'] = away
                            #比分
                            point = result_other[2].split(' ')
                            #主隊分數
                            PredictResultsFlex_othergame['contents'][1]['contents'][1]['contents'][0]['contents'][0]['text'] = point[0]
                            #客隊分數
                            PredictResultsFlex_othergame['contents'][1]['contents'][1]['contents'][2]['contents'][0]['text'] = point[2]
                            #其他賽事
                            PredictResultsFlex_sport['body']['contents'][3]['contents'][5]['contents'][0]['contents'][0]['contents'] += [PredictResultsFlex_othergame]
                    else:
                        result_o = ['1']
                        #其他賽事消失
                        PredictResultsFlex_sport['body']['contents'][3]['height'] = '0px'

                    #報酬率
                    if int(profit) > 0:
                        totalgame = len(result_m) + len(result_o) - 2
                        total_rate = round(int((profit / (totalgame*1000))*100),0)
                        PredictResultsFlex_sport['footer']['contents'][1]['contents'][0]['text'] = "今日投報率 : " + str(total_rate) + "%"         
                    else:   
                        PredictResultsFlex_sport['footer']['contents'][1]['height'] = '0px'

                    predictresult_text += [PredictResultsFlex_sport]
            
        Carousel ={
          "type": "carousel",
          "contents": predictresult_text
        }
        return Carousel
    except Exception as e:
        print(e)

#PK賽事配對成功的FlexMessage
def set_PKMatchFlex(UserId,data,ToUser=1):
    all_member = get_member()
    member1 = all_member[all_member['UserId'] == data['UserId1']]['member'].iloc[0]
    member2 = all_member[all_member['UserId'] == UserId]['member'].iloc[0]
    PKMatchFlex= json.load(open('static/PKMatchFlex.json', 'r', encoding='utf-8'))
    #發起者名稱
    PKMatchFlex['body']['contents'][1]['contents'][0]['text'] = member1
    #發起者大頭
    PKMatchFlex['body']['contents'][2]['contents'][0]['url'] = f"https://{domain_name}/static/memberlogo/{data['UserId1']}.png?timestamp={g.timestamp}"
    #發起者選擇
    PKMatchFlex['body']['contents'][6]['contents'][0]['text'] = data['option1'].replace(" ","+")
    #挑戰者名稱
    PKMatchFlex['body']['contents'][3]['contents'][0]['text'] = member2
    #挑戰者大頭
    PKMatchFlex['body']['contents'][4]['contents'][0]['url'] = f"https://{domain_name}/static/memberlogo/{UserId}.png?timestamp={g.timestamp}"
    #挑戰者選擇
    PKMatchFlex['body']['contents'][5]['contents'][0]['text'] = data['option2'].replace(" ","+")
    #賽事時間
    PKMatchFlex['body']['contents'][7]['contents'][0]['contents'][0]['text'] = \
    f"開賽時間 : {data['MatchTime'][5:-3]}"
    #PK場號
    PKMatchFlex['body']['contents'][7]['contents'][2]['contents'][0]['text'] = f"PK場號 : {data['id']}"
    #盤口
    PKMatchFlex['body']['contents'][7]['contents'][3]['contents'][0]['text'] = data['GroupOptionName']
    #主隊
    PKMatchFlex['body']['contents'][7]['contents'][4]['contents'][0]['contents'][0]['text'] = data['HomeTeam']
    #客隊
    PKMatchFlex['body']['contents'][7]['contents'][4]['contents'][2]['contents'][0]['text'] = data['AwayTeam']
    #成功配對
    if ToUser == 1:
        PKMatchFlex['body']['contents'][7]['contents'][5]['contents'][0]['text'] = \
        f"{member2}已接受挑戰"
    elif ToUser == 2:
        PKMatchFlex['body']['contents'][7]['contents'][5]['contents'][0]['text'] = \
        f"您成功接受{member1}挑戰"
    return PKMatchFlex

#查詢指定期間的賽事類別
def sql_SearchLastGame(day,scope=1):
    if day <= -1:
        SQL = """
            SELECT A.TournamentText,B.CName,b.Popular, 1 as rowOrder
            FROM [dbo].[MatchResults] AS A 
            INNER JOIN Games AS B ON A.TournamentText = B.game 
            WHERE MatchTime >= '{0}' and  MatchTime < '{1}'  AND time_status = 'Ended'  and b.Popular != 0
            group by a.TournamentText,b.CName,b.Popular         
        UNION

        SELECT A.TournamentText,B.CName,b.Popular, 2 as rowOrder
                      FROM [dbo].[MatchResults] AS A 
                      INNER JOIN Games AS B ON A.TournamentText = B.game 
                      WHERE MatchTime >= '{0}' and  MatchTime < '{1}'  AND time_status = 'Ended'  and b.Popular = 0
                      group by a.TournamentText,b.CName,b.Popular
        ORDER BY rowOrder,Popular asc
        """.format((datetime.now()+timedelta(days=day)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'),
                  (datetime.now()).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'))
        results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    else:
        SQL ="""
            SELECT A.TournamentText,B.CName,b.Popular, 1 as rowOrder
              FROM [dbo].[MatchEntry] AS A 
              INNER JOIN Games AS B ON A.TournamentText = B.game 
              WHERE MatchTime >= '{0}' and  MatchTime < '{1}' and b.Popular != 0
              group by a.TournamentText,b.CName,b.Popular
            UNION
            SELECT A.TournamentText,B.CName,b.Popular, 2 as rowOrder
              FROM [dbo].[MatchEntry] AS A 
              INNER JOIN Games AS B ON A.TournamentText = B.game 
              WHERE MatchTime >= '{0}' and  MatchTime < '{1}' and b.Popular = 0
              group by a.TournamentText,b.CName,b.Popular
            ORDER BY rowOrder,Popular asc
        """.format((datetime.now()+timedelta(days=day)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'),
                   (datetime.now()+timedelta(days=(day+scope))).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'))
        results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    tournametext = results_df.drop_duplicates(subset=None, 
                          keep='first', 
                          inplace=False, 
                          ignore_index=True)
    
    return tournametext

#指定期間賽事的賽果
def SearchMatchResult(day,sport):
    SQL = """SELECT distinct B.id,A.MatchTime,A.HomeTeam AS 'Home',A.AwayTeam as 'Away',B.name as 'HomeTeam',C.name as 'AwayTeam',A.HomeScore,A.AwayScore
          FROM MatchResults AS A
          full outer JOIN teams AS B ON A.HomeTeam = B.team 
          full outer JOIN teams AS C ON A.AwayTeam = C.team
          WHERE TournamentText = '{}' and MatchTime >= '{}' and MatchTime < '{}' AND time_status = 'Ended'
          ORDER BY MatchTime ASC
    """.format(sport,
               (datetime.now()+timedelta(days=day)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'),
               (datetime.now()+timedelta(days=(day+1))).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'))
    results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    if len(results_df) == 0:
        return None
        
    MatchResultBanner_Flex = json.load(open('static/lastmatchresult_banner.json', 'r', encoding='utf-8'))
    #banner
    sport_b = sport.replace(" ","_")
    MatchResultBanner_Flex['hero']['url'] = f"https://{domain_name}/static/banner/result_banner/{sport_b}.png"
    #聯盟
    MatchResultBanner_Flex['body']['contents'][1]['contents'][0]['text'] = f"聯盟 : {sport}"
    #開賽日期
    MatchResultBanner_Flex['body']['contents'][2]['contents'][0]['text'] = f"開賽日期 : {(datetime.now()+timedelta(days=int(day))).astimezone(timezone(timedelta(hours=8))).strftime('%m/%d')}"
    #賽事
    for game in range(0,len(results_df)):
        MatchResult_Flex = json.load(open('static/lastmatchresult_賽事.json', 'r', encoding='utf-8'))
        #主隊
        if pd.isnull(results_df['HomeTeam'][game]):
            MatchResult_Flex['contents'][0]['contents'][0]['text'] = results_df['Home'][game]
        else:
            MatchResult_Flex['contents'][0]['contents'][0]['text'] = results_df['HomeTeam'][game]
        #比分
        if len(results_df['HomeScore'][game]) == 3 or len(results_df['AwayScore'][game]) == 3:
            MatchResult_Flex['contents'][1]['contents'][0]['text'] = f"{results_df['HomeScore'][game]}:{results_df['AwayScore'][game]}"
        else:
            MatchResult_Flex['contents'][1]['contents'][0]['text'] = f"{results_df['HomeScore'][game]} : {results_df['AwayScore'][game]}"
        #客隊
        if pd.isnull(results_df['AwayTeam'][game]):
            MatchResult_Flex['contents'][2]['contents'][0]['text'] = results_df['Away'][game]
        else:
            MatchResult_Flex['contents'][2]['contents'][0]['text'] = results_df['AwayTeam'][game]
        #獲勝隊伍標記
        if int(results_df['HomeScore'][game]) > int(results_df['AwayScore'][game]):
            #主隊
            MatchResult_Flex['contents'][0]['contents'][0]['color'] = '#2a7bcf'
            MatchResult_Flex['contents'][0]['contents'][0]['weight'] = 'bold'
            #客隊
            MatchResult_Flex['contents'][2]['contents'][0]['color'] = '#000000'
            MatchResult_Flex['contents'][2]['contents'][0]['weight'] = 'regular'
        elif int(results_df['HomeScore'][game]) < int(results_df['AwayScore'][game]):
            #主隊
            MatchResult_Flex['contents'][0]['contents'][0]['color'] = '#000000'
            MatchResult_Flex['contents'][0]['contents'][0]['weight'] = 'regular'
            #客隊
            MatchResult_Flex['contents'][2]['contents'][0]['color'] = '#2a7bcf'
            MatchResult_Flex['contents'][2]['contents'][0]['weight'] = 'bold'
        else:
            #主隊
            MatchResult_Flex['contents'][0]['contents'][0]['color'] = '#000000'
            MatchResult_Flex['contents'][0]['contents'][0]['weight'] = 'regular'
            #客隊
            MatchResult_Flex['contents'][2]['contents'][0]['color'] = '#000000'
            MatchResult_Flex['contents'][2]['contents'][0]['weight'] = 'regular'
        MatchResultBanner_Flex['body']['contents'][3]['contents'].append(MatchResult_Flex)
    return MatchResultBanner_Flex

def SearchPlayingMatch(sport):
    print(time.ctime())
    results_df = search_match(sport)    
    MatchResultBanner_Flex = json.load(open('static/playingmatchresult_banner.json', 'r', encoding='utf-8'))
    #banner
    sport_b = sport.replace(" ","_")
    MatchResultBanner_Flex['hero']['url'] = f"https://{domain_name}/static/banner/result_banner/{sport_b}.png"
    #聯盟
    MatchResultBanner_Flex['body']['contents'][1]['contents'][0]['text'] = f"聯盟：{sport}"
    #開賽日期
    MatchResultBanner_Flex['body']['contents'][2]['contents'][0]['text'] = f"開賽日期：{datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%m/%d %H:%M')}"
    #賽事
    eventcode = results_df['EventCode'].values
    games = []
    split = len(eventcode) // 10
    for s in range(0,split+1):
        event_str = ",".join(eventcode[10*s:10*(s+1)])
        url = "https://betsapi2.p.rapidapi.com/v1/bet365/result"

        querystring = {"event_id":event_str}

        headers = {
         "X-RapidAPI-Key": "e61dc7c98emsh4f32f403fe98f3fp12628cjsn98c844755a26",
         "X-RapidAPI-Host": "betsapi2.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        games += json.loads(response.text)['results']
    for game in range(0,len(games)):
        if games[game]['ss'] != None:
            score = games[game]['ss'].split("-")
            awayscore = score[0]
            homescore = score[1]
        else:
            awayscore = None
            homescore = None
        time_status = games[game]['time_status']
        MatchResult_Flex = json.load(open('static/lastmatchresult_賽事.json', 'r', encoding='utf-8'))
        #主隊
        if pd.isnull(results_df['HomeTeam'].iloc[game]):
            MatchResult_Flex['contents'][0]['contents'][0]['text'] = results_df['Home'].iloc[game]
        else:
            MatchResult_Flex['contents'][0]['contents'][0]['text'] = results_df['HomeTeam'].iloc[game]
        if time_status in ['1','3']:
            #比分
            MatchResult_Flex['contents'][1]['contents'][0]['text'] = f"{homescore}:{awayscore}"
        else:
            MatchResult_Flex['contents'][1]['contents'][0]['text'] = "-：-"
        #客隊
        if pd.isnull(results_df['AwayTeam'].iloc[game]):
            MatchResult_Flex['contents'][2]['contents'][0]['text'] = results_df['Away'].iloc[game]
        else:
            MatchResult_Flex['contents'][2]['contents'][0]['text'] = results_df['AwayTeam'].iloc[game]
        if time_status == '3':
            #獲勝隊伍標記
            if int(homescore) > int(awayscore):
                #主隊
                MatchResult_Flex['contents'][0]['contents'][0]['color'] = '#2a7bcf'
                MatchResult_Flex['contents'][0]['contents'][0]['weight'] = 'bold'
                #客隊
                MatchResult_Flex['contents'][2]['contents'][0]['color'] = '#000000'
                MatchResult_Flex['contents'][2]['contents'][0]['weight'] = 'regular'
            elif int(homescore) < int(awayscore):
                #主隊
                MatchResult_Flex['contents'][0]['contents'][0]['color'] = '#000000'
                MatchResult_Flex['contents'][0]['contents'][0]['weight'] = 'regular'
                #客隊
                MatchResult_Flex['contents'][2]['contents'][0]['color'] = '#2a7bcf'
                MatchResult_Flex['contents'][2]['contents'][0]['weight'] = 'bold'
            else:
                #主隊
                MatchResult_Flex['contents'][0]['contents'][0]['color'] = '#000000'
                MatchResult_Flex['contents'][0]['contents'][0]['weight'] = 'regular'
                #客隊
                MatchResult_Flex['contents'][2]['contents'][0]['color'] = '#000000'
                MatchResult_Flex['contents'][2]['contents'][0]['weight'] = 'regular'
        else:
            #主隊
            MatchResult_Flex['contents'][0]['contents'][0]['color'] = '#000000'
            MatchResult_Flex['contents'][0]['contents'][0]['weight'] = 'regular'
            #客隊
            MatchResult_Flex['contents'][2]['contents'][0]['color'] = '#000000'
            MatchResult_Flex['contents'][2]['contents'][0]['weight'] = 'regular'
        MatchResultBanner_Flex['body']['contents'][3]['contents'].append(MatchResult_Flex)
    return MatchResultBanner_Flex

#查詢DB所有盤口
def search_groupoption(sport,day):
    if day == '0':
        SQL = """
              SELECT distinct B.Type_cname
              FROM [dbo].[Odds] AS A
              INNER JOIN GroupOptionCode AS B ON A.GroupOptionCode = B.GroupOptionCode1 
              INNER JOIN MatchEntry AS C ON A.EventCode = C.EventCode
              where C.TournamentText ='{}' and MatchTime >= '{}' and MatchTime < '{}'
            """.format(sport,
                      datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                      datetime.now().astimezone(timezone(timedelta(hours=8))).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999'))
    elif day == '1':
        SQL = """
              SELECT distinct B.Type_cname
              FROM [dbo].[Odds] AS A
              INNER JOIN GroupOptionCode AS B ON A.GroupOptionCode = B.GroupOptionCode1 
              INNER JOIN MatchEntry AS C ON A.EventCode = C.EventCode
              where C.TournamentText ='{}' and MatchTime >= '{}' and MatchTime < '{}'
            """.format(sport,
                      (datetime.now()+timedelta(1)).astimezone(timezone(timedelta(hours=8))).replace(hour=0,minute=0,second=0).strftime('%Y-%m-%d %H:%M:%S.000'),
                      (datetime.now()+timedelta(1)).astimezone(timezone(timedelta(hours=8))).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999'))
    results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 

    results_df = results_df.drop(results_df[results_df["Type_cname"] == '全場雙勝彩'].index)
    return results_df

def search_match(sport):
    SQL = """
        SELECT distinct A.MatchTime,A.EventCode,A.HomeTeam AS 'Home',A.AwayTeam as 'Away',C.name as 'HomeTeam',D.name as 'AwayTeam',B.HomeScore,B.AwayScore
          FROM MatchEntry AS A
          FULL OUTER JOIN MatchResults AS B ON A.EventCode = B.EventCode
          full outer JOIN teams AS C ON A.HomeTeam = C.team 
          full outer JOIN teams AS D ON A.AwayTeam = D.team
          INNER JOIN [Odds] AS E ON A.EventCode = E.EventCode
          WHERE A.TournamentText = '{}' and A.MatchTime >= '{}' and A.MatchTime < '{}' 
          ORDER BY MatchTime ASC
    """.format(sport,
              (datetime.now()).astimezone(timezone(timedelta(hours=8))).replace(hour=0,minute=0,second=0).strftime('%Y-%m-%d %H:%M:%S.000'),
              (datetime.now()).astimezone(timezone(timedelta(hours=8))).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.999'))
    results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True,index_col='MatchTime') 
    return results_df

#查詢指定盤口賠率
def Searchoption(sport=False,groupoption=False,search_all=False):
    if search_all:
        SQL = """SELECT distinct A.GroupOptionCode,A.OptionCode,C.Type_cname,B.TournamentText
              FROM [dbo].[Odds] AS A
              INNER JOIN MatchEntry AS B ON A.EventCode = B.EventCode
              INNER JOIN GroupOptionCode AS C ON A.GroupOptionCode = C.GroupOptionCode1
            """
        results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
        return result_df
    elif sport and groupoption:    
        SQL = """SELECT distinct A.GroupOptionCode,A.OptionCode
              FROM [dbo].[Odds] AS A
              INNER JOIN MatchEntry AS B ON A.EventCode = B.EventCode
              INNER JOIN GroupOptionCode AS C ON A.GroupOptionCode = C.GroupOptionCode1
              WHERE C.Type_cname = N'{}' AND B.TournamentText = '{}'
            """.format(groupoption,sport)
        results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
        option = list(results_df['OptionCode'])
        groupoptioncode = results_df['GroupOptionCode'].iloc[1]
        return option,groupoptioncode

#查詢所有最新賽事
def SearchMatchEntry(day,sport,option,groupoptioncode): 
    if len(option) == 3:
        SQL = """
        SELECT A.HomeTeam as 'Home',A.AwayTeam as 'Away',D.name as 'HomeTeam',E.name as 'AwayTeam',A.MatchTime,B.OptionRate AS 'Homeodds',C.OptionRate AS 'Awayodds',B.SpecialBetValue,F.OptionRate AS 'tieodds'
        FROM [dbo].[MatchEntry] AS A
        INNER JOIN odds AS B ON A.EventCode = B.EventCode
        INNER JOIN odds AS C ON A.EventCode = C.EventCode
        full outer JOIN teams AS D ON A.HomeTeam = D.team 
        full outer JOIN teams AS E ON A.AwayTeam = E.team
        INNER JOIN odds AS F ON A.EventCode = F.EventCode
        where TournamentText = '{}' AND 
        A.MatchTime >= '{}' AND 
        MatchTime < '{}' AND 
        B.GroupOptionCode = '{}' AND 
        B.OptionCode= '{}' AND  
        C.GroupOptionCode = '{}' AND 
        C.OptionCode = '{}' AND  
        F.GroupOptionCode = '{}' AND 
        F.OptionCode = '{}'  
        ORDER BY A.MatchTime ASC
        """.format(sport,
                   (datetime.now()+timedelta(days=int(day))).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'),
                   (datetime.now()+timedelta(days=(int(day)+1))).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'),
                   groupoptioncode,option[0],
                   groupoptioncode,option[1],
                   groupoptioncode,option[2])
    else:
        SQL = """
            SELECT A.HomeTeam as 'Home',A.AwayTeam as 'Away',D.name as 'HomeTeam',E.name as 'AwayTeam',A.MatchTime,B.OptionRate AS 'Homeodds',C.OptionRate AS 'Awayodds',B.SpecialBetValue
            FROM [dbo].[MatchEntry] AS A
            INNER JOIN odds AS B ON A.EventCode = B.EventCode
            INNER JOIN odds AS C ON A.EventCode = C.EventCode
            full outer JOIN teams AS D ON A.HomeTeam = D.team 
            full outer JOIN teams AS E ON A.AwayTeam = E.team
            where TournamentText = '{}' AND 
            A.MatchTime >= '{}' AND 
            MatchTime < '{}' AND 
            B.GroupOptionCode = '{}' AND 
            B.OptionCode= '{}' AND  
            C.GroupOptionCode = '{}' AND 
            C.OptionCode = '{}' 
            ORDER BY A.MatchTime ASC
            """.format(sport,
                      (datetime.now()+timedelta(days=int(day))).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'),
                      (datetime.now()+timedelta(days=(int(day)+1))).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'),
                      groupoptioncode,option[0],
                      groupoptioncode,option[1])
    results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    return results_df

#
def MatchEntryFlex(day,sport,cname,option,groupoption,groupoptioncode,SearchMatch):
    MatchEntryBanner_Flex = json.load(open('static/lastnewgame_banner.json', 'r', encoding='utf-8'))
    #banner
    sport_b = sport.replace(" ","_")
    MatchEntryBanner_Flex['hero']['url'] = f"https://{domain_name}/static/banner/match_banner/{sport_b}.png"
    #聯盟
    MatchEntryBanner_Flex['body']['contents'][1]['contents'][0]['text'] = f"聯盟 : {sport}"
    #開賽日期
    MatchEntryBanner_Flex['body']['contents'][2]['contents'][0]['text'] = f"開賽日期 : {(datetime.now()+timedelta(days=int(day))).astimezone(timezone(timedelta(hours=8))).strftime('%m/%d')}"
    #盤口
    MatchEntryBanner_Flex['body']['contents'][3]['contents'][0]['contents'][1]['contents'][0]['text'] = groupoption
    
    #查詢最新賽事的FlexMessage
    for Match in range(len(SearchMatch)):
        if SearchMatch['MatchTime'][Match] > (datetime.now()):
            
            if len(option) == 3:
                MatchEntry_Flex = json.load(open('static/lastnewgame_have3.json', 'r', encoding='utf-8'))
                #賽時
                time = SearchMatch['MatchTime'][Match].strftime("%H:%M")
                MatchEntry_Flex['contents'][0]['contents'][0]['text'] = f"開賽時間 : {time}"
                #主隊隊名
                if pd.isnull(SearchMatch['HomeTeam'][Match]):
                     MatchEntry_Flex['contents'][1]['contents'][0]['contents'][0]['contents'][0]['text'] = SearchMatch['Home'][Match]
                else:
                    MatchEntry_Flex['contents'][1]['contents'][0]['contents'][0]['contents'][0]['text'] = SearchMatch['HomeTeam'][Match]
                #客隊隊名
                if pd.isnull(SearchMatch['AwayTeam'][Match]):
                    MatchEntry_Flex['contents'][1]['contents'][0]['contents'][0]['contents'][1]['text'] = SearchMatch['Away'][Match]
                else:
                    MatchEntry_Flex['contents'][1]['contents'][0]['contents'][0]['contents'][1]['text'] = SearchMatch['AwayTeam'][Match]
                #主隊(獲勝條件)
                MatchEntry_Flex['contents'][1]['contents'][0]['contents'][1]['contents'][0]['text'] = '主'
                #客隊(獲勝條件)
                MatchEntry_Flex['contents'][1]['contents'][0]['contents'][1]['contents'][1]['text'] = '客'
                #平手(獲勝條件)
                MatchEntry_Flex['contents'][1]['contents'][0]['contents'][1]['contents'][2]['text'] = '平'
                #主隊(賠率)
                MatchEntry_Flex['contents'][1]['contents'][0]['contents'][2]['contents'][0]['contents'][0]['text'] = SearchMatch['Homeodds'][Match]
                #客隊(賠率)
                MatchEntry_Flex['contents'][1]['contents'][0]['contents'][2]['contents'][1]['contents'][0]['text'] = SearchMatch['Awayodds'][Match]
                #平手(賠率)
                MatchEntry_Flex['contents'][1]['contents'][0]['contents'][2]['contents'][2]['contents'][0]['text'] = SearchMatch['tieodds'][Match]
            else:
                MatchEntry_Flex = json.load(open('static/lastnewgame.json', 'r', encoding='utf-8'))
                #賽時
                time = SearchMatch['MatchTime'][Match].strftime("%H:%M")
                MatchEntry_Flex['contents'][0]['contents'][0]['text'] = f"開賽時間 : {time}"
                #主隊隊名
                if pd.isnull(SearchMatch['HomeTeam'][Match]):
                     MatchEntry_Flex['contents'][1]['contents'][0]['contents'][0]['contents'][0]['text'] = SearchMatch['Home'][Match]
                else:
                    MatchEntry_Flex['contents'][1]['contents'][0]['contents'][0]['contents'][0]['text'] = SearchMatch['HomeTeam'][Match]
                #客隊隊名
                if pd.isnull(SearchMatch['AwayTeam'][Match]):
                    MatchEntry_Flex['contents'][1]['contents'][1]['contents'][0]['contents'][0]['text'] = SearchMatch['Away'][Match]
                else:
                    MatchEntry_Flex['contents'][1]['contents'][1]['contents'][0]['contents'][0]['text'] = SearchMatch['AwayTeam'][Match]
                #獲勝條件
                if groupoption == '全場獲勝':
                    option1 = '主'
                    option2 = '客'
                elif groupoption == '全場讓分':
                    if float(SearchMatch['SpecialBetValue'][Match]) > 0:
                        SpecialBetValue = SearchMatch['SpecialBetValue'][Match][1:]
                        option1 = f'主+{SpecialBetValue}'
                        option2 = f'主-{SpecialBetValue}'
                    else:
                        SpecialBetValue = SearchMatch['SpecialBetValue'][Match][1:]
                        option1 = f'主-{SpecialBetValue}'
                        option2 = f'主+{SpecialBetValue}'
                elif groupoption == '全場大小':
                    SpecialBetValue = SearchMatch['SpecialBetValue'][Match]
                    option1 = f'大於{SpecialBetValue}'
                    option2 = f'小於{SpecialBetValue}'
                #主隊(獲勝條件)
                MatchEntry_Flex['contents'][1]['contents'][0]['contents'][1]['contents'][0]['text'] = option1
                #客隊(獲勝條件)
                MatchEntry_Flex['contents'][1]['contents'][1]['contents'][1]['contents'][0]['text'] = option2
                #主隊(賠率)
                MatchEntry_Flex['contents'][1]['contents'][0]['contents'][2]['contents'][0]['text'] = SearchMatch['Homeodds'][Match]
                #客隊(賠率)
                MatchEntry_Flex['contents'][1]['contents'][1]['contents'][2]['contents'][0]['text'] = SearchMatch['Awayodds'][Match]

            #串接
            MatchEntryBanner_Flex['body']['contents'][3]['contents'].append(MatchEntry_Flex)
    return MatchEntryBanner_Flex

#預測賽事的賽事資訊
def manualpushsearch(evencode,option,groupoptioncode):
    if len(option) == 3:
        SQL = """
            SELECT A.EventCode,A.SportText,C.GroupOptionCode,D.name as 'HomeTeam',E.name as 'AwayTeam',A.MatchTime,B.OptionRate AS 'Homeodds',C.OptionRate AS 'Awayodds',B.SpecialBetValue,F.OptionRate AS 'tieodds'
            FROM [dbo].[MatchEntry] AS A
            INNER JOIN odds AS B ON A.EventCode = B.EventCode
            INNER JOIN odds AS C ON A.EventCode = C.EventCode
            full outer JOIN teams AS D ON A.HomeTeam = D.team 
            full outer JOIN  teams AS E ON A.AwayTeam = E.team
            INNER JOIN odds AS F ON A.EventCode = F.EventCode
            where A.EventCode= '{}'AND B.OptionCode= '{}' AND  
            C.GroupOptionCode = '{}'AND B.GroupOptionCode = '{}' AND
            C.OptionCode = '{}' AND  F.GroupOptionCode = '{}' AND F.OptionCode = '{}'
            ORDER BY A.MatchTime ASC
            """.format(evencode,option[0],groupoptioncode,groupoptioncode,option[1],groupoptioncode,option[2])
    else:
        SQL = """
            SELECT A.EventCode,A.SportText,C.GroupOptionCode,D.name as 'HomeTeam',E.name as 'AwayTeam',A.MatchTime,B.OptionRate AS 'Homeodds',C.OptionRate AS 'Awayodds',B.SpecialBetValue
            FROM [dbo].[MatchEntry] AS A
            INNER JOIN odds AS B ON A.EventCode = B.EventCode
            INNER JOIN odds AS C ON A.EventCode = C.EventCode
            full outer JOIN teams AS D ON A.HomeTeam = D.team 
            full outer JOIN  teams AS E ON A.AwayTeam = E.team
            INNER JOIN odds AS F ON A.EventCode = F.EventCode
            where A.EventCode= '{}'AND B.OptionCode= '{}' AND  
            C.GroupOptionCode = '{}'AND B.GroupOptionCode = '{}' AND C.OptionCode = '{}'
            ORDER BY A.MatchTime ASC
            """.format(evencode,option[0],groupoptioncode,groupoptioncode,option[1])
    results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)  
    return results_df

#查詢會員資訊
def get_UserId(account,password):
    try:
        SQL = "select * from UserMember where member = '{}' and Password = '{}' ".format(account,password)
        result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
        return result['UserId'].iloc[0]
    except:
        return None

#查詢賽事盤口中文名稱
def get_GroupOptionName(SportCode, GroupOptionCode):
    SQL = "select * from [GroupOptionCode] where SportCode = '{}' and GroupOptionCode1 = '{}' ".format(SportCode,GroupOptionCode)
    result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    return result['Type'].iloc[0]

#根據DB中的option轉換成下注隊伍名稱
def Mapping_PredictTeamName(OptionCode,SportCode,GroupOptionCode,HomeTeam,AwayTeam):
    if SportCode == '1' and GroupOptionCode in ('55'):
        texts = [OptionCode.split('/')[0].strip(), OptionCode.split('/')[1].strip()]
        if not texts[0] == 'Draw' and not texts[1] == 'Draw':
            PredictTeam = texts[1]
        elif not texts[0] == 'Draw' and texts[1] == 'Draw':
            PredictTeam = texts[0]
        elif texts[0] == 'Draw' and not texts[1] == 'Draw':
            PredictTeam = texts[1]
        return PredictTeam.replace(r"'", r"''")
    else:
        if OptionCode == '1':
            PredictTeam = HomeTeam
        elif OptionCode == '2':
            PredictTeam = AwayTeam
        else:
            PredictTeam = ''
        return PredictTeam.replace(r"'", r"''")

#將推播賽事寫到dbo.LIENPushMatch中
def write_linepushmessage(predict,tie):
    account = predict['account']
    password = predict['password']
    evencode = predict['EventCode']
    OptionCode = predict['OptionCode']
    groupoptioncode = predict['GroupOptionCode']
    homeodds = predict['HomeOdds']
    awayodds = predict['AwayOdds']
    homeconfidence = predict['HomeConfidence'].replace("%","")
    awayconfidence = predict['AwayConfidence'].replace("%","")
    main = predict['main']
    SQL = """select * from MatchEntry 
        where EventCode = '{}' and MatchTime >= '{}'  
        """.format(evencode,datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
    results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    if len(results_df)> 0:
        MatchEntry = results_df.iloc[0]

        SQL = """
            select * from Odds 
                where EventCode = '{}' and GroupOptionCode='{}' and OptionCode='{}'
        """.format(evencode,groupoptioncode,OptionCode)
        results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
        Odds = results_df.iloc[0]
        UserId = get_UserId(account,password)
        if tie == True:
            tieodds = predict['TieOdds']
            tieconfidence = predict['TieConfidence'].replace("%","")
            LinePush_sql = '''INSERT INTO [dbo].[LINEPushMatch] ([UserId],[SportCode],[EventType],[EventCode],[TournamentCode],[TournamentText],[GroupOptionCode],[GroupOptionName],[PredictTeam],[OptionCode],
                                [SpecialBetValue],[OptionRate],[status],[gameType],[MarketType],[PredictDatetime],[CreatedTime],[HomeOdds],[AwayOdds],[TieOdds],[HomeConfidence],[AwayConfidence],[TieConfidence],[main]) 
                                VALUES('{}','{}','0','{}','{}','{}','{}','{}','{}','{}','{}','{}','2','OnlyPush','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}') \n
                            '''.format(UserId,MatchEntry['SportCode'],MatchEntry['EventCode'],MatchEntry['SportTournamentCode'],
                                      MatchEntry['TournamentText'],Odds['GroupOptionCode'],get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode']),
                                      Mapping_PredictTeamName(Odds['OptionCode'], MatchEntry['SportCode'], Odds['GroupOptionCode'], MatchEntry['HomeTeam'], MatchEntry['AwayTeam']),
                                      Odds['OptionCode'],Odds['SpecialBetValue'],Odds['OptionRate'],
                                      "international" if MatchEntry['SourceCode'] == "Bet365" else "sportslottery",
                                      datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                      datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                      homeodds,awayodds,tieodds,homeconfidence,awayconfidence,tieconfidence,main)
        else:
            LinePush_sql = '''INSERT INTO [dbo].[LINEPushMatch] ([UserId],[SportCode],[EventType],[EventCode],[TournamentCode],[TournamentText],[GroupOptionCode],[GroupOptionName],[PredictTeam],[OptionCode],
                                [SpecialBetValue],[OptionRate],[status],[gameType],[MarketType],[PredictDatetime],[CreatedTime],[HomeOdds],[AwayOdds],[HomeConfidence],[AwayConfidence],[main]) 
                                    VALUES('{}','{}','0','{}','{}','{}','{}','{}','{}','{}','{}','{}','2','OnlyPush','{}','{}','{}','{}','{}','{}','{}','{}') \n
                                '''.format(UserId,MatchEntry['SportCode'],MatchEntry['EventCode'],MatchEntry['SportTournamentCode'],
                                          MatchEntry['TournamentText'],Odds['GroupOptionCode'],get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode']),
                                          Mapping_PredictTeamName(Odds['OptionCode'], MatchEntry['SportCode'], Odds['GroupOptionCode'], MatchEntry['HomeTeam'], MatchEntry['AwayTeam']),
                                          Odds['OptionCode'],Odds['SpecialBetValue'],Odds['OptionRate'],
                                          "international" if MatchEntry['SourceCode'] == "Bet365" else "sportslottery",
                                          datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                          datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                          homeodds,awayodds,homeconfidence,awayconfidence,main)
        return LinePush_sql
    else:
        return "game had start!!"
    
    
#查詢dbo.LIENPushMatch指定賽事中最新的id
def maxid(pre):
    evencode = pre['EventCode']
    groupoptioncode = pre['GroupOptionCode']
    SQL = """
          SELECT MAX(id) as maxid
          FROM [dbo].[LINEPushMatch]
          WHERE EventCode = '{}' AND GroupOptionCode = '{}'
    """.format(evencode,groupoptioncode)
    results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    pushid = results['maxid'].iloc[0]
    return pushid

#將推播的會員寫入dbo.LinePushMember
def write_linepushmember(lineid, pushid):                     
    Insert_sql = """
            INSERT INTO [dbo].[LinePushMember] (LinePushId,LineUniqueID,CreatedTime)
            values ('{}','{}','{}') \n
    """.format(pushid,lineid,datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"))
    return Insert_sql

#查詢所有dbo.Team的資訊
def TeamNameCorrection():
    SQL = f"SELECT * FROM teams"
    TeamName = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    return TeamName
    
    
#查詢所有已推送過的會員
def searchalreadlypush():
    SQL = """
        SELECT A.UserId,A.EventCode,A.GroupOptionCode,B.LineUniqueID,A.id
          FROM [dbo].[LINEPushMatch] as A
          INNER JOIN LinePushMember AS B ON A.id = B.LinePushId
          INNER JOIN MatchEntry as C ON A.EventCode = C.EventCode
          WHERE C.MatchTime >= '{}'
    """.format(datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"))
    results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    if len(results) != 0:
        return results
    else:
        return pd.DataFrame(columns=["UserId","EventCode","GroupOptionCode","LineUniqueID","id"])

    
#方形圖轉成圓形大頭照
def crop_max_square(pil_img):
    return crop_center(pil_img,min(pil_img.size),min(pil_img.size))

def crop_center(pil_img,crop_width,crop_height):
    img_width,img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width)//2,
                        (img_height - crop_height)//2,
                        (img_width + crop_width)//2,
                        (img_height + crop_height)//2))

def mask_circle_transparent(pil_img,blur_radius,offset=0):
    offset = blur_radius * 2 + offset
    mask = Image.new("L",pil_img.size,0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset,offset,pil_img.size[0] - offset,pil_img.size[1] - offset),fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    result = pil_img.copy()
    result.putalpha(mask)
    return result

#訂閱的FlexMessage
def subscriptionlinepay(sport_name,directions1,directions2,price,days,userid): 
        FlexMessage = json.load(open('static/subscriptionlinepay.json', 'r', encoding='utf-8'))
        #banner
        FlexMessage['hero']['url'] = f'https://{domain_name}/static/banner/{sport_name}.png'
        #球類名稱
        FlexMessage['body']['contents'][1]['text'] = sport_name
        #賣牌介紹1
        FlexMessage['body']['contents'][3]['text'] = directions1
        #賣牌介紹2
        FlexMessage['body']['contents'][3]['text'] = directions2
        FlexMessage['footer']['contents'][1]['action']['uri'] = f'https://liff.line.me/{linepay_liffid}?{userid}&{sport_name}&{price}&{days}'
        return FlexMessage

#查詢所有目前的訂閱資訊  
def subscriptionlist(userinfo):
    userid = userinfo['UserId']
    subscribeLevel = userinfo['SubscribeLevel'].values
    payment = userinfo['isPayment'].values
    SQL = """
        SELECT *
          FROM [dbo].[LineSubscriptionDisplayParameters]
    """
    results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)   
    
    contents = []
    for i in range(len(results)):
        sport_code = results['code'].iloc[i]
        sport_name = results['name'].iloc[i]
        price = results['price'].iloc[i]
        days= results['days'].iloc[i]
        directions1 = results['directions1'].iloc[i]
        directions2 = results['directions2'].iloc[i]
        if len(subscribeLevel) > 0:
            if sport_name  not in subscribeLevel:
                FlexMessage = subscriptionlinepay(sport_name,directions1,directions2,price,days,userid)
                contents.append(FlexMessage)
            else:
                for s in range(len(subscribeLevel)):
                    if subscribeLevel[s] == sport_name and payment[s] == 'No':
                        FlexMessage = subscriptionlinepay(sport_name,directions1,directions2,price,days,userid)
                        contents.append(FlexMessage)
        else:
            FlexMessage = subscriptionlinepay(sport_name,directions1,directions2,price,days,userid)
            contents.append(FlexMessage)
       
    if len(contents) == 0:
        contents.append('nogame')
    carousel = {
        "type": "carousel",
        "contents": contents
    }

    return carousel

#AI機器人介紹
def about_linebot(sport):
    if sport == 'NBA':
        SQL = """
            (Select distinct b.EventCode,b.TournamentText,b.GroupOptionCode,e.Type_cname,b.PredictTeam,b.OptionCode,b.SpecialBetValue,d.MatchTime,h.HomeTeam,f.name as Home_CTeam,h.AwayTeam,g.name as Away_CTeam,h.HomeScore,h.AwayScore,b.SportCode,c.Profit
                from UserMember as a
                inner join  PredictMatch as b on a.UserId = b.UserId
                inner join PredictResults as c on b.id = c.Predict_id
                INNER JOIN MatchEntry AS d on b.EventCode = d.EventCode
                inner join GroupOptionCode as e on b.GroupOptionCode = e.GroupOptionCode1
                inner join MatchResults as h on d.EventCode = h.EventCode
                inner join teams as f on h.HomeTeam = f.team
                inner join teams as g on h.AwayTeam = g.team
                where member = 'ring860112' and gameType = 'Selling' and b.TournamentText= '{0}' AND GroupOptionCode = '20' AND d.MatchTime > '2022-10-01' and d.MatchTime < '2022-11-30')
            union 
            (SELECT distinct a.EventCode,a.TournamentText,a.GroupOptionCode,e.Type_cname,a.PredictTeam,a.OptionCode,a.SpecialBetValue,
                b.MatchTime,b.HomeTeam,f.name as Home_CTeam,b.AwayTeam,g.name as Away_CTeam,b.HomeScore,b.AwayScore,a.SportCode,d.Profit
                FROM (select ROW_NUMBER() over (partition BY LINEPushMatch.EventCode order by LINEPushMatch.CreatedTime) as sn,* from LINEPushMatch) as a
                inner join MatchResults as b on a.EventCode = b.EventCode
                inner join PredictMatch as c on a.EventCode = c.EventCode and a.UserId = c.UserId
                inner join PredictResults as d on c.id = d.Predict_id
                inner join GroupOptionCode as e on a.GroupOptionCode = e.GroupOptionCode1
                inner join teams as f on b.HomeTeam = f.team
                inner join teams as g on b.AwayTeam = g.team
                where b.time_status = 'Ended' and sn = 1 and a.TournamentText = '{0}' AND MatchTime > '2022-11-30')
                order by MatchTime desc
        """.format(sport)
    elif sport == 'NPB':
        SQL = """
            SELECT distinct a.EventCode,a.TournamentText,a.GroupOptionCode,e.Type_cname,a.PredictTeam,a.OptionCode,a.SpecialBetValue,
                b.MatchTime,b.HomeTeam,f.name as Home_CTeam,b.AwayTeam,g.name as Away_CTeam,b.HomeScore,b.AwayScore,a.SportCode,d.Profit
                FROM (select ROW_NUMBER() over (partition BY LINEPushMatch.EventCode order by LINEPushMatch.CreatedTime) as sn,* from LINEPushMatch) as a
                inner join MatchResults as b on a.EventCode = b.EventCode
                inner join PredictMatch as c on a.EventCode = c.EventCode and a.UserId = c.UserId
                inner join PredictResults as d on c.id = d.Predict_id
                inner join GroupOptionCode as e on a.GroupOptionCode = e.GroupOptionCode1
                inner join teams as f on b.HomeTeam = f.team
                inner join teams as g on b.AwayTeam = g.team
                where b.time_status = 'Ended' and sn = 1 and a.TournamentText = '{0}' and b.HomeScore != b.AwayScore
                order by MatchTime desc
        """.format(sport)
    else:
        SQL = """
            SELECT distinct a.EventCode,a.TournamentText,a.GroupOptionCode,e.Type_cname,a.PredictTeam,a.OptionCode,a.SpecialBetValue,
                b.MatchTime,b.HomeTeam,f.name as Home_CTeam,b.AwayTeam,g.name as Away_CTeam,b.HomeScore,b.AwayScore,a.SportCode,d.Profit
                FROM (select ROW_NUMBER() over (partition BY LINEPushMatch.EventCode order by LINEPushMatch.CreatedTime) as sn,* from LINEPushMatch) as a
                inner join MatchResults as b on a.EventCode = b.EventCode
                inner join PredictMatch as c on a.EventCode = c.EventCode and a.UserId = c.UserId
                inner join PredictResults as d on c.id = d.Predict_id
                inner join GroupOptionCode as e on a.GroupOptionCode = e.GroupOptionCode1
                inner join teams as f on b.HomeTeam = f.team
                inner join teams as g on b.AwayTeam = g.team
                where b.time_status = 'Ended' and sn = 1 and a.TournamentText = '{0}'
                order by MatchTime desc
        """.format(sport)
    PredictResults = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True,index_col=['MatchTime']) 
    PredictResults['Profit'] = PredictResults['Profit'].replace(0,-1000)
    PredictResults['Profit'] = PredictResults['Profit']*10
    def datelimite(time):
        matchdate = datetime.strptime(PredictResults.index.strftime("%Y-%m-%d").unique()[0],"%Y-%m-%d")
        date = (matchdate - timedelta(days=time)).astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d")
        return date

    #近1日勝率
    game5 = (PredictResults[PredictResults.index >= datelimite(0)]['Profit'] > 0).mean() *100
    #近3日勝率
    game10 = (PredictResults[PredictResults.index >= datelimite(2)]['Profit'] > 0).mean() *100
    #近7日勝率
    game30 = (PredictResults[PredictResults.index >= datelimite(6)]['Profit'] > 0).mean() *100
    #近30日勝率
    game50 = (PredictResults[PredictResults.index >= datelimite(29)]['Profit'] > 0).mean() *100
    #所有勝率
    game100 = (PredictResults['Profit'] > 0).mean() *100
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
    plt.rcParams['axes.unicode_minus'] = False
    # 開新一個畫布 
    fig = plt.figure(figsize=(25, 10),facecolor='white') # 寬10 長8
    gs = GridSpec(1, 1) # 設立1x1的網格
    # 設定網格及子圖
    ax = plt.subplot(gs[0, 0],facecolor='#FFFAFA') # 子圖ax在網格的[0, 0]

    x = ['全賽季','近1月','近7日','近3日','近1日']
    y = [game100,game50,game30,game10,game5]
    ax.plot(x, y, color='red',linewidth = 10, markersize="50", marker="o")

    for x1,y1 in zip(x,y):
        ax.text(x1,y1+5,f'{int(round(y1,0))}%',fontdict={'fontsize':55},verticalalignment='bottom',horizontalalignment='center', weight='bold')

    plt.fill_between(x,0, y, facecolor='red',alpha=0.3)
    plt.xticks(fontsize=55,fontweight = "bold")
    plt.yticks(range(0,101,25),fontsize=55,fontweight = "bold",labels=['0%','25%','50%','75%','100%'])
    plt.title("近期戰績",fontsize=80,fontweight = "bold")
    plt.grid()
    plt.savefig(f'static/Profit/{sport}_profit.png',bbox_inches='tight',dpi=fig.dpi,pad_inches=0.2)
    plt.close(fig)
    aboutlinebot_Flex = json.load(open('static/about_aiprofit.json', 'r', encoding='utf-8'))
    
    profit = int(PredictResults['Profit'].sum())
    accuracy = str(round(game100,1)) + '%'
    wingame = str(len(PredictResults)) + '過' + str(len(PredictResults[PredictResults['Profit'] > 0]))
    performance_graph(PredictResults,sport)
    PredictResults.index = PredictResults.index.strftime("%Y-%m-%d")
    PredictResults_g = PredictResults.groupby(by='MatchTime',sort = False)
    count_earn = 0
    for day,match in PredictResults_g:
        profitsum = match['Profit'].sum()
        if profitsum > 0:
            count_earn += 1
        elif profitsum < 0:
            break
    
    #banner
    aboutlinebot_Flex['body']['contents'][0]['url'] = f'https://{domain_name}/static/banner/aboutai/{sport}_about_linebot.png?timestamp={g.timestamp}'
    #獲利
    aboutlinebot_Flex['body']['contents'][1]['contents'][0]['contents'][1]['text'] = str(profit)
    #獲勝場數
    aboutlinebot_Flex['body']['contents'][1]['contents'][2]['contents'][0]['contents'][1]['text'] = wingame
    #準確度
    aboutlinebot_Flex['body']['contents'][1]['contents'][2]['contents'][2]['contents'][1]['text'] = accuracy
    #season
    aboutlinebot_Flex['body']['contents'][1]['contents'][2]['contents'][4]['contents'][1]['text'] = f'{count_earn}天'
    #總績效圖
    aboutlinebot_Flex['body']['contents'][2]['contents'][0]['url'] = f'https://{domain_name}/static/Profit/{sport}_profit.png?timestamp={g.timestamp}'
    #近期績效圖
    aboutlinebot_Flex['body']['contents'][3]['contents'][0]['url'] = f'https://{domain_name}/static/Profit/{sport}_performance_graph.png?timestamp={g.timestamp}'
    return aboutlinebot_Flex

#機器人績效圖
def performance_graph(PredictResults,sport):
    df_mon = PredictResults.copy()
    df_mon.index = PredictResults.index.strftime("%Y-%m-%d")
    df_g = df_mon.groupby("MatchTime").sum()
    df_g.index = pd.to_datetime(pd.to_datetime(df_g.index).strftime('%Y-%m-%d'))
    money_count = []
    win_all = []
    money = 0
    for i in range(len(df_g)):
        money += df_g['Profit'][i]
        money_count.append(money)
    df_g["累計獲利"] = money_count
    show_max = int(round(df_g["累計獲利"].max(),0))
    show_min = int(round(df_g["累計獲利"].min(),0))
    o_max = df_g[df_g["累計獲利"] ==df_g["累計獲利"].max()]
    o_min = df_g[df_g["累計獲利"] ==df_g["累計獲利"].min()]
    o_last = df_g[-1:]
    index = pd.date_range(df_g.index.min(), df_g.index.max())
    show_last = str(float(round(o_last["累計獲利"] /10000,1))) + "萬元"
    data = df_g['累計獲利']

    df = pd.DataFrame(data, index=index)
    df['累計獲利'] = df['累計獲利'].fillna(method='pad')
    x = df.index
    y = df['累計獲利']

    # workaround by creating linespace for length of your x axis
    x_new = np.linspace(0, len(df_g.index))
    a_BSpline = make_interp_spline(
        [i for i in range(0, len(df_g.index))],
        df_g['累計獲利'],
        k=3,
    )
    y_new = a_BSpline(x_new)

    # plot this new plot with linestyle = "-"
    x = list(x.astype(str))
    t = pd.date_range(start=df_g.iloc[0].name.strftime("%Y-%m-%d"),
                      end=df_g.iloc[-1].name.strftime("%Y-%m-%d"),
                      periods=len(df_g))
    X_Y_Spline = make_interp_spline(df_g.index,df_g["累計獲利"])

    # Returns evenly spaced numbers
    # over a specified interval.
    X_ = np.linspace(t.min().value, t.max().value,100)
    Y_ = X_Y_Spline(X_)
    time_list = []
    time_ = np.linspace(t.min().value, t.max().value,300)
    for ti in time_:
        ti = '{:f}'.format(ti)
        time_stamp = int(str(ti)[:10]) # 設定timeStamp
        struct_time = time.localtime(time_stamp) # 轉成時
        timeString = datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", struct_time),"%Y-%m-%d %H:%M:%S") # 轉成字串
        time_list.append(timeString)
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
    plt.rcParams['axes.unicode_minus'] = False
    # 開新一個畫布 
    fig = plt.figure(figsize=(25,10)) # 寬10 長8
    gs = GridSpec(1, 1) # 設立1x1的網格
    # 設定網格及子圖
    ax = plt.subplot(gs[0, 0],facecolor='#FFFAFA') # 子圖ax在網格的[0, 0]
    X_Y_Spline = make_interp_spline(df_g.index,df_g["累計獲利"])

    # Returns evenly spaced numbers
    # over a specified interval.
    X_ = np.linspace(t.min().value, t.max().value,300)
    Y_ = X_Y_Spline(X_)

    ax.plot(time_list, Y_,'r',linewidth = 10)
    plt.xticks(fontsize=55,fontweight = "bold")
    range_p = Y_.max() / 3
    plt.yticks(range(0,int(Y_.max())+1,int(range_p)),fontsize=55,fontweight = "bold",labels=['$0',f'${str(round(int(range_p*1)/10000,1))}萬',f'${str(round(int(range_p*2)/10000,1))}萬',f'${str(round(int(range_p*3)/10000,1))}萬'])

    plt.fill_between(time_list,0, Y_, facecolor='#F08080',alpha=0.3)

    plt.title("獲利績效",fontsize=80,fontweight = "bold")
    #plt.annotate(show_max,xy=(o_max.index[0],int(o_max["累計獲利"].iloc[0])),xytext = (o_max.index[0]- timedelta(days = 10),int(o_max["累計獲利"].iloc[0])+5500),fontsize=60,color = '#FF4500', weight='bold')
    #plt.annotate(show_min,xy=(o_min.index[0],int(o_min["累計獲利"].iloc[0])),xytext = (o_min.index[0]- timedelta(days = -1),int(o_min["累計獲利"].iloc[0])-5000),fontsize=40,color = '#008B00', weight='bold')
    if int(o_last["累計獲利"].iloc[0]) > Y_[-5:].mean():
        last = int(o_last["累計獲利"].iloc[0]) * 1.04
    else:
        last = int(o_last["累計獲利"].iloc[0]) * 0.8
    plt.annotate(show_last,xy=(o_last.index[0],int(o_last["累計獲利"].iloc[0])),xytext = (o_last.index[0] - timedelta(days = len(df_g["累計獲利"])*0.07),last),fontsize=60,color = '#FF7F24', weight='bold')
    plt.grid()
    plt.margins(x=0,y=0)
    # 圖調整
    ty_values = [0,10000]
    if len(df_g) < 30:
        tick_spacing = len(df_g)*0.25 # x軸密集度
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    else:
        tick_spacing = len(X_)/12 # x軸密集度
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    plt.savefig(f'static/Profit/{sport}_performance_graph.png',bbox_inches='tight',dpi=fig.dpi,pad_inches=0.2)
    plt.close(fig)
    
#訂閱EMAIL
def subscribe_email():
    subscribeemail_Flex = json.load(open('static/subscribe_email.json', 'r', encoding='utf-8'))
    #email訂閱圖
    subscribeemail_Flex['contents'][0]['hero']['url'] = f'https://{domain_name}/static/email/mail_linebot-01.png'
    subscribeemail_Flex['contents'][0]['hero']['action']['uri'] = 'https://liff.line.me/1657119443-MgX9BxBA'
    #email訂閱好康1
    subscribeemail_Flex['contents'][1]['hero']['url'] = f'https://{domain_name}/static/email/mail_linebot-02.png'
    subscribeemail_Flex['contents'][1]['hero']['action']['uri'] = 'https://liff.line.me/1657119443-MgX9BxBA'
    #email訂閱好康2
    subscribeemail_Flex['contents'][2]['hero']['url'] = f'https://{domain_name}/static/email/mail_linebot-03.png'
    subscribeemail_Flex['contents'][2]['hero']['action']['uri'] = 'https://liff.line.me/1657119443-MgX9BxBA'
    #email訂閱好康3
    subscribeemail_Flex['contents'][3]['hero']['url'] = f'https://{domain_name}/static/email/mail_linebot-04.png'
    subscribeemail_Flex['contents'][3]['hero']['action']['uri'] = 'https://liff.line.me/1657119443-MgX9BxBA'
    return subscribeemail_Flex

#兌換商城確認兌換的Flexmessage
def exchangecheck(merchandise,price,GPlus,orderId):
    exchangecheck_Flex = json.load(open('static/exchange_check.json', 'r', encoding='utf-8'))
    #商品名稱
    exchangecheck_Flex['body']['contents'][1]['text'] = merchandise
    #商品原價
    exchangecheck_Flex['body']['contents'][2]['text'] = '原售價${}'.format(price)
    #商品GPlus幣
    exchangecheck_Flex['body']['contents'][4]['contents'][0]['contents'][1]['text'] = str(GPlus)
    #兌換日期
    date = datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y.%m.%d')
    exchangecheck_Flex['body']['contents'][4]['contents'][1]['contents'][1]['text'] = date
    #確認
    exchangecheck_Flex['body']['contents'][5]['contents'][0]['action']['data'] = '@exchange={}|{}'.format(merchandise,orderId)
    return exchangecheck_Flex

#兌換商品的訂單狀況
def merchandise_status(userid,orderId):
        SQL ='''
            SELECT top 1 a.*,b.id as OrderId,b.*
                FROM [dbo].[GPlusStore] AS A
                FULL OUTER JOIN GPlusStore_buyer as b on a.id = b.merchandise_id
                where b.id = '{}'
                order by CreatedTime desc
        '''.format(orderId)
        result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
        Delivery_Flex = json.load(open('static/Delivery.json', 'r', encoding='utf-8'))
        print(result['image'].iloc[0])
        #商品照片
        Delivery_Flex['header']['contents'][0]['contents'][0]['contents'][0]['url'] = result['image'].iloc[0]
        #寄件編號
        Delivery_Flex['header']['contents'][0]['contents'][1]['contents'][0]['text'] = '寄件編號: {}'.format(orderId)
        #商品名稱
        Delivery_Flex['header']['contents'][0]['contents'][1]['contents'][1]['text'] = result['merchandise'].iloc[0]
        #商品狀況
        '''
        0 : 兌換尚未確認
        1 : 兌換成功，但未填寫寄送資訊
        2 : 兌換成功，且以填寫寄送資訊，等待送貨
        3 : 貨已寄出
        4 : 會員按下「確認訂單」完成全部訂單流程
        5 : 兌換成功，但未在期限內填寫寄送資訊
        '''
        delivery_status = result['Delivery_Status'].iloc[0]
        if delivery_status == 1:
            object_ = 1
        elif delivery_status in [2,5]:
            object_ = 3
        elif delivery_status == 3:
            object_ = 5
        elif delivery_status == 4:
            object_ = 7
        for i in range(0,object_):
            Delivery_status_Flex = json.load(open('static/Delivery_status.json', 'r', encoding='utf-8'))
            if i == 0:
                #已成功兌換商品
                Delivery_status_Flex['contents'][0]['text'] = result['CreatedTime'].iloc[0]
                if delivery_status == 1:
                    Delivery_status_Flex['contents'][0]['color'] = '#000000'
                    Delivery_status_Flex['contents'][2]['color'] = '#FA8072'
                    Delivery_status_Flex['contents'][1]['contents'][1]['borderColor'] = '#FA8072'
                    Delivery_status_Flex['contents'][2]['weight'] = 'bold'  
                else:
                    Delivery_status_Flex['contents'][0]['color'] = '#55555595'
                    Delivery_status_Flex['contents'][2]['color'] = '#55555595'
                    Delivery_status_Flex['contents'][1]['contents'][1]['borderColor'] = '#55555595'
                    Delivery_status_Flex['contents'][2]['weight'] = 'regular'
                exchangedate = result['ExchangeDate'].iloc[0].strftime("%Y/%m/%d %H:%M")
                Delivery_status_Flex['contents'][0]['contents'][0]['text'] = exchangedate
                Delivery_status_Flex['contents'][2]['text'] = '已成功兌換商品'
            elif i == 2:
                if delivery_status in [2,5]:
                    Delivery_status_Flex['contents'][0]['color'] = '#000000'
                    Delivery_status_Flex['contents'][2]['color'] = '#FA8072'
                    Delivery_status_Flex['contents'][1]['contents'][1]['borderColor'] = '#FA8072'
                    Delivery_status_Flex['contents'][2]['weight'] = 'bold'
                else:
                    Delivery_status_Flex['contents'][0]['color'] = '#55555595'
                    Delivery_status_Flex['contents'][2]['color'] = '#55555595'
                    Delivery_status_Flex['contents'][1]['contents'][1]['borderColor'] = '#55555595'
                    Delivery_status_Flex['contents'][2]['weight'] = 'regular'
                    Delivery_status_Flex['contents'][2]['weight'] = 'regular'
                
                if delivery_status == 5:
                    Delivery_status_Flex['contents'][2]['text'] = '無效訂單'
                    Canceldate = result['CancelDate'].iloc[0].strftime("%Y/%m/%d %H:%M")
                    Delivery_status_Flex['contents'][0]['contents'][0]['text'] = Canceldate
                else:
                    Delivery_status_Flex['contents'][2]['text'] = '已填寫寄送資料'
                    formdate = result['FormDate'].iloc[0].strftime("%Y/%m/%d %H:%M")
                    Delivery_status_Flex['contents'][0]['contents'][0]['text'] = formdate
            elif i == 4:
                if delivery_status == 3:
                    Delivery_status_Flex['contents'][0]['color'] = '#000000'
                    Delivery_status_Flex['contents'][2]['color'] = '#FA8072'
                    Delivery_status_Flex['contents'][1]['contents'][1]['borderColor'] = '#FA8072'
                    Delivery_status_Flex['contents'][2]['weight'] = 'bold'
                else:
                    Delivery_status_Flex['contents'][0]['color'] = '#55555595'
                    Delivery_status_Flex['contents'][2]['color'] = '#55555595'
                    Delivery_status_Flex['contents'][1]['contents'][1]['borderColor'] = '#55555595'
                    Delivery_status_Flex['contents'][2]['weight'] = 'regular'
                deliverydate = result['DeliveryDate'].iloc[0].strftime("%Y/%m/%d %H:%M")
                Delivery_status_Flex['contents'][0]['contents'][0]['text'] = deliverydate
                Delivery_status_Flex['contents'][2]['text'] = '商品已寄出'
            elif i == 6:
                if delivery_status == 4:
                    Delivery_status_Flex['contents'][0]['color'] = '#000000'
                    Delivery_status_Flex['contents'][2]['color'] = '#FA8072'
                    Delivery_status_Flex['contents'][1]['contents'][1]['borderColor'] = '#FA8072'
                    Delivery_status_Flex['contents'][2]['weight'] = 'bold'
                else:
                    Delivery_status_Flex['contents'][0]['color'] = '#55555595'
                    Delivery_status_Flex['contents'][2]['color'] = '#55555595'
                    Delivery_status_Flex['contents'][1]['contents'][1]['borderColor'] = '#55555595'
                    Delivery_status_Flex['contents'][2]['weight'] = 'regular'
                completedate = result['CompleteDate'].iloc[0].strftime("%Y/%m/%d %H:%M")
                Delivery_status_Flex['contents'][0]['contents'][0]['text'] = completedate    
                Delivery_status_Flex['contents'][2]['text'] = '訂單已完成'
            elif i in [1,3,5]:
                Delivery_status_Flex = json.load(open('static/Delivery_line.json', 'r', encoding='utf-8'))

            Delivery_Flex['body']['contents'].insert( 1, Delivery_status_Flex)
        #按鈕
        if object_ == 1:
            Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['label'] = '填寫寄送資料'
        else:
            Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['label'] = '完成訂單'
        #跳轉寄送資訊的liff
        if delivery_status == 1:
            Delivery_Flex['body']['contents'][-2]['contents'][0]['text'] = '恭喜您兌換成功，請於7天內填寫寄送相關資訊，否則將視為無效兌換'
            Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['type'] = 'uri'
            Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['uri'] = 'https://liff.line.me/1657119443-26AdkxkG?orderId={}'.format(orderId)  
            Delivery_Flex['body']['contents'][-1]['backgroundColor'] = '#1E90FF'
        elif delivery_status == 2:
            Delivery_Flex['body']['contents'][-2]['contents'][0]['text'] = '已收到您的寄送資訊，本公司將於7~14天為您寄送商品'
            Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['type'] = 'message'
            del Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['uri']
            Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['text'] = '商品尚未送出，無法完成訂單'
            Delivery_Flex['body']['contents'][-1]['backgroundColor'] = '#55555595'
        elif delivery_status == 3:
            Delivery_Flex['body']['contents'][-2]['contents'][0]['text'] = '已將商品寄出，如商品無誤請按下「完成訂單」，如有問題請洽客服'
            Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['type'] = 'postback'
            del Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['uri']
            Delivery_Flex['body']['contents'][-1]['contents'][0]['action']['data'] = '@完成訂單={}'.format(orderId)
            Delivery_Flex['body']['contents'][-1]['backgroundColor'] = '#1E90FF'
        elif delivery_status in [4,5]:
            del Delivery_Flex['body']['contents'][-2]
            del Delivery_Flex['body']['contents'][-1]
        return Delivery_Flex

#訂單編號查詢
def search_orderId(userId):
    SQL = """
        SELECT * FROM GPlusStore_buyer
        where UserId = '{}'
        order by CreatedTime desc
    """.format(userId)
    result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
    delivering = list(result[(result['Delivery_Status'] ==1) | (result['Delivery_Status'] ==2) | (result['Delivery_Status'] ==3)]['Id'][:5].values)
    successful = list(result[result['Delivery_Status'] == 4]['Id'][:5].values)
    cancel = list(result[result['Delivery_Status'] == 5]['Id'][:5].values)
    return delivering,successful,cancel
                    
#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7000))
    app.run(host='0.0.0.0', port=port)
