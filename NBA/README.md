# Guess365 NBA預測機器人
製作日期 : 2022/3~2023/3   
製作人 : Rick

## 功能介紹與工具:
### (一)	功能介紹
本專案利用大量歷史NBA(美國職業籃球聯賽)賽事數據，搭配機器學習、深度學習等方式，進行比賽勝負之預測。  
歷史資料年份 : 2014-15~2021-22賽季  
實測年份 : 2022-23賽季  
模型 : FLAML AUTOML  
執行檔:
- 建模程式檔 : NBA預測模型建模_準確度74%獲利21W.ipynb(先發投手位置出錯)
- 修改建模程式檔 : 修改預測模型-先發投手位置問題.ipynb
-	NBA_30MIN_PREDICT.py : 開賽前21分鐘執行程式(為了抓取正確的先發名單)
-	NBA_UPDATE_PREDICT.py : 開賽前一天執行程式(先發名單為網站預估名單)
Excel檔 : 
-	predictdata2.xlsx : 與資料庫中NBA_BasicData資料內容相同，皆是爬蟲整理後組成為最終預測特徵的數據集
### (二)	使用工具與套件
-	Python3.9.12(Jupyter Notbook)
-	nest_asyncio 1.5.6
-	async-generator 1.10
-	pyppeteer  1.0.2
-	beautifulsoup4  4.12.2
-	lxml   4.9.2
-	pyquery 2.0.0
-	selenium 4.8.0
-	requests  2.29.0
-	pandas  1.5.3
-	joblib 1.1.1
-	json5   0.9.6
-	pickleshare 0.7.5
## 系統流程
### 一、	架構圖
透過爬取網路上NBA相關網站之資訊，並整理與統整數據後，搭配AUTOML模型進行賽事預測之運用。
   
![NBA架構圖](./photo/NBA架構圖.png)

