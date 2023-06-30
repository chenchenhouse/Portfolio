import random
import linebot
from linebot import LineBotApi, WebhookHandler
from linebot.models import TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, PostbackEvent, MessageEvent, \
    TextMessage, TextSendMessage, BubbleContainer, ImageComponent, BoxComponent, TextComponent, ImageSendMessage \
    , IconComponent, ButtonComponent, SeparatorComponent, FlexSendMessage, URIAction, PostbackAction
from linebot.models import MessageEvent, TextMessage, PostbackEvent, TextSendMessage, TemplateSendMessage, \
    ConfirmTemplate, MessageTemplateAction, ButtonsTemplate, PostbackTemplateAction, URITemplateAction, \
    CarouselTemplate, CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn
import pandas as pd
import requests
import json
from datetime import datetime
from datetime import datetime, timezone, timedelta
import traceback, pymssql
import time
from time import sleep
import web_config
import pyodbc

line_bot_api = LineBotApi(web_config.line_district().line_bot_api)
handler = WebhookHandler(web_config.line_district().handler)
domain_name = web_config.domain().domain_name

_server_gamania = web_config.production().server
_database_gamania = web_config.production().database
_uid_gamania = web_config.production().username
_pwd_gamania = web_config.production().password
_port = "1433"


def get_ConnectionFromDB():
    # db = pymssql.connect(server, user, password, database)
    # cursor = db.cursor(as_dict=True)
    conn_Gamania = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=' + _server_gamania + ';Port=' + _port + ';DATABASE=' + _database_gamania + ';UID=' + _uid_gamania + ';PWD=' + _pwd_gamania)  # for MSSQL
    cursor = conn_Gamania.cursor()
    return cursor, conn_Gamania


