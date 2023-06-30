#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, make_response,g
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote

import json
import time
import traceback
import pandas as pd
import pyodbc
import requests
import web_config

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.before_request
def before_request():
    auth = HTTPBasicAuth()
    '''
    _server_gamania = web_config.testing().server  # No TCP
    _database_gamania = web_config.testing().database
    _uid_gamania = web_config.testing().username
    _pwd_gamania = web_config.testing().password
    _port = "1433"
    
    '''
    _server_gamania = 'guess365.database.windows.net'  # No TCP
    _database_gamania = 'Guess365' 
    _uid_gamania = 'crawl'
    _pwd_gamania = '@Guess365123!'
    _port = "1433"
    
    g.conn_Guess365 = pyodbc.connect('DRIVER={SQL Server};SERVER='+_server_gamania+';Port='+_port+';DATABASE='+_database_gamania+';UID='+_uid_gamania+';PWD='+_pwd_gamania)  # for MSSQL
    g.cursor = g.conn_Guess365.cursor()

users = [
    {'username': 'rick', 'password': generate_password_hash('123rick456'), 'password_2': '123rick456'}
]
@auth.verify_password
def verify_password(username, password):
    for user in users:
        if user['username'] == username:
            if check_password_hash(user['password'], password):
                return True
    return False

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/MatchEntryInfo/DateBetween/All/<DateBetween>', methods=['GET'])
@app.route('/MatchEntryInfo/DateBetween/<TournamentText>/<DateBetween>', methods=['GET'])
@app.route('/MatchEntryInfo/<EventCode>', methods=['GET'])
@auth.login_required
def getMatchEntryInfo(DateBetween=None,TournamentText = None, SourceCode = None ,EventCode = None):
    
    def find_odds(MatchEntry_df,MatchEntry):
        if MatchEntry_df[MatchEntry_df.EventCode == MatchEntry['EventCode']].loc[:,['GroupOptionCode','OptionCode','OptionRate','SpecialBetValue','Type_cname']].to_dict('records')[0]['GroupOptionCode']==None:
             odds = []
        else:
            odds = MatchEntry_df[MatchEntry_df["EventCode"] == MatchEntry['EventCode']].loc[:,['GroupOptionCode','OptionCode','OptionRate','SpecialBetValue','Type_cname']].to_dict('records')
        return odds
            
    try:
        if request.method == 'GET' and EventCode:
            SQL = """
            Select a.SportCode,a.EventCode,a.TournamentText,a.MatchTime,a.SourceCode,a.HomeTeam,c.name as Home,a.AwayTeam,d.name as Away,a.CollectedTime,GroupOptionCode,OptionCode,OptionRate,SpecialBetValue,e.Type_cname
                from MatchEntry  as a
                left join Odds  as b on a.EventCode = b.EventCode 
                inner join teams as c on a.HomeTeam = c.team
                inner join teams as d on a.AwayTeam = d.team
                inner join GroupOptionCode as e on a.SportCode = e.SportCode and b.GroupOptionCode = e.GroupOptionCode1
                where a.EventCode = '{}' and a.MatchTime >= '{}' 
            """.format(EventCode,datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
            MatchEntry_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
            # 整理賽事
            MatchEntrysOutput = []
            records = []
            
            for MatchEntry in MatchEntry_df['EventCode'].unique():
                MatchEntrysOutput.append(dict(EventCode=MatchEntry['EventCode'],
                                                TournamentText=MatchEntry['TournamentText'],
                                                MatchTime=MatchEntry['MatchTime'].strftime('%Y-%m-%d %H:%M:%S.000'),
                                                SportCode=MatchEntry['SportCode'],
                                                SourceCode=MatchEntry['SourceCode'],
                                                HomeTeam=[MatchEntry['HomeTeam'],MatchEntry['Home']],
                                                AwayTeam=[MatchEntry['AwayTeam'],MatchEntry['Away']],
                                                odds= find_odds(MatchEntry_df,MatchEntry),
                                                type_cname = MatchEntry['Type_cname'],
                                                CollectedTime=MatchEntry['CollectedTime'].strftime('%Y-%m-%d %H:%M:%S.000')))
                records.append(MatchEntry['EventCode'])
            return jsonify({'response': MatchEntrysOutput})
        elif request.method == 'GET' and DateBetween and TournamentText is None:
            if DateBetween == 'any':
                DatetimeTop, DatetimeBottom = datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),(datetime.now().astimezone(timezone(timedelta(hours=8)))+timedelta(days=7)).replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S.000')
            else:
                DatetimeTop, DatetimeBottom = datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),DateBetween.split('~')[1].strip()+' 23:59:59.000'
            # 查詢賽事
            SQL = """
                Select a.SportCode,a.EventCode,a.TournamentText,a.MatchTime,a.SourceCode,a.HomeTeam,c.name as Home,a.AwayTeam,d.name as Away,a.CollectedTime,GroupOptionCode,OptionCode,OptionRate,SpecialBetValue,e.Type_cname
                    from MatchEntry  as a
                    left join Odds  as b on a.EventCode = b.EventCode 
                    full outer join teams as c on a.HomeTeam = c.team
                    full outer join teams as d on a.AwayTeam = d.team
                    inner join GroupOptionCode as e on a.SportCode = e.SportCode and b.GroupOptionCode = e.GroupOptionCode1
                    where Matchtime >= '{}' and  Matchtime <= '{}'
                    order by Matchtime,HomeTeam,AwayTeam,a.SourceCode desc 
                """.format(DatetimeTop,DatetimeBottom)
            MatchEntry_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)  

            # 整理賽事
            MatchEntrysOutput = []
            records = []
 
            column_names = ["EventCode"]
            MatchEntry_unique = MatchEntry_df.drop_duplicates(subset=column_names,keep="first")
            
            for Match in range(len(MatchEntry_unique)):
                MatchEntry = MatchEntry_unique.iloc[Match]
                MatchEntrysOutput.append(dict(EventCode=MatchEntry['EventCode'],
                                                TournamentText=MatchEntry['TournamentText'],
                                                MatchTime=MatchEntry['MatchTime'].strftime('%Y-%m-%d %H:%M:%S.000'),
                                                SportCode=MatchEntry['SportCode'],
                                                SourceCode=MatchEntry['SourceCode'],
                                                HomeTeam=[MatchEntry['HomeTeam'],MatchEntry['Home']],
                                                AwayTeam=[MatchEntry['AwayTeam'],MatchEntry['Away']],
                                                odds= find_odds(MatchEntry_df,MatchEntry),
                                                type_cname = MatchEntry['Type_cname'],
                                                CollectedTime=MatchEntry['CollectedTime'].strftime('%Y-%m-%d %H:%M:%S.000')))
                records.append(MatchEntry['EventCode'])
            return jsonify({'response': MatchEntrysOutput})
        elif request.method == 'GET' and TournamentText:
            if DateBetween == 'any':
                DatetimeTop, DatetimeBottom = datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), (datetime.now().astimezone(timezone(timedelta(hours=8))) + timedelta(days=7)).replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S.000')
            else:
                DatetimeTop, DatetimeBottom = datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),DateBetween.split('~')[1].strip()+' 23:59:59.000'
            # 查詢賽事
            SQL = """
            Select a.SportCode,a.EventCode,a.TournamentText,a.MatchTime,a.SourceCode,a.HomeTeam,c.name as Home,a.AwayTeam,d.name as Away,a.CollectedTime,GroupOptionCode,OptionCode,OptionRate,SpecialBetValue,e.Type_cname
                from MatchEntry  as a
                left join Odds  as b on a.EventCode = b.EventCode 
                full outer join teams as c on a.HomeTeam = c.team
                full outer join teams as d on a.AwayTeam = d.team
                inner join GroupOptionCode as e on a.SportCode = e.SportCode and b.GroupOptionCode = e.GroupOptionCode1
                where Matchtime >= '{}' and  Matchtime <= '{}' and TournamentText = '{}'
                order by Matchtime,HomeTeam,AwayTeam,a.SourceCode desc
            """.format(DatetimeTop,DatetimeBottom,TournamentText)
            MatchEntry_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
            # 整理賽事
            MatchEntrysOutput = []
            records = []
            
            column_names = ["EventCode"]
            MatchEntry_unique = MatchEntry_df.drop_duplicates(subset=column_names,keep="first")
            
            for Match in range(len(MatchEntry_unique)):
                MatchEntry = MatchEntry_unique.iloc[Match]
                MatchEntrysOutput.append(dict(EventCode=MatchEntry['EventCode'],
                                                TournamentText=MatchEntry['TournamentText'],
                                                MatchTime=MatchEntry['MatchTime'].strftime('%Y-%m-%d %H:%M:%S.000'),
                                                SportCode=MatchEntry['SportCode'],
                                                SourceCode=MatchEntry['SourceCode'],
                                                HomeTeam=[MatchEntry['HomeTeam'],MatchEntry['Home']],
                                                AwayTeam=[MatchEntry['AwayTeam'],MatchEntry['Away']],
                                                odds= find_odds(MatchEntry_df,MatchEntry),
                                                type_cname = MatchEntry['Type_cname'],
                                                CollectedTime=MatchEntry['CollectedTime'].strftime('%Y-%m-%d %H:%M:%S.000')))
                records.append(MatchEntry['EventCode'])
            return jsonify({'response': MatchEntrysOutput})
    except:
        return jsonify({'response': [{'Error Info': traceback.format_exc()}]})

