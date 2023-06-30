import linebot
import json
import pandas as pd
import random
import requests
import traceback
import time
import web_config
import pyodbc

from datetime import datetime, timezone, timedelta
from linebot import LineBotApi, WebhookHandler
from linebot.models import FlexSendMessage
from flask import g
from time import sleep
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO

class Match_PK:

    def __init__(self,conn_Guess365):
        self.conn_Guess365 = conn_Guess365
        self.line_bot_api = LineBotApi(web_config.line_district().line_bot_api)
        # 必須放上自己的Channel Secret
        self.handler = WebhookHandler(web_config.line_district().handler)

        '''
        self.line_bot_api = LineBotApi(web_config.line_test().line_bot_api) 
        self.handler = WebhookHandler(web_config.line_test().handler)
        '''
        self.domain_name = web_config.domain().domain_name


    def invitePK(self):
        print(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), '開始進行邀請推播')
        PKs = self.get_PKNotMatch(isUserId2=True)
        LineUserMembers = self.get_LineUserMember()
        for PK in range(len(PKs)):
            try:
                UserId1 = PKs['UserId1'][PK]
                user = ['4e232011-0f1d-496a-b101-90d1a40b3aa9', 'b51e1095-a514-45ba-8b67-f459cc1bc0fd',
                        'dcefd442-0874-4092-bb70-dd499a5ee8af', 'afffb87f5f2a929492290697fa1f13b1',
                        'b00de996-5e9b-4daf-99b5-6f0b60f7f711','07374cccfcb7784b6c25232686a3a692',
                        'c0ef0f89-2913-4454-af2f-50f074090c53','d78be24b-6e1a-40fc-a95e-1d5ec0dc09eb',
                        '63530c710a0fbad44ef5fb5fbdefc986','7a4182a1ea993152a32e67c4c43d5bc2']
                if UserId1 in user:
                    LineUserMember = random.choice(LineUserMembers[(LineUserMembers.UserId != UserId1) & (
                                LineUserMembers.situate == 'connect')].to_dict('records'))
                else:
                    LineUserMember = random.choice(LineUserMembers[(LineUserMembers.UserId.isin(user)) & (
                            LineUserMembers.situate == 'connect')].to_dict('records'))
                print(LineUserMember['UserId'])
                invitePKFlex = self.set_invitePKFlex(PKs.iloc[PK])
                self.line_bot_api.push_message(LineUserMember['LineUniqueID'],FlexSendMessage('有人邀您玩PK囉 快來賺G⁺幣拿大獎!!', invitePKFlex))
                SQL = """UPDATE [dbo].[LinePlayerPK] SET [isPushed] = '1',[UserId2] = '{}'
                            where id = {}
                        """.format(LineUserMember['UserId'], PKs['id'].iloc[PK])
                try:
                    cursor = self.conn_Guess365.cursor()
                    cursor.execute(SQL)
                    cursor.commit()
                except Exception as e:
                    print(e)
                    cursor = self.conn_Guess365.cursor()
                    cursor.execute(SQL)
                    cursor.commit()
            except Exception as e:
                print(e)
                print('不存在的用戶---')

    def get_Quotations(self):
        SQL = "SELECT * From LinePKQuotations"
        results = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
        return list(results['Quotation'])

    def check_photo(self,teamlogos, play, team):
        teamlogo = "https://i.imgur.com/x31phAh.jpeg"
        '''
        檢查隊徽圖片是否存在
        '''
        if team == "Home":
            if len(teamlogos[teamlogos['name'] == play]) > 0:
                team = teamlogos[teamlogos['name'] == play]['image'].iloc[0]
                if str(team) != "None":
                    teamlogo = ("https://guess365.cc" + team).replace(" ", "%20")
        elif team == "Away":
            if len(teamlogos[teamlogos['name'] == play]) > 0:
                team = teamlogos[teamlogos['name'] == play]['image'].iloc[0]
                if str(team) != "None":
                    teamlogo = ("https://guess365.cc" + team).replace(" ", "%20")
        return teamlogo




    def set_invitePKFlex(self, PK):

        sql = """
           SELECT *
             FROM [dbo].[teams]
           """
        teamlogos = pd.read_sql(sql=sql, con=self.conn_Guess365, coerce_float=True)


        corpus = self.get_Quotations()

        invitePKFlex = json.load(open('static/LineInvitePKFlex.json', 'r', encoding='utf-8'))
        #teamlogos = pd.read_csv('static/teamlogos.csv', encoding='big5')
        HomeTeam = PK['Home']
        AwayTeam = PK['Away']
        # 邀請者名稱
        invitePKFlex['body']['contents'][1]['contents'][0]['text'] = PK['member']
        # 邀請者戰績連結
        invitePKFlex['body']['contents'][1]['contents'][0]['action']['data'] = \
        f"@查詢他人戰績=['UserId': '{PK['UserId1']}']"
        # 邀請者大頭照
        invitePKFlex['body']['contents'][2]['contents'][0]['contents'][0]['url'] =\
        f"https://{self.domain_name}/static/memberlogo/{PK['UserId1']}.png"
        # 邀請者戰績連結
        invitePKFlex['body']['contents'][2]['contents'][0]['contents'][0]['action']['data'] = \
            f"@查詢他人戰績=['UserId': '{PK['UserId1']}']"
        # 下狠話
        invitePKFlex['body']['contents'][2]['contents'][1]['contents'][0]['text'] = \
            corpus[random.randint(0, len(corpus) - 1)].strip()
        # 比賽時間
        invitePKFlex['body']['contents'][3]['contents'][0]['contents'][0]['text'] =\
            f"開賽時間 : {PK['MatchTime'].strftime('%Y-%m-%d %H:%M')[5:]}"
        # PK場號
        invitePKFlex['body']['contents'][5]['contents'][0]['text'] = f"PK場號 : {PK['id']}"
        # 主隊名稱
        if HomeTeam == None:
            HomeTeam = PK['HomeTeam']
        invitePKFlex['body']['contents'][7]['contents'][0]['contents'][0]['text'] = HomeTeam
        # 主隊LOGO
        invitePKFlex['body']['contents'][6]['contents'][0]['contents'][0]['url'] = self.check_photo(teamlogos,HomeTeam,'Home')
        # 客隊名稱
        if AwayTeam == None:
            AwayTeam = PK['AwayTeam']
        invitePKFlex['body']['contents'][7]['contents'][1]['contents'][0]['text'] = AwayTeam
        # 客隊LOGO
        invitePKFlex['body']['contents'][6]['contents'][2]['contents'][0]['url'] = self.check_photo(teamlogos,AwayTeam,'Away')
        # 盤口
        invitePKFlex['body']['contents'][8]['contents'][1]['contents'][0]['text'] = \
            PK['Type_cname'][:2]
        invitePKFlex['body']['contents'][8]['contents'][1]['contents'][1]['text'] = \
            PK['Type_cname'][2:]
        # 賠率
        Option2code = self.Reverse_OptionCode(PK['Option1'], PK['SportCode'], PK['GroupOptionCode'], HomeTeam, AwayTeam)
        if PK['GroupOptionCode'] == "20":
            if Option2code == '1':
                option1 = "客隊"
                option2 = "主隊"
            else:
                option1 = "主隊"
                option2 = "客隊"
            invitePKFlex['body']['contents'][8]['contents'][0]['contents'][0]['text'] = \
                f"{PK['HomeOdds']}(主)"
            invitePKFlex['body']['contents'][8]['contents'][2]['contents'][0]['text'] = \
                f"{PK['AwayOdds']}(客)"
        elif PK['GroupOptionCode'] in ['60','52']:
            specialBetValue = PK['SpecialBetValue']
            if specialBetValue.split(".")[1] == "0":
                specialBetValue = specialBetValue[:-2]
            if Option2code == 'Over':
                option1 = f"小於{specialBetValue}"
                option2 = f"大於{specialBetValue}"
            else:
                option1 = f"大於{specialBetValue}"
                option2 = f"小於{specialBetValue}"
            invitePKFlex['body']['contents'][8]['contents'][0]['contents'][0]['text'] = \
                f"{PK['HomeOdds']}(大)"
            invitePKFlex['body']['contents'][8]['contents'][2]['contents'][0]['text'] = \
                f"{PK['AwayOdds']}(小)"
        elif PK['GroupOptionCode'] in ['228','51']:
            specialBetValue = PK['SpecialBetValue']
            if specialBetValue.split(".")[1] == "0":
                specialBetValue = specialBetValue[:-2]
            if float(specialBetValue) > 0:
                specialBetValue = specialBetValue[1:]
                if Option2code == '1':
                    option1 = f"客-{specialBetValue}"
                    option2 = f"主+{specialBetValue}"
                else:
                    option1 = f"主+{specialBetValue}"
                    option2 = f"客-{specialBetValue}"
            elif float(specialBetValue) < 0:
                specialBetValue = specialBetValue[1:]
                if Option2code == '1':
                    option1 = f"客+{specialBetValue}"
                    option2 = f"主-{specialBetValue}"
                else:
                    option1 = f"主-{specialBetValue}"
                    option2 = f"客+{specialBetValue}"
            invitePKFlex['body']['contents'][8]['contents'][0]['contents'][0]['text'] = \
                f"{PK['HomeOdds']}(主)"
            invitePKFlex['body']['contents'][8]['contents'][2]['contents'][0]['text'] = \
                f"{PK['AwayOdds']}(客)"

        # LABEL


        invitePKFlex['body']['contents'][9]['contents'][0]['contents'][0]['text'] = \
            f"對手支持『{option1}』"
        invitePKFlex['body']['contents'][9]['contents'][0]['contents'][1]['text'] = \
            f"您是否願意對賭『{option2}』?"
        # ACTION
        invitePKFlex['footer']['contents'][0]['contents'][0]['action']['data'] = \
            f'''@PK邀請選擇=['id':'{PK['id']}','UserId1': '{PK['UserId1']}','option1':'{option1}','option2':'{option2}','Option2Code':'{Option2code}','MatchTime':'{PK['MatchTime']}','LineUniqueID':'{self.get_LineUserMember(UserId=PK['UserId1'])}','HomeTeam':'{HomeTeam}','AwayTeam':'{AwayTeam}','GroupOptionName':'{self.get_TypeCname(PK['SportCode'], PK['GroupOptionCode'])}']'''
        return invitePKFlex

    def matchPK(self, data, userid2):
        print(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'), '開始進行配對')
        # PKs = self.get_PKNotMatch(cursor,isUserId2=False)
        try:
            SQL = """UPDATE [dbo].[LinePlayerPK] SET  [Match_dd] = '{}'
                      where id = {}
                   """.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'),data['id'])
            try:
                cursor = self.conn_Guess365.cursor()
                cursor.execute(SQL)
                cursor.commit()
            except Exception as e:
                print(e)
                cursor = self.conn_Guess365.cursor()
                cursor.execute(SQL)
                cursor.commit()
            for name in [data['UserId1'], userid2]:

                #檢查GPlus存不存在
                SQL = """
                    SELECT *
                      FROM [dbo].[UserGPlus_detail] as a
                      inner join UserGPlus as b on a.UserId = b.UserId
                      where a.UserId = '{}'
                """.format(name)
                try:
                    results = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
                except Exception as e:
                    print(e)
                    results = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)

                if len(results) == 0:
                    #GPlus不存在創建新的
                    SQL = """
                            INSERT INTO UserGPlus (UserId,GPlus,created_dd)
                            VALUES ('{}','0','{}')
                    """.format(name,
                               datetime.now().astimezone(timezone(timedelta(hours=8))).strftime(
                                   '%Y-%m-%d %H:%M:%S.000'))
                    try:
                        cursor = self.conn_Guess365.cursor()
                        cursor.execute(SQL)
                        cursor.commit()
                    except Exception as e:
                        print(e)
                        cursor = self.conn_Guess365.cursor()
                        cursor.execute(SQL)
                        cursor.commit()
                #寫入GPlus_detail
                SQL = """
                        INSERT INTO UserGPlus_detail (UserId,GPlus,Resource,PKindex,created_dd)
                        VALUES ('{}','0','PK','{}','{}')
                """.format(name,data['id'],datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
                try:
                    cursor = self.conn_Guess365.cursor()
                    cursor.execute(SQL)
                    cursor.commit()
                except Exception as e:
                    print(e)
                    cursor = self.conn_Guess365.cursor()
                    cursor.execute(SQL)
                    cursor.commit()
        except:
            traceback.print_exc()

    def get_PKNotMatch(self, isUserId2):
        if isUserId2 == False:
            '''
            取得所有未配對列表
            isAutoMatch=0:手動, UserId2 is null, MatchEntry.MatchTime >= NOW()
            '''
            SQL = """ SELECT a.*,b.*,c.*,d.name as Home,e.name as Away,f.member,g.Type_cname from LinePlayerPK as a
                        inner join MatchEntry  as b on a.EventCode = b.EventCode
                        inner join LineUserMember as c on a.UserId1 =  c.UserId
                        full outer join teams as d on b.HomeTeam = d.team
                        full outer  join teams as e on b.AwayTeam = e.team
                        inner join UserMember as f on a.UserId1 = f.UserId
                        inner join GroupOptionCode as g on g.SportCode = b.SportCode and g.GroupOptionCode1 = a.GroupOptionCode
                        where isAutoMatch=0 and UserId2 is null and b.MatchTime >= '{}'
                        order by id desc
                    """.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
            try:
                results = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
            except Exception as e:
                print(e)
                results = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
            return results
        elif isUserId2 == True:
            '''
             取得所有未推播邀請列表
             isPushed=0, UserId2 is not null, MatchEntry.MatchTime >= NOW()
             '''
            SQL = """ SELECT a.*,b.*,c.*,d.name as Home,e.name as Away,f.member,g.Type_cname from LinePlayerPK as a
                        inner join MatchEntry  as b on a.EventCode = b.EventCode
                        inner join LineUserMember as c on a.UserId1 =  c.UserId
                        full outer join teams as d on b.HomeTeam = d.team
                        full outer  join teams as e on b.AwayTeam = e.team
                        inner join UserMember as f on a.UserId1 = f.UserId
                        inner join GroupOptionCode as g on g.SportCode = b.SportCode and g.GroupOptionCode1 = a.GroupOptionCode
                where isAutoMatch=0 and option2 is null and isPushed=0 and b.MatchTime >= '{}'
                """.format(datetime.now().astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.000'))
            try:

                results = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
            except Exception as e:
                print(e)
                results = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
            return results

    def get_LineUserMember(self, UserId=None):
        if UserId == None:
            '''
            取得所有玩家用戶名單
            '''
            SQL = "select * from [dbo].[LineUserMember] "
            try:
                results = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
            except:
                results = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
            return results
        elif UserId != None:
            '''
            取得指定玩家用戶名單
            '''
            SQL = "select * from [dbo].[LineUserMember] where UserId = '{}' ".format(UserId)
            try:
                result = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
            except:
                result = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
            #cursor.execute(SQL)
            #result = cursor.fetchone()
            if len(result) > 0:
                return result['LineUniqueID'].iloc[0]
            else:
                return None

    def get_TypeCname(self, SportCode, GroupOptionCode):
        SQL = '''SELECT [SportCode],[Type],[Type_cname],[Play_Name],[GroupOptionCode1] FROM [dbo].[GroupOptionCode] 
                    where [SportCode]='{}' and  GroupOptionCode1='{}' 
                '''.format(SportCode,GroupOptionCode)
        #result = cursor.fetchone()
        try:
            result = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
        except:
            result = pd.read_sql(sql=SQL, con=self.conn_Guess365, coerce_float=True)
        if len(result) > 0:
            return result['Type_cname'].iloc[0]
        else:
            return None


    def TeamNameCorrection(self, Eng_TeamName):
        Eng_TeamName = Eng_TeamName.replace(r"'", r"''")
        sql = "SELECT name FROM teams where team = '{}' ;".format(Eng_TeamName)
        try:
            result = pd.read_sql(sql=sql, con=self.conn_Guess365, coerce_float=True)
        except:
            result = pd.read_sql(sql=sql, con=self.conn_Guess365, coerce_float=True)
        #result = cursor.fetchone()
        if len(result) > 0:
            return result['name'].iloc[0]
        else:
            return None

    def get_member(self, UserId):
        sql = "select * from UserMember where UserId = '{}'".format(UserId)
        try:
            result = pd.read_sql(sql=sql, con=self.conn_Guess365, coerce_float=True)
        except:
            result = pd.read_sql(sql=sql, con=self.conn_Guess365, coerce_float=True)
        if len(result) > 0:
            return result['member'].iloc[0]
        else:
            return None

    def Mapping_OptionCode(self, OptionCode, SportCode, GroupOptionCode, HomeTeam, AwayTeam):
        if SportCode == '1' and GroupOptionCode in ('55'):
            texts = [OptionCode.split('/')[0].strip(), OptionCode.split('/')[1].strip()]
            if not texts[0] == 'Draw' and not texts[1] == 'Draw':
                return '平手'
            elif not texts[0] == 'Draw' and texts[1] == 'Draw':
                return HomeTeam + '/平手'
            elif texts[0] == 'Draw' and not texts[1] == 'Draw':
                return '平手/' + AwayTeam
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

    def Reverse_OptionCode(self, OptionCode, SportCode, GroupOptionCode, HomeTeam, AwayTeam):
        if SportCode == '1' and GroupOptionCode in ('55'):
            texts = [OptionCode.split('/')[0].strip(), OptionCode.split('/')[1].strip()]
            if not texts[0] == 'Draw' and not texts[1] == 'Draw':
                return HomeTeam + '/Draw'
            elif not texts[0] == 'Draw' and texts[1] == 'Draw':
                return 'X'
            elif texts[0] == 'Draw' and not texts[1] == 'Draw':
                return 'Draw/' + AwayTeam
        else:
            if OptionCode == '1':
                return '2'
            elif OptionCode == '2':
                return '1'
            elif OptionCode == 'X':
                return '2'
            elif OptionCode == 'Over':
                return 'Under'
            elif OptionCode == 'Under':
                return 'Over'
        return None

    '''方形圖轉成圓形大頭照'''

    def crop_max_square(self, pil_img):
        return self.crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    def crop_center(self, pil_img, crop_width, crop_height):
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))

    def mask_circle_transparent(self, pil_img, blur_radius, offset=0):
        offset = blur_radius * 2 + offset
        mask = Image.new("L", pil_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        result = pil_img.copy()
        result.putalpha(mask)
        return result

    def comply_match(self):
        self.invitePK()


if __name__ == '__main__':
    Match_PK = Match_PK()
    Match_PK.comply_match()