def set_results():
    print(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), '開始更新賽果')
    print(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), '取得所有已開賽，且已選擇PK')
    cursor, conn_Gamania = get_ConnectionFromDB()
    PKs = get_LinePlayerPK()
    for PK in range(len(PKs)):
        try:
            print('* ' * 10, f"取得Id {PKs['id'].iloc[PK]}的賽果，{PKs['EventCode'].iloc[PK][0]}", '* ' * 10)
            HomeScore, AwayScore = get_MatchResult(PKs['EventCode'].iloc[PK][0])
            # MatchResult = {'HomeScore':2,'AwayScore':5}
            Result = None
            if HomeScore == None:
                print(f"Id:{PKs['id'].iloc[PK]} 沒賽果")
                continue
            if PKs['SportCode'].iloc[PK] == '1' and PKs['GroupOptionCode'].iloc[PK] in ('55'):  # 雙勝彩
                pass
            elif PKs['Option1'].iloc[PK] in ('1', '2', 'X') and PKs['SpecialBetValue'].iloc[PK] == '':  # 不讓分
                if float(HomeScore) > float(AwayScore):
                    if PKs['Option1'].iloc[PK] == '1':
                        Result = 'UserId1'
                    elif PKs['Option2'].iloc[PK] == '1':
                        Result = 'UserId2'
                    else:
                        Result = 'X'
                elif float(HomeScore) < float(AwayScore):
                    if PKs['Option1'].iloc[PK] == '2':
                        Result = 'UserId1'
                    elif PKs['Option2'].iloc[PK] == '2':
                        Result = 'UserId2'
                    else:
                        Result = 'X'
                elif float(HomeScore) == float(MAwayScore):
                    if PKs['Option1'].iloc[PK] == 'X':
                        Result = 'UserId1'
                    elif PKs['Option2'].iloc[PK] == 'X':
                        Result = 'UserId2'
                    else:
                        Result = 'X'
            elif PKs['Option1'].iloc[PK] in ('1', '2', 'X') and PKs['SpecialBetValue'].iloc[PK] != '':  # 讓分
                if float(HomeScore) > float(AwayScore) + float(PKs['SpecialBetValue'].iloc[PK]):
                    if PKs['Option1'].iloc[PK] == '1':
                        Result = 'UserId1'
                    elif PKs['Option2'].iloc[PK] == '1':
                        Result = 'UserId2'
                    else:
                        Result = 'X'
                elif float(HomeScore) < float(AwayScore) + float(PKs['SpecialBetValue'].iloc[PK]):
                    if PKs['Option1'].iloc[PK] == '2':
                        Result = 'UserId1'
                    elif PKs['Option2'].iloc[PK] == '2':
                        Result = 'UserId2'
                    else:
                        Result = 'X'
                elif float(HomeScore) == float(AwayScore) + float(PKs['SpecialBetValue'].iloc[PK]):
                    if PKs['Option1'].iloc[PK] == 'X':
                        Result = 'UserId1'
                    elif PKs['Option2'].iloc[PK] == 'X':
                        Result = 'UserId2'
                    else:
                        Result = 'X'
            elif PKs['Option1'].iloc[PK] in ('Over', 'Under'):  # 大小
                if float(HomeScore) + float(AwayScore) > float(PKs['SpecialBetValue'].iloc[PK]):
                    if PKs['Option1'].iloc[PK] == 'Over':
                        Result = 'UserId1'
                    elif PKs['Option2'].iloc[PK] == 'Over':
                        Result = 'UserId2'
                    else:
                        Result = 'X'
                elif float(HomeScore) + float(AwayScore) < float(PKs['SpecialBetValue'].iloc[PK]):
                    if PKs['Option1'].iloc[PK] == 'Under':
                        Result = 'UserId1'
                    elif PKs['Option2'].iloc[PK] == 'Under':
                        Result = 'UserId2'
                    else:
                        Result = 'X'
                elif float(HomeScore) + float(AwayScore) == float(PKs['SpecialBetValue'].iloc[PK]):
                    if PKs['Option1'].iloc[PK] == 'X':
                        Result = 'X'
                    elif PKs['Option2'].iloc[PK] == 'X':
                        Result = 'X'
                    else:
                        Result = 'X'
            print("Result :" + Result)
            if Result is not None:
                SQL = "UPDATE LinePlayerPK SET Result = '{}' WHERE id = '{}'".format(Result, PKs['id'].iloc[PK])
                print(SQL)
                cursor.execute(SQL)
                cursor.commit()
                # db.commit()
        except:
            traceback.print_exc()