@app.route('/PredictResults/<accounts>/<DateBetween>', methods=['GET'])
@app.route('/PredictResults/<accounts>/', methods=['GET'])
@auth.login_required
def get_PredictResults(accounts=None,DateBetween=None,sport=None):
    try:
        if DateBetween==None:
            DatetimeTop, DatetimeBottom = (datetime.now().astimezone(timezone(timedelta(hours=8))) - timedelta(days=1)).replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S.000'), (datetime.now().astimezone(timezone(timedelta(hours=8))) - timedelta(
            days=1)).replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S.000')
        else:
            DatetimeTop, DatetimeBottom = DateBetween.split('~')[0].strip() + ' 00:00:00.000', DateBetween.split('~')[1].strip() + ' 23:59:59.000'



        accounts = accounts.split(',')
        SQL = '''SELECT c.SportCode, d.member, a.EventCode, c.HomeTeam,e.HomeScore, c.AwayTeam,e.AwayScore, a.TournamentText, a.GroupOptionCode, a.PredictTeam, a.OptionCode, c.MatchTime, b.Results 
                    FROM [dbo].[PredictMatch] as a
                    inner join PredictResults as b on a.id=b.Predict_id
                    inner join MatchEntry as c on c.EventCode=a.EventCode
                    inner join UserMember  as d on d.UserId=a.UserId
                    inner join MatchResults as e on a.EventCode = e.EventCode
                    where c.MatchTime>='{}' and c.MatchTime<'{}'
                    and d.member in ({}) and gameType='Selling'
                    order by a.TournamentText,  d.member 
                '''.format(DatetimeTop,DatetimeBottom,str(accounts).replace('[','').replace(']',''))
        PredictResults = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True) 
        if len(PredictResults)>0:
            TournamentTexts = list(set(PredictResults['TournamentText']))
            Times = sorted(list(set(PredictResults['MatchTime'])))
            MatchTimes = pd.to_datetime(Times,format='%Y-%m-%d').strftime("%Y-%m-%d").unique()
            team_info = TeamNameCorrection()
            all_message = []
            all_typecname = get_TypeCname()
            for MatchTime in MatchTimes:
                alliance = []
                for TournamentText in TournamentTexts:
                    message_1x2 = {
                        "type":'全場獲勝'
                    } 
                    message_1x2_one = ''
                    message_handicap = {
                        "type":'全場讓分'
                    }
                    message_handicap_one = ''
                    message_total = {
                        "type":'全場大小'
                    }
                    message_total_one = ''
                    for P in range(len(PredictResults)):
                        matchtime_one = PredictResults['MatchTime'].iloc[P].strftime('%Y-%m-%d')
                        if PredictResults['TournamentText'].iloc[P] == TournamentText and matchtime_one == MatchTime:
                            sport_type = all_typecname[(all_typecname['SportCode'] == int(PredictResults['SportCode'].iloc[P])) & (all_typecname['GroupOptionCode1'] == int(PredictResults['GroupOptionCode'].iloc[P]))]['Type_cname'].iloc[0]
                            HomeTeam, AwayTeam = team_info[team_info['team'] == PredictResults['HomeTeam'].iloc[P]]['name'].iloc[0], team_info[team_info['team'] == PredictResults['AwayTeam'].iloc[P]]['name'].iloc[0]
                            homeScore = PredictResults['HomeScore'].iloc[P]
                            awayScore = PredictResults['AwayScore'].iloc[P]
                            if PredictResults['Results'].iloc[P]=='Y':
                                game_result = '✔️' 
                            elif PredictResults['Results'].iloc[P]=='N':
                                game_result = '❌'
                            else:
                                game_result = '❕'
                            if sport_type == '全場獲勝':
                                message_1x2_one+=f"{game_result}"                                                 f"|{HomeTeam}|{homeScore} : {awayScore}|{AwayTeam}"                                                 f"|{Mapping_OptionCode(PredictResults['OptionCode'].iloc[P],PredictResults['SportCode'].iloc[P],PredictResults['GroupOptionCode'].iloc[P],HomeTeam,AwayTeam)}\n"
                                                    
                            elif sprot_type == '全場讓分':
                                message_handicap_one+=f"{game_result}"                                                      f"|{HomeTeam}|{homeScore} : {awayScore}|{AwayTeam}"                                                      f"|{Mapping_OptionCode(PredictResults['OptionCode'].iloc[P],PredictResults['SportCode'].iloc[P],PredictResults['GroupOptionCode'].iloc[P],HomeTeam,AwayTeam)}\n"
                            elif sprot_type == '全場大小':
                                message_total_one+=f"{game_result}"                                                   f"|{HomeTeam}|{homeScore} : {awayScore}|{AwayTeam}"                                                   f"|{Mapping_OptionCode(PredictResults['OptionCode'].iloc[P],PredictResults['SportCode'].iloc[P],PredictResults['GroupOptionCode'].iloc[P],HomeTeam,AwayTeam)}\n" 

                    message_1x2["game"] = message_1x2_one
                    message_handicap["game"] = message_handicap_one
                    message_total["game"] = message_total_one
                    message_one ={
                        "sport":'👏'+TournamentText,
                        "predictresult" : [message_1x2,message_handicap,message_total]
                            }
                    alliance.append(message_one)
                game_one_message = {
                    "date" : f"開賽日期 : {MatchTime[5:]}",
                    "alliance" :alliance
                }
                all_message.append(game_one_message)
        return jsonify({'responese': all_message })
    except:
        return jsonify({'response':traceback.format_exc()})
    


