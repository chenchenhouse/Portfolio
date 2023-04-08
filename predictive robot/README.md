
* [全部預測機器人](#全部預測機器人)
* [個別預測機器人](#個別預測機器人)
  * [機器人預測MLB](#機器人預測MLB)
  * [機器人預測NBA](#機器人預測NBA)
  * [機器人預測EPL](#機器人預測EPL)
  * [機器人預測SerieA](#機器人預測SerieA)
  * [機器人預測LaLiga](#機器人預測LaLiga)
  * [機器人預測Bundesliga](#機器人預測Bundesliga)
  * [機器人預測Ligue1](#機器人預測Ligue1)
  * [機器人預測LOLLPL](#機器人預測LOLLPL)
  * [機器人預測CPBL](#機器人預測CPBL)
  * [機器人預測NHL](#機器人預測NHL)
  * [機器人預測WorldChampionshipQual2022](#機器人預測WorldChampionshipQual2022)
  * [機器人預測KLeague1](#機器人預測KLeague1)
  * [機器人預測JLeague](#機器人預測JLeague)

# 用途
每日三個時段進行預測機器人賽事的隨機預測，製造網站預測活絡現象

# 工具
* python
	- requests : 訪問自製的API，進行最新賽事查詢
	- logging : 紀錄已預測過的帳號與賽事
	- pandas : 數據處理

# 全部預測機器人
### 程式碼
 ```js
 ALLForecast = ALL_Bot_Forecast()
 ALLForecast.All_bot_predict()
 ```
 
# 個別預測機器人
## 機器人預測MLB
### 程式碼
 ```js
MLBForecast = MLBForecast()
MLBForecast.MLB_predict()
```

## 機器人預測NBA
### 程式碼
 ```js
NBAForecast = NBAForecast()
NBAForecast.NBA_predict()
```


## 機器人預測EPL
### 程式碼
 ```js
EPLForecast = EPLForecast()
EPLForecast.EPL_predict()
```

## 機器人預測SerieA
### 程式碼
 ```js
SerieAForecast = SerieAForecast()
SerieAForecast.SerieA_predict()
```


## 機器人預測LaLiga
### 程式碼
 ```js
LaLigaForecast = LaLigaForecast()
LaLigaForecast.LaLiga_predict()
```

## 機器人預測Bundesliga
### 程式碼
 ```js
BundesligaForecast = BundesligaForecast()
BundesligaForecast.Bundesliga_predict()
```

## 機器人預測Ligue1
### 程式碼
 ```js
Ligue1Forecast = Ligue1Forecast()
Ligue1Forecast.Ligue1_predict()
```

## 機器人預測LOLLPL
### 程式碼
 ```js
LOLLPLForecast = LOLLPLForecast()
LOLLPLForecast.LOLLPL_predict()
```

## 機器人預測CPBL
### 程式碼
 ```js
CPBLForecast = CPBLForecast()
CPBLForecast.CPBL_predict()
```

## 機器人預測NHL
### 程式碼
 ```js
NHLForecast = NHLForecast()
NHLForecast.NHL_predict()
```

## 機器人預測WorldChampionshipQual2022
### 程式碼
 ```js
WorldChampionshipQual2022Forecast = WorldChampionshipQual2022Forecast()
WorldChampionshipQual2022Forecast.WorldChampionshipQual2022_predict()
```

## 機器人預測KLeague1
### 程式碼
 ```js
KLeague1Forecast = KLeague1Forecast()
KLeague1Forecast.KLeague1_predict()
```

## 機器人預測JLeague
### 程式碼
 ```js
J1LeagueForecast = J1LeagueForecast()
J1LeagueForecast.J1League_predict()
```






