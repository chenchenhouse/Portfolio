import Bundesliga_Bot_Forecast as bbf
import CPBL_Bot_Forecast as cbf
import EPL_Bot_Forecast as ebf
import FIFA_Bot_Forecast as fifa
import LaLiga_Bot_Forecast as labf
import Ligue1_Bot_Forecast as libf
import LOLLPL_Bot_Forecast as lolbf
import MLB_Bot_Forecast as mlbf
import NBA_Bot_Forecast as nbabf
import NHL_Bot_Forecast as nhlbf
import SerieA_Bot_Forecast as sbf
import NPB_Bot_Forecast as npbbf
import WorldChampionshipQual2022_Bot_Forecast as wcqbf
import LOLMSI_Bot_Forecast as msi
import KBO_Bot_Forecast as kbo
import KLeague1_Bot_Forecast as kl1bf
import JLeague_Bot_Forecast as jlbf
import LOLS12_Bot_Forecast as S12

from time import sleep
import pandas
import numpy
import datetime

class ALL_Bot_Forecast(object):
    def All_bot_predict(self):
        try:
            # 機器人預測NBA
            NBAForecast = nbabf.NBAForecast()
            NBAForecast.NBA_predict()

            # 機器人預測MLB
            MLBForecast = mlbf.MLBForecast()
            MLBForecast.MLB_predict()

            # 機器人預測KBO
            KBOForecast = kbo.KBOForecast()
            KBOForecast.KBO_predict()

            # 機器人預測LOL MSI
            LOLMSIForecast = msi.LOLMSIForecast()
            LOLMSIForecast.LOLMSI_predict()

            # 機器人預測NPB
            NPBForecast = npbbf.NPBForecast()
            NPBForecast.NPB_predict()

            # 機器人預測EPL
            EPLForecast = ebf.EPLForecast()
            EPLForecast.EPL_predict()

            # 機器人預測EPL
            WorldCup2022Forecast = fifa.WorldCup2022Forecast()
            WorldCup2022Forecast.WorldCup2022_predict()

            # 機器人預測SerieA
            SerieAForecast = sbf.SerieAForecast()
            SerieAForecast.SerieA_predict()

            # 機器人預測LaLiga
            LaLigaForecast = labf.LaLigaForecast()
            LaLigaForecast.LaLiga_predict()

            # 機器人預測Bundesliga
            BundesligaForecast = bbf.BundesligaForecast()
            BundesligaForecast.Bundesliga_predict()

            # 機器人預測Ligue1
            Ligue1Forecast = libf.Ligue1Forecast()
            Ligue1Forecast.Ligue1_predict()

            # 機器人預測LOLLPL
            LOLLPLForecast = lolbf.LOLLPLForecast()
            LOLLPLForecast.LOLLPL_predict()

            # 機器人預測LOLMSI
            LOLMSIForecast = msi.LOLMSIForecast()
            LOLMSIForecast.LOLMSI_predict()

            # 機器人預測LOLS12
            LOLS12Forecast = S12.LOLS12Forecast()
            LOLS12Forecast.LOLS12_predict()


            # 機器人預測CPBL
            CPBLForecast = cbf.CPBLForecast()
            CPBLForecast.CPBL_predict()

            # 機器人預測NHL
            NHLForecast = nhlbf.NHLForecast()
            NHLForecast.NHL_predict()

            # 機器人預測KLeague1
            KLeague1Forecast = kl1bf.KLeague1Forecast()
            KLeague1Forecast.KLeague1_predict()

            # 機器人預測KLeague1
            J1LeagueForecast = jlbf.J1LeagueForecast()
            J1LeagueForecast.J1League_predict()


            #機器人預測WorldChampionshipQual2022
            WorldChampionshipQual2022Forecast = wcqbf.WorldChampionshipQual2022Forecast()
            WorldChampionshipQual2022Forecast.WorldChampionshipQual2022_predict()

        except Exception as e: 
            # 取得現在時間
            now = datetime.datetime.now()
            txt = '上次更新時間為：' + str(now) + str(repr(e))

            df = pandas.DataFrame([txt], index=['UpdateTime'])

            # 存出檔案
            df.to_csv(r'C:\Users\Guess365User\Bot Forecast\log.csv', header=False)
            print(repr(e))

        
        
if __name__ == '__main__':
    ALLForecast = ALL_Bot_Forecast()
    ALLForecast.All_bot_predict()


# In[ ]:




