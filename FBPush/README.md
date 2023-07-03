# FB預測賽事推播
會與預測推播的程式碼寫在一起，一預測就跟著在FB中發文
### 程式碼
 ```js
FBPushBot = fb.FBPushBot(predlist)
FBPushBot.PushBot('predict')
 ```
 ![image](https://i.imgur.com/cWwYbMG.png)
 
 
 # FB預測賽事結果推播
 寫到immediatePredictResultsPush.py中，每日早上10:00一併在FB中發文出來
### 程式碼
 ```js
FBPushBot = fb.FBPushBot()
FBPushBot.PushBot('result')
 ```
 ![image](https://i.imgur.com/xwnEazF.png)