# 模組元件功能說明
## 一、	特徵值
| 特徵名稱 |  介紹   |
|---------|---------|
|讓分| 讓分盤口之分水嶺| 
|總分| 總分盤口之分水嶺| 
|主勝(初)| 不讓分盤口之主隊初盤| 
|客勝(初)| 不讓分盤口之客隊初盤| 
|主勝率(初)| 不讓分盤口之主隊初盤勝率| 
|客勝率(初)| 不讓分盤口之客隊初盤勝率| 
|凱利指數(初)| 初盤賠率的期望收益與風險間的平衡點| 
|凱利指數(終)| 終盤賠率的期望收益與風險間的平衡點| 
|主勝(終)| 不讓分盤口之主隊終盤| 
|客勝(終)| 不讓分盤口之客隊終盤| 
|主勝率(終)| 不讓分盤口之主隊終盤勝率| 
|客勝率(終)| 不讓分盤口之客隊終盤勝率| 
|主勝(終)| 不讓分盤口之主隊終盤| 
|客勝(終)| 不讓分盤口之客隊終盤| 
|Away_game| 客隊本賽季賽事場數| 
|Away_win| 客隊本賽季獲勝場數| 
|Away_lose| 客隊本賽季敗北場數| 
|Away_win_score| 客隊本賽季獲勝時平均得分| 
|Away_lose_score| 客隊本賽季敗北時平均得分| 
|Away_net_score| 客隊平均淨得分| 
|Away_rank| 客隊本賽季戰績排行| 
|Away_win_rate| 客隊本賽季勝率| 
|Away_game_inhome| 客隊本賽季在主場賽事場數| 
|Away_win_inhome| 客隊本賽季主場獲勝場數| 
|Away_lose_inhome| 客隊本賽季主場敗北場數| 
|Away_win_score_inhome| 客隊本賽季主場獲勝時平均得分| 
|Away_lose_score_inhome| 客隊本賽季主場敗北時平均得分| 
|Away_net_score_inhome| 客隊主場平均淨得分| 
|Away_rank_inhome| 客隊本賽季主場戰績排行| 
|Away_win_rate_inhome| 客隊本賽季主場勝率| 
|Away_game_inaway| 客隊本賽季在客場賽事場數| 
|Away_win_inaway| 客隊本賽季客場獲勝場數| 
|Away_lose_inaway| 客隊本賽季客場敗北場數| 
|Away_win_score_inaway| 客隊本賽季客場獲勝時平均得分| 
|Away_lose_score_inaway| 客隊本賽季客場敗北時平均得分| 
|Away_net_score_inaway| 客隊客場平均淨得分| 
|Away_rank_inaway| 客隊本賽季客場戰績排行| 
|Away_win_rate_inaway| 客隊本賽季客場勝率| 
|Away_game_insix| 客隊本賽季在近6場賽事場數| 
|Away_win_insix| 客隊本賽季近6場獲勝場數| 
|Away_lose_insix| 客隊本賽季近6場敗北場數| 
|Away_win_score_insix| 客隊本賽季近6場獲勝時平均得分| 
|Away_lose_score_insix| 客隊本賽季近6場敗北時平均得分| 
|Away_net_score_insix| 客隊近6場平均淨得分| 
|Away_rank_insix| 客隊本賽季近6場戰績排行| 
|Away_win_rate_insix| 客隊本賽季近6場勝率| 
|Home_game| 主隊本賽季賽事場數| 
|Home_win| 主隊本賽季獲勝場數| 
|Home_lose| 主隊本賽季敗北場數| 
|Home_win_score| 主隊本賽季獲勝時平均得分| 
|Home_lose_score| 主隊本賽季敗北時平均得分| 
|Home_net_score| 主隊平均淨得分| 
|Home_rank| 主隊本賽季戰績排行| 
|Home_win_rate| 主隊本賽季勝率| 
|Home_game_inhome| 主隊本賽季在主場賽事場數| 
|Home_win_inhome| 主隊本賽季主場獲勝場數| 
|Home_lose_inhome| 主隊本賽季主場敗北場數| 
|Home_win_score_inhome| 主隊本賽季主場獲勝時平均得分| 
|Home_lose_score_inhome| 主隊本賽季主場敗北時平均得分| 
|Home_net_score_inhome| 主隊主場平均淨得分| 
|Home_rank_inhome| 主隊本賽季主場戰績排行| 
|Home_win_rate_inhome| 主隊本賽季主場勝率| 
|Home_game_inaway| 主隊本賽季在客場賽事場數| 
|Home_win_inaway| 主隊本賽季客場獲勝場數| 
|Home_lose_inaway| 主隊本賽季客場敗北場數| 
|Home_win_score_inaway| 主隊本賽季客場獲勝時平均得分| 
|Home_lose_score_inaway| 主隊本賽季客場敗北時平均得分| 
|Home_net_score_inaway| 主隊客場平均淨得分| 
|Home_rank_inaway| 主隊本賽季客場戰績排行| 
|Home_win_rate_inaway| 主隊本賽季客場勝率| 
|Home_game_insix| 主隊本賽季在近6場賽事場數| 
|Home_win_insix| 主隊本賽季近6場獲勝場數| 
|Home_lose_insix| 主隊本賽季近6場敗北場數| 
|Home_win_score_insix| 主隊本賽季近6場獲勝時平均得分| 
|Home_lose_score_insix| 主隊本賽季近6場敗北時平均得分| 
|Home_net_score_insix| 主隊近6場平均淨得分| 
|Home_rank_insix| 主隊本賽季近6場戰績排行| 
|Home_win_rate_insix| 主隊本賽季近6場勝率| 
|Both_battle| 雙方本賽季對戰勝率| 
|Away_battle| 客隊近10場勝率| 
|Home_battle| 主隊近10場勝率| 
|Home_Line1_inHome| 主隊近10場在主場第一節均得分| 
|Home_Line2_inHome| 主隊近10場在主場第二節均得分| 
|Home_Line3_inHome| 主隊近10場在主場第三節均得分| 
|Home_Line4_inHome| 主隊近10場在主場第四節均得分| 
|Home_Pace_inHome| 主隊近10場在主場有多少進攻回合| 
|Home_Total_FG_inHome| 主隊近10場在主場場均投籃命中次數| 
|Home_Total_FGA_inHome| 主隊近10場在主場場均投籃出手次數| 
|Home_Total_FG%_inHome| 主隊近10場在主場場均投籃命中比率| 
|Home_Total_3P_inHome| 主隊近10場在主場場均三分投籃命中次數| 
|Home_Total_3PA_inHome| 主隊近10場在主場場均三分投籃出手次數| 
|Home_Total_3P%_inHome| 主隊近10場在主場場均三分投籃命中比率| 
|Home_Total_FT_inHome| 主隊近10場在主場場均罰球命中次數| 
|Home_Total_FTA_inHome| 主隊近10場在主場場均罰球出手次數| 
|Home_Total_FT%_inHome| 主隊近10場在主場場均罰球命中率| 
|Home_Total_ORB_inHome| 主隊近10場在主場場均進攻籃板數| 
|Home_Total_DRB_inHome| 主隊近10場在主場場均防守籃板數| 
|Home_Total_TBR_inHome| 主隊近10場在主場場均總籃板數| 
|Home_Total_AST_inHome| 主隊近10場在主場場均助攻數| 
|Home_Total_STL_inHome| 主隊近10場在主場場均抄截數| 
|Home_Total_BLK_inHome| 主隊近10場在主場場均火鍋數| 
|Home_Total_TOV_inHome| 主隊近10場在主場場均失誤數| 
|Home_Total_PF_inHome| 主隊近10場在主場場均犯規數| 
|Home_Total_PTS_inHome| 主隊近10場在主場場均得分數| 
|Home_Total_TS%_inHome| 主隊近10場在主場場均真實投籃命中率| 
|Home_Total_eFG%_inHome| 主隊近10場在主場場均有效命中率| 
|Home_Total_3PAr_inHome| 主隊近10場在主場場均三分出手比率| 
|Home_Total_FTr_inHome| 主隊近10場在主場場均造犯規能力| 
|Home_Total_ORB%_inHome| 主隊近10場在主場場均進攻籃板比率| 
|Home_Total_DRB%_inHome| 主隊近10場在主場場均防守籃板比率| 
|Home_Total_TRB%_inHome| 主隊近10場在主場場均總籃板比率| 
|Home_Total_AST%_inHome| 主隊近10場在主場場均助攻比率| 
|Home_Total_STL%_inHome| 主隊近10場在主場場均抄截比率| 
|Home_Total_BLK%_inHome| 主隊近10場在主場場均火鍋比率| 
|Home_Total_TOV%_inHome| 主隊近10場在主場場均失誤比率| 
|Home_Total_ORtg_inHome| 主隊近10場在主場場均進攻效率| 
|Home_Total_DRtg_inHome| 主隊近10場在主場場均防守效率| 
|Home_Ties_inHome| 主隊近10場在主場場均平手次數| 
|Home_LeadChanges_inHome| 主隊近10場在主場場均交換領先次數| 
|Home_GameTied_inHome| 主隊近10場在主場場均平手時間(秒)| 
|Home_Led_inHome| 主隊近10場在主場場均領先時間(秒)| 
|Home_MCpoints_inHome| 主隊近10場在主場場均最大連續得分數| 
|Home_LSdrought_inHome| 主隊近10場在主場場均最久無得分時間(秒)| 
|Home_Line1_inAway| 主隊近10場在客場第一節均得分| 
|Home_Line2_inAway| 主隊近10場在客場第二節均得分| 
|Home_Line3_inAway| 主隊近10場在客場第三節均得分| 
|Home_Line4_inAway| 主隊近10場在客場第四節均得分| 
|Home_Pace_inAway| 主隊近10場在客場有多少進攻回合| 
|Home_Total_FG_inAway| 主隊近10場在客場場均投籃命中次數| 
|Home_Total_FGA_inAway| 主隊近10場在客場場均投籃出手次數| 
|Home_Total_FG%_inAway| 主隊近10場在客場場均投籃命中比率| 
|Home_Total_3P_inAway| 主隊近10場在客場場均三分投籃命中次數| 
|Home_Total_3PA_inAway| 主隊近10場在客場場均三分投籃出手次數| 
|Home_Total_3P%_inAway| 主隊近10場在客場場均三分投籃命中比率| 
|Home_Total_FT_inAway| 主隊近10場在客場場均罰球命中次數| 
|Home_Total_FTA_inAway| 主隊近10場在客場場均罰球出手次數| 
|Home_Total_FT%_inAway| 主隊近10場在客場場均罰球命中率| 
|Home_Total_ORB_inAway| 主隊近10場在客場場均進攻籃板數| 
|Home_Total_DRB_inAway| 主隊近10場在客場場均防守籃板數| 
|Home_Total_TBR_inAway| 主隊近10場在客場場均總籃板數| 
|Home_Total_AST_inAway| 主隊近10場在客場場均助攻數| 
|Home_Total_STL_inAway| 主隊近10場在客場場均抄截數| 
|Home_Total_BLK_inAway| 主隊近10場在客場場均火鍋數| 
|Home_Total_TOV_inAway| 主隊近10場在客場場均失誤數| 
|Home_Total_PF_inAway| 主隊近10場在客場場均犯規數| 
|Home_Total_PTS_inAway| 主隊近10場在客場場均得分數| 
|Home_Total_TS%_inAway| 主隊近10場在客場場均真實投籃命中率| 
|Home_Total_eFG%_inAway| 主隊近10場在客場場均有效命中率| 
|Home_Total_3PAr_inAway| 主隊近10場在客場場均三分出手比率| 
|Home_Total_FTr_inAway| 主隊近10場在客場場均造犯規能力| 
|Home_Total_ORB%_inAway| 主隊近10場在客場場均進攻籃板比率| 
|Home_Total_DRB%_inAway| 主隊近10場在客場場均防守籃板比率| 
|Home_Total_TRB%_inAway| 主隊近10場在客場場均總籃板比率| 
|Home_Total_AST%_inAway| 主隊近10場在客場場均助攻比率| 
|Home_Total_STL%_inAway| 主隊近10場在客場場均抄截比率| 
|Home_Total_BLK%_inAway| 主隊近10場在客場場均火鍋比率| 
|Home_Total_TOV%_inAway| 主隊近10場在客場場均失誤比率| 
|Home_Total_ORtg_inAway| 主隊近10場在客場場均進攻效率| 
|Home_Total_DRtg_inAway| 主隊近10場在客場場均防守效率| 
|Home_Ties_inAway| 主隊近10場在客場場均平手次數| 
|Home_LeadChanges_inAway| 主隊近10場在客場場均交換領先次數| 
|Home_GameTied_inAway| 主隊近10場在客場場均平手時間(秒)| 
|Home_Led_inAway| 主隊近10場在客場場均領先時間(秒)| 
|Home_MCpoints_inAway| 主隊近10場在客場場均最大連續得分數| 
|Home_LSdrought_inAway| 主隊近10場在客場場均最久無得分時間(秒)| 
|Home_Line1_inTotal| 主隊近10場總第一節均得分| 
|Home_Line2_inTotal| 主隊近10場總第二節均得分| 
|Home_Line3_inTotal| 主隊近10場總第三節均得分| 
|Home_Line4_inTotal| 主隊近10場總第四節均得分| 
|Home_Pace_inTotal| 主隊近10場總有多少進攻回合| 
|Home_Total_FG_inTotal| 主隊近10場總場均投籃命中次數| 
|Home_Total_FGA_inTotal| 主隊近10場總場均投籃出手次數| 
|Home_Total_FG%_inTotal| 主隊近10場總場均投籃命中比率| 
|Home_Total_3P_inTotal| 主隊近10場總場均三分投籃命中次數| 
|Home_Total_3PA_inTotal| 主隊近10場總場均三分投籃出手次數| 
|Home_Total_3P%_inTotal| 主隊近10場總場均三分投籃命中比率| 
|Home_Total_FT_inTotal| 主隊近10場總場均罰球命中次數| 
|Home_Total_FTA_inTotal| 主隊近10場總場均罰球出手次數| 
|Home_Total_FT%_inTotal| 主隊近10場總場均罰球命中率| 
|Home_Total_ORB_inTotal| 主隊近10場總場均進攻籃板數| 
|Home_Total_DRB_inTotal| 主隊近10場總場均防守籃板數| 
|Home_Total_TBR_inTotal| 主隊近10場總場均總籃板數| 
|Home_Total_AST_inTotal| 主隊近10場總場均助攻數| 
|Home_Total_STL_inTotal| 主隊近10場總場均抄截數| 
|Home_Total_BLK_inTotal| 主隊近10場總場均火鍋數| 
|Home_Total_TOV_inTotal| 主隊近10場總場均失誤數| 
|Home_Total_PF_inTotal| 主隊近10場總場均犯規數| 
|Home_Total_PTS_inTotal| 主隊近10場總場均得分數| 
|Home_Total_TS%_inTotal| 主隊近10場總場均真實投籃命中率| 
|Home_Total_eFG%_inTotal| 主隊近10場總場均有效命中率| 
|Home_Total_3PAr_inTotal| 主隊近10場總場均三分出手比率| 
|Home_Total_FTr_inTotal| 主隊近10場總場均造犯規能力| 
|Home_Total_ORB%_inTotal| 主隊近10場總場均進攻籃板比率| 
|Home_Total_DRB%_inTotal| 主隊近10場總場均防守籃板比率| 
|Home_Total_TRB%_inTotal| 主隊近10場總場均總籃板比率| 
|Home_Total_AST%_inTotal| 主隊近10場總場均助攻比率| 
|Home_Total_STL%_inTotal| 主隊近10場總場均抄截比率| 
|Home_Total_BLK%_inTotal| 主隊近10場總場均火鍋比率| 
|Home_Total_TOV%_inTotal| 主隊近10場總場均失誤比率| 
|Home_Total_ORtg_inTotal| 主隊近10場總場均進攻效率| 
|Home_Total_DRtg_inTotal| 主隊近10場總場均防守效率| 
|Home_Ties_inTotal| 主隊近10場總場均平手次數| 
|Home_LeadChanges_inTotal| 主隊近10場總場均交換領先次數| 
|Home_GameTied_inTotal| 主隊近10場總場均平手時間(秒)| 
|Home_Led_inTotal| 主隊近10場總場均領先時間(秒)| 
|Home_MCpoints_inTotal| 主隊近10場總場均最大連續得分數| 
|Home_LSdrought_inTotal| 主隊近10場總場均最久無得分時間(秒)| 
|Away_Line1_inHome| 客隊近10場在主場第一節均得分| 
|Away_Line2_inHome| 客隊近10場在主場第二節均得分| 
|Away_Line3_inHome| 客隊近10場在主場第三節均得分| 
|Away_Line4_inHome| 客隊近10場在主場第四節均得分| 
|Away_Pace_inHome| 客隊近10場在主場有多少進攻回合| 
|Away_Total_FG_inHome| 客隊近10場在主場場均投籃命中次數| 
|Away_Total_FGA_inHome| 客隊近10場在主場場均投籃出手次數| 
|Away_Total_FG%_inHome| 客隊近10場在主場場均投籃命中比率| 
|Away_Total_3P_inHome| 客隊近10場在主場場均三分投籃命中次數| 
|Away_Total_3PA_inHome| 客隊近10場在主場場均三分投籃出手次數| 
|Away_Total_3P%_inHome| 客隊近10場在主場場均三分投籃命中比率| 
|Away_Total_FT_inHome| 客隊近10場在主場場均罰球命中次數| 
|Away_Total_FTA_inHome| 客隊近10場在主場場均罰球出手次數| 
|Away_Total_FT%_inHome| 客隊近10場在主場場均罰球命中率| 
|Away_Total_ORB_inHome| 客隊近10場在主場場均進攻籃板數| 
|Away_Total_DRB_inHome| 客隊近10場在主場場均防守籃板數| 
|Away_Total_TBR_inHome| 客隊近10場在主場場均總籃板數| 
|Away_Total_AST_inHome| 客隊近10場在主場場均助攻數| 
|Away_Total_STL_inHome| 客隊近10場在主場場均抄截數| 
|Away_Total_BLK_inHome| 客隊近10場在主場場均火鍋數| 
|Away_Total_TOV_inHome| 客隊近10場在主場場均失誤數| 
|Away_Total_PF_inHome| 客隊近10場在主場場均犯規數| 
|Away_Total_PTS_inHome| 客隊近10場在主場場均得分數| 
|Away_Total_TS%_inHome| 客隊近10場在主場場均真實投籃命中率| 
|Away_Total_eFG%_inHome| 客隊近10場在主場場均有效命中率| 
|Away_Total_3PAr_inHome| 客隊近10場在主場場均三分出手比率| 
|Away_Total_FTr_inHome| 客隊近10場在主場場均造犯規能力| 
|Away_Total_ORB%_inHome| 客隊近10場在主場場均進攻籃板比率| 
|Away_Total_DRB%_inHome| 客隊近10場在主場場均防守籃板比率| 
|Away_Total_TRB%_inHome| 客隊近10場在主場場均總籃板比率| 
|Away_Total_AST%_inHome| 客隊近10場在主場場均助攻比率| 
|Away_Total_STL%_inHome| 客隊近10場在主場場均抄截比率| 
|Away_Total_BLK%_inHome| 客隊近10場在主場場均火鍋比率| 
|Away_Total_TOV%_inHome| 客隊近10場在主場場均失誤比率| 
|Away_Total_ORtg_inHome| 客隊近10場在主場場均進攻效率| 
|Away_Total_DRtg_inHome| 客隊近10場在主場場均防守效率| 
|Away_Ties_inHome| 客隊近10場在主場場均平手次數| 
|Away_LeadChanges_inHome| 客隊近10場在主場場均交換領先次數| 
|Away_GameTied_inHome| 客隊近10場在主場場均平手時間(秒)| 
|Away_Led_inHome| 客隊近10場在主場場均領先時間(秒)| 
|Away_MCpoints_inHome| 客隊近10場在主場場均最大連續得分數| 
|Away_LSdrought_inHome| 客隊近10場在主場場均最久無得分時間(秒)| 
|Away_Line1_inAway| 客隊近10場在客場第一節均得分| 
|Away_Line2_inAway| 客隊近10場在客場第二節均得分| 
|Away_Line3_inAway| 客隊近10場在客場第三節均得分| 
|Away_Line4_inAway| 客隊近10場在客場第四節均得分| 
|Away_Pace_inAway| 客隊近10場在客場有多少進攻回合| 
|Away_Total_FG_inAway| 客隊近10場在客場場均投籃命中次數| 
|Away_Total_FGA_inAway| 客隊近10場在客場場均投籃出手次數| 
|Away_Total_FG%_inAway| 客隊近10場在客場場均投籃命中比率| 
|Away_Total_3P_inAway| 客隊近10場在客場場均三分投籃命中次數| 
|Away_Total_3PA_inAway| 客隊近10場在客場場均三分投籃出手次數| 
|Away_Total_3P%_inAway| 客隊近10場在客場場均三分投籃命中比率| 
|Away_Total_FT_inAway| 客隊近10場在客場場均罰球命中次數| 
|Away_Total_FTA_inAway| 客隊近10場在客場場均罰球出手次數| 
|Away_Total_FT%_inAway| 客隊近10場在客場場均罰球命中率| 
|Away_Total_ORB_inAway| 客隊近10場在客場場均進攻籃板數| 
|Away_Total_DRB_inAway| 客隊近10場在客場場均防守籃板數| 
|Away_Total_TBR_inAway| 客隊近10場在客場場均總籃板數| 
|Away_Total_AST_inAway| 客隊近10場在客場場均助攻數| 
|Away_Total_STL_inAway| 客隊近10場在客場場均抄截數| 
|Away_Total_BLK_inAway| 客隊近10場在客場場均火鍋數| 
|Away_Total_TOV_inAway| 客隊近10場在客場場均失誤數| 
|Away_Total_PF_inAway| 客隊近10場在客場場均犯規數| 
|Away_Total_PTS_inAway| 客隊近10場在客場場均得分數| 
|Away_Total_TS%_inAway| 客隊近10場在客場場均真實投籃命中率| 
|Away_Total_eFG%_inAway| 客隊近10場在客場場均有效命中率| 
|Away_Total_3PAr_inAway| 客隊近10場在客場場均三分出手比率| 
|Away_Total_FTr_inAway| 客隊近10場在客場場均造犯規能力| 
|Away_Total_ORB%_inAway| 客隊近10場在客場場均進攻籃板比率| 
|Away_Total_DRB%_inAway| 客隊近10場在客場場均防守籃板比率| 
|Away_Total_TRB%_inAway| 客隊近10場在客場場均總籃板比率| 
|Away_Total_AST%_inAway| 客隊近10場在客場場均助攻比率| 
|Away_Total_STL%_inAway| 客隊近10場在客場場均抄截比率| 
|Away_Total_BLK%_inAway| 客隊近10場在客場場均火鍋比率| 
|Away_Total_TOV%_inAway| 客隊近10場在客場場均失誤比率| 
|Away_Total_ORtg_inAway| 客隊近10場在客場場均進攻效率| 
|Away_Total_DRtg_inAway| 客隊近10場在客場場均防守效率| 
|Away_Ties_inAway| 客隊近10場在客場場均平手次數| 
|Away_LeadChanges_inAway| 客隊近10場在客場場均交換領先次數| 
|Away_GameTied_inAway| 客隊近10場在客場場均平手時間(秒)| 
|Away_Led_inAway| 客隊近10場在客場場均領先時間(秒)| 
|Away_MCpoints_inAway| 客隊近10場在客場場均最大連續得分數| 
|Away_LSdrought_inAway| 客隊近10場在客場場均最久無得分時間(秒)| 
|Away_Line1_inTotal| 客隊近10場總第一節均得分| 
|Away_Line2_inTotal| 客隊近10場總第二節均得分| 
|Away_Line3_inTotal| 客隊近10場總第三節均得分| 
|Away_Line4_inTotal| 客隊近10場總第四節均得分| 
|Away_Pace_inTotal| 客隊近10場總有多少進攻回合| 
|Away_Total_FG_inTotal| 客隊近10場總場均投籃命中次數| 
|Away_Total_FGA_inTotal| 客隊近10場總場均投籃出手次數| 
|Away_Total_FG%_inTotal| 客隊近10場總場均投籃命中比率| 
|Away_Total_3P_inTotal| 客隊近10場總場均三分投籃命中次數| 
|Away_Total_3PA_inTotal| 客隊近10場總場均三分投籃出手次數| 
|Away_Total_3P%_inTotal| 客隊近10場總場均三分投籃命中比率| 
|Away_Total_FT_inTotal| 客隊近10場總場均罰球命中次數| 
|Away_Total_FTA_inTotal| 客隊近10場總場均罰球出手次數| 
|Away_Total_FT%_inTotal| 客隊近10場總場均罰球命中率| 
|Away_Total_ORB_inTotal| 客隊近10場總場均進攻籃板數| 
|Away_Total_DRB_inTotal| 客隊近10場總場均防守籃板數| 
|Away_Total_TBR_inTotal| 客隊近10場總場均總籃板數| 
|Away_Total_AST_inTotal| 客隊近10場總場均助攻數| 
|Away_Total_STL_inTotal| 客隊近10場總場均抄截數| 
|Away_Total_BLK_inTotal| 客隊近10場總場均火鍋數| 
|Away_Total_TOV_inTotal| 客隊近10場總場均失誤數| 
|Away_Total_PF_inTotal| 客隊近10場總場均犯規數| 
|Away_Total_PTS_inTotal| 客隊近10場總場均得分數| 
|Away_Total_TS%_inTotal| 客隊近10場總場均真實投籃命中率| 
|Away_Total_eFG%_inTotal| 客隊近10場總場均有效命中率| 
|Away_Total_3PAr_inTotal| 客隊近10場總場均三分出手比率| 
|Away_Total_FTr_inTotal| 客隊近10場總場均造犯規能力| 
|Away_Total_ORB%_inTotal| 客隊近10場總場均進攻籃板比率| 
|Away_Total_DRB%_inTotal| 客隊近10場總場均防守籃板比率| 
|Away_Total_TRB%_inTotal| 客隊近10場總場均總籃板比率| 
|Away_Total_AST%_inTotal| 客隊近10場總場均助攻比率| 
|Away_Total_STL%_inTotal| 客隊近10場總場均抄截比率| 
|Away_Total_BLK%_inTotal| 客隊近10場總場均火鍋比率| 
|Away_Total_TOV%_inTotal| 客隊近10場總場均失誤比率| 
|Away_Total_ORtg_inTotal| 客隊近10場總場均進攻效率| 
|Away_Total_DRtg_inTotal| 客隊近10場總場均防守效率| 
|Away_Ties_inTotal| 客隊近10場總場均平手次數| 
|Away_LeadChanges_inTotal| 主隊近10場總場均交換領先次數| 
|Away_GameTied_inTotal| 主隊近10場總場均平手時間(秒)| 
|Away_Led_inTotal| 主隊近10場總場均領先時間(秒)| 
|Away_MCpoints_inTotal| 主隊近10場總場均最大連續得分數| 
|Away_LSdrought_inTotal| 主隊近10場總場均最久無得分時間(秒)| 
|Home_starters1_PointDiff| 主隊先發球員1近10場場均上場時兩隊分差| 
|Home_starters1_Game_Start| 主隊先發球員1近10場場均先發次數| 
|Home_starters1_Minutes| 主隊先發球員1近10場場均上場時間| 
|Home_starters1_FG| 主隊先發球員1近10場場均投籃命中數| 
|Home_starters1_FGA| 主隊先發球員1近10場場均投籃出手數| 
|Home_starters1_FG_P| 主隊先發球員1近10場場均投籃命中率| 
|Home_starters1_P3| 主隊先發球員1近10場場均三分命中數| 
|Home_starters1_P3A| 主隊先發球員1近10場場均三分出手數| 
|Home_starters1_P3_P| 主隊先發球員1近10場場均三分命中率| 
|Home_starters1_FT| 主隊先發球員1近10場場均罰球命中數| 
|Home_starters1_FTA| 主隊先發球員1近10場場均罰球出手數| 
|Home_starters1_FT_P| 主隊先發球員1近10場場均罰球命中率| 
|Home_starters1_ORB| 主隊先發球員1近10場場均進攻籃板數| 
|Home_starters1_TRB| 主隊先發球員1近10場場均總籃板數| 
|Home_starters1_AST| 主隊先發球員1近10場場均助攻數| 
|Home_starters1_STL| 主隊先發球員1近10場場均抄截數| 
|Home_starters1_BLK| 主隊先發球員1近10場場均火鍋數| 
|Home_starters1_TOV| 主隊先發球員1近10場場均失誤數| 
|Home_starters1_PF| 主隊先發球員1近10場場均罰球數| 
|Home_starters1_PTS| 主隊先發球員1近10場場均得分| 
|Home_starters1_Game_Score| 主隊先發球員1近10場場均全面得分| 
|Home_starters1_+/-| 主隊先發球員1近10場場均正負值| 
|Home_starters1_noplay_PointDiff| 主隊先發球員2近10場場均無上場兩隊分差| 
|Home_starters2_PointDiff| 主隊先發球員2近10場場均上場時兩隊分差| 
|Home_starters2_Game_Start| 主隊先發球員2近10場場均先發次數| 
|Home_starters2_Minutes| 主隊先發球員2近10場場均上場時間| 
|Home_starters2_FG| 主隊先發球員2近10場場均投籃命中數| 
|Home_starters2_FGA| 主隊先發球員2近10場場均投籃出手數| 
|Home_starters2_FG_P| 主隊先發球員2近10場場均投籃命中率| 
|Home_starters2_P3| 主隊先發球員2近10場場均三分命中數| 
|Home_starters2_P3A| 主隊先發球員2近10場場均三分出手數| 
|Home_starters2_P3_P| 主隊先發球員2近10場場均三分命中率| 
|Home_starters2_FT| 主隊先發球員2近10場場均罰球命中數| 
|Home_starters2_FTA| 主隊先發球員2近10場場均罰球出手數| 
|Home_starters2_FT_P| 主隊先發球員2近10場場均罰球命中率| 
|Home_starters2_ORB| 主隊先發球員2近10場場均進攻籃板數| 
|Home_starters2_TRB| 主隊先發球員2近10場場均總籃板數| 
|Home_starters2_AST| 主隊先發球員2近10場場均助攻數| 
|Home_starters2_STL| 主隊先發球員2近10場場均抄截數| 
|Home_starters2_BLK| 主隊先發球員2近10場場均火鍋數| 
|Home_starters2_TOV| 主隊先發球員2近10場場均失誤數| 
|Home_starters2_PF| 主隊先發球員2近10場場均罰球數| 
|Home_starters2_PTS| 主隊先發球員2近10場場均得分| 
|Home_starters2_Game_Score| 主隊先發球員2近10場場均全面得分| 
|Home_starters2_+/-| 主隊先發球員2近10場場均正負值| 
|Home_starters2_noplay_PointDiff| 主隊先發球員2近10場場均無上場兩隊分差|
|Home_starters3_PointDiff| 主隊先發球員3近10場場均上場時兩隊分差| 
|Home_starters3_Game_Start| 主隊先發球員3近10場場均先發次數| 
|Home_starters3_Minutes| 主隊先發球員3近10場場均上場時間| 
|Home_starters3_FG| 主隊先發球員3近10場場均投籃命中數| 
|Home_starters3_FGA| 主隊先發球員3近10場場均投籃出手數| 
|Home_starters3_FG_P| 主隊先發球員3近10場場均投籃命中率| 
|Home_starters3_P3| 主隊先發球員3近10場場均三分命中數| 
|Home_starters3_P3A| 主隊先發球員3近10場場均三分出手數| 
|Home_starters3_P3_P| 主隊先發球員3近10場場均三分命中率| 
|Home_starters3_FT| 主隊先發球員3近10場場均罰球命中數| 
|Home_starters3_FTA| 主隊先發球員3近10場場均罰球出手數| 
|Home_starters3_FT_P| 主隊先發球員3近10場場均罰球命中率| 
|Home_starters3_ORB| 主隊先發球員3近10場場均進攻籃板數| 
|Home_starters3_TRB| 主隊先發球員3近10場場均總籃板數| 
|Home_starters3_AST| 主隊先發球員3近10場場均助攻數| 
|Home_starters3_STL| 主隊先發球員3近10場場均抄截數| 
|Home_starters3_BLK| 主隊先發球員3近10場場均火鍋數| 
|Home_starters3_TOV| 主隊先發球員3近10場場均失誤數| 
|Home_starters3_PF| 主隊先發球員3近10場場均罰球數| 
|Home_starters3_PTS| 主隊先發球員3近10場場均得分| 
|Home_starters3_Game_Score| 主隊先發球員3近10場場均全面得分| 
|Home_starters3_+/-| 主隊先發球員3近10場場均正負值| 
|Home_starters3_noplay_PointDiff| 主隊先發球員3近10場場均無上場兩隊分差|
|Home_starters4_PointDiff| 主隊先發球員4近10場場均上場時兩隊分差| 
|Home_starters4_Game_Start| 主隊先發球員4近10場場均先發次數| 
|Home_starters4_Minutes| 主隊先發球員4近10場場均上場時間| 
|Home_starters4_FG| 主隊先發球員4近10場場均投籃命中數| 
|Home_starters4_FGA| 主隊先發球員4近10場場均投籃出手數| 
|Home_starters4_FG_P| 主隊先發球員4近10場場均投籃命中率| 
|Home_starters4_P3| 主隊先發球員4近10場場均三分命中數| 
|Home_starters4_P3A| 主隊先發球員4近10場場均三分出手數| 
|Home_starters4_P3_P| 主隊先發球員4近10場場均三分命中率| 
|Home_starters4_FT| 主隊先發球員4近10場場均罰球命中數| 
|Home_starters4_FTA| 主隊先發球員4近10場場均罰球出手數| 
|Home_starters4_FT_P| 主隊先發球員4近10場場均罰球命中率| 
|Home_starters4_ORB| 主隊先發球員4近10場場均進攻籃板數| 
|Home_starters4_TRB| 主隊先發球員4近10場場均總籃板數| 
|Home_starters4_AST| 主隊先發球員4近10場場均助攻數| 
|Home_starters4_STL| 主隊先發球員4近10場場均抄截數| 
|Home_starters4_BLK| 主隊先發球員4近10場場均火鍋數| 
|Home_starters4_TOV| 主隊先發球員4近10場場均失誤數| 
|Home_starters4_PF| 主隊先發球員4近10場場均罰球數| 
|Home_starters4_PTS| 主隊先發球員4近10場場均得分| 
|Home_starters4_Game_Score| 主隊先發球員4近10場場均全面得分| 
|Home_starters4_+/-| 主隊先發球員4近10場場均正負值| 
|Home_starters4_noplay_PointDiff| 主隊先發球員4近10場場均無上場兩隊分差|
|Home_starters5_PointDiff| 主隊先發球員5近10場場均上場時兩隊分差| 
|Home_starters5_Game_Start| 主隊先發球員5近10場場均先發次數| 
|Home_starters5_Minutes| 主隊先發球員5近10場場均上場時間| 
|Home_starters5_FG| 主隊先發球員5近10場場均投籃命中數| 
|Home_starters5_FGA| 主隊先發球員5近10場場均投籃出手數| 
|Home_starters5_FG_P| 主隊先發球員5近10場場均投籃命中率| 
|Home_starters5_P3| 主隊先發球員5近10場場均三分命中數| 
|Home_starters5_P3A| 主隊先發球員5近10場場均三分出手數| 
|Home_starters5_P3_P| 主隊先發球員5近10場場均三分命中率| 
|Home_starters5_FT| 主隊先發球員5近10場場均罰球命中數| 
|Home_starters5_FTA| 主隊先發球員5近10場場均罰球出手數| 
|Home_starters5_FT_P| 主隊先發球員5近10場場均罰球命中率| 
|Home_starters5_ORB| 主隊先發球員5近10場場均進攻籃板數| 
|Home_starters5_TRB| 主隊先發球員5近10場場均總籃板數| 
|Home_starters5_AST| 主隊先發球員5近10場場均助攻數| 
|Home_starters5_STL| 主隊先發球員5近10場場均抄截數| 
|Home_starters5_BLK| 主隊先發球員5近10場場均火鍋數| 
|Home_starters5_TOV| 主隊先發球員5近10場場均失誤數| 
|Home_starters5_PF| 主隊先發球員5近10場場均罰球數| 
|Home_starters5_PTS| 主隊先發球員5近10場場均得分| 
|Home_starters5_Game_Score| 主隊先發球員5近10場場均全面得分| 
|Home_starters5_+/-| 主隊先發球員5近10場場均正負值| 
|Home_starters5_noplay_PointDiff| 主隊先發球員5近10場場均無上場兩隊分差|
|Away_starters1_PointDiff| 主隊先發球員1近10場場均上場時兩隊分差| 
|Away_starters1_Game_Start| 主隊先發球員1近10場場均先發次數| 
|Away_starters1_Minutes| 主隊先發球員1近10場場均上場時間| 
|Away_starters1_FG| 主隊先發球員1近10場場均投籃命中數| 
|Away_starters1_FGA| 主隊先發球員1近10場場均投籃出手數| 
|Away_starters1_FG_P| 主隊先發球員1近10場場均投籃命中率| 
|Away_starters1_P3| 主隊先發球員1近10場場均三分命中數| 
|Away_starters1_P3A| 主隊先發球員1近10場場均三分出手數| 
|Away_starters1_P3_P| 主隊先發球員1近10場場均三分命中率| 
|Away_starters1_FT| 主隊先發球員1近10場場均罰球命中數| 
|Away_starters1_FTA| 主隊先發球員1近10場場均罰球出手數| 
|Away_starters1_FT_P| 主隊先發球員1近10場場均罰球命中率| 
|Away_starters1_ORB| 主隊先發球員1近10場場均進攻籃板數| 
|Away_starters1_TRB| 主隊先發球員1近10場場均總籃板數| 
|Away_starters1_AST| 主隊先發球員1近10場場均助攻數| 
|Away_starters1_STL| 主隊先發球員1近10場場均抄截數| 
|Away_starters1_BLK| 主隊先發球員1近10場場均火鍋數| 
|Away_starters1_TOV| 主隊先發球員1近10場場均失誤數| 
|Away_starters1_PF| 主隊先發球員1近10場場均罰球數| 
|Away_starters1_PTS| 主隊先發球員1近10場場均得分| 
|Away_starters1_Game_Score| 主隊先發球員1近10場場均全面得分| 
|Away_starters1_+/-| 主隊先發球員1近10場場均正負值| 
|Away_starters1_noplay_PointDiff| 主隊先發球員2近10場場均無上場兩隊分差| 
|Away_starters2_PointDiff| 主隊先發球員2近10場場均上場時兩隊分差| 
|Away_starters2_Game_Start| 主隊先發球員2近10場場均先發次數| 
|Away_starters2_Minutes| 主隊先發球員2近10場場均上場時間| 
|Away_starters2_FG| 主隊先發球員2近10場場均投籃命中數| 
|Away_starters2_FGA| 主隊先發球員2近10場場均投籃出手數| 
|Away_starters2_FG_P| 主隊先發球員2近10場場均投籃命中率| 
|Away_starters2_P3| 主隊先發球員2近10場場均三分命中數| 
|Away_starters2_P3A| 主隊先發球員2近10場場均三分出手數| 
|Away_starters2_P3_P| 主隊先發球員2近10場場均三分命中率| 
|Away_starters2_FT| 主隊先發球員2近10場場均罰球命中數| 
|Away_starters2_FTA| 主隊先發球員2近10場場均罰球出手數| 
|Away_starters2_FT_P| 主隊先發球員2近10場場均罰球命中率| 
|Away_starters2_ORB| 主隊先發球員2近10場場均進攻籃板數| 
|Away_starters2_TRB| 主隊先發球員2近10場場均總籃板數| 
|Away_starters2_AST| 主隊先發球員2近10場場均助攻數| 
|Away_starters2_STL| 主隊先發球員2近10場場均抄截數| 
|Away_starters2_BLK| 主隊先發球員2近10場場均火鍋數| 
|Away_starters2_TOV| 主隊先發球員2近10場場均失誤數| 
|Away_starters2_PF| 主隊先發球員2近10場場均罰球數| 
|Away_starters2_PTS| 主隊先發球員2近10場場均得分| 
|Away_starters2_Game_Score| 主隊先發球員2近10場場均全面得分| 
|Away_starters2_+/-| 主隊先發球員2近10場場均正負值| 
|Away_starters2_noplay_PointDiff| 主隊先發球員2近10場場均無上場兩隊分差|
|Away_starters3_PointDiff| 主隊先發球員3近10場場均上場時兩隊分差| 
|Away_starters3_Game_Start| 主隊先發球員3近10場場均先發次數| 
|Away_starters3_Minutes| 主隊先發球員3近10場場均上場時間| 
|Away_starters3_FG| 主隊先發球員3近10場場均投籃命中數| 
|Away_starters3_FGA| 主隊先發球員3近10場場均投籃出手數| 
|Away_starters3_FG_P| 主隊先發球員3近10場場均投籃命中率| 
|Away_starters3_P3| 主隊先發球員3近10場場均三分命中數| 
|Away_starters3_P3A| 主隊先發球員3近10場場均三分出手數| 
|Away_starters3_P3_P| 主隊先發球員3近10場場均三分命中率| 
|Away_starters3_FT| 主隊先發球員3近10場場均罰球命中數| 
|Away_starters3_FTA| 主隊先發球員3近10場場均罰球出手數| 
|Away_starters3_FT_P| 主隊先發球員3近10場場均罰球命中率| 
|Away_starters3_ORB| 主隊先發球員3近10場場均進攻籃板數| 
|Away_starters3_TRB| 主隊先發球員3近10場場均總籃板數| 
|Away_starters3_AST| 主隊先發球員3近10場場均助攻數| 
|Away_starters3_STL| 主隊先發球員3近10場場均抄截數| 
|Away_starters3_BLK| 主隊先發球員3近10場場均火鍋數| 
|Away_starters3_TOV| 主隊先發球員3近10場場均失誤數| 
|Away_starters3_PF| 主隊先發球員3近10場場均罰球數| 
|Away_starters3_PTS| 主隊先發球員3近10場場均得分| 
|Away_starters3_Game_Score| 主隊先發球員3近10場場均全面得分| 
|Away_starters3_+/-| 主隊先發球員3近10場場均正負值| 
|Away_starters3_noplay_PointDiff| 主隊先發球員3近10場場均無上場兩隊分差|
|Away_starters4_PointDiff| 主隊先發球員4近10場場均上場時兩隊分差| 
|Away_starters4_Game_Start| 主隊先發球員4近10場場均先發次數| 
|Away_starters4_Minutes| 主隊先發球員4近10場場均上場時間| 
|Away_starters4_FG| 主隊先發球員4近10場場均投籃命中數| 
|Away_starters4_FGA| 主隊先發球員4近10場場均投籃出手數| 
|Away_starters4_FG_P| 主隊先發球員4近10場場均投籃命中率| 
|Away_starters4_P3| 主隊先發球員4近10場場均三分命中數| 
|Away_starters4_P3A| 主隊先發球員4近10場場均三分出手數| 
|Away_starters4_P3_P| 主隊先發球員4近10場場均三分命中率| 
|Away_starters4_FT| 主隊先發球員4近10場場均罰球命中數| 
|Away_starters4_FTA| 主隊先發球員4近10場場均罰球出手數| 
|Away_starters4_FT_P| 主隊先發球員4近10場場均罰球命中率| 
|Away_starters4_ORB| 主隊先發球員4近10場場均進攻籃板數| 
|Away_starters4_TRB| 主隊先發球員4近10場場均總籃板數| 
|Away_starters4_AST| 主隊先發球員4近10場場均助攻數| 
|Away_starters4_STL| 主隊先發球員4近10場場均抄截數| 
|Away_starters4_BLK| 主隊先發球員4近10場場均火鍋數| 
|Away_starters4_TOV| 主隊先發球員4近10場場均失誤數| 
|Away_starters4_PF| 主隊先發球員4近10場場均罰球數| 
|Away_starters4_PTS| 主隊先發球員4近10場場均得分| 
|Away_starters4_Game_Score| 主隊先發球員4近10場場均全面得分| 
|Away_starters4_+/-| 主隊先發球員4近10場場均正負值| 
|Away_starters4_noplay_PointDiff| 主隊先發球員4近10場場均無上場兩隊分差|
|Away_starters5_PointDiff| 主隊先發球員5近10場場均上場時兩隊分差| 
|Away_starters5_Game_Start| 主隊先發球員5近10場場均先發次數| 
|Away_starters5_Minutes| 主隊先發球員5近10場場均上場時間| 
|Away_starters5_FG| 主隊先發球員5近10場場均投籃命中數| 
|Away_starters5_FGA| 主隊先發球員5近10場場均投籃出手數| 
|Away_starters5_FG_P| 主隊先發球員5近10場場均投籃命中率| 
|Away_starters5_P3| 主隊先發球員5近10場場均三分命中數| 
|Away_starters5_P3A| 主隊先發球員5近10場場均三分出手數| 
|Away_starters5_P3_P| 主隊先發球員5近10場場均三分命中率| 
|Away_starters5_FT| 主隊先發球員5近10場場均罰球命中數| 
|Away_starters5_FTA| 主隊先發球員5近10場場均罰球出手數| 
|Away_starters5_FT_P| 主隊先發球員5近10場場均罰球命中率| 
|Away_starters5_ORB| 主隊先發球員5近10場場均進攻籃板數| 
|Away_starters5_TRB| 主隊先發球員5近10場場均總籃板數| 
|Away_starters5_AST| 主隊先發球員5近10場場均助攻數| 
|Away_starters5_STL| 主隊先發球員5近10場場均抄截數| 
|Away_starters5_BLK| 主隊先發球員5近10場場均火鍋數| 
|Away_starters5_TOV| 主隊先發球員5近10場場均失誤數| 
|Away_starters5_PF| 主隊先發球員5近10場場均罰球數| 
|Away_starters5_PTS| 主隊先發球員5近10場場均得分| 
|Away_starters5_Game_Score| 主隊先發球員5近10場場均全面得分| 
|Away_starters5_+/-| 主隊先發球員5近10場場均正負值| 
|Away_starters5_noplay_PointDiff| 主隊先發球員5近10場場均無上場兩隊分差|
|客隊ELO| 客隊計算球隊未來比賽的勝率評分| 
|主隊ELO| 主隊計算球隊未來比賽的勝率評分| 
|Home_startersAll_+/-| 主隊全隊近10場場均正負值| 
|Away_startersAll_+/-| 客隊全隊近10場場均正負值|

## 二、	自訂函式
### 1.	函數名稱 : schedule()
-	函數功能 : 抓取Basketball reference的賽程
-	儲存檔 : /sch.xlsx
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置
### 2.	函數名稱 : linepoint()
-	參數 : df_b – schedule()中預測日前一日已完賽事
-	函數功能 : 抓取Basketball reference的每場賽事的基本數據
-	儲存檔 : /boxscore_all.xlsx
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置
### 3.	函數名稱 : scorechange()
-	參數 : df_b – schedule()中預測日前一日已完賽事
-	函數功能 : 抓取Basketball reference的每場賽事的得分狀況
-	儲存檔 : /all_game.xlsx
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置
### 4.	函數名稱 : odds_sch()
-	函數功能 : 抓取球探網每場賽事的賽程
-	儲存檔 : /odds_sch.xlsx
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置	
### 5.	函數名稱 : battlegame()
-	參數 : odds_sch - odds_sch()中抓取的賽程
-	函數功能 : 抓取球探網每場賽事的雙方對戰狀況
-	儲存檔 : /odds_rank.xlsx
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置
### 6.	函數名稱 : odds()
-	參數 : odds_sch - odds_sch()中抓取的賽程
-	函數功能 : 抓取球探網每場賽事的各家莊家平均不讓分賠率
-	儲存檔 : /odds_all.xlsx
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置
### 7.	函數名稱 : check_odds()
-	參數 : odds_all - odds()中抓取的莊家平均不讓分賠率
-	函數功能 : 抓取球探網每場賽事的莊家36*或易*讓分跟總分的分水嶺
-	儲存檔 : /odds_hand_over.xlsx
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置
### 8.	函數名稱 : before_data()
-	參數 : o_sch_all – basketball reference抓取的數據  
         odds_all - 球探網抓取的數據
