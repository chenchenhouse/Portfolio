# Guess365 Line Bot 官方機器人
製作日期 : 2022/6~2023/1
製作人 : Rick

## 功能介紹與工具:
### (一)	功能介紹
本專案將Guess365相關訊息與LINE BOT進行串接
- 加入LINE BOT即可自動註冊會員 :
  1.帳號密碼隨機創建，email與手機號碼預設為空(目前使用方式)
  2.製作小網頁，讓使用者自行註冊帳號密碼
-	預測模型之結果與成績推播
-	各項體育賽程與賽事結果查詢
-	PK賽事即時搓合，獲勝可得相對應的G⁺幣
-	推播Guess365相關廣告
-	PK商城，兌換好禮
-	好友推薦，贈送超商禮券

### (二)	使用工具
-	Python3.9.12(Jupyter Notbook)
  - datetime
  - flask
  - linebot
  - matplotlib
  - time
  - json
  - numpy
  - pandas
  - pyodbc
  - requests
-	LINE official Account Manager
-	LINE Developers
-	Aaure Data Studio
-	Ngrok
## 系統流程圖
### 一、	架構圖
架構圖顯示Linebot機器人的主要功能，及LineBot機器人與其他實體的溝通方式。
目前系統主要功能分成:
(一)	會員資訊
(二)	預測推播(手動&自動)
(三)	賽果通知
(四)	好手PK(隨機配對PK對手，獲勝者得G Plus幣)
(五)	獲利績效(隨時查詢最新預測機器人預測結果)
(六)	查詢賽況(可查詢昨、今日已開賽結果；開賽中之即時比分；今、明日未開賽之賽果)
(七)	訂閱資訊(訂閱預測機器人之方法與價錢)
(八)	好友推薦(推薦好友加入，填寫推薦人即可獲得超商禮券)
(九)	兌換商品(GPlus幣商品兌換)