def set_GPlus():
    print(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), '開始更新GPlus')
    print(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), '取得所有已完賽，且已選擇PK')
    cursor, conn_Gamania = get_ConnectionFromDB()
    PKs = get_LinePlayerPK(result=1)
    print(PKs)
    for PK in range(len(PKs)):
        try:
            capital = float(PKs['GplusPoint'].iloc[PK])
            print(PKs['GplusPoint'].iloc[PK])
            print('* ' * 10, f"取得Id {PKs['id'].iloc[PK]}PK勝負", '* ' * 10)
            Result = PKs['Result'].iloc[PK]
            if Result == 'UserId1':
                if PKs['Option1'].iloc[PK] in ('1', 'Over'):
                    profit = round((capital) * (float(PKs['HomeOdds'].iloc[PK]) - 1), 0)
                elif PKs['Option1'].iloc[PK] in ('2', 'Under'):
                    profit = round((capital) * (float(PKs['AwayOdds'].iloc[PK]) - 1), 0)
                else:
                    profit = 0
                SQL = "UPDATE [dbo].[LinePlayerPK] SET [GPlus] = {} where [id]='{}'".format(profit, PKs['id'].iloc[PK])
                # cursor.execute(SQL)
                # db.commit()
                cursor.execute(SQL)
                cursor.commit()
                print(SQL)
                # 發起者獲勝
                # GPlus_detail新增明細
                SQL = """
                        INSERT INTO [dbo].[UserGPlus_detail] (UserId,GPlus,Resource,PKindex,created_dd)
                        VALUES ('{}',{},'PK','{}','{}')
                    """.format(PKs['UserId1'].iloc[PK], profit, PKs['id'].iloc[PK]
                               , datetime.now().astimezone(timezone(timedelta(hours=8))).strftime
                                                     ('%Y-%m-%d %H:%M:%S.000'))
                print(SQL)
                # cursor.execute(SQL)
                # db.commit()
                cursor.execute(SQL)
                cursor.commit()

                # GPlus更改總額
                SQL = '''SELECT a.Userid,sum(b.GPlus) as total_GPlus
                          FROM [dbo].[UserGPlus] as a
                          inner join UserGPlus_detail as b on a.UserId = b.UserId
                           where a.UserId = '{}'
                          group by a.UserId
                    '''.format(PKs['UserId1'].iloc[PK])
                # cursor.execute(SQL)
                print(SQL)
                usergplus = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
                gplus = usergplus['total_GPlus'].iloc[0]

                SQL = """
                    UPDATE  [dbo].[UserGPlus] SET GPlus = {},Modify_dd = '{}' where UserId = '{}' 
                """.format(gplus,
                           datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                           PKs['UserId1'].iloc[PK])
                print(SQL)
                # cursor.execute(SQL)
                # db.commit()
                cursor.execute(SQL)
                cursor.commit()

            elif Result == 'UserId2':
                if PKs['Option2'].iloc[PK] in ('1', 'Over'):
                    profit = capital * (float(PKs['HomeOdds'].iloc[PK]) - 1)
                elif PKs['Option2'].iloc[PK] in ('2', 'Under'):
                    profit = capital * (float(PKs['AwayOdds'].iloc[PK]) - 1)
                else:
                    profit = 0

                SQL = """UPDATE [dbo].[LinePlayerPK] SET [GPlus] = {} 
                    where [id]='{}'
                """.format(profit, PKs['id'].iloc[PK])
                # cursor.execute(SQL)
                # db.commit()
                cursor.execute(SQL)
                cursor.commit()
                print(SQL)

                # 挑戰者獲勝
                # GPlus_detail新增明細
                SQL = """
                        INSERT INTO [dbo].[UserGPlus_detail] (UserId,GPlus,Resource,PKindex,created_dd)
                        VALUES ('{}',{},'PK','{}','{}')
                    """.format(PKs['UserId2'].iloc[PK], profit, PKs['id'].iloc[PK]
                               , datetime.now().astimezone(timezone(timedelta(hours=8))).strftime
                                                     ('%Y-%m-%d %H:%M:%S.000'))
                print(SQL)
                # cursor.execute(SQL)
                # db.commit()
                cursor.execute(SQL)
                cursor.commit()

                # GPlus更改總額
                SQL = '''SELECT a.Userid,sum(b.GPlus) as total_GPlus
                                          FROM [dbo].[UserGPlus] as a
                                          inner join UserGPlus_detail as b on a.UserId = b.UserId
                                           where a.UserId = '{}'
                                          group by a.UserId
                                    '''.format(PKs['UserId2'].iloc[PK])
                # cursor.execute(SQL)
                print(SQL)
                usergplus = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
                gplus = usergplus['total_GPlus'].iloc[0]

                SQL = """
                    UPDATE  [dbo].[UserGPlus] SET GPlus = {},Modify_dd = '{}' where UserId = '{}' 
                """.format(gplus,
                           datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),
                           PKs['UserId2'].iloc[PK])
                print(SQL)
                # cursor.execute(SQL)
                # db.commit()
                cursor.execute(SQL)
                cursor.commit()

            else:
                SQL = """UPDATE [dbo].[LinePlayerPK] SET [GPlus] = {}
                    where [id]='{}'
                """.format(0, PKs['id'].iloc[PK])
                print(SQL)
                # cursor.execute(SQL)
                # db.commit()
                cursor.execute(SQL)
                cursor.commit()


        except:
            traceback.print_exc()


