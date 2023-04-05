import datetime
import json
import logging
import numpy as np
import os
import pandas as pd
import requests
import warnings

warnings.filterwarnings("ignore")

class CPBLForecast(object):
    '''
    預測CPBL
    '''
    
    def __init__(self):
        self.account = [accounts]
        self.password = password
        self.date = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        self.path =r"\bot_predict_logfile.log"
        
    def found(self):
        '''
        查詢CPBL賽事
        '''
        if self.update == False:
            print("*********************Found CPBL Data start*********************")   
            try:
                url = f'https://ecocoapidev1.southeastasia.cloudapp.azure.com/MatchEntryInfo/DateBetween/CPBL/{self.date}~{self.date}'
                response = requests.get(url,verify=False,auth=HTTPBasicAuth('rick', 'rick000')).text
                j = json.loads(response)
                json_data = j['response']
                data_all = []
                for i in range(len(json_data)):
                    MatchTime = json_data[i]['MatchTime']
                    odd = json_data[i]['odds']
                    for j in range(len(odd)):
                        Evencode = json_data[i]['EventCode']
                        GroupOptionCode = odd[j]['GroupOptionCode']
                        
                        OptionCode = odd[j]['OptionCode']
                        OptionRate = odd[j]['OptionRate']
                        
                        data_one = {
                            'EventCode':Evencode,
                            'GroupOptionCode':GroupOptionCode,
                            'MatchTime': MatchTime,
                            'OptionCode':OptionCode,
                            'OptionRate':OptionRate,
                        }
                        data_all.append(data_one)
                df = pd.DataFrame(data_all)
                df_group = df.groupby(by=["EventCode","GroupOptionCode","MatchTime"])
                data_all = []
                for key,value in df_group:
                    OptionRate = value["OptionRate"]
                    if len(OptionRate) == 3:
                        rate_1 = float(OptionRate.iloc[1]) / OptionRate.astype(float).sum()
                        rate_2 = float(OptionRate.iloc[0]) / OptionRate.astype(float).sum()
                        rate_3 = float(OptionRate.iloc[2]) / OptionRate.astype(float).sum()
                        data_all.append(rate_1)
                        data_all.append(rate_2)
                        data_all.append(rate_3)
                    else:
                        rate_1 = float(OptionRate.iloc[1]) / OptionRate.astype(float).sum()
                        rate_2 = float(OptionRate.iloc[0]) / OptionRate.astype(float).sum()
                        data_all.append(rate_1)
                        data_all.append(rate_2)
                df = df.sort_values(by=["EventCode","GroupOptionCode","MatchTime"])
                df["win_rate"] = data_all
                df_group = df.groupby(by=["EventCode","GroupOptionCode","MatchTime"])
                self.update = True
                print("*********************Found CPBL Data successful!!*********************")  
                return df_group
            except Exception as e: 
                print(repr(e))
                print("無任何賽事")
    
    def bot_predict(self,df_group):
        '''
        預測CPBL賽事
        '''
        if self.update == True and self.successful == False:
            print("*********************Bot Predict CPBL start*********************")  
            try:
                for bot in self.account:
                    Log_Format = "%(levelname)s %(asctime)s - %(message)s"
                    logging.basicConfig(filename = self.path,
                                                filemode = "a+",
                                                format = Log_Format, 
                                                level = logging.INFO)
                    logger = logging.getLogger()
                    count = 0
                    for key,value in df_group:
                        result = self.logfile(value, bot)
                        if result != True:
                            long = value["OptionCode"].values
                            win = value["win_rate"].values
                            MatchTime = value["MatchTime"].values
                            random_forecast = np.random.choice([0,1],p=[0.3,0.7])
                            if random_forecast == 0:
                                if len(long) == 3:
                                        win1 = round(win[0],4)
                                        win2 = round(win[1],4)
                                        win3 = round(win[2],4)
                                        all_rate = win1 + win2 + win3
                                        if all_rate != 1:
                                            rate_gap = all_rate - 1
                                            random_team = np.random.choice([long[0],long[1],long[2]])
                                            random = False
                                            while random == False:
                                                if random_team == long[0] and win1 > rate_gap:
                                                    win1 = win1 - rate_gap
                                                    random = True
                                                elif random_team == long[1] and win2 > rate_gap:
                                                    win2 = win2 - rate_gap
                                                    random = True
                                                elif random_team == long[2] and win1 > rate_gap:
                                                    win3 = win3 - rate_gap
                                                    random = True
                                                else:
                                                    random_team = np.random.choice([long[0],long[1],long[2]])
                                        random = np.random.choice([long[0],long[1],long[2]],p=[win1,win2,win3])
                                else:
                                    win1 = round(win[0],4)
                                    win2 = round(win[1],4)
                                    all_rate = win1 + win2
                                    if all_rate != 1:
                                        rate_gap = all_rate - 1
                                        random_team = np.random.choice([long[0],long[1]])
                                        random = False
                                        while random == False:
                                            if random_team == long[0] and win1 > rate_gap:
                                                win1 = win1 - rate_gap
                                                random = True
                                            elif random_team == long[1] and win2 > rate_gap:
                                                win2 = win2 - rate_gap
                                                random = True
                                            else:
                                                random_team = np.random.choice([long[0],long[1]])
                                    random = np.random.choice([long[0],long[1]],p=[win1,win2])
                                url = "https://ecocoapidev1.southeastasia.cloudapp.azure.com/PredictMatchEntry/"
                                data = {'account':bot,
                                 'password':self.password,
                                 'GroupOptionCode':value["GroupOptionCode"].values[0],
                                 'OptionCode':random,
                                 'EventCode':value["EventCode"].values[0],
                                 'PredictType':'Forecast'}
                                print(data)
                                response_ = requests.post(url,verify=False, data = data, auth=HTTPBasicAuth('rick', 'rick000')).text
                                print(response_)
                                count += 1
                                logger.info(f"本日{bot}已預測{data['EventCode']}")
                                print("count : ",count)
                logging.shutdown()
                self.successful = True
                print("*********************Bot Predict CPBL successful!!*********************")  
            except Exception as e: 
                print(repr(e))
                print("機器人異常")
                
    def delete_log(self):
        print("*********************delete  before 7 days data start*********************")  
        try:
            lines = []
            date_before = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            already = os.path.exists(self.path)
            if already == False:
                create = open(self.path,"w")
                create.close()
            else:
                fo = open(self.path,"r+")
                for line in fo.readlines():
                    date = line.split(" ")[1]
                    if date >= date_before:
                        lines.append(line)
                fo.close()
                fo = open(self.path,"w+")
                fo.writelines(lines)
                fo.close()
            print("*********************delete  before 7 days data successful!!*********************")
        except Exception as e: 
            print(repr(e))
            print("*********************delete  before 7 days data fail!!*********************")
            
    def logfile(self,value,bot):
        read = open(self.path,"r+")
        for line in read:
            text = line.split(" ")[4]
            time = line.split(" ")[2]
            evencode = value["EventCode"].values[0]
            if bot in text and evencode in text and time < (datetime.datetime.now()- datetime.timedelta(minutes = 1)).strftime("%H:%M:%S,000"):
                print(f"{bot} 已經預測過{evencode}")
                read.close()
                return True
        return False
    
    def CPBL_predict(self):
        self.delete_log()
        self.successful = False
        self.update = False
        df_group = self.found()
        self.bot_predict(df_group)

if __name__ == '__main__':
    CPBLForecast = CPBLForecast()
    CPBLForecast.CPBL_predict()