-	函數功能 : 計算每筆數據前10場的平均，因避免使用到當場數據，造成資料窺視問題
-	儲存檔 : /basebefore10.xlsx
### 9.	函數名稱 : Lineups ()
-	函數功能 : 抓取rotowire網站中的先發球員名單
-	儲存檔 : /player.xlsx
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置
### 10.	函數名稱 : crawler_player()
-	參數 : df_player – Lineups()中抓取的先發球員
-	函數功能 : 比對rotoeire跟reference中的隊員名稱
-	儲存檔 : /player_changename.xlsx
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置
### 11.	函數名稱 : change_playername()
-	參數 : df_player – Lineups()中抓取的先發球員  
        player_event - crawler_player()中比對球員的名稱
-	函數功能 : 變更每筆數據的球員名稱與eventcode
### 12.	函數名稱 : update_player()
-	參數 : player_event – crawler_player()中比對球員的名稱
-	函數功能 : 更新先發球員數據
-	儲存檔 : /player_game/各球員的xlsx檔
-	注意事項 : callurl_and_getdata()中start_parm中executablePath更改為chrome.exe的檔案位置
### 13.	函數名稱 : change_playerposition()
-	參數 : player_event – change_playername ()中更改球員名稱后的每場資料
-	函數功能 : 更改先發球員順序，按照過去10場平均上場時間多至少進行排序
-	儲存檔 : /starts.xlsx
### 14.	函數名稱 : player_before()
-	參數 : odd -先發選手歷史數據
-	函數功能 : 計算先發選手過去10場賽事數據平均
-	儲存檔 : /basebefore10start.xlsx
### 15.	函數名稱 : data_merge ()
-	參數 : odd -先發選手歷史數據
-	函數功能 : 合併先前處理好的數據
-	儲存檔 : /df_all1.xlsx
### 16.	函數名稱 : update_elo ()
-	參數 : df -過去比賽的數據
-	函數功能 : 計算並更新各球隊最新的ELO
-	儲存檔 : / elo_n.xlsx
### 17.	函數名稱 : elo ()
-	參數 : ELO_first – 最新各隊ELO  
        df_elo – 過去球隊ELO數據  
        df_all2 – 整理好的每場數據  