def push_results():
    print(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), '開始通知PK賽果')
    print(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), '取得所有已完賽，且已選擇PK')
    PKs = get_LinePlayerPK(result=2)
    if len(PKs) > 0:
        UserIds = pd.concat([PKs['UserId1'], PKs['UserId2']]).unique()
        for UserId in UserIds:
            try:
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
                                        "url": "https://i.imgur.com/itxdCwT.png",
                                        "size": "full",
                                        "aspectMode": "cover",
                                        "aspectRatio": "1:1.17"
                                    }
                                ],
                                "width": "300px",
                                "height": "350px",
                                "paddingAll": "0px"
                            }
                        }
                    ]
                }
                PKsfilter = PKs[(PKs['UserId1'] == UserId) | (PKs['UserId2'] == UserId)]
                for PKfilter in PKsfilter.to_dict('records'):
                    print(PKfilter)
                    Carousel["contents"] += [get_LinePlayerPKResultFlex(PKfilter, UserId)]

                print(get_LineUserMember(UserId=UserId))
                print(Carousel)
                line_bot_api.push_message(get_LineUserMember(UserId=UserId), FlexSendMessage('PK賽果通知', Carousel))
            except:
                traceback.print_exc()


def get_LinePlayerPKResultFlex(PKfilter, UserId):
    LinePlayerPKResultFlex = json.load(open('static/LinePlayerPKResultFlex.json', 'r', encoding='utf-8'))
    HomeTeam, AwayTeam = TeamNameCorrection(PKfilter['HomeTeam']), TeamNameCorrection(PKfilter['AwayTeam'])
    # 發起者名稱
    LinePlayerPKResultFlex['body']['contents'][1]['contents'][0]['text'] = get_member(PKfilter['UserId1'])
    # 發起者大頭照
    LinePlayerPKResultFlex['body']['contents'][2]['contents'][0]['url'] = f"https://{domain_name}/static/memberlogo/{PKfilter['UserId1']}.png"
    # 挑戰者名稱
    LinePlayerPKResultFlex['body']['contents'][3]['contents'][0]['text'] = get_member(PKfilter['UserId2'])
    # 挑戰者大頭照
    LinePlayerPKResultFlex['body']['contents'][4]['contents'][0]['url'] = f"https://{domain_name}/static/memberlogo/{PKfilter['UserId2']}.png"
    # 輸贏logo
    if PKfilter['Result'] == 'UserId1':
        LinePlayerPKResultFlex['body']['contents'][5]['contents'][0]['url'] = 'https://i.imgur.com/I6K0pjh.png'
        LinePlayerPKResultFlex['body']['contents'][6]['contents'][0]['url'] = 'https://i.imgur.com/dgblXWR.png'
    else:
        LinePlayerPKResultFlex['body']['contents'][5]['contents'][0]['url'] = 'https://i.imgur.com/dgblXWR.png'
        LinePlayerPKResultFlex['body']['contents'][5]['offsetTop'] = '40px'
        LinePlayerPKResultFlex['body']['contents'][6]['contents'][0]['url'] = 'https://i.imgur.com/I6K0pjh.png'
        LinePlayerPKResultFlex['body']['contents'][6]['offsetTop'] = '33px'
    # 挑戰者選擇
    SpecialBetValue = PKfilter['SpecialBetValue']
    if PKfilter['GroupOptionCode'] == '20':
        if PKfilter['Option1'] == '1':
            LinePlayerPKResultFlex['body']['contents'][8]['contents'][0]['text'] = "主隊"
            LinePlayerPKResultFlex['body']['contents'][7]['contents'][0]['text'] = "客隊"
        else:
            LinePlayerPKResultFlex['body']['contents'][8]['contents'][0]['text'] = "客隊"
            LinePlayerPKResultFlex['body']['contents'][7]['contents'][0]['text'] = "主隊"
    elif PKfilter['GroupOptionCode'] in ['60','52']:
        if PKfilter['Option1'] == 'Over':
            LinePlayerPKResultFlex['body']['contents'][8]['contents'][0]['text'] = f"大於{SpecialBetValue}"
            LinePlayerPKResultFlex['body']['contents'][7]['contents'][0]['text'] = f"小於{SpecialBetValue}"
        else:
            LinePlayerPKResultFlex['body']['contents'][8]['contents'][0]['text'] = f"小於{SpecialBetValue}"
            LinePlayerPKResultFlex['body']['contents'][7]['contents'][0]['text'] = f"大於{SpecialBetValue}"
    elif PKfilter['GroupOptionCode'] in ['228','51']:
        if float(SpecialBetValue) > 0:
            SpecialBetValue = SpecialBetValue[1:]
            if PKfilter['Option1'] == 1:
                LinePlayerPKResultFlex['body']['contents'][8]['contents'][0]['text'] = f"主+{SpecialBetValue}"
                LinePlayerPKResultFlex['body']['contents'][7]['contents'][0]['text'] = f"客-{SpecialBetValue}"
            else:
                LinePlayerPKResultFlex['body']['contents'][8]['contents'][0]['text'] = f"客-{SpecialBetValue}"
                LinePlayerPKResultFlex['body']['contents'][7]['contents'][0]['text'] = f"主+{SpecialBetValue}"
        else:
            SpecialBetValue = SpecialBetValue[1:]
            if PKfilter['Option1'] == 1:
                LinePlayerPKResultFlex['body']['contents'][8]['contents'][0]['text'] = f"主-{SpecialBetValue}"
                LinePlayerPKResultFlex['body']['contents'][7]['contents'][0]['text'] = f"客+{SpecialBetValue}"
            else:
                LinePlayerPKResultFlex['body']['contents'][8]['contents'][0]['text'] = f"客+{SpecialBetValue}"
                LinePlayerPKResultFlex['body']['contents'][7]['contents'][0]['text'] = f"主-{SpecialBetValue}"
                # 開賽時間
    LinePlayerPKResultFlex['body']['contents'][9]['contents'][0]['contents'][0]['text'] = '開賽時間：' + PKfilter[
                                                                                                        'MatchTime'].strftime(
        "%Y-%m-%d %H:%M")[5:]
    # PK場號
    LinePlayerPKResultFlex['body']['contents'][9]['contents'][2]['contents'][0]['text'] = f"PK場號 : {PKfilter['id']}"
    # 盤口
    LinePlayerPKResultFlex['body']['contents'][9]['contents'][3]['contents'][0]['text'] = get_TypeCname(
        PKfilter['SportCode'], PKfilter['GroupOptionCode'])
    # 主隊名稱
    LinePlayerPKResultFlex['body']['contents'][9]['contents'][4]['contents'][0]['contents'][0]['text'] = HomeTeam
    # 客隊名稱
    LinePlayerPKResultFlex['body']['contents'][9]['contents'][4]['contents'][2]['contents'][0]['text'] = AwayTeam
    # 獲勝與失敗
    GPlus = int(PKfilter['GPlus'])
    if PKfilter['Result'] == 'UserId1':
        if UserId == PKfilter['UserId1']:
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][0]['text'] = '恭喜獲得PK賽勝利'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][1]['text'] = f'您將贏得『{GPlus}』G⁺幣'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][0]['color'] = '#e32b79'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][1]['color'] = '#e32b79'
        else:
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][0]['text'] = 'QQ沒能獲得PK勝利'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][1]['text'] = f'別氣餒，我們再接再厲!!'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][0]['color'] = '#8B8378'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][1]['color'] = '#8B8378'
    else:
        if UserId == PKfilter['UserId1']:
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][0]['text'] = 'QQ沒能獲得PK勝利'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][1]['text'] = f'別氣餒，我們再接再厲!!'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][0]['color'] = '#8B8378'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][1]['color'] = '#8B8378'
        else:
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][0]['text'] = '恭喜獲得PK賽勝利'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][1]['text'] = f'您將贏得『{GPlus}』G⁺幣'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][0]['color'] = '#e32b79'
            LinePlayerPKResultFlex['body']['contents'][9]['contents'][5]['contents'][1]['color'] = '#e32b79'
    return LinePlayerPKResultFlex


def get_LinePlayerPK(result=None):
    cursor, conn_Gamania = get_ConnectionFromDB()
    if result == None:
        SQL = '''Select * From LinePlayerPK inner join MatchEntry on LinePlayerPK.EventCode = MatchEntry.EventCode 
        Where UserId1 is not null and UserId2 is not null and Option1 is not null and Option2 is not null and Result is null and MatchTime >= '{}'
        '''.format((datetime.now() - timedelta(days=7)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'))
        print(SQL)
        PKs = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
        return PKs
    elif result == 1:
        SQL = '''Select * From LinePlayerPK inner join MatchEntry on LinePlayerPK.EventCode = MatchEntry.EventCode 
        Where  Result is not null and GPlus is null and MatchTime >= '{}'
        '''.format((datetime.now() - timedelta(days=7)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'))
        # cursor.execute(SQL)
        print(SQL)
        PKs = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
        return PKs
    elif result == 2:
        SQL = '''Select * From LinePlayerPK inner join MatchEntry on LinePlayerPK.EventCode = MatchEntry.EventCode 
        Where  Result is not null and GPlus is not null and MatchTime >= '{}'
        '''.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'))
        # cursor.execute(SQL)
        print(SQL)
        PKs = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
        return PKs


def get_MatchResult(EventCode):
    cursor, conn_Gamania = get_ConnectionFromDB()
    SQL = '''Select * From MatchResults where EventCode = '{}' and isChecked=1 '''.format(EventCode)
    print(SQL)
    # cursor.execute(SQL)
    # results = cursor.fetchone()
    get_ConnectionFromDB()
    results = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
    if len(results) > 0:
        return results['HomeScore'].iloc[0], results['AwayScore'].iloc[0]
    else:
        return None, None


def get_LineUserMember(UserId=None):
    cursor, conn_Gamania = get_ConnectionFromDB()
    if UserId == None:
        '''
        取得所有玩家用戶名單
        '''
        SQL = "select * from [dbo].[LineUserMember] "
        # cursor.execute(SQL)
        # results = cursor.fetchall()
        results = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
        return results
    elif UserId != None:
        '''
        取得指定玩家用戶名單
        '''
        SQL = "select * from [dbo].[LineUserMember] where UserId = '{}' ".format(UserId)
        # cursor.execute(SQL)
        # result = cursor.fetchone()
        results = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
        if len(results) > 0:
            return results['LineUniqueID'].iloc[0]
        else:
            return None


def get_TypeCname(SportCode, GroupOptionCode):
    cursor, conn_Gamania = get_ConnectionFromDB()
    SQL = '''SELECT [SportCode],[Type],[Type_cname],[Play_Name],[GroupOptionCode1] FROM [dbo].[GroupOptionCode] 
                where [SportCode]='{}' and  GroupOptionCode1='{}' '''.format(SportCode, GroupOptionCode)
    # cursor.execute(sql)
    # result = cursor.fetchone()
    results = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
    if len(results) > 0:
        return results['Type_cname'].iloc[0]
    else:
        return None


def get_member(UserId):
    cursor, conn_Gamania = get_ConnectionFromDB()
    SQL = "select * from UserMember where UserId = '{}'".format(UserId)
    # cursor.execute(sql)
    # result = cursor.fetchone()
    results = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
    if len(results) > 0:
        return results['member'].iloc[0]
    else:
        return None


def TeamNameCorrection(Eng_TeamName):
    cursor, conn_Gamania = get_ConnectionFromDB()
    Eng_TeamName = Eng_TeamName.replace(r"'", r"''")
    SQL = "SELECT * FROM teams where team = '{}' ;".format(Eng_TeamName)
    # cursor.execute(sql)
    # result  = cursor.fetchone()
    results = pd.read_sql(sql=SQL, con=conn_Gamania, coerce_float=True)
    if len(results) > 0:
        return results['name'].iloc[0]
    else:
        return results['team'].iloc[0]


if __name__ == '__main__':
    set_results()
    set_GPlus()
    push_results()