@app.route('/PredictMatchEntrys/', methods=['POST'])
@auth.login_required
def PredictMatchEntrys():
    try:
        err_msg = ""
        messages = "" 
        # 取得驗證資料
        auth_username = auth.username()
        client_ip = request.remote_addr
        GameType = ['Forecast', 'Selling','OnlyPush']
        data = request.get_json()
        team_info = TeamNameCorrection()
        all_typecname = get_TypeCname()
        # 取得預測列表
        for idx, pred in enumerate(data['predlist']):
            try:
                # 取得每一項預測
                account = pred['account']
                password = pred['password']
                GroupOptionCode = pred['GroupOptionCode']
                OptionCode = pred['OptionCode']
                EventCode = pred['EventCode']
                predict_type = pred['predict_type']
                input_HomeOdds = pred['HomeOdds']
                input_AwayOdds = pred['AwayOdds']
                HomeConfidence = pred['HomeConfidence']
                AwayConfidence = pred['AwayConfidence']
                main = pred['main']
                if GroupOptionCode == 10:
                    input_TieOdds = pred['TieOdds']
                    TieConfidence = pred['TieConfidence']
                    message = f"{datetime.now().astimezone(timezone(timedelta(hours=8)))}[%s]\n"                       "{'MatchTime':'%s',"                       " 'Odds':['%s','%s','%s'],"                       " 'Confidence':['%s','%s','%s'],"                       " 'TournamentText':'%s',"                       " 'HomeTeam':'%s',"                       " 'AwayTeam':'%s',"                       " 'GroupOptionCode':'%s',"                       " 'GroupOptionName':'%s',"                       " 'OptionCode':'%s',"                       " 'Main':'%s'}\n"
                else:
                    message = f"{datetime.now().astimezone(timezone(timedelta(hours=8)))}[%s]\n"                       "{'MatchTime':'%s',"                       " 'Odds':['%s','%s'],"                       " 'Confidence':['%s','%s'],"                       " 'TournamentText':'%s',"                       " 'HomeTeam':'%s',"                       " 'AwayTeam':'%s',"                       " 'GroupOptionCode':'%s',"                       " 'GroupOptionName':'%s',"                       " 'OptionCode':'%s',"                       " 'Main':'%s'}\n"
                    
                start = time.process_time()
                #檢查盤口是否存在
                SQL = """
                    select * from MatchEntry where EventCode = '{}' 
                """.format(EventCode)
                results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
                MatchEntry = results_df.iloc[0]
                
                SQL = """
                    select * from Odds where EventCode = '{}' and GroupOptionCode='{}' and OptionCode='{}' 
                """.format(EventCode,GroupOptionCode,OptionCode)
                results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
                Odds = results_df.iloc[0]
                UserId = get_UserId(account,password)
                level = get_UserMemberLevel(UserId)
                end = time.process_time()

                # 檢查 帳號密碼是否存在
                if UserId is None:
                    err_msg += f'data[{idx}] Account {account} does not exist. data=({pred})\n'
                    continue
                # 檢查 predict_type是否為指定值
                if predict_type is None or predict_type not in GameType:
                    err_msg += f"data[{idx}] Predict type please enter 'Forecast' or 'Selling' or 'OnlyPush' option. data=({pred})\n"
                    continue
                # 預測
                if predict_type == 'Selling':
                    if int(level) not in (1, 2, 3, 6):
                        err_msg += f'data[{idx}] Account {account} non-selling member. data=({pred})\n'
                        continue
                        
                    HomeTeam, AwayTeam = team_info[team_info['team'] == MatchEntry['HomeTeam']]['name'].iloc[0], team_info[team_info['team'] == MatchEntry['AwayTeam']]['name'].iloc[0]
                    if GroupOptionCode == 10:
                        m = message%(idx,
                                     MatchEntry['MatchTime'].strftime('%m-%d %H:%M'),
                                     input_HomeOdds,input_AwayOdds,input_TieOdds,
                                     HomeConfidence,AwayConfidence,TieConfidence,
                                     MatchEntry['TournamentText'],
                                     HomeTeam,AwayTeam,
                                     Odds['GroupOptionCode'],
                                     all_typecname[(all_typecname['SportCode'] == int(MatchEntry['SportCode'])) & (all_typecname['GroupOptionCode1'] == int(Odds['GroupOptionCode']))]['Type_cname'].iloc[0],
                                     Mapping_OptionCode(Odds['OptionCode'], MatchEntry['SportCode'],Odds['GroupOptionCode'], HomeTeam, AwayTeam),
                                     main)
                    else:
                        m = message%(idx,
                                     MatchEntry['MatchTime'].strftime('%m-%d %H:%M'),
                                     input_HomeOdds,input_AwayOdds,
                                     HomeConfidence,AwayConfidence,
                                     MatchEntry['TournamentText'],
                                     HomeTeam,AwayTeam,
                                     Odds['GroupOptionCode'],
                                     all_typecname[(all_typecname['SportCode'] == int(MatchEntry['SportCode'])) & (all_typecname['GroupOptionCode1'] == int(Odds['GroupOptionCode']))]['Type_cname'].iloc[0],
                                     Mapping_OptionCode(Odds['OptionCode'], MatchEntry['SportCode'],Odds['GroupOptionCode'], HomeTeam, AwayTeam),
                                     main)

                    messages += m+"------------------\n"
                    isForcast, Forecast_result = isPredictMacthExists(UserId, EventCode, GroupOptionCode, 'Forecast')
                    isSelling, Selling_result = isPredictMacthExists(UserId, EventCode, GroupOptionCode, 'Selling')
                    if not isForcast:
                        
                        for gametype in GameType[0:2]:
                            predict_sql = '''
                                INSERT INTO [PredictMatch] ([UserId],[SportCode],[EventType],[EventCode],[TournamentCode],[TournamentText],[GroupOptionCode],[GroupOptionName],[PredictTeam],[OptionCode],[SpecialBetValue],[OptionRate],[status],[gameType],[MarketType],[PredictDatetime],[CreatedTime]) 
                                VALUES('{}','{}', '0','{}', '{}','{}','{}','{}','{}','{}','{}','{}','2','{}','{}','{}','{}')
                            '''.format(UserId,MatchEntry['SportCode'],MatchEntry['EventCode'],
                                       MatchEntry['SportTournamentCode'],MatchEntry['TournamentText'],Odds['GroupOptionCode'],
                                     get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode']),
                                      Mapping_PredictTeamName(Odds['OptionCode'], MatchEntry['SportCode'], Odds['GroupOptionCode'], MatchEntry['HomeTeam'], MatchEntry['AwayTeam']),
                                      Odds['OptionCode'],Odds['SpecialBetValue'],Odds['OptionRate'],gametype,
                                      "international" if MatchEntry['SourceCode'] == "Bet365" else "sportslottery",
                                      datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                      datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"))
                            cursor = g.conn_Guess365.cursor()
                            cursor.execute(predict_sql)
                            cursor.commit()
                        add_userbouns(UserId)
                        send_JANDIMessage(m, client_ip, auth_username, '[預+賣]')


                    elif isForcast and not isSelling:
                        if Forecast_result['OptionCode'] == Odds['OptionCode']:
                            predict_sql = '''
                                INSERT INTO [dbo].[PredictMatch] ([UserId],[SportCode],[EventType],[EventCode],[TournamentCode],[TournamentText],[GroupOptionCode],[GroupOptionName],[PredictTeam],[OptionCode],[SpecialBetValue],[OptionRate],[status],[gameType],[MarketType],[PredictDatetime],[CreatedTime]) 
                                VALUES('{}','{}', '0','{}', '{}','{}','{}','{}','{}','{}','{}','{}','2','{}','{}','{}','{}') 
                            '''.format(UserId,MatchEntry['SportCode'],MatchEntry['EventCode'],MatchEntry['SportTournamentCode'],
                                      MatchEntry['TournamentText'],Odds['GroupOptionCode'],
                                      get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode']),
                                      Mapping_PredictTeamName(Odds['OptionCode'], MatchEntry['SportCode'], Odds['GroupOptionCode'], MatchEntry['HomeTeam'], MatchEntry['AwayTeam']),
                                      Odds['OptionCode'],Odds['SpecialBetValue'],Odds['OptionRate'],GameType[-2],
                                      "international" if MatchEntry['SourceCode'] == "Bet365" else "sportslottery",
                                       datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                      datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"))
                            cursor = g.conn_Guess365.cursor()
                            cursor.execute(predict_sql)
                            cursor.commit()
                            HomeTeam, AwayTeam = team_info[team_info['team'] == MatchEntry['HomeTeam']]['name'].iloc[0], team_info[team_info['team'] == MatchEntry['AwayTeam']]['name'].iloc[0]
                            if GroupOptionCode == 10:
                                m = message%(idx,
                                             MatchEntry['MatchTime'].strftime('%m-%d %H:%M'),
                                             input_HomeOdds,input_AwayOdds,input_TieOdds,
                                             HomeConfidence,AwayConfidence,TieConfidence,
                                             MatchEntry['TournamentText'],
                                             HomeTeam,AwayTeam,
                                             Odds['GroupOptionCode'],
                                             all_typecname[(all_typecname['SportCode'] == int(MatchEntry['SportCode'])) & (all_typecname['GroupOptionCode1'] == int(Odds['GroupOptionCode']))]['Type_cname'].iloc[0],
                                             Mapping_OptionCode(Odds['OptionCode'], MatchEntry['SportCode'],Odds['GroupOptionCode'], HomeTeam, AwayTeam),
                                             main)
                            else:
                                m = message % (idx,
                                               MatchEntry['MatchTime'].strftime('%m-%d %H:%M'),
                                               input_HomeOdds, input_AwayOdds,
                                               HomeConfidence, AwayConfidence,
                                               MatchEntry['TournamentText'],
                                               HomeTeam, AwayTeam,
                                               Odds['GroupOptionCode'],
                                               all_typecname[(all_typecname['SportCode'] == int(MatchEntry['SportCode'])) & (all_typecname['GroupOptionCode1'] == int(Odds['GroupOptionCode']))]['Type_cname'].iloc[0],
                                               Mapping_OptionCode(Odds['OptionCode'], MatchEntry['SportCode'], Odds['GroupOptionCode'],HomeTeam, AwayTeam),
                                               main)
                            messages += m + "------------------\n"
                            send_JANDIMessage(m, client_ip, auth_username, '[預>賣]')
                        else:
                            err_msg += f'data[{idx}] Forecasts and Sellings must be the same. data=({pred})\n'
                            continue
                    else:
                        err_msg += f'data[{idx}] Have repeated sellings. data=({pred})\n'
                        continue

                elif predict_type == 'Forecast':
                    HomeTeam, AwayTeam = team_info[team_info['team'] == MatchEntry['HomeTeam']]['name'].iloc[0], team_info[team_info['team'] == MatchEntry['AwayTeam']]['name'].iloc[0]
                    if GroupOptionCode == 10:
                        m = message%(idx,
                                     MatchEntry['MatchTime'].strftime('%m-%d %H:%M'),
                                     input_HomeOdds,input_AwayOdds,input_TieOdds,
                                     HomeConfidence,AwayConfidence,TieConfidence,
                                     MatchEntry['TournamentText'],
                                     HomeTeam,AwayTeam,
                                     Odds['GroupOptionCode'],
                                     all_typecname[(all_typecname['SportCode'] == int(MatchEntry['SportCode'])) & (all_typecname['GroupOptionCode1'] == int(Odds['GroupOptionCode']))]['Type_cname'].iloc[0],
                                     Mapping_OptionCode(Odds['OptionCode'], MatchEntry['SportCode'],Odds['GroupOptionCode'], HomeTeam, AwayTeam),
                                     main)
                    else:
                        m = message % (idx,
                                       MatchEntry['MatchTime'].strftime('%m-%d %H:%M'),
                                       input_HomeOdds, input_AwayOdds,
                                       HomeConfidence, AwayConfidence,
                                       MatchEntry['TournamentText'],
                                       HomeTeam, AwayTeam,
                                       Odds['GroupOptionCode'],
                                       all_typecname[(all_typecname['SportCode'] == int(MatchEntry['SportCode'])) & (all_typecname['GroupOptionCode1'] == int(Odds['GroupOptionCode']))]['Type_cname'].iloc[0],
                                       Mapping_OptionCode(Odds['OptionCode'], MatchEntry['SportCode'],Odds['GroupOptionCode'], HomeTeam, AwayTeam),
                                       main)
                    messages += m + "------------------\n"
                    isForcast, Forecast_result = isPredictMacthExists(UserId, EventCode, GroupOptionCode, 'Forecast')
                    if isForcast:
                        err_msg += f'data[{idx}] Have repeated forecasts. data=({pred})\n'
                        continue

                    elif not isForcast:
                        predict_sql = '''
                            INSERT INTO [dbo].[PredictMatch] ([UserId],[SportCode],[EventType],[EventCode],[TournamentCode],[TournamentText],[GroupOptionCode],[GroupOptionName],[PredictTeam],[OptionCode],[SpecialBetValue],[OptionRate],[status],[gameType],[MarketType],[PredictDatetime],[CreatedTime]) 
                            VALUES('{}','{}', '0','{}', '{}','{}','{}','{}','{}','{}','{}','{}','2','{}','{}','{}','{}') 
                        '''.format(UserId,MatchEntry['SportCode'],MatchEntry['EventCode'],MatchEntry['SportTournamentCode'],
                                  MatchEntry['TournamentText'],Odds['GroupOptionCode'],
                                   get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode']),
                                  Mapping_PredictTeamName(Odds['OptionCode'], MatchEntry['SportCode'], Odds['GroupOptionCode'], MatchEntry['HomeTeam'], MatchEntry['AwayTeam']),
                                  Odds['OptionCode'],Odds['SpecialBetValue'],Odds['OptionRate'],GameType[0],
                                  "international" if MatchEntry['SourceCode'] == "Bet365" else "sportslottery",
                                  datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                  datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"))
                        cursor = g.conn_Guess365.cursor()
                        cursor.execute(predict_sql)
                        cursor.commit()
                        add_userbouns(UserId)
                        send_JANDIMessage(m, client_ip, auth_username, '[預]')
                elif predict_type == 'OnlyPush':
                    HomeTeam, AwayTeam = team_info[team_info['team'] == MatchEntry['HomeTeam']]['name'].iloc[0], team_info[team_info['team'] == MatchEntry['AwayTeam']]['name'].iloc[0]
                    if GroupOptionCode == 10:
                        m = message%(idx,
                                     MatchEntry['MatchTime'].strftime('%m-%d %H:%M'),
                                     input_HomeOdds,input_AwayOdds,input_TieOdds,
                                     HomeConfidence,AwayConfidence,TieConfidence,
                                     MatchEntry['TournamentText'],
                                     HomeTeam,AwayTeam,
                                     Odds['GroupOptionCode'],
                                     all_typecname[(all_typecname['SportCode'] == int(MatchEntry['SportCode'])) & (all_typecname['GroupOptionCode1'] == int(Odds['GroupOptionCode']))]['Type_cname'].iloc[0],
                                     Mapping_OptionCode(Odds['OptionCode'], MatchEntry['SportCode'],Odds['GroupOptionCode'], HomeTeam, AwayTeam),
                                     main)
                    else:
                        m = message % (idx,
                                       MatchEntry['MatchTime'].strftime('%m-%d %H:%M'),
                                       input_HomeOdds, input_AwayOdds,
                                       HomeConfidence, AwayConfidence,
                                       MatchEntry['TournamentText'],
                                       HomeTeam, AwayTeam,
                                       Odds['GroupOptionCode'],
                                       all_typecname[(all_typecname['SportCode'] == MatchEntry['SportCode']) & (all_typecname['GroupOptionCode1'] == int(Odds['GroupOptionCode']))]['Type_cname'].iloc[0],
                                       Mapping_OptionCode(Odds['OptionCode'], MatchEntry['SportCode'],Odds['GroupOptionCode'], HomeTeam, AwayTeam),
                                       main)
                    messages += m + "------------------\n"
                    send_JANDIMessage(m, client_ip, auth_username, '[推]')

            except KeyError:
                traceback.print_exc()
                err_msg += f'data[{idx}] JSON data parameter incorrect. data=({pred})\n'
                continue
            except:
                traceback.print_exc()
                err_msg += f"data[{idx}] MatchEntry ({EventCode}) has no GroupOptionCode ({GroupOptionCode}). data=({pred})\n"
                continue
        print(messages)
        if messages != "":
            return jsonify({'PredictSQL': messages+'err_msg:\n'+err_msg})
        else:
            return jsonify({'response':"Prediction failed for all input data.\n"+'err_msg:\n'+err_msg})

    except:
        return jsonify({'response': [{'Error Info': traceback.format_exc()}]})


@app.route('/PredictMatchEntry/', methods=['POST'])
@auth.login_required
def PredictMatchEntry():
    try:
        auth_username = auth.username()
        client_ip = request.remote_addr
        account = request.form.get('account')
        password = request.form.get('password')
        GroupOptionCode = request.form.get('GroupOptionCode')
        OptionCode = request.form.get('OptionCode')
        EventCode = request.form.get('EventCode')
        predict_type = request.form.get('PredictType')
        GameType = ['Forecast','Selling']
        if request.method == 'POST' and not account is None and not password is None                 and not GroupOptionCode is None and not OptionCode is None  and not EventCode is None:
            SQL = """
                select * from MatchEntry 
                where EventCode = '{}' and MatchTime >= '{}' 
            """.format(EventCode,datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
            results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            MatchEntry = results_df.iloc[0]

            SQL = """
                select * from Odds 
                where EventCode = '{}' and GroupOptionCode='{}' and OptionCode='{}'
            """.format(EventCode,GroupOptionCode,OptionCode)
            results_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
            Odds = results_df.iloc[0]
            UserId = get_UserId(account,password)
            level = get_UserMemberLevel(UserId)
            if UserId is None:
                return jsonify({'response':f'Account {account} does not exist.'})
            if predict_type is None or  predict_type not in GameType:
                return jsonify({'response':f"Predict type please enter 'Forecast' or 'Selling' option."})

            if predict_type == 'Selling':
                if int(level) not in (1,2,3,6):
                    return jsonify({'response': f'Account {account} non-selling member.'})

                isForcast,Forecast_result = isPredictMacthExists(UserId,EventCode,GroupOptionCode,'Forecast')
                isSelling,Selling_result = isPredictMacthExists(UserId,EventCode,GroupOptionCode,'Selling')
                if not isForcast:
                    for gametype in GameType:
                        predict_sql = '''
                            INSERT INTO [dbo].[PredictMatch] ([UserId],[SportCode],[EventType],[EventCode],[TournamentCode],[TournamentText],[GroupOptionCode],[GroupOptionName],[PredictTeam],[OptionCode],[SpecialBetValue],[OptionRate],[status],[gameType],[MarketType],[PredictDatetime],[CreatedTime]) 
                            VALUES('{}','{}', '0','{}', '{}','{}','{}','{}','{}','{}','{}','{}','2','{}','{}','{}','{}') 
                        '''.format(UserId,MatchEntry['SportCode'],MatchEntry['EventCode'],MatchEntry['SportTournamentCode'],
                                  MatchEntry['TournamentText'],Odds['GroupOptionCode'],
                                  get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode']),
                                  Mapping_PredictTeamName(Odds['OptionCode'], MatchEntry['SportCode'], Odds['GroupOptionCode'], MatchEntry['HomeTeam'], MatchEntry['AwayTeam']),
                                  Odds['OptionCode'],Odds['SpecialBetValue'],Odds['OptionRate'],gametype,
                                  "international" if MatchEntry['SourceCode'] == "Bet365" else "sportslottery",
                                  datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                  datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"))
                        cursor = g.conn_Guess365.cursor()
                        cursor.execute(predict_sql)
                        cursor.commit()
                    add_userbouns(UserId)
                    message = f"比賽資訊：\n"                               f"EventCode = {EventCode} \n"                               f"TournamentText = {MatchEntry['TournamentText']} \n"                               f"{MatchEntry['HomeTeam']} vs {MatchEntry['AwayTeam']} \n"                               f"預測資訊：\n"                               f"GroupOptionName = {get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode'])} \n"                               f"GroupOptionCode = {Odds['GroupOptionCode']}\n"                               f"OptionCode = {Odds['OptionCode']}\n"                               f"SourceCode = {MatchEntry['SourceCode']}\n"
                    send_JANDIMessage(message, client_ip, auth_username,'[預+賣]')
                    return jsonify({'PredictSQL': message})
                elif isForcast and not isSelling:
                    if Forecast_result['OptionCode']==Odds['OptionCode']:
                        predict_sql = '''
                            INSERT INTO [dbo].[PredictMatch] 
                             ([UserId],[SportCode],[EventType],[EventCode],[TournamentCode],[TournamentText],[GroupOptionCode],[GroupOptionName],[PredictTeam],[OptionCode],[SpecialBetValue],[OptionRate],[status],[gameType],[MarketType],[PredictDatetime],[CreatedTime]) 
                             VALUES('{}','{}', '0','{}', '{}','{}','{}','{}','{}','{}','{}','{}','2','{}','{}','{}','{}') 
                            '''.format(UserId,MatchEntry['SportCode'],MatchEntry['EventCode'],MatchEntry['SportTournamentCode'],
                                       MatchEntry['TournamentText'],Odds['GroupOptionCode'],
                                      get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode']),
                                      Mapping_PredictTeamName(Odds['OptionCode'], MatchEntry['SportCode'], Odds['GroupOptionCode'], MatchEntry['HomeTeam'], MatchEntry['AwayTeam']),
                                       Odds['OptionCode'],Odds['SpecialBetValue'],Odds['OptionRate'],GameType[-1],
                                      "international" if MatchEntry['SourceCode'] == "Bet365" else "sportslottery",
                                       datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                       datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"))
                        cursor = g.conn_Guess365.cursor()
                        cursor.execute(predict_sql)
                        cursor.commit()
                        message = f"比賽資訊：\n"                                   f"EventCode = {EventCode} \n"                                   f"TournamentText = {MatchEntry['TournamentText']} \n"                                   f"{MatchEntry['HomeTeam']} vs {MatchEntry['AwayTeam']} \n"                                   f"預測資訊：\n"                                   f"GroupOptionName = {get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode'])} \n"                                   f"GroupOptionCode = {Odds['GroupOptionCode']}\n"                                   f"OptionCode = {Odds['OptionCode']}\n"                                   f"SourceCode = {MatchEntry['SourceCode']}\n"
                        send_JANDIMessage(message, client_ip, auth_username, '[預>賣]')
                        return jsonify({'PredictSQL': message})
                    else:
                        return jsonify({'response': [{'Error Info': 'Forecasts and Sellings must be the same.'}]})
                else:
                    return jsonify({'response': [{'Error Info': 'Have repeated sellings.'}]})
            elif predict_type == 'Forecast':
                isForcast,Forecast_result = isPredictMacthExists(UserId,EventCode,GroupOptionCode,'Forecast')
                if  isForcast:
                    return jsonify({'response': [{'Error Info': 'Have repeated forecasts.'}]})
                elif not isForcast:
                    predict_sql = '''
                    INSERT INTO [dbo].[PredictMatch] 
                        ([UserId],[SportCode],[EventType],[EventCode],[TournamentCode],
                        [TournamentText],[GroupOptionCode],[GroupOptionName],[PredictTeam],
                        [OptionCode],[SpecialBetValue],[OptionRate],[status],[gameType],[MarketType],
                        [PredictDatetime],[CreatedTime]) 
                    VALUES
                        ('{}','{}', '0','{}','{}','{}','{}','{}','{}','{}','{}','{}','2','{}','{}','{}','{}') 
                        '''.format(UserId,MatchEntry['SportCode'],MatchEntry['EventCode'],MatchEntry['SportTournamentCode'],
                                   MatchEntry['TournamentText'],Odds['GroupOptionCode'],
                                   get_GroupOptionName(MatchEntry['SportCode'],Odds['GroupOptionCode']),
                                  Mapping_PredictTeamName(Odds['OptionCode'],MatchEntry['SportCode'], Odds['GroupOptionCode'], MatchEntry['HomeTeam'], MatchEntry['AwayTeam']),
                                  Odds['OptionCode'],Odds['SpecialBetValue'],Odds['OptionRate'],GameType[0],
                                  "international" if MatchEntry['SourceCode'] == "Bet365" else "sportslottery",
                                  datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"),
                                  datetime.now().astimezone(timezone(timedelta(hours=8))).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000"))
                    cursor = g.conn_Guess365.cursor()
                    cursor.execute(predict_sql)
                    cursor.commit()
                    add_userbouns(UserId)
                    message = f"比賽資訊：\n"                               f"EventCode = {EventCode} \n"                               f"TournamentText = {MatchEntry['TournamentText']} \n"                               f"{MatchEntry['HomeTeam']} vs {MatchEntry['AwayTeam']} \n"                               f"預測資訊：\n"                               f"GroupOptionName = {get_GroupOptionName(MatchEntry['SportCode'], Odds['GroupOptionCode'])} \n"                               f"GroupOptionCode = {Odds['GroupOptionCode']}\n"                               f"OptionCode = {Odds['OptionCode']}\n"                               f"SourceCode = {MatchEntry['SourceCode']}\n"
                    send_JANDIMessage(message, client_ip, auth_username, '[預]')
                    return jsonify({'PredictSQL': message})
        else:
            return jsonify({'response': [{'Error Info': 'JSON data parameter incorrect '}]})
    except Exception as e:
        print(e)
        return jsonify({'response': [{'Error Info': f"MatchEntry ({EventCode}) has no GroupOptionCode ({GroupOptionCode})"}]})

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
        elif OptionCode == 'Over':
            return '大分'
        elif OptionCode == 'Under':
            return '小分'
        elif OptionCode == 'X':
            return '平手'
    return None

def get_GroupOptionName(SportCode, GroupOptionCode):
    SQL = """
        select * from [GroupOptionCode] 
        where SportCode = '{}' and GroupOptionCode1 = '{}'
    """.format(SportCode,GroupOptionCode)
    result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    return result['Type'].iloc[0]

def get_UserId(account,password):
    try:
        SQL = """
            select * from UserMember 
            where member = '{}' and Password = '{}'
        """.format(account,password)
        result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
        return result['UserId'].iloc[0]
    except:
        return None

def get_UserMemberLevel(UserId):
    try:
        SQL = """
            select * from UserMember where UserId = '{}'
        """.format(UserId)
        result = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
        return result['level'].iloc[0]
    except:
        return None

def TeamNameCorrection():
    SQL = f"SELECT * FROM teams"
    TeamName = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    return TeamName

def send_JANDIMessage(text,IP,auth_username,gameType):
    webhook_url = 'https://wh.jandi.com/connect-api/webhook/25729815/70b1717ca561d9964afe8027643c4c65'

    jandi_data = {"body": text,
                  "connectColor": "#e31724",
                  "connectInfo": [
                      {
                          "title": f"有員工做{gameType}囉!!，來源IP={IP}，用戶={auth_username}"
                      }]
                 }
    response = requests.post(webhook_url, data=json.dumps(jandi_data),headers={'Content-type': 'application/json'})
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )



def isPredictMacthExists(UserId,EventCode,GroupOptionCode,gametype):
    SQL = '''SELECT * FROM [PredictMatch] 
        where UserId = '{}' and EventCode = '{}' and GroupOptionCode = '{}' and gameType = '{}' 
    '''.format(UserId,EventCode,GroupOptionCode,gametype)
    results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    if len(results)>0:
        return True,results.iloc[0]
    else:
        return False,[]

def get_TypeCname():
    SQL = '''SELECT [SportCode],[Type],[Type_cname],[Play_Name],[GroupOptionCode1] 
        FROM [dbo].[GroupOptionCode] '''
    result_df = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    return result_df

def add_userbouns(UserId):
    predict_num = 1

    Modify_dd = datetime.now().astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S.000")
    start_dd = datetime.now().astimezone(timezone(timedelta(hours=8))).replace(hour=0, minute=0,second=0,microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000")
    end_dd = datetime.now().astimezone(timezone(timedelta(hours=8))).replace(hour=23, minute=59,second=59,microsecond=0).strftime("%Y-%m-%d %H:%M:%S.000")

    SQL = '''SELECT [UserId],[bonus],[Level],[start_dd],[end_dd],[Modify_dd] 
        FROM [dbo].[UserBonus]  
        WHERE UserId = '{}' AND start_dd = '{}' 
        '''.format(UserId,start_dd)
    results = pd.read_sql(sql=SQL,con=g.conn_Guess365,coerce_float=True)
    if len(results)>0:
        ori_predict_num = int(results['bonus'].iloc[0])
        predict_num += ori_predict_num

    if predict_num >=10 and predict_num<20:
        Level= '銅'
    elif predict_num >=20 and predict_num<30:
        Level = '銀'
    elif predict_num >=30 and predict_num<50:
        Level = '金'
    elif predict_num >=50 and predict_num<60:
        Level = '白金'
    elif predict_num >= 60 and predict_num<70:
        Level = '鑽石'
    elif predict_num >= 70:
        Level = '菁英'
    else:
        Level = '無'

    if len(results)>0:
        update_sql = '''
        UPDATE [dbo].[UserBonus] SET [bonus]='{:.2f}',[Level]=N'{}',[start_dd]='{}',[end_dd]='{}',[Modify_dd]='{}' WHERE UserId = '{}' AND start_dd = '{}' 
            '''.format(float(predict_num),Level,start_dd,end_dd,Modify_dd,UserId,start_dd)
        cursor = g.conn_Guess365.cursor()
        cursor.execute(update_sql)
        cursor.commit()
        
    else:
        insert_sql = '''INSERT INTO [dbo].[UserBonus]([UserId],[bonus],[Level],[start_dd],[end_dd],[Modify_dd])
            VALUES('{}','{:.2f}',N'{}','{}','{}','{}')
        '''.format(UserId,float(predict_num),Level,start_dd,end_dd,Modify_dd)
        cursor = g.conn_Guess365.cursor()
        cursor.execute(insert_sql)
        cursor.commit()

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)


# In[ ]:


ecocoapidev1.southeastasia.cloudapp.azure.com