-	函數功能 : 將要預測的賽事填上最新的各隊ELO數據

## 三、	自訂模組
### 1.	模組名稱 : nba_flaml_73%_scaler20230316.model
-	模組介紹 : 特徵標準化轉換
### 2.	模組名稱 : nba_flaml_73%20230316.pkl
-	模組介紹 : 利用FLAML中的AUTOML製作出的預測模型
-	程式碼 : 
```python
from flaml import AutoML
clf = AutoML()
automl_settings = {
  "time_budget": 1,  # in seconds
  "metric": 'accuracy',
  "task": 'classification',
  "log_file_name": "iris.log",
  "time_budget" : 600
	}	
clf.fit(X_train = df_x_train_mm, y_train = y_train,
	        X_val = df_x_val_mm,y_val = y_val,
	        **automl_settings)
```

## 四、	預測API 
```python
url =f'https://{domain_name}/UserMemberSellingPushMessage'
json_= {"SubscribeLevels":"free/NBA",     *推送等級
        "predict_winrate":"58.7%", 
        "title":"本季準確度 : ",
        "body_data":"2021賽季回測|39050|852過500|58.7%",
        "TournamentText_icon":"https://i.imgur.com/4YeALVb.jpeg",
        "body_image":"https://i.imgur.com/w4MQwdZ.png",
        "predlist":predlist,
       "connect":False,
        "banner":"NBA"}
response = requests.post(url, json = json_, auth=HTTPBasicAuth('rick', '123rick456'), verify=False)

predlist = [{'account':"",   *預測者帳號
            'password':"",  *預測者密碼
             'GroupOptionCode':20,   *預測盤口
             'OptionCode':int(OptionCode),  *預測方向
             'EventCode':EventCode,   *賽事Eventcode
             'predict_type':'Selling',     *預測種類
              'HomeOdds':float(HomeOdds),     *主隊賠率
              'AwayOdds':float(AwayOdds),       *客隊賠率
              'HomeConfidence':str(int(round( (pre[i]) * 100,0))) + "%",     *主隊信心度
              'AwayConfidence':str(int(round((1-pre[i]) * 100,0))) + "%",    *客隊信心度
              'main' : main     *是否為主推(NBA主推為85%以上)
}]    
```
